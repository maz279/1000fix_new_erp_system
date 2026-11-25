# -*- coding: utf-8 -*-
"""
bizexhibits — the visual language of the business-reader guide books.

The exhibits in `exhibits.py` describe a *specification*: requirement counts,
delivery layers, state machines. The exhibits here describe a *business*: what
changes for a person, what a job looks like as it travels through the company,
what the module lets somebody do on a Tuesday morning at a branch counter.

Same palette, same geometry, same 300 dpi print resolution. Different question.

House rules
  · one idea per exhibit, and the title states it as a sentence a manager
    would say out loud
  · label directly on the shape; a legend is a failure to design
  · colour carries meaning or it is not used
  · nothing is invented — every figure traces to the module specification

Geometry note. The vertical axis of every exhibit is measured in **inches**,
not in an abstract 0–100 space. Text is drawn at a fixed point size, so a box
whose height is a fraction of the figure will not stay in proportion to the
words inside it. Working in inches means a four-line paragraph reserves exactly
four lines of space, and the exhibit closes up to fit its content instead of
floating in a pool of white. The horizontal axis stays as a percentage of the
text column, which is what layout actually wants.
"""

import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (
    FancyBboxPatch,
    FancyArrowPatch,
    Wedge,
    Polygon,
    Rectangle,
)

import theme as T
from exhibits import _wrap, _clip, _save, FAMILY, W

__all__ = [
    "headline",
    "today_tomorrow",
    "journey_ribbon",
    "capability_map",
    "benefit_stack",
    "swimlane",
    "fan_in",
    "auto_ring",
    "who_can",
    "target_dials",
    "gate_ladder",
    "scale_bars",
    "boundary_panels",
    "volume_profile",
    "compare_columns",
]

C = T.hexc

# ------------------------------------------------------------- measurement
PT = 1.0 / 72.0  # one point, in inches
EM = 0.478  # Calibri mean advance, in em, measured
LH = 1.20  # house line spacing inside exhibits


def _chars(width_pct, fontsize):
    """How many characters of `fontsize` fit across `width_pct` of the column."""
    return max(int((width_pct / 100.0 * W) / (fontsize * EM * PT)), 6)


def _lines(text, width_pct, fontsize, max_lines=None):
    """Wrapped lines for a block of text at a given width."""
    return _wrap(text, _chars(width_pct, fontsize), max_lines=max_lines).split("\n")


def _text_h(nlines, fontsize):
    """Height in inches of `nlines` lines set at `fontsize`."""
    return nlines * fontsize * LH * PT


# --------------------------------------------------------------- primitives
def _canvas(body_h, title, sub, accent, pad_bottom=0.0):
    """Figure sized to the text column. Returns (fig, ax, top_y_in_inches).

    `body_h` is the height in inches the caller needs below the title block.
    The y axis runs 0 (bottom) to the full figure height (top), in inches.
    """
    head = 0.0
    if title:
        head += _text_h(1, 10.2) + 0.055
        if sub:
            head += _text_h(1, 7.8) + 0.040
        head += 0.085  # the accent rule and its air
    total = head + body_h + pad_bottom
    fig = plt.figure(figsize=(W, total))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, total)
    ax.axis("off")

    y = total
    if title:
        y -= _text_h(1, 10.2)
        ax.text(
            0,
            y,
            title,
            ha="left",
            va="baseline",
            fontsize=10.2,
            fontweight="bold",
            color=C(T.NAVY),
        )
        y -= 0.055
        if sub:
            y -= _text_h(1, 7.8)
            ax.text(0, y, sub, ha="left", va="baseline", fontsize=7.8, color=C(T.GREY))
            y -= 0.040
        y -= 0.050
        ax.plot([0, 100], [y, y], lw=0.9, color=C(accent), solid_capstyle="butt")
        y -= 0.035
    return fig, ax, y


def _round(ax, x, y, w, h, fc, r=0.035, z=1, ec="none", lw=0.0):
    """Rounded rectangle in mixed units (x percent, y inches)."""
    p = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0,rounding_size=%f" % r,
        linewidth=lw,
        facecolor=fc,
        edgecolor=ec,
        zorder=z,
        mutation_aspect=(h / max(w, 0.001)) * 26.0,
    )
    ax.add_patch(p)
    return p


def _para(
    ax,
    x,
    y_top,
    text,
    width_pct,
    fontsize,
    colour,
    bold=False,
    max_lines=None,
    ha="left",
):
    """Draw wrapped text from a top edge. Returns the height consumed."""
    lines = _lines(text, width_pct, fontsize, max_lines)
    ax.text(
        x,
        y_top,
        "\n".join(lines),
        ha=ha,
        va="top",
        fontsize=fontsize,
        color=C(colour),
        fontweight="bold" if bold else "normal",
        linespacing=LH,
        family=FAMILY,
    )
    return _text_h(len(lines), fontsize)


def _tick(ax, x, y, h_in, colour, lw=1.2):
    """A drawn check mark — Calibri has no U+2713 glyph.

    `x` is a percentage of the column, `y` inches; `h_in` is the height of the
    mark, and its width is derived so it comes out square on the page.
    """
    w = h_in / W * 100.0
    ax.plot(
        [x, x + w * 0.40, x + w * 1.05],
        [y + h_in * 0.45, y, y + h_in],
        lw=lw,
        color=C(colour),
        solid_capstyle="round",
        solid_joinstyle="round",
        zorder=4,
    )


def _disc_tf(ax, cx, cy, r_pct, r_in):
    from matplotlib.transforms import Affine2D

    return Affine2D().scale(r_pct, r_in).translate(cx, cy) + ax.transData


def _disc(ax, cx, cy, r_pct, r_in, fc, ec="none", lw=0.0, z=4):
    from matplotlib.patches import Ellipse

    e = Ellipse(
        (cx, cy), r_pct * 2, r_in * 2, facecolor=fc, edgecolor=ec, lw=lw, zorder=z
    )
    ax.add_patch(e)
    return e


def _round_r(r_in):
    """Radii for a disc that renders circular: (percent of width, inches)."""
    return r_in / W * 100.0, r_in


def _fit_size(text, width_pct, fontsize, min_size=5.6):
    """Shrink the point size until the longest word fits the column.

    `_wrap` never breaks a word, so a single long word in a narrow lane will
    run past its box. Rather than truncate a word the reader needs, step the
    size down until it fits, and only then give up.
    """
    longest = max((len(w) for w in str(text).split()), default=1)
    fs = fontsize
    while fs > min_size and longest > _chars(width_pct, fs):
        fs -= 0.2
    return round(fs, 1)


# ============================================================ E1 headline
def headline(path, items, accent, title, subtitle, per_row=4):
    """Big-number tiles. `items` = [(value, label, note or None), ...]."""
    items = [i for i in items if i]
    if not items:
        return None
    per_row = min(per_row, len(items))
    rows = int(math.ceil(len(items) / float(per_row)))
    gap_x, gap_y = 1.8, 0.075
    tw = (100.0 - gap_x * (per_row - 1)) / per_row

    has_note = any(len(i) > 2 and i[2] for i in items)
    lab_lines = max(len(_lines(str(i[1]).upper(), tw - 5.5, 6.6, 2)) for i in items)
    th = (
        0.085
        + _text_h(1, 17.0)
        + 0.035
        + _text_h(lab_lines, 6.6)
        + (0.030 + _text_h(1, 6.4) if has_note else 0.0)
        + 0.075
    )

    fig, ax, top = _canvas(rows * th + (rows - 1) * gap_y, title, subtitle, accent)
    for i, it in enumerate(items):
        value, label = it[0], it[1]
        note = it[2] if len(it) > 2 else None
        r, c = divmod(i, per_row)
        x = c * (tw + gap_x)
        y = top - (r + 1) * th - r * gap_y

        _round(ax, x, y, tw, th, C(T.BG_TINT), z=1)
        ax.add_patch(
            Rectangle((x, y), 1.0, th, facecolor=C(accent), edgecolor="none", zorder=2)
        )
        v = str(value)
        fs = 17.0 if len(v) <= 5 else (14.0 if len(v) <= 8 else 11.5)
        yy = y + th - 0.085
        ax.text(
            x + 3.6,
            yy - _text_h(1, 17.0) * 0.80,
            v,
            ha="left",
            va="baseline",
            fontsize=fs,
            fontweight="bold",
            color=C(T.NAVY),
        )
        yy -= _text_h(1, 17.0) + 0.035
        yy -= _para(
            ax, x + 3.6, yy, str(label).upper(), tw - 5.5, 6.6, T.GREY, max_lines=2
        )
        if note:
            yy -= 0.030
            _para(ax, x + 3.6, yy, str(note), tw - 5.5, 6.4, accent, max_lines=1)
    return _save(fig, path)


# ======================================================= E2 today / tomorrow
def today_tomorrow(
    path,
    rows,
    accent,
    title,
    subtitle,
    head=("Who", "How it works today", "How it works once this is live"),
    max_rows=9,
):
    """Three-column before/after board. `rows` = [(role, today, after), ...]."""
    rows = [r for r in rows if r and len(r) >= 3][:max_rows]
    if not rows:
        return None
    wr, wt, wa = 17.0, 38.0, 42.0
    gap = 1.5
    xr, xt, xa = 0.0, wr + gap, wr + gap + wt + gap
    pad = 0.055
    gap_y = 0.055

    hs = []
    for role, today, after in rows:
        n = max(
            len(_lines(today, wt - 3.0, 7.0)),
            len(_lines(after, wa - 5.5, 7.0)),
            len(_lines(role, wr - 2.4, 7.2)),
        )
        hs.append(_text_h(n, 7.0) + pad * 2)

    head_h = _text_h(1, 6.8) + 0.075
    body = head_h + sum(hs) + gap_y * len(rows)
    fig, ax, top = _canvas(body, title, subtitle, accent)

    y = top - _text_h(1, 6.8)
    for x, lbl, col in (
        (xr, head[0], T.GREY),
        (xt, head[1], T.GREY),
        (xa, head[2], accent),
    ):
        ax.text(
            x + 1.6,
            y,
            lbl.upper(),
            ha="left",
            va="baseline",
            fontsize=6.8,
            fontweight="bold",
            color=C(col),
        )
    y -= 0.055
    ax.plot([0, 100], [y, y], lw=0.7, color=C(T.RULE))
    y -= 0.020

    for (role, today, after), h in zip(rows, hs):
        y -= h + gap_y
        ax.add_patch(
            Rectangle(
                (xr, y), wr, h, facecolor=C(T.BG_PAPER), edgecolor="none", zorder=1
            )
        )
        ax.add_patch(
            Rectangle(
                (xt, y), wt, h, facecolor=C(T.BG_PAPER), edgecolor="none", zorder=1
            )
        )
        _round(ax, xa, y, wa, h, C(T.BG_TINT), z=1)
        ax.add_patch(
            Rectangle((xa, y), 0.9, h, facecolor=C(accent), edgecolor="none", zorder=2)
        )
        _para(ax, xr + 1.6, y + h - pad, role, wr - 2.4, 7.2, T.NAVY, bold=True)
        _para(ax, xt + 1.6, y + h - pad, today, wt - 3.0, 7.0, T.GREY)
        _para(ax, xa + 3.0, y + h - pad, after, wa - 5.5, 7.0, T.INK)
    return _save(fig, path)


# ======================================================== E3 journey ribbon
def journey_ribbon(path, stages, accent, title, subtitle, per_row=5):
    """Chevron ribbon. `stages` = [(name, who, flag or None), ...]."""
    stages = [s for s in stages if s][:20]
    if not stages:
        return None
    per_row = min(per_row, len(stages))
    rows = int(math.ceil(len(stages) / float(per_row)))
    gap_x, gap_y = 1.4, 0.085
    cw = (100.0 - gap_x * (per_row - 1)) / per_row
    tip = min(2.4, cw * 0.15)
    inner = cw - tip * 2 - 2.0

    nm = max(len(_lines(s[0], inner, 7.4, 2)) for s in stages)
    ch = (
        0.060
        + _text_h(1, 6.4)
        + 0.020
        + _text_h(nm, 7.4)
        + 0.025
        + _text_h(1, 6.2)
        + 0.060
    )

    fig, ax, top = _canvas(rows * ch + (rows - 1) * gap_y, title, subtitle, accent)
    for i, st in enumerate(stages):
        name = st[0]
        who = st[1] if len(st) > 1 else None
        flag = st[2] if len(st) > 2 else None
        r, c = divmod(i, per_row)
        x = c * (cw + gap_x)
        y = top - (r + 1) * ch - r * gap_y

        first = i == 0
        shade = C(accent) if first else (C(T.BG_TINT) if i % 2 else C(T.BG_PAPER))
        pts = [
            (x, y),
            (x + cw - tip, y),
            (x + cw, y + ch / 2.0),
            (x + cw - tip, y + ch),
            (x, y + ch),
            (x + tip, y + ch / 2.0),
        ]
        ax.add_patch(
            Polygon(
                pts, closed=True, facecolor=shade, edgecolor=C(T.RULE), lw=0.5, zorder=1
            )
        )
        tx = x + tip + 1.0
        yy = y + ch - 0.060
        ax.text(
            tx,
            yy - _text_h(1, 6.4) * 0.78,
            str(i + 1).zfill(2),
            ha="left",
            va="baseline",
            fontsize=6.4,
            fontweight="bold",
            color=C(T.WHITE if first else accent),
        )
        yy -= _text_h(1, 6.4) + 0.020
        yy -= _para(
            ax,
            tx,
            yy,
            name,
            inner,
            7.4,
            T.WHITE if first else T.NAVY,
            bold=True,
            max_lines=nm,
        )
        if who:
            yy -= 0.025
            _para(
                ax,
                tx,
                yy,
                who,
                inner,
                6.2,
                T.SKY_PALE if first else T.GREY,
                max_lines=1,
            )
        if flag:
            ax.text(
                x + cw - tip - 0.6,
                y + ch - 0.055,
                str(flag),
                ha="right",
                va="top",
                fontsize=6.0,
                color=C(T.OCHRE),
                style="italic",
                fontweight="bold",
            )
    return _save(fig, path)


# ======================================================= E4 capability map
def capability_map(path, areas, accent, title, subtitle, per_row=None):
    """Feature areas as tiles. `areas` = [(name, count, description), ...]."""
    areas = [a for a in areas if a][:12]
    if not areas:
        return None
    n = len(areas)
    per_row = per_row or (2 if n <= 6 else 3)
    per_row = min(per_row, n)
    rows = int(math.ceil(n / float(per_row)))
    gap_x, gap_y = 1.8, 0.085
    tw = (100.0 - gap_x * (per_row - 1)) / per_row

    nn = max(len(_lines(a[0], tw - 16.0, 7.8, 2)) for a in areas)
    nd = max(
        len(_lines(a[2], tw - 6.0, 6.8, 3)) if len(a) > 2 and a[2] else 1 for a in areas
    )
    th = (
        0.030
        + 0.060
        + _text_h(nn, 7.8)
        + 0.045
        + _text_h(nd, 6.8)
        + 0.090
        + 0.030
        + 0.060
    )

    fig, ax, top = _canvas(rows * th + (rows - 1) * gap_y, title, subtitle, accent)
    mx = max(a[1] for a in areas) or 1
    for i, a in enumerate(areas):
        name, cnt = a[0], a[1]
        desc = a[2] if len(a) > 2 else None
        r, c = divmod(i, per_row)
        x = c * (tw + gap_x)
        y = top - (r + 1) * th - r * gap_y

        _round(ax, x, y, tw, th, C(T.BG_PAPER), z=1)
        ax.add_patch(
            Rectangle(
                (x, y + th - 0.030),
                tw,
                0.030,
                facecolor=C(accent),
                edgecolor="none",
                zorder=2,
            )
        )
        # count chip, top right
        chip_w = 7.4
        _round(
            ax,
            x + tw - chip_w - 2.2,
            y + th - 0.030 - 0.050 - _text_h(1, 9.0),
            chip_w,
            _text_h(1, 9.0) + 0.020,
            C(accent),
            r=0.030,
            z=3,
        )
        ax.text(
            x + tw - chip_w / 2.0 - 2.2,
            y + th - 0.030 - 0.050 - _text_h(1, 9.0) * 0.62,
            str(cnt),
            ha="center",
            va="baseline",
            fontsize=9.0,
            fontweight="bold",
            color=C(T.WHITE),
            zorder=4,
        )

        yy = y + th - 0.030 - 0.060
        yy -= _para(
            ax, x + 3.0, yy, name, tw - 16.0, 7.8, T.NAVY, bold=True, max_lines=nn
        )
        yy -= 0.045
        if desc:
            _para(ax, x + 3.0, yy, desc, tw - 6.0, 6.8, T.GREY, max_lines=nd)
        ax.text(
            x + 3.0,
            y + 0.058,
            "%d things you can do" % cnt,
            ha="left",
            va="baseline",
            fontsize=6.2,
            color=C(accent),
        )
        bw = (tw - 6.0) * (cnt / float(mx))
        ax.add_patch(
            Rectangle(
                (x + 3.0, y + 0.028),
                tw - 6.0,
                0.020,
                facecolor=C(T.RULE_SOFT),
                edgecolor="none",
                zorder=2,
            )
        )
        ax.add_patch(
            Rectangle(
                (x + 3.0, y + 0.028),
                bw,
                0.020,
                facecolor=C(accent),
                edgecolor="none",
                zorder=3,
            )
        )
    return _save(fig, path)


# ========================================================= E5 benefit stack
def benefit_stack(path, items, accent, title, subtitle, note=None):
    """Ranked benefit bars. `items` = [(label, number, display text), ...]."""
    items = [i for i in items if i and i[1]][:10]
    if not items:
        return None
    items = sorted(items, key=lambda t: -float(t[1]))
    lw_ = 34.0
    nl = [len(_lines(i[0], lw_ - 2.0, 7.4, 2)) for i in items]
    rh = [max(_text_h(k, 7.4), 0.185) for k in nl]
    gap = 0.055
    body = sum(rh) + gap * (len(items) - 1) + (0.14 if note else 0.0)

    fig, ax, top = _canvas(body, title, subtitle, accent)
    mx = max(float(i[1]) for i in items) or 1.0
    span = 100.0 - lw_ - 14.0
    y = top
    for (label, val, txt), h in zip(items, rh):
        y -= h
        bw = span * (float(val) / mx)
        ax.add_patch(
            Rectangle(
                (lw_, y + h * 0.18),
                bw,
                h * 0.64,
                facecolor=C(accent),
                edgecolor="none",
                zorder=2,
            )
        )
        _para(
            ax,
            lw_ - 2.0,
            y + h,
            label,
            lw_ - 2.0,
            7.4,
            T.NAVY,
            bold=True,
            max_lines=2,
            ha="right",
        )
        ax.text(
            lw_ + bw + 1.2,
            y + h * 0.50,
            txt,
            ha="left",
            va="center",
            fontsize=7.6,
            fontweight="bold",
            color=C(T.OCHRE),
        )
        y -= gap
    if note:
        ax.text(
            lw_,
            y,
            note,
            ha="left",
            va="top",
            fontsize=6.4,
            color=C(T.GREY),
            style="italic",
        )
    return _save(fig, path)


# ============================================================== E6 swimlane
def swimlane(path, lanes, accent, title, subtitle, columns=None):
    """A job travelling across departments.

    `lanes` = [(actor, [(col_index, step_text), ...]), ...]
    """
    lanes = [l for l in lanes if l][:8]
    if not lanes:
        return None
    ncol = max(ci for _, steps in lanes for ci, _ in steps) + 1
    if columns:
        ncol = max(ncol, len(columns))
    if ncol > 6:
        raise ValueError(
            "swimlane: %d columns will not fit the text column; "
            "six is the working maximum" % ncol
        )
    lw_ = 14.0
    gap = 1.0
    cw = (100.0 - lw_ - gap * (ncol - 1)) / ncol
    pad = 0.048
    step_w = cw - 3.2
    fs = min(
        [_fit_size(t, step_w, 6.8) for _, steps in lanes for _, t in steps] or [6.8]
    )

    hs = []
    for actor, steps in lanes:
        n = max([len(_lines(t, step_w, fs, 4)) for _, t in steps] or [1])
        n = max(n, len(_lines(actor, lw_ - 1.2, 7.2, 2)))
        hs.append(_text_h(n, fs) + pad * 2)

    head_h = (_text_h(1, 6.6) + 0.065) if columns else 0.0
    body = head_h + sum(hs) + 0.045 * len(lanes)
    fig, ax, top = _canvas(body, title, subtitle, accent)

    y = top
    if columns:
        y -= _text_h(1, 6.6)
        for ci, cl in enumerate(columns[:ncol]):
            ax.text(
                lw_ + ci * (cw + gap) + cw / 2.0,
                y,
                str(cl).upper(),
                ha="center",
                va="baseline",
                fontsize=6.6,
                fontweight="bold",
                color=C(T.GREY),
            )
        y -= 0.045
        ax.plot([lw_, 100], [y, y], lw=0.7, color=C(T.RULE))
        y -= 0.020

    lane_top = y
    for li, ((actor, steps), h) in enumerate(zip(lanes, hs)):
        y -= h + 0.045
        if li % 2 == 0:
            ax.add_patch(
                Rectangle(
                    (0, y),
                    100,
                    h + 0.045,
                    facecolor=C(T.BG_PAPER),
                    edgecolor="none",
                    zorder=0,
                )
            )
        _para(
            ax, 0.4, y + h - pad, actor, lw_ - 1.2, 7.2, T.NAVY, bold=True, max_lines=2
        )
        for ci, text in steps:
            x = lw_ + ci * (cw + gap)
            _round(ax, x, y + 0.020, cw, h - 0.040, C(T.BG_TINT), z=2)
            ax.add_patch(
                Rectangle(
                    (x, y + 0.020),
                    0.8,
                    h - 0.040,
                    facecolor=C(accent),
                    edgecolor="none",
                    zorder=3,
                )
            )
            _para(ax, x + 2.2, y + h - pad, text, step_w, fs, T.INK, max_lines=4)
    for ci in range(ncol - 1):
        x = lw_ + (ci + 1) * (cw + gap) - gap / 2.0
        ax.plot(
            [x, x],
            [y, lane_top],
            lw=0.5,
            color=C(T.RULE_SOFT),
            zorder=0,
            linestyle=(0, (2, 2)),
        )
    return _save(fig, path)


# =============================================================== E7 fan in
def fan_in(
    path,
    sources,
    hub,
    accent,
    title,
    subtitle,
    hub_note=None,
    footer="one number  ·  one history  ·  one truth",
):
    """Many ways in, one record out. `sources` = [str, ...]."""
    sources = [s for s in sources if s][:16]
    if not sources:
        return None
    n = len(sources)
    bw = 40.0
    pad = 0.040
    hs = [_text_h(len(_lines(s, bw - 3.4, 7.0, 2)), 7.0) + pad * 2 for s in sources]
    gap = 0.045
    col_h = sum(hs) + gap * (n - 1)
    foot_h = _text_h(1, 6.4) + 0.055 if footer else 0.0
    fig, ax, top = _canvas(col_h + foot_h, title, subtitle, accent)

    hub_w = 26.0
    hub_h = min(1.05, col_h * 0.42)
    hx = 68.0
    hy = top - foot_h - col_h / 2.0 - hub_h / 2.0

    y = top - foot_h
    for s, h in zip(sources, hs):
        y -= h
        _round(ax, 0, y, bw, h, C(T.BG_TINT), z=2)
        ax.add_patch(
            Rectangle((0, y), 0.8, h, facecolor=C(accent), edgecolor="none", zorder=3)
        )
        _para(ax, 2.4, y + h - pad, s, bw - 3.4, 7.0, T.INK, max_lines=2)
        mid = y + h / 2.0
        rad = 0.18 if mid > hy + hub_h / 2.0 else -0.18
        ax.add_patch(
            FancyArrowPatch(
                (bw + 0.8, mid),
                (hx - 1.0, hy + hub_h / 2.0),
                connectionstyle="arc3,rad=%.2f" % rad,
                arrowstyle="-|>",
                mutation_scale=6,
                lw=0.7,
                color=C(T.STEEL),
                zorder=1,
                shrinkA=0,
                shrinkB=2,
            )
        )
        y -= gap

    _round(ax, hx, hy, hub_w, hub_h, C(accent), r=0.045, z=4)
    ax.text(
        hx + hub_w / 2.0,
        hy + hub_h * 0.58,
        _clip(hub, 22),
        ha="center",
        va="center",
        fontsize=9.6,
        fontweight="bold",
        color=C(T.WHITE),
        zorder=5,
    )
    if hub_note:
        ax.text(
            hx + hub_w / 2.0,
            hy + hub_h * 0.24,
            _clip(hub_note, 30),
            ha="center",
            va="center",
            fontsize=6.6,
            color=C(T.SKY_PALE),
            zorder=5,
        )
    if footer:
        ax.text(
            hx + hub_w / 2.0,
            0.020,
            footer,
            ha="center",
            va="bottom",
            fontsize=6.4,
            color=C(T.GREY),
            style="italic",
        )
    return _save(fig, path)


# ============================================================= E8 auto ring
def auto_ring(path, groups, accent, title, subtitle, centre_label=None):
    """What the system does without being asked.

    `groups` = [(trigger label, count, example), ...]
    """
    groups = [g for g in groups if g][:8]
    if not groups:
        return None
    total = sum(g[1] for g in groups)
    rh = _text_h(1, 7.6) + 0.020 + _text_h(1, 6.6) + 0.070
    body = max(len(groups) * rh, 1.95)
    fig, ax, top = _canvas(body, title, subtitle, accent)

    cols = [accent, T.STEEL, T.OCHRE, T.TEAL, T.PLUM, T.GREEN, T.GOLD, T.SKY]
    # donut, drawn in its own square axes so it stays circular
    d = min(body, 1.95)
    fig_h = fig.get_figheight()
    ax2 = fig.add_axes([0.0, (top - d) / fig_h, d / W, d / fig_h])
    ax2.set_aspect("equal")
    ax2.axis("off")
    ax2.set_xlim(-1.12, 1.12)
    ax2.set_ylim(-1.12, 1.12)
    start = 90.0
    for i, (label, cnt, _ex) in enumerate(groups):
        ext = 360.0 * cnt / float(total)
        ax2.add_patch(
            Wedge(
                (0, 0),
                1.0,
                start - ext,
                start,
                width=0.36,
                facecolor=C(cols[i % len(cols)]),
                edgecolor="white",
                lw=1.3,
            )
        )
        start -= ext
    ax2.text(
        0,
        0.13,
        str(total),
        ha="center",
        va="center",
        fontsize=21,
        fontweight="bold",
        color=C(T.NAVY),
    )
    ax2.text(
        0,
        -0.26,
        centre_label or "things the system\ndoes on its own",
        ha="center",
        va="center",
        fontsize=6.8,
        color=C(T.GREY),
        linespacing=1.3,
    )

    x0 = (d / W) * 100.0 + 3.0
    y = top
    for i, (label, cnt, ex) in enumerate(groups):
        y -= rh
        ax.add_patch(
            Rectangle(
                (x0, y + 0.030),
                1.4,
                rh - 0.070,
                facecolor=C(cols[i % len(cols)]),
                edgecolor="none",
                zorder=2,
            )
        )
        yy = y + rh - 0.010
        yy -= _para(
            ax,
            x0 + 3.2,
            yy,
            "%s  ·  %d" % (label, cnt),
            100 - x0 - 4.0,
            7.6,
            T.NAVY,
            bold=True,
            max_lines=1,
        )
        yy -= 0.020
        _para(ax, x0 + 3.2, yy, ex, 100 - x0 - 4.0, 6.6, T.GREY, max_lines=1)
    return _save(fig, path)


# ============================================================== E9 who can
def who_can(path, roles, actions, marks, accent, title, subtitle):
    """Permission grid. `marks[r][c]` in {'', 'y', 'a', 'v'}."""
    roles = roles[:14]
    actions = actions[:8]
    if not roles or not actions:
        return None
    lw_ = 34.0
    cw = (100.0 - lw_) / len(actions)
    nh = max(len(_lines(a, cw - 1.0, 6.6, 3)) for a in actions)
    head_h = _text_h(nh, 6.6) + 0.060
    rh = _text_h(1, 7.0) + 0.075
    key_h = _text_h(1, 6.4) + 0.070
    fig, ax, top = _canvas(head_h + len(roles) * rh + key_h, title, subtitle, accent)

    y = top - head_h + 0.060
    for j, a in enumerate(actions):
        _para(
            ax,
            lw_ + j * cw + cw / 2.0,
            top,
            a,
            cw - 1.0,
            6.6,
            T.NAVY,
            bold=True,
            max_lines=3,
            ha="center",
        )
    ax.plot([0, 100], [y, y], lw=0.7, color=C(T.RULE))

    rx, ry = _round_r(min(rh * 0.26, 0.052))
    for i, role in enumerate(roles):
        yb = y - (i + 1) * rh
        if i % 2 == 0:
            ax.add_patch(
                Rectangle(
                    (0, yb),
                    100,
                    rh,
                    facecolor=C(T.BG_PAPER),
                    edgecolor="none",
                    zorder=0,
                )
            )
        ax.text(
            0.6,
            yb + rh * 0.36,
            _clip(role, 46),
            ha="left",
            va="baseline",
            fontsize=7.0,
            color=C(T.INK),
            zorder=2,
        )
        for j in range(len(actions)):
            m = marks[i][j] if i < len(marks) and j < len(marks[i]) else ""
            if not m:
                continue
            cx, cy = lw_ + j * cw + cw / 2.0, yb + rh / 2.0
            if m == "y":
                _disc(ax, cx, cy, rx, ry, C(accent))
            elif m == "a":
                _disc(ax, cx, cy, rx, ry, "white", ec=C(T.OCHRE), lw=0.8, z=3)
                ax.add_patch(
                    Wedge(
                        (0, 0),
                        1.0,
                        90,
                        270,
                        facecolor=C(T.OCHRE),
                        edgecolor="none",
                        zorder=4,
                        transform=_disc_tf(ax, cx, cy, rx, ry),
                    )
                )
            else:
                _disc(ax, cx, cy, rx, ry, "white", ec=C(T.GREY_LIGHT), lw=0.9)

    yk = y - len(roles) * rh - 0.100
    keys = [
        ("y", "may do it", accent),
        ("a", "may do it with approval", T.OCHRE),
        ("v", "can see it only", T.GREY_LIGHT),
    ]
    kx = 0.4
    for m, lbl, col in keys:
        cy = yk + _text_h(1, 6.4) * 0.28
        if m == "y":
            _disc(ax, kx + rx, cy, rx, ry, C(col))
        elif m == "a":
            _disc(ax, kx + rx, cy, rx, ry, "white", ec=C(col), lw=0.8, z=3)
            ax.add_patch(
                Wedge(
                    (0, 0),
                    1.0,
                    90,
                    270,
                    facecolor=C(col),
                    edgecolor="none",
                    zorder=4,
                    transform=_disc_tf(ax, kx + rx, cy, rx, ry),
                )
            )
        else:
            _disc(ax, kx + rx, cy, rx, ry, "white", ec=C(col), lw=0.9)
        ax.text(
            kx + rx * 2 + 1.2,
            yk,
            lbl,
            ha="left",
            va="baseline",
            fontsize=6.4,
            color=C(T.GREY),
        )
        kx += rx * 2 + 1.2 + len(lbl) * 0.72 + 3.0
    return _save(fig, path)


# =========================================================== E10 target dials
def target_dials(path, kpis, accent, title, subtitle, per_row=4):
    """KPI dials. `kpis` = [(name, display value, fraction 0-1), ...]."""
    kpis = [k for k in kpis if k][:8]
    if not kpis:
        return None
    per_row = min(per_row, len(kpis))
    rows = int(math.ceil(len(kpis) / float(per_row)))
    cw_in = W / per_row
    dial_h = cw_in * 0.46
    nl = max(len(_lines(k[0], (100.0 / per_row) - 3.0, 6.6, 3)) for k in kpis)
    ch = dial_h + 0.045 + _text_h(nl, 6.6) + 0.085
    fig, ax, top = _canvas(rows * ch, title, subtitle, accent)
    fig_h = fig.get_figheight()

    for i, (name, disp, frac) in enumerate(kpis):
        r, c = divmod(i, per_row)
        y_top = top - r * ch
        ax_d = fig.add_axes(
            [
                c * cw_in / W + 0.010,
                (y_top - dial_h) / fig_h,
                cw_in / W - 0.020,
                dial_h / fig_h,
            ]
        )
        ax_d.set_aspect("equal")
        ax_d.axis("off")
        ax_d.set_xlim(-1.10, 1.10)
        ax_d.set_ylim(-0.10, 1.10)
        f = max(0.0, min(1.0, float(frac)))
        ax_d.add_patch(
            Wedge(
                (0, 0),
                1.0,
                0,
                180,
                width=0.30,
                facecolor=C(T.RULE_SOFT),
                edgecolor="none",
            )
        )
        ax_d.add_patch(
            Wedge(
                (0, 0),
                1.0,
                180 - 180 * f,
                180,
                width=0.30,
                facecolor=C(accent),
                edgecolor="none",
            )
        )
        ax_d.text(
            0,
            0.16,
            disp,
            ha="center",
            va="center",
            fontsize=11.5,
            fontweight="bold",
            color=C(T.NAVY),
        )
        _para(
            ax,
            c * (100.0 / per_row) + (100.0 / per_row) / 2.0,
            y_top - dial_h - 0.045,
            name,
            (100.0 / per_row) - 3.0,
            6.6,
            T.GREY,
            max_lines=3,
            ha="center",
        )
    return _save(fig, path)


# =========================================================== E11 gate ladder
def gate_ladder(path, gates, accent, title, subtitle):
    """Sequential gates a job must pass. `gates` = [(name, test, who), ...]."""
    gates = [g for g in gates if g][:9]
    if not gates:
        return None
    xn, xt = 9.0, 37.0
    wn, wt = 26.0, 40.0
    pad = 0.050
    hs = []
    for g in gates:
        n = max(
            len(_lines(g[0], wn, 7.4, 2)),
            len(_lines(g[1] if len(g) > 1 else "", wt, 6.9, 3)),
        )
        hs.append(max(_text_h(n, 7.4) + pad * 2, 0.30))
    gap = 0.070
    fig, ax, top = _canvas(sum(hs) + gap * (len(gates) - 1), title, subtitle, accent)

    y = top
    for i, (g, h) in enumerate(zip(gates, hs)):
        name = g[0]
        test = g[1] if len(g) > 1 else ""
        who = g[2] if len(g) > 2 else ""
        y -= h
        _round(ax, 0, y, 100, h, C(T.BG_PAPER), z=1)
        ax.add_patch(
            Rectangle((0, y), 1.0, h, facecolor=C(accent), edgecolor="none", zorder=2)
        )
        _disc(ax, 5.3, y + h / 2.0, 2.0, 0.088, C(accent), z=3)
        ax.text(
            5.3,
            y + h / 2.0 - 0.022,
            str(i + 1),
            ha="center",
            va="baseline",
            fontsize=6.6,
            fontweight="bold",
            color=C(T.WHITE),
            zorder=4,
        )
        _para(ax, xn, y + h - pad, name, wn, 7.4, T.NAVY, bold=True, max_lines=2)
        if test:
            _para(ax, xt, y + h - pad, test, wt, 6.9, T.INK, max_lines=3)
        if who:
            ax.text(
                99.4,
                y + h / 2.0 - 0.020,
                _clip(who, 22),
                ha="right",
                va="baseline",
                fontsize=6.4,
                color=C(T.GREY),
            )
        if i < len(gates) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (5.3, y - 0.008),
                    (5.3, y - gap + 0.006),
                    arrowstyle="-|>",
                    mutation_scale=5,
                    lw=0.8,
                    color=C(T.RULE),
                    zorder=1,
                )
            )
        y -= gap
    return _save(fig, path)


# =========================================================== E12 scale bars
def scale_bars(path, items, accent, title, subtitle, unit="", note=None, label_w=32.0):
    """Ranked bars with value labels. `items` = [(label, value), ...]."""
    items = [i for i in items if i][:16]
    if not items:
        return None
    rh = _text_h(1, 7.2) + 0.055
    note_h = _text_h(1, 6.4) + 0.050 if note else 0.0
    fig, ax, top = _canvas(len(items) * rh + note_h, title, subtitle, accent)
    mx = max(float(v) for _, v in items) or 1.0
    span = 100.0 - label_w - 12.0
    y = top
    for label, val in items:
        y -= rh
        bw = span * (float(val) / mx)
        ax.add_patch(
            Rectangle(
                (label_w, y + rh * 0.22),
                bw,
                rh * 0.56,
                facecolor=C(accent),
                edgecolor="none",
                zorder=2,
            )
        )
        ax.text(
            label_w - 1.6,
            y + rh * 0.34,
            _clip(label, 40),
            ha="right",
            va="baseline",
            fontsize=7.2,
            color=C(T.NAVY),
        )
        v = int(val) if float(val) == int(val) else val
        ax.text(
            label_w + bw + 1.2,
            y + rh * 0.34,
            "%s%s" % (v, unit),
            ha="left",
            va="baseline",
            fontsize=7.2,
            fontweight="bold",
            color=C(T.OCHRE),
        )
    if note:
        ax.text(
            label_w,
            y - 0.050,
            note,
            ha="left",
            va="top",
            fontsize=6.4,
            color=C(T.GREY),
            style="italic",
        )
    return _save(fig, path)


# ======================================================= E13 boundary panels
def boundary_panels(
    path,
    does,
    does_not,
    accent,
    title,
    subtitle,
    heads=("This module handles", "This module deliberately leaves alone"),
):
    """Two facing panels: what it owns, what it hands to someone else."""
    does = [d for d in does if d][:10]
    does_not = [d for d in does_not if d][:10]
    if not does and not does_not:
        return None
    pw = 48.5
    tw = pw - 7.0
    pad = 0.060
    gap = 0.055

    def col_h(items):
        return sum(_text_h(len(_lines(i, tw, 7.0, 3)), 7.0) + gap for i in items)

    head_h = _text_h(1, 6.8) + 0.075
    body = max(col_h(does), col_h(does_not)) + head_h + pad * 2
    fig, ax, top = _canvas(body, title, subtitle, accent)

    for x, head, items, col, kind in (
        (0.0, heads[0], does, accent, "tick"),
        (51.5, heads[1], does_not, T.GREY, "arrow"),
    ):
        _round(ax, x, top - body, pw, body, C(T.BG_PAPER), z=1)
        ax.add_patch(
            Rectangle(
                (x, top - 0.030),
                pw,
                0.030,
                facecolor=C(col),
                edgecolor="none",
                zorder=2,
            )
        )
        y = top - 0.030 - pad
        ax.text(
            x + 2.6,
            y - _text_h(1, 6.8) * 0.76,
            head.upper(),
            ha="left",
            va="baseline",
            fontsize=6.8,
            fontweight="bold",
            color=C(col),
        )
        y -= _text_h(1, 6.8) + 0.075
        for it in items:
            nl = len(_lines(it, tw, 7.0, 3))
            if kind == "tick":
                _tick(ax, x + 2.6, y - 0.088, 0.056, col)
            else:
                aw = 0.052 / W * 100.0
                ax.add_patch(
                    Polygon(
                        [
                            (x + 2.6, y - 0.036),
                            (x + 2.6, y - 0.098),
                            (x + 2.6 + aw * 1.5, y - 0.067),
                        ],
                        closed=True,
                        facecolor=C(col),
                        edgecolor="none",
                        zorder=4,
                    )
                )
            _para(ax, x + 5.6, y, it, tw, 7.0, T.INK, max_lines=3)
            y -= _text_h(nl, 7.0) + gap
    return _save(fig, path)


# ======================================================= E14 volume profile
def volume_profile(path, items, accent, title, subtitle):
    """Strip of big numbers with a caption each. `items` = [(big, label, cap)]."""
    items = [i for i in items if i][:6]
    if not items:
        return None
    n = len(items)
    gap = 1.4
    tw = (100.0 - gap * (n - 1)) / n
    nl = max(len(_lines(str(i[1]).upper(), tw - 3.0, 6.5, 2)) for i in items)
    nc = max(len(_lines(str(i[2]), tw - 3.0, 6.2, 2)) if i[2] else 1 for i in items)
    th = (
        0.030
        + 0.075
        + _text_h(1, 19.0)
        + 0.030
        + _text_h(nl, 6.5)
        + 0.030
        + _text_h(nc, 6.2)
        + 0.070
    )
    fig, ax, top = _canvas(th, title, subtitle, accent)

    for i, (big, label, cap) in enumerate(items):
        x = i * (tw + gap)
        y = top - th
        _round(ax, x, y, tw, th, C(T.BG_TINT), z=1)
        ax.add_patch(
            Rectangle(
                (x, top - 0.030),
                tw,
                0.030,
                facecolor=C(accent),
                edgecolor="none",
                zorder=2,
            )
        )
        b = str(big)
        fs = 19.0 if len(b) <= 4 else (15.5 if len(b) <= 7 else 12.5)
        yy = top - 0.075
        ax.text(
            x + tw / 2.0,
            yy - _text_h(1, 19.0) * 0.80,
            b,
            ha="center",
            va="baseline",
            fontsize=fs,
            fontweight="bold",
            color=C(T.NAVY),
        )
        yy -= _text_h(1, 19.0) + 0.030
        yy -= _para(
            ax,
            x + tw / 2.0,
            yy,
            str(label).upper(),
            tw - 3.0,
            6.5,
            accent,
            bold=True,
            max_lines=2,
            ha="center",
        )
        if cap:
            yy -= 0.030
            _para(
                ax,
                x + tw / 2.0,
                yy,
                str(cap),
                tw - 3.0,
                6.2,
                T.GREY,
                max_lines=2,
                ha="center",
            )
    return _save(fig, path)


# ===================================================== E15 compare columns
def compare_columns(path, columns, accent, title, subtitle):
    """Side-by-side option cards. `columns` = [(head, sub, [line, ...]), ...]."""
    columns = [c for c in columns if c][:4]
    if not columns:
        return None
    n = len(columns)
    gap = 1.6
    cw = (100.0 - gap * (n - 1)) / n
    tw = cw - 6.0
    pad = 0.060
    line_gap = 0.048

    def h_of(col):
        head, sub, lines = col
        h = _text_h(len(_lines(head, tw, 8.4, 2)), 8.4) + 0.030
        if sub:
            h += _text_h(len(_lines(sub, tw, 6.6, 2)), 6.6) + 0.055
        for l in lines:
            h += _text_h(len(_lines(l, tw - 2.0, 6.9, 3)), 6.9) + line_gap
        return h

    body = max(h_of(c) for c in columns) + pad * 2 + 0.030
    fig, ax, top = _canvas(body, title, subtitle, accent)
    cols = [accent, T.STEEL, T.PLUM, T.GREEN]
    for i, (head, sub, lines) in enumerate(columns):
        x = i * (cw + gap)
        col = cols[i % len(cols)]
        _round(ax, x, top - body, cw, body, C(T.BG_PAPER), z=1)
        ax.add_patch(
            Rectangle(
                (x, top - 0.030),
                cw,
                0.030,
                facecolor=C(col),
                edgecolor="none",
                zorder=2,
            )
        )
        y = top - 0.030 - pad
        y -= _para(ax, x + 3.0, y, head, tw, 8.4, T.NAVY, bold=True, max_lines=2)
        y -= 0.030
        if sub:
            y -= _para(ax, x + 3.0, y, sub, tw, 6.6, col, max_lines=2)
            y -= 0.055
        for l in lines:
            ax.add_patch(
                Rectangle(
                    (x + 3.0, y - 0.052),
                    1.1,
                    0.022,
                    facecolor=C(col),
                    edgecolor="none",
                    zorder=3,
                )
            )
            y -= _para(ax, x + 5.0, y, l, tw - 2.0, 6.9, T.INK, max_lines=3)
            y -= line_gap
    return _save(fig, path)
