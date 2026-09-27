/**
 * Database: schema creation, settings store, and demo seed data.
 * Uses the SQLite engine built into Node 22 — no native modules to install.
 */
import { DatabaseSync } from 'node:sqlite';
import { mkdirSync, existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomBytes, scryptSync, timingSafeEqual } from 'node:crypto';
import { DEFAULT_TZ, localStamp, num, round } from './util.js';

const HERE = dirname(fileURLToPath(import.meta.url));
export const DATA_DIR = process.env.BAKERY_DATA_DIR || join(HERE, '..', 'data');
export const DB_PATH = process.env.BAKERY_DB || join(DATA_DIR, 'bakery.sqlite');

if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });

export const db = new DatabaseSync(DB_PATH);

db.exec(`
  PRAGMA journal_mode = WAL;
  PRAGMA foreign_keys = ON;
  PRAGMA busy_timeout = 5000;
`);

/* ------------------------------------------------------------------ *
 * Schema
 * ------------------------------------------------------------------ */
db.exec(`
CREATE TABLE IF NOT EXISTS settings (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS users (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT    NOT NULL,
  phone      TEXT    NOT NULL UNIQUE,
  role       TEXT    NOT NULL DEFAULT 'staff' CHECK (role IN ('owner','staff')),
  pass_hash  TEXT    NOT NULL,
  pass_salt  TEXT    NOT NULL,
  must_change INTEGER NOT NULL DEFAULT 0,
  active     INTEGER NOT NULL DEFAULT 1,
  created_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  token_hash TEXT PRIMARY KEY,
  user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL,
  last_seen  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
  id   INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  sort INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS products (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL,
  category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
  price       REAL NOT NULL DEFAULT 0,
  cost        REAL,
  active      INTEGER NOT NULL DEFAULT 1,
  created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS suppliers (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  name       TEXT NOT NULL,
  phone      TEXT,
  notes      TEXT,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ingredients (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT NOT NULL,
  unit          TEXT NOT NULL DEFAULT 'kg',
  stock         REAL NOT NULL DEFAULT 0,
  reorder_level REAL NOT NULL DEFAULT 0,
  cost_per_unit REAL NOT NULL DEFAULT 0,
  supplier_id   INTEGER REFERENCES suppliers(id) ON DELETE SET NULL,
  active        INTEGER NOT NULL DEFAULT 1,
  created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stock_moves (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
  kind          TEXT NOT NULL CHECK (kind IN ('purchase','usage','waste','adjustment')),
  qty           REAL NOT NULL,
  unit_cost     REAL NOT NULL DEFAULT 0,
  total_cost    REAL NOT NULL DEFAULT 0,
  note          TEXT,
  ref           TEXT,
  user_id       INTEGER REFERENCES users(id) ON DELETE SET NULL,
  created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recipes (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id    INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
  qty           REAL NOT NULL,
  UNIQUE (product_id, ingredient_id)
);

CREATE TABLE IF NOT EXISTS customers (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL,
  phone       TEXT,
  address     TEXT,
  notes       TEXT,
  is_walk_in  INTEGER NOT NULL DEFAULT 0,
  created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sales (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  invoice_no TEXT NOT NULL UNIQUE,
  customer_id INTEGER REFERENCES customers(id) ON DELETE SET NULL,
  user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
  subtotal   REAL NOT NULL DEFAULT 0,
  discount   REAL NOT NULL DEFAULT 0,
  total      REAL NOT NULL DEFAULT 0,
  paid       REAL NOT NULL DEFAULT 0,
  method     TEXT NOT NULL DEFAULT 'cash' CHECK (method IN ('cash','mobile','card','credit')),
  status     TEXT NOT NULL DEFAULT 'paid'  CHECK (status IN ('paid','partial','unpaid','void')),
  note       TEXT,
  sale_at    TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sale_items (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  sale_id    INTEGER NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
  product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
  name       TEXT NOT NULL,
  qty        REAL NOT NULL,
  unit_price REAL NOT NULL,
  line_total REAL NOT NULL,
  unit_cost  REAL NOT NULL DEFAULT 0,
  line_cost  REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS expenses (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  title      TEXT NOT NULL,
  category   TEXT NOT NULL DEFAULT 'Other',
  amount     REAL NOT NULL,
  note       TEXT,
  user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
  expense_at TEXT NOT NULL,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sales_date     ON sales (sale_at);
CREATE INDEX IF NOT EXISTS idx_sales_status   ON sales (status);
CREATE INDEX IF NOT EXISTS idx_items_sale     ON sale_items (sale_id);
CREATE INDEX IF NOT EXISTS idx_items_product  ON sale_items (product_id);
CREATE INDEX IF NOT EXISTS idx_moves_ing      ON stock_moves (ingredient_id, created_at);
CREATE INDEX IF NOT EXISTS idx_expenses_date  ON expenses (expense_at);
CREATE INDEX IF NOT EXISTS idx_sessions_exp   ON sessions (expires_at);
CREATE INDEX IF NOT EXISTS idx_recipe_product ON recipes (product_id);
`);

/* ------------------------------------------------------------------ *
 * Migrations
 *
 * Additive and idempotent, so they are safe to run on every boot against
 * both a fresh database and one created by an earlier version. Table and
 * column names below are literals in this file, never caller input.
 * ------------------------------------------------------------------ */

function ensureColumn(table, column, decl) {
  const cols = db.prepare('SELECT name FROM pragma_table_info(?)').all(table).map((r) => r.name);
  if (cols.includes(column)) return false;
  db.exec(`ALTER TABLE ${table} ADD COLUMN ${column} ${decl}`);
  console.log(`[migrate] added ${table}.${column}`);
  return true;
}

// Offline outbox support. A phone that loses connection keeps trading and
// replays its queue later; `client_ref` is the caller-generated idempotency
// key that makes a replayed POST return the original row instead of inserting
// a second one. Unique per table, and NULL for everything created online.
for (const table of ['sales', 'expenses', 'stock_moves']) ensureColumn(table, 'client_ref', 'TEXT');

db.exec(`
CREATE UNIQUE INDEX IF NOT EXISTS uq_sales_client_ref
  ON sales (client_ref) WHERE client_ref IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_expenses_client_ref
  ON expenses (client_ref) WHERE client_ref IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_stock_moves_client_ref
  ON stock_moves (client_ref) WHERE client_ref IS NOT NULL;
`);

/**
 * If a record with this client_ref already exists, return it so the caller can
 * answer idempotently. Returns null when the ref is absent or unseen.
 */
export function findByClientRef(table, clientRef) {
  if (!clientRef) return null;
  const allowed = ['sales', 'expenses', 'stock_moves'];
  if (!allowed.includes(table)) throw new Error(`findByClientRef: unknown table ${table}`);
  return db.prepare(`SELECT * FROM ${table} WHERE client_ref = ?`).get(String(clientRef)) || null;
}

/* ------------------------------------------------------------------ *
 * Settings
 * ------------------------------------------------------------------ */

export const DEFAULT_SETTINGS = {
  business_name: "Gide's Bakery",
  tagline: 'Fresh bread, cakes & pastries',
  currency_code: 'BIF',
  currency_symbol: 'FBu',
  currency_decimals: '0',
  timezone: DEFAULT_TZ,
  phone: '+257 79 000 000',
  address: 'Bujumbura, Burundi',
  receipt_note: 'Thank you for your purchase! Karibu tena.',
  low_stock_alerts: '1',
  auto_deduct_stock: '1',
  next_invoice: '1',
};

const setStmt = db.prepare(
  `INSERT INTO settings (key, value) VALUES (?, ?)
   ON CONFLICT(key) DO UPDATE SET value = excluded.value`
);
const getStmt = db.prepare('SELECT value FROM settings WHERE key = ?');
const allSettingsStmt = db.prepare('SELECT key, value FROM settings');

/** Insert defaults only for keys that do not exist yet (never overwrites user edits). */
for (const [k, v] of Object.entries(DEFAULT_SETTINGS)) {
  if (!getStmt.get(k)) setStmt.run(k, v);
}

export function getSetting(key, fallback = '') {
  const row = getStmt.get(key);
  return row ? row.value : (DEFAULT_SETTINGS[key] ?? fallback);
}

export function getSettings() {
  const out = { ...DEFAULT_SETTINGS };
  for (const r of allSettingsStmt.all()) out[r.key] = r.value;
  return out;
}

export function setSettings(pairs) {
  for (const [k, v] of Object.entries(pairs)) setStmt.run(k, v === null ? '' : String(v));
}

export const tz = () => getSetting('timezone', DEFAULT_TZ);
export const decimals = () => Math.max(0, Math.min(4, num(getSetting('currency_decimals', '0'))));
/** Round a money value to the business's configured precision. */
export const money = (v) => round(num(v), decimals());
export const now = () => localStamp(new Date(), tz());

/* ------------------------------------------------------------------ *
 * Passwords (scrypt, per-user salt, constant-time compare)
 * ------------------------------------------------------------------ */

export function hashPassword(password, saltHex) {
  const salt = saltHex ? Buffer.from(saltHex, 'hex') : randomBytes(16);
  const hash = scryptSync(String(password), salt, 64);
  return { salt: salt.toString('hex'), hash: hash.toString('hex') };
}

export function verifyPassword(password, saltHex, hashHex) {
  try {
    const a = Buffer.from(hashHex, 'hex');
    const b = scryptSync(String(password), Buffer.from(saltHex, 'hex'), a.length);
    return a.length === b.length && timingSafeEqual(a, b);
  } catch {
    return false;
  }
}

/* ------------------------------------------------------------------ *
 * Transactions
 * ------------------------------------------------------------------ */

export function tx(fn) {
  db.exec('BEGIN IMMEDIATE');
  try {
    const out = fn();
    db.exec('COMMIT');
    return out;
  } catch (err) {
    try { db.exec('ROLLBACK'); } catch { /* ignore */ }
    throw err;
  }
}

/* ------------------------------------------------------------------ *
 * Unit cost of one product, derived from its recipe.
 * Snapshotted onto each sale line so historical profit never shifts
 * when ingredient prices change later.
 * ------------------------------------------------------------------ */

const recipeCostStmt = db.prepare(`
  SELECT COALESCE(SUM(r.qty * i.cost_per_unit), 0) AS cost
  FROM recipes r JOIN ingredients i ON i.id = r.ingredient_id
  WHERE r.product_id = ?
`);
const productStmt = db.prepare('SELECT * FROM products WHERE id = ?');

export function unitCostOf(productId) {
  const p = productStmt.get(productId);
  if (!p) return 0;
  const fromRecipe = num(recipeCostStmt.get(productId)?.cost);
  if (fromRecipe > 0) return money(fromRecipe);
  return money(p.cost ?? 0); // manual fallback when no recipe is set up
}

/* ------------------------------------------------------------------ *
 * Invoice numbering (monotonic, gap-free)
 * ------------------------------------------------------------------ */

export function nextInvoiceNo() {
  const counter = Math.max(1, num(getSetting('next_invoice', '1')));
  // Self-heal against an existing invoice with the same number. This can
  // happen after restoring a backup, importing data, or seeding a demo
  // database, and without it the very first sale would fail.
  const highest = num(db.prepare(
    `SELECT MAX(CAST(substr(invoice_no, 5) AS INTEGER)) AS n
       FROM sales WHERE invoice_no LIKE 'INV-%'`).get().n);
  const n = Math.max(counter, highest + 1);
  setSettings({ next_invoice: String(n + 1) });
  return `INV-${String(n).padStart(5, '0')}`;
}

/* ------------------------------------------------------------------ *
 * Counts — used to decide whether to offer the demo seed
 * ------------------------------------------------------------------ */

export function isEmpty() {
  const c = (t) => num(db.prepare(`SELECT COUNT(*) n FROM ${t}`).get().n);
  return c('users') === 0;
}

export function tableCounts() {
  const tables = ['users', 'products', 'ingredients', 'suppliers', 'customers', 'sales', 'expenses', 'categories'];
  const out = {};
  for (const t of tables) out[t] = num(db.prepare(`SELECT COUNT(*) n FROM ${t}`).get().n);
  return out;
}

export { localStamp };
