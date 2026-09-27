/**
 * Expenses: every cost that is not an ingredient — rent, salaries, power,
 * transport. These are what turn gross profit into the real number.
 */
import { api } from '../api.js';
import { state, isOwner, invalidate } from '../store.js';
import { icon, $, on, toast, busy, sheet, emptyState, confirmDialog,
  bindRangePicker, defaultRange } from '../ui.js';
import { money, moneyCompact, num, esc, dateTime, dateOnly, todayStr, localStamp } from '../format.js';
import { enqueue, makeRef, putCache, getCache, cacheAge } from '../offline.js';
import { pendingPanel } from '../pending.js';
import { hbars } from '../charts.js';

export async function render(host) {
  const owner = isOwner();
  const range = { ...defaultRange() };
  const filter = { category: '', q: '' };
  const cleanups = [];
  // True when the list on screen came from the offline snapshot rather than the
  // server. Edits are still allowed; they are queued with the stamp we last saw.
  let offlineList = false;

  host.innerHTML = `
    <div class="page-head">
      <div class="grow">
        <h1>Expenses</h1>
        <div class="small muted">${owner ? 'Every cost that eats into your profit.' : 'Costs you have recorded.'}</div>
      </div>
      <div class="page-actions">
        <button class="btn btn-primary" data-add>${icon('plus', { size: 17 })} Add expense</button>
      </div>
    </div>

    <div id="e-queued" style="margin-bottom:12px"></div>

    <div class="card" style="margin-bottom:12px"><div class="card-body" id="e-range"></div></div>

    <div class="grid grid-3" id="e-kpis" style="margin-bottom:12px"></div>

    <div class="grid grid-2">
      <div class="card">
        <div class="card-head"><h3 class="grow">Where it went</h3></div>
        <div class="card-body" id="e-split"></div>
      </div>
      <div class="card">
        <div class="card-head">
          <h3 class="grow">Records</h3>
          <select id="e-cat" style="min-height:34px;width:auto;font-size:13px" aria-label="Filter by category">
            <option value="">All categories</option>
          </select>
        </div>
        <div class="card-body tight" id="e-list"></div>
      </div>
    </div>`;

  const kpis = $('#e-kpis', host);
  const split = $('#e-split', host);
  const list = $('#e-list', host);

  cleanups.push(bindRangePicker($('#e-range', host), range, load));
  cleanups.push(on(host, 'click', '[data-add]', () => editor(null)));
  cleanups.push(on(host, 'change', '#e-cat', (_e, el) => { filter.category = el.value; paint(); }));
  cleanups.push(pendingPanel($('#e-queued', host), { kinds: ['expense'], title: 'Expense changes queued on this device' }));

  let cache = { expenses: [], totals: { count: 0, total: 0 }, categories: [] };

  async function load() {
    list.innerHTML = '<div class="loading-page" style="padding:26px"><div class="spinner"></div></div>';
    try {
      cache = await api.expenses({ from: range.from, to: range.to });
      offlineList = false;
      // Snapshot so the records stay visible — and therefore editable — offline.
      putCache('expenses', { ...cache, _range: { ...range }, _at: Date.now() });
      const sel = $('#e-cat', host);
      const current = filter.category;
      sel.innerHTML = '<option value="">All categories</option>'
        + (cache.categories || []).map((c) => `<option value="${esc(c)}"${c === current ? ' selected' : ''}>${esc(c)}</option>`).join('');
      paint();
    } catch (err) {
      const saved = await getCache('expenses');
      if (saved && Array.isArray(saved.expenses)) {
        cache = saved;
        offlineList = true;
        paint();
        return;
      }
      list.innerHTML = emptyState({ icon: 'alert', title: 'Could not load expenses', message: err.message });
    }
  }

  function paint() {
    const rows = cache.expenses.filter((e) => !filter.category || e.category === filter.category);
    const total = rows.reduce((a, e) => a + Number(e.amount), 0);

    if (offlineList) {
      const since = cache._at ? localStamp(new Date(cache._at)) : 'an earlier visit';
      const note = $('#e-offline-note', host) || (() => {
        const d = document.createElement('div');
        d.id = 'e-offline-note';
        d.style.marginBottom = '12px';
        kpis.parentNode.insertBefore(d, kpis);
        return d;
      })();
      note.innerHTML = `<div class="pill-note">${icon('wifiOff', { size: 17 })}
        <div><strong>Offline.</strong> These are the expenses saved at your last sync (${esc(since)}),
        not the live list. You can still add, edit and delete — each change is queued on this
        device and applied when you reconnect. If someone else changed one of these in the
        meantime, you will be asked which version to keep rather than having it overwritten.</div></div>`;
    } else {
      $('#e-offline-note', host)?.remove();
    }

    kpis.innerHTML = `
      ${kpi('Total spent', moneyCompact(total, true), `${dateOnly(range.from)} – ${dateOnly(range.to)}`, 'wallet')}
      ${kpi('Records', num(rows.length), rows.length ? `avg ${money(total / rows.length)}` : 'Nothing recorded', 'list')}
      ${kpi('Per day', moneyCompact(range.from === range.to ? total : total / Math.max(1, daysBetween(range.from, range.to)), true),
        'across the selected period', 'clock')}`;

    const byCat = new Map();
    for (const e of cache.expenses) byCat.set(e.category, (byCat.get(e.category) || 0) + Number(e.amount));
    const catRows = [...byCat.entries()].sort((a, b) => b[1] - a[1]);
    split.innerHTML = catRows.length
      ? hbars(catRows.map(([label, value]) => ({ label, value })), { valueFormat: (v) => moneyCompact(v, true) })
      : emptyState({ icon: 'wallet', title: 'No expenses yet', message: 'Add rent, power, transport and salaries to see your true profit.' });

    if (!rows.length) {
      list.innerHTML = emptyState({ icon: 'wallet', title: 'Nothing recorded',
        message: 'Tap “Add expense” to record a cost.',
        action: '<button class="btn btn-primary btn-sm" data-add2>Add expense</button>' });
      return;
    }

    list.innerHTML = `<div class="list">${rows.map((e) => `
      <div class="list-item clickable" data-exp="${e.id}" role="button" tabindex="0">
        <span class="thumb gold">${icon(catIcon(e.category), { size: 18 })}</span>
        <span class="list-main">
          <span class="list-title">${esc(e.title)}</span>
          <span class="list-sub">${esc(e.category)} · ${esc(dateTime(e.expense_at))}${e.recorded_by ? ` · ${esc(e.recorded_by)}` : ''}</span>
        </span>
        <span class="list-side"><span class="list-amount">−${esc(money(e.amount))}</span></span>
      </div>`).join('')}</div>`;
  }

  const catIcon = (c) => ({
    Rent: 'store', Utilities: 'flask', Salaries: 'users', Transport: 'truck',
    Equipment: 'settings', Repairs: 'settings', Marketing: 'star', Permits: 'shield',
    Packaging: 'box', Ingredients: 'box',
  }[c] || 'wallet');

  const kpi = (label, value, sub, ic) => `
    <div class="kpi"><span class="kpi-icon">${icon(ic, { size: 32, stroke: 1.6 })}</span>
      <div class="kpi-label">${esc(label)}</div><div class="kpi-value">${esc(value)}</div>
      <div class="kpi-sub">${esc(sub)}</div></div>`;

  function editor(expense) {
    const isNew = !expense;
    const e = expense || { title: '', category: 'Other', amount: '', note: '', expense_at: `${todayStr()} 12:00:00` };
    const cats = cache.categories?.length ? cache.categories
      : ['Rent', 'Utilities', 'Salaries', 'Transport', 'Equipment', 'Ingredients', 'Packaging', 'Marketing', 'Permits', 'Repairs', 'Other'];

    sheet({
      title: isNew ? 'Add expense' : 'Edit expense',
      subtitle: isNew ? 'Anything you paid out that was not stock' : e.title,
      body: `<form id="e-form">
        <label class="field"><span class="field-label">What did you pay for?</span>
          <input type="text" name="title" value="${esc(e.title)}" required maxlength="160" placeholder="e.g. Electricity bill"></label>
        <div class="field-row field-row-2">
          <label class="field"><span class="field-label">Amount (${esc(state.settings.currency_symbol || '')})</span>
            <input type="number" name="amount" min="0" step="1" inputmode="numeric" value="${esc(e.amount ?? '')}" required></label>
          <label class="field"><span class="field-label">Category</span>
            <select name="category">${cats.map((c) => `<option value="${esc(c)}"${e.category === c ? ' selected' : ''}>${esc(c)}</option>`).join('')}
            </select></label>
        </div>
        <label class="field"><span class="field-label">Date</span>
          <input type="date" name="date" value="${esc(String(e.expense_at || '').slice(0, 10))}" max="${esc(todayStr())}"></label>
        <label class="field" style="margin-bottom:0"><span class="field-label">Note (optional)</span>
          <input type="text" name="note" value="${esc(e.note ?? '')}" maxlength="300" placeholder="e.g. September, meter 4412"></label>
      </form>`,
      footer: `${!isNew ? `<button class="btn btn-danger" data-delete style="flex:0 0 auto">${icon('trash', { size: 16 })}</button>` : ''}
        <button class="btn" data-close>Cancel</button>
        <button class="btn btn-primary" data-save>${isNew ? 'Save expense' : 'Save changes'}</button>`,
      onMount: (el, closeSheet) => {
        on(el, 'click', '[data-save]', async () => {
          const form = $('#e-form', el);
          const d = Object.fromEntries(new FormData(form).entries());
          if (!String(d.title).trim()) return toast('What was it for?', 'warn');
          if (!(Number(d.amount) > 0)) return toast('Enter an amount above zero', 'warn');
          const btn = $('[data-save]', el);
          const payload = {
            title: d.title, amount: Number(d.amount), category: d.category,
            note: d.note || null, expense_at: d.date ? `${d.date} 12:00:00` : localStamp(),
          };
          const isOffline = typeof navigator !== 'undefined' && navigator.onLine === false;

          if (isOffline && !isNew) {
            // Queue the edit against the stamp we last saw. If the record moved on
            // while we were offline the server refuses it and the pending panel
            // asks which version to keep — it never guesses.
            busy(btn, true, 'Saving');
            try {
              await enqueue('expense:update', {
                id: e.id, ...payload, base_updated_at: e.updated_at || null,
              }, { label: `${d.title} · ${money(payload.amount)}` });
              busy(btn, false);
              toast('Edit saved on this device — it will send when you reconnect', 'ok', 4200);
              closeSheet();
              await load();
            } catch (err2) { busy(btn, false); toast(`Could not save on this device: ${err2.message || ''}`, 'bad', 6000); }
            return;
          }
          if (isOffline) {
            busy(btn, true, 'Saving');
            try {
              await enqueue('expense', { ...payload, client_ref: makeRef('exp') }, {
                label: `${d.title} · ${money(payload.amount)}`,
              });
              busy(btn, false);
              toast(`${money(payload.amount)} saved on this device — it will send when you reconnect`, 'ok', 4200);
              closeSheet();
            } catch (err2) { busy(btn, false); toast(`Could not save on this device: ${err2.message || ''}`, 'bad', 6000); }
            return;
          }

          busy(btn, true, 'Saving');
          try {
            await api.saveExpense(isNew ? null : e.id, isNew
              ? { ...payload, client_ref: makeRef('exp') }
              : { ...payload, client_ref: makeRef('exp'), base_updated_at: e.updated_at || null });
            toast(isNew ? `${money(d.amount)} recorded` : 'Expense updated', 'ok');
            closeSheet();
            await load();
          } catch (err) {
            busy(btn, false);
            // Connection dropped mid-save. Queue it; the client_ref stops a retry
            // from recording the same expense twice.
            if (isNew && (err?.offline || err?.status === 0)) {
              try {
                await enqueue('expense', { ...payload, client_ref: makeRef('exp') }, { label: `${d.title} · ${money(payload.amount)}` });
                toast(`Connection lost — ${money(payload.amount)} saved on this device instead`, 'warn', 5000);
                closeSheet();
                return;
              } catch { /* fall through to the plain error */ }
            }
            toast(err.message, 'bad');
          }
        });
        if (!isNew) {
          on(el, 'click', '[data-delete]', async () => {
            if (!await confirmDialog({ title: 'Delete this expense?', message: `${e.title} — ${money(e.amount)}`, confirmLabel: 'Delete', danger: true })) return;
            const offline = typeof navigator !== 'undefined' && navigator.onLine === false;
            if (offline) {
              try {
                await enqueue('expense:delete', { id: e.id, base_updated_at: e.updated_at || null },
                  { label: `${e.title} · ${money(e.amount)}` });
                toast('Deletion queued — it will apply when you reconnect', 'ok', 4200);
                closeSheet(); await load();
              } catch (err2) { toast(`Could not queue the deletion: ${err2.message || ''}`, 'bad', 6000); }
              return;
            }
            try {
              await api.deleteExpense(e.id, { client_ref: makeRef('exp'), base_updated_at: e.updated_at || null });
              toast('Expense deleted', 'ok');
              closeSheet(); await load();
            } catch (err) {
              if (err?.status === 409) {
                toast('That expense changed on the server — reload the list and try again', 'warn', 6000);
                closeSheet(); await load();
                return;
              }
              toast(err.message, 'bad');
            }
          });
        }
      },
    });
  }

  cleanups.push(on(host, 'click', '[data-exp]', (_e, el) => {
    const e = cache.expenses.find((x) => String(x.id) === el.dataset.exp);
    if (e) editor(e);
  }));
  cleanups.push(on(host, 'click', '[data-add2]', () => editor(null)));

  await load();
  return () => cleanups.forEach((fn) => { try { fn?.(); } catch { /* ignore */ } });
}

function daysBetween(from, to) {
  const a = new Date(`${from}T00:00:00`);
  const b = new Date(`${to}T00:00:00`);
  return Math.max(1, Math.round((b - a) / 86400000) + 1);
}

export { invalidate };
