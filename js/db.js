/* Circadia — IndexedDB. Everything lives on-device so reminders work offline. */
const CircadiaDB = (() => {
  const NAME = "circadia";
  const VERSION = 1;
  let dbp;

  function open() {
    if (dbp) return dbp;
    dbp = new Promise((resolve, reject) => {
      const req = indexedDB.open(NAME, VERSION);
      req.onupgradeneeded = () => {
        const db = req.result;
        if (!db.objectStoreNames.contains("events")) {
          const store = db.createObjectStore("events", { keyPath: "id" });
          store.createIndex("byDate", "date");
        }
        if (!db.objectStoreNames.contains("fired")) {
          db.createObjectStore("fired", { keyPath: "id" });
        }
        if (!db.objectStoreNames.contains("meta")) {
          db.createObjectStore("meta", { keyPath: "key" });
        }
      };
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
    return dbp;
  }

  function tx(store, mode, fn) {
    return open().then(
      (db) =>
        new Promise((resolve, reject) => {
          const t = db.transaction(store, mode);
          const s = t.objectStore(store);
          const result = fn(s);
          t.oncomplete = () => resolve(result);
          t.onerror = () => reject(t.error);
          t.onabort = () => reject(t.error);
        })
    );
  }

  function reqToPromise(req) {
    return new Promise((resolve, reject) => {
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async function getAllEvents() {
    const db = await open();
    return new Promise((resolve, reject) => {
      const t = db.transaction("events", "readonly");
      const r = t.objectStore("events").getAll();
      r.onsuccess = () => resolve(r.result || []);
      r.onerror = () => reject(r.error);
    });
  }

  async function putEvent(event) {
    const db = await open();
    return new Promise((resolve, reject) => {
      const t = db.transaction("events", "readwrite");
      t.objectStore("events").put(event);
      t.oncomplete = () => resolve(event);
      t.onerror = () => reject(t.error);
    });
  }

  async function deleteEvent(id) {
    const db = await open();
    return new Promise((resolve, reject) => {
      const t = db.transaction("events", "readwrite");
      t.objectStore("events").delete(id);
      t.oncomplete = () => resolve();
      t.onerror = () => reject(t.error);
    });
  }

  async function wasFired(id) {
    const db = await open();
    return new Promise((resolve, reject) => {
      const t = db.transaction("fired", "readonly");
      const r = t.objectStore("fired").get(id);
      r.onsuccess = () => resolve(!!r.result);
      r.onerror = () => reject(r.error);
    });
  }

  async function markFired(id) {
    const db = await open();
    return new Promise((resolve, reject) => {
      const t = db.transaction("fired", "readwrite");
      t.objectStore("fired").put({ id, at: Date.now() });
      t.oncomplete = () => resolve();
      t.onerror = () => reject(t.error);
    });
  }

  async function unmarkFired(id) {
    const db = await open();
    return new Promise((resolve, reject) => {
      const t = db.transaction("fired", "readwrite");
      t.objectStore("fired").delete(id);
      t.oncomplete = () => resolve();
      t.onerror = () => reject(t.error);
    });
  }

  async function getMeta(key, fallback) {
    const db = await open();
    return new Promise((resolve, reject) => {
      const t = db.transaction("meta", "readonly");
      const r = t.objectStore("meta").get(key);
      r.onsuccess = () => resolve(r.result ? r.result.value : fallback);
      r.onerror = () => reject(r.error);
    });
  }

  async function setMeta(key, value) {
    const db = await open();
    return new Promise((resolve, reject) => {
      const t = db.transaction("meta", "readwrite");
      t.objectStore("meta").put({ key, value });
      t.oncomplete = () => resolve(value);
      t.onerror = () => reject(t.error);
    });
  }

  async function clearAll() {
    const db = await open();
    return new Promise((resolve, reject) => {
      const t = db.transaction(["events", "fired", "meta"], "readwrite");
      t.objectStore("events").clear();
      t.objectStore("fired").clear();
      t.objectStore("meta").clear();
      t.oncomplete = () => resolve();
      t.onerror = () => reject(t.error);
    });
  }

  return {
    open,
    getAllEvents,
    putEvent,
    deleteEvent,
    wasFired,
    markFired,
    unmarkFired,
    getMeta,
    setMeta,
    clearAll,
  };
})();
