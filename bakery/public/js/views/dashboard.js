/**
 * Dashboard — what happened today, what needs attention, and a fast path
 * into the till. Staff see their own numbers; owners see profit too.
 */
import { api } from '../api.js';
import { state, isOwner, loadData } from '../store.js';
import { icon, $, on, emptyState, toastError, skeletons } from '../ui.js';
import { money, moneyCompact, num, qty, esc, shortDate, relTime, todayStr, shiftDays, deltaPct } from '../format.js';
import { lineChart, hbars, sparkline } from '../charts.js';
import { navigate } from '../router.js';

const greeting = () => {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
};

const longToday = () => new Date().toLocaleDateString(undefined,
  { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });

export async function render(host) {
  const cleanups = [];
  const today = state.serverToday || todayStr();
  const owner = isOwner();

  host.innerHTML = `
    <div class="page-head">
      <div class="grow">
        <h1>${esc(greeting())}, ${esc((state.user?.name || 'there').split(' ')[0])}</h1>
        <div class="small muted">${esc(longToday())}</div>
      </div>
      <div class="page-actions">
        <button class="btn btn-primary" data-new-sale>${icon('cart', { size: 17 })} New sale</button>
      </div>
    </div>
    <div class="grid grid-4" id="dash-kpis">
      ${Array.from({ length: owner ? 4 : 3 }, () => `
        <div class="kpi">
          <div class="skeleton" style="height:11px;width:58%"></div>
          <div class="skeleton" style="height:25px;margin-top:9px;width:78%"></div>
          <div class="skeleton" style="height:10px;margin-top:9px;width:45%"></div>
        </div>`).join('')}
    </div>
    <div class="stack" id="dash-body" style="margin-top:12px">
      <div class="card"><div class="card-head"><h3>Loading…</h3></div>${skeletons(3)}</div>
    </div>`;

  on(host, 'click', '[data-new-sale]', () => navigate('/sell'));

  const body = $('#dash-body', host);
  const kpis = $('#dash-kpis', host);

  try {
    if (owner) cleanups.push(...await renderOwner(kpis, body, today));
    else cleanups.push(...await renderStaff(kpis, body, today));
  } catch (err) {
    kpis.innerHTML = '';
    body.innerHTML = `<div class="card"><div class="empty">
      ${icon('alert', { size: 40, stroke: 1.5 })}<h4>Could not load your dashboard</h4>
      <p>${esc(err?.message || '')}</p></div></div>`;
    toastError(err);
  }

  return () => cleanups.forEach((fn) => { try { fn?.(); } catch { /* ignore */ } });
}

/* ------------------------------------------------------------------ *
 * Owner dashboard
 * ------------------------------------------------------------------ */

async function renderOwner(kpis, body, today) {
  const monthStart = `${today.slice(0, 7)}-01`;
  const from14 = shiftDays(today, -13);

  const [summary, series] = await Promise.all([
    api.report('summary', { from: monthStart, to: today }),
    api.report('timeseries', { from: from14, to: today, bucket: 'day' }),
  ]);

  const d = summary.todaySoFar;

  kpis.innerHTML = `
    ${kpi({
      label: 'Today’s takings', value: money(d.revenue), accent: true, icon: 'cash',
      sub: `${num(d.sales)} sale${d.sales === 1 ? '' : 's'} · avg ${money(d.averageSale)}`,
      spark: sparkline(series.points.map((p) => p.revenue), { color: '#E8A33D' }),
    })}
    ${kpi({
      label: 'Profit today', value: money(d.netProfit), icon: 'trending',
      tone: d.netProfit >= 0 ? 'ok' : 'bad',
      sub: `Gross margin ${d.grossMargin}% · expenses ${money(d.expenses)}`,
    })}
    ${kpi({
      label: 'Revenue this month', value: money(summary.revenue), icon: 'calendar',
      sub: `${delta(summary.change.revenue)} vs previous ${summary.days} days`,
    })}
    ${kpi({
      label: 'Net profit this month', value: money(summary.netProfit), icon: 'chart',
      tone: summary.netProfit >= 0 ? 'ok' : 'bad',
      sub: `${summary.netMargin}% margin · ${money(summary.revenuePerDay)}/day`,
    })}`;

  const low = summary.inventory?.lowStock ?? 0;
  const owed = summary.credit?.outstanding ?? 0;
  const alerts = [];
  if (low > 0) alerts.push({ tone: 'warn', icon: 'alert', title: `${low} ingredient${low === 1 ? '' : 's'} at or below reorder level`, action: 'Check stock', href: '/stock?filter=low' });
  if (owed > 0) alerts.push({ tone: 'info', icon: 'credit', title: `${money(owed)} owed by ${summary.credit.count} credit customer${summary.credit.count === 1 ? '' : 's'}`, action: 'Chase up', href: '/sales?status=unpaid' });
  if (state.user?.must_change) alerts.push({ tone: 'bad', icon: 'lock', title: 'Your password is still the temporary one', action: 'Change it', href: '/settings?tab=password' });

  body.innerHTML = `
    ${alerts.length ? `<div class="stack" style="gap:8px">${alerts.map(alertRow).join('')}</div>` : ''}

    <div class="card">
      <div class="card-head">
        <h3 class="grow">Last 14 days</h3>
        <div class="legend">
          <span><i style="background:#B4531F"></i>Revenue</span>
          <span><i style="background:#2F7D4F"></i>Net profit</span>
        </div>
      </div>
      <div class="card-body"><div class="chart" id="chart-revenue" style="min-height:210px"></div></div>
    </div>

    <div class="grid grid-2">
      <div class="card">
        <div class="card-head"><h3 class="grow">Best sellers this month</h3>
          <a class="btn btn-ghost btn-sm" href="#/reports">Reports ${icon('chevronRight', { size: 15 })}</a></div>
        <div class="card-body" id="top-products"></div>
      </div>
      <div class="card">
        <div class="card-head"><h3 class="grow">Stock to reorder</h3>
          <a class="btn btn-ghost btn-sm" href="#/stock">All stock ${icon('chevronRight', { size: 15 })}</a></div>
        <div class="card-body tight" id="low-stock"></div>
      </div>
    </div>

    <div class="card">
      <div class="card-head"><h3 class="grow">Latest sales</h3>
        <a class="btn btn-ghost btn-sm" href="#/sales">View all ${icon('chevronRight', { size: 15 })}</a></div>
      <div class="card-body tight" id="recent-sales">${skeletons(3)}</div>
    </div>`;

  const top = summary.topProducts ?? [];
  $('#top-products', body).innerHTML = top.length
    ? hbars(top.slice(0, 6).map((p) => ({ label: p.name, value: p.revenue, margin: p.margin })),
      { valueFormat: (v) => moneyCompact(v, true), subFormat: (it) => `${it.margin}%` })
    : emptyState({ icon: 'chart', title: 'No sales this month', message: 'Your best sellers will appear here.' });

  renderLowStock($('#low-stock', body), summary.inventory);
  await renderRecentSales($('#recent-sales', body), today);

  return [lineChart($('#chart-revenue', body), {
    labels: series.points.map((p) => shortDate(p.bucket)),
    series: [
      { name: 'Revenue', values: series.points.map((p) => p.revenue), color: '#B4531F', area: true },
      { name: 'Net profit', values: series.points.map((p) => p.netProfit), color: '#2F7D4F', area: false },
    ],
    kind: 'money', height: 210, formatTip: (v) => money(v),
  })];
}

/* ------------------------------------------------------------------ *
 * Staff dashboard — own till performance, no cost data
 * ------------------------------------------------------------------ */

async function renderStaff(kpis, body, today) {
  const [mine, boot] = await Promise.all([api.get('/api/my-summary'), loadData()]);

  const lowList = (boot.ingredients || []).filter((i) => Number(i.reorder_level) > 0
    && Number(i.stock) <= Number(i.reorder_level));

  kpis.innerHTML = `
    ${kpi({ label: 'My takings today', value: money(mine.today.revenue), accent: true, icon: 'cash',
      sub: `${num(mine.today.sales)} sale${mine.today.sales === 1 ? '' : 's'} · avg ${money(mine.today.averageSale)}`,
      spark: sparkline(mine.series.map((p) => p.revenue), { color: '#E8A33D' }) })}
    ${kpi({ label: 'Items sold today', value: num(mine.today.items), icon: 'box',
      sub: mine.today.sales ? `avg ${num(mine.today.items / mine.today.sales, 1)} items per sale` : 'No sales yet' })}
    ${kpi({ label: 'My month total', value: money(mine.month.revenue), icon: 'calendar',
      sub: `${num(mine.month.sales)} sales · ${num(mine.month.items)} items` })}`;

  body.innerHTML = `
    <div class="grid grid-3">
      <button class="tile" data-go="/sell" style="min-height:96px;align-items:flex-start;gap:7px">
        <span class="thumb">${icon('cart', { size: 19 })}</span>
        <span class="tile-name" style="font-size:14.5px">Record a sale</span>
        <span class="tile-meta">Open the till</span>
      </button>
      <button class="tile" data-go="/expenses" style="min-height:96px;align-items:flex-start;gap:7px">
        <span class="thumb gold">${icon('wallet', { size: 19 })}</span>
        <span class="tile-name" style="font-size:14.5px">Add an expense</span>
        <span class="tile-meta">Petty cash, transport</span>
      </button>
      <button class="tile" data-go="/stock" style="min-height:96px;align-items:flex-start;gap:7px">
        <span class="thumb ${lowList.length ? 'red' : 'green'}">${icon('box', { size: 19 })}</span>
        <span class="tile-name" style="font-size:14.5px">Stock</span>
        <span class="tile-meta">${lowList.length ? `${lowList.length} low — tell the owner` : 'All levels healthy'}</span>
      </button>
    </div>

    <div class="card">
      <div class="card-head"><h3 class="grow">My sales, last 14 days</h3></div>
      <div class="card-body"><div class="chart" id="chart-mine" style="min-height:190px"></div></div>
    </div>

    ${lowList.length ? `
      <div class="card">
        <div class="card-head"><h3 class="grow">Running low</h3>
          <span class="badge warn">${lowList.length}</span></div>
        <div class="card-body tight">
          <div class="list">${lowList.slice(0, 5).map((i) => `
            <div class="list-item">
              <span class="thumb gold">${icon('alert', { size: 18 })}</span>
              <span class="list-main"><span class="list-title">${esc(i.name)}</span>
                <span class="list-sub">Reorder at ${esc(qty(i.reorder_level))} ${esc(i.unit)}</span></span>
              <span class="list-side"><span class="list-amount">${esc(qty(i.stock))} ${esc(i.unit)}</span></span>
            </div>`).join('')}</div>
        </div>
      </div>` : ''}

    <div class="card">
      <div class="card-head"><h3 class="grow">My latest sales</h3>
        <a class="btn btn-ghost btn-sm" href="#/sales">View all ${icon('chevronRight', { size: 15 })}</a></div>
      <div class="card-body tight" id="recent-sales">${skeletons(3)}</div>
    </div>`;

  on(body, 'click', '[data-go]', (_e, el) => navigate(el.dataset.go));
  await renderRecentSales($('#recent-sales', body), today);

  return [lineChart($('#chart-mine', body), {
    labels: mine.series.map((p) => shortDate(p.bucket)),
    series: [{ name: 'Sales', values: mine.series.map((p) => p.sales), color: '#B4531F', area: true }],
    kind: 'number', height: 190, formatTip: (v) => `${num(v)} sale${v === 1 ? '' : 's'}`,
  })];
}

/* ------------------------------------------------------------------ *
 * Shared pieces
 * ------------------------------------------------------------------ */

function kpi({ label, value, sub, icon: ic, accent, tone, spark }) {
  const color = tone === 'bad' ? 'var(--bad)' : tone === 'ok' ? 'var(--ok)' : '';
  return `
    <div class="kpi${accent ? ' accent' : ''}">
      ${ic ? `<span class="kpi-icon">${icon(ic, { size: 34, stroke: 1.6 })}</span>` : ''}
      <div class="kpi-label">${esc(label)}</div>
      <div class="kpi-value"${color ? ` style="color:${color}"` : ''}>${esc(value)}</div>
      <div class="row between" style="gap:8px;align-items:flex-end">
        <div class="kpi-sub grow">${sub || ''}</div>
        ${spark ? `<span style="opacity:.9;flex:0 0 auto">${spark}</span>` : ''}
      </div>
    </div>`;
}

const delta = (v) => {
  if (v === null || v === undefined) return '<span class="muted tiny">no prior data</span>';
  const cls = v > 0 ? 'up' : v < 0 ? 'down' : 'flat';
  return `<span class="delta ${cls}">${icon(v >= 0 ? 'arrowUp' : 'arrowDown', { size: 11, stroke: 2.6 })}${esc(deltaPct(v))}</span>`;
};

const alertRow = (a) => `
  <div class="pill-note ${a.tone}">
    ${icon(a.icon, { size: 17 })}
    <div class="grow"><strong>${esc(a.title)}</strong></div>
    <a class="btn btn-sm btn-ghost" href="#${a.href}">${esc(a.action)}</a>
  </div>`;

/** Shared by the dashboard and the sales list. */
export function salesListHtml(sales) {
  const methodIcon = { mobile: 'mobile', card: 'card', credit: 'credit', cash: 'cash' };
  return `<div class="list">${sales.map((s) => `
    <div class="list-item clickable" data-sale="${s.id}" role="button" tabindex="0">
      <span class="thumb ${s.status === 'void' ? 'red' : s.status === 'paid' ? 'green' : 'gold'}">
        ${icon(s.status === 'void' ? 'x' : (methodIcon[s.method] || 'cash'), { size: 18 })}
      </span>
      <span class="list-main">
        <span class="list-title">${esc(s.invoice_no)}${s.customer && !/^walk-in/i.test(s.customer) ? ` · ${esc(s.customer)}` : ''}</span>
        <span class="list-sub">${num(s.qty ?? 0, 0)} items · ${esc(relTime(s.sale_at))}${s.sold_by ? ` · ${esc(s.sold_by.split(' ')[0])}` : ''}</span>
      </span>
      <span class="list-side">
        <span class="list-amount"${s.status === 'void' ? ' style="text-decoration:line-through;opacity:.55"' : ''}>${esc(money(s.total))}</span>
        ${Number(s.due) > 0 ? `<span class="badge warn" style="margin-top:3px">owes ${esc(money(s.due))}</span>` : ''}
        ${s.status === 'void' ? '<span class="badge bad" style="margin-top:3px">voided</span>' : ''}
      </span>
    </div>`).join('')}</div>`;
}

function renderLowStock(hostEl, inventory) {
  if (!hostEl) return;
  const low = (inventory?.lowStock || []).slice(0, 6);
  hostEl.innerHTML = low.length
    ? `<div class="list">${low.map((i) => `
        <div class="list-item">
          <span class="thumb ${Number(i.stock) <= 0 ? 'red' : 'gold'}">${icon('alert', { size: 18 })}</span>
          <span class="list-main">
            <span class="list-title">${esc(i.name)}</span>
            <span class="list-sub">${i.supplier ? `Supplier: ${esc(i.supplier)}` : 'No supplier set'}</span>
          </span>
          <span class="list-side">
            <span class="list-amount">${esc(qty(i.stock))} ${esc(i.unit)}</span>
            <span class="badge warn">reorder at ${esc(qty(i.reorder_level))}</span>
          </span>
        </div>`).join('')}</div>`
    : emptyState({ icon: 'check', title: 'Stock looks healthy', message: 'Nothing is at or below its reorder level.' });
}

async function renderRecentSales(hostEl, today) {
  if (!hostEl) return;
  try {
    const { sales } = await api.sales({ from: today, to: today, limit: 6 });
    hostEl.innerHTML = sales.length
      ? salesListHtml(sales)
      : emptyState({ icon: 'cart', title: 'No sales today yet', message: 'The till is waiting.' });
    on(hostEl, 'click', '[data-sale]', async (_e, el) => {
      const { showReceipt } = await import('./sales.js');
      showReceipt(el.dataset.sale);
    });
  } catch (err) {
    hostEl.innerHTML = emptyState({ icon: 'alert', title: 'Could not load sales', message: err.message });
  }
}
