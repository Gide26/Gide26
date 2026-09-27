/* Offline outbox.
 *
 * A bakery cannot stop trading because the connection dropped. This module lets
 * the till keep recording sales, expenses and stock movements with no server,
 * stores them in IndexedDB, and replays them in order once the connection
 * returns.
 *
 * Two properties matter more than anything else here:
 *
 *  1. Nothing is lost. A queued write survives closing the tab, killing the
 *     browser and rebooting the phone. IndexedDB is used rather than
 *     localStorage because it is durable storage and is not swept away by
 *     "clear browsing data" in an installed PWA.
 *
 *  2. Nothing is duplicated. Every queued write carries a client-generated
 *     `client_ref`. The server treats that as an idempotency key, so a replay
 *     that arrives twice — the common case when a connection drops mid-request
 *     and the client cannot tell whether the write landed — is recorded once.
 *
 * Reference data (products, categories, customers, settings) is snapshotted on
 * every successful load so the till has something to render offline. Stock
 * quantities are deliberately NOT cached: a stale number on a till is worse
 * than no number, so the offline UI hides quantities and says so.
 */

const DB_NAME = 'bakery-offline';
const DB_VERSION = 1;
const OUTBOX = 'outbox';
const CACHE = 'cache';

let dbp = null;
let listeners = new Set();
let cacheCount = 0;

/* ------------------------------------------------------------------ *
 * IndexedDB plumbing
 * ------------------------------------------------------------------ */

function openDb() {
  if (dbp) return dbp;
  dbp = new Promise((resolve, reject) => {
    if (typeof indexedDB === 'undefined') {
      reject(new Error('This browser has no IndexedDB'));
      return;
    }
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains(OUTBOX)) {
        const store = db.createObjectStore(OUTBOX, { keyPath: 'ref' });
        store.createIndex('queuedAt', 'queuedAt');
        store.createIndex('kind', 'kind');
      }
      if (!db.objectStoreNames.contains(CACHE)) {
        db.createObjectStore(CACHE, { keyPath: 'key' });
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error || new Error('Could not open the offline store'));
    req.onblocked = () => reject(new Error('Offline store is blocked by another tab'));
  });
  return dbp;
}

function txStore(store, mode) {
  return openDb().then((db) => db.transaction(store, mode).objectStore(store));
}

function reqP(req) {
  return new Promise((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

/** A unique-enough reference. crypto.randomUUID needs a secure context, which
 *  plain-HTTP LAN access does not provide, so fall back to random bytes. */
export function makeRef(prefix = 'q') {
  const c = typeof crypto !== 'undefined' ? crypto : null;
  if (c?.randomUUID) return `${prefix}-${c.randomUUID()}`;
  const bytes = new Uint8Array(16);
  if (c?.getRandomValues) c.getRandomValues(bytes);
  else for (let i = 0; i < 16; i++) bytes[i] = Math.floor(Math.random() * 256);
  return `${prefix}-${Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('')}`;
}

/* ------------------------------------------------------------------ *
 * Notifications
 * ------------------------------------------------------------------ */

export function onOutboxChange(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

function emit() {
  const snapshot = { count: cacheCount, syncing: syncState.syncing, failed: syncState.failed };
  for (const fn of listeners) {
    try { fn(snapshot); } catch { /* a broken listener must not stall the queue */ }
  }
}

/* ------------------------------------------------------------------ *
 * Outbox
 * ------------------------------------------------------------------ */

/**
 * Queue a write. `kind` selects the endpoint it will be replayed against.
 * Returns the stored record, including the provisional label the UI shows
 * until the server assigns a real invoice number.
 */
export async function enqueue(kind, payload, meta = {}) {
  const store = await txStore(OUTBOX, 'readwrite');
  const ref = makeRef(kind.slice(0, 3));
  const queuedAt = Date.now();
  const record = {
    ref,
    kind,
    payload: { ...payload, client_ref: ref },
    queuedAt,
    // The moment the cashier tapped save, in their own wall clock — this is what
    // the sale is dated with, not the moment it eventually syncs.
    capturedAt: meta.capturedAt || new Date().toISOString(),
    provisional: meta.provisional || null,
    label: meta.label || null,
    attempts: 0,
    lastError: null,
    failed: false,
  };
  await reqP(store.put(record));
  cacheCount = await countOutbox();
  emit();
  return record;
}

export async function listOutbox() {
  const store = await txStore(OUTBOX, 'readonly');
  const all = await reqP(store.index('queuedAt').getAll());
  return all.sort((a, b) => a.queuedAt - b.queuedAt);
}

export async function countOutbox() {
  const store = await txStore(OUTBOX, 'readonly');
  return reqP(store.count());
}

async function removeRef(ref) {
  const store = await txStore(OUTBOX, 'readwrite');
  await reqP(store.delete(ref));
}

async function updateRef(ref, patch) {
  const store = await txStore(OUTBOX, 'readwrite');
  const existing = await reqP(store.get(ref));
  if (!existing) return null;
  const next = { ...existing, ...patch };
  await reqP(store.put(next));
  return next;
}

/** Drop a queued item without sending it. */
export async function discard(ref) {
  await removeRef(ref);
  cacheCount = await countOutbox();
  emit();
}

/** Re-arm an item that failed validation so the next sync retries it. */
export async function retry(ref) {
  await updateRef(ref, { failed: false, lastError: null, attempts: 0 });
  cacheCount = await countOutbox();
  emit();
  return syncOutbox();
}

/* ------------------------------------------------------------------ *
 * Reference-data cache
 * ------------------------------------------------------------------ */

export async function putCache(key, value) {
  try {
    const store = await txStore(CACHE, 'readwrite');
    await reqP(store.put({ key, value, at: Date.now() }));
  } catch { /* caching is best-effort; never break a live load over it */ }
}

export async function getCache(key) {
  try {
    const store = await txStore(CACHE, 'readonly');
    const hit = await reqP(store.get(key));
    return hit ? hit.value : null;
  } catch { return null; }
}

/** When the reference data was last refreshed, for an "as of" label. */
export async function cacheAge(key) {
  try {
    const store = await txStore(CACHE, 'readonly');
    const hit = await reqP(store.get(key));
    return hit ? hit.at : null;
  } catch { return null; }
}

/* ------------------------------------------------------------------ *
 * Sync
 * ------------------------------------------------------------------ */

const syncState = { syncing: false, failed: 0, conflicts: 0, lastSyncAt: null, lastError: null };

/**
 * Settle a queued change the server refused because the record moved on.
 *   'mine'   — overwrite the server's version with this device's
 *   'theirs' — drop the queued change and accept what is on the server
 * Neither is automatic: choosing for the user is how work gets destroyed.
 */
export async function resolveConflict(ref, choice) {
  if (choice === 'theirs') return discard(ref);
  if (choice === 'mine') {
    await updateRef(ref, { failed: false, conflict: false, lastError: null, force: true });
    cacheCount = await countOutbox();
    emit();
    return syncOutbox();
  }
  throw new Error(`Unknown conflict resolution: ${choice}`);
}

/**
 * Where each kind of queued write is replayed to.
 *
 * Kinds are either a bare noun ('sale') for a create, or 'noun:verb' for an edit
 * or delete. Updates and deletes carry the record id in the payload, plus the
 * `base_updated_at` the device last saw — that is what lets the server notice a
 * change made elsewhere while this phone was disconnected.
 */
const ROUTES = {
  'sale':               (p) => ['POST', '/api/sales'],
  'expense':            (p) => ['POST', '/api/expenses'],
  'stock':              (p) => ['POST', `/api/ingredients/${p.ingredient_id}/stock`],
  'expense:update':     (p) => ['PUT', `/api/expenses/${p.id}`],
  'expense:delete':     (p) => ['DELETE', `/api/expenses/${p.id}`],
  'product:update':     (p) => ['PUT', `/api/products/${p.id}`],
  'product:delete':     (p) => ['DELETE', `/api/products/${p.id}`],
  'customer:update':    (p) => ['PUT', `/api/customers/${p.id}`],
  'customer:delete':    (p) => ['DELETE', `/api/customers/${p.id}`],
  'ingredient:update':  (p) => ['PUT', `/api/ingredients/${p.id}`],
  'ingredient:delete':  (p) => ['DELETE', `/api/ingredients/${p.id}`],
};

function endpointFor(record) {
  const build = ROUTES[record.kind];
  if (!build) return null;
  const [method, path] = build(record.payload || {});
  if (path.endsWith('/undefined') || path.endsWith('/null')) return null;
  return { method, path };
}

/** Human-readable label for a queued change, used in the pending list. */
export function describeKind(kind) {
  const [noun, verb] = String(kind).split(':');
  const nouns = { sale: 'sale', expense: 'expense', stock: 'stock movement',
    product: 'product', customer: 'customer', ingredient: 'ingredient' };
  const what = nouns[noun] || noun;
  if (!verb || verb === 'create') return `New ${what}`;
  if (verb === 'update') return `Edit to ${what}`;
  if (verb === 'delete') return `Deleted ${what}`;
  return `${verb} ${what}`;
}

export function syncStatus() {
  return { ...syncState, count: cacheCount };
}

/**
 * Drain the queue oldest-first. Stops on a network failure (the connection is
 * gone again, so retrying now would only churn) but steps over records the
 * server rejected on validation, marking them for the cashier to fix — one bad
 * line must not hold up the rest of the day's trading.
 */
export async function syncOutbox() {
  if (syncState.syncing) return { synced: 0, blocked: true };
  if (typeof navigator !== 'undefined' && navigator.onLine === false) {
    return { synced: 0, offline: true };
  }

  syncState.syncing = true;
  emit();

  let synced = 0;
  try {
    for (;;) {
      const pending = await listOutbox();
      const next = pending.find((r) => !r.failed);
      if (!next) {
        syncState.failed = pending.filter((r) => r.failed).length;
        break;
      }

      const target = endpointFor(next);
      if (!target) { await updateRef(next.ref, { failed: true, lastError: 'Unknown record type' }); continue; }

      // `force` means the user has seen the conflict and chosen their own
      // version, so the concurrency check is deliberately dropped.
      const payload = next.force
        ? (() => { const { base_updated_at, ...rest } = next.payload; return rest; })()
        : next.payload;

      let res;
      try {
        res = await fetch(target.path, {
          method: target.method,
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify(payload),
          credentials: 'same-origin',
          cache: 'no-store',
        });
      } catch {
        // No connection again — leave the queue exactly as it is.
        syncState.lastError = 'Connection lost during sync';
        break;
      }

      if (res.status === 401) {
        // Session ended mid-outage. Keep the queue; the user must sign in again.
        syncState.lastError = 'Sign in again to send the queued items';
        break;
      }

      const text = await res.text();
      let data = null;
      try { data = text ? JSON.parse(text) : null; } catch { data = { error: text.slice(0, 200) }; }

      if (res.status === 409) {
        // Someone changed this record while we were offline. Never guess: park it
        // with both timestamps so a human can choose, and carry on with the rest.
        await updateRef(next.ref, {
          attempts: (next.attempts || 0) + 1,
          failed: true,
          conflict: true,
          lastError: data?.error || 'Changed on the server while you were offline',
          serverUpdatedAt: data?.details?.server_updated_at || null,
          clientBase: data?.details?.client_base || null,
        });
        syncState.conflicts = (syncState.conflicts || 0) + 1;
        continue;
      }

      if (!res.ok) {
        // A 5xx may succeed later, so retry it; a 4xx will never succeed as-is
        // and needs a human, so park it and move on.
        const retryable = res.status >= 500;
        await updateRef(next.ref, {
          attempts: (next.attempts || 0) + 1,
          lastError: data?.error || `Server replied ${res.status}`,
          failed: !retryable || (next.attempts || 0) >= 4,
        });
        if (!retryable) continue;
        syncState.lastError = data?.error || `Server replied ${res.status}`;
        break;
      }

      // Accepted (fresh insert or an idempotent replay of one already stored).
      await updateRef(next.ref, { synced: true, serverId: data?.id ?? null, invoice_no: data?.invoice_no ?? null });
      await removeRef(next.ref);
      synced++;
      syncState.lastSyncAt = Date.now();
      syncState.lastError = null;
    }
  } finally {
    const left = await listOutbox().catch(() => []);
    cacheCount = left.length;
    syncState.failed = left.filter((r) => r.failed).length;
    syncState.conflicts = left.filter((r) => r.conflict).length;
    syncState.syncing = false;
    emit();
  }

  return { synced, remaining: cacheCount, failed: syncState.failed };
}

/** Call once at boot: restores the badge count and flushes anything left over. */
export async function initOffline() {
  try {
    await openDb();
  } catch (err) {
    syncState.lastError = err.message;
    return { available: false, reason: err.message };
  }
  cacheCount = await countOutbox();
  emit();
  if (cacheCount > 0) syncOutbox();
  return { available: true, count: cacheCount };
}

export function offlineAvailable() {
  return dbp !== null;
}
