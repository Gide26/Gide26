/**
 * Charts drawn by hand as SVG — no chart library.
 * Every chart measures its container, re-renders on resize, and supports
 * touch as well as mouse, which matters because most views happen on a phone.
 */
import { moneyCompact, num, esc, pct } from './format.js';

const NS = 'http://www.w3.org/2000/svg';
const PALETTE = ['#B4531F', '#E8A33D', '#2F7D4F', '#2A6089', '#8E5BA6', '#B3382C', '#5C8A6A', '#C97B3C'];

let uid = 0;
const nextId = (p) => `${p}${++uid}`;

const svgEl = (tag, attrs = {}) => {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v !== null && v !== undefined) e.setAttribute(k, v);
  return e;
};

/** Round an axis maximum up to 1, 2, 2.5, 5 or 10 × 10^n. */
function niceScale(min, max, ticks = 4) {
  if (!Number.isFinite(min) || !Number.isFinite(max)) return { min: 0, max: 1, step: 0.25 };
  if (min === max) { max = min + (Math.abs(min) || 1); min = Math.min(0, min); }
  const raw = (max - min) / ticks;
  const mag = 10 ** Math.floor(Math.log10(Math.abs(raw) || 1));
  const norm = raw / mag;
  const step = (norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 2.5 ? 2.5 : norm <= 5 ? 5 : 10) * mag;
  return { min: Math.floor(min / step) * step, max: Math.ceil(max / step) * step, step };
}

const fmtTick = (v, kind) => (kind === 'money' ? moneyCompact(v) : num(v, Math.abs(v) < 10 ? 1 : 0));

/** Re-render on resize, debounced. Returns a cleanup function. */
function observe(el, draw) {
  let frame = 0;
  const schedule = () => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(() => { if (el.isConnected && el.clientWidth > 0) draw(); });
  };
  schedule();
  const ro = new ResizeObserver(schedule);
  ro.observe(el);
  return () => { ro.disconnect(); cancelAnimationFrame(frame); };
}

function tooltipLayer(el) {
  el.style.position = 'relative';
  let tip = el.querySelector(':scope > .chart-tip');
  if (!tip) {
    tip = document.createElement('div');
    tip.className = 'chart-tip';
    tip.style.cssText = 'position:absolute;pointer-events:none;opacity:0;transition:opacity .12s;'
      + 'background:#241A13;color:#F6EDE3;padding:7px 10px;border-radius:9px;font-size:12px;'
      + 'font-weight:600;white-space:nowrap;box-shadow:0 8px 24px rgba(0,0,0,.28);z-index:5;'
      + 'transform:translate(-50%,-100%);line-height:1.45';
    el.appendChild(tip);
  }
  return tip;
}

/* ------------------------------------------------------------------ *
 * Multi-series line / area chart
 * ------------------------------------------------------------------ */

/**
 * @param {HTMLElement} el
 * @param {{labels:string[], series:{name:string,values:number[],color?:string,area?:boolean,dashed?:boolean}[],
 *          kind?:'money'|'number', height?:number, yTicks?:number, formatTip?:Function}} cfg
 */
export function lineChart(el, cfg) {
  if (!el) return () => {};
  const { labels = [], series = [], kind = 'money', height = 200, yTicks = 4, formatTip } = cfg;
  const tip = tooltipLayer(el);
  el.querySelectorAll('svg').forEach((s) => s.remove());

  if (!labels.length || !series.some((s) => s.values?.length)) {
    el.innerHTML = '<div class="empty" style="padding:26px 12px"><p>No data for this period</p></div>';
    return () => {};
  }

  const draw = () => {
    el.querySelectorAll('svg').forEach((s) => s.remove());
    const W = Math.max(280, el.clientWidth);
    const H = height;
    const pad = { l: kind === 'money' ? 48 : 34, r: 12, t: 12, b: 24 };
    const iw = W - pad.l - pad.r;
    const ih = H - pad.t - pad.b;

    const all = series.flatMap((s) => s.values.map(Number).filter(Number.isFinite));
    const hasNeg = all.some((v) => v < 0);
    const { min, max, step } = niceScale(Math.min(0, ...all), Math.max(...all, 0), yTicks);

    const x = (i) => pad.l + (labels.length === 1 ? iw / 2 : (i / (labels.length - 1)) * iw);
    const y = (v) => pad.t + ih - ((v - min) / (max - min || 1)) * ih;

    const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img' });
    const gradId = nextId('grad');

    // gradient for the first area series
    const defs = svgEl('defs');
    const grad = svgEl('linearGradient', { id: gradId, x1: 0, y1: 0, x2: 0, y2: 1 });
    grad.append(svgEl('stop', { offset: '0%', 'stop-color': series[0]?.color || PALETTE[0], 'stop-opacity': .26 }));
    grad.append(svgEl('stop', { offset: '100%', 'stop-color': series[0]?.color || PALETTE[0], 'stop-opacity': 0 }));
    defs.append(grad);
    svg.append(defs);

    // horizontal grid + y labels
    for (let v = min; v <= max + step / 2; v += step) {
      const yy = y(v);
      svg.append(svgEl('line', { x1: pad.l, y1: yy, x2: W - pad.r, y2: yy,
        class: v === 0 ? 'axis-line' : 'grid-line' }));
      const t = svgEl('text', { x: pad.l - 7, y: yy + 3.5, 'text-anchor': 'end' });
      t.textContent = fmtTick(v, kind);
      svg.append(t);
    }

    // x labels — at most ~7, always including first and last
    const every = Math.max(1, Math.ceil(labels.length / 7));
    labels.forEach((lb, i) => {
      if (i % every !== 0 && i !== labels.length - 1) return;
      const t = svgEl('text', { x: x(i), y: H - 6, 'text-anchor': i === 0 ? 'start' : (i === labels.length - 1 ? 'end' : 'middle') });
      t.textContent = lb;
      svg.append(t);
    });

    // series
    series.forEach((s, si) => {
      const color = s.color || PALETTE[si % PALETTE.length];
      const pts = s.values.map((v, i) => [x(i), y(Number(v) || 0)]);
      const d = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
      if (s.area !== false && si === 0 && !hasNeg) {
        svg.append(svgEl('path', { d: `${d} L${pts[pts.length - 1][0].toFixed(1)} ${y(Math.max(0, min)).toFixed(1)} L${pts[0][0].toFixed(1)} ${y(Math.max(0, min)).toFixed(1)} Z`, fill: `url(#${gradId})` }));
      }
      svg.append(svgEl('path', { d, class: 'line-path', stroke: color,
        'stroke-dasharray': s.dashed ? '5 4' : null, fill: 'none' }));
      if (pts.length <= 34) {
        pts.forEach((p) => svg.append(svgEl('circle', { cx: p[0], cy: p[1], r: 2.6, class: 'dot', stroke: color })));
      }
    });

    // hover / touch guide
    const guide = svgEl('line', { y1: pad.t, y2: pad.t + ih, class: 'axis-line', opacity: 0 });
    svg.append(guide);
    const markers = series.map((s, si) => svgEl('circle', { r: 4.2, fill: '#fff',
      stroke: s.color || PALETTE[si % PALETTE.length], 'stroke-width': 2.4, opacity: 0 }));
    markers.forEach((m) => svg.append(m));

    const hit = svgEl('rect', { x: pad.l, y: pad.t, width: iw, height: ih, fill: 'transparent', style: 'cursor:crosshair' });
    svg.append(hit);

    const nearest = (clientX) => {
      const box = svg.getBoundingClientRect();
      const rel = ((clientX - box.left) / box.width) * W;
      const i = Math.round(((rel - pad.l) / (iw || 1)) * (labels.length - 1));
      return Math.max(0, Math.min(labels.length - 1, i));
    };

    const show = (clientX) => {
      const i = nearest(clientX);
      guide.setAttribute('x1', x(i)); guide.setAttribute('x2', x(i)); guide.setAttribute('opacity', 1);
      series.forEach((s, si) => {
        markers[si].setAttribute('cx', x(i));
        markers[si].setAttribute('cy', y(Number(s.values[i]) || 0));
        markers[si].setAttribute('opacity', 1);
      });
      const rows = series.map((s, si) =>
        `<div style="display:flex;gap:8px;align-items:center"><span style="width:8px;height:8px;border-radius:2px;background:${s.color || PALETTE[si % PALETTE.length]};display:inline-block"></span>`
        + `<span style="opacity:.75">${esc(s.name)}</span> <span style="margin-left:auto;font-variant-numeric:tabular-nums">`
        + `${esc(formatTip ? formatTip(s.values[i], s) : (kind === 'money' ? moneyCompact(s.values[i], true) : num(s.values[i])))}</span></div>`).join('');
      tip.innerHTML = `<div style="opacity:.7;margin-bottom:2px">${esc(labels[i])}</div>${rows}`;
      tip.style.opacity = 1;
      const box = svg.getBoundingClientRect();
      const px = (x(i) / W) * box.width;
      tip.style.left = `${Math.max(60, Math.min(box.width - 60, px))}px`;
      tip.style.top = `${Math.max(34, pad.t + 6)}px`;
    };
    const hide = () => {
      tip.style.opacity = 0;
      guide.setAttribute('opacity', 0);
      markers.forEach((m) => m.setAttribute('opacity', 0));
    };

    hit.addEventListener('pointermove', (e) => show(e.clientX));
    hit.addEventListener('pointerdown', (e) => show(e.clientX));
    hit.addEventListener('pointerleave', hide);
    hit.addEventListener('pointercancel', hide);

    el.appendChild(svg);
  };

  return observe(el, draw);
}

/* ------------------------------------------------------------------ *
 * Vertical bars (e.g. revenue by hour of day)
 * ------------------------------------------------------------------ */

export function barChart(el, { labels, values, kind = 'money', height = 190, color = PALETTE[0], labelEvery = 2 }) {
  if (!el) return () => {};
  const tip = tooltipLayer(el);
  const draw = () => {
    el.querySelectorAll('svg').forEach((s) => s.remove());
    if (!values?.length) {
      el.innerHTML = '<div class="empty" style="padding:26px 12px"><p>No data yet</p></div>';
      return;
    }
    const W = Math.max(280, el.clientWidth);
    const H = height;
    const pad = { l: kind === 'money' ? 46 : 32, r: 8, t: 12, b: 24 };
    const iw = W - pad.l - pad.r, ih = H - pad.t - pad.b;
    const { max, step } = niceScale(0, Math.max(...values.map(Number), 0), 4);
    const y = (v) => pad.t + ih - (v / (max || 1)) * ih;
    const slot = iw / values.length;
    const bw = Math.max(3, Math.min(26, slot * 0.66));

    const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img' });
    for (let v = 0; v <= max + step / 2; v += step) {
      svg.append(svgEl('line', { x1: pad.l, y1: y(v), x2: W - pad.r, y2: y(v), class: v === 0 ? 'axis-line' : 'grid-line' }));
      const t = svgEl('text', { x: pad.l - 7, y: y(v) + 3.5, 'text-anchor': 'end' });
      t.textContent = fmtTick(v, kind);
      svg.append(t);
    }
    values.forEach((v, i) => {
      const cx = pad.l + slot * i + slot / 2;
      const h = Math.max(1.5, pad.t + ih - y(Number(v) || 0));
      svg.append(svgEl('rect', { x: cx - bw / 2, y: pad.t + ih - h, width: bw, height: h, rx: Math.min(3, bw / 2),
        fill: color, opacity: 0.9 }));
      if (i % labelEvery === 0) {
        const t = svgEl('text', { x: cx, y: H - 6, 'text-anchor': 'middle' });
        t.textContent = labels[i];
        svg.append(t);
      }
      const hitRect = svgEl('rect', { x: pad.l + slot * i, y: pad.t, width: slot, height: ih, fill: 'transparent' });
      hitRect.addEventListener('pointerenter', () => {
        tip.innerHTML = `<div style="opacity:.7">${esc(labels[i])}</div>${kind === 'money' ? esc(moneyCompact(v, true)) : esc(num(v))}`;
        tip.style.opacity = 1;
        const box = svg.getBoundingClientRect();
        tip.style.left = `${Math.max(46, Math.min(box.width - 46, (cx / W) * box.width))}px`;
        tip.style.top = `${pad.t + 10}px`;
      });
      hitRect.addEventListener('pointerleave', () => { tip.style.opacity = 0; });
      svg.append(hitRect);
    });
    el.appendChild(svg);
  };
  return observe(el, draw);
}

/* ------------------------------------------------------------------ *
 * Donut (payment mix, expense split)
 * ------------------------------------------------------------------ */

export function donut(el, { slices, centerLabel = '', centerValue = '', size = 168, thickness = 20 }) {
  if (!el) return () => {};
  const total = slices.reduce((a, s) => a + Math.max(0, Number(s.value) || 0), 0);
  const r = (size - thickness) / 2;
  const c = 2 * Math.PI * r;
  const cx = size / 2, cy = size / 2;

  const svg = svgEl('svg', { viewBox: `0 0 ${size} ${size}`, width: size, height: size, role: 'img' });
  svg.append(svgEl('circle', { cx, cy, r, fill: 'none', stroke: '#F1E7DB', 'stroke-width': thickness }));

  let offset = 0;
  slices.forEach((s, i) => {
    const v = Math.max(0, Number(s.value) || 0);
    if (total <= 0 || v <= 0) return;
    const frac = v / total;
    const len = frac * c;
    const color = s.color || PALETTE[i % PALETTE.length];
    const arc = svgEl('circle', {
      cx, cy, r, fill: 'none', stroke: color, 'stroke-width': thickness,
      'stroke-dasharray': `${Math.max(0, len - 1.6)} ${c - Math.max(0, len - 1.6)}`,
      'stroke-dashoffset': -offset, 'stroke-linecap': 'butt',
      transform: `rotate(-90 ${cx} ${cy})`,
    });
    arc.style.transition = 'stroke-width .12s';
    svg.append(arc);
    offset += len;
  });

  const t1 = svgEl('text', { x: cx, y: cy - 2, 'text-anchor': 'middle',
    style: 'font-size:16px;font-weight:750;fill:#2A1F17' });
  t1.textContent = centerValue;
  const t2 = svgEl('text', { x: cx, y: cy + 15, 'text-anchor': 'middle',
    style: 'font-size:10.5px;fill:#8C7B6B;font-weight:600;letter-spacing:.04em;text-transform:uppercase' });
  t2.textContent = centerLabel;
  svg.append(t1, t2);

  el.innerHTML = '';
  el.appendChild(svg);

  const legend = document.createElement('div');
  legend.className = 'donut-legend grow';
  legend.innerHTML = slices.map((s, i) => {
    const v = Math.max(0, Number(s.value) || 0);
    return `<div class="row between" style="gap:10px">
      <span class="row" style="gap:7px;min-width:0"><i style="width:9px;height:9px;border-radius:3px;background:${s.color || PALETTE[i % PALETTE.length]};flex:0 0 9px"></i>
      <span class="grow" style="overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(s.label)}</span></span>
      <span class="nowrap strong" style="font-variant-numeric:tabular-nums">${esc(s.display ?? num(v))}
      <span class="muted tiny"> ${esc(pct(total ? (v / total) * 100 : 0, 0))}</span></span>
    </div>`;
  }).join('');
  el.parentElement?.querySelector('[data-donut-legend]')?.replaceWith(legend);
  if (!el.parentElement?.querySelector('.donut-legend')) el.after(legend);
  return () => {};
}

/* ------------------------------------------------------------------ *
 * Horizontal bars as HTML (best-sellers, top customers)
 * ------------------------------------------------------------------ */

export function hbars(items, { valueFormat = (v) => num(v), max, subFormat } = {}) {
  if (!items?.length) return '<div class="empty"><p>No data for this period</p></div>';
  const top = max ?? Math.max(...items.map((i) => Number(i.value) || 0), 1);
  return items.map((it) => `
    <div class="bar-row" title="${esc(it.label)}">
      <span class="lbl">${esc(it.label)}</span>
      <span class="track"><i style="width:${Math.max(1.5, ((Number(it.value) || 0) / top) * 100).toFixed(1)}%"></i></span>
      <span class="val">${esc(valueFormat(it.value))}${subFormat ? `<span class="muted tiny"> ${esc(subFormat(it))}</span>` : ''}</span>
    </div>`).join('');
}

/** Tiny inline trend line for KPI cards. */
export function sparkline(values, { color = '#B4531F', width = 92, height = 26 } = {}) {
  const vals = (values || []).map(Number).filter(Number.isFinite);
  if (vals.length < 2) return '';
  const min = Math.min(...vals), max = Math.max(...vals);
  const span = max - min || 1;
  const pts = vals.map((v, i) => [(i / (vals.length - 1)) * width, height - 2 - ((v - min) / span) * (height - 5)]);
  const d = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  return `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" fill="none" aria-hidden="true">
    <path d="${d} L${width} ${height} L0 ${height} Z" fill="${color}" opacity=".10"/>
    <path d="${d}" stroke="${color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>`;
}

export { PALETTE };
