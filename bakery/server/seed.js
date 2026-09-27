/**
 * Demo seed data: a realistic Bujumbura bakery with ~60 days of trading
 * history, so every report and chart has something to show on first login.
 *
 * Recipe yields and prices are calibrated so each product lands in the
 * 50-70% gross-margin band a bakery actually targets, and the stock ledger
 * balances: opening purchases cover everything the 60 days consumed, so
 * ending stock is exactly what the catalogue says it is.
 *
 * Uses a fixed PRNG seed so the demo dataset is reproducible.
 */
import { db, tx, hashPassword, unitCostOf, money, tz, now } from './db.js';
import { localStamp, addDays, localDate, num, round } from './util.js';

/* Deterministic PRNG (mulberry32) */
function rng(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rand = rng(20260927);
const pick = (arr) => arr[Math.floor(rand() * arr.length)];
const between = (lo, hi) => lo + rand() * (hi - lo);
const intBetween = (lo, hi) => Math.floor(between(lo, hi + 1));
const chance = (p) => rand() < p;

/* ------------------------------------------------------------------ *
 * Catalogue
 * ------------------------------------------------------------------ */

const CATEGORIES = ['Bread', 'Pastries', 'Cakes', 'Snacks', 'Drinks'];

// name, category, selling price (FBu)
const PRODUCTS = [
  ['Bread loaf (Umukate)', 'Bread', 2000],
  ['Baguette', 'Bread', 2500],
  ['Bread roll', 'Bread', 500],
  ['Whole wheat loaf', 'Bread', 3000],
  ['Chapati', 'Pastries', 1000],
  ['Mandazi (5 pcs)', 'Pastries', 2000],
  ['Donut', 'Pastries', 1200],
  ['Croissant', 'Pastries', 2200],
  ['Cinnamon bun', 'Pastries', 2000],
  ['Birthday cake 1kg', 'Cakes', 28000],
  ['Cupcake', 'Cakes', 1500],
  ['Chocolate cake slice', 'Cakes', 3500],
  ['Sausage roll', 'Snacks', 2500],
  ['Meat pie', 'Snacks', 3500],
  ['Cheese bun', 'Snacks', 2200],
  ['Biscuit pack', 'Snacks', 3000],
  ['Tea (chai)', 'Drinks', 600],
  ['Coffee', 'Drinks', 1000],
  ['Juice bottle', 'Drinks', 1800],
];

const SUPPLIERS = [
  ['Mukase Millers', '+257 71 22 33 44', 'Flour and dry goods, delivers Mon & Thu'],
  ['Bujumbura Wholesale Ltd', '+257 76 55 12 90', 'Sugar, oil, salt, baking powder'],
  ['Kigobe Dairy & Eggs', '+257 79 88 41 07', 'Milk, butter and eggs — call a day ahead'],
  ['Rohero Packaging', '+257 72 30 19 55', 'Paper bags, cups and cake boxes'],
];

// name, unit, cost per unit (FBu), target ending stock, reorder level, supplier index
// Ending stock is deliberately at/below reorder level for a few lines so the
// low-stock alerts have something to show.
const INGREDIENTS = [
  ['Wheat flour', 'kg', 2200, 260, 80, 0],
  ['Whole wheat flour', 'kg', 2900, 45, 30, 0],
  ['Sugar', 'kg', 2800, 90, 40, 1],
  ['Margarine', 'kg', 6500, 38, 20, 2],
  ['Butter', 'kg', 14000, 6, 8, 2],        // low
  ['Eggs', 'pcs', 400, 540, 300, 2],
  ['Milk', 'L', 2000, 55, 30, 2],
  ['Yeast', 'kg', 12000, 4.5, 3, 1],
  ['Salt', 'kg', 1200, 22, 10, 1],
  ['Cooking oil', 'L', 4500, 60, 25, 1],
  ['Baking powder', 'kg', 8000, 3.2, 2, 1],
  ['Cocoa powder', 'kg', 18000, 4, 3, 1],
  ['Vanilla essence', 'bottle', 5000, 3, 4, 1], // low
  ['Sausages', 'kg', 14000, 9, 6, 2],
  ['Minced meat', 'kg', 16000, 5.5, 6, 2], // low
  ['Cheese', 'kg', 22000, 3, 3, 2],        // low
  ['Cinnamon', 'kg', 25000, 1.2, 1, 1],
  ['Tea leaves', 'kg', 15000, 2.5, 2, 1],
  ['Coffee powder', 'kg', 20000, 3.5, 2, 1],
  ['Paper bag', 'pcs', 100, 700, 800, 3],  // low
  ['Paper cup', 'pcs', 60, 900, 400, 3],
  ['Cake box', 'pcs', 800, 55, 30, 3],
  ['Juice bottle', 'pcs', 1000, 40, 24, 1],
];

// product name -> [[ingredient, qty consumed per single unit sold], ...]
// Yields are per-item, e.g. a bread roll shares a bag with others (0.5).
const RECIPES = {
  'Bread loaf (Umukate)': [['Wheat flour', 0.35], ['Yeast', 0.005], ['Salt', 0.006], ['Sugar', 0.02], ['Paper bag', 1]],
  Baguette: [['Wheat flour', 0.4], ['Yeast', 0.006], ['Salt', 0.008], ['Paper bag', 1]],
  'Bread roll': [['Wheat flour', 0.055], ['Yeast', 0.0012], ['Salt', 0.001], ['Sugar', 0.004], ['Paper bag', 0.5]],
  'Whole wheat loaf': [['Whole wheat flour', 0.35], ['Wheat flour', 0.08], ['Yeast', 0.007], ['Salt', 0.007], ['Paper bag', 1]],
  Chapati: [['Wheat flour', 0.12], ['Cooking oil', 0.015], ['Salt', 0.002], ['Paper bag', 0.5]],
  'Mandazi (5 pcs)': [['Wheat flour', 0.18], ['Sugar', 0.04], ['Cooking oil', 0.022], ['Yeast', 0.0025], ['Paper bag', 1]],
  Donut: [['Wheat flour', 0.07], ['Sugar', 0.02], ['Cooking oil', 0.025], ['Eggs', 0.4], ['Paper bag', 0.5]],
  Croissant: [['Wheat flour', 0.1], ['Butter', 0.025], ['Milk', 0.04], ['Sugar', 0.012], ['Yeast', 0.003], ['Paper bag', 0.5]],
  'Cinnamon bun': [['Wheat flour', 0.1], ['Butter', 0.025], ['Sugar', 0.035], ['Cinnamon', 0.004], ['Milk', 0.035], ['Paper bag', 0.5]],
  'Birthday cake 1kg': [['Wheat flour', 0.4], ['Sugar', 0.4], ['Butter', 0.35], ['Eggs', 6], ['Milk', 0.2], ['Baking powder', 0.02], ['Vanilla essence', 0.1], ['Cake box', 1]],
  Cupcake: [['Wheat flour', 0.04], ['Sugar', 0.03], ['Margarine', 0.025], ['Eggs', 0.3], ['Baking powder', 0.002], ['Vanilla essence', 0.005], ['Paper bag', 0.5]],
  'Chocolate cake slice': [['Wheat flour', 0.06], ['Sugar', 0.05], ['Cocoa powder', 0.018], ['Butter', 0.03], ['Margarine', 0.02], ['Eggs', 0.5], ['Milk', 0.03], ['Paper bag', 0.5]],
  'Sausage roll': [['Wheat flour', 0.09], ['Margarine', 0.035], ['Sausages', 0.04], ['Eggs', 0.2], ['Paper bag', 0.5]],
  'Meat pie': [['Wheat flour', 0.1], ['Margarine', 0.04], ['Minced meat', 0.06], ['Eggs', 0.2], ['Salt', 0.003], ['Paper bag', 0.5]],
  'Cheese bun': [['Wheat flour', 0.1], ['Cheese', 0.025], ['Margarine', 0.02], ['Milk', 0.025], ['Yeast', 0.003], ['Paper bag', 0.5]],
  'Biscuit pack': [['Wheat flour', 0.15], ['Margarine', 0.07], ['Sugar', 0.06], ['Eggs', 0.5], ['Vanilla essence', 0.01], ['Paper bag', 1]],
  'Tea (chai)': [['Tea leaves', 0.005], ['Milk', 0.05], ['Sugar', 0.02], ['Paper cup', 1]],
  Coffee: [['Coffee powder', 0.012], ['Sugar', 0.02], ['Milk', 0.05], ['Paper cup', 1]],
  'Juice bottle': [['Juice bottle', 1]],
};

const CUSTOMERS = [
  ['Walk-in customer', null, null, 'Default counter customer'],
  ['Cafe Aroma', '+257 71 40 22 10', 'Rohero II, Bujumbura', 'Daily 20 loaves, pays by mobile money'],
  ['Hotel Club du Lac', '+257 78 22 60 14', 'Lac Tanganyika shore', 'Weekly pastry order, invoice at month end'],
  ['Ecole Belge de Bujumbura', '+257 76 11 05 33', 'Kiriri', 'School canteen — bread rolls twice a week'],
  ['Niyonkuru Josephine', '+257 79 55 71 08', 'Ngagara Q4', 'Regular, likes mandazi on Fridays'],
  ['Hakizimana Patrick', '+257 71 90 44 27', 'Kamenge', 'Orders birthday cakes for family'],
  ['Boutique Sandrine', '+257 72 68 30 91', 'Bwiza', 'Resells bread and biscuits'],
  ['Nkurunziza Fabrice', '+257 76 04 88 12', 'Musaga', 'Corporate meetings — croissants'],
  ['Ishimwe Divine', '+257 79 31 26 45', 'Rohero I', 'Wedding cake enquiries'],
  ['SOSUMO Office Canteen', '+257 71 77 19 02', 'Gitega road', 'Bulk bread order monthly'],
];

const EXPENSE_TEMPLATES = [
  // title, category, amount, cadence — sized for a bakery running two ovens
  // and five staff, so the demo lands near a realistic 20-30% net margin.
  ['Shop rent', 'Rent', () => 1200000, 'monthly'],
  ["Head baker's salary", 'Salaries', () => 500000, 'monthly'],
  ["Bakers' salaries (2)", 'Salaries', () => 600000, 'monthly'],
  ["Cashiers' salaries (2)", 'Salaries', () => 400000, 'monthly'],
  ['Cleaner & assistant', 'Salaries', () => 130000, 'monthly'],
  ['Night security guard', 'Salaries', () => 150000, 'monthly'],
  ['Electricity (REGIDESE)', 'Utilities', () => 450000, 'monthly'],
  ['Water bill (REGIDESO)', 'Utilities', () => 90000, 'monthly'],
  ['Gas & firewood for ovens', 'Utilities', () => 380000, 'monthly'],
  ['Packaging supplies', 'Packaging', () => 350000, 'monthly'],
  ['Mobile money & bank fees', 'Other', () => 200000, 'monthly'],
  ['Cleaning supplies', 'Other', () => 70000, 'monthly'],
  ['Hygiene permit', 'Permits', () => 60000, 'monthly'],
  ['Flour delivery transport', 'Transport', () => intBetween(6000, 22000), 'random'],
  ['Market transport', 'Transport', () => intBetween(3000, 12000), 'random'],
  ['Oven maintenance', 'Repairs', () => intBetween(30000, 120000), 'random'],
  ['Mixer repair', 'Repairs', () => intBetween(15000, 70000), 'random'],
  ['Spare parts & tools', 'Equipment', () => intBetween(5000, 30000), 'random'],
  ['Flyers & signage', 'Marketing', () => intBetween(10000, 45000), 'random'],
];

/* ------------------------------------------------------------------ *
 * Seeding
 * ------------------------------------------------------------------ */

/**
 * Delete every business row, in dependency order.
 *
 * Shared by `wipe` and by a forced re-seed so the two can never drift apart.
 * `sync_log` is cleared too: it records which offline writes have already been
 * applied, and leaving entries behind after a re-seed would make a reused
 * client_ref look like a replay of a row that no longer exists.
 */
export function clearAll() {
  for (const t of ['sale_items', 'sales', 'stock_moves', 'recipes', 'expenses', 'sessions',
    'customers', 'ingredients', 'suppliers', 'products', 'categories', 'users', 'sync_log']) {
    db.prepare(`DELETE FROM ${t}`).run();
  }
  db.prepare("DELETE FROM sqlite_sequence WHERE name <> 'settings'").run();
  db.prepare('DELETE FROM settings').run();
}

export function seedDemo({ ownerPassword = 'changeme', staffPassword = 'staff123', days = 60, force = false } = {}) {
  const timezone = tz();

  if (!force && num(db.prepare('SELECT COUNT(*) n FROM users').get().n) > 0) {
    return { skipped: true, reason: 'Database already has users. Pass force=true to re-seed.' };
  }

  return tx(() => {
    // A forced re-seed has to start from empty. It used to insert users on top
    // of the existing ones and die on UNIQUE(users.phone), which made the
    // documented "reload the demo data" step fail on any database that had
    // already been seeded once.
    if (force) clearAll();

    const stamp = localStamp(new Date(), timezone);
    const today = localDate(new Date(), timezone);

    /* --- users --- */
    const insUser = db.prepare(
      `INSERT INTO users (name, phone, role, pass_hash, pass_salt, must_change, active, created_at)
       VALUES (?,?,?,?,?,?,?,?)`);
    const mk = (name, phone, role, pw) => {
      const { salt, hash } = hashPassword(pw);
      return Number(insUser.run(name, phone, role, hash, salt, 1, 1, stamp).lastInsertRowid);
    };
    const ownerId = mk('Gide (Owner)', '079000000', 'owner', ownerPassword);
    const staffIds = [mk('Aline (Cashier)', '079111111', 'staff', staffPassword),
                      mk('Blaise (Cashier)', '079222222', 'staff', staffPassword)];
    const allUsers = [ownerId, ...staffIds];

    /* --- categories --- */
    const insCat = db.prepare('INSERT INTO categories (name, sort) VALUES (?,?)');
    const catId = {};
    CATEGORIES.forEach((c, i) => { catId[c] = Number(insCat.run(c, i).lastInsertRowid); });

    /* --- suppliers --- */
    const insSup = db.prepare('INSERT INTO suppliers (name, phone, notes, created_at) VALUES (?,?,?,?)');
    const supIds = SUPPLIERS.map(([n, p, note]) => Number(insSup.run(n, p, note, stamp).lastInsertRowid));

    /* --- ingredients --- */
    const insIng = db.prepare(
      `INSERT INTO ingredients (name, unit, stock, reorder_level, cost_per_unit, supplier_id, active, created_at, updated_at)
       VALUES (?,?,?,?,?,?,1,?,?)`);
    const ingId = {};
    for (const [name, unit, cost, target, reorder, si] of INGREDIENTS) {
      ingId[name] = Number(insIng.run(name, unit, 0, reorder, cost, supIds[si], stamp, stamp).lastInsertRowid);
    }

    /* --- products --- */
    const insProd = db.prepare(
      'INSERT INTO products (name, category_id, price, cost, active, created_at, updated_at) VALUES (?,?,?,NULL,1,?,?)');
    const prodId = {};
    const priceOf = {};
    for (const [name, cat, price] of PRODUCTS) {
      prodId[name] = Number(insProd.run(name, catId[cat], price, stamp, stamp).lastInsertRowid);
      priceOf[name] = price;
    }

    /* --- recipes --- */
    const insRec = db.prepare('INSERT OR IGNORE INTO recipes (product_id, ingredient_id, qty) VALUES (?,?,?)');
    for (const [prodName, lines] of Object.entries(RECIPES)) {
      for (const [ingName, qtyPer] of lines) {
        if (!(ingName in ingId)) throw new Error(`Recipe references missing ingredient: ${ingName}`);
        if (qtyPer <= 0) continue;
        insRec.run(prodId[prodName], ingId[ingName], qtyPer);
      }
    }

    /* --- customers --- */
    const insCust = db.prepare(
      'INSERT INTO customers (name, phone, address, notes, is_walk_in, created_at, updated_at) VALUES (?,?,?,?,?,?,?)');
    const custIds = CUSTOMERS.map(([n, p, a, note], i) =>
      Number(insCust.run(n, p, a, note, i === 0 ? 1 : 0, stamp, stamp).lastInsertRowid));
    const walkInId = custIds[0];

    // Recipe map in memory: { product_id -> [{ing_id, qty, cost}] }
    const recipeMap = {};
    const costOfIng = {};
    for (const [name, , cost, , , ] of INGREDIENTS) costOfIng[ingId[name]] = cost;
    for (const [prodName, lines] of Object.entries(RECIPES)) {
      recipeMap[prodId[prodName]] = lines
        .filter(([, q]) => q > 0)
        .map(([ingName, q]) => ({ ing_id: ingId[ingName], qty: q, cost: costOfIng[ingId[ingName]] ?? 0 }));
    }

    const costOfProduct = {};
    for (const [name] of PRODUCTS) costOfProduct[prodId[name]] = unitCostOf(prodId[name]);

    /* --- sales + ingredient usage --- */
    const insSale = db.prepare(
      `INSERT INTO sales (invoice_no, customer_id, user_id, subtotal, discount, total, paid, method, status, note, sale_at, created_at)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`);
    const insItem = db.prepare(
      `INSERT INTO sale_items (sale_id, product_id, name, qty, unit_price, line_total, unit_cost, line_cost)
       VALUES (?,?,?,?,?,?,?,?)`);
    const insMove = db.prepare(
      `INSERT INTO stock_moves (ingredient_id, kind, qty, unit_cost, total_cost, note, ref, user_id, created_at)
       VALUES (?,?,?,?,?,?,?,?,?)`);
    const insExp = db.prepare(
      'INSERT INTO expenses (title, category, amount, note, user_id, expense_at, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)');

    // Demand weights: staples dominate a bakery counter, cakes are occasional.
    const weights = {
      'Bread loaf (Umukate)': 12, 'Bread roll': 10, Chapati: 8, 'Mandazi (5 pcs)': 7,
      'Tea (chai)': 7, Donut: 5, Baguette: 5, Croissant: 4, 'Sausage roll': 5, Coffee: 4,
      Cupcake: 3, 'Meat pie': 3, 'Biscuit pack': 2, 'Cheese bun': 3, 'Cinnamon bun': 2,
      'Chocolate cake slice': 2, 'Juice bottle': 3, 'Whole wheat loaf': 2, 'Birthday cake 1kg': 0.3,
    };
    const pool = [];
    for (const [name, w] of Object.entries(weights)) {
      const times = Math.max(1, Math.round(w * 4));
      for (let i = 0; i < times; i++) pool.push(name);
    }

    const usageTotals = {}; // ingredient id -> total consumed
    let invoice = 1;
    let saleCount = 0;
    let moveCount = 0;

    for (let d = days; d >= 0; d--) {
      const date = addDays(today, -d);
      const dow = new Date(`${date}T12:00:00Z`).getUTCDay();
      const weekendBoost = dow === 0 || dow === 6 ? 1.4 : 1;
      // Trading grows over the two months — gives the trend chart a story.
      const growth = 0.75 + (0.25 * (days - d)) / days;
      const nSales = Math.max(8, Math.round(intBetween(34, 82) * weekendBoost * growth));

      for (let s = 0; s < nSales; s++) {
        const hour = intBetween(6, 19);
        const saleAt = `${date} ${String(hour).padStart(2, '0')}:${String(intBetween(0, 59)).padStart(2, '0')}:${String(intBetween(0, 59)).padStart(2, '0')}`;

        const nItems = chance(0.5) ? intBetween(1, 2) : intBetween(2, 4);
        const chosen = new Map();
        for (let i = 0; i < nItems; i++) {
          const name = pick(pool);
          const qty = name === 'Birthday cake 1kg' ? 1 : intBetween(1, name === 'Bread roll' ? 10 : 4);
          chosen.set(name, (chosen.get(name) || 0) + qty);
        }

        const lines = [...chosen.entries()].map(([name, qty]) => {
          const price = priceOf[name];
          const cost = costOfProduct[prodId[name]];
          return { pid: prodId[name], name, qty, price, cost,
            total: money(qty * price), lineCost: money(qty * cost) };
        });

        const subtotal = money(lines.reduce((a, l) => a + l.total, 0));
        const discount = chance(0.08) ? money(round(subtotal * between(0.02, 0.08))) : 0;
        const total = money(subtotal - discount);
        const method = chance(0.6) ? 'cash' : chance(0.6) ? 'mobile' : chance(0.78) ? 'card' : 'credit';
        const isCredit = method === 'credit';
        const paid = isCredit ? (chance(0.55) ? 0 : money(total * 0.5)) : total;
        const status = total <= 0 || paid >= total ? 'paid' : paid > 0 ? 'partial' : 'unpaid';

        const customerId = chance(0.2)
          ? custIds[intBetween(1, custIds.length - 1)]
          : (chance(0.35) ? walkInId : null);
        const userId = chance(0.42) ? ownerId : pick(staffIds);
        const invoiceNo = `INV-${String(invoice++).padStart(5, '0')}`;

        const saleId = Number(insSale.run(invoiceNo, customerId, userId, subtotal, discount, total, paid,
          method, status, isCredit ? 'Customer to settle on next visit' : null, saleAt, saleAt).lastInsertRowid);

        for (const l of lines) {
          insItem.run(saleId, l.pid, l.name, l.qty, l.price, l.total, l.cost, l.lineCost);
          // What the kitchen actually consumed to make this sale.
          for (const rc of recipeMap[l.pid] ?? []) {
            const used = round(rc.qty * l.qty, 3);
            if (!(used > 0)) continue;
            usageTotals[rc.ing_id] = round((usageTotals[rc.ing_id] ?? 0) + used, 3);
            insMove.run(rc.ing_id, 'usage', -used, rc.cost, money(used * rc.cost), null, invoiceNo, userId, saleAt);
            moveCount++;
          }
        }
        saleCount++;
      }

      /* --- expenses --- */
      const dayOfMonth = Number(date.slice(8, 10));
      for (const [title, cat, amountFn, cadence] of EXPENSE_TEMPLATES) {
        const due = cadence === 'monthly' ? dayOfMonth === 1 : chance(0.07);
        if (!due) continue;
        const at = `${date} ${String(intBetween(9, 17)).padStart(2, '0')}:15:00`;
        insExp.run(title, cat, money(amountFn()), null, ownerId, at, at, at);
      }
    }

    /* --- purchases that reconcile the ledger to the target stock --- */
    // For each ingredient: purchases = what was consumed + what should still
    // be on the shelf at the end. Spread over several deliveries.
    const targetStock = {};
    for (const [name, , , target] of INGREDIENTS) targetStock[ingId[name]] = target;

    const purchaseDates = [];
    for (let d = days; d >= 1; d -= intBetween(3, 6)) purchaseDates.push(addDays(today, -d));

    for (const [name, unit, cost, target, , si] of INGREDIENTS) {
      const id = ingId[name];
      const consumed = usageTotals[id] ?? 0;
      const needed = round(consumed + target, 3);
      if (needed <= 0) continue;

      const batches = Math.min(purchaseDates.length, Math.max(2, Math.round(consumed / 40)));
      let remaining = needed;
      for (let b = 0; b < batches; b++) {
        const isLast = b === batches - 1;
        const qty = isLast ? round(remaining, 3) : round(needed / batches * between(0.7, 1.3), 3);
        remaining = round(remaining - qty, 3);
        if (qty <= 0) continue;
        const at = `${purchaseDates[b % purchaseDates.length]} ${String(intBetween(7, 10)).padStart(2, '0')}:30:00`;
        insMove.run(id, 'purchase', qty, cost, money(qty * cost), `Delivery from ${SUPPLIERS[si][0]}`, null, ownerId, at);
        moveCount++;
      }
      // The ledger now sums to exactly the target.
      db.prepare('UPDATE ingredients SET stock = ? WHERE id = ?').run(target, id);
    }

    const setSetting = db.prepare(
      `INSERT INTO settings (key, value) VALUES (?, ?)
       ON CONFLICT(key) DO UPDATE SET value = excluded.value`);
    setSetting.run('seeded_at', now());
    setSetting.run('demo_seeded', '1');
    setSetting.run('next_invoice', String(invoice));

    return { skipped: false, users: allUsers.length, products: PRODUCTS.length,
      ingredients: INGREDIENTS.length, customers: CUSTOMERS.length,
      sales: saleCount, invoices: invoice - 1, stockMoves: moveCount, days };
  });
}

/** Minimal seed for a real deployment: one owner account, empty catalogue. */
export function seedOwner({ name = 'Owner', phone = '079000000', password = 'changeme' } = {}) {
  return tx(() => {
    const stamp = localStamp(new Date(), tz());
    const { salt, hash } = hashPassword(password);
    const id = Number(db.prepare(
      `INSERT INTO users (name, phone, role, pass_hash, pass_salt, must_change, active, created_at)
       VALUES (?,?, 'owner', ?,?,1,1,?)`).run(name, phone, hash, salt, stamp).lastInsertRowid);
    const insCat = db.prepare('INSERT OR IGNORE INTO categories (name, sort) VALUES (?,?)');
    CATEGORIES.forEach((c, i) => insCat.run(c, i));
    db.prepare(
      `INSERT INTO customers (name, notes, is_walk_in, created_at, updated_at)
       VALUES ('Walk-in customer', 'Default counter customer', 1, ?, ?)`).run(stamp, stamp);
    return { ownerId: id };
  });
}
