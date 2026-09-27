/* The pending-changes panel.
 *
 * One component, used by every screen that can queue work, so a cashier sees the
 * same list and the same choices whichever screen they are on. It answers three
 * questions: what is waiting, did anything go wrong, and what do I do about it.
 *
 * Conflicts get an explicit choice rather than an automatic resolution. Picking
 * for the user is how someone's afternoon of work quietly disappears.
 */

import { icon, on, toast, busy, confirmDialog } from './ui.js';
import { esc, money, dateTime, kindLabel } from './format.js';
import { listOutbox, discard, retry, syncOutbox, resolveConflict, describeKind, onOutboxChange } from './offline.js';

/**
 * Render the queue into `host`, filtered to the kinds this screen cares about.
 * `kinds` may be exact ('sale') or a prefix ('expense' matches 'expense:update').
 * Returns a cleanup function.
 */
export function pendingPanel(host, { kinds = null, title = 'Queued on this device' } = {}) {
  if (!host) return () => {};

  const matches = (kind) => {
    if (!kinds) return true;
    const list = Array.isArray(kinds) ? kinds : [kinds];
    return list.some((k) => kind === k || kind.startsWith(`${k}:`));
  };

  async function paint() {
    let items = [];
    try { items = (await listOutbox()).filter((r) => matches(r.kind)); } catch { return; }
    if (!items.length) { host.innerHTML = ''; return; }

    const conflicts = items.filter((i) => i.conflict);
    const failed = items.filter((i) => i.failed && !i.conflict);

    host.innerHTML = `
      <div class="card">
        <div class="card-head">
          <h3 class="grow">${icon('wifiOff', { size: 16 })} ${esc(title)}</h3>
          <span class="badge ${conflicts.length ? 'bad' : failed.length ? 'warn' : 'info'}">
            ${items.length} waiting${conflicts.length ? ` · ${conflicts.length} conflict${conflicts.length === 1 ? '' : 's'}` : ''}
          </span>
        </div>
        <div class="card-body tight">
          <div class="list">
            ${items.map((i) => rowHtml(i)).join('')}
          </div>
          <div style="padding:10px 14px;border-top:1px solid var(--line);display:flex;gap:8px;align-items:center;flex-wrap:wrap">
            <button class="btn btn-primary btn-sm" data-p-send>${icon('refresh', { size: 15 })} Send now</button>
            <span class="small muted">Stored safely on this device. They send automatically
            when the connection returns.</span>
          </div>
        </div>
      </div>`;
  }

  function rowHtml(i) {
    const thumb = i.conflict ? 'red' : i.failed ? 'red' : 'gold';
    const glyph = i.conflict ? 'alert' : i.failed ? 'alert' : 'clock';
    const summary = describeSummary(i);

    if (i.conflict) {
      return `
        <div class="list-item" data-row="${esc(i.ref)}">
          <span class="thumb ${thumb}">${icon(glyph, { size: 17 })}</span>
          <span class="list-main">
            <span class="list-title">${esc(describeKind(i.kind))} <span class="badge bad">conflict</span></span>
            <span class="list-sub">${esc(summary)}<br>
              Someone changed this while you were offline. Your version is based on
              ${esc(i.clientBase || 'an older copy')}; the server now has
              ${esc(i.serverUpdatedAt || 'a newer one')}.</span>
          </span>
          <span class="list-side" style="gap:6px;flex-wrap:wrap;justify-content:flex-end">
            <button class="btn btn-sm" data-p-mine="${esc(i.ref)}">Keep mine</button>
            <button class="btn btn-sm" data-p-theirs="${esc(i.ref)}">Keep server's</button>
          </span>
        </div>`;
    }

    return `
      <div class="list-item" data-row="${esc(i.ref)}">
        <span class="thumb ${thumb}">${icon(glyph, { size: 17 })}</span>
        <span class="list-main">
          <span class="list-title">${esc(i.provisional || describeKind(i.kind))}</span>
          <span class="list-sub">${esc(summary)} · captured ${esc(dateTime(i.capturedAt))}
            ${i.lastError ? `<br><span style="color:var(--bad)">${esc(i.lastError)}</span>` : ''}</span>
        </span>
        <span class="list-side" style="gap:6px">
          ${i.payload?.total !== undefined ? `<span class="list-amount">${esc(money(i.payload.total))}</span>` : ''}
          ${i.failed ? `<button class="btn btn-ghost btn-sm" data-p-retry="${esc(i.ref)}">Retry</button>` : ''}
          <button class="btn btn-ghost btn-icon btn-sm" data-p-drop="${esc(i.ref)}"
            title="Remove this queued change" aria-label="Remove queued change">${icon('trash', { size: 15 })}</button>
        </span>
      </div>`;
  }

  function describeSummary(i) {
    if (i.label) return i.label;
    const p = i.payload || {};
    if (p.title && p.amount !== undefined) return `${p.title} · ${money(p.amount)}`;
    if (p.name && p.price !== undefined) return `${p.name} · ${money(p.price)}`;
    if (p.name) return String(p.name);
    if (p.kind && p.qty !== undefined) return `${kindLabel(p.kind)} · ${p.qty}`;
    if (Array.isArray(p.items)) return `${p.items.length} line${p.items.length === 1 ? '' : 's'}`;
    return '';
  }

  const offs = [];

  offs.push(on(host, 'click', '[data-p-send]', async (_e, el) => {
    busy(el, true, 'Sending');
    const out = await syncOutbox();
    busy(el, false);
    toast(out.synced
      ? `Sent ${out.synced} queued ${out.synced === 1 ? 'change' : 'changes'}`
      : (out.offline ? 'Still no connection — they are safe on this device'
        : (out.failed ? `${out.failed} need your attention below` : 'Nothing could be sent yet')),
      out.synced ? 'ok' : 'warn', 4200);
    await paint();
  }));

  offs.push(on(host, 'click', '[data-p-retry]', async (_e, el) => {
    await retry(el.dataset.pRetry);
    await paint();
  }));

  offs.push(on(host, 'click', '[data-p-drop]', async (_e, el) => {
    const ok = await confirmDialog({
      title: 'Remove this queued change?',
      message: 'It has not reached the server, so removing it here discards it completely. '
        + 'Only do this if the change was a mistake.',
      confirmLabel: 'Remove it', danger: true,
    });
    if (!ok) return;
    await discard(el.dataset.pDrop);
    toast('Queued change removed', 'ok');
    await paint();
  }));

  offs.push(on(host, 'click', '[data-p-mine]', async (_e, el) => {
    const ok = await confirmDialog({
      title: 'Overwrite the server version?',
      message: 'This replaces whatever is on the server with your offline change. '
        + 'If someone else edited it while you were offline, their edit is lost.',
      confirmLabel: 'Use my version', danger: true,
    });
    if (!ok) return;
    const out = await resolveConflict(el.dataset.pMine, 'mine');
    toast(out?.synced ? 'Your version was applied' : 'Could not apply it yet', out?.synced ? 'ok' : 'warn');
    await paint();
  }));

  offs.push(on(host, 'click', '[data-p-theirs]', async (_e, el) => {
    const ok = await confirmDialog({
      title: 'Discard your offline change?',
      message: 'The server version is kept and your queued edit is thrown away.',
      confirmLabel: 'Keep the server version', danger: true,
    });
    if (!ok) return;
    await resolveConflict(el.dataset.pTheirs, 'theirs');
    toast('Server version kept', 'ok');
    await paint();
  }));

  paint();

  // A background sync (triggered by reconnection, or by another screen) changes
  // the queue underneath us, so keep the panel truthful without the caller
  // having to remember to refresh it.
  offs.push(onOutboxChange(() => { paint(); }));

  return () => { offs.forEach((off) => { try { off(); } catch { /* ignore */ } }); };
}
