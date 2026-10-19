const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const script = fs.readFileSync(path.join(__dirname, '../care_app/interactions.js'), 'utf8');

function harness({ muted = false, reduced = false, noAudio = false, noStorage = false } = {}) {
  const metrics = { contexts: 0, taps: 0, ripples: 0, duration: 0, peak: 0 };
  const listeners = new Map();
  const storage = new Map(muted ? [['cancer-care:sound', 'off']] : []);
  function listen(type, fn, { signal } = {}) {
    if (!listeners.has(type)) listeners.set(type, new Set());
    listeners.get(type).add(fn);
    signal?.addEventListener('abort', () => listeners.get(type).delete(fn), { once: true });
  }
  class Element {
    constructor(toggle = false) { this.toggle = toggle; this.attrs = {}; this.label = {}; this.style = {}; }
    setAttribute(key, value) { this.attrs[key] = value; }
    closest(selector) {
      if (selector === '[data-care-sound]') return this.toggle ? this : null;
      if (selector.includes('[disabled]')) return this.disabled ? this : null;
      return this;
    }
    querySelector(selector) { return selector === '[data-care-sound-label]' ? this.label : null; }
    matches(selector) { return selector === 'button, a'; }
    getBoundingClientRect() { return { width: 90, height: 44, left: 0, top: 0 }; }
    appendChild() { metrics.ripples++; }
    addEventListener() {}
    remove() {}
  }
  const toggle = new Element(true);
  class Audio {
    constructor() { metrics.contexts++; this.state = 'running'; this.currentTime = 1; this.destination = {}; }
    createOscillator() {
      return {
        frequency: { setValueAtTime() {}, exponentialRampToValueAtTime() {} },
        connect() {}, disconnect() {}, start() { metrics.taps++; },
        stop(time) { metrics.duration = time - 1; this.onended(); }
      };
    }
    createGain() {
      return { gain: { setValueAtTime() {}, exponentialRampToValueAtTime(value) { metrics.peak = Math.max(metrics.peak, value); } },
        connect() {}, disconnect() {} };
    }
    resume() { return Promise.resolve(); }
    close() { this.state = 'closed'; return Promise.resolve(); }
  }
  const document = { visibilityState: 'visible', querySelectorAll: () => [toggle],
    createElement: () => new Element(), addEventListener: listen };
  const window = { matchMedia: () => ({ matches: reduced }), addEventListener: listen,
    AudioContext: noAudio ? undefined : Audio };
  const context = vm.createContext({ window, document, Element, AbortController,
    performance: { now: () => clock }, setTimeout: fn => fn(),
    localStorage: { getItem(key) { if (noStorage) throw Error('Blocked'); return storage.get(key); },
      setItem(key, value) { if (noStorage) throw Error('Blocked'); storage.set(key, value); } }
  });
  let clock = 0;
  const run = () => vm.runInContext(script, context);
  function click(target = new Element(), trusted = true) {
    clock += 100;
    for (const fn of listeners.get('click')) fn({ target, isTrusted: trusted, detail: 0 });
  }
  run();
  return { metrics, toggle, storage, listeners, click, run, Element, document };
}

test('sound starts only after a user action, stays quiet, and reuses one audio context', () => {
  const h = harness();
  assert.equal(h.metrics.contexts, 0);
  h.click(undefined, false);
  assert.equal(h.metrics.taps, 0);
  h.click(); h.click();
  assert.equal(h.metrics.taps, 2);
  assert.equal(h.metrics.contexts, 1);
  assert.ok(h.metrics.duration <= .08);
  assert.ok(h.metrics.peak <= .04);
});

test('mute survives rerenders without accumulating event listeners', () => {
  const h = harness();
  h.click(h.toggle);
  assert.equal(h.toggle.attrs['aria-checked'], 'false');
  assert.equal(h.storage.get('cancer-care:sound'), 'off');
  h.run(); h.run(); h.click();
  assert.equal(h.listeners.get('click').size, 1);
  assert.equal(h.metrics.taps, 0);
  h.click(h.toggle);
  assert.equal(h.toggle.label.textContent, 'Sound on');
  assert.equal(h.metrics.taps, 1);
});

test('saved mute, disabled controls, and hidden pages produce no sound', () => {
  const h = harness({ muted: true });
  h.click();
  assert.equal(h.metrics.taps, 0);
  h.click(h.toggle);
  const before = h.metrics.taps;
  const disabled = new h.Element(); disabled.disabled = true;
  h.click(disabled);
  h.document.visibilityState = 'hidden'; h.click();
  assert.equal(h.metrics.taps, before);
});

test('reduced motion skips ripples while preserving user-selected sound', () => {
  const h = harness({ reduced: true });
  h.click();
  assert.equal(h.metrics.ripples, 0);
  assert.equal(h.metrics.taps, 1);
});

test('missing audio and blocked browser storage do not block interactions', () => {
  const h = harness({ noAudio: true, noStorage: true });
  assert.doesNotThrow(() => { h.click(); h.click(h.toggle); h.click(h.toggle); });
  assert.equal(h.toggle.attrs['aria-checked'], 'true');
});
