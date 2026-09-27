/**
 * Reporting engine: revenue, cost of goods sold, expenses, profit and the
 * breakdowns a bakery owner actually asks about (peak hours, best sellers,
 * stock valuation, staff performance, credit outstanding).
 *
 * All money figures come from `sale_items.line_cost`, which is snapshotted
 * at the moment of sale — so historic profit never moves when ingredient
 * prices are updated later.
 */
import { db, money, tz, decimals } from './db.js';
import { range, addDays, num, round, toCsv, str } from './util.js';
import { requireOwner } from './auth.js';
import { csv as csvResponse } from './router.js';

const ACTIVE = "s.status <> 'void'";

// Revenue earned by a single sale line, net of that sale's discount.
// A discount is stored once on the sale, but product and category reports group
// by line — so the discount is spread pro-rata across the lines of its sale.
// Without this, breakdowns are computed pre-discount (SUM(line_total)) while
// every headline figure is post-discount (SUM(total)), and the parts never add
// up to the whole. For any sale: SUM(line_total * total / subtotal) == total.
const NET_LINE =
  '(si.line_total * s.total / CASE WHEN s.subtotal > 0 THEN s.subtotal ELSE 1 END)';

/** 'YYYY-MM-DD' pair -> inclusive timestamp bounds matching how we store them. */
const span = (from, to) => [`${from} 00:00:00`, `${to} 23:59:59`];

const one = (sql, params = []) => db.prepare(sql).get(...params) ?? {};

function daysBetween(from, to) {
  const a = new Date(`${from}T00:00:00Z`).getTime();
  const b = new Date(`${to}T00:00:00Z`).getTime();
  return Math.max(1, Math.round((b - a) / 86400000) + 1);
}

/** The equally-sized period immediately before the given one. */
function previousRange(from, to) {
  const n = daysBetween(from, to);
  return { from: addDays(from, -n), to: addDays(from, -1) };
}

const pctChange = (now, before) => {
  const b = num(before);
  if (b === 0) return num(now) === 0 ? 0 : null; // null = "not comparable"
  return round(((num(now) - b) / Math.abs(b)) * 100, 1);
};

/* ------------------------------------------------------------------ *
 * Core figures for a date range
 * ------------------------------------------------------------------ */

export function coreFigures(from, to) {
  const [lo, hi] = span(from, to);

  const s = one(
    `SELECT COUNT(*) AS sales,
            COALESCE(SUM(s.total), 0)    AS revenue,
            COALESCE(SUM(s.discount), 0) AS discounts,
            COALESCE(SUM(s.paid), 0)     AS collected
       FROM sales s
      WHERE ${ACTIVE} AND s.sale_at BETWEEN ? AND ?`, [lo, hi]);

  const i = one(
    `SELECT COALESCE(SUM(si.qty), 0)       AS items,
            COALESCE(SUM(si.line_cost), 0) AS cogs
       FROM sale_items si JOIN sales s ON s.id = si.sale_id
      WHERE ${ACTIVE} AND s.sale_at BETWEEN ? AND ?`, [lo, hi]);

  const e = one(
    `SELECT COUNT(*) AS count, COALESCE(SUM(amount), 0) AS total
       FROM expenses WHERE expense_at BETWEEN ? AND ?`, [lo, hi]);

  const revenue = money(s.revenue);
  const cogs = money(i.cogs);
  const expenses = money(e.total);
  const grossProfit = money(revenue - cogs);
  const netProfit = money(grossProfit - expenses);

  return {
    from, to, days: daysBetween(from, to),
    sales: num(s.sales),
    items: round(i.items, 2),
    revenue,
    discounts: money(s.discounts),
    collected: money(s.collected),
    cogs,
    expenses,
    expenseCount: num(e.count),
    grossProfit,
    netProfit,
    grossMargin: revenue ? round((grossProfit / revenue) * 100, 1) : 0,
    netMargin: revenue ? round((netProfit / revenue) * 100, 1) : 0,
    averageSale: num(s.sales) ? money(revenue / num(s.sales)) : 0,
    revenuePerDay: money(revenue / daysBetween(from, to)),
  };
}

export function summary(query) {
  const { from, to } = range(query, tz());
  const current = coreFigures(from, to);
  const prevRange = previousRange(from, to);
  const previous = coreFigures(prevRange.from, prevRange.to);

  // Money owed by credit customers, across all time.
  const credit = one(
    `SELECT COUNT(*) AS count,
            COALESCE(SUM(s.total - s.paid), 0) AS outstanding
       FROM sales s WHERE s.status IN ('partial','unpaid')`);

  const inv = inventorySummary();

  return {
    ...current,
    previous: { range: prevRange, revenue: previous.revenue, netProfit: previous.netProfit,
                sales: previous.sales, expenses: previous.expenses },
    change: {
      revenue: pctChange(current.revenue, previous.revenue),
      netProfit: pctChange(current.netProfit, previous.netProfit),
      sales: pctChange(current.sales, previous.sales),
      expenses: pctChange(current.expenses, previous.expenses),
    },
    credit: { count: num(credit.count), outstanding: money(credit.outstanding) },
    inventory: { value: inv.value, lowStock: inv.lowStock.length, items: inv.items },
    topProducts: topProducts(query, 5),
    todaySoFar: todaySnapshot(),
  };
}

function todaySnapshot() {
  const t = range({}, tz());
  return coreFigures(t.from, t.to);
}

/* ------------------------------------------------------------------ *
 * Time series (charts)
 * ------------------------------------------------------------------ */

function dateSpine(from, to, bucket) {
  const out = [];
  if (bucket === 'month') {
    let cur = `${from.slice(0, 7)}`;
    const end = `${to.slice(0, 7)}`;
    while (cur <= end) {
      out.push(cur);
      const [y, m] = cur.split('-').map(Number);
      const next = new Date(Date.UTC(y, m, 1));
      cur = next.toISOString().slice(0, 7);
      if (out.length > 600) break;
    }
  } else {
    let cur = from;
    while (cur <= to) {
      out.push(cur);
      cur = addDays(cur, 1);
      if (out.length > 1000) break;
    }
  }
  return out;
}

export function timeseries(query) {
  const { from, to } = range(query, tz());
  const bucket = str(query.bucket) === 'month' ? 'month' : 'day';
  const len = bucket === 'month' ? 7 : 10;
  const [lo, hi] = span(from, to);

  const salesRows = db.prepare(
    `SELECT substr(s.sale_at, 1, ${len}) AS b,
            COUNT(*) AS sales,
            COALESCE(SUM(s.total), 0) AS revenue
       FROM sales s
      WHERE ${ACTIVE} AND s.sale_at BETWEEN ? AND ?
      GROUP BY b`).all(lo, hi);

  const cogsRows = db.prepare(
    `SELECT substr(s.sale_at, 1, ${len}) AS b,
            COALESCE(SUM(si.line_cost), 0) AS cogs,
            COALESCE(SUM(si.qty), 0) AS items
       FROM sale_items si JOIN sales s ON s.id = si.sale_id
      WHERE ${ACTIVE} AND s.sale_at BETWEEN ? AND ?
      GROUP BY b`).all(lo, hi);

  const expRows = db.prepare(
    `SELECT substr(expense_at, 1, ${len}) AS b,
            COALESCE(SUM(amount), 0) AS expenses
       FROM expenses WHERE expense_at BETWEEN ? AND ?
      GROUP BY b`).all(lo, hi);

  const index = (rows) => rows.reduce((a, r) => ((a[r.b] = r), a), {});
  const S = index(salesRows), C = index(cogsRows), E = index(expRows);

  const points = dateSpine(from, to, bucket).map((b) => {
    const revenue = money(S[b]?.revenue ?? 0);
    const cogs = money(C[b]?.cogs ?? 0);
    const expenses = money(E[b]?.expenses ?? 0);
    return {
      bucket: b,
      sales: num(S[b]?.sales ?? 0),
      items: round(C[b]?.items ?? 0, 2),
      revenue,
      cogs,
      expenses,
      grossProfit: money(revenue - cogs),
      netProfit: money(revenue - cogs - expenses),
    };
  });

  return { from, to, bucket, points };
}

/** When the shop is busy — tells the owner when to have bread ready. */
export function byHour(query) {
  const { from, to } = range(query, tz());
  const [lo, hi] = span(from, to);
  const rows = db.prepare(
    `SELECT CAST(substr(s.sale_at, 12, 2) AS INTEGER) AS hour,
            COUNT(*) AS sales,
            COALESCE(SUM(s.total), 0) AS revenue
       FROM sales s
      WHERE ${ACTIVE} AND s.sale_at BETWEEN ? AND ?
      GROUP BY hour`).all(lo, hi);

  const out = Array.from({ length: 24 }, (_, h) => ({ hour: h, sales: 0, revenue: 0 }));
  for (const r of rows) {
    if (r.hour >= 0 && r.hour < 24) {
      out[r.hour].sales = num(r.sales);
      out[r.hour].revenue = money(r.revenue);
    }
  }
  const peak = out.reduce((best, r) => (r.revenue > best.revenue ? r : best), out[0]);
  return { hours: out.filter((r) => r.sales > 0), peak };
}

/* ------------------------------------------------------------------ *
 * Breakdowns
 * ------------------------------------------------------------------ */

export function topProducts(query, limit = 10) {
  const { from, to } = range(query, tz());
  const [lo, hi] = span(from, to);
  const rows = db.prepare(
    `SELECT si.product_id, si.name,
            COALESCE(c.name, 'Uncategorised') AS category,
            SUM(si.qty) AS qty,
            SUM(${NET_LINE}) AS revenue,
            SUM(si.line_cost) AS cogs
       FROM sale_items si
       JOIN sales s ON s.id = si.sale_id
       LEFT JOIN products p ON p.id = si.product_id
       LEFT JOIN categories c ON c.id = p.category_id
      WHERE ${ACTIVE} AND s.sale_at BETWEEN ? AND ?
      GROUP BY si.name
      ORDER BY revenue DESC
      LIMIT ?`).all(lo, hi, Math.max(1, Math.min(50, num(limit, 10)) || 10));

  const totalRevenue = rows.reduce((a, r) => a + num(r.revenue), 0);
  return rows.map((r) => {
    const revenue = money(r.revenue), cogs = money(r.cogs);
    return {
      product_id: r.product_id,
      name: r.name,
      category: r.category,
      qty: round(r.qty, 2),
      revenue,
      cogs,
      profit: money(revenue - cogs),
      margin: revenue ? round(((revenue - cogs) / revenue) * 100, 1) : 0,
      share: totalRevenue ? round((revenue / totalRevenue) * 100, 1) : 0,
    };
  });
}

export function categoryMix(query) {
  const { from, to } = range(query, tz());
  const [lo, hi] = span(from, to);
  const rows = db.prepare(
    `SELECT COALESCE(c.name, 'Uncategorised') AS category,
            SUM(${NET_LINE}) AS revenue,
            SUM(si.qty) AS qty
       FROM sale_items si
       JOIN sales s ON s.id = si.sale_id
       LEFT JOIN products p ON p.id = si.product_id
       LEFT JOIN categories c ON c.id = p.category_id
      WHERE ${ACTIVE} AND s.sale_at BETWEEN ? AND ?
      GROUP BY c.name ORDER BY revenue DESC`).all(lo, hi);
  return rows.map((r) => ({ category: r.category, revenue: money(r.revenue), qty: round(r.qty, 2) }));
}

export function paymentMix(query) {
  const { from, to } = range(query, tz());
  const [lo, hi] = span(from, to);
  const rows = db.prepare(
    `SELECT s.method, COUNT(*) AS sales, COALESCE(SUM(s.paid), 0) AS collected
       FROM sales s WHERE ${ACTIVE} AND s.sale_at BETWEEN ? AND ?
      GROUP BY s.method ORDER BY collected DESC`).all(lo, hi);
  const total = rows.reduce((a, r) => a + num(r.collected), 0);
  return rows.map((r) => ({
    method: r.method, sales: num(r.sales), collected: money(r.collected),
    share: total ? round((num(r.collected) / total) * 100, 1) : 0,
  }));
}

export function staffPerformance(query) {
  const { from, to } = range(query, tz());
  const [lo, hi] = span(from, to);
  const rows = db.prepare(
    `SELECT u.id, u.name,
            COUNT(*) AS sales,
            COALESCE(SUM(s.total), 0) AS revenue,
            COALESCE(SUM(s.discount), 0) AS discounts
       FROM sales s LEFT JOIN users u ON u.id = s.user_id
      WHERE ${ACTIVE} AND s.sale_at BETWEEN ? AND ?
      GROUP BY u.id ORDER BY revenue DESC`).all(lo, hi);
  return rows.map((r) => ({
    user_id: r.id,
    name: r.name ?? 'Unknown',
    sales: num(r.sales),
    revenue: money(r.revenue),
    discounts: money(r.discounts),
    averageSale: num(r.sales) ? money(num(r.revenue) / num(r.sales)) : 0,
  }));
}

export function topCustomers(query, limit = 10) {
  const { from, to } = range(query, tz());
  const [lo, hi] = span(from, to);
  const rows = db.prepare(
    `SELECT c.id, c.name, c.phone,
            COUNT(s.id) AS orders,
            COALESCE(SUM(s.total), 0) AS revenue,
            COALESCE(SUM(s.total - s.paid), 0) AS owed,
            MAX(s.sale_at) AS last_visit
       FROM sales s JOIN customers c ON c.id = s.customer_id
      WHERE ${ACTIVE} AND c.is_walk_in = 0 AND s.sale_at BETWEEN ? AND ?
      GROUP BY c.id ORDER BY revenue DESC
      LIMIT ?`).all(lo, hi, Math.max(1, Math.min(50, num(limit, 10)) || 10));
  return rows.map((r) => ({
    id: r.id, name: r.name, phone: r.phone, orders: num(r.orders),
    revenue: money(r.revenue), owed: money(r.owed), last_visit: r.last_visit,
  }));
}

export function expenseBreakdown(query) {
  const { from, to } = range(query, tz());
  const [lo, hi] = span(from, to);
  const rows = db.prepare(
    `SELECT category, COUNT(*) AS count, SUM(amount) AS total
       FROM expenses WHERE expense_at BETWEEN ? AND ?
      GROUP BY category ORDER BY total DESC`).all(lo, hi);
  const sum = rows.reduce((a, r) => a + num(r.total), 0);
  return rows.map((r) => ({
    category: r.category, count: num(r.count), total: money(r.total),
    share: sum ? round((num(r.total) / sum) * 100, 1) : 0,
  }));
}

/* ------------------------------------------------------------------ *
 * Inventory
 * ------------------------------------------------------------------ */

export function inventorySummary() {
  const rows = db.prepare(
    `SELECT i.*, s.name AS supplier
       FROM ingredients i LEFT JOIN suppliers s ON s.id = i.supplier_id
      WHERE i.active = 1 ORDER BY i.name`).all();

  let value = 0;
  const lowStock = [];
  const items = rows.map((r) => {
    const stock = round(r.stock, 3);
    const worth = money(stock * num(r.cost_per_unit));
    value += worth;
    const low = num(r.reorder_level) > 0 && stock <= num(r.reorder_level);
    if (low) lowStock.push({ id: r.id, name: r.name, unit: r.unit, stock, reorder_level: num(r.reorder_level), supplier: r.supplier });
    return {
      id: r.id, name: r.name, unit: r.unit, stock,
      reorder_level: num(r.reorder_level), cost_per_unit: money(r.cost_per_unit),
      value: worth, supplier: r.supplier, supplier_id: r.supplier_id,
      low,
      coverage: num(r.reorder_level) > 0 ? round(stock / num(r.reorder_level), 2) : null,
    };
  });

  return { items, value: money(value), lowStock, count: items.length };
}

/** Which ingredients are consumed fastest, based on real sales. */
export function ingredientUsage(query, limit = 12) {
  const { from, to } = range(query, tz());
  const [lo, hi] = span(from, to);
  const rows = db.prepare(
    `SELECT i.id, i.name, i.unit, SUM(-m.qty) AS used, SUM(m.total_cost) AS cost
       FROM stock_moves m JOIN ingredients i ON i.id = m.ingredient_id
      WHERE m.kind IN ('usage','waste') AND m.created_at BETWEEN ? AND ?
      GROUP BY i.id ORDER BY cost DESC LIMIT ?`)
    .all(lo, hi, Math.max(1, Math.min(50, num(limit, 12)) || 12));
  return rows.map((r) => ({ id: r.id, name: r.name, unit: r.unit, used: round(r.used, 3), cost: money(r.cost) }));
}

/* ------------------------------------------------------------------ *
 * Profit & loss statement
 * ------------------------------------------------------------------ */

export function profitAndLoss(query) {
  const { from, to } = range(query, tz());
  const c = coreFigures(from, to);
  const exp = expenseBreakdown(query);
  const top = topProducts(query, 8);

  return {
    range: { from, to, days: c.days },
    statement: {
      // grossRevenue - discounts === revenue, so the statement foots top to bottom.
      grossRevenue: money(c.revenue + c.discounts),
      discounts: c.discounts,
      revenue: c.revenue,
      netRevenue: c.revenue,
      cogs: c.cogs,
      grossProfit: c.grossProfit,
      grossMargin: c.grossMargin,
      expenses: exp,
      totalExpenses: c.expenses,
      netProfit: c.netProfit,
      netMargin: c.netMargin,
    },
    bestSellers: top,
    perDay: {
      revenue: c.revenuePerDay,
      profit: money(c.netProfit / c.days),
      sales: round(c.sales / c.days, 1),
    },
  };
}

/* ------------------------------------------------------------------ *
 * CSV exports
 * ------------------------------------------------------------------ */

function exportRows(query) {
  const type = str(query.type) || 'sales';
  const { from, to } = range(query, tz());
  const [lo, hi] = span(from, to);

  if (type === 'expenses') {
    const rows = db.prepare(
      `SELECT e.expense_at AS date, e.title, e.category, e.amount, e.note, u.name AS recorded_by
         FROM expenses e LEFT JOIN users u ON u.id = e.user_id
        WHERE e.expense_at BETWEEN ? AND ? ORDER BY e.expense_at DESC`).all(lo, hi);
    return { name: `expenses-${from}-to-${to}.csv`, rows, columns: [
      { key: 'date', label: 'Date' }, { key: 'title', label: 'Title' },
      { key: 'category', label: 'Category' }, { key: 'amount', label: 'Amount' },
      { key: 'note', label: 'Note' }, { key: 'recorded_by', label: 'Recorded by' }] };
  }

  if (type === 'products') {
    const rows = db.prepare(
      `SELECT p.name, c.name AS category, p.price,
              COALESCE(rc.cost, p.cost, 0) AS unit_cost,
              (p.price - COALESCE(rc.cost, p.cost, 0)) AS margin_per_unit,
              CASE WHEN p.active = 1 THEN 'yes' ELSE 'no' END AS active
         FROM products p
         LEFT JOIN categories c ON c.id = p.category_id
         LEFT JOIN (SELECT r.product_id, SUM(r.qty * i.cost_per_unit) AS cost
                      FROM recipes r JOIN ingredients i ON i.id = r.ingredient_id
                     GROUP BY r.product_id) rc ON rc.product_id = p.id
        ORDER BY c.sort, p.name`).all();
    return { name: 'products-costing.csv', rows, columns: [
      { key: 'name', label: 'Product' }, { key: 'category', label: 'Category' },
      { key: 'price', label: 'Selling price' }, { key: 'unit_cost', label: 'Unit cost',
        value: (r) => money(r.unit_cost) },
      { key: 'margin_per_unit', label: 'Margin per unit', value: (r) => money(r.margin_per_unit) },
      { key: 'active', label: 'Active' }] };
  }

  if (type === 'inventory') {
    const inv = inventorySummary();
    return { name: 'inventory-valuation.csv', rows: inv.items, columns: [
      { key: 'name', label: 'Ingredient' }, { key: 'stock', label: 'In stock' },
      { key: 'unit', label: 'Unit' }, { key: 'cost_per_unit', label: 'Cost per unit' },
      { key: 'value', label: 'Stock value' }, { key: 'reorder_level', label: 'Reorder at' },
      { key: 'supplier', label: 'Supplier' },
      { key: 'low', label: 'Low stock', value: (r) => (r.low ? 'yes' : 'no') }] };
  }

  // default: itemised sales
  const rows = db.prepare(
    `SELECT s.invoice_no, s.sale_at, s.total, s.discount, s.paid, s.method, s.status,
            u.name AS sold_by, c.name AS customer,
            si.name AS item, si.qty, si.unit_price, si.line_total, si.line_cost
       FROM sales s
       JOIN sale_items si ON si.sale_id = s.id
       LEFT JOIN users u ON u.id = s.user_id
       LEFT JOIN customers c ON c.id = s.customer_id
      WHERE ${ACTIVE} AND s.sale_at BETWEEN ? AND ?
      ORDER BY s.sale_at DESC, s.id DESC`).all(lo, hi);
  return { name: `sales-${from}-to-${to}.csv`, rows, columns: [
    { key: 'invoice_no', label: 'Invoice' }, { key: 'sale_at', label: 'Date & time' },
    { key: 'item', label: 'Item' }, { key: 'qty', label: 'Qty' },
    { key: 'unit_price', label: 'Unit price' }, { key: 'line_total', label: 'Line total' },
    { key: 'line_cost', label: 'Line cost' },
    { key: 'discount', label: 'Discount' }, { key: 'total', label: 'Sale total' },
    { key: 'paid', label: 'Paid' }, { key: 'method', label: 'Method' },
    { key: 'status', label: 'Status' }, { key: 'sold_by', label: 'Sold by' },
    { key: 'customer', label: 'Customer' }] };
}

/* ------------------------------------------------------------------ *
 * Routes
 * ------------------------------------------------------------------ */

export function registerReportRoutes(r) {
  // Reports show money and profit, so they are owner-only.
  r.get('/api/reports/summary', (ctx) => { requireOwner(ctx); return summary(ctx.query); }, { owner: true });
  r.get('/api/reports/timeseries', (ctx) => { requireOwner(ctx); return timeseries(ctx.query); }, { owner: true });
  r.get('/api/reports/hours', (ctx) => { requireOwner(ctx); return byHour(ctx.query); }, { owner: true });
  r.get('/api/reports/top-products', (ctx) => { requireOwner(ctx); return topProducts(ctx.query, num(ctx.query.limit, 10)); }, { owner: true });
  r.get('/api/reports/categories', (ctx) => { requireOwner(ctx); return categoryMix(ctx.query); }, { owner: true });
  r.get('/api/reports/payments', (ctx) => { requireOwner(ctx); return paymentMix(ctx.query); }, { owner: true });
  r.get('/api/reports/staff', (ctx) => { requireOwner(ctx); return staffPerformance(ctx.query); }, { owner: true });
  r.get('/api/reports/customers', (ctx) => { requireOwner(ctx); return topCustomers(ctx.query, num(ctx.query.limit, 10)); }, { owner: true });
  r.get('/api/reports/expenses', (ctx) => { requireOwner(ctx); return expenseBreakdown(ctx.query); }, { owner: true });
  r.get('/api/reports/inventory', (ctx) => { requireOwner(ctx); return inventorySummary(); }, { owner: true });
  r.get('/api/reports/ingredient-usage', (ctx) => { requireOwner(ctx); return ingredientUsage(ctx.query, num(ctx.query.limit, 12)); }, { owner: true });
  r.get('/api/reports/profit-loss', (ctx) => { requireOwner(ctx); return profitAndLoss(ctx.query); }, { owner: true });

  r.get('/api/reports/export', (ctx) => {
    requireOwner(ctx);
    const { name, rows, columns } = exportRows(ctx.query);
    return csvResponse(toCsv(rows, columns), name);
  }, { owner: true });
}

export { decimals };
