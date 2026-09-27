/**
 * Inventory: ingredient stock levels, the movements that changed them, and
 * suppliers. Sales deduct stock automatically through recipes, so this
 * screen is mostly about purchasing, waste and stock counts.
 */
import { api } from '../api.js';
import { state, isOwner, loadData, invalidate } from '../store.js';
import { icon, $, on, toast, busy, sheet, emptyState, confirmDialog,
  rangePickerHtml, bindRangePicker, defaultRange } from '../ui.js';
import { money, moneyCompact, num, qty, esc, dateTime, kindLabel, shortDate } from '../format.js';

const TABS = [
  { id: 'stock', label: 'Stock levels', icon: 'box' },
  { id: 'history', label: 'Movements', icon: 'list' },
  { id: 'suppliers', label: 'Suppliers', icon: 'truck' },
];

export async function render(host, ctx) {
  const owner = isOwner();
  let tab = ctx.params.get('tab') || 'stock';
  const filter = { q: '', onlyLow: ctx.params.get('filter') === 'low' };
  const range = { ...defaultRange() };
  const cleanups = [];

  host.innerHTML = `
    <div class="page-head">
      <div class="grow">
        <h1>Inventory</h1>
        <div class="small muted">What you have, what is running out, and where it came from.</div>
      </div>
      <div class="page-actions">
        ${owner ? `<button class="btn btn-primary" data-add-ing>${icon('plus', { size: 17 })} Add ingredient</button>` : ''}
      </div>
    </div>

    <div class="chips" style="margin-bottom:12px">
      ${TABS.map((t) => `<button class="chip${tab === t.id ? ' active' : ''}" data-tab="${t.id}">
        ${esc(t.label)}</button>`).join('')}
    </div>

    <div id="inv-kpis" class="grid grid-3" style="margin-bottom:12px"></div>
    <div id="inv-body"></div>`;

  const body = $('#inv-body', host);
  const kpis = $('#inv-kpis', host);

  cleanups.push(on(host, 'click', '[data-tab]', (_e, el) => { tab = el.dataset.tab; paintTabs(); paint(); }));
  cleanups.push(on(host, 'click', '[data-add-ing]', () => ingredientEditor(null)));

  const paintTabs = () => {
    host.querySelectorAll('[data-tab]').forEach((b) => b.classList.toggle('active', b.dataset.tab === tab));
  };

  async function paint() {
    body.innerHTML = '<div class="loading-page"><div class="spinner"></div></div>';
    kpis.innerHTML = '';
    try {
      if (tab === 'stock') await paintStock();
      else if (tab === 'history') await paintHistory();
      else await paintSuppliers();
    } catch (err) {
      body.innerHTML = `<div class="card"><div class="empty">${icon('alert', { size: 38, stroke: 1.5 })}
        <h4>Could not load this</h4><p>${esc(err.message)}</p></div></div>`;
    }
  }

  /* ---------------- stock levels ---------------- */

  async function paintStock() {
    const rows = await api.ingredients({ active: '0', q: filter.q });
    const active = rows.filter((r) => r.active);
    const low = active.filter((r) => r.low);
    const value = active.reduce((a, r) => a + Number(r.value || 0), 0);
    const shown = filter.onlyLow ? low : active;

    kpis.innerHTML = `
      ${kpi('Stock lines', num(active.length), `${low.length} below reorder level`, 'box')}
      ${owner ? kpi('Value on shelf', moneyCompact(value, true), 'at current supplier prices', 'wallet') : ''}
      ${kpi('Needs reordering', num(low.length), low.length ? low.slice(0, 2).map((l) => l.name).join(', ') : 'Everything is stocked up', 'alert')}`;

    body.innerHTML = `
      <div class="card" style="margin-bottom:12px">
        <div class="card-body">
          <div class="search-wrap" style="margin-bottom:10px">
            ${icon('search', { size: 17 })}
            <input type="search" id="i-search" placeholder="Search ingredients…" value="${esc(filter.q)}">
          </div>
          <div class="chips">
            <button class="chip${!filter.onlyLow ? ' active' : ''}" data-filter="all">All<span class="count">${active.length}</span></button>
            <button class="chip${filter.onlyLow ? ' active' : ''}" data-filter="low">Low stock<span class="count">${low.length}</span></button>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-head"><h3 class="grow">${filter.onlyLow ? 'Needs reordering' : 'All ingredients'}</h3>
          <span class="small muted">${shown.length}</span></div>
        <div class="card-body tight" id="i-list">
          ${shown.length ? `<div class="list">${shown.map(rowHtml).join('')}</div>`
            : emptyState({ icon: 'box', title: filter.onlyLow ? 'Nothing is running low' : 'No ingredients yet',
              message: filter.onlyLow ? 'Every ingredient is above its reorder level.'
                : 'Add flour, sugar, butter and the rest so recipes can cost themselves.',
              action: owner ? '<button class="btn btn-primary btn-sm" data-add-ing2>Add ingredient</button>' : '' })}
        </div>
      </div>`;

    function rowHtml(r) {
      const ratio = Number(r.reorder_level) > 0
        ? Math.min(1.6, Number(r.stock) / Number(r.reorder_level)) : 1;
      const cls = r.low ? (Number(r.stock) <= 0 ? 'bad' : 'warn') : 'ok';
      return `
        <div class="list-item clickable" data-ing="${r.id}" role="button" tabindex="0">
          <span class="thumb ${r.low ? (Number(r.stock) <= 0 ? 'red' : 'gold') : 'green'}">
            ${icon(r.low ? 'alert' : 'check', { size: 18 })}</span>
          <span class="list-main">
            <span class="list-title">${esc(r.name)}</span>
            <span class="list-sub">
              reorder at ${esc(qty(r.reorder_level))} ${esc(r.unit)}
              ${r.supplier ? ` · ${esc(r.supplier)}` : ''}
              ${r.active ? '' : ' · archived'}
            </span>
            <span class="level ${cls}" style="margin-top:6px;max-width:150px">
              <i style="width:${Math.max(3, (ratio / 1.6) * 100)}%"></i></span>
          </span>
          <span class="list-side">
            <span class="list-amount">${esc(qty(r.stock))} <span class="tiny muted">${esc(r.unit)}</span></span>
            ${owner && r.value !== undefined ? `<span class="badge" style="margin-top:3px">${esc(moneyCompact(r.value, true))}</span>` : ''}
          </span>
        </div>`;
    }

    let t = 0;
    cleanups.push(on(body, 'input', '#i-search', (_e, el) => {
      clearTimeout(t);
      const v = el.value;
      t = setTimeout(() => { filter.q = v; paintStock(); }, 300);
    }));
    cleanups.push(on(body, 'click', '[data-filter]', (_e, el) => { filter.onlyLow = el.dataset.filter === 'low'; paintStock(); }));
    cleanups.push(on(body, 'click', '[data-add-ing2]', () => ingredientEditor(null)));
    cleanups.push(on(body, 'click', '[data-ing]', (_e, el) => {
      const r = rows.find((x) => String(x.id) === el.dataset.ing);
      if (r) ingredientSheet(r);
    }));
  }

  /* ---------------- movements ---------------- */

  async function paintHistory() {
    body.innerHTML = `
      <div class="card" style="margin-bottom:12px"><div class="card-body" id="h-range"></div></div>
      <div class="card">
        <div class="card-head"><h3 class="grow">Stock movements</h3><span class="small muted" id="h-count"></span></div>
        <div class="card-body tight" id="h-list"></div>
      </div>`;

    const loadMoves = async () => {
      const list = $('#h-list', body);
      list.innerHTML = '<div class="loading-page"><div class="spinner"></div></div>';
      try {
        const moves = await api.stockMoves({ from: range.from, to: range.to, limit: 300 });
        $('#h-count', body).textContent = `${moves.length}`;
        if (!moves.length) {
          list.innerHTML = emptyState({ icon: 'list', title: 'No movements in this period',
            message: 'Purchases, recipe usage and waste all show up here.' });
          return;
        }
        list.innerHTML = `<div class="list">${moves.map((m) => `
          <div class="list-item">
            <span class="thumb ${m.kind === 'purchase' ? 'green' : m.kind === 'waste' ? 'red' : m.kind === 'usage' ? 'grey' : 'gold'}">
              ${icon(m.kind === 'purchase' ? 'truck' : m.kind === 'waste' ? 'trash' : m.kind === 'usage' ? 'cart' : 'pencil', { size: 17 })}
            </span>
            <span class="list-main">
              <span class="list-title">${esc(m.ingredient)}</span>
              <span class="list-sub">${esc(kindLabel(m.kind))} · ${esc(dateTime(m.created_at))}${m.ref ? ` · ${esc(m.ref)}` : ''}${m.user ? ` · ${esc(m.user)}` : ''}${m.note ? ` · ${esc(m.note)}` : ''}</span>
            </span>
            <span class="list-side">
              <span class="list-amount" style="color:${Number(m.qty) >= 0 ? 'var(--ok)' : 'var(--bad)'}">
                ${Number(m.qty) >= 0 ? '+' : ''}${esc(qty(m.qty))} <span class="tiny">${esc(m.unit)}</span></span>
            </span>
          </div>`).join('')}</div>`;
      } catch (err) {
        list.innerHTML = emptyState({ icon: 'alert', title: 'Could not load movements', message: err.message });
      }
    };

    cleanups.push(bindRangePicker($('#h-range', body), range, loadMoves));
    await loadMoves();
  }

  /* ---------------- suppliers ---------------- */

  async function paintSuppliers() {
    const [suppliers, ingredients] = await Promise.all([api.suppliers(), api.ingredients({ active: '0' })]);

    kpis.innerHTML = `${kpi('Suppliers', num(suppliers.length), 'who you buy from', 'truck')}`;

    body.innerHTML = `
      <div class="card">
        <div class="card-head"><h3 class="grow">Suppliers</h3>
          ${owner ? '<button class="btn btn-primary btn-sm" data-add-sup>' + icon('plus', { size: 15 }) + ' Add</button>' : ''}</div>
        <div class="card-body tight">
          ${suppliers.length ? `<div class="list">${suppliers.map((s) => {
            const count = ingredients.filter((i) => i.supplier_id === s.id).length;
            return `<div class="list-item clickable" data-sup="${s.id}" role="button" tabindex="0">
              <span class="thumb blue">${icon('truck', { size: 18 })}</span>
              <span class="list-main">
                <span class="list-title">${esc(s.name)}</span>
                <span class="list-sub">${s.phone ? esc(s.phone) : 'No phone'} · ${count} ingredient(s)</span>
                ${s.notes ? `<span class="list-sub">${esc(s.notes)}</span>` : ''}
              </span>
              <span class="list-side">${icon('chevronRight', { size: 18 })}</span>
            </div>`;
          }).join('')}</div>`
          : emptyState({ icon: 'truck', title: 'No suppliers yet',
            message: 'Add the millers, dairy and packaging people you buy from.',
            action: owner ? '<button class="btn btn-primary btn-sm" data-add-sup2>Add supplier</button>' : '' })}
        </div>
      </div>`;

    const open = (s) => supplierEditor(s);
    cleanups.push(on(body, 'click', '[data-add-sup]', () => open(null)));
    cleanups.push(on(body, 'click', '[data-add-sup2]', () => open(null)));
    cleanups.push(on(body, 'click', '[data-sup]', (_e, el) => open(suppliers.find((s) => String(s.id) === el.dataset.sup))));
  }

  /* ---------------- editors ---------------- */

  function ingredientEditor(ing) {
    const isNew = !ing;
    const i = ing || { name: '', unit: 'kg', stock: 0, reorder_level: 0, cost_per_unit: 0, supplier_id: '', active: 1 };
    sheet({
      title: isNew ? 'Add ingredient' : i.name,
      subtitle: isNew ? 'Something you buy to bake with' : `${qty(i.stock)} ${esc(i.unit)} in stock`,
      body: `<form id="i-form">
        <label class="field"><span class="field-label">Name</span>
          <input type="text" name="name" value="${esc(i.name)}" required maxlength="120" placeholder="e.g. Wheat flour"></label>
        <div class="field-row field-row-3">
          <label class="field"><span class="field-label">Unit</span>
            <select name="unit">${['kg', 'g', 'L', 'ml', 'pcs', 'bottle', 'bag', 'box', 'tray', 'dozen']
              .map((u) => `<option value="${u}"${i.unit === u ? ' selected' : ''}>${u}</option>`).join('')}</select></label>
          <label class="field"><span class="field-label">Cost per ${esc(i.unit || 'unit')}</span>
            <input type="number" name="cost_per_unit" min="0" step="1" inputmode="numeric" value="${esc(i.cost_per_unit ?? 0)}"></label>
          <label class="field"><span class="field-label">Reorder at</span>
            <input type="number" name="reorder_level" min="0" step="0.1" inputmode="decimal" value="${esc(i.reorder_level ?? 0)}"></label>
        </div>
        <label class="field"><span class="field-label">Supplier</span>
          <select name="supplier_id" id="i-supplier"><option value="">— None —</option></select></label>
        ${isNew ? `<label class="field"><span class="field-label">Opening stock</span>
          <input type="number" name="stock" min="0" step="0.1" inputmode="decimal" value="0">
          <span class="field-hint">Count what is on the shelf right now. Later changes should go through
          “Record movement” so the history stays honest.</span></label>` : ''}
        <label class="switch"><input type="checkbox" name="active" ${Number(i.active ?? 1) ? 'checked' : ''}>
          <span class="track"></span><span class="switch-text">In use<small>Turn off for ingredients you no longer buy</small></span></label>
      </form>`,
      footer: `${!isNew ? `<button class="btn btn-danger" data-delete style="flex:0 0 auto">${icon('trash', { size: 16 })}</button>` : ''}
        <button class="btn" data-close>Cancel</button>
        <button class="btn btn-primary" data-save>${isNew ? 'Add ingredient' : 'Save'}</button>`,
      onMount: async (el, closeSheet) => {
        try {
          const sups = await api.suppliers();
          const sel = $('#i-supplier', el);
          sel.innerHTML = '<option value="">— None —</option>' + sups.map((s) =>
            `<option value="${s.id}"${String(i.supplier_id) === String(s.id) ? ' selected' : ''}>${esc(s.name)}</option>`).join('');
        } catch { /* supplier list is optional */ }

        on(el, 'click', '[data-save]', async () => {
          const form = $('#i-form', el);
          const d = Object.fromEntries(new FormData(form).entries());
          if (!String(d.name).trim()) return toast('Give it a name', 'warn');
          const btn = $('[data-save]', el);
          busy(btn, true, 'Saving');
          try {
            await api.saveIngredient(isNew ? null : i.id, {
              name: d.name, unit: d.unit, cost_per_unit: Number(d.cost_per_unit) || 0,
              reorder_level: Number(d.reorder_level) || 0, supplier_id: d.supplier_id || null,
              active: form.querySelector('[name=active]').checked ? 1 : 0,
              ...(isNew ? { stock: Number(d.stock) || 0 } : {}),
            });
            invalidate();
            toast(isNew ? `${d.name} added` : 'Saved', 'ok');
            closeSheet();
            paint();
          } catch (err) { busy(btn, false); toast(err.message, 'bad'); }
        });

        if (!isNew) {
          on(el, 'click', '[data-delete]', async () => {
            if (!await confirmDialog({ title: `Remove ${i.name}?`, message: 'If it is used in recipes or has stock history it will be archived instead.', confirmLabel: 'Remove', danger: true })) return;
            try {
              const out = await api.deleteIngredient(i.id);
              invalidate();
              toast(out.archived ? 'Archived — kept for recipe and stock history' : 'Ingredient deleted', 'ok');
              closeSheet(); paint();
            } catch (err) { toast(err.message, 'bad', 4500); }
          });
        }
      },
    });
  }

  /** One ingredient: level, movement form, recent history. */
  function ingredientSheet(ing) {
    const kinds = owner
      ? [['purchase', 'Purchase / delivery', 'truck'], ['adjustment', 'Stock count', 'pencil'],
         ['waste', 'Waste / spoilage', 'trash'], ['usage', 'Used outside a sale', 'cart']]
      : [['usage', 'Used outside a sale', 'cart'], ['waste', 'Waste / spoilage', 'trash']];

    sheet({
      title: ing.name,
      subtitle: `${qty(ing.stock)} ${esc(ing.unit)} in stock${ing.supplier ? ` · ${esc(ing.supplier)}` : ''}`,
      body: `
        ${ing.low ? `<div class="pill-note warn" style="margin-bottom:12px">${icon('alert', { size: 17 })}
          <div>Below the reorder level of ${esc(qty(ing.reorder_level))} ${esc(ing.unit)}.</div></div>` : ''}
        <div class="grid grid-3" style="margin-bottom:14px">
          <div class="kpi"><div class="kpi-label">In stock</div>
            <div class="kpi-value">${esc(qty(ing.stock))}</div><div class="kpi-sub">${esc(ing.unit)}</div></div>
          ${owner ? `<div class="kpi"><div class="kpi-label">Cost per ${esc(ing.unit)}</div>
            <div class="kpi-value">${esc(money(ing.cost_per_unit))}</div><div class="kpi-sub">last paid</div></div>
          <div class="kpi"><div class="kpi-label">Shelf value</div>
            <div class="kpi-value">${esc(moneyCompact(ing.value ?? 0, true))}</div><div class="kpi-sub">stock × cost</div></div>` : ''}
        </div>

        <form id="m-form" class="card" style="box-shadow:none">
          <div class="card-head"><h3>Record a movement</h3></div>
          <div class="card-body">
            <div class="field"><span class="field-label">What happened?</span>
              <div class="pay-grid">
                ${kinds.map(([id, label, ic], idx) => `<button type="button" class="pay-opt${idx === 0 ? ' active' : ''}" data-kind="${id}">
                  ${icon(ic, { size: 19 })}<span style="font-size:11.5px;text-align:center;line-height:1.2">${esc(label)}</span></button>`).join('')}
              </div>
            </div>
            <div class="field-row field-row-2" data-fields>
              <label class="field"><span class="field-label" data-qty-label>Quantity (${esc(ing.unit)})</span>
                <input type="number" name="qty" min="0" step="0.001" inputmode="decimal" placeholder="0"></label>
              <label class="field" data-cost-field><span class="field-label">Cost per ${esc(ing.unit)} paid</span>
                <input type="number" name="unit_cost" min="0" step="1" inputmode="numeric"
                  value="${esc(ing.cost_per_unit ?? 0)}"></label>
            </div>
            <div class="field" data-setto-field style="display:none">
              <span class="field-label">Counted quantity (${esc(ing.unit)})</span>
              <input type="number" name="set_to" step="0.001" inputmode="decimal" placeholder="${esc(String(ing.stock))}">
              <span class="field-hint">Type what you actually counted. The difference is recorded as an adjustment.</span>
            </div>
            <label class="field" style="margin-bottom:0"><span class="field-label">Note (optional)</span>
              <input type="text" name="note" maxlength="200" placeholder="e.g. delivery from Mukase Millers"></label>
          </div>
        </form>

        <div class="divider"></div>
        <h4 style="margin-bottom:8px">Recent movements</h4>
        <div id="m-history"><div class="loading-page" style="padding:20px"><div class="spinner"></div></div></div>`,
      footer: `<button class="btn" data-close>Close</button>
        ${owner ? `<button class="btn" data-edit-ing>${icon('pencil', { size: 16 })} Edit</button>` : ''}
        <button class="btn btn-primary" data-save-move>${icon('check')} Save movement</button>`,
      onMount: async (el, closeSheet) => {
        let kind = kinds[0][0];

        const syncFields = () => {
          const isAdjust = kind === 'adjustment';
          $('[data-setto-field]', el).style.display = isAdjust ? '' : 'none';
          $('[data-qty-label]', el).parentElement.style.display = isAdjust ? 'none' : '';
          const costField = $('[data-cost-field]', el);
          if (costField) costField.style.display = kind === 'purchase' ? '' : 'none';
          el.querySelectorAll('[data-kind]').forEach((b) => b.classList.toggle('active', b.dataset.kind === kind));
        };
        syncFields();

        on(el, 'click', '[data-kind]', (_e, btn) => { kind = btn.dataset.kind; syncFields(); });

        const hist = $('#m-history', el);
        try {
          const moves = await api.stockMoves({ ingredient_id: ing.id, limit: 12 });
          hist.innerHTML = moves.length ? `<div class="list">${moves.map((m) => `
            <div class="list-item">
              <span class="list-main">
                <span class="list-title">${esc(kindLabel(m.kind))}</span>
                <span class="list-sub">${esc(dateTime(m.created_at))}${m.ref ? ` · ${esc(m.ref)}` : ''}${m.note ? ` · ${esc(m.note)}` : ''}</span>
              </span>
              <span class="list-side"><span class="list-amount" style="color:${Number(m.qty) >= 0 ? 'var(--ok)' : 'var(--bad)'}">
                ${Number(m.qty) >= 0 ? '+' : ''}${esc(qty(m.qty))}</span></span>
            </div>`).join('')}</div>`
            : '<p class="small muted">No movements recorded yet.</p>';
        } catch (err) { hist.innerHTML = `<p class="small muted">${esc(err.message)}</p>`; }

        on(el, 'click', '[data-edit-ing]', () => { closeSheet(); ingredientEditor(ing); });

        on(el, 'click', '[data-save-move]', async () => {
          const form = $('#m-form', el);
          const d = Object.fromEntries(new FormData(form).entries());
          const payload = { kind, note: d.note || null };
          if (kind === 'adjustment') {
            if (d.set_to === '' || d.set_to === null) return toast('Enter the counted quantity', 'warn');
            payload.set_to = Number(d.set_to);
          } else {
            if (!(Number(d.qty) > 0)) return toast('Enter a quantity above zero', 'warn');
            payload.qty = Number(d.qty);
          }
          if (kind === 'purchase') payload.unit_cost = Number(d.unit_cost) || 0;

          const btn = $('[data-save-move]', el);
          busy(btn, true, 'Saving');
          try {
            const out = await api.stockMove(ing.id, payload);
            invalidate();
            const dir = Number(out.signed) >= 0 ? 'in' : 'out';
            toast(`Stock ${dir}: now ${qty(out.stock)} ${ing.unit}${out.cost_updated ? ' · cost per unit updated' : ''}`, 'ok', 3800);
            closeSheet();
            paint();
          } catch (err) { busy(btn, false); toast(err.message, 'bad'); }
        });
      },
    });
  }

  function supplierEditor(sup) {
    const isNew = !sup;
    const s = sup || { name: '', phone: '', notes: '' };
    sheet({
      title: isNew ? 'Add supplier' : s.name,
      body: `<form id="s-form">
        <label class="field"><span class="field-label">Name</span>
          <input type="text" name="name" value="${esc(s.name)}" required maxlength="120" placeholder="e.g. Mukase Millers"></label>
        <label class="field"><span class="field-label">Phone</span>
          <input type="tel" name="phone" value="${esc(s.phone ?? '')}" maxlength="40" inputmode="tel" placeholder="+257 …"></label>
        <label class="field" style="margin-bottom:0"><span class="field-label">Notes</span>
          <textarea name="notes" maxlength="400" placeholder="Delivery days, payment terms…">${esc(s.notes ?? '')}</textarea></label>
      </form>`,
      footer: `${!isNew ? `<button class="btn btn-danger" data-delete style="flex:0 0 auto">${icon('trash', { size: 16 })}</button>` : ''}
        <button class="btn" data-close>Cancel</button>
        <button class="btn btn-primary" data-save>${isNew ? 'Add supplier' : 'Save'}</button>`,
      onMount: (el, closeSheet) => {
        on(el, 'click', '[data-save]', async () => {
          const d = Object.fromEntries(new FormData($('#s-form', el)).entries());
          if (!String(d.name).trim()) return toast('Give the supplier a name', 'warn');
          const btn = $('[data-save]', el);
          busy(btn, true, 'Saving');
          try {
            await api.saveSupplier(isNew ? null : s.id, d);
            invalidate();
            toast(isNew ? 'Supplier added' : 'Supplier saved', 'ok');
            closeSheet(); paint();
          } catch (err) { busy(btn, false); toast(err.message, 'bad'); }
        });
        if (!isNew) {
          on(el, 'click', '[data-delete]', async () => {
            if (!await confirmDialog({ title: `Delete ${s.name}?`, confirmLabel: 'Delete', danger: true })) return;
            try { await api.deleteSupplier(s.id); toast('Supplier deleted', 'ok'); closeSheet(); paint(); }
            catch (err) { toast(err.message, 'bad', 4500); }
          });
        }
      },
    });
  }

  const kpi = (label, value, sub, ic) => `
    <div class="kpi"><span class="kpi-icon">${icon(ic, { size: 32, stroke: 1.6 })}</span>
      <div class="kpi-label">${esc(label)}</div><div class="kpi-value">${esc(value)}</div>
      <div class="kpi-sub">${esc(sub)}</div></div>`;

  await paint();

  return () => cleanups.forEach((fn) => { try { fn?.(); } catch { /* ignore */ } });
}
