# -*- coding: utf-8 -*-
"""
exhibits — the visual language of the guide-book library.

Every exhibit is generated from measured specification data. Nothing here
invents a number. Where a data set is empty the generator returns None and
the document builder omits the exhibit rather than printing an empty frame.

House rules for every exhibit
  · one idea per exhibit, stated in the title
  · direct labelling in preference to legends
  · no gridlines where a value label will do
  · the category accent carries identity; the navy carries structure
  · every figure sized to the 174 mm text column so nothing is scaled in Word
"""

import os
import re
import math
import textwrap
from collections import OrderedDict, Counter

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle
import matplotlib.font_manager as fm
import numpy as np

import theme as T

# ------------------------------------------------------------------- fonts
_AVAILABLE = {f.name for f in fm.fontManager.ttflist}
FAMILY = (
    "Calibri"
    if "Calibri" in _AVAILABLE
    else ("Carlito" if "Carlito" in _AVAILABLE else "DejaVu Sans")
)
MONO = "Consolas" if "Consolas" in _AVAILABLE else "DejaVu Sans Mono"

matplotlib.rcParams.update(
    {
        "font.family": FAMILY,
        "font.size": 8.0,
        "axes.edgecolor": T.hexc(T.RULE),
        "axes.labelcolor": T.hexc(T.INK_SOFT),
        "text.color": T.hexc(T.INK),
        "xtick.color": T.hexc(T.GREY),
        "ytick.color": T.hexc(T.INK_SOFT),
        "axes.linewidth": 0.6,
        "xtick.major.width": 0.5,
        "ytick.major.width": 0.5,
        "figure.dpi": T.DPI,
        "savefig.dpi": T.DPI,
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "svg.fonttype": "none",
    }
)

W = T.CONTENT_W_IN  # 6.85 in — full text column


# ------------------------------------------------------------------ helpers
def _wrap(s, n, max_lines=None):
    """Wrap on word boundaries only — never break a word mid-glyph."""
    s = re.sub(r"\s+", " ", str(s)).strip()
    if not s:
        return ""
    lines = textwrap.wrap(
        s, max(int(n), 4), break_long_words=False, break_on_hyphens=False
    )
    if max_lines and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" ,&-") + "…"
    return "\n".join(lines)


def _clip(s, n):
    s = re.sub(r"\s+", " ", str(s)).strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


_KEEP_UPPER = {
    "QC",
    "AI",
    "ML",
    "KYC",
    "ETA",
    "NID",
    "OTP",
    "SLA",
    "WIP",
    "B2B",
    "CSAT",
    "NPS",
    "PO",
    "GRN",
    "AMC",
    "RMA",
    "GL",
    "AR",
    "AP",
    "VAT",
    "TDS",
    "VDS",
    "HR",
    "IT",
    "SMS",
    "OTC",
    "L1",
    "L2",
    "L3",
    "EOL",
    "EOD",
    "TAT",
    "FX",
    "PDPA",
    "ISO",
    "MSP",
}


def _case(s):
    """Title-case a state name without destroying acronyms."""
    out = []
    for w in str(s).split():
        core = w.strip("()[].,")
        if core.upper() in _KEEP_UPPER or (
            core.isupper() and len(core) <= 3 and not core.isdigit()
        ):
            out.append(w.upper())
        elif "-" in w:
            out.append(
                "-".join(
                    p.capitalize() if p.upper() not in _KEEP_UPPER else p.upper()
                    for p in w.split("-")
                )
            )
        else:
            out.append(w.capitalize())
    return " ".join(out)


def _save(fig, path):
    """Save at print resolution, then palette-quantise.

    Exhibits are flat-colour vector-like graphics; a 256-entry adaptive
    palette is visually lossless here and cuts the embedded weight of a
    typical guide book by roughly two thirds.
    """
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    fig.savefig(
        path, bbox_inches="tight", pad_inches=0.04, facecolor="white", edgecolor="none"
    )
    plt.close(fig)
    try:
        from PIL import Image

        im = Image.open(path).convert("RGB")
        q = im.quantize(colors=256, method=Image.MEDIANCUT, dither=Image.NONE)
        q.save(path, format="PNG", optimize=True, dpi=(T.DPI, T.DPI))
    except Exception:
        pass
    return path


def _titleblock(ax, title, sub=None, accent=T.NAVY):
    """Left-aligned title with an accent tick, drawn in axes-fraction space."""
    ax.text(
        0.0,
        1.0,
        title,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9.5,
        fontweight="bold",
        color=T.hexc(T.NAVY),
    )
    if sub:
        ax.text(
            0.0,
            1.0,
            sub,
            transform=ax.transAxes,
            ha="left",
            va="top",
            fontsize=7.6,
            color=T.hexc(T.GREY),
        )


def _bare(ax, keep=()):
    for s in ("top", "right", "bottom", "left"):
        ax.spines[s].set_visible(s in keep)
    ax.tick_params(length=0)


def _rounded(ax, x, y, w, h, fc, ec="none", lw=0.8, r=0.02, z=2, alpha=1.0):
    p = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0,rounding_size=%f" % r,
        linewidth=lw,
        facecolor=fc,
        edgecolor=ec,
        zorder=z,
        alpha=alpha,
        mutation_aspect=1,
    )
    ax.add_patch(p)
    return p


# ============================================================== E1 scorecard
def scorecard(path, sc, accent, title, subtitle, cols=4):
    """Tile grid of the specification's measured dimensions.

    Reads as a dashboard: label first in small caps, figure beneath it,
    a category-accent spine on the left edge of every live tile and a
    muted treatment for any dimension measured at zero — which is itself
    a finding, not a blank.
    """
    items = list(sc.items())
    rows = int(math.ceil(len(items) / float(cols)))
    cellw, cellh = 10.0, 10.0
    fig_h = 0.545 * rows + 0.72
    fig, ax = plt.subplots(figsize=(W, fig_h))
    ax.set_xlim(0, cols * cellw)
    ax.set_ylim(-rows * cellh, 0.34 * cellh)
    ax.axis("off")

    ax.text(
        0,
        0.30 * cellh,
        title,
        fontsize=10.4,
        fontweight="bold",
        color=T.hexc(T.NAVY),
        va="bottom",
    )
    ax.text(0, 0.26 * cellh, subtitle, fontsize=7.5, color=T.hexc(T.GREY), va="top")

    padx, pady = 0.30, 0.55
    for i, (k, v) in enumerate(items):
        r, c = divmod(i, cols)
        x = c * cellw + padx
        y = -(r + 1) * cellh + pady
        w = cellw - 2 * padx
        h = cellh - 2 * pady
        zero = v == 0
        _rounded(
            ax,
            x,
            y,
            w,
            h,
            T.hexc(T.BG_PAPER if zero else T.BG_TINT),
            ec=T.hexc(T.RULE_SOFT),
            lw=0.6,
            r=0.28,
        )
        ax.add_patch(
            Rectangle(
                (x, y),
                0.32,
                h,
                facecolor=T.hexc(T.GREY_LIGHT if zero else accent),
                edgecolor="none",
                zorder=4,
            )
        )
        ax.text(
            x + 1.05,
            y + h * 0.76,
            _wrap(k.upper(), 24, 1),
            fontsize=6.8,
            color=T.hexc(T.GREY),
            va="center",
            ha="left",
            zorder=5,
        )
        ax.text(
            x + 1.05,
            y + h * 0.34,
            str(v),
            fontsize=15.5,
            fontweight="bold",
            color=T.hexc(T.GREY_LIGHT if zero else T.NAVY),
            va="center",
            ha="left",
            zorder=5,
        )
    return _save(fig, path)


# ======================================================= E2 requirements/area
def req_by_area(path, area_mix, accent, title, subtitle):
    if not area_mix:
        return None
    labels = [_clip(k, 46) for k in area_mix.keys()]
    vals = list(area_mix.values())
    order = np.argsort(vals)
    labels = [labels[i] for i in order]
    vals = [vals[i] for i in order]
    h = max(1.7, 0.30 * len(vals) + 1.1)
    fig, ax = plt.subplots(figsize=(W, h))
    y = np.arange(len(vals))
    ax.barh(y, vals, height=0.62, color=T.hexc(accent), zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8.0, color=T.hexc(T.INK))
    ax.set_xlim(0, max(vals) * 1.16)
    ax.set_xticks([])
    _bare(ax)
    for yy, v in zip(y, vals):
        ax.text(
            v + max(vals) * 0.018,
            yy,
            str(v),
            va="center",
            fontsize=8.2,
            fontweight="bold",
            color=T.hexc(T.NAVY),
        )
    ax.grid(axis="x", visible=False)
    _titleblock(ax, title, subtitle)
    return _save(fig, path)


# ============================================================ E3 priority mix
def priority_mix(path, mix, total, title, subtitle):
    order = ["P0", "P1", "P2", "P3"]
    data = [(p, mix.get(p, 0)) for p in order if mix.get(p, 0)]
    if not data:
        return None
    fig, ax = plt.subplots(figsize=(W, 0.46 * len(data) + 0.95))
    ax.axis("off")
    axd = fig.add_axes([0.02, 0.02, 0.30, 0.82])
    vals = [v for _, v in data]
    cols = [T.hexc(T.PRIORITY[p]) for p, _ in data]
    wedges, _ = axd.pie(
        vals,
        colors=cols,
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.36, edgecolor="white", linewidth=1.6),
    )
    axd.text(
        0,
        0.10,
        str(total),
        ha="center",
        va="center",
        fontsize=18,
        fontweight="bold",
        color=T.hexc(T.NAVY),
    )
    axd.text(
        0,
        -0.26,
        "REQUIREMENTS",
        ha="center",
        va="center",
        fontsize=7.0,
        color=T.hexc(T.GREY),
    )
    axd.set_aspect("equal")

    meaning = {
        "P0": "Blocking — cannot be descoped",
        "P1": "Must have — in the committed scope",
        "P2": "Important — planned, deferrable under pressure",
        "P3": "Desirable — value-add if capacity allows",
    }
    step = 0.80 / max(len(data), 1)
    for i, (p, v) in enumerate(data):
        yy = 0.86 - (i + 0.5) * step
        ax.add_patch(
            Rectangle(
                (0.38, yy - 0.045),
                0.018,
                0.090,
                transform=ax.transAxes,
                facecolor=T.hexc(T.PRIORITY[p]),
                edgecolor="none",
                clip_on=False,
            )
        )
        ax.text(
            0.415,
            yy + 0.030,
            "%s  ·  %d requirement%s  ·  %.0f%%"
            % (p, v, "" if v == 1 else "s", 100.0 * v / total),
            transform=ax.transAxes,
            fontsize=8.4,
            fontweight="bold",
            color=T.hexc(T.NAVY),
            va="center",
        )
        ax.text(
            0.415,
            yy - 0.038,
            meaning[p],
            transform=ax.transAxes,
            fontsize=7.2,
            color=T.hexc(T.GREY),
            va="center",
        )
    _titleblock(ax, title, subtitle)
    return _save(fig, path)


# =========================================================== E4 layer mix
def layer_allocation(path, alloc, title, subtitle):
    keys = [k for k in ["L1", "L2", "L3", "L4", "L5", "L6"] if k in alloc]
    vals = [(alloc[k].get("pct") or 0.0) for k in keys]
    if not keys or sum(vals) <= 0:
        return None
    tot = sum(vals)
    vals = [v * 100.0 / tot for v in vals]
    fig, ax = plt.subplots(figsize=(W, 1.05 + 0.26 * len(keys)))
    ax.axis("off")
    x = 0.0
    barY, barH = 0.72, 0.20
    for k, v in zip(keys, vals):
        ax.add_patch(
            Rectangle(
                (x, barY),
                v / 100.0,
                barH,
                facecolor=T.hexc(T.LAYER_COLOUR[k]),
                edgecolor="white",
                linewidth=1.2,
            )
        )
        if v >= 7:
            ax.text(
                x + v / 200.0,
                barY + barH / 2,
                "%s\n%.0f%%" % (k, v),
                ha="center",
                va="center",
                fontsize=7.6,
                fontweight="bold",
                color="white",
                linespacing=1.2,
            )
        x += v / 100.0
    for i, (k, v) in enumerate(zip(keys, vals)):
        yy = 0.52 - i * 0.235
        ax.add_patch(
            Rectangle(
                (0.0, yy - 0.055),
                0.018,
                0.11,
                facecolor=T.hexc(T.LAYER_COLOUR[k]),
                edgecolor="none",
            )
        )
        ax.text(
            0.032,
            yy,
            "%s  %s" % (k, T.LAYER_NAME[k]),
            fontsize=7.8,
            fontweight="bold",
            color=T.hexc(T.NAVY),
            va="center",
        )
        ax.text(
            1.0,
            yy,
            "%.0f%%" % v,
            fontsize=7.8,
            ha="right",
            va="center",
            color=T.hexc(T.INK_SOFT),
        )
        comp = _clip(
            " · ".join(alloc[k].get("parts", [])[:2]) or alloc[k].get("component", ""),
            96,
        )
        if comp:
            ax.text(
                0.032, yy - 0.105, comp, fontsize=7.1, color=T.hexc(T.GREY), va="center"
            )
    ax.set_xlim(0, 1)
    ax.set_ylim(0.52 - 0.235 * len(keys) - 0.10, 1.02)
    _titleblock(ax, title, subtitle)
    return _save(fig, path)


# ====================================================== E5 integration surface
def integration_surface(
    path,
    uid,
    upstream,
    downstream,
    events,
    externals,
    accent,
    title,
    subtitle,
    up_label="Consumes from",
    down_label="Provides to",
):
    """Hub diagram: sources left, this module centre, consumers right."""

    def pick(rows, n=9):
        out = []
        for r in rows:
            lab = re.sub(r"\s+", " ", re.sub(r"[*`]", "", r[0])).strip()
            if lab:
                out.append(_clip(lab, 34))
        return out[:n], max(0, len(out) - n)

    L, lmore = pick(upstream)
    R, rmore = pick(downstream)
    if not L and not R:
        return None

    rows = max(len(L), len(R), 4)
    fig_h = max(2.6, 0.34 * rows + 1.5)
    fig, ax = plt.subplots(figsize=(W, fig_h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    top, bot = 82.0, 10.0

    def ys(n):
        if n == 0:
            return []
        if n == 1:
            return [(top + bot) / 2]
        step = (top - bot) / (n - 1)
        return [top - i * step for i in range(n)]

    hubx, huby, hubw, hubh = 41.0, 40.0, 18.0, 18.0
    _rounded(ax, hubx, huby, hubw, hubh, T.hexc(accent), r=1.2, z=4)
    ax.text(
        hubx + hubw / 2,
        huby + hubh * 0.62,
        uid,
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
        color="white",
        zorder=5,
    )
    ax.text(
        hubx + hubw / 2,
        huby + hubh * 0.28,
        "%d in · %d out" % (len(upstream), len(downstream)),
        ha="center",
        va="center",
        fontsize=7.1,
        color="white",
        zorder=5,
    )

    boxw, boxh = 30.0, 5.2
    for lab, y in zip(L, ys(len(L))):
        _rounded(
            ax,
            1.0,
            y - boxh / 2,
            boxw,
            boxh,
            T.hexc(T.BG_TINT),
            ec=T.hexc(T.RULE),
            lw=0.5,
            r=0.7,
        )
        ax.text(2.4, y, lab, ha="left", va="center", fontsize=7.1, color=T.hexc(T.INK))
        ax.add_patch(
            FancyArrowPatch(
                (31.4, y),
                (hubx - 0.6, huby + hubh / 2),
                connectionstyle="arc3,rad=0.10",
                arrowstyle="-|>",
                mutation_scale=6.5,
                linewidth=0.7,
                color=T.hexc(T.SKY),
                zorder=1,
            )
        )
    for lab, y in zip(R, ys(len(R))):
        _rounded(
            ax,
            69.0,
            y - boxh / 2,
            boxw,
            boxh,
            T.hexc(T.BG_PAPER),
            ec=T.hexc(T.RULE),
            lw=0.5,
            r=0.7,
        )
        ax.text(70.4, y, lab, ha="left", va="center", fontsize=7.1, color=T.hexc(T.INK))
        ax.add_patch(
            FancyArrowPatch(
                (hubx + hubw + 0.6, huby + hubh / 2),
                (68.6, y),
                connectionstyle="arc3,rad=-0.10",
                arrowstyle="-|>",
                mutation_scale=6.5,
                linewidth=0.7,
                color=T.hexc(accent),
                zorder=1,
            )
        )

    ax.text(
        1.0,
        89.0,
        up_label.upper(),
        fontsize=7.0,
        fontweight="bold",
        color=T.hexc(T.GREY),
    )
    ax.text(
        99.0,
        89.0,
        down_label.upper(),
        fontsize=7.0,
        fontweight="bold",
        color=T.hexc(T.GREY),
        ha="right",
    )
    if lmore:
        ax.text(
            1.0, bot - 5.0, "+%d more" % lmore, fontsize=7.0, color=T.hexc(T.GREY_LIGHT)
        )
    if rmore:
        ax.text(
            99.0,
            bot - 5.0,
            "+%d more" % rmore,
            fontsize=7.0,
            color=T.hexc(T.GREY_LIGHT),
            ha="right",
        )

    foot = "%d domain event%s · %d external integration%s" % (
        len(events),
        "" if len(events) == 1 else "s",
        len(externals),
        "" if len(externals) == 1 else "s",
    )
    ax.text(50, 2.0, foot, ha="center", fontsize=7.1, color=T.hexc(T.GREY))
    ax.text(
        0, 97, title, fontsize=9.5, fontweight="bold", color=T.hexc(T.NAVY), va="bottom"
    )
    ax.text(0, 96, subtitle, fontsize=7.4, color=T.hexc(T.GREY), va="top")
    return _save(fig, path)


# ============================================================ E6 rule classes
def rule_classes(path, mix, total, title, subtitle):
    order = [c for c in ["H", "A", "S", "C"] if mix.get(c, 0)]
    if not order:
        return None
    fig, ax = plt.subplots(figsize=(W, 0.33 * len(order) + 1.15))
    vals = [mix[c] for c in order]
    y = np.arange(len(order))[::-1]
    ax.barh(
        y, vals, height=0.52, color=[T.hexc(T.RULE_CLASS[c]) for c in order], zorder=3
    )
    ax.set_yticks(y)
    ax.set_yticklabels(
        ["%s — %s" % (c, T.RULE_CLASS_NAME[c]) for c in order],
        fontsize=8.0,
        color=T.hexc(T.INK),
    )
    ax.set_xlim(0, max(vals) * 1.22)
    ax.set_xticks([])
    _bare(ax)
    for yy, v in zip(y, vals):
        ax.text(
            v + max(vals) * 0.02,
            yy,
            "%d  (%.0f%%)" % (v, 100.0 * v / total),
            va="center",
            fontsize=8.0,
            fontweight="bold",
            color=T.hexc(T.NAVY),
        )
    _titleblock(ax, title, subtitle)
    return _save(fig, path)


# ============================================================= E7 state model
# A state name is an upper-case word, optionally joined to further upper-case
# words by a SINGLE separator. Two or more spaces mean two different states —
# which is exactly how the house ASCII diagrams lay them out.
STATE_TOKEN = re.compile(r"[A-Z][A-Z0-9]*(?:[ _/'&-][A-Z0-9][A-Z0-9]*)*")
_NOISE = {
    "RULE",
    "NOTE",
    "IF",
    "OR",
    "AND",
    "THEN",
    "ELSE",
    "M",
    "L",
    "SLA",
    "WHERE",
    "NB",
    "N/A",
    "TO",
    "FROM",
    "VIA",
    "ON",
    "BY",
    "AT",
    "NOT",
    "ALL",
    "ANY",
    "NEW",
    "NO",
    "NB.",
    "SEE",
    "PER",
    "NOTE:",
    "NB:",
}


def _tokens(fragment):
    """State-name candidates inside one fragment of ASCII art."""
    frag = re.sub(r"\([^)]*\)", "   ", fragment)  # drop parentheticals
    frag = re.sub(r"-{1,}>|=+>|<-{1,}|<=+", "   ", frag)
    frag = re.sub(r"[|+^*]", "   ", frag)
    frag = re.sub(r"\bv\b", "   ", frag)
    frag = re.sub(r"[<>:,.]", "   ", frag)
    frag = re.sub(r"-{2,}", "   ", frag)
    out = []
    for m in STATE_TOKEN.findall(frag):
        t = m.strip(" -_/&'")
        if len(t) < 3 or t in _NOISE:
            continue
        if re.fullmatch(r"[A-Z]{1,2}\d*", t):
            continue
        if len(t) > 30:
            t = t[:30].rstrip()
        out.append(t)
    return out


def parse_state_edges(lines):
    """Extract 'A --> B' style edges from the house ASCII state machines."""
    edges, states = [], []
    for line in lines:
        if not re.search(r"-{1,}>|=+>", line):
            continue
        parts = re.split(r"-{1,}>|=+>", line)
        toks = []
        for i, part in enumerate(parts):
            cand = _tokens(part)
            if not cand:
                toks.append(None)
            elif i == 0:
                toks.append(cand[-1])
            else:
                toks.append(cand[0])
        for a, b in zip(toks, toks[1:]):
            if a and b and a != b:
                edges.append((a, b))
    for a, b in edges:
        for s in (a, b):
            if s not in states:
                states.append(s)
    return states, edges


_BOX_EDGE = "│|┃┤├╡╞╢╟║"
BOXED = re.compile(
    r"[%s]\s*([A-Z][A-Z0-9][A-Z0-9 /&'’\-\.]{0,28}?)\s*[%s]" % (_BOX_EDGE, _BOX_EDGE)
)
TERMINALS = re.compile(
    r"terminal(?:\s+\w+)*\s*[:\-—]\s*(.+)$|exceptions?\s*[:\-—]\s*(.+)$", re.I
)


def parse_box_chain(lines):
    """Principal path from a box-drawing flow diagram.

    The house diagrams draw the main sequence as a vertical column of boxes
    joined by ▼, with side branches drawn unboxed. Reading the boxed labels
    in document order therefore recovers the principal path exactly, and
    leaves the exception branches out of the simplified rendering — which
    is where they belong, because the verbatim diagram sits beside it.
    """
    chain, terminals = [], []
    for line in lines:
        for m in BOXED.finditer(line):
            t = re.sub(r"\s{2,}", " ", m.group(1)).strip(" -.")
            if len(t) < 2 or t in _NOISE:
                continue
            if chain and chain[-1] == t:
                continue
            chain.append(t)
        mt = TERMINALS.search(line)
        if mt:
            tail = mt.group(1) or mt.group(2) or ""
            for piece in re.split(r"[·,]| and ", tail):
                p = piece.strip(" .·—-")
                if p and p.isupper() and 3 <= len(p) <= 30:
                    terminals.append(p)
    # de-duplicate while preserving order
    seen, out = set(), []
    for s in chain:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out, terminals


def all_states(lines):
    """Every state-looking token in declaration order (no edges implied)."""
    seen = []
    for line in lines:
        for t in _tokens(line):
            if t not in seen:
                seen.append(t)
    return seen


def state_chain(path, models, accent, title, subtitle, max_states=16):
    """Serpentine rendering of the principal path through a box diagram."""
    chain, terminals, name = [], [], ""
    for m in models:
        c, t = parse_box_chain(m["lines"])
        if len(c) >= 3:
            chain, terminals, name = c[:max_states], t, m["title"]
            break
    if not chain:
        return None

    per = 4 if len(chain) <= 8 else (5 if len(chain) <= 15 else 6)
    rows = int(math.ceil(len(chain) / float(per)))
    colw = 100.0 / per
    bw = colw - 4.0
    bh, gap = 10.0, 7.0
    head = 12.0
    termh = 8.0 if terminals else 0.0
    total = rows * bh + (rows - 1) * gap + head + termh + 3.0

    fig, ax = plt.subplots(figsize=(W, max(1.5, total / 100.0 * (W * 0.64) + 0.34)))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, total)
    ax.axis("off")

    top = total - head
    pos = []
    for i, s in enumerate(chain):
        r = i // per
        c = i % per
        if r % 2 == 1:  # serpentine: reverse odd rows
            c = per - 1 - c
        x = c * colw + (colw - bw) / 2.0
        y = top - (r + 1) * bh - r * gap
        pos.append((x, y))

    for i in range(len(chain) - 1):
        (x0, y0), (x1, y1) = pos[i], pos[i + 1]
        same_row = abs(y0 - y1) < 0.1
        if same_row:
            a = (x0 + bw, y0 + bh / 2) if x1 > x0 else (x0, y0 + bh / 2)
            b = (x1, y1 + bh / 2) if x1 > x0 else (x1 + bw, y1 + bh / 2)
            ax.add_patch(
                FancyArrowPatch(
                    a,
                    b,
                    arrowstyle="-|>",
                    mutation_scale=7,
                    linewidth=0.9,
                    color=T.hexc(T.GREY_LIGHT),
                    zorder=1,
                )
            )
        else:
            ax.add_patch(
                FancyArrowPatch(
                    (x0 + bw / 2, y0),
                    (x1 + bw / 2, y1 + bh),
                    arrowstyle="-|>",
                    mutation_scale=7,
                    connectionstyle="arc3,rad=0.0",
                    linewidth=0.9,
                    color=T.hexc(T.GREY_LIGHT),
                    zorder=1,
                )
            )

    for i, (s, (x, y)) in enumerate(zip(chain, pos)):
        first, last = (i == 0), (i == len(chain) - 1)
        fc = (
            T.hexc(accent) if first else (T.hexc(T.NAVY) if last else T.hexc(T.BG_TINT))
        )
        tc = "white" if (first or last) else T.hexc(T.INK)
        _rounded(ax, x, y, bw, bh, fc, ec=T.hexc(T.RULE), lw=0.6, r=0.9, z=3)
        ax.text(
            x + bw / 2,
            y + bh / 2,
            _wrap(_case(s), 15),
            ha="center",
            va="center",
            fontsize=7.1,
            fontweight="bold",
            color=tc,
            zorder=4,
            linespacing=1.18,
        )

    if terminals:
        ax.text(
            0,
            2.0,
            "TERMINAL EXCEPTIONS   " + "   ·   ".join(_case(t) for t in terminals[:6]),
            fontsize=7.0,
            color=T.hexc(T.RED),
            va="bottom",
        )

    ax.text(
        0,
        total - 3.0,
        title,
        fontsize=9.5,
        fontweight="bold",
        color=T.hexc(T.NAVY),
        va="bottom",
    )
    ax.text(
        0,
        total - 3.6,
        "%s — %s" % (name, subtitle),
        fontsize=7.4,
        color=T.hexc(T.GREY),
        va="top",
    )
    return _save(fig, path)


def state_inventory(path, models, accent, title, subtitle, max_states=18):
    """Chip grid of declared states where the arrows cannot be parsed safely.

    Deliberately draws no arrows: the source diagram is reproduced verbatim
    in the accompanying panel, and inventing transitions would misstate it.
    """
    chips, name = [], ""
    for m in models:
        st = all_states(m["lines"])
        if len(st) >= 3:
            chips, name = st[:max_states], m["title"]
            break
    if not chips:
        return None
    cols = 4
    rows = int(math.ceil(len(chips) / cols))
    fig, ax = plt.subplots(figsize=(W, 0.52 * rows + 1.15))
    ax.set_xlim(0, cols)
    ax.set_ylim(-rows, 0.95)
    ax.axis("off")
    for i, s in enumerate(chips):
        r, c = divmod(i, cols)
        x, y = c + 0.035, -(r + 1) + 0.10
        _rounded(
            ax,
            x,
            y,
            1 - 0.07,
            0.80,
            T.hexc(T.BG_TINT),
            ec=T.hexc(T.RULE),
            lw=0.5,
            r=0.05,
        )
        ax.add_patch(
            Rectangle(
                (x, y),
                0.030,
                0.80,
                facecolor=T.hexc(accent),
                edgecolor="none",
                zorder=3,
            )
        )
        ax.text(
            x + 0.10,
            y + 0.40,
            _wrap(_case(s), 24),
            fontsize=7.1,
            va="center",
            ha="left",
            color=T.hexc(T.INK),
            linespacing=1.2,
        )
    ax.text(
        0,
        0.72,
        title,
        fontsize=9.5,
        fontweight="bold",
        color=T.hexc(T.NAVY),
        va="bottom",
    )
    ax.text(
        0,
        0.66,
        "%s — %s" % (name, subtitle),
        fontsize=7.4,
        color=T.hexc(T.GREY),
        va="top",
    )
    return _save(fig, path)


def state_flow(path, models, accent, title, subtitle, max_states=14):
    """Layered left-to-right flow for the first parseable state machine."""
    best = None
    for m in models:
        states, edges = parse_state_edges(m["lines"])
        if len(states) >= 3 and len(edges) >= 2 and len(states) <= max_states:
            best = (m["title"], states, edges)
            break
    if not best:
        return None
    name, states, edges = best

    # longest-path layering
    succ = {s: [] for s in states}
    indeg = {s: 0 for s in states}
    for a, b in set(edges):
        succ[a].append(b)
        indeg[b] += 1
    layer = {s: 0 for s in states}
    for _ in range(len(states)):
        changed = False
        for a, b in set(edges):
            if layer[b] < layer[a] + 1:
                layer[b] = layer[a] + 1
                changed = True
        if not changed:
            break
    cols = OrderedDict()
    for s in states:
        cols.setdefault(min(layer[s], 6), []).append(s)

    ncol = max(cols) + 1
    nrow = max(len(v) for v in cols.values())

    # Compact geometry: rows are packed at a fixed pitch rather than spread
    # across the frame, so a two-state column does not leave half a page blank.
    colw = 100.0 / ncol
    bw = min(21.0, colw - 3.2)
    bh, gap = 9.0, 4.2
    band = nrow * bh + (nrow - 1) * gap
    head = 13.0
    total = band + head + 3.0
    fig_h = max(1.55, total / 100.0 * (W * 0.62) + 0.30)
    fig, ax = plt.subplots(figsize=(W, fig_h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, total)
    ax.axis("off")

    top = total - head
    pos = {}
    for c in sorted(cols):
        items = cols[c]
        xs = c * colw + (colw - bw) / 2.0
        offset = (band - (len(items) * bh + (len(items) - 1) * gap)) / 2.0
        for i, s in enumerate(items):
            yy = top - offset - (i + 1) * bh - i * gap
            pos[s] = (xs, yy)
    for a, b in set(edges):
        if a not in pos or b not in pos:
            continue
        ax1, ay1 = pos[a]
        bx1, by1 = pos[b]
        start = (ax1 + bw, ay1 + bh / 2) if bx1 > ax1 else (ax1 + bw / 2, ay1)
        end = (bx1, by1 + bh / 2) if bx1 > ax1 else (bx1 + bw / 2, by1 + bh)
        ax.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=7,
                connectionstyle="arc3,rad=0.08",
                linewidth=0.8,
                color=T.hexc(T.GREY_LIGHT),
                zorder=1,
            )
        )
    for s, (x, y) in pos.items():
        terminal = not succ.get(s)
        initial = indeg.get(s, 0) == 0
        fc = (
            T.hexc(accent)
            if initial
            else (T.hexc(T.NAVY) if terminal else T.hexc(T.BG_TINT))
        )
        tc = "white" if (initial or terminal) else T.hexc(T.INK)
        _rounded(ax, x, y, bw, bh, fc, ec=T.hexc(T.RULE), lw=0.6, r=0.9, z=3)
        ax.text(
            x + bw / 2,
            y + bh / 2,
            _wrap(_case(s), 15),
            ha="center",
            va="center",
            fontsize=7.0,
            fontweight="bold",
            color=tc,
            zorder=4,
            linespacing=1.2,
        )
    ax.text(
        0,
        total - 3.0,
        title,
        fontsize=9.5,
        fontweight="bold",
        color=T.hexc(T.NAVY),
        va="bottom",
    )
    ax.text(
        0,
        total - 3.6,
        "%s — %s" % (name, subtitle),
        fontsize=7.4,
        color=T.hexc(T.GREY),
        va="top",
    )
    return _save(fig, path)


# ============================================================ E8 data ownership
def data_ownership(
    path,
    owned,
    referenced,
    accent,
    title,
    subtitle,
    owned_label="Entities this module owns",
):
    n_o, n_r = len(owned), len(referenced)
    if n_o + n_r == 0:
        return None
    owners = Counter()
    for r in referenced:
        for m in re.findall(r"\bM\d{2}\b", " ".join(r[1:2]) if len(r) > 1 else ""):
            owners[m] += 1
    top = owners.most_common(10)

    fig_h = max(2.3, 0.30 * max(len(top), 6) + 1.4)
    fig, ax = plt.subplots(figsize=(W, fig_h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    _rounded(ax, 0, 62, 46, 26, T.hexc(accent), r=1.0)
    ax.text(3, 80, str(n_o), fontsize=22, fontweight="bold", color="white", va="center")
    ax.text(3, 69, owned_label.upper(), fontsize=7.0, color="white", va="center")
    _rounded(ax, 54, 62, 46, 26, T.hexc(T.BG_TINT), ec=T.hexc(T.RULE), lw=0.6, r=1.0)
    ax.text(
        57,
        80,
        str(n_r),
        fontsize=22,
        fontweight="bold",
        color=T.hexc(T.NAVY),
        va="center",
    )
    ax.text(
        57,
        69,
        "ENTITIES IT READS FROM OTHER MODULES",
        fontsize=7.0,
        color=T.hexc(T.GREY),
        va="center",
    )

    if top:
        ax.text(
            0,
            55,
            "WHERE THE REFERENCED DATA IS OWNED",
            fontsize=7.0,
            fontweight="bold",
            color=T.hexc(T.GREY),
        )
        mx = max(v for _, v in top)
        for i, (m, v) in enumerate(top):
            yy = 47 - i * (44.0 / max(len(top), 1))
            ax.text(
                0,
                yy,
                m,
                fontsize=7.4,
                fontweight="bold",
                color=T.hexc(T.NAVY),
                va="center",
            )
            ax.add_patch(
                Rectangle(
                    (9, yy - 1.6),
                    74.0 * v / mx,
                    3.2,
                    facecolor=T.hexc(T.STEEL),
                    edgecolor="none",
                )
            )
            ax.text(
                9 + 74.0 * v / mx + 1.4,
                yy,
                str(v),
                fontsize=7.0,
                va="center",
                color=T.hexc(T.INK_SOFT),
            )
    ax.text(
        0, 97, title, fontsize=9.5, fontweight="bold", color=T.hexc(T.NAVY), va="bottom"
    )
    ax.text(0, 96, subtitle, fontsize=7.4, color=T.hexc(T.GREY), va="top")
    return _save(fig, path)


# ============================================================== E9 role matrix
PERM_ORDER = ["C", "R", "U", "D", "A"]
PERM_NAME = {"C": "Create", "R": "Read", "U": "Update", "D": "Delete", "A": "Approve"}


def role_matrix(path, roles, accent, title, subtitle, max_roles=16):
    roles = [r for r in roles if r.get("name")][:max_roles]
    if not roles:
        return None
    fig_h = max(1.9, 0.265 * len(roles) + 1.35)
    fig, ax = plt.subplots(figsize=(W, fig_h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    x0, cellw = 47.0, 6.2
    top = 84.0
    rowh = 78.0 / max(len(roles), 1)
    rowh = min(rowh, 5.0)

    for j, p in enumerate(PERM_ORDER):
        ax.text(
            x0 + j * cellw + cellw / 2,
            top + 3.0,
            p,
            ha="center",
            fontsize=7.0,
            fontweight="bold",
            color=T.hexc(T.GREY),
        )
    ax.text(
        x0 + 5 * cellw + 3.0,
        top + 3.0,
        "SCOPE",
        ha="left",
        fontsize=7.0,
        fontweight="bold",
        color=T.hexc(T.GREY),
    )

    for i, r in enumerate(roles):
        y = top - (i + 1) * rowh
        if i % 2 == 0:
            ax.add_patch(
                Rectangle(
                    (0, y),
                    100,
                    rowh,
                    facecolor=T.hexc(T.BG_PAPER),
                    edgecolor="none",
                    zorder=0,
                )
            )
        label = ("%s %s" % (r.get("id", ""), r["name"])).strip()
        ax.text(
            0.5,
            y + rowh / 2,
            _clip(label, 42),
            fontsize=7.1,
            va="center",
            color=T.hexc(T.INK),
            zorder=2,
        )
        for j, p in enumerate(PERM_ORDER):
            on = p in r["perms"]
            cx = x0 + j * cellw + cellw / 2
            ax.add_patch(
                Circle(
                    (cx, y + rowh / 2),
                    min(rowh, cellw) * 0.30,
                    facecolor=T.hexc(accent) if on else T.hexc("EDF1F6"),
                    edgecolor="none",
                    zorder=2,
                )
            )
        ax.text(
            x0 + 5 * cellw + 3.0,
            y + rowh / 2,
            _clip(r.get("scope", ""), 27),
            fontsize=7.0,
            va="center",
            color=T.hexc(T.GREY),
            zorder=2,
        )

    ax.text(
        0, 97, title, fontsize=9.5, fontweight="bold", color=T.hexc(T.NAVY), va="bottom"
    )
    ax.text(
        0,
        96,
        subtitle
        + "   ·   "
        + " · ".join("%s %s" % (k, PERM_NAME[k]) for k in PERM_ORDER),
        fontsize=7.0,
        color=T.hexc(T.GREY),
        va="top",
    )
    return _save(fig, path)


# ============================================================ E10 wave position
WAVE_MONTHS = OrderedDict(
    [
        ("W1", (1, 4)),
        ("W2", (5, 8)),
        ("W3", (9, 13)),
        ("W4", (14, 18)),
        ("W5", (19, 22)),
        ("W6", (23, 26)),
        ("W7", (27, 30)),
        ("W8", (31, 34)),
        ("W9", (35, 36)),
    ]
)


def wave_position(path, waves, accent, title, subtitle):
    fig, ax = plt.subplots(figsize=(W, 1.72))
    ax.set_xlim(0, 37)
    ax.set_ylim(0, 10)
    ax.axis("off")
    for i, (w, (a, b)) in enumerate(WAVE_MONTHS.items()):
        on = w in waves
        fc = T.hexc(accent) if on else T.hexc(T.BG_TINT)
        _rounded(
            ax,
            a - 1 + 0.12,
            3.4,
            (b - a + 1) - 0.24,
            3.0,
            fc,
            ec=T.hexc(T.RULE if not on else accent),
            lw=0.6,
            r=0.12,
        )
        ax.text(
            (a - 1 + b) / 2.0,
            4.9,
            w,
            ha="center",
            va="center",
            fontsize=8.0,
            fontweight="bold",
            color="white" if on else T.hexc(T.GREY),
        )
        ax.text(
            (a - 1 + b) / 2.0,
            2.6,
            "M%d–%d" % (a, b),
            ha="center",
            va="center",
            fontsize=7.0,
            color=T.hexc(T.INK_SOFT if on else T.GREY_LIGHT),
        )
    ax.annotate(
        "",
        xy=(37, 1.5),
        xytext=(0, 1.5),
        arrowprops=dict(arrowstyle="-|>", color=T.hexc(T.RULE), lw=0.8),
    )
    ax.text(0, 0.5, "PROGRAMME MONTH 1", fontsize=7.0, color=T.hexc(T.GREY))
    ax.text(37, 0.5, "MONTH 36", fontsize=7.0, color=T.hexc(T.GREY), ha="right")
    ax.text(
        0,
        9.4,
        title,
        fontsize=9.5,
        fontweight="bold",
        color=T.hexc(T.NAVY),
        va="bottom",
    )
    ax.text(0, 8.9, subtitle, fontsize=7.4, color=T.hexc(T.GREY), va="top")
    return _save(fig, path)


# ========================================================= E11 peer comparison
def peer_comparison(
    path,
    peers,
    this_uid,
    accent,
    title,
    subtitle,
    metric="reqs",
    metric_label="Functional requirements",
):
    if len(peers) < 2:
        return None
    peers = sorted(peers, key=lambda p: p[metric], reverse=True)
    labels = ["%s %s" % (p["uid"], _clip(p["name"], 34)) for p in peers]
    vals = [p[metric] for p in peers]
    cols = [
        T.hexc(accent) if p["uid"] == this_uid else T.hexc(T.SKY_PALE) for p in peers
    ]
    fig, ax = plt.subplots(figsize=(W, max(1.7, 0.30 * len(peers) + 1.15)))
    y = np.arange(len(peers))[::-1]
    ax.barh(y, vals, height=0.62, color=cols, zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.6, color=T.hexc(T.INK))
    for tick, p in zip(ax.get_yticklabels(), peers):
        if p["uid"] == this_uid:
            tick.set_fontweight("bold")
            tick.set_color(T.hexc(T.NAVY))
    ax.set_xlim(0, max(vals) * 1.14)
    ax.set_xticks([])
    _bare(ax)
    for yy, v, p in zip(y, vals, peers):
        ax.text(
            v + max(vals) * 0.016,
            yy,
            str(v),
            va="center",
            fontsize=7.6,
            fontweight="bold" if p["uid"] == this_uid else "normal",
            color=T.hexc(T.NAVY if p["uid"] == this_uid else T.GREY),
        )
    _titleblock(ax, title, subtitle)
    return _save(fig, path)


# =============================================================== E12 KPI board
NUM = re.compile(r"(-?\d+(?:[.,]\d+)?)\s*(%|BDT|hrs?|days?|min|×|x)?", re.I)


def kpi_board(path, kpi_rows, kpi_header, accent, title, subtitle, max_n=8):
    """Baseline → target slope chart for KPIs whose figures are numeric."""
    if not kpi_rows:
        return None
    hdr = [re.sub(r"[*`]", "", h).strip().lower() for h in kpi_header]

    def idx(*names, default=None):
        for i, h in enumerate(hdr):
            if any(n in h for n in names):
                return i
        return default

    i_metric = idx("metric", "kpi", default=1 if len(hdr) > 1 else 0)
    i_base = idx("baseline", "today", "current")
    tgt_cols = [i for i, h in enumerate(hdr) if "target" in h]
    if i_base is None or not tgt_cols:
        return None
    i_tgt = tgt_cols[-1]

    items = []
    for r in kpi_rows:
        if max(i_metric, i_base, i_tgt) >= len(r):
            continue
        name = re.sub(r"[*`]", "", r[i_metric]).strip()
        b = NUM.search(re.sub(r"[*`,]", "", r[i_base]))
        t = NUM.search(re.sub(r"[*`,]", "", r[i_tgt]))
        if not name or not b or not t:
            continue
        try:
            bv, tv = float(b.group(1)), float(t.group(1))
        except ValueError:
            continue
        unit = (b.group(2) or t.group(2) or "").strip()
        items.append((name, bv, tv, unit))
    items = items[:max_n]
    if len(items) < 2:
        return None

    fig, ax = plt.subplots(figsize=(W, max(2.1, 0.42 * len(items) + 1.2)))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    top, rowh = 84.0, min(9.0, 78.0 / len(items))
    for i, (name, bv, tv, unit) in enumerate(items):
        y = top - i * rowh
        ax.text(0, y, _clip(name, 52), fontsize=7.4, va="center", color=T.hexc(T.INK))
        x0, x1 = 55.0, 88.0
        ax.plot([x0, x1], [y, y], color=T.hexc(T.RULE), lw=0.7, zorder=1)
        ax.scatter([x0], [y], s=26, color=T.hexc(T.GREY_LIGHT), zorder=3)
        ax.scatter([x1], [y], s=34, color=T.hexc(accent), zorder=3)
        fmt = lambda v: ("%g" % v) + (
            unit if unit and unit != "%" else ("%" if unit == "%" else "")
        )
        ax.text(
            x0 - 1.5,
            y,
            fmt(bv),
            fontsize=7.1,
            ha="right",
            va="center",
            color=T.hexc(T.GREY),
        )
        ax.text(
            x1 + 1.5,
            y,
            fmt(tv),
            fontsize=7.2,
            ha="left",
            va="center",
            fontweight="bold",
            color=T.hexc(T.NAVY),
        )
    ax.text(
        55,
        top + rowh * 0.75,
        "BASELINE",
        fontsize=7.0,
        color=T.hexc(T.GREY),
        ha="center",
    )
    ax.text(
        88, top + rowh * 0.75, "TARGET", fontsize=7.0, color=T.hexc(T.GREY), ha="center"
    )
    ax.text(
        0, 97, title, fontsize=9.5, fontweight="bold", color=T.hexc(T.NAVY), va="bottom"
    )
    ax.text(0, 96, subtitle, fontsize=7.4, color=T.hexc(T.GREY), va="top")
    return _save(fig, path)


# ========================================================== E13 boundary map
def boundary_map(path, n_in, out_rows, shared_rows, accent, title, subtitle):
    if not out_rows and not n_in:
        return None
    owners = Counter()
    for r in out_rows:
        joined = " ".join(r[1:2]) if len(r) > 1 else " ".join(r)
        for m in re.findall(r"\bM\d{2}\b", joined):
            owners[m] += 1
    top = owners.most_common(12)
    fig, ax = plt.subplots(figsize=(W, max(2.0, 0.28 * max(len(top), 4) + 1.5)))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    for i, (val, lab, col) in enumerate(
        [
            (n_in, "CAPABILITIES IN SCOPE", accent),
            (len(out_rows), "EXPLICITLY OUT OF SCOPE", T.GREY),
            (len(shared_rows), "SHARED CONCEPTS", T.STEEL),
        ]
    ):
        x = i * 34.0
        _rounded(ax, x, 66, 31, 24, T.hexc(col), r=0.9)
        ax.text(
            x + 2.5,
            82,
            str(val),
            fontsize=19,
            fontweight="bold",
            color="white",
            va="center",
        )
        ax.text(x + 2.5, 71.5, lab, fontsize=7.0, color="white", va="center")

    if top:
        ax.text(
            0,
            59,
            "WHO OWNS WHAT THIS MODULE DELIBERATELY DOES NOT",
            fontsize=7.0,
            fontweight="bold",
            color=T.hexc(T.GREY),
        )
        mx = max(v for _, v in top)
        for i, (m, v) in enumerate(top):
            yy = 51 - i * (48.0 / max(len(top), 1))
            ax.text(
                0,
                yy,
                m,
                fontsize=7.2,
                fontweight="bold",
                color=T.hexc(T.NAVY),
                va="center",
            )
            ax.add_patch(
                Rectangle(
                    (9, yy - 1.5),
                    76.0 * v / mx,
                    3.0,
                    facecolor=T.hexc(T.GREY_LIGHT),
                    edgecolor="none",
                )
            )
            ax.text(
                9 + 76.0 * v / mx + 1.4,
                yy,
                str(v),
                fontsize=7.1,
                va="center",
                color=T.hexc(T.INK_SOFT),
            )
    ax.text(
        0, 97, title, fontsize=9.5, fontweight="bold", color=T.hexc(T.NAVY), va="bottom"
    )
    ax.text(0, 96, subtitle, fontsize=7.4, color=T.hexc(T.GREY), va="top")
    return _save(fig, path)


# ========================================================= E14 automation ring
def automation_profile(path, automations, header, accent, title, subtitle):
    if not automations:
        return None
    hdr = [re.sub(r"[*`]", "", h).strip().lower() for h in header]
    i_fail = next((i for i, h in enumerate(hdr) if "failure" in h), None)
    buckets = Counter()
    for r in automations:
        txt = (
            r[i_fail] if i_fail is not None and i_fail < len(r) else " ".join(r)
        ).lower()
        if "retry" in txt or "re-try" in txt:
            k = "Retry with back-off"
        elif "queue" in txt or "defer" in txt or "hold" in txt:
            k = "Queue and defer"
        elif "alert" in txt or "escalat" in txt or "notify" in txt or "raise" in txt:
            k = "Alert or escalate to a human"
        elif "manual" in txt or "fall back" in txt or "fallback" in txt:
            k = "Fall back to manual"
        elif "block" in txt or "fail closed" in txt or "reject" in txt:
            k = "Fail closed and block"
        elif "log" in txt or "record" in txt or "no action" in txt or "silent" in txt:
            k = "Log only"
        else:
            k = "Other declared behaviour"
        buckets[k] += 1
    items = buckets.most_common()
    fig, ax = plt.subplots(figsize=(W, max(1.8, 0.36 * len(items) + 1.2)))
    y = np.arange(len(items))[::-1]
    vals = [v for _, v in items]
    ax.barh(
        y,
        vals,
        height=0.56,
        color=[T.hexc(c) for c in (T.SERIES * 4)[: len(items)]],
        zorder=3,
    )
    ax.set_yticks(y)
    ax.set_yticklabels([k for k, _ in items], fontsize=7.8, color=T.hexc(T.INK))
    ax.set_xlim(0, max(vals) * 1.18)
    ax.set_xticks([])
    _bare(ax)
    for yy, v in zip(y, vals):
        ax.text(
            v + max(vals) * 0.02,
            yy,
            str(v),
            va="center",
            fontsize=7.8,
            fontweight="bold",
            color=T.hexc(T.NAVY),
        )
    _titleblock(ax, title, subtitle)
    return _save(fig, path)
