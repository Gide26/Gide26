/**
 * Authentication: scrypt password hashing, opaque session tokens stored
 * server-side (hashed), cookie handling, role guards and login throttling.
 */
import { randomBytes, createHash, timingSafeEqual } from 'node:crypto';
import { db, hashPassword, verifyPassword, now } from './db.js';
import { unauthorized, forbidden, badRequest, num, str } from './util.js';

const SESSION_DAYS = 30;
export const COOKIE_NAME = 'bk_sid';

const sha = (s) => createHash('sha256').update(s).digest('hex');

const expiry = (days) =>
  new Date(Date.now() + days * 86400000).toISOString().replace('T', ' ').slice(0, 19);

/* ------------------------------------------------------------------ *
 * Login throttling — slows password guessing without locking a real
 * owner out of their own till.
 * ------------------------------------------------------------------ */
const MAX_ATTEMPTS = 8;
const LOCK_MINUTES = 10;
const attempts = new Map(); // "phone|ip" -> { count, until }

const keyOf = (phone, ip) => `${str(phone).toLowerCase()}|${ip}`;

function checkThrottle(key) {
  const rec = attempts.get(key);
  if (!rec?.until) return;
  if (Date.now() < rec.until) {
    const mins = Math.ceil((rec.until - Date.now()) / 60000);
    throw forbidden(`Too many failed attempts. Try again in ${mins} minute${mins === 1 ? '' : 's'}.`);
  }
  attempts.delete(key);
}

function recordFailure(key) {
  const rec = attempts.get(key) || { count: 0, until: 0 };
  rec.count += 1;
  if (rec.count >= MAX_ATTEMPTS) {
    rec.count = 0;
    rec.until = Date.now() + LOCK_MINUTES * 60000;
  }
  attempts.set(key, rec);
}

/** Accepts "079000000", "+25779000000" or "079 000 000" for the same account. */
const normalisePhone = (v) => str(v).replace(/[\s\-()]/g, '');

/* ------------------------------------------------------------------ *
 * Sessions
 * ------------------------------------------------------------------ */

export function createSession(userId) {
  const token = randomBytes(32).toString('base64url');
  const stamp = now();
  db.prepare(
    'INSERT INTO sessions (token_hash, user_id, created_at, expires_at, last_seen) VALUES (?,?,?,?,?)'
  ).run(sha(token), userId, stamp, expiry(SESSION_DAYS), stamp);
  return token;
}

/** Look up a session, slide its expiry, and return the user. */
export function userFromToken(token) {
  if (!token) return null;
  const row = db.prepare(
    `SELECT s.expires_at, u.id, u.name, u.phone, u.role, u.must_change, u.active
       FROM sessions s JOIN users u ON u.id = s.user_id
      WHERE s.token_hash = ?`
  ).get(sha(token));
  if (!row || !row.active) return null;

  const stamp = now();
  if (row.expires_at < stamp) {
    db.prepare('DELETE FROM sessions WHERE token_hash = ?').run(sha(token));
    return null;
  }
  // Slide the expiry forward once it is within a week of lapsing.
  const fresh = row.expires_at < expiry(SESSION_DAYS - 7);
  db.prepare(fresh
    ? 'UPDATE sessions SET last_seen = ?, expires_at = ? WHERE token_hash = ?'
    : 'UPDATE sessions SET last_seen = ? WHERE token_hash = ?')
    .run(...(fresh ? [stamp, expiry(SESSION_DAYS), sha(token)] : [stamp, sha(token)]));

  return { id: row.id, name: row.name, phone: row.phone, role: row.role, must_change: !!row.must_change };
}

export function destroySession(token) {
  if (token) db.prepare('DELETE FROM sessions WHERE token_hash = ?').run(sha(token));
}

/** Drop expired rows so the table does not grow forever. */
export function pruneSessions() {
  return db.prepare('DELETE FROM sessions WHERE expires_at < ?').run(now()).changes;
}

export const sessionCount = () => num(db.prepare('SELECT COUNT(*) n FROM sessions').get().n);

/* ------------------------------------------------------------------ *
 * Login / password changes
 * ------------------------------------------------------------------ */

export function login(rawPhone, password, ip) {
  const phone = normalisePhone(rawPhone);
  const key = keyOf(phone, ip);
  checkThrottle(key);

  const user = db.prepare('SELECT * FROM users WHERE active = 1').all()
    .find((u) => normalisePhone(u.phone) === phone.toLowerCase() || u.phone.toLowerCase() === phone.toLowerCase());

  if (!user || !verifyPassword(password, user.pass_salt, user.pass_hash)) {
    recordFailure(key);
    throw unauthorized('Wrong phone number or password');
  }
  attempts.delete(key);

  return {
    token: createSession(user.id),
    user: { id: user.id, name: user.name, phone: user.phone, role: user.role, must_change: !!user.must_change },
  };
}

export function changePassword(userId, currentPassword, newPassword) {
  const user = db.prepare('SELECT * FROM users WHERE id = ?').get(userId);
  if (!user) throw unauthorized();
  if (!verifyPassword(currentPassword, user.pass_salt, user.pass_hash)) {
    throw forbidden('Your current password is not correct');
  }
  if (str(newPassword).length < 6) {
    throw badRequest('Use at least 6 characters for your new password');
  }
  const { salt, hash } = hashPassword(newPassword);
  db.prepare('UPDATE users SET pass_hash = ?, pass_salt = ?, must_change = 0 WHERE id = ?')
    .run(hash, salt, userId);
  // Sign out every device so the old password cannot linger anywhere.
  db.prepare('DELETE FROM sessions WHERE user_id = ?').run(userId);
}

/* ------------------------------------------------------------------ *
 * Cookies
 * ------------------------------------------------------------------ */

export function parseCookies(header) {
  const out = {};
  for (const part of str(header).split(';')) {
    const i = part.indexOf('=');
    if (i < 1) continue;
    const k = part.slice(0, i).trim();
    const v = part.slice(i + 1).trim();
    if (!k) continue;
    try { out[k] = decodeURIComponent(v); } catch { out[k] = v; }
  }
  return out;
}

export const sessionCookie = (token, { secure }) =>
  [`${COOKIE_NAME}=${encodeURIComponent(token)}`, 'Path=/', 'HttpOnly', 'SameSite=Strict',
   `Max-Age=${SESSION_DAYS * 86400}`, secure ? 'Secure' : ''].filter(Boolean).join('; ');

export const clearCookie = ({ secure }) =>
  [`${COOKIE_NAME}=`, 'Path=/', 'HttpOnly', 'SameSite=Strict', 'Max-Age=0', secure ? 'Secure' : '']
    .filter(Boolean).join('; ');

/* ------------------------------------------------------------------ *
 * Guards
 * ------------------------------------------------------------------ */

export function requireUser(ctx) {
  if (!ctx.user) throw unauthorized();
  return ctx.user;
}

export function requireOwner(ctx) {
  const u = requireUser(ctx);
  if (u.role !== 'owner') throw forbidden('Only the owner can do that');
  return u;
}

export function safeEqual(a, b) {
  const ba = Buffer.from(str(a));
  const bb = Buffer.from(str(b));
  return ba.length === bb.length && timingSafeEqual(ba, bb);
}
