"""Single-host community demo. Credentials never appear in the public directory."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import hmac
from pathlib import Path
import re
import secrets
import sqlite3
import uuid

SCHEMA = '''
CREATE TABLE IF NOT EXISTS profiles (
 id TEXT PRIMARY KEY, alias TEXT COLLATE NOCASE UNIQUE NOT NULL,
 cancer TEXT NOT NULL, phase TEXT NOT NULL, region TEXT NOT NULL,
 interests TEXT NOT NULL, token_hash TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS connections (
 id INTEGER PRIMARY KEY, sender TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
 receiver TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
 pair_key TEXT UNIQUE NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('pending','accepted','declined','blocked')),
 created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
 id INTEGER PRIMARY KEY, connection_id INTEGER NOT NULL REFERENCES connections(id) ON DELETE CASCADE,
 author TEXT NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
 body TEXT NOT NULL, created_at TEXT NOT NULL
);
'''


def now():
    return datetime.now(timezone.utc).isoformat()


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


class CommunityStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript(SCHEMA)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys = ON')
        try:
            with db:
                yield db
        finally:
            db.close()

    def authenticate(self, db, credential):
        profile = db.execute('SELECT * FROM profiles WHERE id=?', (credential['id'],)).fetchone()
        if profile is None or not hmac.compare_digest(profile['token_hash'], token_hash(credential['token'])):
            raise ValueError('Your community session is no longer valid. Sign in again.')
        return profile

    def create_profile(self, alias, cancer, phase, region, interests, *, consent):
        if not consent:
            raise ValueError('Agree to publish your community profile before joining.')
        alias = alias.strip()
        if not re.fullmatch(r'[A-Za-z0-9_ -]{3,30}', alias):
            raise ValueError('Use a 3–30 character alias containing letters, numbers, spaces, _ or -.')
        fields = [str(x).strip() for x in [cancer, phase, region, interests]]
        if not fields[0] or any(len(x) > limit for x, limit in zip(fields, [80,80,80,300])):
            raise ValueError('Check your profile fields and their length limits.')
        credential = {'id': str(uuid.uuid4()), 'token': secrets.token_urlsafe(32)}
        try:
            with self.connect() as db:
                db.execute('INSERT INTO profiles VALUES (?,?,?,?,?,?,?,?)',
                           (credential['id'], alias, *fields, token_hash(credential['token']), now()))
        except sqlite3.IntegrityError as exc:
            raise ValueError('That community alias is taken. Choose another.') from exc
        return credential

    def login(self, alias, token):
        with self.connect() as db:
            row = db.execute('SELECT id,token_hash FROM profiles WHERE alias=?', (alias.strip(),)).fetchone()
        if row is None or not hmac.compare_digest(row['token_hash'], token_hash(token.strip())):
            raise ValueError('Alias or access code is incorrect.')
        return {'id': row['id'], 'token': token.strip()}

    def profile(self, credential):
        with self.connect() as db:
            row = dict(self.authenticate(db, credential))
        row.pop('token_hash')
        return row

    def peers(self, credential, same_cancer=False, same_region=False):
        with self.connect() as db:
            me = self.authenticate(db, credential)
            rows = db.execute('SELECT id,alias,cancer,phase,region,interests FROM profiles WHERE id<>?',
                              (me['id'],)).fetchall()
            # Blocked or declined relationships are not suggested again.
            excluded = {r[0] for r in db.execute(
                "SELECT CASE WHEN sender=? THEN receiver ELSE sender END FROM connections "
                "WHERE (sender=? OR receiver=?) AND status IN ('blocked','declined')",
                (me['id'], me['id'], me['id']))}
        peers = []
        for row in rows:
            peer = dict(row)
            if peer['id'] in excluded:
                continue
            if same_cancer and peer['cancer'] != me['cancer']:
                continue
            if same_region and (not me['region'] or peer['region'].casefold() != me['region'].casefold()):
                continue
            peer['shared'] = [name for name, match in [
                ('cancer group', peer['cancer'] != 'Prefer not to say' and peer['cancer'] == me['cancer']),
                ('treatment phase', peer['phase'] != 'Prefer not to say' and peer['phase'] == me['phase']),
                ('region', bool(me['region']) and peer['region'].casefold() == me['region'].casefold())] if match]
            peers.append(peer)
        return sorted(peers, key=lambda p: (-len(p['shared']), p['alias'].casefold()))[:100]

    def request(self, credential, receiver):
        with self.connect() as db:
            me = self.authenticate(db, credential)
            if receiver == me['id'] or not db.execute('SELECT 1 FROM profiles WHERE id=?', (receiver,)).fetchone():
                raise ValueError('Choose another available community member.')
            pair = ':'.join(sorted([me['id'], receiver]))
            if db.execute('SELECT 1 FROM connections WHERE pair_key=?', (pair,)).fetchone():
                raise ValueError('A connection already exists or was declined. Check your requests.')
            db.execute('INSERT INTO connections(sender,receiver,pair_key,status,created_at) VALUES (?,?,?,?,?)',
                       (me['id'], receiver, pair, 'pending', now()))

    def connections(self, credential):
        with self.connect() as db:
            me = self.authenticate(db, credential)
            rows = db.execute('''SELECT c.*, p.alias, p.cancer FROM connections c JOIN profiles p
                ON p.id=CASE WHEN c.sender=? THEN c.receiver ELSE c.sender END
                WHERE c.sender=? OR c.receiver=? ORDER BY c.id DESC''', (me['id'], me['id'], me['id'])).fetchall()
        return [dict(row) for row in rows]

    def connection(self, db, credential, connection_id):
        me = self.authenticate(db, credential)
        row = db.execute('SELECT * FROM connections WHERE id=? AND (sender=? OR receiver=?)',
                         (connection_id, me['id'], me['id'])).fetchone()
        if row is None:
            raise ValueError('This connection is not available to your account.')
        return me, row

    def respond(self, credential, connection_id, status):
        if status not in {'accepted', 'declined', 'blocked'}:
            raise ValueError('Invalid connection response.')
        with self.connect() as db:
            me, row = self.connection(db, credential, connection_id)
            if status != 'blocked' and (row['receiver'] != me['id'] or row['status'] != 'pending'):
                raise ValueError('Only the recipient can respond to a pending request.')
            db.execute('UPDATE connections SET status=? WHERE id=?', (status, connection_id))

    def send(self, credential, connection_id, body):
        body = body.strip()
        if not body or len(body) > 1000:
            raise ValueError('Write a message of 1–1000 characters.')
        with self.connect() as db:
            me, row = self.connection(db, credential, connection_id)
            if row['status'] != 'accepted':
                raise ValueError('Both people must connect before messaging.')
            db.execute('INSERT INTO messages(connection_id,author,body,created_at) VALUES (?,?,?,?)',
                       (connection_id, me['id'], body, now()))

    def messages(self, credential, connection_id):
        with self.connect() as db:
            _, row = self.connection(db, credential, connection_id)
            if row['status'] != 'accepted':
                raise ValueError('Messaging is available only for accepted connections.')
            rows = db.execute('''SELECT m.body,m.created_at,p.alias FROM messages m JOIN profiles p
                ON p.id=m.author WHERE connection_id=? ORDER BY m.id DESC LIMIT 100''', (connection_id,)).fetchall()
        return [dict(row) for row in reversed(rows)]

    def delete_profile(self, credential):
        with self.connect() as db:
            me = self.authenticate(db, credential)
            db.execute('DELETE FROM profiles WHERE id=?', (me['id'],))
