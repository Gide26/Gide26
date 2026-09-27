/**
 * App shell: navigation, auth gate, route rendering.
 * Views are lazy-loaded so the first paint on a phone stays quick.
 */
import { state, restoreSession, signOut, subscribe, setSessionExpiredHandler, isOwner } from './store.js';
import { icon, $, toast, on } from './ui.js';
import { esc, initials } from './format.js';
import { currentRoute, navigate, onRoute, start } from './router.js';
import { initOffline, onOutboxChange, syncStatus, syncOutbox } from './offline.js';

/* ------------------------------------------------------------------ *
 * Route table
 * ------------------------------------------------------------------ */

const NAV = [
  { path: '/', label: 'Home', icon: 'home', group: 'Every day', primary: true,
    view: () => import('./views/dashboard.js') },
  { path: '/sell', label: 'Sell', icon: 'cart', group: 'Every day', primary: true,
    view: () => import('./views/pos.js') },
  { path: '/sales', label: 'Sales', icon: 'receipt', group: 'Every day', primary: true,
    view: () => import('./views/sales.js') },
  { path: '/stock', label: 'Stock', icon: 'box', group: 'Manage', primary: true,
    view: () => import('./views/inventory.js') },
  { path: '/products', label: 'Products', icon: 'tag', group: 'Manage',
    view: () => import('./views/products.js') },
  { path: '/expenses', label: 'Expenses', icon: 'wallet', group: 'Manage',
    view: () => import('./views/expenses.js') },
  { path: '/customers', label: 'Customers', icon: 'users', group: 'Manage',
    view: () => import('./views/customers.js') },
  { path: '/reports', label: 'Reports', icon: 'chart', group: 'Insight', ownerOnly: true,
    view: () => import('./views/reports.js') },
  { path: '/settings', label: 'Settings', icon: 'settings', group: 'Account',
    view: () => import('./views/settings.js') },
  { path: '/more', label: 'More', icon: 'more', primary: true, mobileOnly: true,
    view: () => import('./views/more.js') },
];

const GROUP_ORDER = ['Every day', 'Manage', 'Insight', 'Account'];

const findNav = (path) => NAV.find((n) => n.path === path);
const visible = (entry) => !entry.ownerOnly || isOwner();

/* ------------------------------------------------------------------ *
 * Shell
 * ------------------------------------------------------------------ */

let viewHost = null;
let renderToken = 0;
let cleanup = null;
let offlineUnsub = null;
let outboxUnsub = null;

function shellHtml() {
  const business = esc(state.settings.business_name || 'Bakery Tracker');

  const sideLinks = NAV.filter((n) => !n.mobileOnly && visible(n))
    .reduce((acc, n) => {
      (acc[n.group] ||= []).push(
        `<a href="#${n.path}" data-nav="${n.path}">${icon(n.icon)}<span>${esc(n.label)}</span></a>`);
      return acc;
    }, {});

  const sidebar = GROUP_ORDER.filter((g) => sideLinks[g])
    .map((g) => `<div class="side-group">${esc(g)}</div>${sideLinks[g].join('')}`).join('');

  const tabs = NAV.filter((n) => n.primary && visible(n))
    .map((n) => `<a href="#${n.path}" data-nav="${n.path}" aria-label="${esc(n.label)}">
        ${icon(n.icon, { size: 22 })}<span>${esc(n.label)}</span></a>`).join('');

  return `
  <div class="app">
    <aside class="sidebar">
      <div class="brandmark">
        <span class="brandmark-logo"><img src="/icons/icon-192.png" alt=""></span>
        <span style="min-width:0">
          <span class="brandmark-name">${business}</span>
          <span class="brandmark-sub">${esc(state.settings.tagline || 'Bakery Tracker')}</span>
        </span>
      </div>
      ${sidebar}
      <div class="side-foot">
        <div class="side-user">
          <span class="avatar" data-avatar>${esc(initials(state.user?.name))}</span>
          <span style="min-width:0" class="grow">
            <span class="side-user-name">${esc(state.user?.name || '')}</span>
            <span class="side-user-role">${state.user?.role === 'owner' ? 'Owner' : 'Staff'}</span>
          </span>
          <button type="button" class="btn btn-ghost btn-icon btn-sm" data-logout title="Sign out"
            style="color:#B9A48F">${icon('logout', { size: 18 })}</button>
        </div>
      </div>
    </aside>

    <div class="content">
      <div id="offline-bar"></div>
      <header class="topbar">
        <span class="avatar" style="width:30px;height:30px;flex-basis:30px;font-size:12px" data-avatar>
          ${esc(initials(state.user?.name))}</span>
        <div class="grow" style="min-width:0">
          <div class="topbar-title" data-title>Home</div>
          <div class="topbar-sub">${business}</div>
        </div>
        <button type="button" class="btn btn-ghost btn-icon btn-sm" data-logout aria-label="Sign out">
          ${icon('logout', { size: 19 })}</button>
      </header>
      <div id="banner"></div>
      <main class="main" id="view"></main>
    </div>

    <nav class="tabbar" aria-label="Main">${tabs}</nav>
  </div>`;
}

function mountShell() {
  const app = $('#app');
  app.innerHTML = shellHtml();
  viewHost = $('#view');

  on(app, 'click', '[data-logout]', async () => {
    await signOut();
    showLogin();
  });

  renderBanner();
  renderOffline();

  if (offlineUnsub) offlineUnsub();
  offlineUnsub = subscribe((what) => {
    if (what === 'online') renderOffline();
    if (what === 'session') { renderBanner(); paintNav(); }
  });

  // The queue changes underneath us (a sync finishes, an item is added from the
  // till), so keep the banner honest without the views having to remember to.
  if (outboxUnsub) outboxUnsub();
  outboxUnsub = onOutboxChange(() => renderOffline());

  on(document.body, 'click', '[data-sync-now]', async (_e, el) => {
    el.disabled = true;
    const out = await syncOutbox();
    toast(out.synced
      ? `Sent ${out.synced} queued ${out.synced === 1 ? 'item' : 'items'}`
      : (out.offline ? 'Still no connection' : 'Nothing new to send'), out.synced ? 'ok' : 'warn');
    el.disabled = false;
  });
}

/**
 * The connection banner. It has to be precise, because a cashier reading it
 * during a power cut needs to know whether the sale they just took is safe.
 * Three distinct states: offline with work queued, offline with none, and back
 * online but still holding items that need attention.
 */
function renderOffline() {
  const host = $('#offline-bar');
  if (!host) return;
  const st = syncStatus();

  if (!state.online) {
    const held = st.count
      ? `${st.count} ${st.count === 1 ? 'item is' : 'items are'} saved on this device and will send automatically`
      : 'anything you record is saved on this device and will send automatically';
    host.innerHTML = `
      <div class="offline-bar">${icon('wifiOff', { size: 14 })} You are offline — keep trading.
      ${held} when the connection returns.</div>`;
    return;
  }

  // Online, but the queue is not empty: either a sync is running or something
  // was rejected and needs a human. Both are worth saying out loud.
  if (st.count > 0) {
    const detail = st.failed
      ? `${st.failed} need${st.failed === 1 ? 's' : ''} your attention`
      : st.syncing ? 'sending now' : 'waiting to send';
    host.innerHTML = `
      <div class="offline-bar warn">${icon('refresh', { size: 14 })} ${st.count} queued
      ${st.count === 1 ? 'item' : 'items'} — ${detail}.
      <button type="button" class="btn btn-ghost btn-sm" data-sync-now>Send now</button></div>`;
    return;
  }

  host.innerHTML = '';
}

/** Persistent nudge while a seeded/temporary password is still in use. */
function renderBanner() {
  const host = $('#banner');
  if (!host) return;
  if (!state.user?.must_change) { host.innerHTML = ''; return; }
  host.innerHTML = `
    <div style="padding:10px 12px 0;max-width:1280px;margin:0 auto">
      <div class="pill-note bad">
        ${icon('lock', { size: 17 })}
        <div class="grow">
          <strong>Change your password.</strong> You are still using the temporary one from setup.
          <div class="row" style="gap:8px;margin-top:8px">
            <button type="button" class="btn btn-sm btn-danger" data-fix-password>Change it now</button>
            <button type="button" class="btn btn-sm btn-ghost" data-dismiss-banner>Later</button>
          </div>
        </div>
      </div>
    </div>`;
  on(host, 'click', '[data-fix-password]', () => navigate('/settings?tab=password'));
  on(host, 'click', '[data-dismiss-banner]', () => { host.innerHTML = ''; });
}

function paintNav() {
  const { path } = currentRoute();
  document.querySelectorAll('[data-nav]').forEach((a) => {
    a.classList.toggle('active', a.dataset.nav === path);
  });
  const entry = findNav(path);
  const title = $('[data-title]');
  if (title) title.textContent = entry?.label || 'Bakery Tracker';
  document.title = `${entry?.label || 'Bakery'} · ${state.settings.business_name || 'Bakery Tracker'}`;
}

/* ------------------------------------------------------------------ *
 * Route rendering
 * ------------------------------------------------------------------ */

async function renderRoute(route) {
  const token = ++renderToken;
  const entry = findNav(route.path);

  if (typeof cleanup === 'function') { try { cleanup(); } catch { /* ignore */ } cleanup = null; }

  if (!entry) {
    viewHost.innerHTML = `<div class="card"><div class="empty">
      ${icon('search', { size: 40, stroke: 1.5 })}
      <h4>Page not found</h4><p>Nothing lives at <code>${esc(route.path)}</code>.</p>
      <button class="btn btn-primary btn-sm" data-home>Back to Home</button></div></div>`;
    on(viewHost, 'click', '[data-home]', () => navigate('/'));
    return;
  }

  if (entry.ownerOnly && !isOwner()) {
    toast('That page is for the owner only', 'warn');
    navigate('/', { replace: true });
    return;
  }

  paintNav();
  viewHost.innerHTML = `<div class="loading-page"><div class="spinner"></div>
    <div class="small muted">Loading ${esc(entry.label)}…</div></div>`;

  try {
    const mod = await entry.view();
    if (token !== renderToken) return; // a newer navigation already won
    viewHost.innerHTML = '';
    cleanup = await mod.render(viewHost, { params: route.params, route, navigate });
    if (typeof cleanup !== 'function') cleanup = null;
  } catch (err) {
    if (token !== renderToken) return;
    console.error('[view error]', err);
    viewHost.innerHTML = `<div class="card"><div class="empty">
      ${icon('alert', { size: 40, stroke: 1.5 })}
      <h4>Could not load this page</h4>
      <p>${esc(err?.message || 'Unexpected error')}</p>
      <button class="btn btn-primary btn-sm" data-retry>Try again</button></div></div>`;
    on(viewHost, 'click', '[data-retry]', () => { renderToken = 0; renderRoute(currentRoute()); });
  }
}

/* ------------------------------------------------------------------ *
 * Auth screens
 * ------------------------------------------------------------------ */

async function showLogin() {
  if (typeof cleanup === 'function') { try { cleanup(); } catch { /* ignore */ } cleanup = null; }
  renderToken++;
  const app = $('#app');
  app.innerHTML = `<div class="loading-page"><div class="spinner"></div></div>`;
  const { render } = await import('./views/login.js');
  app.innerHTML = '';
  cleanup = await render(app, { onSignedIn: showApp });
  if (typeof cleanup !== 'function') cleanup = null;
}

async function showApp() {
  mountShell();
  onRoute(renderRoute);
  start();
  // Make sure reference data is warm for the POS before the user taps Sell.
  import('./store.js').then(({ loadData }) => loadData().catch(() => {}));
}

/* ------------------------------------------------------------------ *
 * Boot
 * ------------------------------------------------------------------ */

/**
 * Report uncaught browser errors to the server, which prints them in its
 * terminal. A page that "does nothing" on click is nearly always throwing
 * somewhere invisible, and the terminal is the one place the owner watches.
 */
function reportClientError(message, extra = {}) {
  try {
    fetch('/api/client-log', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ message, ...extra, ua: navigator.userAgent, href: location.href }),
      keepalive: true,
    }).catch(() => { /* the report must never become another error */ });
  } catch { /* ignore */ }
}

/**
 * Escape hatch for a poisoned cache: /?fresh=1 unregisters every service
 * worker and deletes every cache, then reloads once.
 *
 * The shell is cache-first by design, which is exactly what makes a half-written
 * or outdated cached module hard to shake — the symptom is a page whose buttons
 * stop doing anything at all. This gives the owner a single address that always
 * gets back to a known-good state, without touching their data.
 */
async function dropCachesAndReload() {
  try {
    if ('serviceWorker' in navigator) {
      const regs = await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map((r) => r.unregister()));
    }
    if ('caches' in window) {
      for (const key of await caches.keys()) await caches.delete(key);
    }
  } catch { /* best effort */ }
  location.replace(location.pathname + location.hash);
}

async function boot() {
  if (location.search.includes('fresh=1')) {
    await dropCachesAndReload();
    return;
  }

  window.addEventListener('error', (e) => reportClientError(e.message || 'unknown error',
    { src: e.filename, line: e.lineno }));
  window.addEventListener('unhandledrejection', (e) =>
    reportClientError(`unhandled rejection: ${e.reason?.message || e.reason || 'unknown'}`));

  setSessionExpiredHandler(() => {
    toast('You were signed out — please sign in again', 'warn');
    showLogin();
  });

  // Open the offline store first and flush anything left from a previous
  // session — a phone that was closed mid-outage still owes us those sales.
  const offline = await initOffline();
  if (!offline.available) console.warn('Offline capture unavailable:', offline.reason);

  // Warm the format config from whatever settings we already have.
  try {
    await restoreSession();
  } catch (err) {
    console.warn('Session restore failed:', err?.message);
  }

  if (state.user) showApp();
  else showLogin();

  if ('serviceWorker' in navigator && location.protocol !== 'file:') {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch(() => { /* offline caching is optional */ });
    });
  }
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
else boot();
