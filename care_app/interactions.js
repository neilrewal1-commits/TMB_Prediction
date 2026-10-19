/* Local interaction effects. No reports, identifiers, or network calls. */
(() => {
  'use strict';
  const VERSION = '1';
  const STORAGE_KEY = 'cancer-care:sound';
  const existing = window.__cancerCareInteractions;
  if (existing?.version === VERSION) {
    existing.sync();
    return;
  }
  existing?.destroy();

  let enabled = true;
  try { enabled = localStorage.getItem(STORAGE_KEY) !== 'off'; } catch (_) { /* Storage is optional. */ }
  let context;
  let lastTap = -Infinity;
  const controller = new AbortController();
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function sync() {
    document.querySelectorAll('[data-care-sound]').forEach(button => {
      button.setAttribute('aria-checked', String(enabled));
      const label = button.querySelector('[data-care-sound-label]');
      if (label) label.textContent = enabled ? 'Sound on' : 'Sound off';
    });
  }

  function tap() {
    if (!enabled || document.visibilityState === 'hidden') return;
    const now = performance.now();
    if (now - lastTap < 65) return; // Labels may also trigger a native input click.
    lastTap = now;
    try {
      const Audio = window.AudioContext || window.webkitAudioContext;
      if (!Audio) return;
      if (!context || context.state === 'closed') context = new Audio();
      // Called synchronously from a user gesture, including keyboard activation.
      if (context.state === 'suspended') context.resume().catch(() => {});
      const start = context.currentTime;
      const oscillator = context.createOscillator();
      const gain = context.createGain();
      oscillator.type = 'sine';
      oscillator.frequency.setValueAtTime(740, start);
      oscillator.frequency.exponentialRampToValueAtTime(480, start + 0.055);
      gain.gain.setValueAtTime(0.0001, start);
      gain.gain.exponentialRampToValueAtTime(0.035, start + 0.004);
      gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.065);
      oscillator.connect(gain);
      gain.connect(context.destination);
      oscillator.onended = () => { oscillator.disconnect(); gain.disconnect(); };
      oscillator.start(start);
      oscillator.stop(start + 0.07);
    } catch (_) { /* Audio support never blocks an app action. */ }
  }

  function ripple(element, event) {
    if (motion.matches || !element.matches('button, a')) return;
    const box = element.getBoundingClientRect();
    const size = Math.max(box.width, box.height) * 2;
    if (!size) return;
    const ink = document.createElement('span');
    ink.className = 'care-ripple';
    ink.setAttribute('aria-hidden', 'true');
    const x = event.detail ? event.clientX - box.left : box.width / 2;
    const y = event.detail ? event.clientY - box.top : box.height / 2;
    Object.assign(ink.style, { width: `${size}px`, height: `${size}px`,
      left: `${x - size / 2}px`, top: `${y - size / 2}px` });
    element.appendChild(ink);
    const remove = () => ink.remove();
    ink.addEventListener('animationend', remove, { once: true });
    setTimeout(remove, 700);
  }

  function onClick(event) {
    if (!event.isTrusted || !(event.target instanceof Element)) return;
    const soundSwitch = event.target.closest('[data-care-sound]');
    if (soundSwitch) {
      enabled = !enabled;
      try { localStorage.setItem(STORAGE_KEY, enabled ? 'on' : 'off'); } catch (_) { /* Optional. */ }
      sync();
      if (enabled) tap();
      return;
    }
    const target = event.target.closest('button, a[href], summary, [role="tab"], [role="radio"], [role="checkbox"], input[type="checkbox"], input[type="radio"], label');
    if (!target || target.closest('[disabled], [aria-disabled="true"]')) return;
    if (target.matches('label') && !target.querySelector('input[type="checkbox"], input[type="radio"]')) return;
    const input = target.querySelector('input');
    if (input?.disabled) return;
    tap();
    ripple(target, event);
  }

  document.addEventListener('click', onClick, { capture: true, signal: controller.signal });
  window.addEventListener('storage', event => {
    if (event.key === STORAGE_KEY) { enabled = event.newValue !== 'off'; sync(); }
  }, { signal: controller.signal });
  window.__cancerCareInteractions = {
    version: VERSION, sync,
    destroy() { controller.abort(); if (context && context.state !== 'closed') context.close().catch(() => {}); }
  };
  sync();
})();
