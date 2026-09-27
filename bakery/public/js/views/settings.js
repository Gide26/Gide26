/**
 * Settings: business profile & currency, password, the staff team, and
 * housekeeping. Sections that only concern the owner are hidden from staff.
 */
import { api } from '../api.js';
import { state, isOwner, applySettings, signOut, invalidate } from '../store.js';
import { icon, $, on, toast, busy, sheet, emptyState, confirmDialog } from '../ui.js';
import { money, num, esc, dateTime, relTime } from '../format.js';
import { navigate } from '../router.js';

const CURRENCIES = [
  { code: 'BIF', symbol: 'FBu', name: 'Burundian franc', decimals: 0 },
  { code: 'RWF', symbol: 'RF', name: 'Rwandan franc', decimals: 0 },
  { code: 'UGX', symbol: 'USh', name: 'Ugandan shilling', decimals: 0 },
  { code: 'KES', symbol: 'KSh', name: 'Kenyan shilling', decimals: 0 },
  { code: 'CDF', symbol: 'FC', name: 'Congolese franc', decimals: 0 },
  { code: 'TZS', symbol: 'TSh', name: 'Tanzanian shilling', decimals: 0 },
  { code: 'USD', symbol: '$', name: 'US dollar', decimals: 2 },
  { code: 'EUR', symbol: '€', name: 'Euro', decimals: 2 },
];

export async function render(host, ctx) {
  const owner = isOwner();
  let meta = null;
  try { meta = await api.meta(); } catch { meta = { timezones: ['Africa/Bujumbura'], units: [] }; }

  const tabs = [
    ...(owner ? [{ id: 'business', label: 'Business', icon: 'store' }] : []),
    { id: 'password', label: 'Password', icon: 'lock' },
    ...(owner ? [{ id: 'team', label: 'Team', icon: 'users' }] : []),
    { id: 'about', label: 'About & data', icon: 'database' },
  ];
  let tab = tabs.some((t) => t.id === ctx.params.get('tab')) ? ctx.params.get('tab') : tabs[0].id;

  host.innerHTML = `
    <div class="page-head">
      <div class="grow">
        <h1>Settings</h1>
        <div class="small-muted small muted">Signed in as ${esc(state.user?.name || '')} · ${owner ? 'Owner' : 'Staff'}</div>
      </div>
    </div>
    <div class="chips" style="margin-bottom:12px">
      ${tabs.map((t) => `<button class="chip${tab === t.id ? ' active' : ''}" data-tab="${t.id}">${esc(t.label)}</button>`).join('')}
    </div>
    <div id="s-body"></div>`;

  const body = $('#s-body', host);
  const cleanups = [];
  cleanups.push(on(host, 'click', '[data-tab]', (_e, el) => {
    tab = el.dataset.tab;
    host.querySelectorAll('[data-tab]').forEach((b) => b.classList.toggle('active', b.dataset.tab === tab));
    paint();
  }));

  async function paint() {
    if (tab === 'business') paintBusiness();
    else if (tab === 'password') paintPassword();
    else if (tab === 'team') await paintTeam();
    else paintAbout();
  }

  /* ---------------- business ---------------- */

  function paintBusiness() {
    const s = state.settings;
    const cur = CURRENCIES.find((c) => c.code === s.currency_code);
    body.innerHTML = `
      <div class="card">
        <div class="card-head"><h3 class="grow">Your business</h3></div>
        <div class="card-body">
          <form id="biz-form">
            <div class="field-row field-row-2">
              <label class="field"><span class="field-label">Business name</span>
                <input type="text" name="business_name" value="${esc(s.business_name || '')}" maxlength="120"></label>
              <label class="field"><span class="field-label">Tagline</span>
                <input type="text" name="tagline" value="${esc(s.tagline || '')}" maxlength="160"
                  placeholder="Fresh bread, cakes & pastries"></label>
            </div>
            <div class="field-row field-row-2">
              <label class="field"><span class="field-label">Phone</span>
                <input type="tel" name="phone" value="${esc(s.phone || '')}" maxlength="40" inputmode="tel"></label>
              <label class="field"><span class="field-label">Address</span>
                <input type="text" name="address" value="${esc(s.address || '')}" maxlength="200"></label>
            </div>
            <label class="field"><span class="field-label">Receipt thank-you line</span>
              <input type="text" name="receipt_note" value="${esc(s.receipt_note || '')}" maxlength="300"></label>
            <label class="field"><span class="field-label">Timezone</span>
              <select name="timezone">
                ${meta.timezones.map((t) => `<option value="${esc(t)}"${s.timezone === t ? ' selected' : ''}>${esc(t)}</option>`).join('')}
              </select>
              <span class="field-hint">Used to decide which day a sale belongs to. Today is
                ${esc(String(state.serverToday || ''))} in this timezone.</span></label>

            <div class="divider"></div>
            <h4 style="margin-bottom:10px">Money</h4>
            <div class="field-row field-row-3">
              <label class="field"><span class="field-label">Currency</span>
                <select name="currency_code" id="cur-code">
                  ${CURRENCIES.map((c) => `<option value="${c.code}"${s.currency_code === c.code ? ' selected' : ''}>${esc(c.name)} (${c.code})</option>`).join('')}
                </select></label>
              <label class="field"><span class="field-label">Symbol</span>
                <input type="text" name="currency_symbol" id="cur-symbol" value="${esc(s.currency_symbol || '')}" maxlength="8"></label>
              <label class="field"><span class="field-label">Decimal places</span>
                <select name="currency_decimals" id="cur-dec">
                  ${[0, 1, 2].map((d) => `<option value="${d}"${Number(s.currency_decimals ?? 0) === d ? ' selected' : ''}>${d}</option>`).join('')}
                </select></label>
            </div>
            <div class="pill-note warn" style="margin-bottom:14px">${icon('info', { size: 17 })}
              <div>Changing the currency only changes how amounts are <strong>displayed</strong>. Existing sales and
              expenses are <strong>not converted</strong> — they keep the numbers you typed.</div></div>

            <div class="divider"></div>
            <h4 style="margin-bottom:10px">How the till behaves</h4>
            <label class="switch" style="margin-bottom:12px">
              <input type="checkbox" name="auto_deduct_stock" ${s.auto_deduct_stock !== '0' ? 'checked' : ''}>
              <span class="track"></span>
              <span class="switch-text">Take ingredients off the shelf automatically
                <small>When a product has a recipe, each sale reduces the ingredients it used</small></span>
            </label>
            <label class="switch">
              <input type="checkbox" name="low_stock_alerts" ${s.low_stock_alerts !== '0' ? 'checked' : ''}>
              <span class="track"></span>
              <span class="switch-text">Warn me when something runs low
                <small>Shows a notice after a sale and on the dashboard</small></span>
            </label>

            <div class="row end" style="gap:8px;margin-top:16px">
              <button type="button" class="btn" data-reset-biz>Undo changes</button>
              <button type="button" class="btn btn-primary" data-save-biz>${icon('check')} Save settings</button>
            </div>
          </form>
        </div>
      </div>`;

    // Keep symbol/decimals in step with the chosen currency, but allow overrides.
    const codeSel = $('#cur-code', body);
    const symIn = $('#cur-symbol', body);
    const decSel = $('#cur-dec', body);
    cleanups.push(on(body, 'change', '#cur-code', () => {
      const c = CURRENCIES.find((x) => x.code === codeSel.value);
      if (c) { symIn.value = c.symbol; decSel.value = String(c.decimals); }
    }));

    cleanups.push(on(body, 'click', '[data-save-biz]', async (_e, btn) => {
      const form = $('#biz-form', body);
      const d = Object.fromEntries(new FormData(form).entries());
      busy(btn, true, 'Saving');
      try {
        const out = await api.saveSettings({
          ...d,
          auto_deduct_stock: form.querySelector('[name=auto_deduct_stock]').checked,
          low_stock_alerts: form.querySelector('[name=low_stock_alerts]').checked,
        });
        applySettings(out.settings, state.serverToday);
        invalidate();
        toast('Settings saved', 'ok');
        // The business name appears in the sidebar, so refresh the shell.
        setTimeout(() => location.reload(), 450);
      } catch (err) { busy(btn, false); toast(err.message, 'bad'); }
    }));

    cleanups.push(on(body, 'click', '[data-reset-biz]', () => paintBusiness()));
  }

  /* ---------------- password ---------------- */

  function paintPassword() {
    body.innerHTML = `
      <div class="card">
        <div class="card-head"><h3 class="grow">Change your password</h3></div>
        <div class="card-body">
          ${state.user?.must_change ? `<div class="pill-note bad" style="margin-bottom:14px">${icon('alert', { size: 17 })}
            <div>You are still using the temporary password from setup. Please change it now — anyone who
            knows it could see your sales.</div></div>` : ''}
          <form id="pw-form" style="max-width:420px">
            <label class="field"><span class="field-label">Current password</span>
              <input type="password" name="current" autocomplete="current-password" required></label>
            <label class="field"><span class="field-label">New password</span>
              <input type="password" name="next" autocomplete="new-password" minlength="6" required>
              <span class="field-hint">At least 6 characters. Longer is better — a phrase works well.</span></label>
            <label class="field"><span class="field-label">Type it again</span>
              <input type="password" name="confirm" autocomplete="new-password" minlength="6" required></label>
            <button type="submit" class="btn btn-primary">${icon('lock', { size: 16 })} Update password</button>
          </form>
          <p class="small muted" style="margin-top:14px">For your safety, changing your password signs you out of
          every device. You will sign straight back in here.</p>
        </div>
      </div>

      <div class="card">
        <div class="card-head"><h3 class="grow">Your login</h3></div>
        <div class="card-body tight">
          <div class="list">
            <div class="list-item"><span class="list-main"><span class="list-title">${esc(state.user?.name || '')}</span>
              <span class="list-sub">${owner ? 'Owner — full access' : 'Staff — selling and recording only'}</span></span>
              <span class="badge ${owner ? 'gold' : 'info'}">${owner ? 'Owner' : 'Staff'}</span></div>
            <div class="list-item"><span class="list-main"><span class="list-title">Sign-in phone</span>
              <span class="list-sub">${esc(state.user?.phone || '')}</span></span></div>
          </div>
        </div>
      </div>`;

    cleanups.push(on(body, 'submit', '#pw-form', async (e) => {
      e.preventDefault();
      const form = e.target;
      const d = Object.fromEntries(new FormData(form).entries());
      if (d.next !== d.confirm) return toast('The two new passwords do not match', 'warn');
      if (String(d.next).length < 6) return toast('Use at least 6 characters', 'warn');
      const btn = form.querySelector('button[type=submit]');
      busy(btn, true, 'Updating');
      try {
        await api.changePassword(d.current, d.next);
        toast('Password changed. Signing you back in…', 'ok');
        // The server killed every session, so re-authenticate silently.
        await api.login(state.user.phone, d.next);
        const me = await api.me();
        state.user = me.user;
        applySettings(me.settings, me.today);
        setTimeout(() => location.reload(), 600);
      } catch (err) { busy(btn, false); toast(err.message, 'bad', 5000); }
    }));
  }

  /* ---------------- team ---------------- */

  async function paintTeam() {
    body.innerHTML = '<div class="loading-page"><div class="spinner"></div></div>';
    let users = [];
    try { users = await api.users(); }
    catch (err) {
      body.innerHTML = `<div class="card"><div class="empty">${icon('alert', { size: 36, stroke: 1.5 })}
        <h4>Could not load the team</h4><p>${esc(err.message)}</p></div></div>`;
      return;
    }

    body.innerHTML = `
      <div class="card">
        <div class="card-head"><h3 class="grow">Who can sign in</h3>
          <button class="btn btn-primary btn-sm" data-add-user>${icon('plus', { size: 15 })} Add person</button></div>
        <div class="card-body tight">
          <div class="list">${users.map((u) => `
            <div class="list-item clickable" data-user="${u.id}" role="button" tabindex="0">
              <span class="thumb ${u.active ? (u.role === 'owner' ? 'gold' : '') : 'grey'}">
                ${icon(u.role === 'owner' ? 'shield' : 'user', { size: 18 })}</span>
              <span class="list-main">
                <span class="list-title">${esc(u.name)}${u.id === state.user?.id ? ' <span class="badge info">you</span>' : ''}
                  ${u.active ? '' : ' <span class="badge">deactivated</span>'}</span>
                <span class="list-sub">${esc(u.phone)} · ${num(u.sales_count)} sales${u.last_sale ? ` · last ${esc(relTime(u.last_sale))}` : ''}</span>
              </span>
              <span class="list-side"><span class="badge ${u.role === 'owner' ? 'gold' : ''}">${u.role === 'owner' ? 'Owner' : 'Staff'}</span></span>
            </div>`).join('')}</div>
        </div>
        <div class="card-foot small muted">
          ${icon('info', { size: 14 })} Owners see profit, costs and reports. Staff can sell, record expenses and
          check stock — but never see what things cost you.
        </div>
      </div>`;

    cleanups.push(on(body, 'click', '[data-add-user]', () => userEditor(null, users)));
    cleanups.push(on(body, 'click', '[data-user]', (_e, el) =>
      userEditor(users.find((u) => String(u.id) === el.dataset.user), users)));
  }

  function userEditor(u, users) {
    const isNew = !u;
    const person = u || { name: '', phone: '', role: 'staff', active: 1 };
    const isSelf = !isNew && person.id === state.user?.id;

    sheet({
      title: isNew ? 'Add a person' : person.name,
      subtitle: isNew ? 'Give them their own login' : `${person.phone} · ${person.role === 'owner' ? 'Owner' : 'Staff'}`,
      body: `<form id="u-form">
        <label class="field"><span class="field-label">Name</span>
          <input type="text" name="name" value="${esc(person.name)}" required maxlength="80" placeholder="e.g. Aline Niyonzima"></label>
        <label class="field"><span class="field-label">Phone number (their login)</span>
          <input type="tel" name="phone" value="${esc(person.phone)}" required maxlength="30" inputmode="tel"
            placeholder="079123456" ${isSelf ? 'readonly' : ''}></label>
        <label class="field"><span class="field-label">Role</span>
          <select name="role" ${isSelf ? 'disabled' : ''}>
            <option value="staff"${person.role !== 'owner' ? ' selected' : ''}>Staff — can sell and record</option>
            <option value="owner"${person.role === 'owner' ? ' selected' : ''}>Owner — full access including profit</option>
          </select>
          <span class="field-hint">${isSelf ? 'You cannot change your own role here, so you never lock yourself out.' : ''}</span></label>
        ${isNew ? `<label class="field" style="margin-bottom:0"><span class="field-label">Starting password</span>
          <input type="text" name="password" minlength="6" required placeholder="At least 6 characters">
          <span class="field-hint">They will be asked to change it the first time they sign in.</span></label>` : ''}
        ${!isNew ? `<div class="divider"></div>
          <label class="switch"><input type="checkbox" name="active" ${Number(person.active) ? 'checked' : ''} ${isSelf ? 'disabled' : ''}>
            <span class="track"></span><span class="switch-text">Can sign in
              <small>Turn off for someone who has left — their sales stay in your history</small></span></label>` : ''}
      </form>`,
      footer: `${!isNew && !isSelf ? `<button class="btn" data-reset-pw>${icon('key', { size: 16 })} New password</button>` : ''}
        ${!isNew && !isSelf ? `<button class="btn btn-danger" data-delete style="flex:0 0 auto">${icon('trash', { size: 16 })}</button>` : ''}
        <button class="btn" data-close>Cancel</button>
        <button class="btn btn-primary" data-save>${isNew ? 'Add person' : 'Save'}</button>`,
      onMount: (el, closeSheet) => {
        on(el, 'click', '[data-save]', async () => {
          const form = $('#u-form', el);
          const d = Object.fromEntries(new FormData(form).entries());
          if (!String(d.name).trim()) return toast('Enter a name', 'warn');
          if (isNew && String(d.password || '').length < 6) return toast('Password needs at least 6 characters', 'warn');
          const btn = $('[data-save]', el);
          busy(btn, true, 'Saving');
          try {
            const payload = isNew
              ? { name: d.name, phone: d.phone, role: d.role, password: d.password }
              : { name: d.name, role: isSelf ? person.role : d.role,
                  active: isSelf ? 1 : (form.querySelector('[name=active]')?.checked ? 1 : 0) };
            await api.saveUser(isNew ? null : person.id, payload);
            toast(isNew ? `${d.name} can now sign in` : 'Saved', 'ok');
            closeSheet();
            await paintTeam();
          } catch (err) { busy(btn, false); toast(err.message, 'bad', 5000); }
        });

        if (!isNew && !isSelf) {
          on(el, 'click', '[data-reset-pw]', async () => {
            const pw = window.prompt(`New password for ${person.name} (at least 6 characters):`);
            if (pw === null) return;
            if (String(pw).length < 6) return toast('Use at least 6 characters', 'warn');
            try {
              await api.resetUserPassword(person.id, pw);
              toast(`Password reset. Tell ${person.name.split(' ')[0]} the new one.`, 'ok', 4500);
              closeSheet();
            } catch (err) { toast(err.message, 'bad'); }
          });

          on(el, 'click', '[data-delete]', async () => {
            if (!await confirmDialog({
              title: `Remove ${person.name}?`,
              message: 'If they have recorded sales, they are deactivated instead of deleted so your history stays intact.',
              confirmLabel: 'Remove', danger: true,
            })) return;
            try {
              const out = await api.deleteUser(person.id);
              toast(out.archived ? 'Deactivated — their sales are kept' : 'Removed', 'ok');
              closeSheet();
              await paintTeam();
            } catch (err) { toast(err.message, 'bad', 5000); }
          });
        }
      },
    });
  }

  /* ---------------- about & data ---------------- */

  function paintAbout() {
    const s = state.settings;
    body.innerHTML = `
      <div class="card">
        <div class="card-head"><h3 class="grow">This system</h3></div>
        <div class="card-body tight">
          <div class="list">
            ${row('Business', s.business_name || '—')}
            ${row('Currency', `${s.currency_symbol || ''} ${s.currency_code || ''}`)}
            ${row('Timezone', s.timezone || '—')}
            ${row('Server date', state.serverToday || '—')}
            ${row('Signed in as', `${state.user?.name || ''} (${state.user?.role === 'owner' ? 'owner' : 'staff'})`)}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-head"><h3 class="grow">Use it on your phone</h3></div>
        <div class="card-body">
          <p class="small">Add this to your home screen and it opens like a normal app, full screen:</p>
          <div class="stack" style="gap:8px;margin-top:10px">
            <div class="pill-note info">${icon('info', { size: 17 })}
              <div><strong>iPhone / iPad:</strong> tap the Share button in Safari, then “Add to Home Screen”.</div></div>
            <div class="pill-note info">${icon('info', { size: 17 })}
              <div><strong>Android:</strong> tap the ⋮ menu in Chrome, then “Add to Home screen” or “Install app”.</div></div>
            <div class="pill-note info">${icon('info', { size: 17 })}
              <div><strong>Computer:</strong> look for the install icon in the address bar, or just keep the tab open.</div></div>
          </div>
        </div>
      </div>

      ${owner ? `
      <div class="card">
        <div class="card-head"><h3 class="grow">Your data</h3></div>
        <div class="card-body">
          <p class="small">Everything is stored in a single SQLite file on the machine running the server
          (<code>bakery/data/bakery.sqlite</code>). Back that file up and you have backed up the whole business.</p>
          <div class="row wrap" style="gap:8px;margin-top:12px">
            <a class="btn" href="${esc(api.exportUrl('sales', { from: '2000-01-01', to: '2999-12-31' }))}">
              ${icon('download', { size: 16 })} All sales (CSV)</a>
            <a class="btn" href="${esc(api.exportUrl('expenses', { from: '2000-01-01', to: '2999-12-31' }))}">
              ${icon('download', { size: 16 })} All expenses (CSV)</a>
            <a class="btn" href="${esc(api.exportUrl('products'))}">
              ${icon('download', { size: 16 })} Product costing (CSV)</a>
            <a class="btn" href="${esc(api.exportUrl('inventory'))}">
              ${icon('download', { size: 16 })} Stock valuation (CSV)</a>
          </div>
          <div class="divider"></div>
          <p class="small muted">To snapshot the whole database, run <code>npm run backup</code> on the server.
          Backups land in <code>bakery/data/backups/</code>.</p>
        </div>
      </div>` : ''}

      <div class="card">
        <div class="card-body">
          <button class="btn btn-block" data-signout>${icon('logout', { size: 16 })} Sign out</button>
        </div>
      </div>`;

    cleanups.push(on(body, 'click', '[data-signout]', async () => {
      if (!await confirmDialog({ title: 'Sign out?', message: 'You will need your phone number and password to get back in.', confirmLabel: 'Sign out' })) return;
      await signOut();
      location.hash = '#/';
      location.reload();
    }));
  }

  const row = (label, value) => `
    <div class="list-item">
      <span class="list-main"><span class="list-sub">${esc(label)}</span>
      <span class="list-title">${esc(value)}</span></span>
    </div>`;

  await paint();
  return () => cleanups.forEach((fn) => { try { fn?.(); } catch { /* ignore */ } });
}
