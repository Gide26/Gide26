/* Money Tracker — revenue goal dashboard
   Streams: clothes sales, writing gigs, job income
   Oct 2026 → Mar 2027 | All amounts in UGX
   Data lives in this browser's localStorage. */

const STORE_KEY = 'gide26.revenue.v2';
const DAY = 86400000;

/* ---------- defaults ---------- */
/* ---------- defaults ----------
   The committed code ships with DEMO numbers only.
   Real figures live in config.js (gitignored) — copy config.example.js to get started.
   Anything set in config.js seeds a fresh browser; after that localStorage wins. */
const defaults = () => {
  const base = {
    version: 3,
    currency: 'UGX',
    goal: 24000000,
    start: '2026-10',
    months: 6,
    monthlyTargets: {},
    streams: [
      { id: 'clothes', name: 'Clothes sales', color: '#34d399', monthly: 1000000, growth: 10, scalable: true },
      { id: 'writing', name: 'Writing gigs',  color: '#38bdf8', monthly: 500000,  growth: 0,  scalable: true },
      { id: 'job',     name: 'Job income',    color: '#fbbf24', monthly: 500000,  growth: 0,  scalable: false },
      { id: 'invest',  name: 'Investing',     color: '#a78bfa', monthly: 100000,  growth: 0,  scalable: false }
    ],
    entries: [
      // demo rows so the dashboard isn't empty on first open — clear them with one click
      { id: 's1', sample: true, date: '2026-10-01', stream: 'job',     amount: 500000, note: 'demo entry' },
      { id: 's2', sample: true, date: '2026-10-05', stream: 'clothes', amount: 250000, note: 'demo entry' },
      { id: 's3', sample: true, date: '2026-10-08', stream: 'writing', amount: 200000, note: 'demo entry' },
      { id: 's4', sample: true, date: '2026-10-09', stream: 'invest',  amount: 100000, note: 'demo entry' }
    ],
    milestones: [
      { id: uid(), title: 'Put my real monthly rates in ⚙ Settings',  due: '2026-10-31', done: false },
      { id: uid(), title: 'Log every payment the day it lands',       due: '2026-11-30', done: false },
      { id: uid(), title: 'Review the plan at the end of each month', due: '2026-11-30', done: false }
    ]
  };

  const cfg = (typeof window !== 'undefined' && window.TRACKER_CONFIG) || null;
  if (cfg){
    ['goal', 'start', 'months', 'currency'].forEach(k => { if (cfg[k] != null) base[k] = cfg[k]; });
    if (Array.isArray(cfg.streams) && cfg.streams.length)
      base.streams = cfg.streams.map(s => Object.assign({ color: '#60a5fa', growth: 0, scalable: false }, s));
    if (Array.isArray(cfg.milestones))
      base.milestones = cfg.milestones.map(m => Object.assign({ id: uid(), done: false }, m));
    if (Array.isArray(cfg.entries))
      base.entries = cfg.entries.map(e => Object.assign({ id: uid() }, e));
  }
  return base;
};

/* ---------- tiny helpers ---------- */
function uid(){ return Date.now().toString(36) + Math.random().toString(36).slice(2, 7); }
function esc(s){ return String(s).replace(/[&<>"]/g, c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;' }[c])); }
function num(v){ const n = parseFloat(v); return isFinite(n) ? n : 0; }
function fmt(n){ return 'UGX ' + Math.round(n).toLocaleString('en-US'); }
function fmtC(n){
  const a = Math.abs(n);
  if (a >= 1e9) return (n/1e9).toFixed(1).replace(/\.0$/,'') + 'B';
  if (a >= 1e6) return (n/1e6).toFixed(a >= 1e8 ? 0 : 2).replace(/\.?0+$/,'') + 'M';
  if (a >= 1e3) return Math.round(n/1e3) + 'K';
  return String(Math.round(n));
}
function parseMonth(key){ const [y, m] = key.split('-').map(Number); return { y, m }; }
function monthDate(key, day){
  const { y, m } = parseMonth(key);
  return new Date(y, m - 1, day || 1);
}
function monthKey(d){ return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0'); }
function addMonthKey(key, n){
  const { y, m } = parseMonth(key);
  return monthKey(new Date(y, m - 1 + n, 1));
}
function monthLabel(key){ return monthDate(key).toLocaleDateString('en-GB', { month: 'short', year: '2-digit' }); }
function monthLong(key){ return monthDate(key).toLocaleDateString('en-GB', { month: 'long', year: 'numeric' }); }
function daysInMonth(key){ const { y, m } = parseMonth(key); return new Date(y, m, 0).getDate(); }
function todayISO(){ const d = new Date(); return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0'); }
function prettyDate(iso){ const [y,m,d] = iso.split('-').map(Number); return new Date(y, m-1, d).toLocaleDateString('en-GB', { day:'numeric', month:'short' }); }

/* ---------- state ---------- */
let state = load();

function load(){
  try {
    const raw = localStorage.getItem(STORE_KEY) || localStorage.getItem('gide26.revenue.v1');
    if (!raw) return seed();
    const s = Object.assign(defaults(), JSON.parse(raw));
    s.streams = s.streams.filter(x => x && x.id);
    // migrate v1 (fixed per-stream targets) → v2 (monthly rate + growth)
    s.streams.forEach(st => {
      if (st.monthly == null) st.monthly = Math.round(num(st.target) / Math.max(1, s.months));
      if (st.growth == null) st.growth = 0;
    });
    s.entries = Array.isArray(s.entries) ? s.entries : [];
    s.milestones = Array.isArray(s.milestones) ? s.milestones : [];
    return s;
  } catch (e) { console.warn('reset', e); return seed(); }
}
function seed(){ const s = defaults(); save(s); return s; }
function save(s){ try { localStorage.setItem(STORE_KEY, JSON.stringify(s || state)); } catch(e){} }
function monthKeys(){ return Array.from({ length: state.months }, (_, i) => addMonthKey(state.start, i)); }

/* what a stream is expected to bring in month i (growth compounds monthly) */
function streamMonth(s, i){ return num(s.monthly) * Math.pow(1 + num(s.growth) / 100, i); }
function streamPlanTotal(s){
  let t = 0;
  for (let i = 0; i < state.months; i++) t += streamMonth(s, i);
  return t;
}
function monthlyTarget(key){
  if (state.monthlyTargets[key] != null) return num(state.monthlyTargets[key]);
  const i = monthKeys().indexOf(key);
  return state.streams.reduce((a, s) => a + streamMonth(s, i < 0 ? 0 : i), 0);
}
function planTotal(){ return monthKeys().reduce((a, k) => a + monthlyTarget(k), 0); }
function horizon(){
  const keys = monthKeys();
  const startD = monthDate(keys[0], 1);
  const lastKey = keys[keys.length - 1];
  const endD = monthDate(lastKey, daysInMonth(lastKey));
  return { startD, endD, days: Math.round((endD - startD) / DAY) + 1 };
}

/* map any entry date to a month slot inside the horizon (clamped) */
function slotOf(iso){
  const keys = monthKeys();
  const [y, m] = iso.split('-').map(Number);
  const d = new Date(y, (m || 1) - 1, 1);
  for (let i = 0; i < keys.length; i++) if (monthKey(d) === keys[i]) return i;
  const first = monthDate(keys[0]), last = monthDate(keys[keys.length - 1]);
  return d < first ? 0 : keys.length - 1;
}

/* ---------- derived numbers ---------- */
function compute(){
  const keys = monthKeys();
  const byMonth = keys.map(() => 0);
  const byMonthStream = keys.map(() => ({}));
  state.streams.forEach(s => keys.forEach((_, i) => byMonthStream[i][s.id] = 0));

  state.entries.forEach(e => {
    const amt = num(e.amount);
    const i = slotOf(e.date || todayISO());
    byMonth[i] += amt;
    byMonthStream[i][e.stream] = (byMonthStream[i][e.stream] || 0) + amt;
  });

  const logged = state.entries.reduce((a, e) => a + num(e.amount), 0);
  const byStream = {};
  state.streams.forEach(s => byStream[s.id] = 0);
  state.entries.forEach(e => { byStream[e.stream] = (byStream[e.stream] || 0) + num(e.amount); });

  const { startD, endD, days } = horizon();
  const now = new Date();
  const elapsedDays = Math.min(days, Math.max(0, Math.floor((now - startD) / DAY) + 1));
  const daysLeft = Math.max(0, days - elapsedDays);

  // expected-to-date: full past months + prorated slice of the current month
  let expected = 0;
  const today = new Date();
  keys.forEach(k => {
    const t = monthlyTarget(k);
    const mEnd = monthDate(k, daysInMonth(k));
    const mStart = monthDate(k, 1);
    if (today > mEnd) expected += t;
    else if (today >= mStart) expected += t * ((today.getDate()) / daysInMonth(k));
  });

  const remaining = Math.max(0, state.goal - logged);
  const gap = logged - expected;
  const perDay = daysLeft > 0 ? remaining / daysLeft : remaining;
  const projection = elapsedDays > 0 ? (logged / elapsedDays) * days : logged;
  const pct = state.goal > 0 ? (logged / state.goal) * 100 : 0;

  return { keys, byMonth, byMonthStream, logged, byStream, days, elapsedDays, daysLeft,
           expected, remaining, gap, perDay, projection, pct, startD, endD };
}

/* ---------- render ---------- */
function render(){
  const c = compute();
  document.getElementById('sampleBanner').hidden = !state.entries.some(e => e.sample);
  renderHead(c);
  renderProgress(c);
  renderGap();
  renderStreams(c);
  renderCumChart(c);
  renderMonthChart(c);
  renderMonthTable(c);
  renderMilestones();
  renderEntries();
  renderSelects();
}

function renderHead(c){
  document.getElementById('rangeLabel').textContent = monthLong(c.keys[0]) + ' → ' + monthLong(c.keys[c.keys.length - 1]);
  document.getElementById('appTitle').textContent = fmtC(state.goal) + ' Tracker';
  document.getElementById('kpiTarget').textContent = fmtC(state.goal);
  document.getElementById('kpiTargetHint').textContent = state.months + '-month goal · plan says ' + fmtC(planTotal());
  document.getElementById('kpiLogged').textContent = fmtC(c.logged);
  document.getElementById('kpiLoggedHint').textContent = state.entries.length + ' entries · ' + fmt(c.logged);
  document.getElementById('kpiRemaining').textContent = fmtC(c.remaining);
  document.getElementById('kpiRemainingHint').textContent = c.daysLeft + ' days of the plan left';
  document.getElementById('kpiPct').textContent = c.pct.toFixed(1) + '%';
  document.getElementById('kpiPctHint').textContent = fmtC(c.logged) + ' of ' + fmtC(state.goal);
}

function renderProgress(c){
  const fill = document.getElementById('progressFill');
  fill.style.width = Math.min(100, c.pct) + '%';
  const pacePct = state.goal > 0 ? (c.expected / state.goal) * 100 : 0;
  document.getElementById('paceMark').style.left = 'calc(' + Math.min(100, Math.max(0, pacePct)) + '% - 1px)';

  const badge = document.getElementById('paceBadge');
  const ahead = c.gap >= 0;
  badge.className = 'paceBadge ' + (c.expected === 0 ? '' : ahead ? 'ahead' : 'behind');
  badge.textContent = c.expected === 0 ? 'Plan starts ' + monthLong(c.keys[0])
    : ahead ? 'Ahead by ' + fmtC(c.gap) : 'Behind by ' + fmtC(Math.abs(c.gap));

  document.getElementById('paceText').textContent =
    'To be on pace today you should have ' + fmt(c.expected) + ' logged — you have ' + fmt(c.logged) + '.';

  document.getElementById('perDay').textContent = fmtC(c.perDay);
  const planLeft = Math.max(0, planTotal() - c.logged);
  document.getElementById('perDayPlan').textContent = fmtC(c.daysLeft > 0 ? planLeft / c.daysLeft : planLeft);
  document.getElementById('perWeek').textContent = fmtC(c.perDay * 7);
  document.getElementById('projection').textContent = fmtC(c.projection);
  document.getElementById('daysLeft').textContent = c.daysLeft;
}

/* plan total if the scalable streams grow at g (fraction) every month */
function totalWithGrowth(g){
  let t = 0;
  state.streams.forEach(s => {
    const m0 = num(s.monthly);
    if (s.scalable){ for (let i = 0; i < state.months; i++) t += m0 * Math.pow(1 + g, i); }
    else t += m0 * state.months;
  });
  return t;
}
/* monthly growth the scalable streams need to reach `goal` — null = impossible */
function growthForGoal(goal){
  if (totalWithGrowth(0) >= goal) return 0;
  if (totalWithGrowth(5) < goal) return null;
  let lo = 0, hi = 5;
  for (let i = 0; i < 90; i++){ const mid = (lo + hi) / 2; if (totalWithGrowth(mid) < goal) lo = mid; else hi = mid; }
  return (lo + hi) / 2;
}

function gapFacts(){
  const pt = planTotal();
  const perMonth = state.months > 0 ? pt / state.months : 0;
  const needed = state.months > 0 ? state.goal / state.months : 0;
  const short = state.goal - pt;
  const mult = perMonth > 0 ? needed / perMonth : 0;
  const monthsNeeded = perMonth > 0 ? Math.ceil(state.goal / perMonth) : 0;
  const etaKey = monthsNeeded ? addMonthKey(state.start, monthsNeeded - 1) : null;
  const growth = growthForGoal(state.goal);
  const scalable = state.streams.filter(s => s.scalable).map(s => s.name);
  return { pt, perMonth, needed, short, mult, monthsNeeded, etaKey, growth, scalable };
}

function renderGap(){
  const g = gapFacts();
  const endKey = monthKeys()[state.months - 1];
  document.getElementById('gapGrid').innerHTML = `
    <div><span>Plan delivers</span><strong>${fmtC(g.pt)}</strong>
      <div class="muted tiny" style="margin-top:4px">${fmtC(g.perMonth)}/mo × ${state.months}</div></div>
    <div><span>Goal</span><strong>${fmtC(state.goal)}</strong>
      <div class="muted tiny" style="margin-top:4px">needs ${fmtC(g.needed)}/mo</div></div>
    <div><span>${g.short > 0 ? 'Shortfall' : 'Headroom'}</span>
      <strong style="color:${g.short > 0 ? 'var(--warn)' : 'var(--good)'}">${g.short > 0 ? '−' : '+'}${fmtC(Math.abs(g.short))}</strong>
      <div class="muted tiny" style="margin-top:4px">${g.mult ? g.mult.toFixed(1) + '× your current rate' : '—'}</div></div>
    <div><span>Time at today's rate</span><strong>${g.monthsNeeded} mo</strong>
      <div class="muted tiny" style="margin-top:4px">${g.etaKey ? 'around ' + monthLong(g.etaKey) : '—'}</div></div>`;

  const tol = Math.max(1000, state.goal * 0.002); // within 0.2% counts as on the nose
  document.getElementById('gapLine').innerHTML = (Math.abs(g.short) <= tol)
    ? (Math.abs(state.goal - g.pt) <= tol
        ? `Plan and goal match: <b>${fmtC(g.pt)}</b> by <b>${monthLong(endKey)}</b>. Nothing left to fix but execution — log the money as it comes in.`
        : `Your plan lands on <b>${fmtC(g.pt)}</b> by <b>${monthLong(endKey)}</b>, which <i>is</i> the <b>${fmtC(state.goal)}</b> goal. Nothing to fix but execution.`)
    : g.short < 0
    ? `Your plan of <b>${fmtC(g.perMonth)}/month</b> clears the <b>${fmtC(state.goal)}</b> goal with <b>${fmtC(Math.abs(g.short))}</b> to spare by <b>${monthLong(endKey)}</b>. Now the job is just not slipping.`
    : `At <b>${fmtC(g.perMonth)}/month</b> average the plan lands at <b>${fmtC(g.pt)}</b> by <b>${monthLong(endKey)}</b> — <b>${fmtC(g.short)} short</b> of ${fmtC(state.goal)}. Closing that gap in ${state.months} months takes <b>${fmtC(g.needed)}/month</b> (${g.mult.toFixed(1)}× the plan's average) or <b>${g.growth === null ? 'more growth than +500% a month — it is not reachable from here' : '+' + (g.growth * 100).toFixed(1) + '% growth every month on ' + g.scalable.join(' + ')}</b>. Keep today's rate and you get there around <b>${g.etaKey ? monthLong(g.etaKey) : '—'}</b>.`;

  document.getElementById('btnGoalToPlan').textContent = `↓ Set goal to ${fmtC(g.pt)} (what the plan delivers)`;
  document.getElementById('btnGoalToTime').textContent = `→ Keep ${fmtC(state.goal)}, go ${g.monthsNeeded} months`;
  const gb = document.getElementById('btnGoalToGrowth');
  gb.textContent = g.growth === null
    ? '↗ Growth can\'t reach it'
    : `↗ Keep both, run +${(g.growth * 100).toFixed(1)}%/mo on ${g.scalable.join(' + ')}`;
  gb.disabled = g.growth === null;
}

function renderStreams(c){
  const el = document.getElementById('streams');
  el.innerHTML = state.streams.map(s => {
    const got = c.byStream[s.id] || 0;
    const target = streamPlanTotal(s);
    const pct = target > 0 ? (got / target) * 100 : 0;
    const left = Math.max(0, target - got);
    const n = state.entries.filter(e => e.stream === s.id).length;
    return `<div class="stream">
      <div class="streamTop">
        <span class="streamName"><i class="dot" style="background:${s.color}"></i>${esc(s.name)}</span>
        <span class="streamPct" style="color:${s.color}">${pct.toFixed(0)}%</span>
      </div>
      <div class="bar"><div class="fill" style="width:${Math.min(100, pct)}%;--c:${s.color}"></div></div>
      <div class="streamNums">
        <span>${fmtC(got)} / ${fmtC(target)}</span>
        <span>${fmtC(left)} to go · ${n} ${n === 1 ? 'entry' : 'entries'}</span>
      </div>
      <div class="streamNums"><span class="muted">plan ${fmtC(num(s.monthly))}/mo${num(s.growth) ? ' · +' + s.growth + '% growth' : ''}</span></div>
    </div>`;
  }).join('');
}

/* ---------- SVG charts ---------- */
const SVG = 'http://www.w3.org/2000/svg';
function svgEl(tag, attrs, text){
  const n = document.createElementNS(SVG, tag);
  for (const k in attrs) n.setAttribute(k, attrs[k]);
  if (text != null) n.textContent = text;
  return n;
}
function chartBase(host, pad){
  const W = 600, H = 230;
  host.innerHTML = '';
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, preserveAspectRatio: 'xMidYMid meet' });
  host.appendChild(svg);
  const iw = W - pad.l - pad.r, ih = H - pad.t - pad.b;
  return { svg, W, H, pad, iw, ih, x: v => pad.l + v * iw, y: f => pad.t + (1 - f) * ih };
}

function renderCumChart(c){
  const host = document.getElementById('cumChart');
  const g = chartBase(host, { l: 54, r: 14, t: 18, b: 32 });
  const n = c.keys.length;

  // gridlines
  for (let i = 0; i <= 4; i++){
    const f = i / 4;
    g.svg.appendChild(svgEl('line', { x1: g.pad.l, x2: g.W - g.pad.r, y1: g.y(f), y2: g.y(f), stroke: '#22304f', 'stroke-width': 1 }));
    const t = svgEl('text', { x: g.pad.l - 8, y: g.y(f) + 4, 'text-anchor': 'end', fill: '#8fa1c4', 'font-size': 10 }, fmtC(state.goal * f));
    g.svg.appendChild(t);
  }

  // plan line: cumulative targets at each month end
  let cum = 0;
  const planPts = [[0, 0]];
  c.keys.forEach((k, i) => { cum += monthlyTarget(k); planPts.push([(i + 1) / n, cum / state.goal]); });

  // actual line: month-end cumulative for finished months, plus today's position
  let a = 0;
  const actPts = [[0, 0]];
  const now = new Date();
  c.keys.forEach((k, i) => {
    const mEnd = monthDate(k, daysInMonth(k));
    a += c.byMonth[i];
    if (now > mEnd) actPts.push([(i + 1) / n, a / state.goal]);
    else if (monthKey(now) === k){
      const frac = now.getDate() / daysInMonth(k);
      actPts.push([(i + frac) / n, a / state.goal]);
    }
  });

  const toXY = p => [g.x(p[0]), g.y(Math.max(0, Math.min(1.05, p[1])))];

  // area under actual
  if (actPts.length > 1){
    const d = actPts.map(toXY);
    const area = `M ${d[0][0]} ${g.y(0)} ` + d.map(p => `L ${p[0]} ${p[1]}`).join(' ') + ` L ${d[d.length-1][0]} ${g.y(0)} Z`;
    g.svg.appendChild(svgEl('path', { d, fill: '#34d39922', stroke: 'none' }));
  }
  g.svg.appendChild(svgEl('polyline', {
    points: planPts.map(p => toXY(p).join(',')).join(' '), fill: 'none',
    stroke: '#5b739c', 'stroke-width': 2, 'stroke-dasharray': '5 4'
  }));
  g.svg.appendChild(svgEl('polyline', {
    points: actPts.map(p => toXY(p).join(',')).join(' '), fill: 'none',
    stroke: '#34d399', 'stroke-width': 2.5, 'stroke-linejoin': 'round', 'stroke-linecap': 'round'
  }));
  const last = toXY(actPts[actPts.length - 1]);
  g.svg.appendChild(svgEl('circle', { cx: last[0], cy: last[1], r: 4.5, fill: '#34d399' }));

  // today marker
  const todayPct = state.goal > 0 ? c.expected / state.goal : 0;
  const tx = g.x(Math.min(1, Math.max(0, c.elapsedDays / c.days)));
  g.svg.appendChild(svgEl('line', { x1: tx, x2: tx, y1: g.pad.t, y2: g.H - g.pad.b, stroke: '#ffffff55', 'stroke-width': 1, 'stroke-dasharray': '3 3' }));

  // x labels
  c.keys.forEach((k, i) => {
    g.svg.appendChild(svgEl('text', {
      x: g.x((i + 0.5) / n), y: g.H - g.pad.b + 16, 'text-anchor': 'middle', fill: '#8fa1c4', 'font-size': 10
    }, monthLabel(k)));
  });

  document.getElementById('cumLegend').innerHTML =
    `<span><i style="background:#34d399"></i>Actual ${fmtC(c.logged)}</span>
     <span><i style="background:#5b739c"></i>Plan ${fmtC(state.goal)}</span>
     <span class="muted">Should be at ${fmtC(c.expected)} today (${(todayPct*100).toFixed(0)}%)</span>`;
}

function renderMonthChart(c){
  const host = document.getElementById('monthChart');
  const g = chartBase(host, { l: 54, r: 14, t: 18, b: 32 });
  const n = c.keys.length;
  const maxV = Math.max(state.goal / n, ...c.byMonth, ...c.keys.map(monthlyTarget)) * 1.15 || 1;
  const y = v => g.pad.t + (1 - Math.max(0, Math.min(1, v / maxV))) * g.ih;

  for (let i = 0; i <= 4; i++){
    const f = i / 4;
    g.svg.appendChild(svgEl('line', { x1: g.pad.l, x2: g.W - g.pad.r, y1: y(maxV * f), y2: y(maxV * f), stroke: '#22304f', 'stroke-width': 1 }));
    g.svg.appendChild(svgEl('text', { x: g.pad.l - 8, y: y(maxV * f) + 4, 'text-anchor': 'end', fill: '#8fa1c4', 'font-size': 10 }, fmtC(maxV * f)));
  }

  const slot = g.iw / n, bw = Math.min(46, slot * 0.5);
  c.keys.forEach((k, i) => {
    const cx = g.pad.l + slot * (i + 0.5);
    let acc = 0;
    state.streams.forEach(s => {
      const v = c.byMonthStream[i][s.id] || 0;
      if (v <= 0) return;
      const y1 = y(acc), y2 = y(acc + v);
      const rect = svgEl('rect', { x: cx - bw/2, y: y2, width: bw, height: Math.max(1, y1 - y2), fill: s.color, rx: 2 });
      rect.appendChild(svgEl('title', {}, `${s.name} · ${monthLong(k)} · ${fmt(v)}`));
      g.svg.appendChild(rect);
      acc += v;
    });
    if (c.byMonth[i] > 0){
      g.svg.appendChild(svgEl('text', { x: cx, y: y(c.byMonth[i]) - 6, 'text-anchor': 'middle', fill: '#e8eefb', 'font-size': 10, 'font-weight': 700 }, fmtC(c.byMonth[i])));
    }
    // target marker
    const ty = y(monthlyTarget(k));
    g.svg.appendChild(svgEl('line', { x1: cx - bw/2 - 4, x2: cx + bw/2 + 4, y1: ty, y2: ty, stroke: '#60a5fa', 'stroke-width': 2, 'stroke-dasharray': '4 3' }));
    g.svg.appendChild(svgEl('text', { x: cx, y: g.H - g.pad.b + 16, 'text-anchor': 'middle', fill: '#8fa1c4', 'font-size': 10 }, monthLabel(k)));
  });

  document.getElementById('monthLegend').innerHTML =
    state.streams.map(s => `<span><i style="background:${s.color}"></i>${esc(s.name)}</span>`).join('') +
    `<span><i style="background:#60a5fa"></i>Monthly target</span>`;
}

/* ---------- tables ---------- */
function renderMonthTable(c){
  const rows = c.keys.map((k, i) => {
    const t = monthlyTarget(k), got = c.byMonth[i];
    const diff = got - t;
    const isPast = new Date() > monthDate(k, daysInMonth(k));
    const isNow = monthKey(new Date()) === k;
    const cls = isPast ? (got >= t ? 'hit' : 'miss') : 'future';
    const label = isPast ? (got >= t ? 'Hit' : 'Miss') : isNow ? 'In progress' : 'Upcoming';
    const cells = state.streams.map(s => `<td class="num" style="color:${c.byMonthStream[i][s.id] ? s.color : '#5c6f96'}">${fmtC(c.byMonthStream[i][s.id] || 0)}</td>`).join('');
    return `<tr${isNow ? ' style="background:#16213c"' : ''}>
      <td><strong>${monthLong(k)}</strong></td>
      <td class="num">${fmtC(t)}</td>
      <td class="num"><strong>${fmtC(got)}</strong></td>
      ${cells}
      <td class="num" style="color:${diff >= 0 ? 'var(--good)' : 'var(--warn)'}">${diff >= 0 ? '+' : '−'}${fmtC(Math.abs(diff))}</td>
      <td><span class="pill ${cls}">${label}</span></td>
    </tr>`;
  }).join('');

  const tTot = c.keys.reduce((a, k) => a + monthlyTarget(k), 0);
  const gTot = c.byMonth.reduce((a, b) => a + b, 0);
  const streamTotals = state.streams.map(s => `<td class="num" style="color:${s.color}"><strong>${fmtC(c.byStream[s.id] || 0)}</strong></td>`).join('');
  const drift = tTot - state.goal;
  const driftTag = drift === 0 ? '' : ` <span class="muted">(${drift > 0 ? '+' : '−'}${fmtC(Math.abs(drift))} vs goal)</span>`;

  document.getElementById('monthTable').innerHTML = `
    <thead><tr>
      <th>Month</th><th class="num">Target</th><th class="num">Logged</th>
      ${state.streams.map(s => `<th class="num">${esc(s.name)}</th>`).join('')}
      <th class="num">vs target</th><th>Status</th>
    </tr></thead>
    <tbody>${rows}
    <tr style="border-top:2px solid var(--line)">
      <td><strong>Total</strong></td>
      <td class="num"><strong>${fmtC(tTot)}</strong>${driftTag}</td>
      <td class="num"><strong>${fmtC(gTot)}</strong></td>
      ${streamTotals}
      <td class="num" style="color:${gTot - tTot >= 0 ? 'var(--good)' : 'var(--warn)'}">${gTot - tTot >= 0 ? '+' : '−'}${fmtC(Math.abs(gTot - tTot))}</td>
      <td></td>
    </tr></tbody>`;
}

function renderEntries(){
  const f = document.getElementById('filterStream').value || 'all';
  const list = state.entries
    .filter(e => f === 'all' || e.stream === f)
    .slice().sort((a, b) => b.date.localeCompare(a.date) || b.id.localeCompare(a.id));

  if (!list.length){
    document.getElementById('entryTable').innerHTML = `<tbody><tr><td class="empty">No entries yet — log your first one above.</td></tr></tbody>`;
    return;
  }
  const rows = list.slice(0, 60).map(e => {
    const s = state.streams.find(x => x.id === e.stream);
    return `<tr>
      <td>${prettyDate(e.date)}</td>
      <td><span class="streamName"><i class="dot" style="background:${s ? s.color : '#666'}"></i>${esc(s ? s.name : e.stream)}</span></td>
      <td class="muted">${esc(e.note || '')}</td>
      <td class="num"><strong>${fmt(num(e.amount))}</strong></td>
      <td class="num"><button class="del" data-del="${e.id}" title="Delete">×</button></td>
    </tr>`;
  }).join('');
  const more = list.length > 60 ? `<tr><td colspan="5" class="muted" style="text-align:center">Showing latest 60 of ${list.length}</td></tr>` : '';
  document.getElementById('entryTable').innerHTML =
    `<thead><tr><th>Date</th><th>Stream</th><th>Note</th><th class="num">Amount</th><th></th></tr></thead><tbody>${rows}${more}</tbody>`;
}

function renderMilestones(){
  const el = document.getElementById('milestones');
  if (!state.milestones.length){
    el.innerHTML = `<li class="muted">No milestones yet — add the things that move the money.</li>`;
    return;
  }
  const today = todayISO();
  el.innerHTML = state.milestones
    .slice().sort((a, b) => (a.done - b.done) || (a.due || '9999').localeCompare(b.due || '9999'))
    .map(m => `<li class="${m.done ? 'done' : ''}">
      <input type="checkbox" data-ms="${m.id}" ${m.done ? 'checked' : ''} />
      <span class="title">${esc(m.title)}</span>
      ${m.due ? `<span class="due ${!m.done && m.due < today ? 'late' : ''}">${prettyDate(m.due)}${!m.done && m.due < today ? ' · overdue' : ''}</span>` : ''}
      <button class="del" data-msdel="${m.id}" title="Delete">×</button>
    </li>`).join('');
}

function renderSelects(){
  const opts = state.streams.map(s => `<option value="${s.id}">${esc(s.name)}</option>`).join('');
  const cur = document.getElementById('inStream').value;
  document.getElementById('inStream').innerHTML = opts;
  if (cur && state.streams.some(s => s.id === cur)) document.getElementById('inStream').value = cur;

  const f = document.getElementById('filterStream');
  const fv = f.value;
  f.innerHTML = `<option value="all">All streams</option>` + opts;
  if (fv) f.value = fv;

  document.getElementById('quickChips').innerHTML =
    [100000, 200000, 500000, 1000000, 2000000, 5000000].map(v => `<button class="chip" data-amt="${v}">+${fmtC(v)}</button>`).join('');
}

/* ---------- settings ---------- */
function renderSettings(){
  document.getElementById('setGoal').value = state.goal;
  document.getElementById('setStart').value = state.start;
  document.getElementById('setMonths').value = state.months;

  document.getElementById('setStreams').innerHTML = state.streams.map((s, i) => `
    <div class="row" data-si="${i}">
      <input type="color" value="${s.color}" data-sk="color" />
      <input type="text" value="${esc(s.name)}" data-sk="name" />
      <input type="number" min="0" step="50000" value="${num(s.monthly)}" data-sk="monthly" />
      <input type="number" min="0" max="200" step="1" value="${num(s.growth)}" data-sk="growth" />
      <label class="chk" title="Can this stream scale? Growth is only pushed onto ticked streams.">
        <input type="checkbox" data-sk="scalable" ${s.scalable ? 'checked' : ''} /> grows
      </label>
    </div>`).join('');

  document.getElementById('setMonths').innerHTML = monthKeys().map(k => `
    <div class="row"><label>${monthLong(k)}</label>
      <input type="number" min="0" step="100000" value="${monthlyTarget(k)}" data-mk="${k}" /></div>`).join('');
}

/* ---------- events ---------- */
document.getElementById('logForm').addEventListener('submit', e => {
  e.preventDefault();
  const amount = num(document.getElementById('inAmount').value);
  if (amount <= 0) return;
  state.entries.push({
    id: uid(),
    date: document.getElementById('inDate').value || todayISO(),
    stream: document.getElementById('inStream').value,
    amount,
    note: document.getElementById('inNote').value.trim()
  });
  save(); render();
  document.getElementById('inAmount').value = '';
  document.getElementById('inNote').value = '';
  document.getElementById('inAmount').focus();
  toast('Logged ' + fmt(amount));
});

document.getElementById('quickChips').addEventListener('click', e => {
  const b = e.target.closest('[data-amt]'); if (!b) return;
  const el = document.getElementById('inAmount');
  el.value = num(el.value) + num(b.dataset.amt);
  el.focus();
});

document.getElementById('filterStream').addEventListener('change', renderEntries);

document.getElementById('entryTable').addEventListener('click', e => {
  const b = e.target.closest('[data-del]'); if (!b) return;
  state.entries = state.entries.filter(x => x.id !== b.dataset.del);
  save(); render(); toast('Entry deleted');
});

document.getElementById('milestoneForm').addEventListener('submit', e => {
  e.preventDefault();
  const t = document.getElementById('msTitle').value.trim();
  if (!t) return;
  state.milestones.push({ id: uid(), title: t, due: document.getElementById('msDue').value || '', done: false });
  save(); render();
  document.getElementById('msTitle').value = ''; document.getElementById('msDue').value = '';
});

document.getElementById('milestones').addEventListener('click', e => {
  const del = e.target.closest('[data-msdel]');
  if (del){ state.milestones = state.milestones.filter(m => m.id !== del.dataset.msdel); save(); render(); return; }
});
document.getElementById('milestones').addEventListener('change', e => {
  const cb = e.target.closest('[data-ms]'); if (!cb) return;
  const m = state.milestones.find(x => x.id === cb.dataset.ms);
  if (m){ m.done = cb.checked; save(); renderMilestones(); }
});

document.getElementById('btnClearSample').addEventListener('click', () => {
  state.entries = state.entries.filter(e => !e.sample);
  save(); render(); toast('Sample data cleared — start logging real money');
});

/* settings */
const drawer = document.getElementById('drawer');
document.getElementById('btnSettings').addEventListener('click', () => { renderSettings(); drawer.hidden = false; });
document.getElementById('btnCloseSettings').addEventListener('click', () => drawer.hidden = true);
drawer.addEventListener('click', e => { if (e.target === drawer) drawer.hidden = true; });

document.getElementById('setGoal').addEventListener('change', e => { state.goal = Math.max(0, num(e.target.value)); save(); render(); renderSettings(); });
document.getElementById('setStart').addEventListener('change', e => { if (e.target.value) { state.start = e.target.value; renderSettings(); } save(); render(); });
document.getElementById('setMonths').addEventListener('change', e => {
  state.months = Math.max(1, Math.min(36, Math.round(num(e.target.value)) || 6));
  save(); render(); renderSettings();
});
document.getElementById('setStreams').addEventListener('change', e => {
  const row = e.target.closest('[data-si]'); if (!row) return;
  const s = state.streams[+row.dataset.si]; if (!s) return;
  const k = e.target.dataset.sk;
  if (k === 'scalable') s.scalable = e.target.checked;
  else s[k] = (k === 'monthly' || k === 'growth') ? Math.max(0, num(e.target.value)) : e.target.value;
  save(); render();
});
document.getElementById('setMonths').addEventListener('change', e => {
  const k = e.target.dataset.mk; if (!k) return;
  state.monthlyTargets[k] = Math.max(0, num(e.target.value));
  save(); render();
});
/* the three ways out of a goal the plan can't reach */
document.getElementById('btnGoalToPlan').addEventListener('click', () => {
  const pt = Math.round(planTotal());
  state.goal = pt; save(); render(); renderSettings();
  toast('Goal set to ' + fmtC(pt) + ' — the honest 6-month number');
});
document.getElementById('btnGoalToTime').addEventListener('click', () => {
  const n = Math.min(36, Math.max(1, gapFacts().monthsNeeded));
  state.months = n; save(); render(); renderSettings();
  toast('Horizon stretched to ' + n + ' months → ' + monthLong(monthKeys()[n - 1]) + (gapFacts().monthsNeeded > 36 ? ' (capped at 36)' : ''));
});
document.getElementById('btnGoalToGrowth').addEventListener('click', () => {
  const g = gapFacts().growth;
  if (g == null){
    toast('Not reachable: even +500%/month on ' + gapFacts().scalable.join(' + ') + ' misses ' + fmtC(state.goal));
    return;
  }
  const gp = Math.round(g * 1000) / 10; // percent, one decimal
  state.monthlyTargets = {};
  state.streams.forEach(s => { if (s.scalable) s.growth = gp; });
  save(); render(); renderSettings();
  toast('+' + gp.toFixed(1) + '%/mo applied to ' + gapFacts().scalable.join(' + ') + '. Job and investing left flat.');
});

document.getElementById('btnSpread').addEventListener('click', () => {
  state.monthlyTargets = {};
  save(); render(); renderSettings();
  toast('Monthly targets now follow your stream rates (' + fmtC(planTotal() / state.months) + '/mo)');
});
document.getElementById('btnReset').addEventListener('click', () => {
  if (!confirm('Delete all entries, milestones and settings? This cannot be undone.')) return;
  localStorage.removeItem(STORE_KEY);
  state = seed(); render(); renderSettings(); toast('Reset done');
});

/* data io */
document.getElementById('btnExport').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = '60m-tracker-' + todayISO() + '.json';
  a.click(); URL.revokeObjectURL(a.href);
  toast('Exported');
});
document.getElementById('btnImport').addEventListener('click', () => document.getElementById('fileInput').click());
document.getElementById('fileInput').addEventListener('change', e => {
  const f = e.target.files[0]; if (!f) return;
  const r = new FileReader();
  r.onload = () => {
    try {
      const s = JSON.parse(r.result);
      if (!s || !Array.isArray(s.streams)) throw 0;
      state = Object.assign(defaults(), s); save(); render(); toast('Imported');
    } catch (err){ toast('That file did not look right'); }
  };
  r.readAsText(f);
  e.target.value = '';
});
document.getElementById('btnPrint').addEventListener('click', () => window.print());
document.addEventListener('keydown', e => { if (e.key === 'Escape') drawer.hidden = true; });

/* toast */
let tid;
function toast(msg){
  let t = document.querySelector('.toast');
  if (!t){ t = document.createElement('div'); t.className = 'toast'; document.body.appendChild(t); }
  t.textContent = msg; t.classList.add('show');
  clearTimeout(tid); tid = setTimeout(() => t.classList.remove('show'), 2200);
}

/* ---------- install / offline ---------- */
let deferredPrompt = null;
const installBtn = document.getElementById('btnInstall');

window.addEventListener('beforeinstallprompt', e => {
  e.preventDefault();               // we trigger it from our own button
  deferredPrompt = e;
  installBtn.hidden = false;
});

installBtn.addEventListener('click', async () => {
  if (!deferredPrompt) return;
  installBtn.hidden = true;
  deferredPrompt.prompt();
  const { outcome } = await deferredPrompt.userChoice;
  deferredPrompt = null;
  toast(outcome === 'accepted' ? 'Installing — it will be on your home screen' : 'Install cancelled');
});

window.addEventListener('appinstalled', () => {
  installBtn.hidden = true;
  toast('Installed. Open it from your home screen.');
});

/* iPhone/iPad: Safari fires no install event, so say it in words */
(function iosHint(){
  const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent) ||
              (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const standalone = window.navigator.standalone ||
    (window.matchMedia ? window.matchMedia('(display-mode: standalone)').matches : false);
  const dismissed = (() => { try { return localStorage.getItem('gide26.iosHint') === 'off'; } catch(e){ return false; } })();
  if (!iOS || standalone || dismissed) return;
  document.getElementById('iosHint').hidden = false;
  document.getElementById('btnHideIosHint').addEventListener('click', () => {
    document.getElementById('iosHint').hidden = true;
    try { localStorage.setItem('gide26.iosHint', 'off'); } catch(e){}
  });
})();

/* service worker — only over http(s), never from a file:// double-click */
if ('serviceWorker' in navigator && /^https?:$/.test(location.protocol)) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  });
}

/* ---------- boot ---------- */
document.getElementById('inDate').value = todayISO();
render();
