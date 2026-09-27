/**
 * Client-side app state: session, business settings and the shared
 * reference data the POS needs. One bootstrap call keeps phone round-trips
 * (and therefore data cost) low.
 */
import { api, setUnauthorizedHandler, ApiError } from './api.js';
import { setFormatConfig } from './format.js';
import { putCache, syncOutbox } from './offline.js';

export const state = {
  ready: false,
  user: null,
  settings: {},
  meta: null,
  data: null,           // bootstrap payload: products, categories, customers, ingredients
  dataLoadedAt: 0,
  canSeeCosts: false,
  online: typeof navigator === 'undefined' ? true : navigator.onLine,
  serverToday: null,
};

const listeners = new Set();
export const subscribe = (fn) => { listeners.add(fn); return () => listeners.delete(fn); };
const emit = (what) => listeners.forEach((fn) => { try { fn(what, state); } catch (e) { console.error(e); } });

export function applySettings(settings, today) {
  state.settings = settings || {};
  if (today) state.serverToday = today;
  setFormatConfig({
    symbol: state.settings.currency_symbol || 'FBu',
    code: state.settings.currency_code || 'BIF',
    decimals: Number(state.settings.currency_decimals ?? 0),
    timezone: state.settings.timezone,
    businessName: state.settings.business_name,
    today,
    monthStart: today ? `${today.slice(0, 7)}-01` : null,
  });
}

export const isOwner = () => state.user?.role === 'owner';
export const isSignedIn = () => !!state.user;

let unauthorizedHook = () => {};
export const setSessionExpiredHandler = (fn) => { unauthorizedHook = fn; };
setUnauthorizedHandler(() => {
  state.user = null;
  state.data = null;
  unauthorizedHook();
});

/** Restore an existing session from the cookie. Returns the user or null. */
export async function restoreSession() {
  try {
    const me = await api.me();
    state.user = me.user;
    state.canSeeCosts = !!me.canSeeCosts;
    applySettings(me.settings, me.today);
    state.ready = true;
    emit('session');
    return me.user;
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      state.user = null;
      state.ready = true;
      return null;
    }
    throw err;
  }
}

export async function signIn(phone, password) {
  const out = await api.login(phone, password);
  state.user = out.user;
  state.canSeeCosts = out.user.role === 'owner';
  applySettings(out.settings, out.today);
  state.data = null;
  state.ready = true;
  emit('session');
  return out.user;
}

export async function completeSetup(payload) {
  const out = await api.setup(payload);
  state.user = out.user;
  state.canSeeCosts = true;
  applySettings(out.settings, out.today);
  state.ready = true;
  emit('session');
  return out.user;
}

export async function signOut() {
  try { await api.logout(); } catch { /* ignore — clear locally regardless */ }
  state.user = null;
  state.data = null;
  state.canSeeCosts = false;
  emit('session');
}

/**
 * Reference data with a short freshness window so switching tabs does not
 * re-download everything, but a new product still shows up promptly.
 */
export async function loadData({ maxAgeMs = 45_000, force = false } = {}) {
  if (!force && state.data && Date.now() - state.dataLoadedAt < maxAgeMs) return state.data;
  const [data, meta] = await Promise.all([api.bootstrap(), state.meta ? Promise.resolve(state.meta) : api.meta()]);
  state.data = data;
  state.meta = meta;
  state.canSeeCosts = !!data.canSeeCosts;
  if (data.settings) applySettings(data.settings, data.today);
  state.dataLoadedAt = Date.now();

  // Snapshot the reference data so the till still has products, prices and
  // customers to render if the connection drops later. Stock quantities are
  // deliberately left out of this: a stale quantity on a till is worse than no
  // quantity, so the offline UI hides them instead of lying.
  putCache('bootstrap', data);

  emit('data');
  return data;
}

export const invalidate = () => { state.dataLoadedAt = 0; };

/* Offline awareness — a phone in a low-signal area needs to know, and anything
 * queued while offline must be flushed the moment the connection returns. */
if (typeof window !== 'undefined') {
  const set = () => {
    const wasOffline = !state.online;
    state.online = navigator.onLine;
    emit('online');
    if (state.online && wasOffline) syncOutbox();
  };
  window.addEventListener('online', set);
  window.addEventListener('offline', set);
}
