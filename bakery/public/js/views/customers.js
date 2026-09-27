/**
 * Customers: who buys, how often, and — importantly for a bakery that sells
 * on credit — who still owes you.
 */
import { api } from '../api.js';
import { state, isOwner, invalidate } from '../store.js';
import { icon, $, on, toast, busy, sheet, emptyState, confirmDialog } from '../ui.js';
import { money, moneyCompact, num, esc, dateTime, relTime, methodLabel } from '../format.js';

export async function render(host) {
  const owner = isOwner();
  let all = [];
  const filter = { q: '', onlyOwed: false };
  const cleanups = [];

  host.innerHTML = `
    <div class="page-head">
      <div class="grow">
        <h1>Customers</h1>
        <div class="small muted">Regulars, wholesale accounts and who owes what.</div>
      </div>
      <div class="page-actions">
        <button class="btn btn-primary" data-add>${icon('plus', { size: 17 })} Add customer</button>
      </div>
    </div>

    <div class="card" style="margin-bottom:12px">
      <div class="card-body">
        <div class="search-wrap" style="margin-bottom:10px">
          ${icon('search', { size: 17 })}
          <input type="search" id="c-search" placeholder="Search by name or phone…" aria-label="Search customers">
        </div>
        <div class="chips">
          <button class="chip active" data-cfilter="all">Everyone</button>
          <button class="chip" data-cfilter="owed">Owe money</button>
          <button class="chip" data-cfilter="regular">Regulars</button>
        </div>
      </div>
    </div>

    <div class="grid grid-3" id="c-kpis" style="margin-bottom:12px"></div>

    <div class="card">
      <div class="card-head"><h3 class="grow" id="c-heading">Customers</h3><span class="small muted" id="c-count"></span></div>
      <div class="card-body tight" id="c-list"></div>
    </div>`;

  const list = $('#c-list', host);
  const kpis = $('#c-kpis', host);

  async function load() {
    try {
      all = await api.customers({ q: filter.q, limit: 400 });
      paint();
    } catch (err) {
      list.innerHTML = emptyState({ icon: 'alert', title: 'Could not load customers', message: err.message });
    }
  }

  function shown() {
    return all.filter((c) => {
      if (filter.onlyOwed === 'owed' && !(Number(c.owed) > 0)) return false;
      if (filter.onlyOwed === 'regular' && Number(c.orders) < 3) return false;
      return true;
    });
  }

  function paint() {
    const rows = shown();
    const real = all.filter((c) => !c.is_walk_in);
    const owed = real.reduce((a, c) => a + Number(c.owed || 0), 0);
    const revenue = real.reduce((a, c) => a + Number(c.revenue || 0), 0);
    const debtors = real.filter((c) => Number(c.owed) > 0);

    kpis.innerHTML = `
      ${kpi('Customers', num(real.length), `${num(all.reduce((a, c) => a + Number(c.orders || 0), 0))} orders recorded`, 'users')}
      ${kpi('Their spend', moneyCompact(revenue, true), 'all time, excluding counter sales', 'trending')}
      ${kpi('Owed to you', moneyCompact(owed, true), debtors.length ? `${debtors.length} customer(s) on credit` : 'Nobody owes you', 'credit')}`;

    $('#c-count', host).textContent = `${rows.length}`;

    if (!rows.length) {
      list.innerHTML = emptyState({
        icon: 'users',
        title: filter.q ? 'No match' : filter.onlyOwed === 'owed' ? 'Nobody owes you' : 'No customers yet',
        message: filter.q ? `Nothing matches “${filter.q}”.`
          : filter.onlyOwed === 'owed' ? 'Every credit sale has been settled.'
            : 'Add the cafes, schools and regulars who buy from you.',
        action: '<button class="btn btn-primary btn-sm" data-add2>Add customer</button>',
      });
      return;
    }

    list.innerHTML = `<div class="list">${rows.map((c) => `
      <div class="list-item clickable" data-cust="${c.id}" role="button" tabindex="0">
        <span class="thumb ${c.is_walk_in ? 'grey' : Number(c.owed) > 0 ? 'gold' : 'blue'}">
          ${icon(c.is_walk_in ? 'store' : Number(c.owed) > 0 ? 'credit' : 'user', { size: 18 })}</span>
        <span class="list-main">
          <span class="list-title">${esc(c.name)}</span>
          <span class="list-sub">${num(c.orders || 0)} order(s)${c.last_visit ? ` · last ${esc(relTime(c.last_visit))}` : ' · no sales yet'}${c.phone ? ` · ${esc(c.phone)}` : ''}</span>
        </span>
        <span class="list-side">
          ${owner && !c.is_walk_in ? `<span class="list-amount">${esc(moneyCompact(c.revenue, true))}</span>` : ''}
          ${Number(c.owed) > 0 ? `<span class="badge warn" style="margin-top:3px">owes ${esc(money(c.owed))}</span>` : ''}
        </span>
      </div>`).join('')}</div>`;
  }

  const kpi = (label, value, sub, ic) => `
    <div class="kpi"><span class="kpi-icon">${icon(ic, { size: 32, stroke: 1.6 })}</span>
      <div class="kpi-label">${esc(label)}</div><div class="kpi-value">${esc(value)}</div>
      <div class="kpi-sub">${esc(sub)}</div></div>`;

  let t = 0;
  cleanups.push(on(host, 'input', '#c-search', (_e, el) => {
    clearTimeout(t);
    const v = el.value;
    t = setTimeout(() => { filter.q = v; load(); }, 300);
  }));
  cleanups.push(on(host, 'click', '[data-cfilter]', (_e, el) => {
    filter.onlyOwed = el.dataset.cfilter;
    host.querySelectorAll('[data-cfilter]').forEach((b) => b.classList.toggle('active', b === el));
    paint();
  }));
  cleanups.push(on(host, 'click', '[data-add]', () => editor(null)));
  cleanups.push(on(host, 'click', '[data-add2]', () => editor(null)));
  cleanups.push(on(host, 'click', '[data-cust]', (_e, el) => {
    const c = all.find((x) => String(x.id) === el.dataset.cust);
    if (c) detail(c);
  }));

  /* ---------------- detail ---------------- */

  async function detail(c) {
    let sales = [];
    try {
      sales = (await api.sales({ customer_id: c.id, from: '2000-01-01', to: '2999-12-31', limit: 12 })).sales;
    } catch { /* history is a nice-to-have */ }

    sheet({
      title: c.name,
      subtitle: c.is_walk_in ? 'Counter sales' : [c.phone, c.address].filter(Boolean).join(' · ') || 'No contact details',
      body: `
        ${Number(c.owed) > 0 ? `<div class="pill-note warn" style="margin-bottom:12px">${icon('credit', { size: 17 })}
          <div class="grow"><strong>${esc(money(c.owed))} outstanding.</strong> Across
          ${num(c.orders)} order(s).</div></div>` : ''}
        <div class="grid grid-3" style="margin-bottom:14px">
          <div class="kpi"><div class="kpi-label">Orders</div><div class="kpi-value">${num(c.orders || 0)}</div></div>
          ${owner ? `<div class="kpi"><div class="kpi-label">Lifetime spend</div>
            <div class="kpi-value">${esc(moneyCompact(c.revenue || 0, true))}</div></div>` : ''}
          <div class="kpi"><div class="kpi-label">Last visit</div>
            <div class="kpi-value" style="font-size:15px">${c.last_visit ? esc(dateTime(c.last_visit)) : 'Never'}</div></div>
        </div>
        ${c.notes ? `<div class="pill-note info" style="margin-bottom:12px">${icon('info', { size: 17 })}<div>${esc(c.notes)}</div></div>` : ''}
        <h4 style="margin-bottom:8px">Recent orders</h4>
        ${sales.length ? `<div class="list" style="border:1px solid var(--line);border-radius:var(--r-md);overflow:hidden">
          ${sales.map((s) => `<div class="list-item" data-sale="${s.id}" style="cursor:pointer">
            <span class="list-main">
              <span class="list-title">${esc(s.invoice_no)} · ${esc(dateTime(s.sale_at))}</span>
              <span class="list-sub">${esc(methodLabel(s.method))} · ${num(s.qty ?? 0, 0)} items</span>
            </span>
            <span class="list-side"><span class="list-amount">${esc(money(s.total))}</span>
              ${Number(s.due) > 0 ? `<span class="badge warn" style="margin-top:3px">owes ${esc(money(s.due))}</span>` : ''}</span>
          </div>`).join('')}</div>`
        : '<p class="small muted">No sales recorded for this customer yet.</p>'}`,
      footer: `${!c.is_walk_in && owner ? `<button class="btn btn-danger" data-delete style="flex:0 0 auto">${icon('trash', { size: 16 })}</button>` : ''}
        <button class="btn" data-close>Close</button>
        ${!c.is_walk_in ? `<button class="btn btn-primary" data-edit>${icon('pencil', { size: 16 })} Edit</button>` : ''}`,
      onMount: (el, closeSheet) => {
        on(el, 'click', '[data-edit]', () => { closeSheet(); editor(c); });
        on(el, 'click', '[data-sale]', async (_e, row) => {
          const { showReceipt } = await import('./sales.js');
          showReceipt(row.dataset.sale, { afterActions: () => { closeSheet(); load(); } });
        });
        if (!c.is_walk_in && owner) {
          on(el, 'click', '[data-delete]', async () => {
            if (!await confirmDialog({ title: `Delete ${c.name}?`, message: 'Only possible if they have no sales recorded.', confirmLabel: 'Delete', danger: true })) return;
            try {
              await api.deleteCustomer(c.id);
              invalidate();
              toast('Customer deleted', 'ok');
              closeSheet(); load();
            } catch (err) { toast(err.message, 'bad', 5000); }
          });
        }
      },
    });
  }

  /* ---------------- editor ---------------- */

  function editor(c) {
    const isNew = !c;
    const cust = c || { name: '', phone: '', address: '', notes: '' };
    sheet({
      title: isNew ? 'Add customer' : cust.name,
      body: `<form id="c-form">
        <label class="field"><span class="field-label">Name</span>
          <input type="text" name="name" value="${esc(cust.name)}" required maxlength="120"
            placeholder="e.g. Cafe Aroma"></label>
        <label class="field"><span class="field-label">Phone</span>
          <input type="tel" name="phone" value="${esc(cust.phone ?? '')}" maxlength="40" inputmode="tel"
            placeholder="+257 …"></label>
        <label class="field"><span class="field-label">Address / area</span>
          <input type="text" name="address" value="${esc(cust.address ?? '')}" maxlength="200"
            placeholder="e.g. Rohero II, Bujumbura"></label>
        <label class="field" style="margin-bottom:0"><span class="field-label">Notes</span>
          <textarea name="notes" maxlength="400" placeholder="What they usually order, payment terms…">${esc(cust.notes ?? '')}</textarea></label>
      </form>`,
      footer: `<button class="btn" data-close>Cancel</button>
        <button class="btn btn-primary" data-save>${isNew ? 'Add customer' : 'Save changes'}</button>`,
      onMount: (el, closeSheet) => {
        on(el, 'click', '[data-save]', async () => {
          const d = Object.fromEntries(new FormData($('#c-form', el)).entries());
          if (!String(d.name).trim()) return toast('Give the customer a name', 'warn');
          const btn = $('[data-save]', el);
          busy(btn, true, 'Saving');
          try {
            await api.saveCustomer(isNew ? null : cust.id, d);
            invalidate();
            toast(isNew ? `${d.name} added` : 'Customer saved', 'ok');
            closeSheet();
            await load();
          } catch (err) { busy(btn, false); toast(err.message, 'bad'); }
        });
      },
    });
  }

  await load();
  return () => cleanups.forEach((fn) => { try { fn?.(); } catch { /* ignore */ } });
}
