/**
 * Point of sale. The screen staff live in all day, so it is built for
 * thumbs first: big tiles, a sticky summary bar on phones that opens the
 * cart as a sheet, and a persistent cart column on a computer.
 *
 * Events are delegated on document.body rather than on this view's host,
 * because the cart sheet is appended to <body> and must stay interactive.
 */
import { api } from '../api.js';
import { state, isOwner, loadData, invalidate, subscribe } from '../store.js';
import { icon, $, on, toast, busy, sheet, emptyState, confirmDialog } from '../ui.js';
import { money, num, esc, roundUpTo, methodLabel, localStamp } from '../format.js';
import { getCache, enqueue, countOutbox, makeRef, syncOutbox, syncStatus } from '../offline.js';

/** Cheap read of how much is still waiting to send. */
const syncStatusCount = () => { try { return syncStatus().count || 0; } catch { return 0; } };

const METHODS = [
  { id: 'cash', label: 'Cash', icon: 'cash' },
  { id: 'mobile', label: 'Mobile money', icon: 'mobile' },
  { id: 'card', label: 'Card', icon: 'card' },
  { id: 'credit', label: 'On credit', icon: 'credit' },
];

const ROOT = () => document.body;

export async function render(host) {
  let data;
  // `offline` means the till is running from the last cached snapshot. Trading
  // continues; writes are queued and replayed later.
  let offline = typeof navigator !== 'undefined' && navigator.onLine === false;
  try {
    data = await loadData();
  } catch (err) {
    // No server. Fall back to the snapshot taken at the last successful load so
    // the bakery can keep selling rather than staring at an error screen.
    data = await getCache('bootstrap');
    offline = true;
    if (!data || !Array.isArray(data.products)) {
      host.innerHTML = `<div class="card"><div class="empty">${icon('wifiOff', { size: 40, stroke: 1.5 })}
        <h4>Cannot reach the server</h4>
        <p>${esc(err.message)}</p>
        <p class="small muted">There is no saved product list on this device yet, so the till
        cannot open offline. Sign in once while connected to cache it.</p>
        <button class="btn btn-primary btn-sm" data-reload>Reload</button></div></div>`;
      const off = on(host, 'click', '[data-reload]', () => location.reload());
      return off;
    }
  }

  const products = (data.products || []).filter((p) => p.active !== 0);
  const categories = data.categories || [];
  const customers = data.customers || [];
  const walkIn = customers.find((c) => c.is_walk_in);

  /** @type {Map<number, {product:object, qty:number, price:number}>} */
  const cart = new Map();
  const filter = { category: 'all', q: '' };
  let payment = {
    method: 'cash', discount: 0, tendered: '', paidNow: '',
    customerId: walkIn?.id ?? '', note: '',
  };
  let sheetClose = null;

  /* ---------------- layout ---------------- */

  host.innerHTML = `
    <div class="page-head">
      <div class="grow">
        <h1>Sell</h1>
        <div class="small muted">Tap a product to add it. Tap again for one more.</div>
      </div>
      <div class="page-actions">
        <button class="btn btn-ghost btn-sm" data-refresh>${icon('refresh', { size: 15 })} Refresh</button>
      </div>
    </div>

    <div id="pos-offline" style="margin-bottom:12px"></div>

    <div class="pos">
      <div style="min-width:0">
        <div class="search-wrap" style="margin-bottom:10px">
          ${icon('search', { size: 17 })}
          <input type="search" id="pos-search" placeholder="Search products…" autocomplete="off" aria-label="Search products">
        </div>
        <div class="chips" id="pos-chips" style="margin-bottom:11px"></div>
        <div class="product-grid" id="pos-grid"></div>
      </div>

      <div class="pos-cart"><div class="card" id="cart-desktop"></div></div>
    </div>

    <div class="cart-bar" id="cart-bar">
      <div class="grow" style="min-width:0">
        <div class="strong" id="bar-count">Empty</div>
        <div class="tiny muted" id="bar-sub">Tap a product to start</div>
      </div>
      <button class="btn btn-primary btn-lg" id="bar-review" disabled style="min-width:136px">
        Review <span id="bar-total"></span>
      </button>
    </div>`;

  /* ---------------- product grid ---------------- */

  const paintChips = () => {
    const counts = new Map([['all', products.length]]);
    for (const p of products) {
      const key = p.category || 'Other';
      counts.set(key, (counts.get(key) || 0) + 1);
    }
    const chip = (key, label, count) =>
      `<button type="button" class="chip${filter.category === key ? ' active' : ''}" data-cat="${esc(key)}">
        ${esc(label)}<span class="count">${count}</span></button>`;
    $('#pos-chips', host).innerHTML =
      chip('all', 'All', products.length)
      + categories.filter((c) => counts.get(c.name)).map((c) => chip(c.name, c.name, counts.get(c.name))).join('')
      + (counts.get('Other') ? chip('Other', 'Other', counts.get('Other')) : '');
  };

  const visibleProducts = () => {
    const q = filter.q.trim().toLowerCase();
    return products.filter((p) => {
      if (filter.category !== 'all' && (p.category || 'Other') !== filter.category) return false;
      return !q || p.name.toLowerCase().includes(q) || (p.category || '').toLowerCase().includes(q);
    });
  };

  const paintGrid = () => {
    const list = visibleProducts();
    const grid = $('#pos-grid', host);
    if (!list.length) {
      grid.innerHTML = `<div style="grid-column:1/-1">${emptyState({
        icon: 'search',
        title: 'No products match',
        message: filter.q ? `Nothing found for “${filter.q}”.` : 'Add products in the Products screen first.',
        action: isOwner() ? '<a class="btn btn-primary btn-sm" href="#/products">Go to Products</a>' : '',
      })}</div>`;
      return;
    }
    grid.innerHTML = list.map((p) => {
      const line = cart.get(p.id);
      return `<button type="button" class="tile${line ? ' in-cart' : ''}" data-add="${p.id}">
        ${line ? `<span class="tile-qty">${num(line.qty)}</span>` : ''}
        <span class="tile-name">${esc(p.name)}</span>
        <span class="tile-price">${esc(money(p.price))}</span>
        ${p.category ? `<span class="tile-meta">${esc(p.category)}</span>` : ''}
      </button>`;
    }).join('');
  };

  /* ---------------- cart maths ---------------- */

  const totals = () => {
    let subtotal = 0;
    let count = 0;
    for (const line of cart.values()) {
      subtotal += line.qty * line.price;
      count += line.qty;
    }
    subtotal = Math.round(subtotal * 100) / 100;
    const discount = Math.min(Math.max(0, Math.round(Number(payment.discount) || 0)), subtotal);
    const total = Math.round((subtotal - discount) * 100) / 100;
    const tendered = payment.tendered === '' ? null : Math.max(0, Number(payment.tendered) || 0);
    const paidNow = payment.paidNow === '' ? null : Math.max(0, Number(payment.paidNow) || 0);

    const paid = Math.min(payment.method === 'credit' ? (paidNow ?? 0) : total, total);
    const change = payment.method === 'cash' && tendered !== null ? Math.max(0, tendered - total) : 0;
    return { subtotal, discount, total, count, paid, change, tendered, due: Math.max(0, total - paid) };
  };

  /** Handy cash denominations to tap instead of typing. */
  const quickCash = () => {
    const t = totals().total;
    if (t <= 0) return [];
    const opts = new Set([t]);
    for (const step of [500, 1000, 2000, 5000, 10000]) {
      const v = roundUpTo(t, step);
      if (v > t) opts.add(v);
    }
    return [...opts].sort((a, b) => a - b).slice(0, 5);
  };

  /* ---------------- cart rendering ---------------- */

  const cartHtml = () => {
    const t = totals();
    const lines = [...cart.values()];
    const decimals = Number(state.settings.currency_decimals ?? 0) || 0;
    const symbol = state.settings.currency_symbol || '';

    if (!lines.length) {
      return `
        <div class="card-head"><h3 class="grow">Current sale</h3></div>
        <div class="empty" style="padding:34px 18px">${icon('cart', { size: 38, stroke: 1.5 })}
          <h4>Nothing here yet</h4><p>Tap a product to start the order.</p></div>`;
    }

    return `
      <div class="card-head">
        <h3 class="grow">Current sale</h3>
        <button type="button" class="btn btn-ghost btn-sm" data-clear-cart>${icon('trash', { size: 15 })} Clear</button>
      </div>

      <div class="card-body tight" style="max-height:min(42vh,380px);overflow-y:auto">
        ${lines.map((l) => `
          <div class="cart-line">
            <div class="grow" style="min-width:0">
              <div class="cart-line-name">${esc(l.product.name)}</div>
              <div class="cart-line-sub">${esc(money(l.price))} each${Number(l.qty) !== 1 ? ` · ${esc(money(l.qty * l.price))}` : ''}</div>
            </div>
            <div class="stepper">
              <button type="button" data-dec="${l.product.id}" aria-label="One fewer">−</button>
              <input type="number" inputmode="decimal" min="0" step="${decimals ? 0.1 : 1}" value="${l.qty}"
                data-qty="${l.product.id}" aria-label="Quantity of ${esc(l.product.name)}">
              <button type="button" data-inc="${l.product.id}" aria-label="One more">+</button>
            </div>
            <button type="button" class="btn btn-ghost btn-icon btn-sm" data-del="${l.product.id}"
              aria-label="Remove ${esc(l.product.name)}">${icon('x', { size: 15 })}</button>
          </div>`).join('')}
      </div>

      <div class="card-body" style="border-top:1px solid var(--line)">
        <label class="field" style="margin-bottom:11px">
          <span class="field-label">Customer</span>
          <select data-customer>
            <option value="">— No customer —</option>
            ${customers.map((c) => `<option value="${c.id}"${String(payment.customerId) === String(c.id) ? ' selected' : ''}>${esc(c.name)}${c.is_walk_in ? ' (counter)' : ''}</option>`).join('')}
          </select>
        </label>

        <div class="field" style="margin-bottom:11px">
          <span class="field-label">Discount (${esc(symbol)})</span>
          <div class="row" style="gap:7px">
            <input type="number" min="0" step="1" inputmode="numeric" data-discount
              value="${payment.discount || ''}" placeholder="0" style="flex:1 1 auto;min-width:0">
            <button type="button" class="btn btn-sm" data-discount-pct="5">5%</button>
            <button type="button" class="btn btn-sm" data-discount-pct="10">10%</button>
          </div>
        </div>

        <div class="field" style="margin-bottom:11px">
          <span class="field-label">Payment</span>
          <div class="pay-grid">
            ${METHODS.map((m) => `<button type="button" class="pay-opt${payment.method === m.id ? ' active' : ''}" data-method="${m.id}">
              ${icon(m.icon, { size: 20 })}${esc(m.label)}</button>`).join('')}
          </div>
        </div>

        ${payment.method === 'cash' ? `
          <label class="field" style="margin-bottom:11px">
            <span class="field-label">Cash handed to you</span>
            <input type="number" min="0" step="1" inputmode="numeric" data-tendered
              value="${esc(payment.tendered)}" placeholder="${esc(String(t.total))}">
            <div class="quick-cash" style="margin-top:7px">
              ${quickCash().map((v) => `<button type="button" data-quick-val="${v}"${v === t.total ? ' class="active"' : ''}>${esc(money(v))}</button>`).join('')}
            </div>
          </label>` : ''}

        ${payment.method === 'credit' ? `
          <label class="field" style="margin-bottom:11px">
            <span class="field-label">Paid now (the rest is owed)</span>
            <input type="number" min="0" step="1" inputmode="numeric" data-paid-now
              value="${esc(payment.paidNow)}" placeholder="0">
            ${!payment.customerId ? '<div class="field-hint" style="color:var(--warn)">Pick a customer so you know who owes you.</div>' : ''}
          </label>` : ''}

        <label class="field" style="margin-bottom:0">
          <span class="field-label">Note (optional)</span>
          <input type="text" data-note value="${esc(payment.note)}" maxlength="200"
            placeholder="e.g. birthday cake for Friday">
        </label>
      </div>

      <div class="totals">
        <div class="total-row"><span>Subtotal · ${num(t.count)} items</span><span class="num">${esc(money(t.subtotal))}</span></div>
        ${t.discount ? `<div class="total-row"><span>Discount</span><span class="num">−${esc(money(t.discount))}</span></div>` : ''}
        <div class="total-row grand"><span>Total</span><span class="num">${esc(money(t.total))}</span></div>
        ${payment.method === 'cash' && t.tendered !== null ? `
          <div class="total-row" style="color:var(--ok);font-weight:700">
            <span>Change to give</span><span class="num">${esc(money(t.change))}</span></div>` : ''}
        ${payment.method === 'credit' && t.due > 0 ? `
          <div class="total-row" style="color:var(--warn);font-weight:700">
            <span>Still owed</span><span class="num">${esc(money(t.due))}</span></div>` : ''}
      </div>

      <div class="card-body" style="border-top:1px solid var(--line)">
        <button type="button" class="btn btn-primary btn-lg btn-block" data-complete>
          ${icon('check')} Complete sale · ${esc(money(t.total))}
        </button>
      </div>`;
  };

  const paintCart = () => {
    const t = totals();
    const html = cartHtml();

    const desktop = $('#cart-desktop', host);
    if (desktop) desktop.innerHTML = html;

    const barCount = $('#bar-count', host);
    if (barCount) {
      barCount.textContent = t.count ? `${num(t.count)} item${t.count === 1 ? '' : 's'}` : 'Empty';
      $('#bar-sub', host).textContent = t.count
        ? `${methodLabel(payment.method)}${t.discount ? ` · ${money(t.discount)} off` : ''}`
        : 'Tap a product to start';
      $('#bar-total', host).textContent = t.count ? money(t.total) : '';
      $('#bar-review', host).disabled = !t.count;
    }

    if (sheetClose) {
      const sheetCart = document.querySelector('[data-sheet-cart]');
      if (sheetCart) sheetCart.innerHTML = html;
    }
  };

  /* ---------------- cart actions ---------------- */

  const addProduct = (id, delta) => {
    const product = products.find((p) => p.id === Number(id));
    if (!product) return;
    const line = cart.get(product.id);
    if (line) {
      line.qty = Math.max(0, Math.round((line.qty + delta) * 1000) / 1000);
      if (line.qty === 0) cart.delete(product.id);
    } else if (delta > 0) {
      cart.set(product.id, { product, qty: delta, price: Number(product.price) || 0 });
    }
    paintGrid();
    paintCart();
  };

  const setQty = (id, value) => {
    const key = Number(id);
    const line = cart.get(key);
    if (!line) return;
    const q = Math.max(0, Math.min(100000, Number(value) || 0));
    if (q === 0) cart.delete(key);
    else line.qty = Math.round(q * 1000) / 1000;
    paintGrid();
    paintCart();
  };

  const reset = () => {
    cart.clear();
    payment = { ...payment, discount: 0, tendered: '', paidNow: '', note: '' };
    paintGrid();
    paintCart();
  };

  /* ---------------- events ---------------- */

  const offs = [];
  const bind = (event, selector, handler) => offs.push(on(ROOT(), event, selector, handler));

  bind('click', '[data-add]', (_e, el) => addProduct(el.dataset.add, 1));
  bind('click', '[data-inc]', (e, el) => { e.stopPropagation(); addProduct(el.dataset.inc, 1); });
  bind('click', '[data-dec]', (e, el) => { e.stopPropagation(); addProduct(el.dataset.dec, -1); });
  bind('click', '[data-del]', (e, el) => { e.stopPropagation(); setQty(el.dataset.del, 0); });
  bind('change', '[data-qty]', (_e, el) => setQty(el.dataset.qty, el.value));
  bind('click', '[data-cat]', (_e, el) => { filter.category = el.dataset.cat; paintChips(); paintGrid(); });
  bind('input', '#pos-search', (_e, el) => { filter.q = el.value; paintGrid(); });

  bind('click', '[data-refresh]', async (_e, el) => {
    busy(el, true);
    invalidate();
    try {
      const fresh = await loadData({ force: true });
      toast(`${fresh.products.length} products up to date`, 'ok', 1800);
      location.reload();
    } catch (err) { toast(err.message, 'bad'); busy(el, false); }
  });

  bind('change', '[data-customer]', (_e, el) => { payment.customerId = el.value; paintCart(); });
  bind('input', '[data-discount]', (_e, el) => { payment.discount = el.value; paintCart(); });
  bind('click', '[data-discount-pct]', (e, el) => {
    e.preventDefault();
    payment.discount = Math.round(totals().subtotal * (Number(el.dataset.discountPct) / 100));
    paintCart();
  });
  bind('click', '[data-method]', (_e, el) => {
    payment.method = el.dataset.method;
    if (payment.method !== 'cash') payment.tendered = '';
    if (payment.method !== 'credit') payment.paidNow = '';
    paintCart();
  });
  bind('input', '[data-tendered]', (_e, el) => { payment.tendered = el.value; paintCart(); });
  bind('input', '[data-paid-now]', (_e, el) => { payment.paidNow = el.value; paintCart(); });
  bind('input', '[data-note]', (_e, el) => { payment.note = el.value; });
  bind('click', '[data-quick-val]', (_e, el) => { payment.tendered = el.dataset.quickVal; paintCart(); });

  bind('click', '[data-clear-cart]', async () => {
    if (!cart.size) return;
    if (await confirmDialog({ title: 'Clear this sale?', message: 'Every item will be removed.', confirmLabel: 'Clear it', danger: true })) reset();
  });

  bind('click', '#bar-review', () => {
    if (!cart.size) return;
    sheetClose = sheet({
      title: 'Review sale',
      subtitle: `${num(totals().count)} items · ${methodLabel(payment.method)}`,
      body: '<div data-sheet-cart></div>',
      onMount: (el) => { $('[data-sheet-cart]', el).innerHTML = cartHtml(); },
      onClose: () => { sheetClose = null; },
    });
  });

  bind('click', '[data-complete]', (_e, el) => completeSale(el));

  async function completeSale(btn) {
    const t = totals();
    if (!cart.size) return toast('Add something to the sale first', 'warn');
    if (payment.method === 'credit' && !payment.customerId) {
      const go = await confirmDialog({
        title: 'No customer selected',
        message: 'Credit is hard to chase without a name. Save it anyway?',
        confirmLabel: 'Save anyway', cancelLabel: 'Go back',
      });
      if (!go) return;
    }

    // The payload is built once and always carries a client-generated
    // reference. That is what makes queueing safe: if a request fails we cannot
    // know whether the server recorded it, so we queue the same payload and let
    // the server's idempotency check decide. A sale can never be counted twice.
    const ref = makeRef('sale');
    const payload = {
      items: [...cart.values()].map((l) => ({ product_id: l.product.id, qty: l.qty, unit_price: l.price })),
      customer_id: payment.customerId || null,
      discount: t.discount,
      paid: t.paid,
      method: payment.method,
      note: payment.note || null,
      client_ref: ref,
    };
    // Snapshot the lines now: reset() clears the cart before any receipt is shown.
    const lines = [...cart.values()].map((l) => ({ ...l }));

    if (offline || (typeof navigator !== 'undefined' && navigator.onLine === false)) {
      return saveOffline(btn, ref, payload, t, lines);
    }

    busy(btn, true, 'Saving');
    try {
      const out = await api.createSale(payload);
      invalidate();
      const close = sheetClose;
      sheetClose = null;
      close?.();
      reset();
      if (out.low_stock?.length) toast(`Running low: ${out.low_stock.slice(0, 3).join(', ')}`, 'warn', 5000);
      toast(`Sale ${out.invoice_no} saved — ${money(out.total)}`, 'ok', 2600);
      const { showReceipt } = await import('./sales.js');
      showReceipt(out.id);
    } catch (err) {
      busy(btn, false);
      // Connection failed mid-request. Queue it rather than making the cashier
      // take the payment again — the client_ref guarantees no double count.
      if (err?.offline || err?.status === 0 || (typeof navigator !== 'undefined' && navigator.onLine === false)) {
        offline = true;
        return saveOffline(btn, ref, payload, t, lines, err);
      }
      toast(err.message || 'Could not save the sale', 'bad', 5000);
    }
  }

  /**
   * Store the sale on the device and hand the customer a provisional receipt.
   * The real invoice number arrives when the queue syncs.
   */
  async function saveOffline(btn, ref, payload, t, lines, err) {
    busy(btn, true, 'Saving');
    try {
      const position = (await countOutbox()) + 1;
      const provisional = `OFFLINE-${position}`;
      await enqueue('sale', { ...payload, sale_at: localStamp() }, {
        provisional,
        label: `${num(t.count)} ${t.count === 1 ? 'item' : 'items'} · ${money(t.total)}`,
      });
      const close = sheetClose;
      sheetClose = null;
      close?.();
      reset();
      busy(btn, false);
      toast(`Saved on this device as ${provisional} — ${money(t.total)}`, 'ok', 4200);
      showProvisionalReceipt({ provisional, t, lines, payload, when: localStamp() });
      syncOutbox(); // try immediately in case the connection just came back
    } catch (e) {
      busy(btn, false);
      toast(`Could not save on this device: ${e.message || 'storage unavailable'}. Write it down.`, 'bad', 8000);
    }
  }

  /**
   * A receipt built entirely from local data, so the customer still leaves with
   * something. It is clearly marked provisional: the server has not seen it yet
   * and will assign the real invoice number on sync.
   */
  function showProvisionalReceipt({ provisional, t, lines, payload, when }) {
    const biz = state.settings || {};
    const due = money(Math.max(0, Number(t.total) - Number(t.paid)));
    const customer = customers.find((c) => c.id === payload.customer_id);
    // `.pill-note` with no modifier is the gold/warning style.
    const body = `
      <div class="pill-note" style="margin-bottom:12px">${icon('wifiOff', { size: 17 })}
        <div>Saved on this device only. It will be sent to the server automatically once the
        connection returns, which is when the official invoice number is issued.</div></div>
      <div class="receipt" id="receipt-print">
        <div class="receipt-head">
          <div class="biz">${esc(biz.business_name || "Mama G's Bakery House")}</div>
          <div>${esc(biz.address || '')}</div>
          <div>${esc(biz.phone || '')}</div>
          <div class="rule"></div>
          <div><strong>${esc(provisional)}</strong> <span class="muted">(provisional)</span></div>
          <div>${esc(when || '')}</div>
          ${customer ? `<div>Customer: ${esc(customer.name)}</div>` : ''}
          <div>Served by: ${esc(state.user?.name || '')}</div>
          <div class="rule"></div>
        </div>
        <table>
          ${lines.map((l) => `
            <tr>
              <td>${esc(num(l.qty, 2))} × ${esc(l.product.name)}</td>
              <td class="r">${esc(money(l.price))}</td>
              <td class="r">${esc(money(l.qty * l.price))}</td>
            </tr>`).join('')}
        </table>
        <div class="rule"></div>
        <table>
          <tr><td>Subtotal</td><td class="r">${esc(money(t.subtotal))}</td></tr>
          ${t.discount ? `<tr><td>Discount</td><td class="r">−${esc(money(t.discount))}</td></tr>` : ''}
          <tr class="grand"><td>TOTAL</td><td class="r">${esc(money(t.total))}</td></tr>
          <tr><td>${esc(methodLabel(payload.method))} paid</td><td class="r">${esc(money(t.paid))}</td></tr>
          ${Number(due) > 0 ? `<tr><td><strong>Balance owed</strong></td><td class="r"><strong>${esc(due)}</strong></td></tr>` : ''}
          ${t.change > 0 ? `<tr><td>Change</td><td class="r">${esc(money(t.change))}</td></tr>` : ''}
        </table>
        ${payload.note ? `<div class="rule"></div><div>Note: ${esc(payload.note)}</div>` : ''}
        <div class="receipt-foot">${esc(biz.receipt_note || 'Thank you!')}</div>
      </div>`;

    const closeSheet = sheet({
      title: provisional,
      subtitle: `${num(t.count)} ${t.count === 1 ? 'item' : 'items'} · queued on this device`,
      wide: false,
      body,
      footer: `
        <button class="btn" data-print>${icon('printer', { size: 16 })} Print</button>
        <button class="btn btn-primary" data-done>Done</button>`,
      onMount: (el, close) => {
        on(el, 'click', '[data-print]', () => window.print());
        on(el, 'click', '[data-done]', () => close());
      },
      onClose: () => { sheetClose = null; },
    });
    sheetClose = closeSheet;
  }

  /* ---------------- mount ---------------- */

  /** Where the offline notice lives, so it can be repainted without a re-render. */
  const paintOfflineNotice = () => {
    const host2 = $('#pos-offline', host);
    if (!host2) return;
    const pending = syncStatusCount();
    host2.innerHTML = offline ? `
      <div class="pill-note">${icon('wifiOff', { size: 17 })}
        <div><strong>Working offline.</strong> Keep selling — every sale is stored on this
        device and sent automatically when the connection returns.
        ${pending ? `<br><span class="muted">${pending} item${pending === 1 ? '' : 's'} waiting to send.</span>` : ''}
        <br><span class="muted">Stock levels are not shown offline, because a stale number
        would be worse than none.</span></div></div>` : '';
  };

  paintOfflineNotice();
  paintChips();
  paintGrid();
  paintCart();

  // Follow the connection: coming back online flips the till to live mode and
  // flushes the queue; losing it switches to queueing without a page reload.
  offs.push(subscribe((what) => {
    if (what !== 'online') return;
    const nowOnline = typeof navigator === 'undefined' || navigator.onLine !== false;
    if (nowOnline === !offline) { paintOfflineNotice(); return; }
    offline = !nowOnline;
    paintOfflineNotice();
    if (nowOnline) {
      syncOutbox().then((out) => {
        if (out.synced) toast(`Sent ${out.synced} queued ${out.synced === 1 ? 'sale' : 'sales'} to the server`, 'ok', 3600);
        invalidate();
      });
    }
  }));

  // Leave room for the fixed summary bar on phones.
  const main = host.closest('.main');
  const prevPad = main ? main.style.paddingBottom : '';
  const fitPadding = () => {
    if (!main) return;
    main.style.paddingBottom = window.innerWidth < 1000 ? 'calc(var(--nav-h) + 96px)' : (prevPad || '');
  };
  fitPadding();
  window.addEventListener('resize', fitPadding);

  return () => {
    offs.forEach((off) => { try { off(); } catch { /* ignore */ } });
    window.removeEventListener('resize', fitPadding);
    if (sheetClose) { const c = sheetClose; sheetClose = null; c(); }
    if (main) main.style.paddingBottom = prevPad || '';
  };
}

export { METHODS };
