/**
 * Formatting helpers. Timestamps are stored as plain local wall-clock
 * strings ('YYYY-MM-DD HH:MM:SS') in the business timezone, so they are
 * rendered by reading the parts directly — never re-parsed as UTC, which
 * would shift every date by the viewer's timezone offset.
 */

let CFG = {
  symbol: 'FBu', code: 'BIF', decimals: 0,
  timezone: 'Africa/Bujumbura',
  businessName: "Gide's Bakery",
  today: null, monthStart: null,
};

export const setFormatConfig = (c) => { CFG = { ...CFG, ...(c || {}) }; };
export const fmtCfg = () => CFG;

const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const MONTHS_LONG = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
  'August', 'September', 'October', 'November', 'December'];
const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

/* ------------------------------------------------------------------ *
 * HTML escaping — every value from the server goes through this before
 * it is placed into innerHTML.
 * ------------------------------------------------------------------ */
const ESC_MAP = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;', '`': '&#96;' };
export const esc = (v) => (v === null || v === undefined ? '' : String(v).replace(/[&<>"'`]/g, (c) => ESC_MAP[c]));

/* ------------------------------------------------------------------ *
 * Numbers & money
 * ------------------------------------------------------------------ */
const n = (v) => {
  const x = typeof v === 'number' ? v : parseFloat(String(v ?? '').replace(/,/g, ''));
  return Number.isFinite(x) ? x : 0;
};

const group = (value, d) =>
  new Intl.NumberFormat('en-US', { minimumFractionDigits: d, maximumFractionDigits: d }).format(value);

/** Trim trailing zeros: 2.500 -> 2.5, 3.000 -> 3 */
export function qty(value, maxDecimals = 3) {
  const v = n(value);
  const rounded = Math.round(v * 10 ** maxDecimals) / 10 ** maxDecimals;
  return group(rounded, Math.min(maxDecimals, Math.max(0, (String(rounded).split('.')[1] || '').length)));
}

export function num(value, decimals = 0) {
  return group(n(value), decimals);
}

/** 'FBu 12,500' — sign goes in front of the symbol so negatives read clearly. */
export function money(value, opts = {}) {
  const v = n(value);
  const d = opts.decimals ?? CFG.decimals;
  const body = group(Math.abs(v), d);
  const sign = v < 0 ? '-' : (opts.signed && v > 0 ? '+' : '');
  return `${sign}${CFG.symbol} ${body}`;
}

/** Money without the symbol, for tight table columns. */
export const moneyBare = (value, d) => group(n(value), d ?? CFG.decimals);

/** Compact money for chart axes: FBu 1.2M / 340K. */
export function moneyCompact(value, withSymbol = false) {
  const v = n(value);
  const a = Math.abs(v);
  const sym = withSymbol ? `${CFG.symbol} ` : '';
  const sign = v < 0 ? '-' : '';
  if (a >= 1e9) return `${sign}${sym}${(a / 1e9).toFixed(1)}B`;
  if (a >= 1e6) return `${sign}${sym}${(a / 1e6).toFixed(a >= 1e7 ? 0 : 1)}M`;
  if (a >= 1e3) return `${sign}${sym}${Math.round(a / 1e3)}K`;
  return `${sign}${sym}${group(a, 0)}`;
}

export function pct(value, decimals = 0) {
  const v = n(value);
  return `${group(v, decimals)}%`;
}

/** '+12.4%' / '-3%' / '—' when there is nothing to compare against. */
export function deltaPct(value, decimals = 1) {
  if (value === null || value === undefined || value === '') return '—';
  const v = n(value);
  return `${v > 0 ? '+' : ''}${group(v, decimals)}%`;
}

/** Round a number up to a "nice" amount for quick-cash buttons. */
export function roundUpTo(value, step) {
  const v = n(value);
  return Math.ceil(v / step) * step;
}

/* ------------------------------------------------------------------ *
 * Dates
 * ------------------------------------------------------------------ */

function parts(value) {
  if (!value) return null;
  if (value instanceof Date) {
    return { y: value.getFullYear(), mo: value.getMonth() + 1, d: value.getDate(),
      h: value.getHours(), mi: value.getMinutes(), s: value.getSeconds(), hasTime: true };
  }
  const m = /^(\d{4})-(\d{2})(?:-(\d{2}))?(?:[ T](\d{2}):(\d{2})(?::(\d{2}))?)?/.exec(String(value).trim());
  if (!m) return null;
  return { y: +m[1], mo: +m[2], d: +(m[3] || 1), h: +(m[4] || 0), mi: +(m[5] || 0), s: +(m[6] || 0),
    hasTime: !!m[4], hasDay: !!m[3] };
}

/** Local Date built from stored components (no timezone shifting). */
function asDate(value) {
  const p = parts(value);
  return p ? new Date(p.y, p.mo - 1, p.d, p.h, p.mi, p.s) : null;
}

export const dateOnly = (value) => {
  const p = parts(value);
  return p ? `${p.d} ${MONTHS[p.mo - 1]} ${p.y}` : '—';
};
export const shortDate = (value) => {
  const p = parts(value);
  return p ? `${p.d} ${MONTHS[p.mo - 1]}` : '—';
};
export const timeOnly = (value) => {
  const p = parts(value);
  return p ? `${String(p.h).padStart(2, '0')}:${String(p.mi).padStart(2, '0')}` : '';
};
export const dateTime = (value) => {
  const p = parts(value);
  if (!p) return '—';
  return p.hasTime ? `${p.d} ${MONTHS[p.mo - 1]} ${p.y}, ${String(p.h).padStart(2, '0')}:${String(p.mi).padStart(2, '0')}`
    : `${p.d} ${MONTHS[p.mo - 1]} ${p.y}`;
};
export const dayName = (value, long = false) => {
  const d = asDate(value);
  return d ? (long ? DAYS[d.getDay()] : DAYS[d.getDay()].slice(0, 3)) : '';
};
export const monthLabel = (value, long = false) => {
  const p = parts(value);
  return p ? `${(long ? MONTHS_LONG : MONTHS)[p.mo - 1]} ${p.y}` : '—';
};

/** For <input type="date"> */
export const toDateInput = (value) => {
  const p = parts(value);
  return p ? `${p.y}-${String(p.mo).padStart(2, '0')}-${String(p.d).padStart(2, '0')}` : '';
};
/** For <input type="datetime-local"> */
export const toDateTimeLocal = (value) => {
  const p = parts(value);
  return p ? `${toDateInput(value)}T${String(p.h).padStart(2, '0')}:${String(p.mi).padStart(2, '0')}` : '';
};

export function todayStr() {
  if (CFG.today) return CFG.today;
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

/**
 * A naive wall-clock stamp ('YYYY-MM-DD HH:MM:SS') for `when`, expressed in the
 * BUSINESS timezone rather than the device's.
 *
 * This exists for offline capture. A sale queued on a phone during an outage is
 * replayed hours later, and the handset may be set to any timezone at all. The
 * server stores sale_at as business-local time, so converting here is what stops
 * a Saturday evening sale from being reported on Sunday — or from landing on a
 * day the bakery was shut.
 */
export function localStamp(when = new Date()) {
  const d = when instanceof Date ? when : new Date(when);
  if (Number.isNaN(d.getTime())) return null;
  const pad = (n) => String(n).padStart(2, '0');
  try {
    const p = new Intl.DateTimeFormat('en-CA', {
      timeZone: CFG.timezone, hour12: false,
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
    }).formatToParts(d).reduce((a, x) => { a[x.type] = x.value; return a; }, {});
    // Some engines render midnight as '24' with hour12:false.
    const hour = p.hour === '24' ? '00' : p.hour;
    return `${p.year}-${p.month}-${p.day} ${hour}:${p.minute}:${p.second}`;
  } catch {
    // Unknown timezone: fall back to the device clock. Losing the timezone is
    // better than losing the sale.
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} `
      + `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }
}

export function monthStartStr() {
  if (CFG.monthStart) return CFG.monthStart;
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`;
}

export function shiftDays(dateStr, days) {
  const p = parts(dateStr) ?? parts(todayStr());
  const d = new Date(p.y, p.mo - 1, p.d);
  d.setDate(d.getDate() + days);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

export function relTime(value) {
  const d = asDate(value);
  if (!d) return '—';
  const diff = Date.now() - d.getTime();
  const mins = Math.round(diff / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins} min ago`;
  const hours = Math.round(mins / 60);
  if (hours < 24 && d.getDate() === new Date().getDate()) return `${hours} h ago`;
  const yest = new Date(); yest.setDate(yest.getDate() - 1);
  if (d.toDateString() === yest.toDateString()) return `Yesterday ${timeOnly(value)}`;
  const days = Math.round(diff / 86400000);
  if (days < 7) return `${days} days ago`;
  return dateOnly(value);
}

export const initials = (name) =>
  String(name || '?').trim().split(/[\s(]+/).filter(Boolean).slice(0, 2)
    .map((w) => w[0].toUpperCase()).join('') || '?';

/** '2026-09-01'..'2026-09-27' -> 'Sep 2026' style label for a range picker. */
export function rangeLabel(from, to) {
  const a = parts(from), b = parts(to);
  if (!a || !b) return '';
  if (a.y === b.y && a.mo === b.mo) return `${a.d}–${b.d} ${MONTHS[a.mo - 1]} ${a.y}`;
  if (a.y === b.y) return `${a.d} ${MONTHS[a.mo - 1]} – ${b.d} ${MONTHS[b.mo - 1]} ${a.y}`;
  return `${shortDate(from)} ${a.y} – ${shortDate(to)} ${b.y}`;
}

export const METHOD_LABELS = { cash: 'Cash', mobile: 'Mobile money', card: 'Card', credit: 'On credit' };
export const STATUS_LABELS = { paid: 'Paid', partial: 'Part paid', unpaid: 'Unpaid', void: 'Voided' };
export const KIND_LABELS = { purchase: 'Purchase', usage: 'Used in sale', waste: 'Waste / spoilage', adjustment: 'Adjustment' };

export const methodLabel = (m) => METHOD_LABELS[m] || m;
export const statusLabel = (s) => STATUS_LABELS[s] || s;
export const kindLabel = (k) => KIND_LABELS[k] || k;
