/**
 * UI primitives: icon set, toasts, bottom-sheet/modal dialogs, confirm
 * prompts, empty states, and the shared date-range picker.
 */
import { esc, todayStr, monthStartStr, shiftDays, dateOnly, rangeLabel } from './format.js';

/* ------------------------------------------------------------------ *
 * Icons — inline SVG, stroke-based, inherit currentColor
 * ------------------------------------------------------------------ */

const ICONS = {
  home: '<path d="M3 10.6 12 3.2l9 7.4V20a1.4 1.4 0 0 1-1.4 1.4h-4.3v-6.3H8.7v6.3H4.4A1.4 1.4 0 0 1 3 20z"/>',
  cart: '<circle cx="9.5" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M2 3h2.3l2.4 12.3a1.8 1.8 0 0 0 1.8 1.4h8.9a1.8 1.8 0 0 0 1.8-1.4L21 7.2H5.1"/>',
  receipt: '<path d="M5.5 2.8v18.4l2.3-1.5 2.2 1.5 2-1.5 2 1.5 2.2-1.5 2.3 1.5V2.8l-2.3 1.5-2.2-1.5-2 1.5-2-1.5-2.2 1.5z"/><path d="M9 8.5h6M9 12.5h6M9 16h3.5"/>',
  box: '<path d="M21 8.2 12 3 3 8.2v7.6L12 21l9-5.2z"/><path d="m3 8.2 9 5.2 9-5.2M12 13.4V21"/>',
  wallet: '<path d="M20 12.5V8H6.2A2.2 2.2 0 0 1 6.2 3.6H19V8"/><path d="M4 5.8v12.4a2.2 2.2 0 0 0 2.2 2.2h14.3v-4.2"/><path d="M21.5 12.2a2 2 0 0 0-2-2h-3.8a2 2 0 0 0 0 4h3.8a2 2 0 0 0 2-2z"/>',
  users: '<path d="M16.5 20.5v-1.8a3.8 3.8 0 0 0-3.8-3.8H5.8A3.8 3.8 0 0 0 2 18.7v1.8"/><circle cx="9.2" cy="7.4" r="3.6"/><path d="M22 20.5v-1.8a3.8 3.8 0 0 0-2.9-3.7M16.4 3.9a3.8 3.8 0 0 1 0 7.1"/>',
  chart: '<path d="M6 20.5v-6M12 20.5V4M18 20.5v-9"/><path d="M3 20.5h18"/>',
  settings: '<path d="M4 21v-6.5M4 10.5V3M12 21v-9M12 8V3M20 21v-4.5M20 12.5V3"/><path d="M1.5 14.5h5M9.5 8h5M17.5 16.5h5"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  minus: '<path d="M5 12h14"/>',
  search: '<circle cx="11" cy="11" r="7.2"/><path d="m21 21-4.4-4.4"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  check: '<path d="m20 6.5-11 11-5-5"/>',
  trash: '<path d="M3.5 6.2h17M8.5 6.2V4.4a1.2 1.2 0 0 1 1.2-1.2h4.6a1.2 1.2 0 0 1 1.2 1.2v1.8"/><path d="m18.4 6.2-.9 13.4a2 2 0 0 1-2 1.9H8.5a2 2 0 0 1-2-1.9L5.6 6.2"/><path d="M10.2 10.6v6.4M13.8 10.6v6.4"/>',
  pencil: '<path d="M12.5 20.5H21"/><path d="M16.4 3.6a2.1 2.1 0 0 1 3 3L7.6 18.4l-4 1 1-4z"/>',
  chevronRight: '<path d="m9 18 6-6-6-6"/>',
  chevronDown: '<path d="m6 9.5 6 6 6-6"/>',
  chevronLeft: '<path d="m15 18-6-6 6-6"/>',
  alert: '<path d="M10.3 3.9 1.9 18a2 2 0 0 0 1.7 3h16.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9.2v4.3M12 17.2h.01"/>',
  clock: '<circle cx="12" cy="12" r="9.2"/><path d="M12 6.8V12l3.4 2"/>',
  calendar: '<rect x="3.2" y="4.8" width="17.6" height="16.4" rx="2.2"/><path d="M16.2 2.6v4.4M7.8 2.6v4.4M3.2 10.2h17.6"/>',
  download: '<path d="M20.8 15.2v3.6a2.2 2.2 0 0 1-2.2 2.2H5.4a2.2 2.2 0 0 1-2.2-2.2v-3.6"/><path d="m7.4 10.4 4.6 4.6 4.6-4.6M12 15V3.2"/>',
  printer: '<path d="M6.5 9.2V2.8h11v6.4"/><path d="M6.5 18.2H4.6a2 2 0 0 1-2-2v-4.8a2 2 0 0 1 2-2h14.8a2 2 0 0 1 2 2v4.8a2 2 0 0 1-2 2h-1.9"/><rect x="6.5" y="14.2" width="11" height="7" rx="1"/><path d="M17.8 6.2h.01"/>',
  logout: '<path d="M9.5 21H5.4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4.1"/><path d="m16.2 16.8 4.8-4.8-4.8-4.8M21 12H9.4"/>',
  user: '<circle cx="12" cy="8" r="4.1"/><path d="M4.2 21v-.9a6.2 6.2 0 0 1 6.2-6.2h3.2a6.2 6.2 0 0 1 6.2 6.2v.9"/>',
  shield: '<path d="M12 21.8s8-3.8 8-9.8V5.3L12 2.4 4 5.3V12c0 6 8 9.8 8 9.8z"/><path d="m9 12 2.2 2.2L15.4 10"/>',
  bread: '<path d="M3.6 12.4c0-3.4 3.8-6.2 8.4-6.2s8.4 2.8 8.4 6.2v3.2a2.2 2.2 0 0 1-2.2 2.2H5.8a2.2 2.2 0 0 1-2.2-2.2z"/><path d="M8.6 10.4c.7.9.7 2.3 0 3.2M12 10c.7 1 .7 2.6 0 3.6M15.4 10.4c.7.9.7 2.3 0 3.2"/>',
  arrowUp: '<path d="M12 19.5v-15M5.2 11.3 12 4.5l6.8 6.8"/>',
  arrowDown: '<path d="M12 4.5v15M18.8 12.7 12 19.5l-6.8-6.8"/>',
  arrowUpRight: '<path d="M7 17 17 7M8.4 7H17v8.6"/>',
  trending: '<path d="M22 7.4 13.6 15.8 8.8 11 2 17.8"/><path d="M16.2 7.4H22v5.8"/>',
  more: '<circle cx="12" cy="5.2" r="1.4"/><circle cx="12" cy="12" r="1.4"/><circle cx="12" cy="18.8" r="1.4"/>',
  refresh: '<path d="M20.8 12a8.8 8.8 0 1 1-2.6-6.2"/><path d="M21 3.4v5.8h-5.8"/>',
  filter: '<path d="M3.4 5.2h17.2l-6.8 8v5.9l-3.6 1.8v-7.7z"/>',
  phone: '<path d="M21.6 16.9v2.7a2 2 0 0 1-2.2 2 19.6 19.6 0 0 1-8.5-3 19.3 19.3 0 0 1-6-6 19.6 19.6 0 0 1-3-8.6 2 2 0 0 1 2-2.2h2.7a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L7.9 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.4c.9.3 1.8.5 2.8.7a2 2 0 0 1 1.6 2z"/>',
  pin: '<path d="M20.6 10.2c0 6.4-8.6 12.2-8.6 12.2s-8.6-5.8-8.6-12.2a8.6 8.6 0 0 1 17.2 0z"/><circle cx="12" cy="10" r="3.1"/>',
  card: '<rect x="2.2" y="5" width="19.6" height="14" rx="2.2"/><path d="M2.2 10h19.6M6.2 15h3"/>',
  cash: '<rect x="2.2" y="6" width="19.6" height="12" rx="2.2"/><circle cx="12" cy="12" r="2.6"/><path d="M6.2 12h.01M17.8 12h.01"/>',
  mobile: '<rect x="6.2" y="2.4" width="11.6" height="19.2" rx="2.4"/><path d="M10.8 18.4h2.4"/>',
  credit: '<path d="M12 3.2v17.6M8 7.2 12 3.2l4 4"/><path d="M4.4 12.4v6a2.4 2.4 0 0 0 2.4 2.4h10.4a2.4 2.4 0 0 0 2.4-2.4v-6"/>',
  info: '<circle cx="12" cy="12" r="9.2"/><path d="M12 16.4v-4.8M12 8h.01"/>',
  lock: '<rect x="4.2" y="10.8" width="15.6" height="10.4" rx="2.2"/><path d="M8 10.8V7.2a4 4 0 0 1 8 0v3.6"/>',
  eye: '<path d="M1.6 12S5.8 5.2 12 5.2 22.4 12 22.4 12 18.2 18.8 12 18.8 1.6 12 1.6 12z"/><circle cx="12" cy="12" r="3.2"/>',
  tag: '<path d="M20.4 13.3 12.9 20.8a2 2 0 0 1-2.8 0L3.4 14V4.6a1.2 1.2 0 0 1 1.2-1.2H14l6.4 6.4a2 2 0 0 1 0 2.8z"/><circle cx="8" cy="8" r="1.3"/>',
  percent: '<path d="M19 5 5 19"/><circle cx="7.6" cy="7.6" r="2.4"/><circle cx="16.4" cy="16.4" r="2.4"/>',
  store: '<path d="M3.4 9.2 5.6 3.2h12.8l2.2 6"/><path d="M4.4 9.2v10.4a1.4 1.4 0 0 0 1.4 1.4h12.4a1.4 1.4 0 0 0 1.4-1.4V9.2"/><path d="M3.4 9.2h17.2M9.4 21v-6h5.2v6"/>',
  truck: '<path d="M2.8 6.4h11v10.4h-11z"/><path d="M13.8 10h3.6l3 3v3.8h-6.6z"/><circle cx="6.6" cy="18.6" r="1.8"/><circle cx="17" cy="18.6" r="1.8"/>',
  flask: '<path d="M9.4 3.2h5.2M10.4 3.2v6L4.9 18.4a2 2 0 0 0 1.7 3h10.8a2 2 0 0 0 1.7-3l-5.5-9.2v-6"/><path d="M7.6 14.6h8.8"/>',
  layers: '<path d="m12 2.8 9.2 4.8L12 12.4 2.8 7.6z"/><path d="m2.8 12.4 9.2 4.8 9.2-4.8M2.8 17.2 12 22l9.2-4.8"/>',
  database: '<ellipse cx="12" cy="5.6" rx="8.4" ry="3.2"/><path d="M3.6 5.6v12.8c0 1.8 3.8 3.2 8.4 3.2s8.4-1.4 8.4-3.2V5.6"/><path d="M3.6 12c0 1.8 3.8 3.2 8.4 3.2s8.4-1.4 8.4-3.2"/>',
  key: '<circle cx="7.8" cy="15.6" r="4.2"/><path d="m10.8 12.6 8-8M16.6 6.8l2.2 2.2M19 4.4l2.2 2.2"/>',
  list: '<path d="M8.4 6.2h12.4M8.4 12h12.4M8.4 17.8h12.4M3.6 6.2h.01M3.6 12h.01M3.6 17.8h.01"/>',
  star: '<path d="m12 3.2 2.7 5.6 6.1.9-4.4 4.3 1 6.1-5.4-2.9-5.4 2.9 1-6.1L3.2 9.7l6.1-.9z"/>',
  gift: '<rect x="3.2" y="8.4" width="17.6" height="4.2" rx="1"/><path d="M4.8 12.6v7a1.6 1.6 0 0 0 1.6 1.6h11.2a1.6 1.6 0 0 0 1.6-1.6v-7M12 8.4v12.8"/><path d="M12 8.4S10.8 3.2 8.2 3.2a2.6 2.6 0 0 0 0 5.2zM12 8.4s1.2-5.2 3.8-5.2a2.6 2.6 0 0 1 0 5.2z"/>',
  wifiOff: '<path d="m2 2 20 20M8.4 15.6a5 5 0 0 1 7 0M5 12.4a10 10 0 0 1 3.4-2.2M2.2 8.8A15 15 0 0 1 7 5.8M19 12.4a10 10 0 0 0-2.4-1.7M21.8 8.8a15 15 0 0 0-6.2-3.4M12 19.6h.01"/>',
  dot: '<circle cx="12" cy="12" r="4"/>',
};

export function icon(name, opts = {}) {
  const { size = 20, cls = '', stroke = 1.85, fill = 'none' } = opts;
  const body = ICONS[name] || ICONS.dot;
  return `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="${fill}" stroke="currentColor" `
    + `stroke-width="${stroke}" stroke-linecap="round" stroke-linejoin="round" `
    + `class="ic${cls ? ` ${cls}` : ''}" aria-hidden="true" focusable="false">${body}</svg>`;
}

/* ------------------------------------------------------------------ *
 * DOM helpers
 * ------------------------------------------------------------------ */

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

/**
 * Event delegation: bind once on a container, match on a selector.
 * Returns an unbind function.
 */
export function on(root, event, selector, handler, opts) {
  const listener = (e) => {
    const el = e.target.closest(selector);
    if (!el || !root.contains(el)) return;
    handler(e, el);
  };
  root.addEventListener(event, listener, opts);
  return () => root.removeEventListener(event, listener, opts);
}

export function scrollLock(on_) {
  document.body.style.overflow = on_ ? 'hidden' : '';
}

/* ------------------------------------------------------------------ *
 * Toasts
 * ------------------------------------------------------------------ */

let toastHost = null;
const TOAST_ICON = { ok: 'check', bad: 'alert', warn: 'alert', info: 'info' };

export function toast(message, type = 'info', ms = 3400) {
  if (!toastHost) {
    toastHost = document.createElement('div');
    toastHost.className = 'toasts';
    toastHost.setAttribute('aria-live', 'polite');
    document.body.appendChild(toastHost);
  }
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `${icon(TOAST_ICON[type] || 'info', { size: 18 })}<div class="grow">${esc(message)}</div>`;
  toastHost.appendChild(el);
  const kill = () => {
    el.classList.add('out');
    setTimeout(() => el.remove(), 200);
  };
  el.addEventListener('click', kill);
  setTimeout(kill, ms);
  // Keep at most three visible.
  while (toastHost.children.length > 3) toastHost.firstElementChild.remove();
  return kill;
}

export const toastError = (err) => toast(err?.message || String(err) || 'Something went wrong', 'bad', 5000);
export const toastOk = (msg) => toast(msg, 'ok');

/* ------------------------------------------------------------------ *
 * Sheets / modals
 * ------------------------------------------------------------------ */

let openSheets = 0;

/**
 * Opens a bottom sheet (phone) / centred dialog (computer).
 * @returns {function} close
 */
export function sheet({ title, body, footer = '', wide = false, subtitle = '', onMount, onClose }) {
  const overlay = document.createElement('div');
  overlay.className = 'overlay';
  overlay.innerHTML = `
    <div class="sheet${wide ? ' wide' : ''}" role="dialog" aria-modal="true" aria-label="${esc(title)}">
      <div class="grabber"></div>
      <div class="sheet-head">
        <div class="grow">
          <h3>${esc(title)}</h3>
          ${subtitle ? `<div class="small muted">${esc(subtitle)}</div>` : ''}
        </div>
        <button type="button" class="btn btn-ghost btn-icon btn-sm" data-close aria-label="Close">${icon('x', { size: 19 })}</button>
      </div>
      <div class="sheet-body">${body}</div>
      ${footer ? `<div class="sheet-foot">${footer}</div>` : ''}
    </div>`;

  const close = () => {
    if (overlay.dataset.closing) return;
    overlay.dataset.closing = '1';
    overlay.remove();
    openSheets = Math.max(0, openSheets - 1);
    if (openSheets === 0) scrollLock(false);
    onClose?.();
  };

  overlay.addEventListener('click', (e) => {
    if (e.target === overlay || e.target.closest('[data-close]')) close();
  });
  const onKey = (e) => {
    if (e.key === 'Escape' && openSheets > 0) {
      e.stopPropagation();
      close();
      document.removeEventListener('keydown', onKey, true);
    }
  };
  document.addEventListener('keydown', onKey, true);

  document.body.appendChild(overlay);
  openSheets += 1;
  scrollLock(true);

  onMount?.(overlay.querySelector('.sheet'), close);
  const first = overlay.querySelector('input, select, textarea, button.btn-primary');
  if (first && window.innerWidth >= 700) setTimeout(() => first.focus({ preventScroll: true }), 60);
  return close;
}

/** Promise-based confirmation. */
export function confirmDialog({ title = 'Are you sure?', message = '', confirmLabel = 'Confirm',
  cancelLabel = 'Cancel', danger = false, body = '' }) {
  return new Promise((resolve) => {
    let settled = false;
    const finish = (v) => { if (!settled) { settled = true; resolve(v); } };
    const close = sheet({
      title,
      body: `${message ? `<p>${esc(message)}</p>` : ''}${body}`,
      footer: `
        <button type="button" class="btn" data-no>${esc(cancelLabel)}</button>
        <button type="button" class="btn ${danger ? 'btn-danger' : 'btn-primary'}" data-yes>${esc(confirmLabel)}</button>`,
      onClose: () => finish(false),
      onMount: (el) => {
        el.querySelector('[data-no]').addEventListener('click', () => { finish(false); close(); });
        el.querySelector('[data-yes]').addEventListener('click', () => { finish(true); close(); });
        setTimeout(() => el.querySelector('[data-yes]')?.focus({ preventScroll: true }), 80);
      },
    });
  });
}

/* ------------------------------------------------------------------ *
 * Buttons & states
 * ------------------------------------------------------------------ */

export function busy(btn, isBusy, label) {
  if (!btn) return;
  if (isBusy) {
    if (!btn.dataset.origHtml) btn.dataset.origHtml = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = `<span class="spinner${btn.classList.contains('btn-primary') || btn.classList.contains('btn-dark') ? ' light' : ''}"></span>${label ? esc(label) : ''}`;
  } else {
    btn.disabled = false;
    if (btn.dataset.origHtml) { btn.innerHTML = btn.dataset.origHtml; delete btn.dataset.origHtml; }
  }
}

export function emptyState({ icon: ic = 'box', title = 'Nothing here yet', message = '', action = '' }) {
  return `<div class="empty">${icon(ic, { size: 40, stroke: 1.5 })}<h4>${esc(title)}</h4>
    ${message ? `<p>${esc(message)}</p>` : ''}${action}</div>`;
}

export const skeletons = (rows = 4) =>
  `<div class="card-body stack">${Array.from({ length: rows }, () =>
    '<div class="skeleton" style="height:38px"></div>').join('')}</div>`;

/* ------------------------------------------------------------------ *
 * Date range picker — shared by Sales, Expenses and Reports
 * ------------------------------------------------------------------ */

export const RANGE_PRESETS = {
  today: () => ({ from: todayStr(), to: todayStr(), label: 'Today' }),
  yesterday: () => { const d = shiftDays(todayStr(), -1); return { from: d, to: d, label: 'Yesterday' }; },
  week: () => ({ from: shiftDays(todayStr(), -6), to: todayStr(), label: 'Last 7 days' }),
  month: () => ({ from: monthStartStr(), to: todayStr(), label: 'This month' }),
  lastMonth: () => {
    const t = todayStr();
    const first = `${t.slice(0, 7)}-01`;
    const prevEnd = shiftDays(first, -1);
    return { from: `${prevEnd.slice(0, 7)}-01`, to: prevEnd, label: 'Last month' };
  },
  quarter: () => ({ from: shiftDays(todayStr(), -89), to: todayStr(), label: 'Last 90 days' }),
};

export function defaultRange() {
  return { from: monthStartStr(), to: todayStr() };
}

/** Which preset a range matches, if any. */
export function matchPreset(from, to) {
  for (const [key, fn] of Object.entries(RANGE_PRESETS)) {
    const r = fn();
    if (r.from === from && r.to === to) return key;
  }
  return 'custom';
}

/**
 * Renders the preset chips + custom date inputs.
 * The host element must carry data-from / data-to and is updated in place.
 */
export function rangePickerHtml(from, to, { compact = false } = {}) {
  const active = matchPreset(from, to);
  const chips = Object.entries(RANGE_PRESETS)
    .filter(([k]) => (compact ? ['today', 'week', 'month'].includes(k) : true))
    .map(([k, fn]) => `<button type="button" class="chip${active === k ? ' active' : ''}" data-preset="${k}">${esc(fn().label)}</button>`)
    .join('');
  return `
    <div class="stack" style="gap:9px">
      <div class="chips">${chips}</div>
      <div class="row wrap" style="gap:8px">
        <input type="date" data-range-from value="${esc(from)}" aria-label="From date" style="flex:1 1 140px;min-width:0">
        <span class="muted small">to</span>
        <input type="date" data-range-to value="${esc(to)}" aria-label="To date" style="flex:1 1 140px;min-width:0">
      </div>
      <div class="small muted" data-range-label>${esc(rangeLabel(from, to))}</div>
    </div>`;
}

/**
 * Wires up a rendered range picker.
 * @param {HTMLElement} host  container holding the markup
 * @param {{from:string,to:string}} state
 * @param {(range:{from:string,to:string}) => void} onChange
 */
export function bindRangePicker(host, state, onChange) {
  if (!host) return () => {};
  const sync = () => {
    const from = $('[data-range-from]', host);
    const to = $('[data-range-to]', host);
    const label = $('[data-range-label]', host);
    if (from) from.value = state.from;
    if (to) to.value = state.to;
    if (label) label.textContent = rangeLabel(state.from, state.to);
    const active = matchPreset(state.from, state.to);
    $$('[data-preset]', host).forEach((b) => b.classList.toggle('active', b.dataset.preset === active));
  };

  const offChip = on(host, 'click', '[data-preset]', (_e, el) => {
    const fn = RANGE_PRESETS[el.dataset.preset];
    if (!fn) return;
    const r = fn();
    state.from = r.from; state.to = r.to;
    sync(); onChange({ ...state });
  });
  const offFrom = on(host, 'change', '[data-range-from]', (_e, el) => {
    state.from = el.value || state.from;
    if (state.from > state.to) state.to = state.from;
    sync(); onChange({ ...state });
  });
  const offTo = on(host, 'change', '[data-range-to]', (_e, el) => {
    state.to = el.value || state.to;
    if (state.to < state.from) state.from = state.to;
    sync(); onChange({ ...state });
  });

  sync();
  return () => { offChip(); offFrom(); offTo(); };
}

export { dateOnly };
