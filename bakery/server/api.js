/**
 * Application API: authentication, catalogue, point-of-sale, inventory,
 * expenses, customers, users and business settings.
 */
import {
  db, tx, money, now, nowStamp, tz, decimals, getSetting, getSettings, setSettings,
  hashPassword, unitCostOf, nextInvoiceNo, tableCounts, isEmpty, findByClientRef,
  syncLogGet, syncLogPut, EDITABLE_TABLES,
} from './db.js';
import {
  str, strOrNull, num, int, idOrNull, bool, round, clip, require_, requireAmount,
  badRequest, notFound, forbidden, range as rangeOf, HttpError, localDate, addDays,
} from './util.js';
import {
  login, changePassword, createSession, destroySession, sessionCookie, clearCookie,
  requireUser, requireOwner,
} from './auth.js';
import { raw } from './router.js';
import { seedDemo } from './seed.js';

/* ------------------------------------------------------------------ *
 * Small helpers
 * ------------------------------------------------------------------ */

const METHODS = ['cash', 'mobile', 'card', 'credit'];

/**
 * Shape a response for a record we have already stored, when a client replays
 * a queued offline write. Only the fields that are actually persisted can be
 * reported; transient values like cash `change` are not recoverable, so they
 * come back null and the client keeps the copy it made at the time of sale.
 */
function replayedSale(row) {
  return {
    ok: true, replay: true, id: row.id, invoice_no: row.invoice_no,
    subtotal: money(row.subtotal), discount: money(row.discount), total: money(row.total),
    paid: money(row.paid), due: money(num(row.total) - num(row.paid)), status: row.status,
    method: row.method, change: null, stock_moves: null, sale_at: row.sale_at, low_stock: [],
  };
}

function replayedExpense(row) {
  return { ok: true, replay: true, id: row.id, title: row.title,
    amount: money(row.amount), category: row.category };
}

/**
 * Apply an edit or delete that may be a replay from an offline queue, and may
 * collide with a change made on another device while this one was disconnected.
 *
 * Three outcomes:
 *   - this client_ref was already applied -> return the stored result, so a
 *     retry after a lost response cannot apply the change twice
 *   - base_updated_at disagrees with the row -> 409, carrying the server's
 *     timestamp so the UI can show what would have been overwritten
 *   - otherwise -> apply, stamp updated_at, and log it
 *
 * Silently taking the last write would destroy someone's work; refusing and
 * asking a human is the only defensible behaviour for money.
 */
function guardedWrite(ctx, table, id, op, apply) {
  if (!EDITABLE_TABLES.includes(table)) throw new Error(`guardedWrite: ${table} is not editable`);
  const b = ctx.body ?? {};
  const clientRef = strOrNull(clip(b.client_ref, 80));
  const numId = Number(id);

  if (clientRef) {
    const done = syncLogGet(clientRef);
    if (done && done.tbl === table && Number(done.record_id) === numId) {
      let result = {};
      try { result = JSON.parse(done.result || '{}'); } catch { /* fall through to a plain ok */ }
      return { ...result, replay: true };
    }
  }

  const row = db.prepare(`SELECT updated_at FROM ${table} WHERE id = ?`).get(numId);

  // The row is already gone. A queued delete is then satisfied; an edit cannot be
  // applied to nothing, and dropping it silently would lose the change.
  if (!row) {
    if (op === 'delete') {
      const out = { ok: true, deleted: true, alreadyGone: true };
      if (clientRef) syncLogPut(clientRef, table, numId, op, JSON.stringify(out));
      return out;
    }
    throw notFound(`That record no longer exists (id ${numId})`);
  }

  // A record can only be compared if it carries a stamp. One written before
  // this column existed — or by a path that forgot it — would otherwise skip
  // the check below and allow exactly the silent overwrite this guard exists to
  // prevent. Repair it in place so the comparison is always meaningful.
  if (!strOrNull(row.updated_at)) {
    row.updated_at = nowStamp();
    db.prepare(`UPDATE ${table} SET updated_at = ? WHERE id = ?`).run(row.updated_at, numId);
  }

  const base = strOrNull(b.base_updated_at);
  if (base && row.updated_at !== base) {
    throw new HttpError(409, 'This changed on the server while you were offline', {
      conflict: true, table, id: numId,
      server_updated_at: row.updated_at, client_base: base,
    });
  }

  const applied = apply() || { ok: true };
  if (!applied.deleted) {
    const stamp = nowStamp();
    db.prepare(`UPDATE ${table} SET updated_at = ? WHERE id = ?`).run(stamp, numId);
    applied.updated_at = stamp;
  }
  if (clientRef) syncLogPut(clientRef, table, numId, op, JSON.stringify(applied));
  return applied;
}

function replayedMove(row, ing) {
  return { ok: true, replay: true, id: row.id, stock: money(num(ing?.stock)),
    signed: num(row.qty), total_cost: money(row.total_cost), unit_cost: money(row.unit_cost),
    cost_updated: false };
}
const MOVE_KINDS = ['purchase', 'usage', 'waste', 'adjustment'];
const EXPENSE_CATEGORIES = ['Rent', 'Utilities', 'Salaries', 'Transport', 'Equipment',
  'Ingredients', 'Packaging', 'Marketing', 'Permits', 'Repairs', 'Other'];

const publicUser = (u) => u && ({ id: u.id, name: u.name, phone: u.phone, role: u.role, must_change: !!u.must_change });

/** The client uses this as its default date-range end, so ranges are always
 *  anchored to the business timezone rather than the phone's own clock. */
const serverToday = () => localDate(new Date(), tz());

/** Costs and margins are owner-only: staff see prices, never the cost base. */
const canSeeCosts = (ctx) => ctx.user?.role === 'owner';

const stripCosts = (obj, allowed) => {
  if (allowed) return obj;
  const { cost, unit_cost, line_cost, cogs, cost_per_unit, value, margin,
    margin_pct, profit, total_cost, ...rest } = obj ?? {};
  return rest;
};

function mustExist(table, id, label = 'Record') {
  const row = db.prepare(`SELECT * FROM ${table} WHERE id = ?`).get(int(id));
  if (!row) throw notFound(`${label} not found`);
  return row;
}

/** Keep timestamps inside the business timezone and within a sane window. */
function normaliseWhen(value, fallback) {
  const s = str(value);
  if (/^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2})?$/.test(s)) {
    return s.replace('T', ' ').length === 16 ? `${s.replace('T', ' ')}:00` : s.replace('T', ' ');
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return `${s} 12:00:00`;
  return fallback;
}

const getIngredient = db.prepare('SELECT * FROM ingredients WHERE id = ?');
const setStock = db.prepare('UPDATE ingredients SET stock = ? WHERE id = ?');
const insMove = db.prepare(
  `INSERT INTO stock_moves (ingredient_id, kind, qty, unit_cost, total_cost, note, ref, user_id, created_at, client_ref)
   VALUES (?,?,?,?,?,?,?,?,?,?)`);

/* ------------------------------------------------------------------ *
 * Routes
 * ------------------------------------------------------------------ */

export function registerApiRoutes(r) {

  /* ---------------- auth ---------------- */

  r.post('/api/login', (ctx) => {
    const phone = require_(ctx.body?.phone, 'Phone number');
    const password = str(ctx.body?.password);
    if (!password) throw badRequest('Password is required');
    const { token, user } = login(phone, password, ctx.ip);
    return raw(200, JSON.stringify({ user, settings: getSettings(), counts: tableCounts(), today: serverToday() }),
      'application/json; charset=utf-8', { 'set-cookie': sessionCookie(token, { secure: ctx.secure }) });
  });

  r.post('/api/logout', (ctx) => {
    destroySession(ctx.token);
    return raw(200, JSON.stringify({ ok: true }), 'application/json; charset=utf-8',
      { 'set-cookie': clearCookie({ secure: ctx.secure }) });
  });

  r.get('/api/me', (ctx) => {
    if (!ctx.user) throw new HttpError(401, 'Not signed in');
    return { user: publicUser(ctx.user), settings: getSettings(), counts: tableCounts(),
             canSeeCosts: canSeeCosts(ctx), today: serverToday() };
  });

  r.post('/api/change-password', (ctx) => {
    const user = requireUser(ctx);
    changePassword(user.id, str(ctx.body?.current), str(ctx.body?.next));
    // changePassword signs every device out; hand back a fresh session for this one.
    const token = createSession(user.id);
    return raw(200, JSON.stringify({ ok: true }), 'application/json; charset=utf-8',
      { 'set-cookie': sessionCookie(token, { secure: ctx.secure }) });
  });

  /** First-run helper: only works while the database has no owner at all. */
  r.post('/api/setup', (ctx) => {
    const hasOwner = num(db.prepare("SELECT COUNT(*) n FROM users WHERE role='owner' AND active=1").get().n);
    if (hasOwner > 0) throw forbidden('Setup is already complete — sign in instead');
    const name = require_(ctx.body?.name, 'Your name');
    const phone = require_(ctx.body?.phone, 'Phone number');
    const password = str(ctx.body?.password);
    if (password.length < 6) throw badRequest('Use at least 6 characters for your password');
    const { salt, hash } = hashPassword(password);
    const id = Number(db.prepare(
      `INSERT INTO users (name, phone, role, pass_hash, pass_salt, must_change, active, created_at)
       VALUES (?,?, 'owner', ?,?,0,1,?)`).run(clip(name, 80), clip(phone, 30), hash, salt, now()).lastInsertRowid);
    db.prepare("INSERT OR IGNORE INTO customers (name, notes, is_walk_in, created_at) VALUES ('Walk-in customer','Default counter customer',1,?)").run(now());
    // Let the owner name the business during first-run setup.
    const businessName = clip(str(ctx.body?.business_name), 120);
    if (businessName) setSettings({ business_name: businessName });
    const token = createSession(id);
    return raw(200, JSON.stringify({ user: publicUser(db.prepare('SELECT * FROM users WHERE id=?').get(id)), settings: getSettings(), today: serverToday() }),
      'application/json; charset=utf-8', { 'set-cookie': sessionCookie(token, { secure: ctx.secure }) });
  });

  r.post('/api/seed-demo', (ctx) => {
    if (num(db.prepare('SELECT COUNT(*) n FROM users').get().n) > 0) {
      throw forbidden('Demo data can only be loaded into an empty database');
    }
    const out = seedDemo({ force: true });
    return { ok: true, seeded: out };
  });

  /* ---------------- settings ---------------- */

  r.put('/api/settings', (ctx) => {
    requireOwner(ctx);
    const b = ctx.body ?? {};
    const updates = {};
    const text = (k, max) => { if (b[k] !== undefined) updates[k] = clip(b[k], max); };

    text('business_name', 120);
    text('tagline', 160);
    text('phone', 40);
    text('address', 200);
    text('receipt_note', 300);
    text('currency_symbol', 8);

    if (b.currency_code !== undefined) {
      const code = str(b.currency_code).toUpperCase().slice(0, 3);
      if (!/^[A-Z]{3}$/.test(code)) throw badRequest('Currency code must be 3 letters, e.g. BIF');
      updates.currency_code = code;
    }
    if (b.currency_decimals !== undefined) {
      updates.currency_decimals = String(Math.max(0, Math.min(4, int(b.currency_decimals, 0))));
    }
    if (b.timezone !== undefined) {
      const candidate = str(b.timezone_code || b.timezone);
      try { new Intl.DateTimeFormat('en-CA', { timeZone: candidate }); }
      catch { throw badRequest(`"${candidate}" is not a valid timezone`); }
      updates.timezone = candidate;
    }
    if (b.low_stock_alerts !== undefined) updates.low_stock_alerts = bool(b.low_stock_alerts) ? '1' : '0';
    if (b.auto_deduct_stock !== undefined) updates.auto_deduct_stock = bool(b.auto_deduct_stock) ? '1' : '0';

    if (!Object.keys(updates).length) throw badRequest('Nothing to update');
    setSettings(updates);
    return { ok: true, settings: getSettings() };
  });

  /* ---------------- bootstrap (one round trip for the POS screen) ---------------- */

  r.get('/api/bootstrap', (ctx) => {
    requireUser(ctx);
    const seeCosts = canSeeCosts(ctx);
    const products = db.prepare(
      `SELECT p.*, c.name AS category
         FROM products p LEFT JOIN categories c ON c.id = p.category_id
        WHERE p.active = 1 ORDER BY c.sort, p.name`).all()
      .map((p) => stripCosts({ ...p, cost: p.cost === null ? null : money(p.cost),
        unit_cost: seeCosts ? unitCostOf(p.id) : undefined }, seeCosts));

    return {
      settings: getSettings(),
      user: publicUser(ctx.user),
      canSeeCosts: seeCosts,
      categories: db.prepare('SELECT * FROM categories ORDER BY sort, name').all(),
      products,
      customers: db.prepare('SELECT id, name, phone, is_walk_in FROM customers ORDER BY name LIMIT 400').all(),
      ingredients: seeCosts
        ? db.prepare('SELECT id, name, unit, stock, reorder_level, cost_per_unit FROM ingredients WHERE active=1 ORDER BY name').all()
        : db.prepare('SELECT id, name, unit, stock, reorder_level FROM ingredients WHERE active=1 ORDER BY name').all(),
      expenseCategories: EXPENSE_CATEGORIES,
      counts: tableCounts(),
      today: serverToday(),
    };
  });

  /* ---------------- categories ---------------- */

  r.get('/api/categories', (ctx) => { requireUser(ctx); return db.prepare('SELECT * FROM categories ORDER BY sort, name').all(); });

  r.post('/api/categories', (ctx) => {
    requireOwner(ctx);
    const name = require_(ctx.body?.name, 'Category name');
    if (db.prepare('SELECT id FROM categories WHERE lower(name) = lower(?)').get(name)) {
      throw badRequest('That category already exists');
    }
    const sort = int(ctx.body?.sort, num(db.prepare('SELECT COALESCE(MAX(sort),0)+1 n FROM categories').get().n));
    const id = Number(db.prepare('INSERT INTO categories (name, sort) VALUES (?,?)').run(clip(name, 60), sort).lastInsertRowid);
    return { id, name: clip(name, 60), sort };
  });

  r.put('/api/categories/:id', (ctx) => {
    requireOwner(ctx);
    const row = mustExist('categories', ctx.params.id, 'Category');
    const name = require_(ctx.body?.name, 'Category name');
    const dup = db.prepare('SELECT id FROM categories WHERE lower(name)=lower(?) AND id <> ?').get(name, row.id);
    if (dup) throw badRequest('Another category already uses that name');
    db.prepare('UPDATE categories SET name = ?, sort = ? WHERE id = ?')
      .run(clip(name, 60), int(ctx.body?.sort, row.sort), row.id);
    return { ok: true };
  });

  r.delete('/api/categories/:id', (ctx) => {
    requireOwner(ctx);
    const row = mustExist('categories', ctx.params.id, 'Category');
    const used = num(db.prepare('SELECT COUNT(*) n FROM products WHERE category_id = ?').get(row.id).n);
    if (used > 0) throw badRequest(`${used} product(s) use this category — move them first`);
    db.prepare('DELETE FROM categories WHERE id = ?').run(row.id);
    return { ok: true };
  });

  /* ---------------- products ---------------- */

  r.get('/api/products', (ctx) => {
    requireUser(ctx);
    const seeCosts = canSeeCosts(ctx);
    const q = str(ctx.query.q).toLowerCase();
    const activeOnly = ctx.query.active !== '0';
    let rows = db.prepare(
      `SELECT p.*, c.name AS category
         FROM products p LEFT JOIN categories c ON c.id = p.category_id
        ORDER BY p.active DESC, c.sort, p.name`).all();
    if (activeOnly) rows = rows.filter((p) => p.active);
    if (q) rows = rows.filter((p) => p.name.toLowerCase().includes(q) || (p.category || '').toLowerCase().includes(q));
    return rows.map((p) => {
      const cost = seeCosts ? unitCostOf(p.id) : undefined;
      const base = { ...p, price: money(p.price), unit_cost: cost,
        margin: seeCosts ? money(num(p.price) - cost) : undefined,
        margin_pct: seeCosts && num(p.price) ? round(((num(p.price) - cost) / num(p.price)) * 100, 1) : undefined,
        has_recipe: !!db.prepare('SELECT 1 FROM recipes WHERE product_id = ? LIMIT 1').get(p.id) };
      return stripCosts(base, seeCosts);
    });
  });

  r.get('/api/products/:id', (ctx) => {
    requireUser(ctx);
    const seeCosts = canSeeCosts(ctx);
    const p = mustExist('products', ctx.params.id, 'Product');
    const category = db.prepare('SELECT name FROM categories WHERE id = ?').get(p.category_id)?.name ?? null;
    const recipe = db.prepare(
      `SELECT r.id, r.ingredient_id, r.qty, i.name, i.unit, i.cost_per_unit, i.stock
         FROM recipes r JOIN ingredients i ON i.id = r.ingredient_id
        WHERE r.product_id = ? ORDER BY i.name`).all(p.id)
      .map((x) => ({ ...x, qty: round(x.qty, 4), cost_per_unit: money(x.cost_per_unit),
        line_cost: seeCosts ? money(num(x.qty) * num(x.cost_per_unit)) : undefined }));
    const cost = seeCosts ? unitCostOf(p.id) : undefined;
    return stripCosts({
      ...p, category, price: money(p.price), unit_cost: cost,
      margin: seeCosts ? money(num(p.price) - cost) : undefined,
      margin_pct: seeCosts && num(p.price) ? round(((num(p.price) - cost) / num(p.price)) * 100, 1) : undefined,
      recipe: seeCosts ? recipe : recipe.map(({ cost_per_unit, line_cost, ...rest }) => rest),
    }, seeCosts);
  });

  r.post('/api/products', (ctx) => {
    requireOwner(ctx);
    const b = ctx.body ?? {};
    const name = clip(require_(b.name, 'Product name'), 120);
    const price = money(requireAmount(b.price, 'Price'));
    const id = Number(db.prepare(
      `INSERT INTO products (name, category_id, price, cost, active, created_at, updated_at) VALUES (?,?,?,?,?,?,?)`)
      .run(name, idOrNull(b.category_id), price,
        b.cost === undefined || b.cost === null || b.cost === '' ? null : money(requireAmount(b.cost, 'Cost')),
        bool(b.active ?? 1), now(), nowStamp()).lastInsertRowid);
    return { id, name, price };
  });

  r.put('/api/products/:id', (ctx) => {
    requireOwner(ctx);
    return guardedWrite(ctx, 'products', ctx.params.id, 'update', () => updateProduct(ctx));
  });

  function updateProduct(ctx) {
    const p = mustExist('products', ctx.params.id, 'Product');
    const b = ctx.body ?? {};
    const name = b.name !== undefined ? clip(require_(b.name, 'Product name'), 120) : p.name;
    const price = b.price !== undefined ? money(requireAmount(b.price, 'Price')) : p.price;
    const cost = b.cost === undefined ? p.cost
      : (b.cost === null || b.cost === '' ? null : money(requireAmount(b.cost, 'Cost')));
    db.prepare('UPDATE products SET name=?, category_id=?, price=?, cost=?, active=? WHERE id=?')
      .run(name, b.category_id !== undefined ? idOrNull(b.category_id) : p.category_id,
        price, cost, b.active !== undefined ? bool(b.active) : p.active, p.id);
    return { ok: true };
  }

  /** Archive when the product has history, hard-delete when it does not. */
  r.delete('/api/products/:id', (ctx) => {
    requireOwner(ctx);
    return guardedWrite(ctx, 'products', ctx.params.id, 'delete', () => {
      const p = mustExist('products', ctx.params.id, 'Product');
      const sold = num(db.prepare('SELECT COUNT(*) n FROM sale_items WHERE product_id = ?').get(p.id).n);
      if (sold > 0) {
        db.prepare('UPDATE products SET active = 0 WHERE id = ?').run(p.id);
        return { ok: true, archived: true, reason: `Kept for history because it appears on ${sold} sale line(s)` };
      }
      db.prepare('DELETE FROM products WHERE id = ?').run(p.id);
      return { ok: true, deleted: true };
    });
  });

  /* ---------------- recipes ---------------- */

  r.put('/api/products/:id/recipe', (ctx) => {
    requireOwner(ctx);
    const p = mustExist('products', ctx.params.id, 'Product');
    const lines = Array.isArray(ctx.body?.lines) ? ctx.body.lines : null;
    if (!lines) throw badRequest('Provide a "lines" array');
    if (lines.length > 60) throw badRequest('A recipe cannot have more than 60 ingredients');

    tx(() => {
      db.prepare('DELETE FROM recipes WHERE product_id = ?').run(p.id);
      const ins = db.prepare('INSERT INTO recipes (product_id, ingredient_id, qty) VALUES (?,?,?)');
      const seen = new Set();
      for (const l of lines) {
        const ingId = idOrNull(l.ingredient_id);
        const qty = round(num(l.qty), 4);
        if (!ingId || qty <= 0) continue;
        if (seen.has(ingId)) continue;
        if (!getIngredient.get(ingId)) throw badRequest(`Ingredient #${ingId} does not exist`);
        seen.add(ingId);
        ins.run(p.id, ingId, qty);
      }
    });
    const cost = unitCostOf(p.id);
    return { ok: true, unit_cost: cost, price: money(p.price),
      margin: money(num(p.price) - cost),
      margin_pct: num(p.price) ? round(((num(p.price) - cost) / num(p.price)) * 100, 1) : 0 };
  });

  /* ---------------- ingredients & stock ---------------- */

  r.get('/api/ingredients', (ctx) => {
    requireUser(ctx);
    const seeCosts = canSeeCosts(ctx);
    const q = str(ctx.query.q).toLowerCase();
    let rows = db.prepare(
      `SELECT i.*, s.name AS supplier FROM ingredients i
         LEFT JOIN suppliers s ON s.id = i.supplier_id
        ORDER BY i.active DESC, i.name`).all();
    if (ctx.query.active !== '0') rows = rows.filter((x) => x.active);
    if (q) rows = rows.filter((x) => x.name.toLowerCase().includes(q));
    return rows.map((x) => stripCosts({
      ...x, stock: round(x.stock, 3), cost_per_unit: money(x.cost_per_unit),
      reorder_level: num(x.reorder_level),
      value: money(num(x.stock) * num(x.cost_per_unit)),
      low: num(x.reorder_level) > 0 && num(x.stock) <= num(x.reorder_level),
    }, seeCosts));
  });

  r.post('/api/ingredients', (ctx) => {
    requireOwner(ctx);
    const b = ctx.body ?? {};
    const name = clip(require_(b.name, 'Ingredient name'), 120);
    const id = Number(db.prepare(
      `INSERT INTO ingredients (name, unit, stock, reorder_level, cost_per_unit, supplier_id, active, created_at, updated_at)
       VALUES (?,?,?,?,?,?,?,?,?)`)
      .run(name, clip(str(b.unit, 'kg'), 20), round(num(b.stock), 3), round(num(b.reorder_level), 3),
        money(requireAmount(b.cost_per_unit, 'Cost per unit')), idOrNull(b.supplier_id), bool(b.active ?? 1), now(), nowStamp()).lastInsertRowid);
    return { id, name };
  });

  r.put('/api/ingredients/:id', (ctx) => {
    requireOwner(ctx);
    return guardedWrite(ctx, 'ingredients', ctx.params.id, 'update', () => updateIngredient(ctx));
  });

  function updateIngredient(ctx) {
    const ing = mustExist('ingredients', ctx.params.id, 'Ingredient');
    const b = ctx.body ?? {};
    db.prepare(
      `UPDATE ingredients SET name=?, unit=?, reorder_level=?, cost_per_unit=?, supplier_id=?, active=?, stock=? WHERE id=?`)
      .run(
        b.name !== undefined ? clip(require_(b.name, 'Ingredient name'), 120) : ing.name,
        b.unit !== undefined ? clip(str(b.unit, ing.unit), 20) : ing.unit,
        b.reorder_level !== undefined ? round(num(b.reorder_level), 3) : ing.reorder_level,
        b.cost_per_unit !== undefined ? money(requireAmount(b.cost_per_unit, 'Cost per unit')) : ing.cost_per_unit,
        b.supplier_id !== undefined ? idOrNull(b.supplier_id) : ing.supplier_id,
        b.active !== undefined ? bool(b.active) : ing.active,
        b.stock !== undefined ? round(num(b.stock), 3) : ing.stock,
        ing.id);
    return { ok: true };
  }

  r.delete('/api/ingredients/:id', (ctx) => {
    requireOwner(ctx);
    return guardedWrite(ctx, 'ingredients', ctx.params.id, 'delete', () => {
      const ing = mustExist('ingredients', ctx.params.id, 'Ingredient');
      const used = num(db.prepare('SELECT COUNT(*) n FROM stock_moves WHERE ingredient_id = ?').get(ing.id).n)
        + num(db.prepare('SELECT COUNT(*) n FROM recipes WHERE ingredient_id = ?').get(ing.id).n);
      if (used > 0) {
        db.prepare('UPDATE ingredients SET active = 0 WHERE id = ?').run(ing.id);
        return { ok: true, archived: true, reason: 'Kept because it appears in recipes or stock history' };
      }
      db.prepare('DELETE FROM ingredients WHERE id = ?').run(ing.id);
      return { ok: true, deleted: true };
    });
  });

  /**
   * Record a stock movement. A purchase may also update the ingredient's
   * unit cost, which is how costing stays in step with supplier prices.
   */
  r.post('/api/ingredients/:id/stock', (ctx) => {
    requireUser(ctx);
    const ing = mustExist('ingredients', ctx.params.id, 'Ingredient');
    const b = ctx.body ?? {};
    const clientRef = strOrNull(clip(b.client_ref, 80));
    if (clientRef) {
      const dup = findByClientRef('stock_moves', clientRef);
      if (dup) return replayedMove(dup, ing);
    }
    const kind = str(b.kind);
    if (!MOVE_KINDS.includes(kind)) throw badRequest(`kind must be one of: ${MOVE_KINDS.join(', ')}`);

    const isOwnerAction = kind === 'purchase' || kind === 'adjustment';
    if (isOwnerAction && ctx.user.role !== 'owner') {
      throw forbidden('Only the owner can record purchases or stock adjustments');
    }

    const result = tx(() => {
      let signed;
      if (kind === 'purchase') {
        const q = requireAmount(b.qty, 'Quantity');
        if (q <= 0) throw badRequest('Quantity must be above zero');
        signed = round(q, 3);
      } else if (kind === 'usage' || kind === 'waste') {
        const q = requireAmount(b.qty, 'Quantity');
        if (q <= 0) throw badRequest('Quantity must be above zero');
        signed = -round(q, 3);
      } else {
        // adjustment: either a signed delta, or a counted "set_to" value
        if (b.set_to !== undefined && b.set_to !== null && b.set_to !== '') {
          signed = round(num(b.set_to) - num(ing.stock), 3);
        } else {
          signed = round(num(b.qty), 3);
          if (signed === 0) throw badRequest('Enter the counted quantity or a change');
        }
      }

      const unitCost = b.unit_cost !== undefined && b.unit_cost !== null && b.unit_cost !== ''
        ? money(requireAmount(b.unit_cost, 'Unit cost'))
        : money(ing.cost_per_unit);
      const totalCost = money(Math.abs(signed) * unitCost);
      const stamp = now();

      insMove.run(ing.id, kind, signed, unitCost, totalCost, strOrNull(clip(b.note, 300)),
        strOrNull(clip(b.ref, 60)), ctx.user.id, stamp, clientRef);

      const newStock = round(num(ing.stock) + signed, 3);
      setStock.run(newStock, ing.id);

      // A purchase price is the newest truth about what this ingredient costs.
      if (kind === 'purchase' && unitCost > 0 && unitCost !== money(ing.cost_per_unit)) {
        db.prepare('UPDATE ingredients SET cost_per_unit = ? WHERE id = ?').run(unitCost, ing.id);
      }
      return { stock: newStock, signed, total_cost: totalCost, unit_cost: unitCost,
        cost_updated: kind === 'purchase' && unitCost > 0 && unitCost !== money(ing.cost_per_unit) };
    });
    return { ok: true, ...result };
  });

  r.get('/api/stock-moves', (ctx) => {
    requireUser(ctx);
    const seeCosts = canSeeCosts(ctx);
    const limit = Math.min(500, Math.max(1, int(ctx.query.limit, 100)));
    const where = [];
    const params = [];
    if (ctx.query.ingredient_id) { where.push('m.ingredient_id = ?'); params.push(int(ctx.query.ingredient_id)); }
    if (ctx.query.kind) { where.push('m.kind = ?'); params.push(str(ctx.query.kind)); }
    const { from, to } = rangeOf(ctx.query, tz());
    where.push('m.created_at BETWEEN ? AND ?'); params.push(`${from} 00:00:00`, `${to} 23:59:59`);
    const rows = db.prepare(
      `SELECT m.*, i.name AS ingredient, i.unit, u.name AS user
         FROM stock_moves m
         JOIN ingredients i ON i.id = m.ingredient_id
         LEFT JOIN users u ON u.id = m.user_id
        WHERE ${where.join(' AND ')}
        ORDER BY m.created_at DESC, m.id DESC LIMIT ?`).all(...params, limit);
    return rows.map((x) => stripCosts({ ...x, qty: round(x.qty, 3) }, seeCosts));
  });

  /* ---------------- suppliers ---------------- */

  r.get('/api/suppliers', (ctx) => { requireUser(ctx); return db.prepare('SELECT * FROM suppliers ORDER BY name').all(); });

  r.post('/api/suppliers', (ctx) => {
    requireOwner(ctx);
    const b = ctx.body ?? {};
    const name = clip(require_(b.name, 'Supplier name'), 120);
    const id = Number(db.prepare('INSERT INTO suppliers (name, phone, notes, created_at) VALUES (?,?,?,?)')
      .run(name, strOrNull(clip(b.phone, 40)), strOrNull(clip(b.notes, 400)), now()).lastInsertRowid);
    return { id, name };
  });

  r.put('/api/suppliers/:id', (ctx) => {
    requireOwner(ctx);
    const s = mustExist('suppliers', ctx.params.id, 'Supplier');
    const b = ctx.body ?? {};
    db.prepare('UPDATE suppliers SET name=?, phone=?, notes=? WHERE id=?')
      .run(b.name !== undefined ? clip(require_(b.name, 'Supplier name'), 120) : s.name,
        b.phone !== undefined ? strOrNull(clip(b.phone, 40)) : s.phone,
        b.notes !== undefined ? strOrNull(clip(b.notes, 400)) : s.notes, s.id);
    return { ok: true };
  });

  r.delete('/api/suppliers/:id', (ctx) => {
    requireOwner(ctx);
    const s = mustExist('suppliers', ctx.params.id, 'Supplier');
    const used = num(db.prepare('SELECT COUNT(*) n FROM ingredients WHERE supplier_id = ?').get(s.id).n);
    if (used > 0) throw badRequest(`${used} ingredient(s) list this supplier — reassign them first`);
    db.prepare('DELETE FROM suppliers WHERE id = ?').run(s.id);
    return { ok: true };
  });

  /* ---------------- customers ---------------- */

  r.get('/api/customers', (ctx) => {
    requireUser(ctx);
    const q = str(ctx.query.q).toLowerCase();
    const limit = Math.min(500, Math.max(1, int(ctx.query.limit, 200)));
    let rows = db.prepare(
      `SELECT c.*,
              (SELECT COUNT(*) FROM sales s WHERE s.customer_id = c.id AND s.status <> 'void') AS orders,
              (SELECT COALESCE(SUM(s.total),0) FROM sales s WHERE s.customer_id = c.id AND s.status <> 'void') AS revenue,
              (SELECT COALESCE(SUM(s.total - s.paid),0) FROM sales s WHERE s.customer_id = c.id AND s.status IN ('partial','unpaid')) AS owed,
              (SELECT MAX(s.sale_at) FROM sales s WHERE s.customer_id = c.id AND s.status <> 'void') AS last_visit
         FROM customers c ORDER BY c.is_walk_in DESC, c.name LIMIT ?`).all(limit);
    if (q) rows = rows.filter((c) => c.name.toLowerCase().includes(q) || str(c.phone).includes(q));
    return rows.map((c) => ({ ...c, revenue: money(c.revenue), owed: money(c.owed) }));
  });

  r.post('/api/customers', (ctx) => {
    requireUser(ctx);
    const b = ctx.body ?? {};
    const name = clip(require_(b.name, 'Customer name'), 120);
    const id = Number(db.prepare(
      'INSERT INTO customers (name, phone, address, notes, is_walk_in, created_at, updated_at) VALUES (?,?,?,?,0,?,?)')
      .run(name, strOrNull(clip(b.phone, 40)), strOrNull(clip(b.address, 200)), strOrNull(clip(b.notes, 400)), now(), nowStamp()).lastInsertRowid);
    return { id, name };
  });

  r.put('/api/customers/:id', (ctx) => {
    requireUser(ctx);
    return guardedWrite(ctx, 'customers', ctx.params.id, 'update', () => updateCustomer(ctx));
  });

  function updateCustomer(ctx) {
    const c = mustExist('customers', ctx.params.id, 'Customer');
    const b = ctx.body ?? {};
    db.prepare('UPDATE customers SET name=?, phone=?, address=?, notes=? WHERE id=?')
      .run(b.name !== undefined ? clip(require_(b.name, 'Customer name'), 120) : c.name,
        b.phone !== undefined ? strOrNull(clip(b.phone, 40)) : c.phone,
        b.address !== undefined ? strOrNull(clip(b.address, 200)) : c.address,
        b.notes !== undefined ? strOrNull(clip(b.notes, 400)) : c.notes, c.id);
    return { ok: true };
  }

  r.delete('/api/customers/:id', (ctx) => {
    requireOwner(ctx);
    return guardedWrite(ctx, 'customers', ctx.params.id, 'delete', () => {
      const c = mustExist('customers', ctx.params.id, 'Customer');
      if (c.is_walk_in) throw badRequest('The walk-in customer cannot be deleted');
      const used = num(db.prepare('SELECT COUNT(*) n FROM sales WHERE customer_id = ?').get(c.id).n);
      if (used > 0) throw badRequest(`This customer has ${used} sale(s). Deleting them would break your records.`);
      db.prepare('DELETE FROM customers WHERE id = ?').run(c.id);
      return { ok: true, deleted: true };
    });
  });

  /* ---------------- sales / point of sale ---------------- */

  r.get('/api/sales', (ctx) => {
    requireUser(ctx);
    const { from, to } = rangeOf(ctx.query, tz());
    const limit = Math.min(300, Math.max(1, int(ctx.query.limit, 60)));
    const offset = Math.max(0, int(ctx.query.offset, 0));
    const where = ['s.sale_at BETWEEN ? AND ?'];
    const params = [`${from} 00:00:00`, `${to} 23:59:59`];

    if (ctx.query.status) { where.push('s.status = ?'); params.push(str(ctx.query.status)); }
    if (ctx.query.method) { where.push('s.method = ?'); params.push(str(ctx.query.method)); }
    if (ctx.query.user_id) { where.push('s.user_id = ?'); params.push(int(ctx.query.user_id)); }
    if (ctx.query.customer_id) { where.push('s.customer_id = ?'); params.push(int(ctx.query.customer_id)); }
    if (ctx.query.q) {
      where.push('(s.invoice_no LIKE ? OR s.note LIKE ? OR c.name LIKE ?)');
      const like = `%${str(ctx.query.q)}%`;
      params.push(like, like, like);
    }
    // Staff see their own sales only; the owner sees everything.
    if (ctx.user.role !== 'owner') { where.push('s.user_id = ?'); params.push(ctx.user.id); }

    const rows = db.prepare(
      `SELECT s.*, c.name AS customer, u.name AS sold_by,
              (SELECT COUNT(*) FROM sale_items si WHERE si.sale_id = s.id) AS item_count,
              (SELECT COALESCE(SUM(si.qty),0) FROM sale_items si WHERE si.sale_id = s.id) AS qty,
              (SELECT COALESCE(SUM(si.line_cost),0) FROM sale_items si WHERE si.sale_id = s.id) AS cogs
         FROM sales s
         LEFT JOIN customers c ON c.id = s.customer_id
         LEFT JOIN users u ON u.id = s.user_id
        WHERE ${where.join(' AND ')}
        ORDER BY s.sale_at DESC, s.id DESC LIMIT ? OFFSET ?`)
      .all(...params, limit, offset);

    const totals = db.prepare(
      `SELECT COUNT(*) AS n, COALESCE(SUM(s.total),0) AS revenue, COALESCE(SUM(s.paid),0) AS collected
         FROM sales s LEFT JOIN customers c ON c.id = s.customer_id
        WHERE ${where.join(' AND ')} AND s.status <> 'void'`).get(...params);

    return {
      from, to, limit, offset,
      sales: rows.map((s) => stripCosts({
        ...s, total: money(s.total), subtotal: money(s.subtotal),
        discount: money(s.discount), paid: money(s.paid),
        due: money(num(s.total) - num(s.paid)), qty: round(s.qty, 2),
      }, canSeeCosts(ctx))),
      totals: { count: num(totals.n), revenue: money(totals.revenue), collected: money(totals.collected) },
    };
  });

  r.get('/api/sales/:id', (ctx) => {
    requireUser(ctx);
    const s = mustExist('sales', ctx.params.id, 'Sale');
    if (ctx.user.role !== 'owner' && s.user_id !== ctx.user.id) {
      throw forbidden('That sale belongs to another staff member');
    }
    const items = db.prepare('SELECT * FROM sale_items WHERE sale_id = ? ORDER BY id').all(s.id)
      .map((i) => stripCosts({ ...i, unit_price: money(i.unit_price), line_total: money(i.line_total),
        line_cost: money(i.line_cost), qty: round(i.qty, 2) }, canSeeCosts(ctx)));
    const cogs = money(items.reduce((a, i) => a + num(i.line_cost ?? 0), 0));
    return stripCosts({
      ...s,
      cogs,
      profit: money(num(s.total) - cogs),
      margin_pct: num(s.total) ? round(((num(s.total) - cogs) / num(s.total)) * 100, 1) : 0,
      total: money(s.total), subtotal: money(s.subtotal), discount: money(s.discount), paid: money(s.paid),
      due: money(num(s.total) - num(s.paid)),
      customer: s.customer_id ? db.prepare('SELECT id, name, phone, address FROM customers WHERE id=?').get(s.customer_id) : null,
      sold_by: s.user_id ? db.prepare('SELECT name FROM users WHERE id=?').get(s.user_id)?.name ?? null : null,
      items,
      business: {
        name: getSetting('business_name'), address: getSetting('address'), phone: getSetting('phone'),
        note: getSetting('receipt_note'), symbol: getSetting('currency_symbol'), decimals: decimals(),
      },
    }, canSeeCosts(ctx));
  });

  r.post('/api/sales', (ctx) => createSale(ctx));

  r.post('/api/sales/:id/void', (ctx) => {
    requireOwner(ctx);
    const s = mustExist('sales', ctx.params.id, 'Sale');
    if (s.status === 'void') throw badRequest('That sale is already voided');
    tx(() => {
      db.prepare("UPDATE sales SET status = 'void' WHERE id = ?").run(s.id);
      // Put the ingredients back on the shelf.
      const used = db.prepare(
        `SELECT ingredient_id, SUM(qty) AS qty FROM stock_moves
          WHERE ref = ? AND kind = 'usage' GROUP BY ingredient_id`).all(s.invoice_no);
      const stamp = now();
      for (const m of used) {
        const ing = getIngredient.get(m.ingredient_id);
        if (!ing) continue;
        const back = round(-num(m.qty), 3);
        if (!back) continue;
        insMove.run(ing.id, 'adjustment', back, money(ing.cost_per_unit), money(Math.abs(back) * num(ing.cost_per_unit)),
          `Reversal of voided ${s.invoice_no}`, s.invoice_no, ctx.user.id, stamp, null);
        setStock.run(round(num(ing.stock) + back, 3), ing.id);
      }
    });
    return { ok: true };
  });

  /** Take a payment against a credit/partial sale. */
  r.post('/api/sales/:id/payment', (ctx) => {
    requireUser(ctx);
    const s = mustExist('sales', ctx.params.id, 'Sale');
    if (s.status === 'void') throw badRequest('Cannot take payment on a voided sale');
    if (ctx.user.role !== 'owner' && s.user_id !== ctx.user.id) throw forbidden('That sale belongs to another staff member');
    const amount = money(requireAmount(ctx.body?.amount, 'Amount'));
    if (amount <= 0) throw badRequest('Enter an amount above zero');
    const method = METHODS.includes(str(ctx.body?.method)) ? str(ctx.body?.method) : s.method;
    const paid = money(Math.min(num(s.total), num(s.paid) + amount));
    const status = paid >= money(s.total) ? 'paid' : 'partial';
    db.prepare('UPDATE sales SET paid = ?, method = ?, status = ? WHERE id = ?').run(paid, method, status, s.id);
    return { ok: true, paid, due: money(num(s.total) - paid), status };
  });

  /* ---------------- expenses ---------------- */

  r.get('/api/expenses', (ctx) => {
    requireUser(ctx);
    const { from, to } = rangeOf(ctx.query, tz());
    const where = ['e.expense_at BETWEEN ? AND ?'];
    const params = [`${from} 00:00:00`, `${to} 23:59:59`];
    if (ctx.query.category) { where.push('e.category = ?'); params.push(str(ctx.query.category)); }
    if (ctx.query.q) { where.push('(e.title LIKE ? OR e.note LIKE ?)'); const l = `%${str(ctx.query.q)}%`; params.push(l, l); }
    // Staff may record expenses but only review their own.
    if (ctx.user.role !== 'owner') { where.push('e.user_id = ?'); params.push(ctx.user.id); }
    const rows = db.prepare(
      `SELECT e.*, u.name AS recorded_by FROM expenses e LEFT JOIN users u ON u.id = e.user_id
        WHERE ${where.join(' AND ')} ORDER BY e.expense_at DESC, e.id DESC LIMIT 500`).all(...params);
    const totals = db.prepare(
      `SELECT COUNT(*) n, COALESCE(SUM(amount),0) total FROM expenses e WHERE ${where.join(' AND ')}`).get(...params);
    return { from, to, expenses: rows.map((e) => ({ ...e, amount: money(e.amount) })),
      totals: { count: num(totals.n), total: money(totals.total) }, categories: EXPENSE_CATEGORIES };
  });

  r.post('/api/expenses', (ctx) => {
    requireUser(ctx);
    const b = ctx.body ?? {};
    const title = clip(require_(b.title, 'Title'), 160);
    const amount = money(requireAmount(b.amount, 'Amount'));
    if (amount <= 0) throw badRequest('Amount must be above zero');
    const category = clip(str(b.category, 'Other'), 60);
    const when = normaliseWhen(b.expense_at, now());
    const clientRef = strOrNull(clip(b.client_ref, 80));
    if (clientRef) {
      const dup = findByClientRef('expenses', clientRef);
      if (dup) return replayedExpense(dup);
    }
    const id = Number(db.prepare(
      'INSERT INTO expenses (title, category, amount, note, user_id, expense_at, created_at, client_ref, updated_at) VALUES (?,?,?,?,?,?,?,?,?)')
      .run(title, category, amount, strOrNull(clip(b.note, 400)), ctx.user.id, when, now(), clientRef, nowStamp()).lastInsertRowid);
    return { ok: true, replay: false, id, title, amount, category };
  });

  r.put('/api/expenses/:id', (ctx) => {
    requireUser(ctx);
    assertExpenseOwnership(ctx, ctx.params.id);
    return guardedWrite(ctx, 'expenses', ctx.params.id, 'update', () => updateExpense(ctx));
  });

  /** Checked before the replay lookup, not inside it. */
  function assertExpenseOwnership(ctx, id) {
    const e = db.prepare('SELECT user_id FROM expenses WHERE id = ?').get(Number(id));
    if (e && ctx.user.role !== 'owner' && e.user_id !== ctx.user.id) {
      throw forbidden('That expense belongs to someone else');
    }
  }

  function updateExpense(ctx) {
    const e = mustExist('expenses', ctx.params.id, 'Expense');
    const b = ctx.body ?? {};
    db.prepare('UPDATE expenses SET title=?, category=?, amount=?, note=?, expense_at=? WHERE id=?')
      .run(b.title !== undefined ? clip(require_(b.title, 'Title'), 160) : e.title,
        b.category !== undefined ? clip(str(b.category, e.category), 60) : e.category,
        b.amount !== undefined ? money(requireAmount(b.amount, 'Amount')) : e.amount,
        b.note !== undefined ? strOrNull(clip(b.note, 400)) : e.note,
        b.expense_at !== undefined ? normaliseWhen(b.expense_at, e.expense_at) : e.expense_at, e.id);
    return { ok: true };
  }

  r.delete('/api/expenses/:id', (ctx) => {
    requireUser(ctx);
    assertExpenseOwnership(ctx, ctx.params.id);
    return guardedWrite(ctx, 'expenses', ctx.params.id, 'delete', () => {
      const e = mustExist('expenses', ctx.params.id, 'Expense');
      db.prepare('DELETE FROM expenses WHERE id = ?').run(e.id);
      return { ok: true, deleted: true };
    });
  });

  /* ---------------- users (owner) ---------------- */

  r.get('/api/users', (ctx) => {
    requireOwner(ctx);
    return db.prepare(
      `SELECT u.id, u.name, u.phone, u.role, u.active, u.must_change, u.created_at,
              (SELECT COUNT(*) FROM sales s WHERE s.user_id = u.id) AS sales_count,
              (SELECT MAX(s.sale_at) FROM sales s WHERE s.user_id = u.id) AS last_sale
         FROM users u ORDER BY u.role, u.name`).all();
  });

  r.post('/api/users', (ctx) => {
    requireOwner(ctx);
    const b = ctx.body ?? {};
    const name = clip(require_(b.name, 'Name'), 80);
    const phone = clip(require_(b.phone, 'Phone number'), 30);
    const password = str(b.password);
    if (password.length < 6) throw badRequest('Use at least 6 characters for their password');
    const role = str(b.role) === 'owner' ? 'owner' : 'staff';
    if (db.prepare('SELECT id FROM users WHERE lower(phone)=lower(?)').get(phone)) {
      throw badRequest('That phone number is already registered');
    }
    const { salt, hash } = hashPassword(password);
    const id = Number(db.prepare(
      `INSERT INTO users (name, phone, role, pass_hash, pass_salt, must_change, active, created_at)
       VALUES (?,?,?,?,?,1,?,?)`)
      .run(name, phone, role, hash, salt, bool(b.active ?? 1), now()).lastInsertRowid);
    return { id, name, phone, role };
  });

  r.put('/api/users/:id', (ctx) => {
    requireOwner(ctx);
    const u = mustExist('users', ctx.params.id, 'User');
    const b = ctx.body ?? {};
    const role = b.role !== undefined ? (str(b.role) === 'owner' ? 'owner' : 'staff') : u.role;
    const active = b.active !== undefined ? bool(b.active) : u.active;

    if (u.id === ctx.user.id && (!active || role !== 'owner')) {
      throw badRequest('You cannot remove your own owner access');
    }
    if (u.role === 'owner' && role !== 'owner' && active) {
      const owners = num(db.prepare("SELECT COUNT(*) n FROM users WHERE role='owner' AND active=1").get().n);
      if (owners <= 1) throw badRequest('Keep at least one active owner');
    }
    if (b.phone !== undefined) {
      const phone = clip(require_(b.phone, 'Phone number'), 30);
      const dup = db.prepare('SELECT id FROM users WHERE lower(phone)=lower(?) AND id <> ?').get(phone, u.id);
      if (dup) throw badRequest('That phone number is already registered');
      db.prepare('UPDATE users SET phone=? WHERE id=?').run(phone, u.id);
    }
    db.prepare('UPDATE users SET name=?, role=?, active=? WHERE id=?')
      .run(b.name !== undefined ? clip(require_(b.name, 'Name'), 80) : u.name, role, active, u.id);
    if (!active) db.prepare('DELETE FROM sessions WHERE user_id = ?').run(u.id);
    return { ok: true };
  });

  r.post('/api/users/:id/password', (ctx) => {
    requireOwner(ctx);
    const u = mustExist('users', ctx.params.id, 'User');
    const password = str(ctx.body?.password);
    if (password.length < 6) throw badRequest('Use at least 6 characters');
    const { salt, hash } = hashPassword(password);
    db.prepare('UPDATE users SET pass_hash=?, pass_salt=?, must_change=1 WHERE id=?').run(hash, salt, u.id);
    if (u.id !== ctx.user.id) db.prepare('DELETE FROM sessions WHERE user_id = ?').run(u.id);
    return { ok: true };
  });

  r.delete('/api/users/:id', (ctx) => {
    requireOwner(ctx);
    const u = mustExist('users', ctx.params.id, 'User');
    if (u.id === ctx.user.id) throw badRequest('You cannot delete your own account');
    if (u.role === 'owner') {
      const owners = num(db.prepare("SELECT COUNT(*) n FROM users WHERE role='owner' AND active=1").get().n);
      if (owners <= 1) throw badRequest('Keep at least one active owner — deactivate instead');
    }
    const sales = num(db.prepare('SELECT COUNT(*) n FROM sales WHERE user_id = ?').get(u.id).n);
    if (sales > 0) {
      db.prepare('UPDATE users SET active = 0 WHERE id = ?').run(u.id);
      db.prepare('DELETE FROM sessions WHERE user_id = ?').run(u.id);
      return { ok: true, archived: true, reason: `Deactivated instead of deleted: ${sales} sale(s) are recorded under this name` };
    }
    db.prepare('DELETE FROM users WHERE id = ?').run(u.id);
    return { ok: true, deleted: true };
  });

  /* ---------------- reference data ---------------- */

  r.get('/api/meta', (ctx) => {
    requireUser(ctx);
    return { methods: METHODS, moveKinds: MOVE_KINDS, expenseCategories: EXPENSE_CATEGORIES,
      units: ['kg', 'g', 'L', 'ml', 'pcs', 'bottle', 'bag', 'box', 'tray', 'dozen'],
      timezones: ['Africa/Bujumbura', 'Africa/Kampala', 'Africa/Nairobi', 'Africa/Kigali',
        'Africa/Dar_es_Salaam', 'Africa/Lubumbashi', 'Africa/Lagos', 'UTC'] };
  });

  /**
   * A staff member's own performance. Deliberately excludes every cost and
   * profit figure — those belong to the owner-only reports.
   */
  r.get('/api/my-summary', (ctx) => {
    const user = requireUser(ctx);
    const today = serverToday();
    const monthStart = `${today.slice(0, 7)}-01`;
    const from14 = addDays(today, -13);
    const lo = (d) => `${d} 00:00:00`;
    const hi = (d) => `${d} 23:59:59`;

    const window_ = (from, to) => db.prepare(
      `SELECT COUNT(*) AS sales,
              COALESCE(SUM(s.total), 0) AS revenue,
              COALESCE(SUM(s.paid), 0) AS collected,
              COALESCE(SUM(s.discount), 0) AS discounts,
              COALESCE((SELECT SUM(si.qty) FROM sale_items si
                         WHERE si.sale_id IN (SELECT s2.id FROM sales s2
                          WHERE s2.user_id = ? AND s2.status <> 'void'
                            AND s2.sale_at BETWEEN ? AND ?)), 0) AS items
         FROM sales s
        WHERE s.user_id = ? AND s.status <> 'void' AND s.sale_at BETWEEN ? AND ?`)
      .get(user.id, lo(from), hi(to), user.id, lo(from), hi(to));

    const shape = (r) => ({
      sales: num(r.sales),
      revenue: money(r.revenue),
      collected: money(r.collected),
      discounts: money(r.discounts),
      items: round(r.items, 2),
      averageSale: num(r.sales) ? money(num(r.revenue) / num(r.sales)) : 0,
    });

    const seriesRows = db.prepare(
      `SELECT substr(sale_at, 1, 10) AS d, COUNT(*) AS n, COALESCE(SUM(total), 0) AS revenue
         FROM sales
        WHERE user_id = ? AND status <> 'void' AND sale_at BETWEEN ? AND ?
        GROUP BY d`).all(user.id, lo(from14), hi(today));
    const byDay = new Map(seriesRows.map((r) => [r.d, r]));
    const series = [];
    for (let d = from14; d <= today; d = addDays(d, 1)) {
      const row = byDay.get(d);
      series.push({ bucket: d, sales: num(row?.n ?? 0), revenue: money(row?.revenue ?? 0) });
    }

    return { today: shape(window_(today, today)), month: shape(window_(monthStart, today)), series };
  });

  /**
   * Public: the browser reports its own JavaScript errors here.
   *
   * A sign-in that silently does nothing is almost always a client-side
   * exception, and the only place its owner looks is the server terminal.
   * Printing the browser's error there turns "nothing happens" into a message
   * we can actually read. Deliberately tiny and rate-limited.
   */
  const clientLogBudget = new Map();
  r.post('/api/client-log', (ctx) => {
    const ip = String(ctx.req?.socket?.remoteAddress || '?');
    const n = (clientLogBudget.get(ip) || 0) + 1;
    clientLogBudget.set(ip, n);
    if (n > 30) return { ok: true, suppressed: true };
    const b = ctx.body ?? {};
    console.log(`[browser-error] ${clip(str(b.message), 300)}`
      + (b.src ? ` (${clip(str(b.src), 120)}:${int(b.line)})` : '')
      + (b.ua ? ` | ${clip(str(b.ua), 120)}` : ''));
    return { ok: true };
  });

  /** Public: tells the login screen whether first-run setup is needed. */
  r.get('/api/status', () => ({
    needsSetup: isEmpty(),
    businessName: getSetting('business_name', 'Bakery Tracker'),
    currencySymbol: getSetting('currency_symbol', 'FBu'),
    demo: getSetting('demo_seeded') === '1',
  }));

  r.get('/api/health', () => ({ ok: true, time: now(), timezone: tz(), counts: tableCounts() }));
}

/* ------------------------------------------------------------------ *
 * Sale creation — the heart of the till
 * ------------------------------------------------------------------ */

function createSale(ctx) {
  const user = requireUser(ctx);
  const b = ctx.body ?? {};

  // A phone that queued this sale while offline may send it more than once if
  // the connection drops mid-request. client_ref is its idempotency key: if the
  // sale is already recorded we answer with the original instead of selling twice.
  const clientRef = strOrNull(clip(b.client_ref, 80));
  if (clientRef) {
    const dup = findByClientRef('sales', clientRef);
    if (dup) return replayedSale(dup);
  }

  const rawItems = Array.isArray(b.items) ? b.items : [];
  if (!rawItems.length) throw badRequest('Add at least one item');
  if (rawItems.length > 200) throw badRequest('Too many lines on one sale');

  const autoDeduct = getSetting('auto_deduct_stock', '1') === '1';
  const stamp = now();
  const saleAt = normaliseWhen(b.sale_at, stamp);
  const getProduct = db.prepare('SELECT * FROM products WHERE id = ?');

  // Build and validate every line before touching the database.
  const lines = [];
  let subtotal = 0;
  for (const raw of rawItems) {
    const pid = idOrNull(raw.product_id);
    const qty = round(num(raw.qty), 3);
    if (!pid) throw badRequest('Every line needs a product');
    if (!(qty > 0)) throw badRequest('Quantity must be above zero');
    if (qty > 100000) throw badRequest('That quantity looks wrong');
    const p = getProduct.get(pid);
    if (!p) throw badRequest('One of the products no longer exists — refresh and try again');
    if (!p.active) throw badRequest(`"${p.name}" is archived and cannot be sold`);

    const hasOverride = raw.unit_price !== undefined && raw.unit_price !== null && raw.unit_price !== '';
    const unitPrice = money(hasOverride ? num(raw.unit_price) : p.price);
    if (unitPrice < 0) throw badRequest('Price cannot be negative');
    if (hasOverride && unitPrice !== money(p.price) && user.role !== 'owner' && num(p.price) > 0
        && unitPrice < money(num(p.price) * 0.5)) {
      throw forbidden('Only the owner can discount an item by more than half');
    }

    const unitCost = unitCostOf(pid);
    subtotal += qty * unitPrice;
    lines.push({
      product_id: pid, name: p.name, qty,
      unit_price: unitPrice, unit_cost: unitCost,
      line_total: money(qty * unitPrice), line_cost: money(qty * unitCost),
    });
  }
  subtotal = money(subtotal);

  let discount = money(Math.max(0, num(b.discount)));
  if (discount > subtotal) discount = subtotal;
  const total = money(subtotal - discount);

  const method = METHODS.includes(str(b.method)) ? str(b.method) : 'cash';
  const requestedPaid = b.paid === undefined || b.paid === null || b.paid === '' ? total : money(num(b.paid));
  if (requestedPaid < 0) throw badRequest('Amount paid cannot be negative');
  const paid = money(Math.min(requestedPaid, total));
  const status = total <= 0 || paid >= total ? 'paid' : paid > 0 ? 'partial' : 'unpaid';
  if (method !== 'credit' && paid < total) {
    throw badRequest(`Choose "On credit" to record a part-payment of ${paid} against ${total}`);
  }

  const customerId = idOrNull(b.customer_id);
  if (customerId && !db.prepare('SELECT id FROM customers WHERE id = ?').get(customerId)) {
    throw badRequest('That customer no longer exists — refresh and try again');
  }

  return tx(() => {
    const invoice = nextInvoiceNo();
    const saleId = Number(db.prepare(
      `INSERT INTO sales (invoice_no, customer_id, user_id, subtotal, discount, total, paid, method, status, note, sale_at, created_at, client_ref)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)`)
      .run(invoice, customerId, user.id, subtotal, discount, total, paid, method, status,
        strOrNull(clip(b.note, 300)), saleAt, stamp, clientRef).lastInsertRowid);

    const insItem = db.prepare(
      `INSERT INTO sale_items (sale_id, product_id, name, qty, unit_price, line_total, unit_cost, line_cost)
       VALUES (?,?,?,?,?,?,?,?)`);
    for (const l of lines) {
      insItem.run(saleId, l.product_id, l.name, l.qty, l.unit_price, l.line_total, l.unit_cost, l.line_cost);
    }

    let stockMoves = 0;
    if (autoDeduct) {
      const recipeOf = db.prepare('SELECT ingredient_id, qty FROM recipes WHERE product_id = ?');
      for (const l of lines) {
        for (const rc of recipeOf.all(l.product_id)) {
          const used = round(num(rc.qty) * l.qty, 3);
          if (!(used > 0)) continue;
          const ing = getIngredient.get(rc.ingredient_id);
          if (!ing) continue;
          const cost = money(used * num(ing.cost_per_unit));
          insMove.run(ing.id, 'usage', -used, money(ing.cost_per_unit), cost,
            `Used in ${invoice}`, invoice, user.id, stamp, null);
          setStock.run(round(num(ing.stock) - used, 3), ing.id);
          stockMoves++;
        }
      }
    }

    return {
      ok: true, replay: false, id: saleId, invoice_no: invoice, subtotal, discount, total, paid,
      due: money(total - paid), status, method, change: money(Math.max(0, requestedPaid - total)),
      stock_moves: stockMoves, sale_at: saleAt,
      low_stock: getSetting('low_stock_alerts', '1') === '1' ? lowStockNames() : [],
    };
  });
}

/** Names of ingredients that just dropped to or below their reorder level. */
function lowStockNames(limit = 5) {
  return db.prepare(
    `SELECT name FROM ingredients
      WHERE active = 1 AND reorder_level > 0 AND stock <= reorder_level
      ORDER BY (stock / MAX(reorder_level, 0.0001)) ASC LIMIT ?`).all(limit).map((x) => x.name);
}
