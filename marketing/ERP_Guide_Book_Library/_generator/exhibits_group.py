# -*- coding: utf-8 -*-
"""
exhibits_group — aggregate exhibits for a category, the portal suite and the
whole estate. Same design language as exhibits.py, one level up in scale.
"""
import re
import math

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

import theme as T
from exhibits import (W, _save, _titleblock, _bare, _rounded, _wrap, _clip,
                      WAVE_MONTHS)


def cat_scale(path, items, accent, title, subtitle):
    """Requirements and build effort, component by component."""
    if not items:
        return None
    items = sorted(items, key=lambda d: d["reqs"], reverse=True)
    labels = ["%s  %s" % (d["uid"], _clip(d["name"], 38)) for d in items]
    reqs = [d["reqs"] for d in items]
    eff = [d.get("effort") or 0 for d in items]
    y = np.arange(len(items))[::-1]

    fig, ax = plt.subplots(figsize=(W, max(2.0, 0.44 * len(items) + 1.45)))
    ax.barh(y + 0.19, reqs, height=0.34, color=T.hexc(accent), zorder=3)
    ax2 = ax.twiny()
    ax2.barh(y - 0.19, eff, height=0.34, color=T.hexc(T.GREY_LIGHT), zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.6, color=T.hexc(T.INK))
    ax.set_xlim(0, (max(reqs) or 1) * 1.22)
    ax2.set_xlim(0, (max(eff) or 1) * 1.22)
    ax.set_xticks([]); ax2.set_xticks([]); ax2.set_yticks([])
    _bare(ax); _bare(ax2)
    for yy, v in zip(y, reqs):
        ax.text(v + (max(reqs) or 1) * 0.015, yy + 0.19, str(v), va="center",
                fontsize=7.4, fontweight="bold", color=T.hexc(T.NAVY))
    for yy, v in zip(y, eff):
        if v:
            ax2.text(v + (max(eff) or 1) * 0.015, yy - 0.19, "%g PW" % v,
                     va="center", fontsize=7.1, color=T.hexc(T.GREY))
    ax.text(0.0, 1.05, title, transform=ax.transAxes, fontsize=9.5,
            fontweight="bold", color=T.hexc(T.NAVY), va="bottom")
    ax.text(0.0, 1.045, subtitle + "   ·   coloured bar: requirements   ·   "
            "grey bar: person-weeks   ·   each on its own scale",
            transform=ax.transAxes, fontsize=7.2, color=T.hexc(T.GREY), va="top")
    return _save(fig, path)


def cat_wave_map(path, items, accent, title, subtitle):
    """Component-by-wave delivery map across the 36-month programme."""
    if not items:
        return None
    waves = list(WAVE_MONTHS.keys())
    items = sorted(items, key=lambda x: (re.sub(r"\D", "", x.get("wave") or "99"),
                                         x["uid"]))
    fig, ax = plt.subplots(figsize=(W, max(2.0, 0.36 * len(items) + 1.5)))
    ax.set_xlim(-4.5, 37)
    ax.set_ylim(0, len(items) + 2.0)
    ax.axis("off")

    for i, (w, (a, b)) in enumerate(WAVE_MONTHS.items()):
        ax.add_patch(Rectangle((a - 1, 0.25), b - a + 1, len(items) + 0.9,
                               facecolor=T.hexc(T.BG_PAPER) if i % 2 == 0 else "white",
                               edgecolor="none", zorder=0))
        ax.text((a - 1 + b) / 2.0, len(items) + 1.25, w, ha="center",
                fontsize=7.4, fontweight="bold", color=T.hexc(T.GREY))
        ax.text((a - 1 + b) / 2.0, len(items) + 0.75, "M%d–%d" % (a, b),
                ha="center", fontsize=6.9, color=T.hexc(T.GREY_LIGHT))

    for i, d in enumerate(items):
        yy = len(items) - i
        ax.text(-4.4, yy, d["uid"], fontsize=7.5, fontweight="bold",
                va="center", ha="left", color=T.hexc(T.NAVY), zorder=4)
        hits = re.findall(r"W(\d)", d.get("wave") or "")
        for wnum in hits:
            w = "W" + wnum
            if w not in WAVE_MONTHS:
                continue
            a, b = WAVE_MONTHS[w]
            _rounded(ax, a - 1 + 0.18, yy - 0.30, (b - a + 1) - 0.36, 0.60,
                     T.hexc(accent), r=0.10, z=3)
        if not hits:
            ax.text(0.4, yy, "wave unassigned", fontsize=7.0, va="center",
                    color=T.hexc(T.RED), zorder=4)
    ax.text(-4.4, len(items) + 1.75, title, fontsize=9.5, fontweight="bold",
            color=T.hexc(T.NAVY), va="bottom")
    return _save(fig, path)


def cat_dependency_matrix(path, items, accent, title, subtitle):
    """Who inside the group depends on whom."""
    ids = [d["uid"] for d in items]
    if len(ids) < 2:
        return None
    idx = {u: i for i, u in enumerate(ids)}
    n = len(ids)
    m = np.zeros((n, n))
    for d in items:
        for dep in d.get("depends_on", []):
            if dep in idx and dep != d["uid"]:
                m[idx[d["uid"]], idx[dep]] = 1
    if m.sum() == 0:
        return None
    # Size the frame to the matrix so an equal-aspect grid leaves no dead space,
    # and centre it in the text column.
    side = min(5.0, max(1.6, 0.34 * n))          # inches, the grid itself
    label_in = 0.62                              # room for the tick labels
    fig_h = side + label_in + 0.72
    fig = plt.figure(figsize=(W, fig_h))
    left = 0.95 / W                              # room for the row labels
    axm = fig.add_axes([left, label_in / fig_h, side / W, side / fig_h])
    axm.imshow(m, cmap=matplotlib.colors.ListedColormap(
        ["#FFFFFF", T.hexc(accent)]), vmin=0, vmax=1, aspect="equal")
    axm.set_xticks(range(n)); axm.set_yticks(range(n))
    axm.set_xticklabels(ids, fontsize=7.1, rotation=90, color=T.hexc(T.INK))
    axm.set_yticklabels(ids, fontsize=7.1, color=T.hexc(T.INK))
    axm.set_xticks(np.arange(-0.5, n, 1), minor=True)
    axm.set_yticks(np.arange(-0.5, n, 1), minor=True)
    axm.grid(which="minor", color=T.hexc(T.RULE), linewidth=0.5)
    axm.tick_params(which="both", length=0)
    for s in axm.spines.values():
        s.set_color(T.hexc(T.RULE))
    axm.set_xlabel("depends on  →", fontsize=7.2, color=T.hexc(T.GREY))
    axm.set_ylabel("component  ↓", fontsize=7.2, color=T.hexc(T.GREY))
    fig.text(0.0, 1.0 - 0.20 / fig_h, title, fontsize=9.5, fontweight="bold",
             color=T.hexc(T.NAVY), va="top")
    fig.text(0.0, 1.0 - 0.36 / fig_h, subtitle, fontsize=7.4,
             color=T.hexc(T.GREY), va="top")
    return _save(fig, path)


def cat_external_reach(path, counts, accent, title, subtitle):
    """How far outside itself this group reaches."""
    items = [(k, v) for k, v in counts.items() if v]
    if not items:
        return None
    items.sort(key=lambda kv: kv[1], reverse=True)
    labels = ["%s — %s" % (k, T.cat_name(k)) for k, _ in items]
    vals = [v for _, v in items]
    y = np.arange(len(items))[::-1]
    fig, ax = plt.subplots(figsize=(W, max(1.8, 0.34 * len(items) + 1.25)))
    ax.barh(y, vals, height=0.6,
            color=[T.hexc(T.cat_colour(k)) for k, _ in items], zorder=3)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.7, color=T.hexc(T.INK))
    ax.set_xlim(0, max(vals) * 1.18)
    ax.set_xticks([])
    _bare(ax)
    for yy, v in zip(y, vals):
        ax.text(v + max(vals) * 0.018, yy, str(v), va="center", fontsize=7.7,
                fontweight="bold", color=T.hexc(T.NAVY))
    _titleblock(ax, title, subtitle)
    return _save(fig, path)


def cat_composition(path, items, accent, title, subtitle):
    """Stacked profile: rules, entities, events and automations per component."""
    if not items:
        return None
    keys = [("rules", "Business rules", T.RED),
            ("entities", "Owned entities", T.STEEL),
            ("events", "Domain events", T.TEAL),
            ("automations", "Automations", T.OCHRE)]
    items = sorted(items, key=lambda d: sum(d.get(k, 0) for k, _, _ in keys),
                   reverse=True)
    labels = [d["uid"] for d in items]
    y = np.arange(len(items))[::-1]
    fig, ax = plt.subplots(figsize=(W, max(2.0, 0.34 * len(items) + 1.7)))
    left = np.zeros(len(items))
    for k, lab, col in keys:
        vals = np.array([d.get(k, 0) for d in items], dtype=float)
        ax.barh(y, vals, left=left, height=0.6, color=T.hexc(col), label=lab,
                zorder=3)
        left += vals
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=7.6, fontweight="bold",
                       color=T.hexc(T.NAVY))
    ax.set_xticks([])
    ax.set_xlim(0, (left.max() or 1) * 1.10)
    _bare(ax)
    for yy, tot in zip(y, left):
        ax.text(tot + (left.max() or 1) * 0.012, yy, "%d" % tot, va="center",
                fontsize=7.4, color=T.hexc(T.GREY))
    leg = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=4,
                    frameon=False, fontsize=7.5)
    for t in leg.get_texts():
        t.set_color(T.hexc(T.INK_SOFT))
    _titleblock(ax, title, subtitle)
    return _save(fig, path)


def stack_bar(path, labels, series, title, subtitle, colours=None,
              value_fmt="%d", horizontal=True):
    """Generic 100%-style stacked bar for aggregate mixes."""
    if not labels:
        return None
    colours = colours or T.SERIES
    fig, ax = plt.subplots(figsize=(W, 1.35 + 0.20 * len(labels)))
    ax.set_xlim(0, 100); ax.set_ylim(0, 10); ax.axis("off")
    total = float(sum(series)) or 1.0
    x = 0.0
    for i, (lab, v) in enumerate(zip(labels, series)):
        w = 100.0 * v / total
        ax.add_patch(Rectangle((x, 6.4), w, 2.0,
                               facecolor=T.hexc(colours[i % len(colours)]),
                               edgecolor="white", linewidth=1.2))
        if w >= 6:
            ax.text(x + w / 2, 7.4, "%.0f%%" % w, ha="center", va="center",
                    fontsize=7.6, fontweight="bold", color="white")
        x += w
    per = 3
    for i, (lab, v) in enumerate(zip(labels, series)):
        r, c = divmod(i, per)
        xx = c * (100.0 / per)
        yy = 5.0 - r * 1.5
        ax.add_patch(Rectangle((xx, yy - 0.35), 1.4, 0.9,
                               facecolor=T.hexc(colours[i % len(colours)]),
                               edgecolor="none"))
        ax.text(xx + 2.2, yy, "%s   %s" % (lab, value_fmt % v), fontsize=7.5,
                va="center", color=T.hexc(T.INK))
    rows = int(math.ceil(len(labels) / float(per)))
    ax.set_ylim(5.0 - rows * 1.5 - 0.8, 10)
    ax.text(0, 9.4, title, fontsize=9.5, fontweight="bold",
            color=T.hexc(T.NAVY), va="bottom")
    ax.text(0, 9.0, subtitle, fontsize=7.4, color=T.hexc(T.GREY), va="top")
    return _save(fig, path)


# ------------------------------------------------------------ estate exhibits
def estate_treemap(path, groups, title, subtitle):
    """Two-band treemap of the estate, one block per category."""
    data = [(k, v) for k, v in groups.items() if v]
    if not data:
        return None
    total = float(sum(v for _, v in data))
    data.sort(key=lambda kv: kv[1], reverse=True)
    first, acc, half = [], 0.0, total / 2.0
    for k, v in data:
        if acc < half or not first:
            first.append((k, v)); acc += v
    second = [d for d in data if d not in first]

    fig, ax = plt.subplots(figsize=(W, 3.6))
    ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
    for group, y0, h in ((first, 88.0, 44.0), (second, 42.0, 40.0)):
        gt = float(sum(v for _, v in group)) or 1.0
        x = 0.0
        for k, v in group:
            w = 100.0 * v / gt
            _rounded(ax, x + 0.35, y0 - h + 0.35, max(w - 0.7, 0.5), h - 0.7,
                     T.hexc(T.cat_colour(k)), r=0.7)
            if w > 6:
                ax.text(x + w / 2, y0 - h / 2 + 5.0, k, ha="center", va="center",
                        fontsize=13.5, fontweight="bold", color="white")
                ax.text(x + w / 2, y0 - h / 2 - 2.0, str(v), ha="center",
                        va="center", fontsize=9.0, color="white")
                if w > 15:
                    ax.text(x + w / 2, y0 - h / 2 - 7.0,
                            _wrap(T.cat_name(k), max(int(w * 0.34), 8), 3),
                            ha="center", va="top", fontsize=7.1, color="white",
                            linespacing=1.15)
            x += w
    ax.text(0, 97, title, fontsize=9.5, fontweight="bold",
            color=T.hexc(T.NAVY), va="bottom")
    ax.text(0, 96, subtitle, fontsize=7.4, color=T.hexc(T.GREY), va="top")
    return _save(fig, path)


def estate_heatmap(path, matrix, rows, cols, title, subtitle):
    """Category-to-category coupling heatmap."""
    m = np.array(matrix, dtype=float)
    if m.size == 0 or m.sum() == 0:
        return None
    fig = plt.figure(figsize=(W, 4.9))
    axm = fig.add_axes([0.10, 0.05, 0.84, 0.79])
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "house", ["#FFFFFF", T.hexc(T.SKY_PALE), T.hexc(T.STEEL), T.hexc(T.NAVY)])
    axm.imshow(m, cmap=cmap, aspect="auto")
    axm.set_xticks(range(len(cols))); axm.set_yticks(range(len(rows)))
    axm.set_xticklabels(cols, fontsize=7.6, color=T.hexc(T.INK))
    axm.set_yticklabels(rows, fontsize=7.6, color=T.hexc(T.INK))
    axm.set_xticks(np.arange(-0.5, len(cols), 1), minor=True)
    axm.set_yticks(np.arange(-0.5, len(rows), 1), minor=True)
    axm.grid(which="minor", color="white", linewidth=1.1)
    axm.tick_params(which="both", length=0)
    for s in axm.spines.values():
        s.set_visible(False)
    mx = m.max() or 1
    for i in range(len(rows)):
        for j in range(len(cols)):
            if m[i, j]:
                axm.text(j, i, "%d" % m[i, j], ha="center", va="center",
                         fontsize=7.2,
                         color="white" if m[i, j] > mx * 0.55 else T.hexc(T.INK))
    axm.set_xlabel("depends on category  →", fontsize=7.5, color=T.hexc(T.GREY))
    axm.set_ylabel("category  ↓", fontsize=7.5, color=T.hexc(T.GREY))
    fig.text(0.02, 0.95, title, fontsize=9.5, fontweight="bold",
             color=T.hexc(T.NAVY), va="bottom")
    fig.text(0.02, 0.935, subtitle, fontsize=7.4, color=T.hexc(T.GREY), va="top")
    return _save(fig, path)


def estate_wave_load(path, wave_counts, wave_effort, title, subtitle):
    """Programme load by wave — build effort with component counts beneath."""
    waves = list(WAVE_MONTHS.keys())
    counts = [wave_counts.get(w, 0) for w in waves]
    effort = [wave_effort.get(w, 0) for w in waves]
    if not any(counts):
        return None
    mx = max(effort) or 1
    fig, ax = plt.subplots(figsize=(W, 2.8))
    x = np.arange(len(waves))
    ax.bar(x, effort, width=0.62, color=T.hexc(T.STEEL), zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(["%s\nM%d–%d" % (w, WAVE_MONTHS[w][0], WAVE_MONTHS[w][1])
                        for w in waves], fontsize=7.3, color=T.hexc(T.INK))
    ax.set_yticks([])
    _bare(ax)
    for xi, (e, c) in enumerate(zip(effort, counts)):
        if e:
            ax.text(xi, e + mx * 0.03, "%g PW" % round(e), ha="center",
                    fontsize=7.5, fontweight="bold", color=T.hexc(T.NAVY))
        ax.text(xi, -mx * 0.11, "%d" % c, ha="center", fontsize=7.3,
                color=T.hexc(T.GREY))
    ax.text(-0.75, -mx * 0.11, "components", ha="left", fontsize=6.9,
            color=T.hexc(T.GREY_LIGHT))
    ax.set_ylim(-mx * 0.20, mx * 1.18)
    _titleblock(ax, title, subtitle)
    return _save(fig, path)


def library_map(path, groups, title, subtitle, per_row=7):
    """A shelf view of the library: every guide book, grouped by category."""
    entries = [(k, v) for k, v in groups.items() if v]
    if not entries:
        return None
    band_rows = [int(math.ceil(len(v) / float(per_row))) for _, v in entries]
    chipw, chiph, gap = 13.2, 5.2, 1.3
    height_units = sum(r * (chiph + gap) for r in band_rows) + 7.0 * len(entries) + 10
    fig, ax = plt.subplots(figsize=(W, max(3.0, height_units / 100.0 * 8.6)))
    ax.set_xlim(0, 100)
    ax.axis("off")

    y = 0.0
    for (k, specs), nrows in zip(entries, band_rows):
        y -= 6.6
        band = ("PORTALS & APPLICATIONS" if k == "P"
                else "CATEGORY %s — %s" % (k, T.cat_name(k).upper()))
        ax.text(0, y + 1.1, "%s   ·   %d guide book%s"
                % (band, len(specs), "" if len(specs) == 1 else "s"),
                fontsize=7.5, fontweight="bold",
                color=T.hexc(T.cat_colour(k)), va="bottom")
        for i, s in enumerate(specs):
            r, c = divmod(i, per_row)
            x = c * (chipw + gap)
            yy = y - 1.4 - r * (chiph + gap) - chiph
            _rounded(ax, x, yy, chipw, chiph, T.hexc(T.cat_colour(k)), r=0.5, z=3)
            ax.text(x + chipw / 2, yy + chiph / 2, s, ha="center", va="center",
                    fontsize=7.8, fontweight="bold", color="white", zorder=4)
        y = y - 1.4 - nrows * (chiph + gap)
    ax.set_ylim(y - 2, 6.5)
    ax.text(0, 5.0, title, fontsize=9.5, fontweight="bold",
            color=T.hexc(T.NAVY), va="bottom")
    ax.text(0, 4.5, subtitle, fontsize=7.4, color=T.hexc(T.GREY), va="top")
    return _save(fig, path)


def revenue_streams(path, streams, title, subtitle):
    """The fourteen revenue streams and the modules that run them."""
    if not streams:
        return None
    n = len(streams)
    rows = int(math.ceil(n / 2.0))
    fig, ax = plt.subplots(figsize=(W, 0.44 * rows + 1.1))
    ax.set_xlim(0, 100)
    ax.set_ylim(-rows * 10.0, 6.0)
    ax.axis("off")
    for i, (num, name, owner, cat) in enumerate(streams):
        r, c = divmod(i, 2)
        x = c * 50.0
        y = -(r + 1) * 10.0 + 1.4
        _rounded(ax, x, y, 47.5, 7.6, T.hexc(T.BG_TINT),
                 ec=T.hexc(T.RULE_SOFT), lw=0.5, r=0.6)
        ax.add_patch(Rectangle((x, y), 1.1, 7.6,
                               facecolor=T.hexc(T.cat_colour(cat)),
                               edgecolor="none", zorder=4))
        ax.text(x + 3.0, y + 3.8, str(num), fontsize=10.5, fontweight="bold",
                color=T.hexc(T.GREY_LIGHT), va="center", zorder=5)
        ax.text(x + 8.0, y + 5.1, _clip(name, 42), fontsize=7.8,
                fontweight="bold", color=T.hexc(T.NAVY), va="center", zorder=5)
        ax.text(x + 8.0, y + 2.2, _clip(owner, 46), fontsize=7.0,
                color=T.hexc(T.GREY), va="center", zorder=5)
    ax.text(0, 4.4, title, fontsize=9.5, fontweight="bold",
            color=T.hexc(T.NAVY), va="bottom")
    ax.text(0, 3.9, subtitle, fontsize=7.4, color=T.hexc(T.GREY), va="top")
    return _save(fig, path)
