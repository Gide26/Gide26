/**
 * Products, pricing and recipes. The recipe editor is the costing engine:
 * it turns ingredient quantities into a unit cost and shows the margin
 * live, so the owner can price by margin instead of by guesswork.
 */
import { api } from '../api.js';
import { state, isOwner, loadData, invalidate } from '../store.js';
import { icon, $, on, toast, busy, sheet, emptyState, confirmDialog } from '../ui.js';
import { money, num, qty, esc } from '../format.js';
import { getCache, enqueue, makeRef } from '../offline.js';
import { pendingPanel } from '../pending.js';

export async function render(host) {
  const owner = isOwner();
  let products = [];
  let categories = [];
  // True when the list came from the offline snapshot rather than the server.
  let offlineList = false;
  let ingredients = [];
  const filter = { q: '', category: 'all' };

  host.innerHTML = `
    <div class="page-head">
      <div class="grow">
        <h1>Products</h1>
        <div class="small muted">${owner ? 'Prices, recipes and what each item costs you.' : 'What you can sell today.'}</div>
      </div>
      <div class="page-actions">
        ${owner ? `<button class="btn" data-manage-cats>${icon('tag', { size: 16 })} Categories</button>
        <button class="btn btn-primary" data-add>${icon('plus', { size: 17 })} Add product</button>` : ''}
      </div>
    </div>

    <div id="p-offline-note" style="margin-bottom:12px"></div>
    <div id="p-queued" style="margin-bottom:12px"></div>

    <div class="card" style="margin-bottom:12px">
      <div class="card-body">
        <div class="search-wrap" style="margin-bottom:10px">
          ${icon('search', { size: 17 })}
          <input type="search" id="p-search" placeholder="Search products…" aria-label="Search products">
        </div>
        <div class="chips" id="p-chips"></div>
      </div>
    </div>

    <div class="card">
      <div class="card-head"><h3 class="grow" id="p-heading">Products</h3><span class="small muted" id="p-count"></span></div>
      <div class="card-body tight" id="p-list"></div>
    </div>`;

  const list = $('#p-list', host);

  async function load() {
    try {
      const [prods, data] = await Promise.all([api.products({ active: '0' }), loadData()]);
      products = prods;
      categories = data.categories || [];
      ingredients = owner ? (data.ingredients || []) : [];
      offlineList = false;
    } catch (err) {
      // Offline: fall back to the bootstrap snapshot so prices can still be
      // corrected at the counter. Costs in the snapshot are only as fresh as the
      // last sync, which is why the screen says so.
      const cached = await getCache('bootstrap');
      if (!cached?.products) throw err;
      products = cached.products;
      categories = cached.categories || [];
      ingredients = owner ? (cached.ingredients || []) : [];
      offlineList = true;
    }
    paint();
  }

  function visible() {
    const q = filter.q.trim().toLowerCase();
    return products.filter((p) => {
      if (filter.category !== 'all' && (p.category || 'Other') !== filter.category) return false;
      return !q || p.name.toLowerCase().includes(q);
    });
  }

  function paint() {
    const noteHost = $('#p-offline-note', host);
    if (noteHost) {
      noteHost.innerHTML = offlineList ? `<div class="pill-note">${icon('wifiOff', { size: 17 })}
        <div><strong>Offline.</strong> These products and prices are from your last sync, so a cost
        figure may be out of date. You can still correct a price or remove a product — the change is
        queued here and applied when you reconnect. Adding a brand-new product needs a connection.</div></div>` : '';
    }

    const counts = new Map();
    for (const p of products) {
      const k = p.category || 'Other';
      counts.set(k, (counts.get(k) || 0) + 1);
    }
    $('#p-chips', host).innerHTML =
      `<button class="chip${filter.category === 'all' ? ' active' : ''}" data-cat="all">All<span class="count">${products.length}</span></button>`
      + categories.filter((c) => counts.get(c.name)).map((c) =>
        `<button class="chip${filter.category === c.name ? ' active' : ''}" data-cat="${esc(c.name)}">${esc(c.name)}<span class="count">${counts.get(c.name)}</span></button>`).join('')
      + (counts.get('Other') ? `<button class="chip${filter.category === 'Other' ? ' active' : ''}" data-cat="Other">Other<span class="count">${counts.get('Other')}</span></button>` : '');

    const rows = visible();
    $('#p-count', host).textContent = `${rows.length} of ${products.length}`;

    if (!rows.length) {
      list.innerHTML = emptyState({
        icon: 'tag', title: 'No products yet',
        message: 'Add the breads, cakes and drinks you sell so the till has something to show.',
        action: owner ? '<button class="btn btn-primary btn-sm" data-add-empty>Add your first product</button>' : '',
      });
      return;
    }

    list.innerHTML = `<div class="list">${rows.map((p) => `
      <div class="list-item clickable" data-edit="${p.id}" role="button" tabindex="0">
        <span class="thumb ${p.active ? '' : 'grey'}">${icon(p.has_recipe ? 'flask' : 'tag', { size: 18 })}</span>
        <span class="list-main">
          <span class="list-title">${esc(p.name)}${p.active ? '' : ' <span class="badge">archived</span>'}</span>
          <span class="list-sub">
            ${esc(p.category || 'Uncategorised')}
            ${p.has_recipe ? ' · recipe set' : owner ? ' · <span style="color:var(--warn)">no recipe</span>' : ''}
          </span>
        </span>
        <span class="list-side">
          <span class="list-amount">${esc(money(p.price))}</span>
          ${owner && p.unit_cost !== undefined ? `
            <span class="badge ${p.margin_pct >= 50 ? 'ok' : p.margin_pct >= 30 ? 'warn' : 'bad'}" style="margin-top:3px">
              ${esc(money(p.margin))} · ${num(p.margin_pct, 0)}%</span>` : ''}
        </span>
      </div>`).join('')}</div>`;
  }

  const offs = [];
  offs.push(on(host, 'input', '#p-search', (_e, el) => { filter.q = el.value; paint(); }));
  offs.push(on(host, 'click', '[data-cat]', (_e, el) => { filter.category = el.dataset.cat; paint(); }));
  offs.push(on(host, 'click', '[data-add]', () => editor(null)));
  offs.push(pendingPanel($('#p-queued', host), { kinds: ['product'], title: 'Product changes queued on this device' }));
  offs.push(on(host, 'click', '[data-add-empty]', () => editor(null)));
  offs.push(on(host, 'click', '[data-manage-cats]', () => categoriesSheet()));
  offs.push(on(host, 'click', '[data-edit]', async (_e, el) => {
    if (!owner) return;
    try { editor(await api.product(el.dataset.edit)); }
    catch (err) { toast(err.message, 'bad'); }
  }));

  try { await load(); }
  catch (err) {
    list.innerHTML = emptyState({ icon: 'alert', title: 'Could not load products', message: err.message });
  }

  /* ---------------- product editor ---------------- */

  function editor(product) {
    const isNew = !product;
    const p = product || { name: '', price: '', category_id: '', cost: '', active: 1, recipe: [] };
    const close = sheet({
      title: isNew ? 'Add product' : p.name,
      subtitle: isNew ? 'Something you sell' : `${esc(p.category || 'Uncategorised')}`,
      body: `
        <form id="p-form">
          <label class="field">
            <span class="field-label">Name</span>
            <input type="text" name="name" value="${esc(p.name)}" required maxlength="120" placeholder="e.g. Bread loaf">
          </label>
          <div class="field-row field-row-2">
            <label class="field">
              <span class="field-label">Category</span>
              <select name="category_id">
                <option value="">— None —</option>
                ${categories.map((c) => `<option value="${c.id}"${String(p.category_id) === String(c.id) ? ' selected' : ''}>${esc(c.name)}</option>`).join('')}
              </select>
            </label>
            <label class="field">
              <span class="field-label">Selling price (${esc(state.settings.currency_symbol || '')})</span>
              <input type="number" name="price" min="0" step="1" inputmode="numeric" value="${esc(p.price ?? '')}" required>
            </label>
          </div>
          <label class="field">
            <span class="field-label">Manual unit cost (optional)</span>
            <input type="number" name="cost" min="0" step="1" inputmode="numeric" value="${esc(p.cost ?? '')}"
              placeholder="Calculated from the recipe instead">
            <span class="field-hint">Only used when the product has no recipe. A recipe is more accurate because it
              follows ingredient prices.</span>
          </label>
          <label class="switch" style="margin-bottom:6px">
            <input type="checkbox" name="active" ${Number(p.active ?? 1) ? 'checked' : ''}>
            <span class="track"></span>
            <span class="switch-text">On sale<small>Turn off to hide it from the till without losing history</small></span>
          </label>
        </form>
        ${!isNew && p.unit_cost !== undefined ? `
          <div class="divider"></div>
          <div class="pill-note info">${icon('flask', { size: 17 })}
            <div class="grow">
              Recipe cost <strong>${esc(money(p.unit_cost))}</strong> ·
              margin <strong>${esc(money(p.margin))}</strong> (${num(p.margin_pct, 1)}%)
            </div>
            <button class="btn btn-sm" data-recipe>Edit recipe</button>
          </div>` : ''}`,
      footer: `
        ${!isNew ? `<button class="btn btn-danger" data-delete style="flex:0 0 auto">${icon('trash', { size: 16 })}</button>` : ''}
        <button class="btn" data-close>Cancel</button>
        <button class="btn btn-primary" data-save>${isNew ? 'Add product' : 'Save changes'}</button>`,
      onMount: (el, closeSheet) => {
        on(el, 'click', '[data-save]', async () => {
          const form = $('#p-form', el);
          const data = Object.fromEntries(new FormData(form).entries());
          if (!String(data.name || '').trim()) return toast('Give the product a name', 'warn');
          const btn = $('[data-save]', el);
          busy(btn, true, 'Saving');
          try {
            const payload = {
              name: data.name,
              category_id: data.category_id || null,
              price: Number(data.price) || 0,
              cost: data.cost === '' ? null : Number(data.cost),
              active: form.querySelector('[name=active]').checked ? 1 : 0,
            };
            const offline = typeof navigator !== 'undefined' && navigator.onLine === false;

            // Creating a product offline is refused rather than queued: a new
            // product has no server-side identity yet, and two devices inventing
            // one each would produce duplicates that no idempotency key can
            // reconcile. Editing an existing one is safe, so that is allowed.
            if (offline && isNew) {
              busy(btn, false);
              return toast('Adding a new product needs a connection. Editing existing ones works offline.', 'warn', 6000);
            }
            if (offline) {
              await enqueue('product:update', { id: p.id, ...payload, base_updated_at: p.updated_at || null },
                { label: `${payload.name} · ${money(payload.price)}` });
              invalidate();
              toast('Price change saved on this device — it will send when you reconnect', 'ok', 4600);
              closeSheet();
              await load();
              return;
            }

            await api.saveProduct(isNew ? null : p.id, isNew ? payload
              : { ...payload, client_ref: makeRef('prd'), base_updated_at: p.updated_at || null });
            invalidate();
            toast(isNew ? `${payload.name} added` : 'Product saved', 'ok');
            closeSheet();
            await load();
          } catch (err) {
            busy(btn, false);
            if (err?.status === 409) {
              toast('That product changed on the server — reload and try again', 'warn', 6000);
              closeSheet(); await load();
              return;
            }
            if (!isNew && (err?.offline || err?.status === 0)) {
              try {
                await enqueue('product:update', { id: p.id, name: data.name, category_id: data.category_id || null,
                  price: Number(data.price) || 0, cost: data.cost === '' ? null : Number(data.cost),
                  active: form.querySelector('[name=active]').checked ? 1 : 0,
                  base_updated_at: p.updated_at || null, client_ref: makeRef('prd') },
                  { label: `${data.name} · ${money(Number(data.price) || 0)}` });
                toast('Connection lost — that change is queued on this device instead', 'warn', 5200);
                closeSheet();
                return;
              } catch { /* fall through to the plain error */ }
            }
            toast(err.message, 'bad');
          }
        });

        on(el, 'click', '[data-recipe]', () => { closeSheet(); recipeEditor(p.id, p.name); });

        if (!isNew) {
          on(el, 'click', '[data-delete]', async () => {
            const ok = await confirmDialog({
              title: `Remove ${p.name}?`,
              message: 'If it has been sold before, it is archived instead of deleted so your reports stay correct.',
              confirmLabel: 'Remove', danger: true,
            });
            if (!ok) return;
            const offline = typeof navigator !== 'undefined' && navigator.onLine === false;
            if (offline) {
              try {
                await enqueue('product:delete', { id: p.id, base_updated_at: p.updated_at || null },
                  { label: p.name });
                invalidate();
                toast('Removal queued — it will apply when you reconnect', 'ok', 4600);
                closeSheet(); await load();
              } catch (err2) { toast(`Could not queue that: ${err2.message || ''}`, 'bad', 6000); }
              return;
            }
            try {
              const out = await api.deleteProduct(p.id, { client_ref: makeRef('prd'), base_updated_at: p.updated_at || null });
              invalidate();
              toast(out.archived ? 'Archived — kept for sales history' : 'Product deleted', 'ok');
              closeSheet();
              await load();
            } catch (err) {
              if (err?.status === 409) {
                toast('That product changed on the server — reload and try again', 'warn', 6000);
                closeSheet(); await load();
                return;
              }
              toast(err.message, 'bad');
            }
          });
        }
      },
    });
    return close;
  }

  /* ---------------- recipe / costing editor ---------------- */

  async function recipeEditor(productId, productName) {
    let product;
    try { product = await api.product(productId); }
    catch (err) { return toast(err.message, 'bad'); }

    const chosen = new Map((product.recipe || []).map((r) => [r.ingredient_id, Number(r.qty)]));
    const ingById = new Map(ingredients.map((i) => [i.id, i]));

    const costNow = () => {
      let c = 0;
      for (const [id, q] of chosen) c += Number(q) * Number(ingById.get(id)?.cost_per_unit ?? 0);
      return Math.round(c * 100) / 100;
    };

    const summaryHtml = () => {
      const cost = costNow();
      const price = Number(product.price) || 0;
      const margin = price - cost;
      const pctMargin = price ? (margin / price) * 100 : 0;
      const tone = pctMargin >= 50 ? 'ok' : pctMargin >= 30 ? 'warn' : 'bad';
      return `
        <div class="pill-note ${tone}" style="align-items:center">
          ${icon('flask', { size: 18 })}
          <div class="grow">
            <div class="tiny" style="opacity:.8">Cost to make one</div>
            <div class="strong" style="font-size:17px">${esc(money(cost))}</div>
          </div>
          <div style="text-align:right">
            <div class="tiny" style="opacity:.8">Margin at ${esc(money(price))}</div>
            <div class="strong" style="font-size:17px">${esc(money(margin))} · ${num(pctMargin, 0)}%</div>
          </div>
        </div>
        <div class="row wrap" style="gap:7px;margin-top:9px">
          <span class="tiny muted">Suggest a price for:</span>
          ${[50, 60, 65, 70].map((m) => `<button class="btn btn-sm" data-suggest="${m}">${m}% margin</button>`).join('')}
        </div>`;
    };

    const rowsHtml = () => `
      <div class="table-wrap">
        <table class="data">
          <thead><tr>
            <th>Ingredient</th><th class="num">Cost / unit</th>
            <th class="num" style="min-width:132px">Qty per ${esc(productName)}</th><th class="num">Cost</th>
          </tr></thead>
          <tbody>
            ${ingredients.map((i) => {
              const v = chosen.get(i.id);
              return `<tr>
                <td>${esc(i.name)} <span class="muted tiny">(${esc(i.unit)})</span></td>
                <td class="num muted">${esc(money(i.cost_per_unit))}</td>
                <td class="num">
                  <input type="number" min="0" step="0.001" inputmode="decimal" data-ing="${i.id}"
                    value="${v ?? ''}" placeholder="—" style="min-height:36px;text-align:right;padding:6px 8px">
                </td>
                <td class="num strong">${v ? esc(money(Number(v) * Number(i.cost_per_unit))) : '<span class="muted">—</span>'}</td>
              </tr>`;
            }).join('')}
          </tbody>
        </table>
      </div>`;

    const close = sheet({
      title: 'Recipe & costing',
      subtitle: productName,
      wide: true,
      body: `<div id="r-summary">${summaryHtml()}</div>
        <div class="divider"></div>
        <p class="small muted">Enter how much of each ingredient goes into <strong>one</strong>
        ${esc(productName)}. Fractions are fine — a shared paper bag might be 0.5.</p>
        <div id="r-rows">${rowsHtml()}</div>`,
      footer: `
        <button class="btn" data-close>Cancel</button>
        <button class="btn btn-primary" data-save-recipe>${icon('check')} Save recipe</button>`,
      onMount: (el, closeSheet) => {
        const live = () => {
          $('#r-summary', el).innerHTML = summaryHtml();
          // refresh only the per-line cost cells, keeping input focus intact
          ingredients.forEach((i) => {
            const cell = el.querySelector(`[data-cost-cell="${i.id}"]`);
            if (cell) cell.textContent = chosen.get(i.id) ? money(Number(chosen.get(i.id)) * Number(i.cost_per_unit)) : '—';
          });
        };

        on(el, 'input', '[data-ing]', (_e, input) => {
          const id = Number(input.dataset.ing);
          const v = Number(input.value);
          if (!input.value || !(v > 0)) chosen.delete(id);
          else chosen.set(id, v);
          // Update this row's cost + the summary without a full re-render.
          const row = input.closest('tr');
          const costCell = row?.querySelector('td:last-child');
          if (costCell) {
            const ing = ingById.get(id);
            costCell.innerHTML = chosen.get(id)
              ? `<span class="strong">${esc(money(Number(chosen.get(id)) * Number(ing?.cost_per_unit ?? 0)))}</span>`
              : '<span class="muted">—</span>';
          }
          $('#r-summary', el).innerHTML = summaryHtml();
        });

        on(el, 'click', '[data-suggest]', (_e, btn) => {
          const target = Number(btn.dataset.suggest) / 100;
          const cost = costNow();
          if (cost <= 0) return toast('Add ingredients first', 'warn');
          const suggested = Math.ceil(cost / (1 - target) / 50) * 50;
          const ok = window.confirm(
            `At a ${btn.dataset.suggest}% margin, ${productName} should sell for ${money(suggested)}.\n\n`
            + `Change the selling price from ${money(product.price)} to ${money(suggested)}?`);
          if (!ok) return;
          api.saveProduct(product.id, { price: suggested }).then(async () => {
            product.price = suggested;
            invalidate();
            toast(`Price updated to ${money(suggested)}`, 'ok');
            $('#r-summary', el).innerHTML = summaryHtml();
          }).catch((err) => toast(err.message, 'bad'));
        });

        on(el, 'click', '[data-save-recipe]', async () => {
          const btn = $('[data-save-recipe]', el);
          busy(btn, true, 'Saving');
          try {
            const lines = [...chosen.entries()].map(([ingredient_id, q]) => ({ ingredient_id, qty: q }));
            const out = await api.saveRecipe(product.id, lines);
            invalidate();
            toast(lines.length
              ? `Recipe saved — costs ${money(out.unit_cost)}, margin ${num(out.margin_pct, 0)}%`
              : 'Recipe cleared', 'ok', 4000);
            closeSheet();
            await load();
          } catch (err) { busy(btn, false); toast(err.message, 'bad'); }
        });
      },
    });
    return close;
  }

  /* ---------------- categories ---------------- */

  async function categoriesSheet() {
    const fresh = await api.categories();
    const close = sheet({
      title: 'Categories',
      subtitle: 'How products are grouped on the till',
      body: `
        <div class="list" id="cat-list">${fresh.map((c) => `
          <div class="list-item">
            <span class="thumb grey">${icon('tag', { size: 17 })}</span>
            <span class="list-main"><span class="list-title">${esc(c.name)}</span></span>
            <button class="btn btn-ghost btn-icon btn-sm" data-cat-del="${c.id}" aria-label="Delete ${esc(c.name)}">${icon('trash', { size: 16 })}</button>
          </div>`).join('') || '<div class="empty"><p>No categories yet</p></div>'}</div>
        <div class="divider"></div>
        <form id="cat-form" class="row" style="gap:8px">
          <input type="text" name="name" placeholder="New category name" maxlength="60" style="flex:1 1 auto">
          <button class="btn btn-primary" type="submit">${icon('plus')} Add</button>
        </form>`,
      onMount: (el, closeSheet) => {
        on(el, 'submit', '#cat-form', async (e) => {
          e.preventDefault();
          const input = el.querySelector('[name=name]');
          const name = input.value.trim();
          if (!name) return;
          try {
            await api.saveCategory(null, { name });
            toast(`Category "${name}" added`, 'ok');
            closeSheet();
            invalidate();
            categoriesSheet();
          } catch (err) { toast(err.message, 'bad'); }
        });
        on(el, 'click', '[data-cat-del]', async (_e, btn) => {
          if (!await confirmDialog({ title: 'Delete this category?', message: 'Products in it become uncategorised.', confirmLabel: 'Delete', danger: true })) return;
          try {
            await api.deleteCategory(btn.dataset.catDel);
            toast('Category deleted', 'ok');
            closeSheet();
            invalidate();
            categoriesSheet();
          } catch (err) { toast(err.message, 'bad', 4500); }
        });
      },
    });
    return close;
  }

  return () => offs.forEach((off) => { try { off(); } catch { /* ignore */ } });
}

export { qty };
