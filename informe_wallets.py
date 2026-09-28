"""Genera el informe HTML del analizador de wallets (un solo archivo, sin dependencias externas)."""

from __future__ import annotations

import json
from pathlib import Path

from informe import PLANTILLA as _PLANTILLA_SIMULADOR

# Mismos colores y estilos base que el informe del simulador
CSS_BASE = _PLANTILLA_SIMULADOR.split("<style>", 1)[1].split("</style>", 1)[0]


def generar_informe(datos: dict, ruta: Path | str):
    payload = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/")
    html = PLANTILLA.replace("__CSS__", CSS_BASE).replace("__DATOS__", payload)
    Path(ruta).write_text(html, encoding="utf-8")


PLANTILLA = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Wallets Polymarket BTC</title>
<style>
__CSS__
.aviso.demo { border-color: var(--s4); color: var(--text); font-weight: 600; }
.kpi .pnl { font-size: 24px; }
.dos { display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 16px; }
@media (max-width: 520px) { .dos { grid-template-columns: 1fr; } }
.dos > * { min-width: 0; }
.chart.peq svg { min-width: 320px; }
th.ord { cursor: pointer; user-select: none; }
th.ord:hover { color: var(--text); }
th.ord.act::after { content: attr(data-dir); margin-left: 4px; }
tr.fila-w { cursor: pointer; }
tr.fila-w:hover td, tr.fila-w.sel td { background: var(--surface-2); }
.mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }
a { color: var(--s1); }
#detalle { scroll-margin-top: 12px; }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 12px 0; }
.tile { background: var(--surface-2); border-radius: 8px; padding: 10px 12px; }
.tile .v { font-size: 20px; font-weight: 650; font-variant-numeric: tabular-nums; }
.tile .l { color: var(--muted); font-size: 12px; }
input[type=number] { font: inherit; width: 70px; padding: 4px 6px; border-radius: 6px; border: 1px solid var(--border);
  background: var(--surface); color: var(--text); }
td.mejor { font-weight: 650; }
</style>
</head>
<body>
<div class="wrap">
  <h1>Analizador de wallets · Polymarket BTC Up or Down</h1>
  <div class="sub" id="cabecera"></div>
  <div id="avisos"></div>

  <div class="kpis" id="kpis"></div>

  <h2>Qué hacen las wallets que ganan</h2>
  <p class="sub" style="margin-top:-6px" id="explicaGrupos"></p>
  <div class="card tabla"><table id="tablaComp"></table></div>
  <div class="dos" style="margin-top:16px">
    <div class="card"><h4 style="margin-top:0">Cuándo compran dentro de la ventana</h4>
      <div class="legend" id="leyT"></div><div class="chart peq" id="histT"></div>
      <div class="pequeno">Porcentaje del dinero gastado en compras en cada tramo de la ventana.</div></div>
    <div class="card"><h4 style="margin-top:0">A qué precio compran</h4>
      <div class="legend" id="leyP"></div><div class="chart peq" id="histP"></div>
      <div class="pequeno">Porcentaje del dinero gastado en compras en cada tramo de precio (0,50 = 50 % de probabilidad).</div></div>
  </div>

  <h2>Volumen frente a ganancia</h2>
  <div class="card">
    <div class="legend" id="leyS"></div>
    <div class="chart" id="scatter"></div>
    <div class="pequeno">Cada punto es una wallet con suficientes ventanas. Relleno = analizada con su actividad completa; hueco = solo con las operaciones del mercado. Pulsa un punto para ver su detalle.</div>
  </div>

  <h2>Ranking de wallets</h2>
  <div class="card">
    <div class="fila">
      <label>Ventanas mínimas <input type="number" id="fMin" min="1"></label>
      <label>Estilo <select id="fEstilo"><option value="">Todos</option></select></label>
      <label><input type="checkbox" id="fAct"> Solo analizadas a fondo</label>
      <span class="pequeno" id="nFilas"></span>
    </div>
    <div class="tabla"><table id="tablaW"></table></div>
  </div>

  <div id="detalle"></div>

  <h2>Mercados analizados</h2>
  <div class="card tabla"><table id="tablaM"></table></div>
</div>

<script id="datos" type="application/json">__DATOS__</script>
<script>
const D = JSON.parse(document.getElementById('datos').textContent);
const P = D.periodo_seg, NT = D.n_tramos, C = D.config, R = D.resumen;
const ESTILO = {
  split_vende: { nombre: 'Crea pares y vende', color: 'var(--s1)', desc: 'Crea pares Up+Down por 1 $ (split) y vende los lados en el libro.' },
  dos_lados:   { nombre: 'Compra los dos lados', color: 'var(--s2)', desc: 'Compra Up y Down en la misma ventana, cada uno cuando está barato.' },
  sale_pronto: { nombre: 'Sale pronto', color: 'var(--s3)', desc: 'Compra y vende antes del cierre en la mayoría de ventanas.' },
  maker:       { nombre: 'Maker', color: 'var(--s4)', desc: 'La mayor parte de su volumen son órdenes puestas en el libro.' },
  direccional: { nombre: 'Direccional', color: 'var(--s5)', desc: 'Apuesta a un lado y suele esperar al cierre.' },
};
const GRUPO = { ganadoras: { nombre: `Las ${D.comparacion.n} que más ganan`, color: 'var(--s1)' },
                perdedoras: { nombre: `Las ${D.comparacion.n} que más pierden`, color: 'var(--s2)' } };
const $ = s => document.querySelector(s);
const el = (tag, attrs = {}, html = '') => { const e = document.createElement(tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]); if (html) e.innerHTML = html; return e; };
const SVGNS = 'http://www.w3.org/2000/svg';
const svgEl = (tag, attrs) => { const e = document.createElementNS(SVGNS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); return e; };
const svgTxt = (x, y, txt, attrs = {}) => { const t = svgEl('text', { x, y, 'font-size': 11, fill: 'var(--text-2)', ...attrs }); t.textContent = txt; return t; };
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const num = (v, d = 2) => v == null ? '–' : v.toLocaleString('es-ES', { minimumFractionDigits: d, maximumFractionDigits: d });
const usd = (v, signo = true) => v == null ? '–' : (signo && v > 0 ? '+' : '') + num(v, 2);
const pct = v => v == null ? '–' : num(v * 100, 0) + ' %';
const seg = v => v == null ? '–' : num(v, 0) + ' s';
const px = v => v == null ? '–' : num(v, 2);
const FMT = { usd: v => usd(v), vol: v => num(v, 0), pct, seg, px, num: v => num(v, 1) };
const cls = v => v == null ? '' : v > 0 ? 'pos' : v < 0 ? 'neg' : '';
const hora = t => new Date(t * 1000).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
const fecha = t => new Date(t * 1000).toLocaleString('es-ES', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
const corta = w => w.slice(0, 6) + '…' + w.slice(-4);
const dot = c => `<span class="dot" style="background:${c}"></span>`;
const badge = r => r === 'up' ? '<span class="badge up">▲ SUBE</span>' : r === 'down' ? '<span class="badge down">▼ BAJA</span>'
  : r === 'empate' ? '<span class="badge nd">= EMPATE</span>' : '<span class="badge nd">sin resolver</span>';
const nombreW = w => w.nombre ? `${esc(w.nombre)} <span class="pequeno mono">${corta(w.wallet)}</span>` : `<span class="mono">${corta(w.wallet)}</span>`;

function niceTicks(min, max, n = 5) {
  if (min === max) { min -= 1; max += 1; }
  const span = max - min, step0 = span / n, mag = Math.pow(10, Math.floor(Math.log10(step0)));
  const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => s >= step0);
  const ticks = []; let v = Math.floor(min / step) * step; ticks.push(+v.toFixed(10));
  while (v < max - 1e-9) { v += step; ticks.push(+v.toFixed(10)); }
  return ticks;
}
function tipEn(tip, cont, ev, html) {
  const r = cont.getBoundingClientRect(); tip.innerHTML = html; tip.style.display = 'block';
  const x = ev.clientX - r.left + cont.scrollLeft, y = ev.clientY - r.top;
  tip.style.left = Math.max(4, Math.min(x + 14, cont.scrollWidth - tip.offsetWidth - 4)) + 'px';
  tip.style.top = Math.max(4, y - tip.offsetHeight - 10) + 'px';
}

// ---------- cabecera y avisos ----------
$('#cabecera').textContent = `Mercados de ${C.periodo} · ${fecha(D.desde)} → ${fecha(D.hasta)} (${num(C.horas, 1)} h) · generado ${D.generado_utc}`;
let avisos = '';
if (D.demo) avisos += '<div class="aviso demo">DATOS INVENTADOS (modo --demo). Este informe solo sirve para ver cómo es; no describe ninguna wallet real.</div>';
avisos += `<div class="aviso">La ganancia de cada wallet se calcula con sus compras, ventas, split y merge en cada ventana, más lo que valían
  al cierre las acciones que le quedaban según la resolución oficial. La comisión se estima (acciones × ${D.mercados[0]?.fee_rate ?? 0.07} × p × (1−p))
  solo en las operaciones en las que tomó liquidez${R.info_taker ? '' : ' (no se pudo saber cuáles, así que no se resta ninguna)'}.
  No incluye reembolsos por poner órdenes (maker) ni lo que hiciera fuera de estos mercados.
  ${R.mercados_truncados ? `<br><b>${R.mercados_truncados} mercados</b> tenían más operaciones de las que dejó bajar la API: sube <code>--max-filas</code>.` : ''}</div>`;
$('#avisos').innerHTML = avisos;

// ---------- KPIs ----------
const kpi = (nombre, valor, meta) => `<div class="card kpi"><div class="nombre">${nombre}</div><div class="pnl">${valor}</div><div class="meta">${meta}</div></div>`;
$('#kpis').innerHTML = [
  kpi('Mercados', R.mercados, `${R.resueltos} resueltos`),
  kpi('Wallets distintas', num(R.wallets, 0), `${R.analizadas} analizadas a fondo`),
  kpi('Volumen negociado', num(R.volumen_taker, 0) + ' <span class="pequeno">USDC</span>', 'suma de las operaciones'),
  kpi('Concentración', pct(R.pct_top10), 'del volumen lo hacen las 10 wallets más activas'),
  kpi('Wallets rentables', `${R.rentables} <span class="pequeno">de ${R.validas}</span>`, `con al menos ${C.min_ventanas} ventanas resueltas`),
].join('');

// ---------- comparación ----------
$('#explicaGrupos').textContent = `Mediana de cada métrica entre las ${D.comparacion.n} wallets que más ganan, las ${D.comparacion.n} que más pierden y todas las que tienen al menos ${C.min_ventanas} ventanas resueltas.`;
(function () {
  const M = D.comparacion.metricas, E = D.comparacion.estilos || {};
  const estiloTop = g => { const c = E[g] || {}; const tot = Object.values(c).reduce((a, b) => a + b, 0);
    return Object.entries(c).filter(([, n]) => n).sort((a, b) => b[1] - a[1]).slice(0, 2)
      .map(([e, n]) => `${dot(ESTILO[e].color)} ${ESTILO[e].nombre} (${n}/${tot})`).join('<br>') || '–'; };
  $('#tablaComp').innerHTML = `<thead><tr><th>Métrica</th><th>${dot(GRUPO.ganadoras.color)} ${GRUPO.ganadoras.nombre}</th>
    <th>${dot(GRUPO.perdedoras.color)} ${GRUPO.perdedoras.nombre}</th><th>Todas</th></tr></thead><tbody>` +
    M.map(m => `<tr><td>${m.etiqueta}</td><td class="${m.formato === 'usd' ? cls(m.ganadoras) : ''}">${FMT[m.formato](m.ganadoras)}</td>
      <td class="${m.formato === 'usd' ? cls(m.perdedoras) : ''}">${FMT[m.formato](m.perdedoras)}</td><td>${FMT[m.formato](m.todas)}</td></tr>`).join('') +
    `<tr><td>Estilo más común</td><td>${estiloTop('ganadoras')}</td><td>${estiloTop('perdedoras')}</td><td>${estiloTop('todas')}</td></tr></tbody>`;
})();

function barras(cont, etiquetas, series, opts = {}) {
  cont.innerHTML = '';
  const hay = series.filter(s => s.vals && s.vals.length);
  if (!hay.length) { cont.innerHTML = '<p class="pequeno">Sin datos.</p>'; return; }
  const W = 560, H = 220, m = { l: 44, r: 8, t: 10, b: 34 };
  const maxV = Math.max(0.01, ...hay.flatMap(s => s.vals));
  const yt = niceTicks(0, maxV, 4), y1 = yt[yt.length - 1];
  const n = etiquetas.length, bw = (W - m.l - m.r) / n, gap = 2, iw = (bw - 8) / hay.length;
  const Y = v => m.t + (1 - v / y1) * (H - m.t - m.b);
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': opts.aria || 'Histograma' });
  for (const v of yt) { svg.append(svgEl('line', { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v), stroke: 'var(--grid)' }));
    svg.append(svgTxt(m.l - 6, Y(v) + 4, pct(v), { 'text-anchor': 'end' })); }
  etiquetas.forEach((e, i) => svg.append(svgTxt(m.l + bw * i + bw / 2, H - m.b + 14, e, { 'text-anchor': 'middle', 'font-size': 10 })));
  if (opts.sub) svg.append(svgTxt(m.l + (W - m.l - m.r) / 2, H - 4, opts.sub, { 'text-anchor': 'middle', 'font-size': 10, fill: 'var(--muted)' }));
  hay.forEach((s, k) => s.vals.forEach((v, i) => {
    if (!v) return;
    const x = m.l + bw * i + 4 + k * iw, h = Y(0) - Y(v), r = Math.min(4, iw / 2 - gap, h);
    const w = Math.max(1, iw - gap);
    svg.append(svgEl('path', { d: `M${x},${Y(0)} V${Y(v) + r} Q${x},${Y(v)} ${x + r},${Y(v)} H${x + w - r} Q${x + w},${Y(v)} ${x + w},${Y(v) + r} V${Y(0)} Z`, fill: s.color }));
  }));
  svg.append(svgEl('line', { x1: m.l, x2: W - m.r, y1: Y(0), y2: Y(0), stroke: 'var(--muted)' }));
  const tip = el('div', { class: 'tip' });
  const hit = svgEl('rect', { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: 'transparent' });
  svg.append(hit); cont.append(svg); cont.append(tip);
  hit.addEventListener('mousemove', ev => {
    const r = svg.getBoundingClientRect(), i = Math.min(n - 1, Math.max(0, Math.floor(((ev.clientX - r.left) / r.width * W - m.l) / bw)));
    tipEn(tip, cont, ev, `<div class="pequeno">${opts.titulo ? opts.titulo(i) : etiquetas[i]}</div>` +
      hay.map(s => `<div>${dot(s.color)} ${s.nombre}: <b>${pct(s.vals[i] || 0)}</b></div>`).join(''));
  });
  hit.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
}
const paso = P / NT;
const ETQ_T = ['antes', ...Array.from({ length: NT }, (_, i) => String(Math.round(paso * i))), 'después'];
const TIT_T = i => i === 0 ? 'Antes de empezar la ventana' : i === NT + 1 ? 'Después del cierre' : `Del segundo ${Math.round(paso * (i - 1))} al ${Math.round(paso * i)}`;
const ETQ_P = Array.from({ length: 10 }, (_, i) => (i / 10).toFixed(1));
const TIT_P = i => `Precio entre ${(i / 10).toFixed(2)} y ${((i + 1) / 10).toFixed(2)}`;
const normal = xs => { const s = xs.reduce((a, b) => a + b, 0); return s ? xs.map(x => x / s) : []; };
(function () {
  const H = D.comparacion;
  const ser = h => ['ganadoras', 'perdedoras'].map(g => ({ nombre: GRUPO[g].nombre, color: GRUPO[g].color, vals: H[h][g] || [] }));
  const ley = ['ganadoras', 'perdedoras'].map(g => `<span>${dot(GRUPO[g].color)}${GRUPO[g].nombre}</span>`).join('');
  $('#leyT').innerHTML = ley; $('#leyP').innerHTML = ley;
  barras($('#histT'), ETQ_T, ser('hist_tiempo'), { titulo: TIT_T, sub: 'segundo de la ventana en que compran', aria: 'Cuándo compran' });
  barras($('#histP'), ETQ_P, ser('hist_precio'), { titulo: TIT_P, sub: 'precio pagado por acción', aria: 'A qué precio compran' });
})();

// ---------- scatter volumen / ganancia ----------
const validas = () => D.wallets.filter(w => w.ventanas_resueltas >= (+$('#fMin').value || 1));
function pintarScatter() {
  const cont = $('#scatter'); cont.innerHTML = '';
  const ws = validas().filter(w => w.volumen > 0);
  $('#leyS').innerHTML = D.estilos.map(e => `<span title="${ESTILO[e].desc}">${dot(ESTILO[e].color)}${ESTILO[e].nombre}</span>`).join('');
  if (!ws.length) { cont.innerHTML = '<p class="pequeno">No hay wallets con suficientes ventanas.</p>'; return; }
  const W = 1000, H = 360, m = { l: 64, r: 16, t: 12, b: 40 };
  const lx = ws.map(w => Math.log10(Math.max(1, w.volumen)));
  const x0 = Math.floor(Math.min(...lx)), x1 = Math.max(x0 + 1, Math.ceil(Math.max(...lx)));
  const yt = niceTicks(Math.min(0, ...ws.map(w => w.pnl_neto)), Math.max(0, ...ws.map(w => w.pnl_neto)), 6), y0 = yt[0], y1 = yt[yt.length - 1];
  const X = v => m.l + (Math.log10(Math.max(1, v)) - x0) / (x1 - x0) * (W - m.l - m.r), Y = v => m.t + (y1 - v) / (y1 - y0) * (H - m.t - m.b);
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Volumen frente a ganancia de cada wallet' });
  for (const v of yt) { svg.append(svgEl('line', { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v), stroke: v === 0 ? 'var(--muted)' : 'var(--grid)' }));
    svg.append(svgTxt(m.l - 8, Y(v) + 4, num(v, 0), { 'text-anchor': 'end' })); }
  for (let e = x0; e <= x1; e++) { const v = Math.pow(10, e);
    svg.append(svgEl('line', { x1: X(v), x2: X(v), y1: m.t, y2: H - m.b, stroke: 'var(--grid)' }));
    svg.append(svgTxt(X(v), H - m.b + 16, v >= 1000 ? num(v / 1000, 0) + ' mil' : num(v, 0), { 'text-anchor': 'middle' })); }
  svg.append(svgTxt(m.l + (W - m.l - m.r) / 2, H - 4, 'volumen negociado (USDC, escala logarítmica)', { 'text-anchor': 'middle', fill: 'var(--muted)' }));
  svg.append(svgTxt(12, m.t + (H - m.t - m.b) / 2, 'ganancia neta (USDC)', { 'text-anchor': 'middle', fill: 'var(--muted)', transform: `rotate(-90 12 ${m.t + (H - m.t - m.b) / 2})` }));
  const pts = [];
  for (const w of [...ws].sort((a, b) => b.volumen - a.volumen)) {
    const x = X(w.volumen), y = Y(w.pnl_neto), col = ESTILO[w.estilo].color, lleno = w.fuente === 'actividad';
    const c = svgEl('circle', { cx: x, cy: y, r: lleno ? 5.5 : 4.5, fill: lleno ? col : 'var(--surface)', stroke: lleno ? 'var(--surface)' : col, 'stroke-width': 2 });
    svg.append(c); pts.push({ x, y, w });
  }
  const tip = el('div', { class: 'tip' });
  const hit = svgEl('rect', { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: 'transparent', style: 'cursor:pointer' });
  svg.append(hit); cont.append(svg); cont.append(tip);
  const cerca = ev => { const r = svg.getBoundingClientRect(), sx = (ev.clientX - r.left) / r.width * W, sy = (ev.clientY - r.top) / r.height * H;
    let best = null, bd = 14; for (const p of pts) { const d = Math.hypot(p.x - sx, p.y - sy); if (d < bd) { bd = d; best = p; } } return best; };
  hit.addEventListener('mousemove', ev => { const p = cerca(ev); if (!p) { tip.style.display = 'none'; return; }
    const w = p.w; tipEn(tip, cont, ev, `<div><b>${nombreW(w)}</b></div><div>${dot(ESTILO[w.estilo].color)} ${ESTILO[w.estilo].nombre}</div>
      <div>Ganancia neta: <b class="${cls(w.pnl_neto)}">${usd(w.pnl_neto)}</b> · por ventana ${usd(w.pnl_ventana)}</div>
      <div>Volumen: <b>${num(w.volumen, 0)}</b> · ${w.ventanas} ventanas · ${pct(w.pct_ganadas)} ganadas</div>`); });
  hit.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
  hit.addEventListener('click', ev => { const p = cerca(ev); if (p) mostrarWallet(p.w.wallet, true); });
}

// ---------- ranking ----------
const COLS = [
  ['#', null], ['Wallet', null], ['Estilo', 'estilo'], ['Ventanas', 'ventanas'], ['Volumen', 'volumen'],
  ['Ganancia neta', 'pnl_neto'], ['Por ventana', 'pnl_ventana'], ['% ganadas', 'pct_ganadas'], ['1.ª compra', 'seg_entrada_med'],
  ['Precio medio', 'precio_compra_medio'], ['Dos lados', 'pct_ambos'], ['Coste par', 'coste_par_medio'],
  ['Vende antes', 'pct_vende_antes'], ['Taker', 'pct_taker'], ['Datos', 'fuente'],
];
let orden = { k: 'pnl_neto', dir: -1 }, selW = null;
$('#fMin').value = C.min_ventanas;
D.estilos.forEach(e => $('#fEstilo').append(el('option', { value: e }, ESTILO[e].nombre)));
function pintarTabla() {
  const fe = $('#fEstilo').value, fa = $('#fAct').checked;
  let ws = validas().filter(w => (!fe || w.estilo === fe) && (!fa || w.fuente === 'actividad'));
  const k = orden.k;
  ws.sort((a, b) => { const x = a[k], y = b[k]; if (x == null) return 1; if (y == null) return -1;
    return (typeof x === 'string' ? x.localeCompare(y) : x - y) * orden.dir; });
  $('#nFilas').textContent = `${ws.length} wallets${ws.length > 200 ? ' (se muestran 200)' : ''}`;
  const th = COLS.map(([n, c]) => c ? `<th class="ord${c === k ? ' act' : ''}${c === 'estilo' ? ' izq' : ''}" data-k="${c}" data-dir="${orden.dir > 0 ? '▲' : '▼'}">${n}</th>` : `<th${n === 'Wallet' ? ' class="izq"' : ''}>${n}</th>`).join('');
  $('#tablaW').innerHTML = `<thead><tr>${th}</tr></thead><tbody>` + ws.slice(0, 200).map((w, i) => `<tr class="fila-w${w.wallet === selW ? ' sel' : ''}" data-w="${w.wallet}">
    <td>${i + 1}</td><td class="izq">${nombreW(w)}</td><td class="izq">${dot(ESTILO[w.estilo].color)} ${ESTILO[w.estilo].nombre}</td>
    <td>${w.ventanas}</td><td>${num(w.volumen, 0)}</td><td class="${cls(w.pnl_neto)}">${usd(w.pnl_neto)}</td><td class="${cls(w.pnl_ventana)}">${usd(w.pnl_ventana)}</td>
    <td>${pct(w.pct_ganadas)}</td><td>${seg(w.seg_entrada_med)}</td><td>${px(w.precio_compra_medio)}</td><td>${pct(w.pct_ambos)}</td>
    <td>${px(w.coste_par_medio)}</td><td>${pct(w.pct_vende_antes)}</td><td>${pct(w.pct_taker)}</td>
    <td class="pequeno">${w.fuente === 'actividad' ? 'completos' : 'parciales'}</td></tr>`).join('') + '</tbody>';
  $('#tablaW').querySelectorAll('th.ord').forEach(th => th.addEventListener('click', () => {
    orden = { k: th.dataset.k, dir: th.dataset.k === orden.k ? -orden.dir : -1 }; pintarTabla(); }));
  $('#tablaW').querySelectorAll('tr.fila-w').forEach(tr => tr.addEventListener('click', () => mostrarWallet(tr.dataset.w, true)));
}
['#fMin', '#fEstilo', '#fAct'].forEach(s => $(s).addEventListener('change', () => { pintarTabla(); pintarScatter(); }));

// ---------- detalle de una wallet ----------
function graficoOps(cont, det) {
  const W = 1000, H = 300, m = { l: 48, r: 16, t: 12, b: 36 }, t0 = -0.15 * P, t1 = 1.05 * P;
  const X = t => m.l + (Math.min(t1, Math.max(t0, t)) - t0) / (t1 - t0) * (W - m.l - m.r), Y = p => m.t + (1 - p) * (H - m.t - m.b);
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Compras y ventas por segundo de la ventana y precio' });
  svg.append(svgEl('rect', { x: X(0), y: m.t, width: X(P) - X(0), height: H - m.t - m.b, fill: 'var(--surface-2)' }));
  for (const v of [0, 0.25, 0.5, 0.75, 1]) { svg.append(svgEl('line', { x1: m.l, x2: W - m.r, y1: Y(v), y2: Y(v), stroke: v === 0.5 ? 'var(--muted)' : 'var(--grid)' }));
    svg.append(svgTxt(m.l - 6, Y(v) + 4, v.toFixed(2), { 'text-anchor': 'end' })); }
  for (let i = 0; i <= NT; i += 2) svg.append(svgTxt(X(paso * i), H - m.b + 16, Math.round(paso * i) + ' s', { 'text-anchor': 'middle' }));
  svg.append(svgTxt(m.l + (W - m.l - m.r) / 2, H - 4, 'segundo de la ventana (zona sombreada = ventana abierta)', { 'text-anchor': 'middle', fill: 'var(--muted)' }));
  const pts = [];
  for (const v of det) for (const e of v.eventos) {
    const [t, tipo, lado, p, sz, tk] = e; if (tipo !== 'B' && tipo !== 'S') continue;
    const x = X(t), y = Y(p), col = lado === 'up' ? 'var(--up)' : 'var(--down)';
    svg.append(svgEl('circle', tipo === 'B' ? { cx: x, cy: y, r: 4, fill: col, stroke: 'var(--surface)', 'stroke-width': 1.5, opacity: .85 }
      : { cx: x, cy: y, r: 4, fill: 'var(--surface)', stroke: col, 'stroke-width': 2 }));
    pts.push({ x, y, e, v });
  }
  const tip = el('div', { class: 'tip' });
  const hit = svgEl('rect', { x: m.l, y: m.t, width: W - m.l - m.r, height: H - m.t - m.b, fill: 'transparent' });
  svg.append(hit); cont.append(svg); cont.append(tip);
  hit.addEventListener('mousemove', ev => {
    const r = svg.getBoundingClientRect(), sx = (ev.clientX - r.left) / r.width * W, sy = (ev.clientY - r.top) / r.height * H;
    const cerca = pts.filter(p => Math.hypot(p.x - sx, p.y - sy) < 10).slice(0, 6);
    if (!cerca.length) { tip.style.display = 'none'; return; }
    tipEn(tip, cont, ev, cerca.map(({ e, v }) => `<div>${hora(v.inicio)} · s ${num(e[0], 0)} · <b>${e[1] === 'B' ? 'COMPRA' : 'VENDE'}</b>
      <span class="${e[2] === 'up' ? 'pos' : 'neg'}">${e[2] === 'up' ? '▲ Up' : '▼ Down'}</span> ${num(e[4], 1)} acc. a ${px(e[3])}
      <span class="pequeno">${e[5] == null ? '' : e[5] ? '· taker' : '· maker'}</span></div>`).join(''));
  });
  hit.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
}

function mostrarWallet(wallet, scroll) {
  selW = wallet; pintarTabla();
  const w = D.wallets.find(x => x.wallet === wallet), box = $('#detalle');
  const tile = (l, v, c = '') => `<div class="tile"><div class="v ${c}">${v}</div><div class="l">${l}</div></div>`;
  box.innerHTML = `<h2>Detalle · ${nombreW(w)}</h2>
    <div class="card">
      <div class="fila"><span>${dot(ESTILO[w.estilo].color)} <b>${ESTILO[w.estilo].nombre}</b></span>
        ${w.etiquetas.map(t => `<span class="chip">${t}</span>`).join('')}
        <a href="https://polymarket.com/profile/${w.wallet}" target="_blank" rel="noopener" style="margin-left:auto">perfil en Polymarket ↗</a></div>
      <div class="pequeno mono">${w.wallet}</div>
      ${w.fuente === 'actividad' ? '' : '<div class="aviso">Datos parciales: solo sus operaciones en el mercado, sin split ni merge. Sube <code>--analizar</code> para incluirla en el análisis completo.</div>'}
      ${w.truncado ? '<div class="aviso">Su actividad tenía más filas de las que se pudieron bajar: puede faltar alguna operación.</div>' : ''}
      ${w.inconsistentes ? `<div class="aviso">En ${w.inconsistentes} ventanas vendió más de lo que se le vio comprar (faltan datos). Su ganancia puede estar mal calculada.</div>` : ''}
      <div class="tiles">
        ${tile('ganancia neta (USDC)', usd(w.pnl_neto), cls(w.pnl_neto))}${tile('por ventana', usd(w.pnl_ventana), cls(w.pnl_ventana))}
        ${tile('ventanas ganadas', `${pct(w.pct_ganadas)} <span class="pequeno">de ${w.ventanas_resueltas}</span>`)}
        ${tile('rentabilidad', pct(w.roi), cls(w.roi))}${tile('volumen', num(w.volumen, 0))}${tile('comisión estimada', num(w.comisiones, 2))}
        ${tile('1.ª compra (mediana)', seg(w.seg_entrada_med))}${tile('precio medio de compra', px(w.precio_compra_medio))}
        ${tile('ventanas con los dos lados', pct(w.pct_ambos))}${tile('coste del par (mediana)', px(w.coste_par_medio))}
        ${tile('vende antes del cierre', pct(w.pct_vende_antes))}${tile('toma liquidez (taker)', pct(w.pct_taker))}
      </div>
      <div class="dos">
        <div><h4>Cuándo compra</h4><div class="chart peq" id="dT"></div></div>
        <div><h4>A qué precio compra</h4><div class="chart peq" id="dP"></div></div>
      </div>
      <div id="dOps"></div>
      <div class="tabla" id="dVent"></div>
    </div>`;
  const s = [{ nombre: 'esta wallet', color: ESTILO[w.estilo].color }];
  barras($('#dT'), ETQ_T, [{ ...s[0], vals: normal(w.hist_tiempo) }], { titulo: TIT_T, sub: 'segundo de la ventana', aria: 'Cuándo compra' });
  barras($('#dP'), ETQ_P, [{ ...s[0], vals: normal(w.hist_precio) }], { titulo: TIT_P, sub: 'precio pagado', aria: 'A qué precio compra' });
  const det = w.detalle;
  if (det) {
    const ops = $('#dOps');
    ops.append(el('h4', {}, 'Todas sus compras y ventas, ventana a ventana superpuestas'));
    ops.append(el('div', { class: 'legend' }, `<span>${dot('var(--up)')}compra Up</span><span>${dot('var(--down)')}compra Down</span>
      <span><span class="dot" style="border:2px solid var(--up);background:var(--surface)"></span>venta Up</span>
      <span><span class="dot" style="border:2px solid var(--down);background:var(--surface)"></span>venta Down</span>`));
    const c = el('div', { class: 'chart' }); ops.append(c); graficoOps(c, det);
    const sh = (n, p) => n ? `${num(n, 0)} <span class="pequeno">a ${px(p)}</span>` : '–';
    $('#dVent').innerHTML = `<h4>Ventana a ventana</h4><table><thead><tr><th>Ventana</th><th>Resultado</th><th>Compró Up</th><th>Compró Down</th>
      <th>Coste par</th><th>Vendió</th><th>Split / merge</th><th>Le quedan Up / Down</th><th>Operaciones</th><th>Comisión</th><th>Ganancia neta</th></tr></thead><tbody>` +
      det.map(v => `<tr><td><a href="https://polymarket.com/event/${v.slug}" target="_blank" rel="noopener">${hora(v.inicio)}</a></td><td>${badge(v.resultado)}</td>
        <td>${sh(v.up_sh, v.up_px)}</td><td>${sh(v.down_sh, v.down_px)}</td><td>${px(v.coste_par)}</td><td>${sh(v.vend_sh, v.vend_px)}</td>
        <td>${v.split || v.merge ? `${num(v.split, 0)} / ${num(v.merge, 0)}` : '–'}</td><td>${num(v.fin_up, 0)} / ${num(v.fin_down, 0)}</td>
        <td>${v.n_ops}${v.eventos_recortados ? ` <span class="pequeno">(${v.eventos_recortados} no mostradas)</span>` : ''}</td>
        <td>${num(v.comision, 2)}</td><td class="${cls(v.pnl_neto)}">${usd(v.pnl_neto)}</td></tr>`).join('') + '</tbody></table>';
  } else {
    $('#dOps').innerHTML = '<p class="pequeno">Sin detalle por operación: esta wallet no se analizó a fondo.</p>';
  }
  if (scroll) box.scrollIntoView({ behavior: 'smooth' });
}

// ---------- mercados ----------
$('#tablaM').innerHTML = `<thead><tr><th>Ventana</th><th>Resultado</th><th>Precio a batir</th><th>Operaciones</th><th>Volumen (USDC)</th><th>Wallets</th><th class="izq">Notas</th></tr></thead><tbody>` +
  D.mercados.map(m => `<tr><td><a href="https://polymarket.com/event/${m.slug}" target="_blank" rel="noopener">${fecha(m.inicio)}</a></td><td>${badge(m.resultado)}</td>
    <td>${num(m.precio_a_batir, 2)}</td><td>${num(m.n_operaciones, 0)}</td><td>${num(m.volumen, 0)}</td><td>${num(m.n_wallets, 0)}</td>
    <td class="izq pequeno">${m.truncado ? 'faltan operaciones (límite de la API)' : ''}</td></tr>`).join('') + '</tbody>';

pintarScatter(); pintarTabla();
const primera = D.wallets.find(w => w.fuente === 'actividad' && w.ventanas_resueltas >= C.min_ventanas);
if (primera) mostrarWallet(primera.wallet, false);
</script>
</body>
</html>
"""
