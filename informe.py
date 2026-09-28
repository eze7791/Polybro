"""Genera informe.html (un solo archivo, sin dependencias externas) a partir de los datos del simulador."""

from __future__ import annotations

import json
from pathlib import Path


def generar_informe(datos: dict, ruta: Path | str):
    payload = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    html = PLANTILLA.replace("__DATOS__", payload)
    Path(ruta).write_text(html, encoding="utf-8")


PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Informe Jev Polymarket</title>
<style>
:root {
  color-scheme: light;
  --bg: #f4f4f1; --surface: #fcfcfb; --surface-2: #f0efec; --border: #e2e1dc;
  --text: #0b0b0b; --text-2: #52514e; --muted: #7a7974; --grid: #e7e6e1;
  --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100; --s5: #e87ba4;
  --up: #0ca30c; --down: #d03b3b; --up-ink: #0a7d0a; --down-ink: #b02f2f;
  --bid: #9ec5f4; --ask: #f2b4ae; --ptb: #52514e; --line: #2a78d6;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) {
    color-scheme: dark;
    --bg: #111110; --surface: #1a1a19; --surface-2: #232321; --border: #33332f;
    --text: #ffffff; --text-2: #c3c2b7; --muted: #8f8e86; --grid: #2c2c29;
    --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181;
    --up-ink: #3fc93f; --down-ink: #f07a7a;
    --bid: #1c5cab; --ask: #8f3434; --ptb: #c3c2b7; --line: #3987e5;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --bg: #111110; --surface: #1a1a19; --surface-2: #232321; --border: #33332f;
  --text: #ffffff; --text-2: #c3c2b7; --muted: #8f8e86; --grid: #2c2c29;
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500; --s5: #d55181;
  --up-ink: #3fc93f; --down-ink: #f07a7a;
  --bid: #1c5cab; --ask: #8f3434; --ptb: #c3c2b7; --line: #3987e5;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font: 14px/1.45 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; }
.wrap { max-width: 1160px; margin: 0 auto; padding: 24px 16px 64px; }
h1 { font-size: 22px; margin: 0 0 4px; }
h2 { font-size: 16px; margin: 32px 0 12px; }
h4 { margin: 18px 0 6px; font-size: 14px; }
.sub { color: var(--text-2); }
.aviso { margin: 16px 0; padding: 10px 14px; border: 1px solid var(--border); border-radius: 8px;
  background: var(--surface); color: var(--text-2); }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 16px; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; }
.kpi .nombre { display: flex; align-items: center; gap: 8px; font-weight: 600; }
.kpi .desc { color: var(--muted); font-size: 12px; min-height: 48px; }
.kpi .pnl { font-size: 26px; font-weight: 650; margin: 6px 0 2px; font-variant-numeric: tabular-nums; }
.kpi .meta { color: var(--text-2); font-size: 13px; font-variant-numeric: tabular-nums; }
.dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; flex: none; vertical-align: middle; }
.pos { color: var(--up-ink); } .neg { color: var(--down-ink); }
.legend { display: flex; flex-wrap: wrap; gap: 14px; margin-bottom: 8px; color: var(--text-2); font-size: 13px; }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.chart { position: relative; width: 100%; overflow-x: auto; }
.chart svg { display: block; width: 100%; min-width: 640px; height: auto; overflow: visible; }
.tip { position: absolute; pointer-events: none; background: var(--surface); border: 1px solid var(--border);
  border-radius: 8px; padding: 8px 10px; font-size: 12px; box-shadow: 0 4px 16px rgba(0,0,0,.15);
  display: none; white-space: nowrap; z-index: 5; font-variant-numeric: tabular-nums; }
.tip b { font-weight: 600; }
table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
th, td { text-align: right; padding: 6px 8px; border-bottom: 1px solid var(--border); white-space: nowrap; }
th { color: var(--text-2); font-weight: 600; font-size: 12px; }
th:first-child, td:first-child { text-align: left; }
td.izq, th.izq { text-align: left; }
.tabla { overflow-x: auto; }
.badge { display: inline-flex; align-items: center; gap: 4px; font-weight: 650; font-size: 12px;
  padding: 2px 8px; border-radius: 999px; border: 1px solid currentColor; }
.badge.up { color: var(--up-ink); } .badge.down { color: var(--down-ink); } .badge.nd { color: var(--muted); }
.chip { display: inline-flex; align-items: center; gap: 4px; font-size: 12px; padding: 1px 7px; margin: 1px 2px;
  border-radius: 999px; background: var(--surface-2); color: var(--text); }
details.ventana { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; margin-bottom: 10px; }
details.ventana > summary { cursor: pointer; list-style: none; padding: 12px 16px; display: flex; flex-wrap: wrap;
  gap: 8px 16px; align-items: center; }
details.ventana > summary::-webkit-details-marker { display: none; }
details.ventana > summary::before { content: "▸"; color: var(--muted); }
details.ventana[open] > summary::before { content: "▾"; }
.ventana .hora { font-weight: 600; min-width: 110px; }
.ventana .precios { color: var(--text-2); font-variant-numeric: tabular-nums; }
.ventana .cuerpo { padding: 0 16px 16px; }
.ventana .pnlv { margin-left: auto; font-variant-numeric: tabular-nums; }
tr.dec { cursor: pointer; }
tr.dec:hover td, tr.dec.sel td { background: var(--surface-2); }
.libros { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin: 8px 0 4px; }
.libro h4 { margin: 0 0 6px; font-size: 13px; }
.libro table td, .libro table th { padding: 3px 6px; font-size: 12px; }
.barra { position: relative; }
.barra i { position: absolute; top: 3px; bottom: 3px; right: 0; border-radius: 3px; opacity: .9; }
.barra span { position: relative; }
.bid i { background: var(--bid); } .ask i { background: var(--ask); }
.pequeno { color: var(--muted); font-size: 12px; }
.presion { display: inline-block; width: 64px; height: 8px; border-radius: 4px; background: var(--surface-2);
  position: relative; vertical-align: middle; margin-right: 6px; }
.presion i { position: absolute; top: 0; bottom: 0; border-radius: 4px; }
.presion::after { content: ""; position: absolute; left: 50%; top: -2px; bottom: -2px; width: 1px; background: var(--muted); }
select { font: inherit; padding: 4px 8px; border-radius: 6px; border: 1px solid var(--border);
  background: var(--surface); color: var(--text); }
.fila { display: flex; gap: 12px; align-items: center; margin-bottom: 8px; flex-wrap: wrap; }
@media (max-width: 600px) { .ventana .pnlv { margin-left: 0; width: 100%; } }
</style>
</head>
<body>
<div class="wrap">
  <h1>Informe de simulación · Jev en Polymarket</h1>
  <div class="sub" id="cabecera"></div>
  <div class="aviso">Simulación con datos reales de mercado: no se envió ninguna orden ni se usó dinero real.
  Precio de referencia: Chainlink BTC/USD, el mismo que usa Polymarket para resolver. Las compras se simulan
  al precio de venta (ask) del libro y las ventas al precio de compra (bid), con comisión.</div>

  <div class="kpis" id="kpis"></div>

  <h2>Ganancia acumulada por estrategia</h2>
  <div class="card">
    <div class="legend" id="leyenda"></div>
    <div class="chart" id="grafPnl"></div>
    <div class="pequeno">Cada punto es una posición cerrada (vendida o liquidada al final de su ventana).</div>
  </div>

  <h2>Resumen</h2>
  <div class="card tabla"><table id="tablaResumen"></table></div>

  <h2>Mercados (ventanas)</h2>
  <p class="sub" style="margin-top:-6px">Pulsa una ventana para ver el precio, las compras y ventas de cada estrategia y cada decisión de Jev. Pulsa una decisión para ver el libro de órdenes y el flujo de ese momento.</p>
  <div id="ventanas"></div>

  <h2>Todas las posiciones</h2>
  <div class="card">
    <div class="fila"><label for="filtro">Estrategia</label>
      <select id="filtro"><option value="">Todas</option></select></div>
    <div class="tabla" id="tablaPos"></div>
  </div>
</div>

<script id="datos" type="application/json">__DATOS__</script>
<script>
const D = JSON.parse(document.getElementById('datos').textContent);
const EST = {
  jev_eleccion: { nombre: 'Jev · elección', color: 'var(--s1)', desc: 'Sigue lo que Jev decide: comprar Up, comprar Down, vender o esperar (si tiene confianza suficiente).' },
  jev_ventaja:  { nombre: 'Jev · ventaja',  color: 'var(--s2)', desc: 'Compra si la probabilidad de Jev supera el precio; vende si el mercado paga más de lo que Jev cree que vale.' },
  flujo:        { nombre: 'Flujo',          color: 'var(--s3)', desc: 'Sin Jev: si todos compran un lado, compra; si la presión se da la vuelta, vende.' },
  favorito:     { nombre: 'Favorito',       color: 'var(--s4)', desc: 'Compra una vez por ventana el lado favorito del mercado y espera al cierre.' },
  moneda:       { nombre: 'Moneda',         color: 'var(--s5)', desc: 'Compra una vez por ventana un lado al azar. Es la referencia a batir.' },
};
const ORDEN = D.estrategias;
const POS = D.posiciones || [];
const $ = s => document.querySelector(s);
const el = (tag, attrs = {}, html = '') => { const e = document.createElement(tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]); if (html) e.innerHTML = html; return e; };
const fmtUsd = (v, signo = false) => v == null ? '–' : (signo && v > 0 ? '+' : '') + v.toFixed(2);
const fmtPx = v => v == null ? '–' : v.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const fmtPct = v => v == null ? '–' : (v * 100).toFixed(0) + '%';
const hora = t => new Date(t * 1000).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
const horaCorta = t => new Date(t * 1000).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
const clsPnl = v => v == null ? '' : v > 0 ? 'pos' : v < 0 ? 'neg' : '';
const badge = r => r === 'up' ? '<span class="badge up">▲ SUBE</span>' : r === 'down' ? '<span class="badge down">▼ BAJA</span>'
  : r === 'empate' ? '<span class="badge nd">= EMPATE</span>' : '<span class="badge nd">sin resolver</span>';
const lado = l => l === 'up' ? '<span class="pos">▲ Up</span>' : '<span class="neg">▼ Down</span>';
const dotE = e => `<span class="dot" style="background:${EST[e].color}"></span>`;
const SVGNS = 'http://www.w3.org/2000/svg';
const svgEl = (tag, attrs) => { const e = document.createElementNS(SVGNS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e; };
const svgTxt = (x, y, txt, attrs = {}) => { const t = svgEl('text', { x, y, 'font-size': 11, fill: 'var(--text-2)', ...attrs }); t.textContent = txt; return t; };
const presionBar = p => { if (p == null) return '–'; const w = Math.abs(p) * 50;
  return `<span class="presion"><i style="${p >= 0 ? 'left:50%' : 'right:50%'};width:${w}%;background:${p >= 0 ? 'var(--up)' : 'var(--down)'}"></i></span>${p > 0 ? '▲' : p < 0 ? '▼' : ''}${Math.abs(p * 100).toFixed(0)}%`; };

function niceTicks(min, max, n = 5) {
  if (min === max) { min -= 1; max += 1; }
  const span = max - min, step0 = span / n, mag = Math.pow(10, Math.floor(Math.log10(step0)));
  const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => s >= step0);
  const ticks = []; let v = Math.floor(min / step) * step; ticks.push(+v.toFixed(10)); while (v < max - 1e-9) { v += step; ticks.push(+v.toFixed(10)); }
  return ticks;
}
function ponerTip(tip, svg, W, x, html) {
  const r = svg.getBoundingClientRect(); tip.innerHTML = html; tip.style.display = 'block';
  const px = x / W * r.width; tip.style.left = Math.max(4, Math.min(px + 12, r.width - tip.offsetWidth - 4)) + 'px'; tip.style.top = '8px';
}

// ---------- cabecera ----------
const c = D.config;
$('#cabecera').textContent = `${c.modo} · mercados de ${c.periodo} · decisión cada ${c.cada} s · ${D.inicio_utc} → ${D.fin_utc} · ${c.stake} USDC ficticios por compra`;

// ---------- estadísticas ----------
const cerradas = POS.filter(p => p.pnl != null);
function stats(est) {
  const xs = cerradas.filter(p => p.estrategia === est);
  const gan = xs.filter(p => p.pnl > 0).length, vend = xs.filter(p => p.cierre === 'vendida').length;
  const inv = xs.reduce((s, p) => s + p.coste + p.comision_compra, 0), pnl = xs.reduce((s, p) => s + p.pnl, 0);
  return { n: xs.length, gan, vend, inv, pnl, pct: xs.length ? gan / xs.length : null, roi: inv ? pnl / inv : null };
}
const S = Object.fromEntries(ORDEN.map(e => [e, stats(e)]));
$('#kpis').innerHTML = ORDEN.map(e => { const s = S[e], m = EST[e];
  return `<div class="card kpi"><div class="nombre">${dotE(e)}${m.nombre}</div><div class="desc">${m.desc}</div>
  <div class="pnl ${clsPnl(s.pnl)}">${s.n ? fmtUsd(s.pnl, true) : '–'} <span class="pequeno">USDC</span></div>
  <div class="meta">${s.n} posiciones · ${s.vend} vendidas antes${s.n ? ' · ' + fmtPct(s.pct) + ' ganadas' : ''}</div></div>`; }).join('');
$('#tablaResumen').innerHTML = `<thead><tr><th>Estrategia</th><th>Posiciones</th><th>Vendidas antes del cierre</th><th>Ganadas</th><th>% ganadas</th><th>Invertido</th><th>Ganancia</th><th>ROI</th></tr></thead><tbody>` +
  ORDEN.map(e => { const s = S[e]; return `<tr><td>${dotE(e)} ${EST[e].nombre}</td><td>${s.n}</td><td>${s.vend}</td><td>${s.gan}</td><td>${fmtPct(s.pct)}</td>
  <td>${s.inv.toFixed(2)}</td><td class="${clsPnl(s.pnl)}">${s.n ? fmtUsd(s.pnl, true) : '–'}</td><td>${s.roi != null ? (s.roi * 100).toFixed(1) + '%' : '–'}</td></tr>`; }).join('') + '</tbody>';

// ---------- gráfico de ganancia acumulada ----------
(function () {
  const cont = $('#grafPnl');
  const series = ORDEN.map(e => { let acc = 0;
    const pts = cerradas.filter(p => p.estrategia === e).sort((a, b) => a.t_venta - b.t_venta).map(p => ({ t: p.t_venta, v: (acc += p.pnl) }));
    return { e, pts }; }).filter(s => s.pts.length);
  $('#leyenda').innerHTML = series.map(s => `<span>${dotE(s.e)}${EST[s.e].nombre}</span>`).join('');
  if (!series.length) { cont.innerHTML = '<p class="sub">Todavía no hay posiciones cerradas.</p>'; return; }
  const W = 1000, H = 320, m = { l: 56, r: 150, t: 12, b: 28 };
  const ts = series.flatMap(s => s.pts.map(p => p.t)), vs = series.flatMap(s => s.pts.map(p => p.v)).concat([0]);
  const t0 = Math.min(...ts), t1 = Math.max(...ts) === t0 ? t0 + 60 : Math.max(...ts);
  const yt = niceTicks(Math.min(...vs), Math.max(...vs)), y0 = yt[0], y1 = yt[yt.length - 1];
  const X = t => m.l + (t - t0) / (t1 - t0) * (W - m.l - m.r), Y = v => m.t + (y1 - v) / (y1 - y0) * (H - m.t - m.b);
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Ganancia acumulada por estrategia' });
  for (const v of yt) { svg.append(svgEl('line', { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v), stroke: v === 0 ? 'var(--muted)' : 'var(--grid)' }));
    svg.append(svgTxt(m.l - 8, Y(v) + 4, v, { 'text-anchor': 'end' })); }
  for (let i = 0; i <= 6; i++) { const t = t0 + (t1 - t0) * i / 6; svg.append(svgTxt(X(t), H - 8, horaCorta(t), { 'text-anchor': 'middle' })); }
  const etq = [];
  for (const s of series) {
    svg.append(svgEl('path', { d: s.pts.map((p, i) => `${i ? 'L' : 'M'}${X(p.t).toFixed(1)},${Y(p.v).toFixed(1)}`).join(''),
      fill: 'none', stroke: EST[s.e].color, 'stroke-width': 2, 'stroke-linejoin': 'round' }));
    for (const p of s.pts) svg.append(svgEl('circle', { cx: X(p.t), cy: Y(p.v), r: 3, fill: EST[s.e].color, stroke: 'var(--surface)', 'stroke-width': 1.5 }));
    const l = s.pts[s.pts.length - 1]; etq.push({ y: Y(l.v), s, v: l.v });
  }
  etq.sort((a, b) => a.y - b.y); for (let i = 1; i < etq.length; i++) if (etq[i].y - etq[i - 1].y < 14) etq[i].y = etq[i - 1].y + 14;
  for (const l of etq) svg.append(svgTxt(W - m.r + 8, l.y + 4, `${EST[l.s.e].nombre} ${fmtUsd(l.v, true)}`, { 'font-size': 12, fill: 'var(--text)' }));
  const cruz = svgEl('line', { y1: m.t, y2: H - m.b, stroke: 'var(--muted)', 'stroke-dasharray': '3 3', visibility: 'hidden' }); svg.append(cruz);
  const hit = svgEl('rect', { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: 'transparent' }); svg.append(hit);
  cont.append(svg); const tip = el('div', { class: 'tip' }); cont.append(tip);
  hit.addEventListener('mousemove', ev => {
    const r = svg.getBoundingClientRect(), t = t0 + ((ev.clientX - r.left) / r.width * W - m.l) / (W - m.l - m.r) * (t1 - t0);
    const tt = ts.reduce((a, b) => Math.abs(b - t) < Math.abs(a - t) ? b : a);
    cruz.setAttribute('x1', X(tt)); cruz.setAttribute('x2', X(tt)); cruz.setAttribute('visibility', 'visible');
    ponerTip(tip, svg, W, X(tt), `<div class="pequeno">${hora(tt)}</div>` + series.map(s => { const p = [...s.pts].reverse().find(p => p.t <= tt + 0.5);
      return `<div>${dotE(s.e)} ${EST[s.e].nombre}: <b class="${clsPnl(p?.v)}">${p ? fmtUsd(p.v, true) : '–'}</b></div>`; }).join(''));
  });
  hit.addEventListener('mouseleave', () => { tip.style.display = 'none'; cruz.setAttribute('visibility', 'hidden'); });
})();

// ---------- ventanas ----------
const decPorSlug = {}; D.decisiones.forEach(d => (decPorSlug[d.slug] ??= []).push(d));
const posPorSlug = {}; POS.forEach(p => (posPorSlug[p.slug] ??= []).push(p));

function graficoChainlink(v, decs) {
  const cont = el('div', { class: 'chart' });
  const pts = (v.serie || []).map(([ms, p]) => ({ t: ms / 1000, p }));
  if (!pts.length) { cont.innerHTML = '<p class="pequeno">Sin datos de precio para esta ventana.</p>'; return cont; }
  const W = 1000, H = 220, m = { l: 72, r: 16, t: 14, b: 26 };
  const t0 = v.inicio - 30, t1 = v.fin + 15;
  const vals = pts.map(p => p.p).concat(v.precio_a_batir != null ? [v.precio_a_batir] : []);
  const yt = niceTicks(Math.min(...vals), Math.max(...vals), 4), y0 = yt[0], y1 = yt[yt.length - 1];
  const X = t => m.l + (t - t0) / (t1 - t0) * (W - m.l - m.r), Y = p => m.t + (y1 - p) / (y1 - y0) * (H - m.t - m.b);
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Precio Chainlink BTC/USD' });
  svg.append(svgEl('rect', { x: X(v.inicio), y: m.t, width: X(v.fin) - X(v.inicio), height: H - m.t - m.b, fill: 'var(--surface-2)' }));
  for (const val of yt) { svg.append(svgEl('line', { x1: m.l, x2: W - m.r, y1: Y(val), y2: Y(val), stroke: 'var(--grid)' }));
    svg.append(svgTxt(m.l - 8, Y(val) + 4, fmtPx(val), { 'text-anchor': 'end' })); }
  svg.append(svgTxt(X(v.inicio), H - 6, 'inicio ' + horaCorta(v.inicio), { 'text-anchor': 'middle' }));
  svg.append(svgTxt(X(v.fin), H - 6, 'fin ' + horaCorta(v.fin), { 'text-anchor': 'middle' }));
  if (v.precio_a_batir != null) {
    svg.append(svgEl('line', { x1: m.l, x2: W - m.r, y1: Y(v.precio_a_batir), y2: Y(v.precio_a_batir), stroke: 'var(--ptb)', 'stroke-width': 1.5, 'stroke-dasharray': '6 4' }));
    svg.append(svgTxt(W - m.r - 4, Y(v.precio_a_batir) - 6, 'precio a batir ' + fmtPx(v.precio_a_batir), { 'text-anchor': 'end' })); }
  svg.append(svgEl('path', { d: pts.map((p, i) => `${i ? 'L' : 'M'}${X(p.t).toFixed(1)},${Y(p.p).toFixed(1)}`).join(''), fill: 'none', stroke: 'var(--line)', 'stroke-width': 2, 'stroke-linejoin': 'round' }));
  if (v.precio_final != null) svg.append(svgEl('circle', { cx: X(v.fin), cy: Y(v.precio_final), r: 5, fill: v.resultado === 'down' ? 'var(--down)' : 'var(--up)', stroke: 'var(--surface)', 'stroke-width': 2 }));
  const cruz = svgEl('line', { y1: m.t, y2: H - m.b, stroke: 'var(--muted)', 'stroke-dasharray': '3 3', visibility: 'hidden' }); svg.append(cruz);
  const hit = svgEl('rect', { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: 'transparent' }); svg.append(hit);
  cont.append(svg); const tip = el('div', { class: 'tip' }); cont.append(tip);
  hit.addEventListener('mousemove', ev => {
    const r = svg.getBoundingClientRect(), t = t0 + ((ev.clientX - r.left) / r.width * W - m.l) / (W - m.l - m.r) * (t1 - t0);
    const p = pts.reduce((a, b) => Math.abs(b.t - t) < Math.abs(a.t - t) ? b : a), dif = v.precio_a_batir != null ? p.p - v.precio_a_batir : null;
    cruz.setAttribute('x1', X(p.t)); cruz.setAttribute('x2', X(p.t)); cruz.setAttribute('visibility', 'visible');
    ponerTip(tip, svg, W, X(p.t), `<div class="pequeno">${hora(p.t)}</div><div>Chainlink: <b>${fmtPx(p.p)}</b></div>` +
      (dif != null ? `<div>vs precio a batir: <b class="${clsPnl(dif)}">${dif > 0 ? '+' : ''}${fmtPx(dif)}</b></div>` : ''));
  });
  hit.addEventListener('mouseleave', () => { tip.style.display = 'none'; cruz.setAttribute('visibility', 'hidden'); });
  return cont;
}

function graficoMercado(v, decs) {
  // Precio de Up y Down en Polymarket (0 a 1 = probabilidad implícita) con las compras y ventas de cada estrategia
  const cont = el('div', { class: 'chart' });
  const pts = decs.filter(d => d.resumen_up.mid != null && d.resumen_down.mid != null);
  if (!pts.length) return cont;
  const W = 1000, H = 240, m = { l: 72, r: 16, t: 14, b: 26 }, t0 = v.inicio - 30, t1 = v.fin + 15;
  const X = t => m.l + (t - t0) / (t1 - t0) * (W - m.l - m.r), Y = p => m.t + (1 - p) * (H - m.t - m.b);
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Precio de Up y Down en Polymarket con compras y ventas' });
  svg.append(svgEl('rect', { x: X(v.inicio), y: m.t, width: X(v.fin) - X(v.inicio), height: H - m.t - m.b, fill: 'var(--surface-2)' }));
  for (const val of [0, 0.25, 0.5, 0.75, 1]) { svg.append(svgEl('line', { x1: m.l, x2: W - m.r, y1: Y(val), y2: Y(val), stroke: val === 0.5 ? 'var(--muted)' : 'var(--grid)' }));
    svg.append(svgTxt(m.l - 8, Y(val) + 4, val.toFixed(2), { 'text-anchor': 'end' })); }
  svg.append(svgTxt(X(v.inicio), H - 6, 'inicio ' + horaCorta(v.inicio), { 'text-anchor': 'middle' }));
  svg.append(svgTxt(X(v.fin), H - 6, 'fin ' + horaCorta(v.fin), { 'text-anchor': 'middle' }));
  for (const [k, col, dash, nom] of [['resumen_up', 'var(--up)', '', '▲ Up'], ['resumen_down', 'var(--down)', '5 4', '▼ Down']]) {
    svg.append(svgEl('path', { d: pts.map((d, i) => `${i ? 'L' : 'M'}${X(d.t).toFixed(1)},${Y(d[k].mid).toFixed(1)}`).join(''),
      fill: 'none', stroke: col, 'stroke-width': 2, 'stroke-dasharray': dash, opacity: .8 }));
    const u = pts[pts.length - 1]; svg.append(svgTxt(Math.min(X(u.t) + 6, W - m.r - 40), Y(u[k].mid) + 4, nom, { fill: 'var(--text)', 'font-size': 12 }));
  }
  const marcas = [];
  for (const d of decs) for (const a of d.acciones) {
    const x = X(d.t) + (ORDEN.indexOf(a.estrategia) - 2) * 5, y = Y(a.precio), s = 7;
    const pathD = a.tipo === 'compra' ? `M${x},${y - s} L${x + s},${y + s * .8} L${x - s},${y + s * .8} Z` : `M${x},${y + s} L${x + s},${y - s * .8} L${x - s},${y - s * .8} Z`;
    const mk = svgEl('path', { d: pathD, fill: EST[a.estrategia].color, stroke: 'var(--surface)', 'stroke-width': 2 });
    svg.append(mk); marcas.push({ x, y, a, d });
  }
  const tip = el('div', { class: 'tip' });
  const hit = svgEl('rect', { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: 'transparent' }); svg.append(hit);
  cont.append(svg); cont.append(tip);
  hit.addEventListener('mousemove', ev => {
    const r = svg.getBoundingClientRect(), sx = (ev.clientX - r.left) / r.width * W, sy = (ev.clientY - r.top) / r.height * H;
    const cerca = marcas.filter(k => Math.hypot(k.x - sx, k.y - sy) < 14);
    if (cerca.length) {
      ponerTip(tip, svg, W, cerca[0].x, `<div class="pequeno">${hora(cerca[0].d.t)} · quedaban ${cerca[0].d.seg_restantes} s</div>` + cerca.map(k => {
        const p = POS[k.a.pos]; return `<div>${dotE(k.a.estrategia)} ${EST[k.a.estrategia].nombre}: <b>${k.a.tipo === 'compra' ? 'COMPRA' : 'VENDE'}</b> ${lado(k.a.lado)} a ${k.a.precio.toFixed(2)}
        <span class="pequeno">· ${k.a.tipo === 'compra' ? p.motivo_compra : p.motivo_venta}</span></div>`; }).join(''));
      return;
    }
    const d = pts.reduce((a, b) => Math.abs(X(b.t) - sx) < Math.abs(X(a.t) - sx) ? b : a);
    ponerTip(tip, svg, W, X(d.t), `<div class="pequeno">${hora(d.t)}</div><div>▲ Up: bid <b>${d.resumen_up.best_bid ?? '–'}</b> / ask <b>${d.resumen_up.best_ask ?? '–'}</b></div>
      <div>▼ Down: bid <b>${d.resumen_down.best_bid ?? '–'}</b> / ask <b>${d.resumen_down.best_ask ?? '–'}</b></div>`);
  });
  hit.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
  return cont;
}

function tablaLibro(titulo, lb) {
  const max = Math.max(1, ...lb.bids.map(x => x[1]), ...lb.asks.map(x => x[1]));
  let filas = ''; for (let i = 0; i < Math.max(lb.bids.length, lb.asks.length, 1); i++) {
    const b = lb.bids[i], a = lb.asks[i];
    filas += `<tr><td class="barra bid">${b ? `<i style="width:${b[1] / max * 100}%"></i><span>${b[1].toFixed(0)}</span>` : ''}</td>
      <td>${b ? b[0].toFixed(2) : ''}</td><td class="izq">${a ? a[0].toFixed(2) : ''}</td>
      <td class="barra ask izq">${a ? `<i style="width:${a[1] / max * 100}%;left:0;right:auto"></i><span>${a[1].toFixed(0)}</span>` : ''}</td></tr>`; }
  return `<div class="libro"><h4>${titulo}</h4><table><thead><tr><th>Acciones</th><th>Compran a (bid)</th><th class="izq">Venden a (ask)</th><th class="izq">Acciones</th></tr></thead><tbody>${filas}</tbody></table></div>`;
}

function tablaFlujo(f) {
  if (!f || !f.disponible) return '<p class="pequeno">Flujo de operaciones no disponible en este momento.</p>';
  const fila = (k, lbl) => { const x = f[k]; if (!x) return '';
    return `<tr><td>${lbl}</td><td>${x.up.taker_buy_shares.toFixed(0)}</td><td>${x.up.taker_sell_shares.toFixed(0)}</td>
    <td>${x.down.taker_buy_shares.toFixed(0)}</td><td>${x.down.taker_sell_shares.toFixed(0)}</td><td>${x.up.trades + x.down.trades}</td><td>${presionBar(x.pressure_toward_up)}</td></tr>`; };
  return `<h4>Flujo de operaciones reales <span class="pequeno">(acciones compradas / vendidas de forma agresiva)</span></h4><table>
    <thead><tr><th>Periodo</th><th>Up compran</th><th>Up venden</th><th>Down compran</th><th>Down venden</th><th>Operaciones</th><th>Presión</th></tr></thead>
    <tbody>${fila('last_30s', 'Últimos 30 s')}${fila('last_60s', 'Últimos 60 s')}</tbody></table>
    <p class="pequeno">Presión ▲ = el dinero empuja hacia Up (comprar Up o vender Down). ▼ = hacia Down.</p>`;
}

function tablaPos(lista, conVentana = false) {
  if (!lista.length) return '<p class="pequeno">Ninguna estrategia abrió posiciones aquí.</p>';
  return `<table><thead><tr><th>Estrategia</th>${conVentana ? '<th>Ventana</th>' : ''}<th>Lado</th><th>Compra</th><th>Precio</th><th class="izq">Motivo compra</th>
    <th>Salida</th><th>Precio</th><th class="izq">Cómo cerró</th><th>Acciones</th><th>Coste + com.</th><th>Ganancia</th></tr></thead><tbody>` +
    lista.map(p => `<tr><td>${dotE(p.estrategia)} ${EST[p.estrategia].nombre}</td>
    ${conVentana ? `<td>${horaCorta(D.ventanas.find(v => v.slug === p.slug)?.inicio ?? p.t_compra)}</td>` : ''}
    <td>${lado(p.lado)}</td><td>${hora(p.t_compra)}</td><td>${p.precio_compra.toFixed(2)}</td><td class="izq pequeno">${p.motivo_compra}</td>
    <td>${p.cierre === 'vendida' ? hora(p.t_venta) : p.cierre === 'al cierre' ? 'fin' : '–'}</td>
    <td>${p.precio_venta != null ? p.precio_venta.toFixed(2) : '–'}</td>
    <td class="izq">${p.cierre === 'vendida' ? `vendida <span class="pequeno">· ${p.motivo_venta}</span>` : p.resultado ? (p.precio_venta >= 1 ? '✓ ganó al cierre' : p.precio_venta > 0 ? '= empate' : '✗ perdió al cierre') : 'pendiente'}</td>
    <td>${p.acciones.toFixed(2)}</td><td>${(p.coste + p.comision_compra).toFixed(2)}</td><td class="${clsPnl(p.pnl)}">${fmtUsd(p.pnl, true)}</td></tr>`).join('') + '</tbody></table>';
}

const contV = $('#ventanas');
const conDatos = D.ventanas.filter(v => (decPorSlug[v.slug] || []).length);
if (!conDatos.length) contV.innerHTML = '<p class="sub">No hubo decisiones en ninguna ventana.</p>';
for (const v of conDatos) {
  const decs = decPorSlug[v.slug] || [], ps = posPorSlug[v.slug] || [];
  const porEst = ORDEN.map(e => { const xs = ps.filter(p => p.estrategia === e && p.pnl != null); if (!xs.length) return '';
    const s = xs.reduce((a, p) => a + p.pnl, 0); return `<span title="${EST[e].nombre}">${dotE(e)} <span class="${clsPnl(s)}">${fmtUsd(s, true)}</span></span>`; }).join(' &nbsp; ');
  const nAcc = decs.reduce((s, d) => s + d.acciones.length, 0);
  const det = el('details', { class: 'ventana' });
  det.innerHTML = `<summary><span class="hora">${horaCorta(v.inicio)}–${horaCorta(v.fin)}</span>${badge(v.resultado)}
    <span class="precios">a batir ${fmtPx(v.precio_a_batir)} → final ${fmtPx(v.precio_final)}</span>
    <span class="pequeno">${decs.length} decisiones · ${nAcc} compras/ventas</span><span class="pnlv">${porEst}</span></summary>`;
  const cu = el('div', { class: 'cuerpo' });
  cu.append(el('p', { class: 'pequeno' }, `${v.titulo} · precio: ${v.fuente || '?'} · a batir según ${v.precio_a_batir_origen || '–'} · resultado: ${v.resultado_origen || 'pendiente'}`));
  cu.append(el('h4', {}, 'Precio de BTC (Chainlink)'));
  cu.append(graficoChainlink(v, decs));
  cu.append(el('h4', {}, 'Precio de Up y Down en Polymarket, con compras (▲) y ventas (▼)'));
  cu.append(el('div', { class: 'legend' }, ORDEN.map(e => `<span>${dotE(e)}${EST[e].nombre}</span>`).join('') + '<span>▲ compra · ▼ venta</span>'));
  cu.append(graficoMercado(v, decs));
  const tDec = el('div', { class: 'tabla' });
  tDec.innerHTML = `<h4>Decisiones <span class="pequeno">(pulsa una fila para ver libro de órdenes y flujo)</span></h4>
    <table><thead><tr><th>Hora</th><th>Quedan</th><th>vs a batir</th><th>Presión 30 s</th><th>Jev dice</th><th>Conf.</th><th>P(up)</th><th>Up bid/ask</th><th>Down bid/ask</th><th class="izq">Compras y ventas</th></tr></thead><tbody>` +
    decs.map(d => { const dif = d.precio_ref - d.precio_a_batir, f = d.flujo && d.flujo.disponible ? d.flujo.last_30s : null;
      return `<tr class="dec" data-id="${d.id}"><td>${hora(d.t)}</td><td>${d.seg_restantes} s</td><td class="${clsPnl(dif)}">${dif > 0 ? '+' : ''}${fmtPx(dif)}</td>
      <td>${presionBar(f ? f.pressure_toward_up : null)}</td><td>${d.jev ? d.jev.accion : 'error'}</td>
      <td>${d.jev && d.jev.accion_conf != null ? fmtPct(d.jev.accion_conf) : '–'}</td><td>${d.jev ? fmtPct(d.jev.p_up) : '–'}</td>
      <td>${d.resumen_up.best_bid ?? '–'} / ${d.resumen_up.best_ask ?? '–'}</td><td>${d.resumen_down.best_bid ?? '–'} / ${d.resumen_down.best_ask ?? '–'}</td>
      <td class="izq">${d.acciones.map(a => `<span class="chip">${dotE(a.estrategia)}${a.tipo === 'compra' ? 'compra' : 'vende'} ${a.lado === 'up' ? '▲' : '▼'} ${a.precio.toFixed(2)}</span>`).join('')}</td></tr>`; }).join('') + '</tbody></table>';
  cu.append(tDec);
  const box = el('div'); cu.append(box);
  tDec.querySelectorAll('tr.dec').forEach(tr => tr.addEventListener('click', () => {
    const d = D.decisiones[+tr.dataset.id], ya = tr.classList.contains('sel');
    tDec.querySelectorAll('tr.dec').forEach(x => x.classList.remove('sel'));
    if (ya) { box.innerHTML = ''; return; }
    tr.classList.add('sel');
    box.innerHTML = `<div class="card" style="margin-top:10px"><div class="pequeno">Momento ${hora(d.t)} · quedaban ${d.seg_restantes} s · Chainlink ${fmtPx(d.precio_ref)} vs a batir ${fmtPx(d.precio_a_batir)}</div>
      <div class="libros">${tablaLibro('<span class="pos">▲ Up</span> · libro de órdenes', d.libro_up)}${tablaLibro('<span class="neg">▼ Down</span> · libro de órdenes', d.libro_down)}</div>
      <div class="tabla">${tablaFlujo(d.flujo)}</div></div>`;
  }));
  const tP = el('div', { class: 'tabla' }); tP.innerHTML = '<h4>Posiciones en esta ventana</h4>' + tablaPos(ps); cu.append(tP);
  det.append(cu); contV.append(det);
}

const filtro = $('#filtro');
ORDEN.forEach(e => filtro.append(el('option', { value: e }, EST[e].nombre)));
const pintar = () => { const f = filtro.value; $('#tablaPos').innerHTML = tablaPos(POS.filter(p => !f || p.estrategia === f), true); };
filtro.addEventListener('change', pintar); pintar();
</script>
</body>
</html>
"""
