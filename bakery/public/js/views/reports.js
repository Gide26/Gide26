/**
 * Reports (owner only). Everything is derived from real recorded data:
 * a profit & loss statement, trend and peak-hour charts, best sellers,
 * payment mix, expense split, staff performance and CSV exports.
 */
import { api } from '../api.js';
import { icon, $, on, toast, emptyState, bindRangePicker, defaultRange } from '../ui.js';
import { money, moneyCompact, num, qty, esc, dateOnly, shortDate, monthLabel, pct } from '../format.js';
import { lineChart, barChart, donut, hbars } from '../charts.js';

export async function render(host, ctx) {
  const cleanups = [];
  const range = { ...defaultRange() };
  let bucket = ctx.params.get('bucket') === 'month' ? 'month' : 'day';

  host.innerHTML = `
    <div class="page-head">
      <div class="grow">
        <h1>Reports</h1>
        <div class="small muted">What you earned, what it cost, and what is left.</div>
      </div>
      <div class="page-actions">
        <div class="segmented" id="r-export">
          <button data-export="sales">Sales CSV</button>
          <button data-export="expenses">Expenses CSV</button>
          <button data-export="inventory">Stock CSV</button>
        </div>
      </div>
    </div>

    <div class="card" style="margin-bottom:12px">
      <div class="card-body">
        <div class="row between wrap" style="gap:10px;margin-bottom:11px">
          <div id="r-range" class="grow" style="min-width:260px"></div>
        </div>
      </div>
    </div>

    <div id="r-body"><div class="loading-page"><div class="spinner"></div>
      <div class="small muted">Crunching the numbers…</div></div></div>`;

  const body = $('#r-body', host);
  cleanups.push(bindRangePicker($('#r-range', host), range, load));
  cleanups.push(on(host, 'click', '[data-export]', (_e, el) => {
    const url = api.exportUrl(el.dataset.export, { from: range.from, to: range.to });
    window.location.href = url;
    toast(`Preparing ${el.dataset.export} download…`, 'info', 2200);
  }));

  async function load() {
    body.innerHTML = '<div class="loading-page"><div class="spinner"></div><div class="small muted">Crunching the numbers…</div></div>';
    try {
      const q = { from: range.from, to: range.to };
      const [pnl, series, hours, payments, staff, customers, categories, usage] = await Promise.all([
        api.report('profit-loss', q),
        api.report('timeseries', { ...q, bucket }),
        api.report('hours', q),
        api.report('payments', q),
        api.report('staff', q),
        api.report('customers', { ...q, limit: 8 }),
        api.report('categories', q),
        api.report('ingredient-usage', { ...q, limit: 10 }),
      ]);
      paint({ pnl, series, hours, payments, staff, customers, categories, usage });
    } catch (err) {
      body.innerHTML = `<div class="card"><div class="empty">${icon('alert', { size: 38, stroke: 1.5 })}
        <h4>Could not build the report</h4><p>${esc(err.message)}</p></div></div>`;
    }
  }

  function paint(d) {
    const s = d.pnl.statement;
    const perDay = d.pnl.perDay;
    const hasData = s.revenue > 0 || s.totalExpenses > 0;

    if (!hasData) {
      body.innerHTML = `<div class="card"><div class="empty">${icon('chart', { size: 40, stroke: 1.5 })}
        <h4>No trading in this period</h4>
        <p>Nothing was sold or spent between ${esc(dateOnly(range.from))} and ${esc(dateOnly(range.to))}.
        Try a wider range.</p></div></div>`;
      return;
    }

    body.innerHTML = `
      <div class="stack">

        <!-- Profit & loss -->
        <div class="card">
          <div class="card-head">
            <h3 class="grow">Profit &amp; loss</h3>
            <span class="badge">${esc(dateOnly(range.from))} – ${esc(dateOnly(range.to))}</span>
          </div>
          <div class="card-body">
            <div class="grid grid-4" style="margin-bottom:14px">
              ${kpi('Revenue', moneyCompact(s.revenue, true), `${num(perDay.sales, 1)} sales per day`, 'cash')}
              ${kpi('Cost of goods', moneyCompact(s.cogs, true), `${pct(s.revenue ? (s.cogs / s.revenue) * 100 : 0, 1)} of revenue`, 'box')}
              ${kpi('Expenses', moneyCompact(s.totalExpenses, true), `${s.expenses.length} categories`, 'wallet')}
              ${kpi('Net profit', moneyCompact(s.netProfit, true), `${s.netMargin}% of revenue`, 'trending',
                s.netProfit >= 0 ? 'ok' : 'bad')}
            </div>

            <div class="table-wrap">
              <table class="data">
                <tbody>
                  ${s.discounts > 0 ? `<tr><td>Gross sales</td><td class="num">${esc(money(s.grossRevenue))}</td></tr>
                  <tr><td class="muted">Less: discounts given</td><td class="num">−${esc(money(s.discounts))}</td></tr>` : ''}
                  <tr><td>Revenue from sales</td><td class="num strong">${esc(money(s.revenue))}</td></tr>
                  <tr><td class="muted">Less: cost of ingredients &amp; packaging</td>
                    <td class="num">−${esc(money(s.cogs))}</td></tr>
                  <tr><td><strong>Gross profit</strong> <span class="muted tiny">(${s.grossMargin}% margin)</span></td>
                    <td class="num strong">${esc(money(s.grossProfit))}</td></tr>
                  ${s.expenses.map((e) => `<tr>
                    <td class="muted">Less: ${esc(e.category)} <span class="tiny">(${e.count}×)</span></td>
                    <td class="num">−${esc(money(e.total))}</td></tr>`).join('')}
                  <tr><td><strong>Net profit</strong></td>
                    <td class="num strong" style="color:${s.netProfit >= 0 ? 'var(--ok)' : 'var(--bad)'};font-size:16px">
                      ${esc(money(s.netProfit))}</td></tr>
                  <tr><td class="muted">Per day over ${d.pnl.range.days} days</td>
                    <td class="num muted">${esc(money(perDay.profit))}</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Trend -->
        <div class="card">
          <div class="card-head">
            <h3 class="grow">${bucket === 'month' ? 'Monthly' : 'Daily'} trend</h3>
            <div class="segmented">
              <button data-bucket="day" class="${bucket === 'day' ? 'active' : ''}">By day</button>
              <button data-bucket="month" class="${bucket === 'month' ? 'active' : ''}">By month</button>
            </div>
          </div>
          <div class="card-body">
            <div class="legend" style="margin-bottom:8px">
              <span><i style="background:#B4531F"></i>Revenue</span>
              <span><i style="background:#2F7D4F"></i>Net profit</span>
              <span><i style="background:#B3382C"></i>Expenses</span>
            </div>
            <div class="chart" id="c-trend" style="min-height:230px"></div>
          </div>
        </div>

        <div class="grid grid-2">
          <!-- Best sellers -->
          <div class="card">
            <div class="card-head"><h3 class="grow">Best sellers</h3>
              <span class="small muted">by revenue</span></div>
            <div class="card-body" id="c-top"></div>
          </div>

          <!-- Peak hours -->
          <div class="card">
            <div class="card-head"><h3 class="grow">Busiest hours</h3>
              ${d.hours.peak?.revenue ? `<span class="badge gold">${icon('clock', { size: 12 })} ${d.hours.peak.hour}:00</span>` : ''}</div>
            <div class="card-body">
              <div class="chart" id="c-hours" style="min-height:190px"></div>
              <p class="tiny muted" style="margin:8px 0 0">Have bread out of the oven before your busiest hour.</p>
            </div>
          </div>

          <!-- Payment mix -->
          <div class="card">
            <div class="card-head"><h3 class="grow">How people paid</h3></div>
            <div class="card-body">
              <div class="row wrap" style="gap:18px;align-items:center">
                <div id="c-pay"></div><div data-donut-legend class="grow" style="min-width:150px"></div>
              </div>
            </div>
          </div>

          <!-- Expense split -->
          <div class="card">
            <div class="card-head"><h3 class="grow">Expense split</h3>
              <a class="btn btn-ghost btn-sm" href="#/expenses">Manage ${icon('chevronRight', { size: 15 })}</a></div>
            <div class="card-body" id="c-exp"></div>
          </div>

          <!-- Staff -->
          <div class="card">
            <div class="card-head"><h3 class="grow">Who sold what</h3></div>
            <div class="card-body tight" id="c-staff"></div>
          </div>

          <!-- Categories -->
          <div class="card">
            <div class="card-head"><h3 class="grow">By category</h3></div>
            <div class="card-body" id="c-cats"></div>
          </div>

          <!-- Top customers -->
          <div class="card">
            <div class="card-head"><h3 class="grow">Best customers</h3>
              <a class="btn btn-ghost btn-sm" href="#/customers">All ${icon('chevronRight', { size: 15 })}</a></div>
            <div class="card-body tight" id="c-cust"></div>
          </div>

          <!-- Ingredient usage -->
          <div class="card">
            <div class="card-head"><h3 class="grow">Ingredients consumed</h3>
              <a class="btn btn-ghost btn-sm" href="#/stock">Stock ${icon('chevronRight', { size: 15 })}</a></div>
            <div class="card-body tight" id="c-usage"></div>
          </div>
        </div>
      </div>`;

    cleanups.push(on(body, 'click', '[data-bucket]', (_e, el) => {
      bucket = el.dataset.bucket;
      load();
    }));

    cleanups.push(lineChart($('#c-trend', body), {
      labels: d.series.points.map((p) => (bucket === 'month' ? monthLabel(p.bucket) : shortDate(p.bucket))),
      series: [
        { name: 'Revenue', values: d.series.points.map((p) => p.revenue), color: '#B4531F', area: true },
        { name: 'Net profit', values: d.series.points.map((p) => p.netProfit), color: '#2F7D4F' },
        { name: 'Expenses', values: d.series.points.map((p) => p.expenses), color: '#B3382C', dashed: true },
      ],
      kind: 'money', height: 235, formatTip: (v) => money(v),
    }));

    $('#c-top', body).innerHTML = d.pnl.bestSellers.length
      ? hbars(d.pnl.bestSellers.map((p) => ({ label: p.name, value: p.revenue, margin: p.margin })),
        { valueFormat: (v) => moneyCompact(v, true), subFormat: (it) => `${num(it.margin, 0)}% margin` })
      : emptyState({ icon: 'tag', title: 'Nothing sold', message: 'No products were sold in this period.' });

    barChart($('#c-hours', body), {
      labels: Array.from({ length: 24 }, (_, h) => `${h}`),
      values: (() => {
        const v = new Array(24).fill(0);
        for (const h of d.hours.hours) v[h.hour] = h.revenue;
        return v;
      })(),
      kind: 'money', height: 190, labelEvery: 3,
    });

    donut($('#c-pay', body), {
      slices: d.payments.map((p, i) => ({
        label: { cash: 'Cash', mobile: 'Mobile money', card: 'Card', credit: 'On credit' }[p.method] || p.method,
        value: p.collected,
        display: moneyCompact(p.collected, true),
        color: ['#2F7D4F', '#B4531F', '#2A6089', '#B57708'][i % 4],
      })),
      centerValue: moneyCompact(d.payments.reduce((a, p) => a + p.collected, 0), true),
      centerLabel: 'collected',
    });

    $('#c-exp', body).innerHTML = d.pnl.statement.expenses.length
      ? hbars(d.pnl.statement.expenses.map((e) => ({ label: e.category, value: e.total })),
        { valueFormat: (v) => moneyCompact(v, true) })
      : '<p class="small muted">No expenses recorded in this period.</p>';

    $('#c-staff', body).innerHTML = d.staff.length ? `<div class="list">${d.staff.map((p) => `
      <div class="list-item">
        <span class="thumb">${esc((p.name || '?').slice(0, 2).toUpperCase())}</span>
        <span class="list-main"><span class="list-title">${esc(p.name)}</span>
          <span class="list-sub">${num(p.sales)} sales · avg ${esc(money(p.averageSale))}</span></span>
        <span class="list-side"><span class="list-amount">${esc(moneyCompact(p.revenue, true))}</span></span>
      </div>`).join('')}</div>` : '<p class="small muted">No sales recorded.</p>';

    $('#c-cats', body).innerHTML = d.categories.length
      ? hbars(d.categories.map((c) => ({ label: c.category, value: c.revenue })),
        { valueFormat: (v) => moneyCompact(v, true) })
      : '<p class="small muted">No category data.</p>';

    $('#c-cust', body).innerHTML = d.customers.length ? `<div class="list">${d.customers.map((c) => `
      <div class="list-item">
        <span class="thumb blue">${icon('user', { size: 17 })}</span>
        <span class="list-main"><span class="list-title">${esc(c.name)}</span>
          <span class="list-sub">${num(c.orders)} orders${Number(c.owed) > 0 ? ` · owes ${esc(money(c.owed))}` : ''}</span></span>
        <span class="list-side"><span class="list-amount">${esc(moneyCompact(c.revenue, true))}</span></span>
      </div>`).join('')}</div>`
      : '<p class="small muted" style="padding:14px">No named-customer sales in this period.</p>';

    $('#c-usage', body).innerHTML = d.usage.length ? `<div class="list">${d.usage.map((u) => `
      <div class="list-item">
        <span class="thumb green">${icon('flask', { size: 17 })}</span>
        <span class="list-main"><span class="list-title">${esc(u.name)}</span>
          <span class="list-sub">used in production</span></span>
        <span class="list-side"><span class="list-amount">${esc(qty(u.used))} <span class="tiny muted">${esc(u.unit)}</span></span>
          <span class="badge" style="margin-top:3px">${esc(moneyCompact(u.cost, true))}</span></span>
      </div>`).join('')}</div>`
      : '<p class="small muted" style="padding:14px">No stock movements in this period.</p>';
  }

  const kpi = (label, value, sub, ic, tone) => `
    <div class="kpi"><span class="kpi-icon">${icon(ic, { size: 32, stroke: 1.6 })}</span>
      <div class="kpi-label">${esc(label)}</div>
      <div class="kpi-value"${tone === 'bad' ? ' style="color:var(--bad)"' : tone === 'ok' ? ' style="color:var(--ok)"' : ''}>${esc(value)}</div>
      <div class="kpi-sub">${esc(sub)}</div></div>`;

  await load();
  return () => cleanups.forEach((fn) => { try { fn?.(); } catch { /* ignore */ } });
}

