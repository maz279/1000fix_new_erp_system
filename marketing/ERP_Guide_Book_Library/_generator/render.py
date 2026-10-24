# -*- coding: utf-8 -*-
"""
render — the typographic layer.

Turns parsed markdown blocks into designed Word content: house tables with
repeating headers and semantic cell colouring, four kinds of callout panel,
monospaced diagram panels, captioned exhibits, KPI strips, pull quotes and
section openers. Every visual decision lives here or in theme.py; nothing
downstream sets a colour or a size directly.
"""

import re
import os

from docx.shared import Pt, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

import theme as T
import docxkit as K
import mdparse as MD

ALIGN = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
}

# columns whose content is an identifier — keep them narrow and mono
ID_HEADERS = (
    "id",
    "fr id",
    "kpi id",
    "cd id",
    "int id",
    "#",
    "ref",
    "code",
    "no.",
    "aut id",
    "bru id",
    "ac",
    "q",
)
NARROW_HEADERS = (
    "pri",
    "priority",
    "layer",
    "class",
    "wave",
    "effort",
    "coverage",
    "access",
    "%",
    "count",
    "volume",
    "type",
    "method",
    "direction",
    "frequency",
    "lifetime",
)


# --------------------------------------------------------------- inline runs
def emit_inline(
    p,
    text,
    size=T.SIZE_BODY,
    colour=T.INK,
    base_bold=False,
    mono_colour=T.BLUE,
    link_colour=T.STEEL,
):
    """Write markdown inline formatting into an existing paragraph."""
    for chunk, f in MD.inline_runs(text):
        if f.get("code"):
            K.run(
                p,
                chunk,
                size=size - 0.5,
                font=T.FONT_MONO,
                colour=mono_colour,
                bold=base_bold or f.get("b", False),
            )
        elif f.get("link"):
            target = f["link"]
            if target.startswith(("http://", "https://", "mailto:")):
                K.external_link(p, target, chunk, size=size, colour=link_colour)
            else:
                K.run(
                    p,
                    chunk,
                    size=size,
                    colour=colour,
                    bold=base_bold or f.get("b", False),
                    italic=f.get("i", False),
                )
        else:
            K.run(
                p,
                chunk,
                size=size,
                bold=base_bold or f.get("b", False),
                italic=f.get("i", False),
                colour=colour,
            )
    return p


def body(
    doc,
    text,
    size=T.SIZE_BODY,
    colour=T.INK,
    before=0,
    after=5,
    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
    indent=0,
    keep_next=False,
):
    p = doc.add_paragraph()
    K.pfmt(
        p,
        before=before,
        after=after,
        line=1.16,
        align=align,
        left_indent=indent,
        keep_next=keep_next,
    )
    emit_inline(p, text, size=size, colour=colour)
    return p


def spacer(doc, pts=4):
    p = doc.add_paragraph()
    K.pfmt(p, before=0, after=0)
    p.paragraph_format.line_spacing = Pt(pts)
    return p


def vspace(container, mm):
    """Exact vertical space, in millimetres, inside a document or a cell.

    Cell margins are honoured inconsistently across renderers; an empty
    paragraph with an exact line height is not. The paragraph carries no run:
    an exact line height needs none, and a hairline-sized run would show up
    in a typography audit as a sub-minimum type size.
    """
    p = container.add_paragraph()
    K.pfmt(p, before=0, after=0)
    p.paragraph_format.line_spacing = Pt(max(1.0, mm * 2.8346))
    return p


def rule_gap(container, colour, weight=6, space=8, gap_pt=2.0):
    """A ruled paragraph used purely as a divider, with no visible run."""
    p = container.add_paragraph()
    K.pfmt(p, before=0, after=0)
    p.paragraph_format.line_spacing = Pt(gap_pt)
    K.para_borders(p, top=(weight, colour, space))
    return p


def hairline(doc, colour=T.RULE, before=5, after=7, size=6):
    p = doc.add_paragraph()
    K.pfmt(p, before=before, after=after)
    p.paragraph_format.line_spacing = Pt(1)
    K.para_borders(p, bottom=(size, colour, 1))
    return p


# ------------------------------------------------------------------ headings
def part_opener(doc, number, title, blurb, accent, page_break=True):
    """Full-width part divider — the library's structural signpost."""
    if page_break:
        pb = doc.add_paragraph()
        K.pfmt(pb, before=0, after=0, page_break_before=True)
        pb.paragraph_format.line_spacing = Pt(1)

    spacer(doc, 40)
    t = doc.add_table(rows=1, cols=1)
    K.no_table_borders(t)
    K.table_width_pct(t, 100)
    K.table_cell_margins(t, top=200, left=220, bottom=200, right=220)
    c = t.cell(0, 0)
    K.shade(c, accent)
    c.text = ""
    p1 = c.paragraphs[0]
    K.pfmt(p1, before=0, after=2)
    K.run(p1, number.upper(), size=9.0, bold=True, colour=T.WHITE, spacing=48)
    p2 = c.add_paragraph()
    K.pfmt(p2, before=0, after=6)
    K.run(p2, title, size=21.0, bold=True, colour=T.WHITE)
    if blurb:
        p3 = c.add_paragraph()
        K.pfmt(p3, before=0, after=0, line=1.20)
        K.run(p3, blurb, size=9.5, colour="E6EDF5")
    spacer(doc, 10)
    return t


def h_section(doc, number, title, accent, page_break=False, kicker=None):
    """Numbered section opener: rule, kicker, large title. Maps to Heading 1."""
    if page_break:
        pb = doc.add_paragraph()
        K.pfmt(pb, before=0, after=0, page_break_before=True)
        pb.paragraph_format.line_spacing = Pt(1)

    if kicker:
        pk = doc.add_paragraph()
        K.pfmt(pk, before=10, after=1, keep_next=True)
        K.run(pk, kicker.upper(), size=7.5, bold=True, colour=accent, spacing=36)

    p = doc.add_paragraph(style="Heading 1")
    K.pfmt(p, before=2 if kicker else 13, after=4, keep_next=True, line=1.02)
    K.para_borders(p, bottom=(10, accent, 5))
    if number:
        K.run(p, str(number) + "  ", size=T.SIZE_H2, bold=True, colour=accent)
    K.run(p, title, size=T.SIZE_H2, bold=True, colour=T.NAVY)
    return p


def h_sub(doc, title, accent=None, number=None):
    p = doc.add_paragraph(style="Heading 2")
    K.pfmt(p, before=10, after=3, keep_next=True, line=1.04)
    if number:
        K.run(
            p, str(number) + "  ", size=T.SIZE_H3, bold=True, colour=accent or T.STEEL
        )
    emit_inline(p, title, size=T.SIZE_H3, colour=T.NAVY, base_bold=True)
    return p


def h_minor(doc, title):
    p = doc.add_paragraph(style="Heading 3")
    K.pfmt(p, before=8, after=2, keep_next=True)
    emit_inline(p, title, size=T.SIZE_H4, colour=T.BLUE, base_bold=True)
    return p


def eyebrow(doc, text, colour=T.GREY, before=8, after=2):
    p = doc.add_paragraph()
    K.pfmt(p, before=before, after=after, keep_next=True)
    K.run(p, text.upper(), size=7.5, bold=True, colour=colour, spacing=32)
    return p


# ------------------------------------------------------------------- callouts
CALLOUT_KINDS = {
    "note": (T.BG_TINT, T.STEEL, "NOTE"),
    "insight": (T.BG_PAPER, T.NAVY, "IN PRACTICE"),
    "warning": (T.GOLD_PALE, T.GOLD, "TAKE CARE"),
    "risk": (T.RED_PALE, T.RED, "OPEN RISK"),
    "audit": (T.OCHRE_PALE, T.OCHRE, "AUDIT FINDING"),
    "rule": (T.PLUM_PALE, T.PLUM, "RULE"),
    "good": (T.GREEN_PALE, T.GREEN, "CONFIRMED"),
    "quote": (T.WHITE, T.NAVY, None),
}


def classify_quote(blocks):
    """Choose a callout treatment from the language of the block quote."""
    txt = " ".join(MD.plain(b.get("text", "")) for b in blocks if b["t"] == "p")
    txt += " ".join(
        MD.plain(" ".join(r))
        for b in blocks
        if b["t"] == "table"
        for r in [b["header"]]
    )
    low = txt.lower()
    if "⚠" in txt or "unresolved" in low or "not buildable" in low:
        return "warning"
    if "audit finding" in low or "finding " in low[:60] or low.startswith("audit"):
        return "audit"
    if "risk" in low[:80] or "must not" in low or "never" in low[:60]:
        return "risk"
    if low.startswith("rule") or "rg-" in low[:40] or "reciprocity" in low:
        return "rule"
    if "confirmed" in low[:40] or "measured" in low[:40]:
        return "good"
    return "note"


def callout(
    doc, blocks_or_text, kind="note", accent=None, title=None, render_children=None
):
    """Single-cell shaded panel with a coloured left spine — the house text box."""
    fill, spine, default_label = CALLOUT_KINDS.get(kind, CALLOUT_KINDS["note"])
    spine = accent or spine
    label = title if title is not None else default_label

    t = doc.add_table(rows=1, cols=1)
    K.no_table_borders(t)
    K.table_width_pct(t, 100)
    K.table_cell_margins(t, top=90, left=150, bottom=95, right=140)
    c = t.cell(0, 0)
    K.shade(c, fill)
    K.cell_borders(
        c, left=(24, spine), top=(4, fill), bottom=(4, fill), right=(4, fill)
    )
    # clear the auto paragraph
    c.paragraphs[0]._p.getparent().remove(c.paragraphs[0]._p)

    if label:
        pl = c.add_paragraph()
        K.pfmt(pl, before=0, after=3, keep_next=True)
        K.run(pl, label, size=7.5, bold=True, colour=spine, spacing=34)

    if isinstance(blocks_or_text, str):
        p = c.add_paragraph()
        K.pfmt(p, before=0, after=0, line=1.16)
        emit_inline(p, blocks_or_text, size=T.SIZE_BODY, colour=T.INK_SOFT)
    else:
        if render_children is None:
            for b in blocks_or_text:
                if b["t"] == "p":
                    p = c.add_paragraph()
                    K.pfmt(p, before=0, after=4, line=1.16)
                    emit_inline(p, b["text"], size=T.SIZE_BODY, colour=T.INK_SOFT)
        else:
            render_children(c)
    spacer(doc, 6)
    return t


def pull_quote(doc, text, accent, attribution=None):
    t = doc.add_table(rows=1, cols=1)
    K.no_table_borders(t)
    K.table_width_pct(t, 100)
    K.table_cell_margins(t, top=110, left=170, bottom=110, right=170)
    c = t.cell(0, 0)
    K.shade(c, T.BG_PAPER)
    K.cell_borders(
        c,
        left=(28, accent),
        top=(4, T.BG_PAPER),
        bottom=(4, T.BG_PAPER),
        right=(4, T.BG_PAPER),
    )
    c.paragraphs[0]._p.getparent().remove(c.paragraphs[0]._p)
    p = c.add_paragraph()
    K.pfmt(p, before=0, after=0, line=1.20)
    emit_inline(p, text, size=11.5, colour=T.NAVY)
    if attribution:
        pa = c.add_paragraph()
        K.pfmt(pa, before=4, after=0)
        K.run(pa, attribution, size=8.0, colour=T.GREY, italic=True)
    spacer(doc, 6)
    return t


# ---------------------------------------------------------------- code panel
def code_panel(doc, lines, title=None, accent=T.NAVY, max_width_chars=104):
    t = doc.add_table(rows=1, cols=1)
    K.no_table_borders(t)
    K.table_width_pct(t, 100)
    K.table_cell_margins(t, top=90, left=140, bottom=90, right=110)
    c = t.cell(0, 0)
    K.shade(c, T.BG_PAPER)
    K.cell_borders(
        c,
        left=(20, accent),
        top=(4, T.RULE_SOFT),
        bottom=(4, T.RULE_SOFT),
        right=(4, T.RULE_SOFT),
    )
    c.paragraphs[0]._p.getparent().remove(c.paragraphs[0]._p)
    if title:
        pt = c.add_paragraph()
        K.pfmt(pt, before=0, after=4, keep_next=True)
        K.run(pt, title.upper(), size=7.5, bold=True, colour=accent, spacing=32)
    longest = max([len(l) for l in lines] or [0])
    size = 7.6 if longest <= 88 else (7.0 if longest <= 104 else 6.5)
    for line in lines:
        p = c.add_paragraph()
        K.pfmt(p, before=0, after=0, line=1.0, keep_lines=True)
        p.paragraph_format.line_spacing = 1.0
        K.run(
            p,
            line if line.strip() else " ",
            size=size,
            font=T.FONT_MONO,
            colour=T.INK_SOFT,
        )
    spacer(doc, 6)
    return t


# -------------------------------------------------------------------- tables
def _col_kind(header_text):
    h = MD.plain(header_text).strip().lower()
    if h in ID_HEADERS or h.endswith(" id") or h == "#":
        return "id"
    if any(h == n or h.startswith(n) for n in NARROW_HEADERS):
        return "narrow"
    return "text"


# ------------------------------------------------- real Calibri text metrics
# Column floors computed from character counts break mid-word on wide strings
# ("Benchmark" is 9 characters but far wider than nine average ones). These
# helpers measure the actual glyph advance in the actual face.
_FONT_CACHE = {}
_WIDTH_CACHE = {}
_FONT_FILES = {
    False: r"C:\Windows\Fonts\calibri.ttf",
    True: r"C:\Windows\Fonts\calibrib.ttf",
}


def _font(size_pt, bold=False):
    key = (round(size_pt, 1), bold)
    if key not in _FONT_CACHE:
        try:
            from PIL import ImageFont

            _FONT_CACHE[key] = ImageFont.truetype(
                _FONT_FILES[bold], int(round(size_pt * 4))
            )  # 4x for precision
        except Exception:
            _FONT_CACHE[key] = None
    return _FONT_CACHE[key]


def text_mm(s, size_pt=T.SIZE_BODY, bold=False):
    """Rendered width of a string in millimetres at the given point size."""
    s = MD.plain(s)
    if not s:
        return 0.0
    key = (s, round(size_pt, 1), bold)
    if key in _WIDTH_CACHE:
        return _WIDTH_CACHE[key]
    f = _font(size_pt, bold)
    if f is None:
        w = len(s) * size_pt * 0.172
    else:
        w = f.getlength(s) / 4.0 * 25.4 / 72.0  # 4x px -> pt -> mm
    _WIDTH_CACHE[key] = w
    return w


def _longest_word(strings):
    n = 0
    for s in strings:
        for w in re.split(r"[\s/]+", MD.plain(s)):
            n = max(n, len(w))
    return n


def _widest_word_mm(strings, size_pt, bold=False):
    w = 0.0
    for s in strings:
        for tok in re.split(r"[\s]+", MD.plain(s)):
            if tok:
                w = max(w, text_mm(tok, size_pt, bold))
    return w


def _weights(header, rows, align, total_mm=None, size=T.SIZE_TABLE):
    """Column widths in mm, converted to fractions.

    Sized in millimetres rather than abstract weights so that a hard floor
    can be enforced: no column may be narrower than its longest unbreakable
    word plus cell padding. Squeezing 'Edition' into three stacked lines is
    the classic failure of proportional-only allocation.
    """
    n = len(header)
    total_mm = total_mm or T.CONTENT_W_MM
    kinds = [_col_kind(h) for h in header]
    cpm = 0.172 * size  # mean advance, used for the *desired* width
    pad = 3.2  # left + right cell padding in mm

    desired, floors = [], []
    for i in range(n):
        cells = [r[i] for r in rows[:80] if i < len(r)]
        samples = sorted(len(MD.plain(c)) for c in cells) or [1]
        avg = sum(samples) / float(len(samples))
        p85 = samples[min(len(samples) - 1, int(0.85 * len(samples)))]
        want = 0.45 * avg + 0.55 * min(p85, 72)
        want = max(want, len(MD.plain(header[i])) * 0.70, 4.0)
        if kinds[i] == "id":
            want = min(want, 13.0)
        elif kinds[i] == "narrow":
            want = min(want, 15.0)
        desired.append(want * cpm + pad)

        # hard floor: the widest single unbreakable word must fit, measured in
        # the real face — bold and 0.4 pt smaller in the header row.
        hdr_w = _widest_word_mm([header[i]], size - 0.4, bold=True)
        cell_w = _widest_word_mm(cells[:80], size, bold=(i == 0))
        floors.append(
            min(max(hdr_w, min(cell_w, 34.0)) + pad + 0.8, total_mm / n * 1.9, 46.0)
        )

    # scale desired to the available width
    s = sum(desired) or 1.0
    widths = [d * total_mm / s for d in desired]

    # raise anything under its floor, and reclaim from the widest columns
    for _ in range(6):
        debt = 0.0
        for i in range(n):
            if widths[i] < floors[i]:
                debt += floors[i] - widths[i]
                widths[i] = floors[i]
        if debt <= 0.01:
            break
        donors = [i for i in range(n) if widths[i] > floors[i] + 2.0]
        pool = sum(widths[i] - floors[i] for i in donors) or 1.0
        if not donors:
            break
        for i in donors:
            widths[i] -= debt * (widths[i] - floors[i]) / pool

    s = sum(widths) or 1.0
    return [w / s for w in widths], kinds


PRI_RE = re.compile(r"\bP([0-3])\b")
CLS_RE = re.compile(r"^\W*\*{0,2}([HASC])\*{0,2}\W*$")


def table(
    doc,
    header,
    rows,
    align=None,
    accent=T.NAVY,
    zebra=True,
    first_col_bold=True,
    size=None,
    caption=None,
    max_rows=None,
    note=None,
    compact=False,
):
    """The house table.

    Navy header that repeats on every page, hairline interior rules, zebra
    banding, semantic colour on priority and rule-class cells, identifier
    columns set in the mono face.
    """
    if not header:
        return None
    ncol = len(header)
    align = align or ["left"] * ncol
    truncated = 0
    if max_rows and len(rows) > max_rows:
        truncated = len(rows) - max_rows
        rows = rows[:max_rows]

    if size is None:
        size = T.SIZE_TABLE if ncol <= 6 else T.SIZE_TABLE_DENSE
    if ncol >= 9:
        size = 7.6

    weights, kinds = _weights(header, rows, align, T.CONTENT_W_MM, size)

    t = doc.add_table(rows=1, cols=ncol)
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    K.table_layout_fixed(t)
    K.table_width_pct(t, 100)
    K.table_borders(t, sz=0, colour=T.WHITE, inside_sz=4, inside_colour=T.RULE_SOFT)
    K.table_cell_margins(
        t, top=46 if compact else 58, left=76, bottom=46 if compact else 58, right=76
    )

    usable = T.CONTENT_W_MM
    for i, c in enumerate(t.columns):
        c.width = Mm(usable * weights[i])

    # header row
    hr = t.rows[0]
    K.repeat_header(hr)
    K.cant_split(hr)
    for i, h in enumerate(header):
        cell = hr.cells[i]
        cell.width = Mm(usable * weights[i])
        K.shade(cell, accent)
        K.cell_valign(cell, "center")
        K.cell_borders(
            cell,
            bottom=(8, accent),
            top=(8, accent),
            left=(2, accent),
            right=(2, accent),
        )
        p = cell.paragraphs[0]
        K.pfmt(
            p,
            before=0,
            after=0,
            line=1.06,
            align=ALIGN.get(align[i], WD_ALIGN_PARAGRAPH.LEFT),
        )
        K.run(p, MD.plain(h), size=size - 0.4, bold=True, colour=T.WHITE)

    for ri, r in enumerate(rows):
        row = t.add_row()
        K.cant_split(row)
        band = zebra and (ri % 2 == 1)
        for i in range(ncol):
            cell = row.cells[i]
            cell.width = Mm(usable * weights[i])
            K.cell_valign(cell, "top")
            txt = r[i] if i < len(r) else ""
            plain = MD.plain(txt)

            fill = T.BG_PAPER if band else T.WHITE
            fg = T.INK
            bold = first_col_bold and i == 0

            hdr_l = MD.plain(header[i]).strip().lower()
            if hdr_l in ("pri", "priority") and PRI_RE.search(plain):
                pr = "P" + PRI_RE.search(plain).group(1)
                fill = T.PRIORITY_PALE[pr]
                fg = T.PRIORITY[pr]
                bold = True
            elif hdr_l == "class" and CLS_RE.match(plain):
                cl = CLS_RE.match(plain).group(1)
                fill = T.BG_PAPER if band else T.WHITE
                fg = T.RULE_CLASS[cl]
                bold = True
            elif hdr_l == "layer" and re.match(r"^L[1-6]", plain):
                fg = T.LAYER_COLOUR.get(plain[:2], T.INK)
                bold = True

            K.shade(cell, fill)
            K.cell_borders(
                cell, bottom=(3, T.RULE_SOFT), left=(2, fill), right=(2, fill)
            )
            p = cell.paragraphs[0]
            K.pfmt(
                p,
                before=0,
                after=0,
                line=1.10,
                align=ALIGN.get(align[i], WD_ALIGN_PARAGRAPH.LEFT),
            )
            if kinds[i] == "id" and plain:
                K.run(
                    p,
                    plain,
                    size=size - 0.6,
                    bold=True,
                    font=T.FONT_MONO,
                    colour=accent,
                )
            else:
                emit_inline(p, txt, size=size, colour=fg, base_bold=bold)

    if truncated:
        row = t.add_row()
        cell = row.cells[0]
        K.shade(cell, T.BG_TINT)
        p = cell.paragraphs[0]
        K.pfmt(p, before=0, after=0)
        K.run(
            p,
            "… and %d further row%s — see the source specification"
            % (truncated, "" if truncated == 1 else "s"),
            size=size - 0.6,
            italic=True,
            colour=T.GREY,
        )
        for i in range(1, ncol):
            K.shade(row.cells[i], T.BG_TINT)

    if note:
        pn = doc.add_paragraph()
        K.pfmt(pn, before=3, after=2)
        K.run(pn, note, size=T.SIZE_SMALL, italic=True, colour=T.GREY)
    if caption:
        table_caption(doc, caption)
    else:
        spacer(doc, 6)
    return t


def table_caption(doc, text, prefix="Table"):
    p = doc.add_paragraph(style="Caption")
    K.pfmt(p, before=3, after=8)
    K.run(p, prefix + " ", size=T.SIZE_CAPTION, bold=True, colour=T.GREY)
    K.add_field(
        p,
        " SEQ %s \\* ARABIC " % prefix,
        "1",
        size=T.SIZE_CAPTION,
        bold=True,
        colour=T.GREY,
    )
    K.run(p, "  ·  ", size=T.SIZE_CAPTION, colour=T.RULE)
    K.run(p, text, size=T.SIZE_CAPTION, colour=T.GREY)
    return p


# ------------------------------------------------------------------- exhibits
def exhibit(
    doc,
    image_path,
    caption,
    accent=T.NAVY,
    width_mm=None,
    source=None,
    keep_with_caption=True,
):
    """Insert a generated exhibit with a numbered, field-based caption."""
    if not image_path or not os.path.isfile(image_path):
        return None
    p = doc.add_paragraph()
    K.pfmt(
        p, before=7, after=2, align=WD_ALIGN_PARAGRAPH.LEFT, keep_next=keep_with_caption
    )
    r = p.add_run()
    r.add_picture(image_path, width=Mm(width_mm or T.CONTENT_W_MM))

    cp = doc.add_paragraph(style="Caption")
    K.pfmt(cp, before=1, after=9)
    K.para_borders(cp, top=(6, accent, 3))
    K.run(cp, "  Exhibit ", size=T.SIZE_CAPTION, bold=True, colour=accent)
    K.add_field(
        cp,
        " SEQ Exhibit \\* ARABIC ",
        "1",
        size=T.SIZE_CAPTION,
        bold=True,
        colour=accent,
    )
    K.run(cp, "  ·  ", size=T.SIZE_CAPTION, colour=T.RULE)
    K.run(cp, caption, size=T.SIZE_CAPTION, colour=T.GREY)
    if source:
        K.run(cp, "   " + source, size=T.SIZE_MICRO, italic=True, colour=T.GREY_LIGHT)
    return p


# ----------------------------------------------------------------- KPI strip
def kpi_strip(doc, items, accent=T.NAVY, cols=None):
    """Row of headline figures — used on openers and summary pages."""
    items = [i for i in items if i]
    if not items:
        return None
    cols = cols or len(items)
    t = doc.add_table(rows=1, cols=cols)
    K.no_table_borders(t)
    K.table_layout_fixed(t)
    K.table_width_pct(t, 100)
    K.table_cell_margins(t, top=70, left=90, bottom=70, right=70)
    for i in range(cols):
        t.columns[i].width = Mm(T.CONTENT_W_MM / cols)
    for i, (value, label) in enumerate(items[:cols]):
        c = t.cell(0, i)
        c.width = Mm(T.CONTENT_W_MM / cols)
        K.shade(c, T.BG_TINT)
        K.cell_borders(
            c,
            left=(20, accent),
            top=(6, T.WHITE),
            bottom=(6, T.WHITE),
            right=(6, T.WHITE),
        )
        c.paragraphs[0]._p.getparent().remove(c.paragraphs[0]._p)
        p1 = c.add_paragraph()
        K.pfmt(p1, before=0, after=0, line=1.0)
        K.run(p1, str(value), size=16.0, bold=True, colour=T.NAVY)
        p2 = c.add_paragraph()
        K.pfmt(p2, before=0, after=0, line=1.05)
        K.run(p2, label.upper(), size=7.0, colour=T.GREY, spacing=14)
    spacer(doc, 8)
    return t


# ------------------------------------------------------------ definition list
def definition_rows(
    doc,
    pairs,
    accent=T.NAVY,
    label_mm=52,
    zebra=True,
    label_colour=None,
    keep_together=False,
):
    """Two-column key/value block used for identity and control panels.

    `keep_together` binds every row to the next so Word moves the whole block
    rather than leaving one orphaned row at the top of a page. Use it on short
    blocks; on a long one it will push a large gap ahead of itself.
    """
    pairs = [(k, v) for k, v in pairs if str(v).strip()]
    if not pairs:
        return None
    t = doc.add_table(rows=0, cols=2)
    K.table_layout_fixed(t)
    K.table_width_pct(t, 100)
    K.no_table_borders(t)
    K.table_cell_margins(t, top=48, left=86, bottom=48, right=86)
    for i, (k, v) in enumerate(pairs):
        row = t.add_row()
        K.cant_split(row)
        c0, c1 = row.cells
        c0.width = Mm(label_mm)
        c1.width = Mm(T.CONTENT_W_MM - label_mm)
        fill = T.BG_PAPER if (zebra and i % 2 == 1) else T.WHITE
        for c in (c0, c1):
            K.shade(c, fill)
            K.cell_valign(c, "top")
            K.cell_borders(c, bottom=(3, T.RULE_SOFT))
        hold = keep_together and i < len(pairs) - 1
        p0 = c0.paragraphs[0]
        K.pfmt(p0, before=0, after=0, line=1.10, keep_next=hold)
        K.run(p0, k, size=T.SIZE_BODY, bold=True, colour=label_colour or T.INK_SOFT)
        p1 = c1.paragraphs[0]
        K.pfmt(p1, before=0, after=0, line=1.10, keep_next=hold)
        emit_inline(p1, str(v), size=T.SIZE_BODY, colour=T.INK)
    spacer(doc, 6)
    return t


# ------------------------------------------------------------------- bullets
def bullets(doc, items, accent=T.NAVY, size=T.SIZE_BODY, glyph="▪", indent=12, after=3):
    for it in items:
        p = doc.add_paragraph()
        K.pfmt(
            p, before=0, after=after, line=1.14, left_indent=indent + 10, first_line=-10
        )
        K.run(p, glyph + "  ", size=size - 1.5, colour=accent, bold=True)
        emit_inline(p, it, size=size, colour=T.INK)
    return doc


def numbered(doc, items, accent=T.NAVY, size=T.SIZE_BODY, indent=12, after=3):
    for i, it in enumerate(items, start=1):
        p = doc.add_paragraph()
        K.pfmt(
            p, before=0, after=after, line=1.14, left_indent=indent + 14, first_line=-14
        )
        K.run(p, "%d  " % i, size=size, colour=accent, bold=True)
        emit_inline(p, it, size=size, colour=T.INK)
    return doc


# ------------------------------------------------------ generic block driver
def render_blocks(
    doc,
    blocks,
    accent=T.NAVY,
    table_max_rows=None,
    heading_offset=0,
    skip_first_hr=True,
    code_title=None,
    quote_as_callout=True,
    compact_tables=False,
):
    """Render an arbitrary run of parsed blocks with house styling."""
    seen_content = False
    for b in blocks:
        t = b["t"]
        if t == "hr":
            if seen_content:
                hairline(doc, T.RULE_SOFT, before=4, after=6, size=4)
            continue
        seen_content = True
        if t == "h":
            lvl = b["level"] + heading_offset
            if lvl <= 3:
                h_sub(doc, b["text"], accent=accent)
            else:
                h_minor(doc, b["text"])
        elif t == "p":
            body(doc, b["text"])
        elif t == "table":
            table(
                doc,
                b["header"],
                b["rows"],
                align=b.get("align"),
                accent=accent,
                max_rows=table_max_rows,
                compact=compact_tables,
            )
        elif t == "quote":
            if quote_as_callout:
                kind = classify_quote(b["children"])
                callout(
                    doc,
                    None,
                    kind=kind,
                    render_children=lambda cell, _bl=b["children"]: _render_into_cell(
                        cell, _bl, accent
                    ),
                )
            else:
                for c in b["children"]:
                    render_blocks(doc, [c], accent=accent)
        elif t == "code":
            code_panel(doc, b["lines"], title=code_title, accent=accent)
        elif t == "list":
            if b["ordered"]:
                numbered(doc, [i["text"] for i in b["items"]], accent=accent)
            else:
                bullets(doc, [i["text"] for i in b["items"]], accent=accent)
    return doc


def _render_into_cell(cell, blocks, accent):
    """Render blocks inside a callout cell — supports nested tables and lists."""
    for b in blocks:
        t = b["t"]
        if t == "p":
            p = cell.add_paragraph()
            K.pfmt(p, before=0, after=4, line=1.16)
            emit_inline(p, b["text"], size=T.SIZE_BODY, colour=T.INK_SOFT)
        elif t == "list":
            for i, it in enumerate(b["items"], start=1):
                p = cell.add_paragraph()
                K.pfmt(p, before=0, after=3, line=1.14, left_indent=14, first_line=-14)
                K.run(
                    p,
                    ("%d  " % i) if b["ordered"] else "▪  ",
                    size=T.SIZE_BODY - (0 if b["ordered"] else 1.5),
                    bold=True,
                    colour=accent,
                )
                emit_inline(p, it["text"], size=T.SIZE_BODY, colour=T.INK_SOFT)
        elif t == "table":
            _mini_table(cell, b, accent)
        elif t == "code":
            for line in b["lines"]:
                p = cell.add_paragraph()
                K.pfmt(p, before=0, after=0, line=1.0)
                K.run(p, line or " ", size=7.4, font=T.FONT_MONO, colour=T.INK_SOFT)
        elif t == "h":
            p = cell.add_paragraph()
            K.pfmt(p, before=4, after=2, keep_next=True)
            emit_inline(p, b["text"], size=T.SIZE_BODY, colour=T.NAVY, base_bold=True)


def _mini_table(cell, b, accent):
    """A compact table nested inside a callout panel."""
    ncol = len(b["header"])
    t = cell.add_table(rows=1, cols=ncol)
    K.table_layout_fixed(t)
    K.table_width_pct(t, 100)
    K.table_borders(t, sz=0, colour=T.WHITE, inside_sz=3, inside_colour=T.RULE_SOFT)
    K.table_cell_margins(t, top=36, left=60, bottom=36, right=60)
    weights, kinds = _weights(
        b["header"], b["rows"], b.get("align"), T.CONTENT_W_MM - 22, 8.3
    )
    avail = T.CONTENT_W_MM - 22
    for i, h in enumerate(b["header"]):
        c = t.rows[0].cells[i]
        c.width = Mm(avail * weights[i])
        K.shade(c, accent)
        p = c.paragraphs[0]
        K.pfmt(p, before=0, after=0, line=1.05)
        K.run(p, MD.plain(h), size=8.0, bold=True, colour=T.WHITE)
    for ri, r in enumerate(b["rows"]):
        row = t.add_row()
        for i in range(ncol):
            c = row.cells[i]
            c.width = Mm(avail * weights[i])
            K.shade(c, T.WHITE if ri % 2 == 0 else T.BG_PAPER_2)
            p = c.paragraphs[0]
            K.pfmt(p, before=0, after=0, line=1.08)
            emit_inline(
                p,
                r[i] if i < len(r) else "",
                size=8.3,
                colour=T.INK,
                base_bold=(i == 0),
            )
    cell.add_paragraph()
