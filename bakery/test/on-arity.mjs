/**
 * Regression test for the event helper `on()`.
 *
 * The sign-in form was once bound with on(form, 'submit', handler) while on()
 * only understood the delegated shape on(root, event, selector, handler). The
 * mistake was silent at bind time and only exploded inside the listener as a
 * SyntaxError from closest(), so the login button appeared dead in a real
 * browser while every server-side test passed. This pins both shapes, and the
 * loud failures, so the mistake cannot come back quietly.
 *
 * Run: node test/on-arity.mjs   (no server needed)
 */
import { on } from '../public/js/ui.js';

let pass = 0;
let fail = 0;
const t = (label, ok, extra = '') => {
  console.log(`  ${ok ? 'PASS' : 'FAIL'}  ${label}${extra ? ' — ' + extra : ''}`);
  ok ? pass++ : fail++;
};

/** Minimal element stub: records listeners and can fire them. */
function stubEl(tag = 'DIV') {
  const listeners = new Map();
  return {
    tagName: tag,
    contains: () => true,
    addEventListener(type, fn) {
      if (!listeners.has(type)) listeners.set(type, []);
      listeners.get(type).push(fn);
    },
    removeEventListener(type, fn) {
      listeners.set(type, (listeners.get(type) || []).filter((f) => f !== fn));
    },
    fire(type, event) {
      for (const fn of [...(listeners.get(type) || [])]) fn(event);
    },
    bound(type) { return (listeners.get(type) || []).length; },
  };
}

console.log('=== direct shape: on(el, event, handler) ===');
{
  const form = stubEl('FORM');
  let seen = null;
  let prevented = false;
  on(form, 'submit', (e) => { seen = e; e.preventDefault(); prevented = e.defaultPrevented; });
  form.fire('submit', { preventDefault() { this.defaultPrevented = true; }, target: { closest() { throw new Error('direct binding must not delegate'); } } });
  t('handler runs on the element itself', seen !== null);
  t('preventDefault still reaches the handler', prevented === true);
}

console.log('\n=== delegated shape: on(el, event, selector, handler) ===');
{
  const host = stubEl('DIV');
  let matched = null;
  on(host, 'click', '[data-save]', (e, el) => { matched = el; });
  const button = { tag: 'BUTTON' };
  host.fire('click', { target: { closest: (sel) => (sel === '[data-save]' ? button : null) } });
  t('matching descendant runs the handler', matched === button);
  matched = null;
  host.fire('click', { target: { closest: () => null } });
  t('non-matching target is ignored', matched === null);
}

console.log('\n=== mistakes fail loudly at bind time, not silently at click time ===');
{
  const el = stubEl('FORM');
  let threw = false;
  try { on(el, 'submit', 42, () => {}); } catch { threw = true; }
  t('a non-string, non-function third argument throws', threw);

  threw = false;
  try { on(el, 'click', '[data-x]'); } catch { threw = true; }
  t('a missing handler throws', threw);

  threw = false;
  try {
    on(el, 'submit', (e) => e.preventDefault());
    el.fire('submit', { preventDefault() {}, target: {} });
  } catch { threw = true; }
  t('the exact login-form binding works end to end', threw === false);
}

console.log('\n=== unbind ===');
{
  const el = stubEl('INPUT');
  let hits = 0;
  const off = on(el, 'change', () => { hits++; });
  el.fire('change', {});
  off();
  el.fire('change', {});
  t('handler stops after unbind', hits === 1 && el.bound('change') === 0, `hits=${hits}`);
}

console.log(`\n  RESULT: ${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
