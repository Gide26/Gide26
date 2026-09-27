/**
 * "More" — the mobile overflow screen. Everything that does not fit in the
 * bottom tab bar lives here, plus quick actions and sign-out.
 */
import { api } from '../api.js';
import { state, isOwner, signOut, loadData } from '../store.js';
import { icon, on, toast, confirmDialog } from '../ui.js';
import { esc, num } from '../format.js';
import { navigate } from '../router.js';

export async function render(host) {
  const owner = isOwner();
  let counts = state.data?.counts || {};
  try { counts = (await loadData()).counts || counts; } catch { /* use what we have */ }

  const links = [
    { href: '/products', icon: 'tag', label: 'Products', sub: `${num(counts.products || 0)} on the menu`, tone: '' },
    { href: '/expenses', icon: 'wallet', label: 'Expenses', sub: `${num(counts.expenses || 0)} recorded`, tone: 'gold' },
    { href: '/customers', icon: 'users', label: 'Customers', sub: `${num(counts.customers || 0)} on file`, tone: 'blue' },
    ...(owner ? [{ href: '/reports', icon: 'chart', label: 'Reports & profit', sub: 'Trends, margins, exports', tone: 'green' }] : []),
    { href: '/settings', icon: 'settings', label: 'Settings', sub: owner ? 'Business, team and data' : 'Your password', tone: 'grey' },
  ];

  host.innerHTML = `
    <div class="page-head">
      <div class="grow">
        <h1>More</h1>
        <div class="small muted">${esc(state.settings.business_name || 'Bakery Tracker')}</div>
      </div>
    </div>

    <div class="card" style="margin-bottom:12px">
      <div class="card-body">
        <div class="row" style="gap:12px">
          <span class="avatar" style="width:46px;height:46px;flex-basis:46px;font-size:16px">
            ${esc((state.user?.name || '?').split(' ').map((w) => w[0]).slice(0, 2).join('').toUpperCase())}</span>
          <div class="grow" style="min-width:0">
            <div class="strong" style="font-size:15.5px">${esc(state.user?.name || '')}</div>
            <div class="small muted">${esc(state.user?.phone || '')} · ${owner ? 'Owner' : 'Staff'}</div>
          </div>
          <span class="badge ${owner ? 'gold' : 'info'}">${owner ? 'Full access' : 'Selling only'}</span>
        </div>
        ${state.user?.must_change ? `
          <div class="pill-note bad" style="margin-top:12px">${icon('lock', { size: 17 })}
            <div class="grow"><strong>Temporary password still in use.</strong></div>
            <button class="btn btn-sm btn-danger" data-fix>Change</button></div>` : ''}
      </div>
    </div>

    <div class="card" style="margin-bottom:12px">
      <div class="card-body tight">
        <div class="list">
          ${links.map((l) => `
            <a class="list-item clickable" href="#${l.href}" style="text-decoration:none;color:inherit">
              <span class="thumb ${l.tone}">${icon(l.icon, { size: 18 })}</span>
              <span class="list-main">
                <span class="list-title">${esc(l.label)}</span>
                <span class="list-sub">${esc(l.sub)}</span>
              </span>
              <span class="list-side muted">${icon('chevronRight', { size: 18 })}</span>
            </a>`).join('')}
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <button class="btn btn-block" data-signout>${icon('logout', { size: 16 })} Sign out</button>
        <p class="tiny muted center" style="margin:12px 0 0">
          Bakery Tracker · data lives on your own server</p>
      </div>
    </div>`;

  const offs = [];
  offs.push(on(host, 'click', '[data-fix]', () => navigate('/settings?tab=password')));
  offs.push(on(host, 'click', '[data-signout]', async () => {
    if (!await confirmDialog({ title: 'Sign out?', message: 'You will need your phone number and password to get back in.', confirmLabel: 'Sign out' })) return;
    await signOut();
    location.hash = '#/';
    location.reload();
  }));

  return () => offs.forEach((off) => { try { off(); } catch { /* ignore */ } });
}
