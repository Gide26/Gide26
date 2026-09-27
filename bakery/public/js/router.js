/**
 * Hash router. Hashes (#/sales) rather than history.pushState so the app
 * works when opened from a phone home-screen shortcut or a file preview
 * without any server-side rewrite rules.
 */

const listeners = new Set();

export function currentRoute() {
  const raw = (location.hash || '#/').replace(/^#/, '');
  const [path, search] = raw.split('?');
  const clean = path.startsWith('/') ? path : `/${path}`;
  return {
    path: clean.length > 1 ? clean.replace(/\/+$/, '') : '/',
    params: new URLSearchParams(search || ''),
    raw,
  };
}

export function navigate(to, { replace = false, keepScroll = false } = {}) {
  const target = to.startsWith('#') ? to : `#${to.startsWith('/') ? to : `/${to}`}`;
  if (!keepScroll) scrollTarget = 0;
  if (replace) location.replace(target);
  else location.hash = target;
  // hashchange does not fire when the hash is unchanged, so nudge listeners.
  if (location.hash === target) notify();
}

export function setParams(params, { replace = true } = {}) {
  const { path } = currentRoute();
  const usp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === '') continue;
    usp.set(k, String(v));
  }
  const s = usp.toString();
  const target = `#${path}${s ? `?${s}` : ''}`;
  if (replace) history.replaceState(null, '', target);
  else location.hash = target;
  notify();
}

let scrollTarget = null;
let lastKey = '';
let notifying = false;

function notify() {
  const r = currentRoute();
  const key = r.raw;
  if (key === lastKey || notifying) return;
  lastKey = key;
  notifying = true;
  try { listeners.forEach((fn) => fn(r)); } finally { notifying = false; }
  if (scrollTarget === 0) window.scrollTo({ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' });
}

/** Force a re-render of the current route (used after data changes). */
export function refresh() {
  lastKey = '';
  notify();
}

export function onRoute(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export function start() {
  window.addEventListener('hashchange', notify);
  if (!location.hash) history.replaceState(null, '', '#/');
  notify();
}
