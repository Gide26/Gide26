/**
 * Shared helpers: timezones, money rounding, input coercion, validation, CSV.
 * No external dependencies.
 */

/** HTTP error that the router turns into a JSON response. */
export class HttpError extends Error {
  constructor(status, message, details) {
    super(message);
    this.status = status;
    this.details = details;
  }
}
export const badRequest = (msg, details) => new HttpError(400, msg, details);
export const unauthorized = (msg = 'Please sign in') => new HttpError(401, msg);
export const forbidden = (msg = 'You do not have permission to do that') => new HttpError(403, msg);
export const notFound = (msg = 'Not found') => new HttpError(404, msg);

/* ------------------------------------------------------------------ *
 * Coercion — node:sqlite rejects `undefined` and `boolean` bindings,
 * so everything gets normalised before it reaches a prepared statement.
 * ------------------------------------------------------------------ */

export const str = (v, fallback = '') => {
  if (v === null || v === undefined) return fallback;
  const s = String(v).trim();
  return s === '' ? fallback : s;
};

/** Optional text that becomes NULL rather than '' when blank. */
export const strOrNull = (v) => {
  if (v === null || v === undefined) return null;
  const s = String(v).trim();
  return s === '' ? null : s;
};

export const num = (v, fallback = 0) => {
  const n = typeof v === 'number' ? v : parseFloat(String(v ?? '').replace(/,/g, ''));
  return Number.isFinite(n) ? n : fallback;
};

/** Optional integer id -> NULL when absent, so foreign keys stay clean. */
export const idOrNull = (v) => {
  if (v === null || v === undefined || v === '') return null;
  const n = Number(v);
  return Number.isInteger(n) && n > 0 ? n : null;
};

export const int = (v, fallback = 0) => {
  const n = parseInt(String(v ?? ''), 10);
  return Number.isInteger(n) ? n : fallback;
};

export const bool = (v) => (v === true || v === 1 || v === '1' || v === 'true' || v === 'on' ? 1 : 0);

export const clamp = (n, lo, hi) => Math.min(hi, Math.max(lo, n));

/** Truncate free text so a stray paste cannot blow up a column. */
export const clip = (v, max = 500) => str(v).slice(0, max);

/* ------------------------------------------------------------------ *
 * Money
 * ------------------------------------------------------------------ */

/** Round to `decimals` places using half-up, avoiding float drift. */
export function round(n, decimals = 0) {
  const v = num(n);
  const f = 10 ** decimals;
  return Math.round((v + Number.EPSILON * Math.sign(v)) * f) / f;
}

export const sum = (arr, pick = (x) => x) => round(arr.reduce((a, b) => a + num(pick(b)), 0), 4);

/* ------------------------------------------------------------------ *
 * Time. Timestamps are stored as *local* wall-clock strings in the
 * business timezone (default Africa/Bujumbura) so that SQL date
 * grouping, "today" and "this month" all behave the way the owner
 * expects without timezone maths in every query.
 * ------------------------------------------------------------------ */

export const DEFAULT_TZ = 'Africa/Bujumbura';

/** 'YYYY-MM-DD HH:MM:SS' for the given instant in `tz`. */
export function localStamp(date = new Date(), tz = DEFAULT_TZ) {
  const p = new Intl.DateTimeFormat('en-CA', {
    timeZone: tz,
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false,
  }).formatToParts(date).reduce((a, x) => ((a[x.type] = x.value), a), {});
  // Intl can return hour "24" at midnight in some runtimes.
  const hour = p.hour === '24' ? '00' : p.hour;
  return `${p.year}-${p.month}-${p.day} ${hour}:${p.minute}:${p.second}`;
}

export function localDate(date = new Date(), tz = DEFAULT_TZ) {
  return localStamp(date, tz).slice(0, 10);
}

export function localMonth(date = new Date(), tz = DEFAULT_TZ) {
  return localStamp(date, tz).slice(0, 7);
}

/** Today's date in tz, plus the first day of this month. */
export function dateBounds(tz = DEFAULT_TZ) {
  const today = localDate(new Date(), tz);
  return { today, monthStart: `${today.slice(0, 7)}-01` };
}

/** Add days to a 'YYYY-MM-DD' string (UTC-safe, no DST drift). */
export function addDays(dateStr, days) {
  const d = new Date(`${dateStr}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() + days);
  return d.toISOString().slice(0, 10);
}

/** Inclusive date-range defaulting to the current month. */
export function range(query, tz = DEFAULT_TZ) {
  const { today, monthStart } = dateBounds(tz);
  let from = str(query.from) || monthStart;
  let to = str(query.to) || today;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(from)) from = monthStart;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(to)) to = today;
  if (from > to) [from, to] = [to, from];
  return { from, to };
}

/* ------------------------------------------------------------------ *
 * Validation
 * ------------------------------------------------------------------ */

export function require_(v, label) {
  const s = str(v);
  if (!s) throw badRequest(`${label} is required`);
  return s;
}

export function requireAmount(v, label = 'Amount') {
  const n = num(v, NaN);
  if (!Number.isFinite(n)) throw badRequest(`${label} must be a number`);
  if (n < 0) throw badRequest(`${label} cannot be negative`);
  return n;
}

export const PHONE_RE = /^[0-9+\-()\s]{6,20}$/;

/* ------------------------------------------------------------------ *
 * CSV export
 * ------------------------------------------------------------------ */

export function toCsv(rows, columns) {
  const esc = (v) => {
    if (v === null || v === undefined) return '';
    const s = String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const head = columns.map((c) => esc(c.label ?? c.key)).join(',');
  const body = rows.map((r) => columns.map((c) => esc(c.value ? c.value(r) : r[c.key])).join(','));
  return `${[head, ...body].join('\r\n')}\r\n`;
}

/** Escape a value for safe interpolation into an HTML attribute. */
export function escAttr(v) {
  return str(v).replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}
