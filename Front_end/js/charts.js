/* =====================================================================
   1000 FiX ERP — dependency-free SVG charts (tokens palette, dark-aware).
   Sparkline · line · bar (v/h) · donut · gauge · heatmap · waterfall ·
   funnel. All directly labelled; ≤8 series; deterministic from seeds.
   ===================================================================== */
(function () {
'use strict';
var CSS = function (n, d) {
  try { return (getComputedStyle(document.documentElement).getPropertyValue(n) || '').trim() || d; }
  catch (e) { return d; }
};
var PAL = function () { return [CSS('--chart-1','#0F9C8E'), CSS('--chart-2','#E8590C'), CSS('--chart-3','#3F51B5'),
  CSS('--chart-4','#6A4C93'), CSS('--chart-5','#B23A2E'), CSS('--chart-6','#2E9BD6'),
  CSS('--chart-7','#12885E'), CSS('--chart-8','#8A8A8A')]; };
var INK = function () { return CSS('--ink-500','#616161'); };
var STROKE = function () { return CSS('--stroke','#E0E0E0'); };
function esc(s){ return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function path(pts) { return pts.map(function(p,i){ return (i?'L':'M') + p[0].toFixed(1) + ' ' + p[1].toFixed(1); }).join(' '); }

/* ---- sparkline: 44×16 — used in every KPI card --------------------- */
window.FXSpark = function (data, w, h, color) {
  w = w || 44; h = h || 16; color = color || CSS('--chart-1','#0F9C8E');
  var mn = Math.min.apply(null, data), mx = Math.max.apply(null, data);
  if (mx === mn) mx = mn + 1;
  var pts = data.map(function (v, i) {
    return [2 + i * (w - 4) / (data.length - 1), h - 2 - (v - mn) / (mx - mn) * (h - 4)];
  });
  return '<svg class="spark" width="' + w + '" height="' + h + '" viewBox="0 0 ' + w + ' ' + h + '" aria-hidden="true">' +
    '<path d="' + path(pts) + '" fill="none" stroke="' + color + '" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>' +
    '<circle cx="' + pts[pts.length-1][0].toFixed(1) + '" cy="' + pts[pts.length-1][1].toFixed(1) + '" r="1.6" fill="' + color + '"/></svg>';
};

/* ---- line chart ------------------------------------------------------ */
window.FXLine = function (series, labels, opt) {
  opt = opt || {}; var W = opt.w || 520, H = opt.h || 190, padL = 44, padB = 24, padT = 12;
  var all = []; series.forEach(function (s) { all = all.concat(s.v); });
  var mx = Math.max.apply(null, all) * 1.08, mn = Math.min(0, Math.min.apply(null, all));
  var pal = PAL();
  var X = function (i) { return padL + i * (W - padL - 8) / (labels.length - 1); };
  var Y = function (v) { return H - padB - (v - mn) / (mx - mn) * (H - padB - padT); };
  var g = '<svg width="' + W + '" height="' + H + '" role="img" class="chart">';
  for (var k = 0; k <= 4; k++) {
    var yy = padT + k * (H - padB - padT) / 4, val = mx - k * (mx - mn) / 4;
    g += '<line x1="' + padL + '" x2="' + (W-6) + '" y1="' + yy + '" y2="' + yy + '" stroke="' + STROKE() + '" stroke-width="1"/>' +
         '<text x="' + (padL-6) + '" y="' + (yy+3) + '" text-anchor="end" font-size="9" fill="' + INK() + '">' + (Math.round(val*10)/10) + '</text>';
  }
  labels.forEach(function (l, i) { if (labels.length <= 14 || i % 2 === 0) g += '<text x="' + X(i) + '" y="' + (H-6) + '" text-anchor="middle" font-size="9" fill="' + INK() + '">' + esc(l) + '</text>'; });
  series.forEach(function (s, si) {
    var pts = s.v.map(function (v, i) { return [X(i), Y(v)]; });
    g += '<path d="' + path(pts) + '" fill="none" stroke="' + pal[si % 8] + '" stroke-width="1.8" stroke-linejoin="round"/>';
    pts.forEach(function (p, i) { g += '<circle cx="' + p[0] + '" cy="' + p[1] + '" r="2.2" fill="' + pal[si % 8] + '"/>'; });
    g += '<rect x="' + (W - 150) + '" y="' + (8 + si * 16) + '" width="8" height="8" rx="2" fill="' + pal[si % 8] + '"/>' +
         '<text x="' + (W - 138) + '" y="' + (15 + si * 16) + '" font-size="10" fill="' + INK() + '">' + esc(s.n) + '</text>';
  });
  return g + '</svg>';
};

/* ---- bar chart (vertical / horizontal) -------------------------------- */
window.FXBar = function (rows, opt) {
  opt = opt || {}; var horiz = !!opt.h, W = opt.w || 520, H = opt.h || 190, pal = PAL();
  var mx = Math.max.apply(null, rows.map(function (r) { return r.v; })) * 1.12;
  var g = '<svg width="' + W + '" height="' + H + '" role="img" class="chart">';
  if (horiz) {
    var bh = Math.min(22, (H - 8) / rows.length - 6);
    rows.forEach(function (r, i) {
      var y = 6 + i * ((H - 8) / rows.length), wv = (r.v / mx) * (W - 150);
      g += '<text x="' + (W - 88) + '" y="' + (y + bh/2 + 3) + '" font-size="10" fill="' + INK() + '" text-anchor="end">' + esc(r.k) + '</text>' +
           '<rect x="' + (W - 82) + '" y="' + y + '" width="0" height="' + bh + '" fill="' + (r.c || pal[i % 8]) + '"><animate attributeName="width" values="0;' + Math.max(2,wv) + '" dur=".4s" fill="freeze"/></rect>' +
           '<text x="' + (W - 82 + Math.max(2,wv) + 4) + '" y="' + (y + bh/2 + 3) + '" font-size="10" font-weight="600" fill="' + CSS('--ink-900','#242424') + '">' + esc(r.f || r.v) + '</text>';
    });
  } else {
    var n = rows.length, bw = Math.min(38, (W - 60) / n - 8);
    rows.forEach(function (r, i) {
      var x = 44 + i * ((W - 52) / n) + ((W - 52) / n - bw) / 2;
      var h = (r.v / mx) * (H - 44);
      g += '<rect x="' + x + '" y="' + (H - 26 - h) + '" width="' + bw + '" height="' + Math.max(2,h) + '" rx="2" fill="' + (r.c || pal[i % 8]) + '"/>' +
           '<text x="' + (x + bw/2) + '" y="' + (H - 28 - h) + '" text-anchor="middle" font-size="9" font-weight="600" fill="' + CSS('--ink-900','#242424') + '">' + esc(r.f || r.v) + '</text>' +
           '<text x="' + (x + bw/2) + '" y="' + (H - 10) + '" text-anchor="middle" font-size="9" fill="' + INK() + '">' + esc(r.k) + '</text>';
    });
    g += '<line x1="40" x2="' + (W-8) + '" y1="' + (H-26) + '" y2="' + (H-26) + '" stroke="' + STROKE() + '"/>';
  }
  return g + '</svg>';
};

/* ---- donut ------------------------------------------------------------- */
window.FXDonut = function (rows, opt) {
  opt = opt || {}; var W = opt.w || 190, H = opt.h || 150, R = 46, cx = W/2, cy = H/2 - 6, pal = PAL();
  var tot = rows.reduce(function (n, r) { return n + r.v; }, 0) || 1, a0 = -Math.PI / 2, g = '<svg width="' + W + '" height="' + H + '" role="img" class="chart">';
  var ri = Math.round(R * 0.62);                  /* inner radius — real hole so centre text sits on card surface (dark-mode safe) */
  rows.forEach(function (r, i) {
    var a1 = a0 + r.v / tot * Math.PI * 2;
    var large = (a1 - a0) > Math.PI ? 1 : 0;
    var x0o = cx + R * Math.cos(a0), y0o = cy + R * Math.sin(a0), x1o = cx + R * Math.cos(a1), y1o = cy + R * Math.sin(a1);
    var x0i = cx + ri * Math.cos(a1), y0i = cy + ri * Math.sin(a1), x1i = cx + ri * Math.cos(a0), y1i = cy + ri * Math.sin(a0);
    g += '<path d="M' + x0o.toFixed(1) + ' ' + y0o.toFixed(1) + ' A' + R + ' ' + R + ' 0 ' + large + ' 1 ' + x1o.toFixed(1) + ' ' + y1o.toFixed(1) +
      ' L' + x0i.toFixed(1) + ' ' + y0i.toFixed(1) + ' A' + ri + ' ' + ri + ' 0 ' + large + ' 0 ' + x1i.toFixed(1) + ' ' + y1i.toFixed(1) + ' Z" fill="' + (r.c || pal[i % 8]) + '" opacity=".92" stroke="var(--surface)" stroke-width="1.5"/>';
    a0 = a1;
  });
  var mid = opt.centre || '';
  g += '<text x="' + cx + '" y="' + (cy - 2) + '" text-anchor="middle" font-size="15" font-weight="700" fill="' + CSS('--ink-900','#242424') + '">' + esc(mid) + '</text>' +
       '<text x="' + cx + '" y="' + (cy + 12) + '" text-anchor="middle" font-size="8" fill="' + INK() + '">' + esc(opt.centreSub || '') + '</text>';
  g += '</svg><div class="donut-legend">' + rows.map(function (r, i) {
    return '<span><i style="background:' + (r.c || pal[i % 8]) + '"></i>' + esc(r.k) + ' <b>' + esc(r.f || r.v) + '</b></span>';
  }).join('') + '</div>';
  return g;
};

/* ---- gauge --------------------------------------------------------------- */
window.FXGauge = function (val, max, label, opt) {
  opt = opt || {}; var W = 150, H = 96, R = 44, cx = W/2, cy = 66;
  var frac = Math.max(0, Math.min(1, val / (max || 100)));
  var a0 = Math.PI, a1 = Math.PI - frac * Math.PI;
  var x1 = cx + R * Math.cos(a1), y1 = cy + R * Math.sin(a1);
  var col = frac >= .85 ? CSS('--ok-bold','#107C10') : frac >= .6 ? CSS('--warn-bold','#F7630C') : CSS('--err-bold','#C50F1F');
  var lab = String(label || ''); if (lab.length > 22) lab = lab.slice(0, 21) + '…';
  return '<svg width="' + W + '" height="' + H + '" role="img" class="chart">' +
    '<path d="M' + (cx - R) + ' ' + cy + ' A' + R + ' ' + R + ' 0 0 1 ' + (cx + R) + ' ' + cy + '" fill="none" stroke="' + CSS('--surface-3','#F0F0F0') + '" stroke-width="10" stroke-linecap="round"/>' +
    '<path d="M' + (cx - R) + ' ' + cy + ' A' + R + ' ' + R + ' 0 0 1 ' + x1.toFixed(1) + ' ' + y1.toFixed(1) + '" fill="none" stroke="' + col + '" stroke-width="10" stroke-linecap="round"/>' +
    '<text x="' + cx + '" y="' + (cy - 12) + '" text-anchor="middle" font-size="17" font-weight="700" fill="' + CSS('--ink-900','#242424') + '">' + esc(opt.disp || (Math.round(frac * 100) + '%')) + '</text>' +
    '<text x="' + cx + '" y="' + (cy + 16) + '" text-anchor="middle" font-size="8" fill="' + INK() + '">' + esc(lab) + '</text></svg>';
};

/* ---- heatmap -------------------------------------------------------------- */
window.FXHeat = function (rowKeys, colKeys, matrix, opt) {
  opt = opt || {}; var cell = opt.cell || 30, padL = 108, padT = 20;
  var W = padL + colKeys.length * cell + 8, H = padT + rowKeys.length * cell + 6;
  var mx = 0; matrix.forEach(function (r) { r.forEach(function (v) { if (v > mx) mx = v; }); });
  var base = CSS('--primary','#0E7A6E');
  var g = '<svg width="' + W + '" height="' + H + '" role="img" class="chart">';
  rowKeys.forEach(function (rk, ri) {
    g += '<text x="' + (padL - 6) + '" y="' + (padT + ri * cell + cell/2 + 3) + '" text-anchor="end" font-size="9" fill="' + INK() + '">' + esc(rk) + '</text>';
    colKeys.forEach(function (ck, ci) {
      var v = matrix[ri][ci] || 0, f = mx ? v / mx : 0;
      if (ri === 0) g += '<text x="' + (padL + ci * cell + cell/2) + '" y="' + (padT - 6) + '" text-anchor="middle" font-size="8" fill="' + INK() + '">' + esc(ck) + '</text>';
      g += '<rect x="' + (padL + ci * cell + 1) + '" y="' + (padT + ri * cell + 1) + '" width="' + (cell-2) + '" height="' + (cell-2) + '" rx="2" fill="' + base + '" opacity="' + (0.08 + f * 0.92).toFixed(2) + '"><title>' + esc(rk + ' · ' + ck + ': ' + v) + '</title></rect>';
      if (v) g += '<text x="' + (padL + ci*cell + cell/2) + '" y="' + (padT + ri*cell + cell/2 + 3) + '" text-anchor="middle" font-size="8" fill="' + (f > .5 ? '#fff' : CSS('--ink-900','#242424')) + '">' + v + '</text>';
    });
  });
  return g + '</svg>';
};

/* ---- waterfall ------------------------------------------------------------- */
window.FXWaterfall = function (rows, opt) {
  opt = opt || {}; var W = opt.w || 540, H = opt.h || 180, padL = 40;
  var cum = 0, all = [];
  rows.forEach(function (r) { var v = r.t === 'total' ? r.v : cum + r.v; all.push(cum, v); if (r.t !== 'total') cum = v; else cum = r.v; });
  var mx = Math.max.apply(null, all.concat([0])), mn = Math.min.apply(null, all.concat([0]));
  var Y = function (v) { return H - 24 - (v - mn) / (mx - mn || 1) * (H - 44); };
  var bw = Math.min(52, (W - padL - 12) / rows.length - 8), g = '<svg width="' + W + '" height="' + H + '" role="img" class="chart">';
  var run = 0;
  rows.forEach(function (r, i) {
    var x = padL + i * ((W - padL - 8) / rows.length) + 4;
    var y1, y2;
    if (r.t === 'total') { y1 = Y(r.v); y2 = Y(0); run = r.v; }
    else { y1 = Y(run + r.v); y2 = Y(run); run += r.v; }
    var col = r.t === 'total' ? CSS('--ink-500','#616161') : r.v >= 0 ? CSS('--ok-bold','#107C10') : CSS('--err-bold','#C50F1F');
    g += '<rect x="' + x + '" y="' + Math.min(y1, y2) + '" width="' + bw + '" height="' + Math.max(2, Math.abs(y2 - y1)) + '" fill="' + col + '" rx="2"/>' +
         '<text x="' + (x + bw/2) + '" y="' + (Math.min(y1,y2) - 4) + '" text-anchor="middle" font-size="9" font-weight="600" fill="' + CSS('--ink-900','#242424') + '">' + (r.v > 0 ? '+' : '') + esc(r.f || r.v) + '</text>' +
         '<text x="' + (x + bw/2) + '" y="' + (H - 8) + '" text-anchor="middle" font-size="8" fill="' + INK() + '">' + esc(r.k) + '</text>';
  });
  g += '<line x1="' + padL + '" x2="' + (W-6) + '" y1="' + Y(0) + '" y2="' + Y(0) + '" stroke="' + STROKE() + '"/>';
  return g + '</svg>';
};

/* ---- funnel ------------------------------------------------------------------ */
window.FXFunnel = function (stages) {
  var W = 300, H = stages.length * 40 + 8, mx = stages[0].v || 1;
  var pal = PAL();
  var g = '<svg width="' + W + '" height="' + H + '" role="img" class="chart">';
  stages.forEach(function (s, i) {
    var w = Math.max(64, (s.v / mx) * (W - 90)), x = (W - w) / 2, y = 6 + i * 40;
    g += '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="28" rx="4" fill="' + pal[i % 8] + '" opacity=".9"/>' +
         '<text x="' + (W/2) + '" y="' + (y + 18) + '" text-anchor="middle" font-size="10" font-weight="600" fill="#fff">' + esc(s.k) + ' · ' + esc(s.f || s.v) + (i ? ' (' + Math.round(s.v / mx * 100) + '%)' : '') + '</text>';
  });
  return g + '</svg>';
};
})();
