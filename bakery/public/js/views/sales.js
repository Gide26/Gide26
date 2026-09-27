/**
 * Sales history + the receipt. The receipt doubles as the confirmation
 * shown straight after a sale, so it can be printed or shared on WhatsApp.
 */
import { api } from '../api.js';
import { state, isOwner } from '../store.js';
import { icon, $, on, toast, busy, sheet, emptyState, confirmDialog,
  rangePickerHtml, bindRangePicker, defaultRange } from '../ui.js';
import { money, num, qty, esc, dateTime, dateOnly, methodLabel, statusLabel, todayStr } from '../format.js';
import { pendingPanel } from '../pending.js';

const PAGE = 40;

export async function render(host, ctx) {
  const cleanups = [];
  const owner = isOwner();
  const range = { ...defaultRange() };
  const filters = {
    status: ctx.params.get('status') || '',
    method: '',
    q: '',
  };
  let offset = 0;
  let rows = [];
  let totals = { count: 0, revenue: 0, collected: 0 };
  let loading = false;

  host.innerHTML = `
    <div class="page-head">
      <div class="grow">
        <h1>Sales</h1>
        <div class="small muted">${owner ? 'Every sale, with what each one earned.' : 'Your own sales.'}</div>
      </div>
      <div class="page-actions">
        <a class="btn btn-primary" href="#/sell">${icon('cart', { size: 17 })} New sale</a>
      </div>
    </div>

    <div id="sales-queued" style="margin-bottom:12px"></div>

    <div class="card" style="margin-bottom:12px">
      <div class="card-body">
        <div id="sales-range"></div>
        <div class="row wrap" style="gap:8px;margin-top:11px">
          <div class="search-wrap" style="flex:1 1 190px">
            ${icon('search', { size: 17 })}
            <input type="search" id="sales-q" placeholder="Invoice, customer or note…" value="${esc(filters.q)}">
          </div>
          <select id="sales-status" style="flex:0 1 150px" aria-label="Filter by status">
            <option value="">Any status</option>
            ${['paid', 'partial', 'unpaid', 'void'].map((s) => `<option value="${s}"${filters.status === s ? ' selected' : ''}>${esc(statusLabel(s))}</option>`).join('')}
          </select>
          <select id="sales-method" style="flex:0 1 160px" aria-label="Filter by payment">
            <option value="">Any payment</option>
            ${['cash', 'mobile', 'card', 'credit'].map((m) => `<option value="${m}"${filters.method === m ? ' selected' : ''}>${esc(methodLabel(m))}</option>`).join('')}
          </select>
        </div>
      </div>
    </div>

    <div class="grid grid-3" id="sales-kpis" style="margin-bottom:12px"></div>

    <div class="card">
      <div class="card-head">
        <h3 class="grow" id="sales-heading">Sales</h3>
        <span class="small muted" id="sales-count"></span>
      </div>
      <div class="card-body tight" id="sales-list"></div>
      <div class="card-foot center" id="sales-more"></div>
    </div>`;

  const kpis = $('#sales-kpis', host);
  const list = $('#sales-list', host);
  const more = $('#sales-more', host);

  cleanups.push(bindRangePicker(
    (() => { const d = $('#sales-range', host); return d; })(),
    range, () => reload()));

  let qTimer = 0;
  cleanups.push(on(host, 'input', '#sales-q', (_e, el) => {
    clearTimeout(qTimer);
    qTimer = setTimeout(() => { filters.q = el.value; reload(); }, 320);
  }));
  cleanups.push(on(host, 'change', '#sales-status', (_e, el) => { filters.status = el.value; reload(); }));
  cleanups.push(on(host, 'change', '#sales-method', (_e, el) => { filters.method = el.value; reload(); }));

  cleanups.push(on(list, 'click', '[data-sale]', (_e, el) => showReceipt(el.dataset.sale)));

  cleanups.push(on(more, 'click', '[data-more]', async (_e, el) => {
    busy(el, true, 'Loading');
    await fetchPage(false);
    busy(el, false);
  }));

  async function fetchPage(reset) {
    if (loading) return;
    loading = true;
    if (reset) { offset = 0; rows = []; }
    try {
      const out = await api.sales({
        from: range.from, to: range.to, limit: PAGE, offset,
        status: filters.status, method: filters.method, q: filters.q,
      });
      rows = reset ? out.sales : rows.concat(out.sales);
      totals = out.totals;
      offset += out.sales.length;
      paint();
    } catch (err) {
      list.innerHTML = emptyState({ icon: 'alert', title: 'Could not load sales', message: err.message });
    } finally {
      loading = false;
    }
  }

  // Sales taken offline are on this device but not yet on the server, so they
  // are invisible to the list below. The shared panel shows them, and offers the
  // conflict choices when the server has moved on without us.
  const queuedHost = $('#sales-queued', host);
  cleanups.push(pendingPanel(queuedHost, { kinds: ['sale'], title: 'Sales queued on this device' }));

  function paint() {
    const due = rows.reduce((a, s) => a + (Number(s.due) > 0 && s.status !== 'void' ? Number(s.due) : 0), 0);
    kpis.innerHTML = `
      ${kpi('Sales', num(totals.count), `${dateOnly(range.from)} – ${dateOnly(range.to)}`, 'receipt')}
      ${kpi('Revenue', money(totals.revenue), totals.count ? `avg ${money(totals.count ? totals.revenue / totals.count : 0)}` : '—', 'cash')}
      ${kpi(owner ? 'Still owed' : 'Collected', owner ? money(due) : money(totals.collected),
        owner ? `${rows.filter((s) => Number(s.due) > 0).length} open sale(s)` : `${money(Math.max(0, totals.revenue - totals.collected))} outstanding`,
        owner ? 'credit' : 'check')}`;

    $('#sales-count', host).textContent = rows.length ? `${rows.length} shown` : '';

    if (!rows.length) {
      list.innerHTML = emptyState({
        icon: 'receipt', title: 'No sales in this period',
        message: filters.q || filters.status || filters.method
          ? 'Try clearing the filters or widening the dates.'
          : 'Record your first sale from the Sell screen.',
        action: '<a class="btn btn-primary btn-sm" href="#/sell">Open the till</a>',
      });
      more.innerHTML = '';
      return;
    }

    list.innerHTML = `<div class="list">${rows.map(rowHtml).join('')}</div>`;
    more.innerHTML = rows.length < totals.count || rows.length >= PAGE
      ? `<button class="btn btn-sm" data-more>Load more</button>`
      : `<span class="small muted">That is everything — ${rows.length} sale${rows.length === 1 ? '' : 's'}</span>`;
  }

  const kpi = (label, value, sub, ic) => `
    <div class="kpi">
      <span class="kpi-icon">${icon(ic, { size: 32, stroke: 1.6 })}</span>
      <div class="kpi-label">${esc(label)}</div>
      <div class="kpi-value">${esc(value)}</div>
      <div class="kpi-sub">${esc(sub)}</div>
    </div>`;

  const rowHtml = (s) => `
    <div class="list-item clickable" data-sale="${s.id}" role="button" tabindex="0">
      <span class="thumb ${s.status === 'void' ? 'red' : s.status === 'paid' ? 'green' : 'gold'}">
        ${icon(s.status === 'void' ? 'x' : s.method === 'mobile' ? 'mobile' : s.method === 'card' ? 'card' : s.method === 'credit' ? 'credit' : 'cash', { size: 18 })}
      </span>
      <span class="list-main">
        <span class="list-title">${esc(s.invoice_no)}${s.customer && !/^walk-in/i.test(s.customer) ? ` · ${esc(s.customer)}` : ''}</span>
        <span class="list-sub">${esc(dateTime(s.sale_at))} · ${num(s.qty ?? 0, 0)} items · ${esc(methodLabel(s.method))}${s.sold_by ? ` · ${esc(s.sold_by)}` : ''}</span>
      </span>
      <span class="list-side">
        <span class="list-amount"${s.status === 'void' ? ' style="text-decoration:line-through;opacity:.55"' : ''}>${esc(money(s.total))}</span>
        ${Number(s.due) > 0 ? `<span class="badge warn" style="margin-top:3px">owes ${esc(money(s.due))}</span>` : ''}
        ${s.status === 'void' ? '<span class="badge bad" style="margin-top:3px">voided</span>' : ''}
        ${s.status === 'partial' ? '<span class="badge info" style="margin-top:3px">part paid</span>' : ''}
      </span>
    </div>`;

  const reload = () => fetchPage(true);
  await reload();

  return () => cleanups.forEach((fn) => { try { fn?.(); } catch { /* ignore */ } });
}

/* ------------------------------------------------------------------ *
 * Receipt
 * ------------------------------------------------------------------ */

export async function showReceipt(saleId, { afterActions } = {}) {
  let sale;
  try {
    sale = await api.sale(saleId);
  } catch (err) {
    toast(err.message || 'Could not load that sale', 'bad');
    return;
  }

  const biz = sale.business || {};
  const owner = isOwner();
  const canEdit = owner || sale.user_id === state.user?.id;
  const symbol = biz.symbol || state.settings.currency_symbol || 'FBu';

  const receiptBody = `
    <div class="receipt" id="receipt-print">
      <div class="receipt-head">
        <div class="biz">${esc(biz.name || state.settings.business_name || 'Bakery')}</div>
        <div>${esc(biz.address || '')}</div>
        <div>${esc(biz.phone || '')}</div>
        <div class="rule"></div>
        <div><strong>${esc(sale.invoice_no)}</strong></div>
        <div>${esc(dateTime(sale.sale_at))}</div>
        ${sale.customer ? `<div>Customer: ${esc(sale.customer.name)}</div>` : ''}
        ${sale.sold_by ? `<div>Served by: ${esc(sale.sold_by)}</div>` : ''}
        <div class="rule"></div>
      </div>
      <table>
        ${sale.items.map((i) => `
          <tr>
            <td>${esc(num(i.qty))} × ${esc(i.name)}</td>
            <td class="r">${esc(money(i.unit_price, { decimals: biz.decimals }))}</td>
            <td class="r">${esc(money(i.line_total, { decimals: biz.decimals }))}</td>
          </tr>`).join('')}
      </table>
      <div class="rule"></div>
      <table>
        <tr><td>Subtotal</td><td class="r">${esc(money(sale.subtotal))}</td></tr>
        ${Number(sale.discount) ? `<tr><td>Discount</td><td class="r">−${esc(money(sale.discount))}</td></tr>` : ''}
        <tr class="grand"><td>TOTAL</td><td class="r">${esc(money(sale.total))}</td></tr>
        <tr><td>${esc(methodLabel(sale.method))} paid</td><td class="r">${esc(money(sale.paid))}</td></tr>
        ${Number(sale.due) > 0 ? `<tr><td><strong>Balance owed</strong></td><td class="r"><strong>${esc(money(sale.due))}</strong></td></tr>` : ''}
        ${owner && sale.cogs !== undefined ? `
          <tr><td class="muted">Cost of goods</td><td class="r muted">${esc(money(sale.cogs ?? 0))}</td></tr>
          <tr><td class="muted">Gross profit</td><td class="r muted">${esc(money(Number(sale.total) - Number(sale.cogs ?? 0)))}</td></tr>` : ''}
      </table>
      ${sale.note ? `<div class="rule"></div><div>Note: ${esc(sale.note)}</div>` : ''}
      <div class="receipt-foot">${esc(biz.note || state.settings.receipt_note || 'Thank you!')}</div>
    </div>`;

  const close = sheet({
    title: sale.invoice_no,
    subtitle: `${dateTime(sale.sale_at)} · ${statusLabel(sale.status)}`,
    wide: false,
    body: `
      ${sale.status === 'void' ? `<div class="pill-note bad" style="margin-bottom:12px">${icon('x', { size: 17 })}
        <div>This sale was voided. It is excluded from every report and the stock was put back.</div></div>` : ''}
      ${receiptBody}`,
    footer: `
      <button class="btn" data-print>${icon('printer', { size: 16 })} Print</button>
      <button class="btn" data-share>${icon('users', { size: 16 })} Share</button>
      ${Number(sale.due) > 0 && canEdit && sale.status !== 'void'
        ? `<button class="btn btn-ok" data-pay>${icon('cash', { size: 16 })} Take payment</button>` : ''}
      ${owner && sale.status !== 'void' ? `<button class="btn btn-danger" data-void>${icon('trash', { size: 16 })} Void</button>` : ''}`,
    onMount: (el, closeSheet) => {
      on(el, 'click', '[data-print]', () => window.print());

      on(el, 'click', '[data-share]', async () => {
        const text = receiptText(sale, biz, symbol);
        if (navigator.share) {
          try { await navigator.share({ title: sale.invoice_no, text }); return; }
          catch (err) { if (err?.name === 'AbortError') return; }
        }
        window.open(`https://wa.me/?text=${encodeURIComponent(text)}`, '_blank', 'noopener');
      });

      on(el, 'click', '[data-pay]', async () => {
        const due = Number(sale.due);
        const amount = window.prompt(`Amount received towards ${sale.invoice_no} (owed ${money(due)}):`, String(due));
        if (amount === null) return;
        const value = Number(String(amount).replace(/,/g, ''));
        if (!Number.isFinite(value) || value <= 0) return toast('Enter an amount above zero', 'warn');
        try {
          const out = await api.paySale(sale.id, { amount: value });
          toast(`Payment recorded. ${out.status === 'paid' ? 'Settled in full.' : `${money(out.due)} still owed.`}`, 'ok');
          closeSheet();
          afterActions?.();
          showReceipt(sale.id, { afterActions });
        } catch (err) { toast(err.message, 'bad'); }
      });

      on(el, 'click', '[data-void]', async () => {
        const ok = await confirmDialog({
          title: `Void ${sale.invoice_no}?`,
          message: `The ${money(sale.total)} sale will be marked voided, removed from all reports, and any stock it used will be returned to the shelf. This cannot be undone.`,
          confirmLabel: 'Void this sale', danger: true,
        });
        if (!ok) return;
        try {
          await api.voidSale(sale.id);
          toast(`${sale.invoice_no} voided`, 'ok');
          closeSheet();
          afterActions?.();
        } catch (err) { toast(err.message, 'bad'); }
      });
    },
  });

  return close;
}

/** Plain-text version of the receipt for WhatsApp / SMS / share sheet. */
function receiptText(sale, biz, symbol) {
  const m = (v) => `${symbol} ${num(v)}`;
  const lines = [
    `*${biz.name || 'Bakery'}*`,
    biz.address, biz.phone,
    '',
    `Receipt ${sale.invoice_no}`,
    dateTime(sale.sale_at),
    sale.customer ? `Customer: ${sale.customer.name}` : '',
    '',
    ...sale.items.map((i) => `${num(i.qty)} x ${i.name} — ${m(i.line_total)}`),
    '',
    `Subtotal: ${m(sale.subtotal)}`,
    Number(sale.discount) ? `Discount: -${m(sale.discount)}` : '',
    `*TOTAL: ${m(sale.total)}*`,
    `Paid (${methodLabel(sale.method)}): ${m(sale.paid)}`,
    Number(sale.due) > 0 ? `Balance owed: ${m(sale.due)}` : '',
    '',
    biz.note || 'Thank you!',
  ];
  return lines.filter(Boolean).join('\n');
}

export { qty, todayStr };
