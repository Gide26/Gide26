/**
 * Sign-in screen, and the first-run setup shown when the database has no
 * owner yet. Both live here because they share the same layout.
 */
import { api } from '../api.js';
import { signIn, completeSetup } from '../store.js';
import { icon, $, toast, busy, on } from '../ui.js';
import { esc } from '../format.js';

export async function render(host, { onSignedIn }) {
  let status = { needsSetup: false, demo: false, businessName: 'Bakery Tracker', currencySymbol: 'FBu' };
  let statusOk = true;
  try {
    status = await api.get('/api/status');
  } catch (err) {
    statusOk = false;
    console.warn('Could not reach the server:', err?.message);
  }

  let mode = status.needsSetup ? 'setup' : 'signin';

  const paint = () => {
    const name = esc(status.businessName || 'Bakery Tracker');
    host.innerHTML = `
      <div class="auth-wrap">
        <div class="auth-card">
          <div class="auth-logo">${icon('bread', { size: 31, stroke: 2 })}</div>
          ${mode === 'setup' ? setupBody(name) : signinBody(name, status)}
          ${!statusOk ? `
            <div class="pill-note bad" style="margin-top:14px">
              ${icon('wifiOff', { size: 17 })}
              <div>Cannot reach the server. Check that it is running and that you are online.</div>
            </div>` : ''}
        </div>
      </div>`;
    bind();
  };

  const setupBody = (business) => `
    <h1 class="auth-title">Set up ${business}</h1>
    <p class="auth-sub">Create your owner login. It takes about 20 seconds.</p>
    <form id="auth-form" novalidate>
      <label class="field">
        <span class="field-label">Your name</span>
        <input type="text" name="name" autocomplete="name" placeholder="e.g. Gide Nkurunziza" required>
      </label>
      <label class="field">
        <span class="field-label">Phone number (used to sign in)</span>
        <input type="tel" name="phone" autocomplete="tel" inputmode="tel" placeholder="079000000" required>
      </label>
      <label class="field">
        <span class="field-label">Password</span>
        <input type="password" name="password" autocomplete="new-password" placeholder="At least 6 characters" minlength="6" required>
      </label>
      <button type="submit" class="btn btn-primary btn-lg btn-block" data-submit>
        ${icon('check')} Create my account
      </button>
    </form>
    <div class="auth-alt">
      Just exploring?
      <a href="#" data-demo>Load a demo bakery</a> with 60 days of sales.
    </div>`;

  const signinBody = (business, st) => `
    <h1 class="auth-title">${business}</h1>
    <p class="auth-sub">Sign in to record sales and track your profit.</p>
    <form id="auth-form" novalidate>
      <label class="field">
        <span class="field-label">Phone number</span>
        <input type="tel" name="phone" autocomplete="username" inputmode="tel" placeholder="079000000" required>
      </label>
      <label class="field">
        <span class="field-label">Password</span>
        <input type="password" name="password" autocomplete="current-password" placeholder="Your password" required>
      </label>
      <button type="submit" class="btn btn-primary btn-lg btn-block" data-submit>
        ${icon('lock', { size: 17 })} Sign in
      </button>
    </form>
    ${st.demo ? `
      <div class="pill-note info" style="margin-top:16px">
        ${icon('info', { size: 17 })}
        <div>
          <strong>Demo data is loaded.</strong>
          <div class="tiny" style="margin-top:4px">
            Owner <code>079000000</code> / <code>changeme</code><br>
            Staff <code>079111111</code> / <code>staff123</code>
          </div>
        </div>
      </div>` : ''}
    ${st.needsSetup ? '' : `
      <div class="auth-alt">
        Forgot your password? Ask the owner, or run
        <code>npm run reset-password</code> on the server.
      </div>`}`;

  const bind = () => {
    const form = $('#auth-form', host);
    if (!form) return;

    on(form, 'submit', async (e) => {
      e.preventDefault();
      const btn = $('[data-submit]', form);
      const data = Object.fromEntries(new FormData(form).entries());

      if (!String(data.phone || '').trim()) return toast('Enter your phone number', 'warn');
      if (!String(data.password || '')) return toast('Enter your password', 'warn');

      busy(btn, true);
      try {
        if (mode === 'setup') {
          if (!String(data.name || '').trim()) { busy(btn, false); return toast('Enter your name', 'warn'); }
          await completeSetup({ name: data.name, phone: data.phone, password: data.password });
          toast('Welcome! Your bakery is ready.', 'ok');
        } else {
          const user = await signIn(data.phone, data.password);
          toast(`Signed in as ${user.name}`, 'ok', 2200);
        }
        onSignedIn();
      } catch (err) {
        busy(btn, false);
        toast(err?.message || 'Could not sign in', 'bad', 5000);
      }
    });

    on(host, 'click', '[data-demo]', async (e) => {
      e.preventDefault();
      const ok = window.confirm(
        'Load a demo bakery with 60 days of sales, stock and expenses?\n\nThis only works on an empty database.');
      if (!ok) return;
      try {
        const out = await api.seedDemo();
        toast(`Demo loaded: ${out.seeded?.sales ?? 0} sales. Sign in with 079000000 / changeme`, 'ok', 6000);
        status.needsSetup = false;
        status.demo = true;
        status.businessName = "Gide's Bakery";
        mode = 'signin';
        paint();
      } catch (err) {
        toast(err?.message || 'Could not load the demo data', 'bad', 5000);
      }
    });
  };

  paint();
  setTimeout(() => $('input[name=phone]', host)?.focus(), 120);
  return null;
}
