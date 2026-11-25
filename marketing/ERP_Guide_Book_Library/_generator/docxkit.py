# -*- coding: utf-8 -*-
"""
docxkit — low-level OOXML helpers on top of python-docx.

python-docx exposes only a fraction of WordprocessingML. Everything the
guide-book design system needs beyond that — cell shading, per-edge borders,
repeating header rows, TOC and page-number fields, paragraph borders,
character spacing, text-box style callouts, section geometry — is
implemented here once, so the document builder stays declarative.
"""

from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.shared import Pt, Mm, RGBColor
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.section import WD_ORIENT

import theme as T


# ----------------------------------------------------------------- utilities
def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(k.replace("__", ":")), str(v))
    return e


def _get_or_add(parent, tag):
    found = parent.find(qn(tag))
    if found is None:
        found = OxmlElement(tag)
        parent.append(found)
    return found


def rgb(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# ------------------------------------------------------------------ shading
def shade(obj, fill):
    """Apply solid fill to a table cell, paragraph or run."""
    if hasattr(obj, "_tc"):
        pr = obj._tc.get_or_add_tcPr()
    elif hasattr(obj, "_p"):
        pr = obj._p.get_or_add_pPr()
    else:
        pr = obj
    old = pr.find(qn("w:shd"))
    if old is not None:
        pr.remove(old)
    pr.append(el("w:shd", w__val="clear", w__color="auto", w__fill=fill.lstrip("#")))


# ------------------------------------------------------------------ borders
_EDGES = ("top", "left", "bottom", "right")


def cell_borders(
    cell, top=None, left=None, bottom=None, right=None, inside_h=None, inside_v=None
):
    """Each edge is None (leave) or (size_eighths_pt, colour, style)."""
    tcPr = cell._tc.get_or_add_tcPr()
    old = tcPr.find(qn("w:tcBorders"))
    if old is not None:
        tcPr.remove(old)
    b = OxmlElement("w:tcBorders")
    spec = dict(zip(_EDGES, (top, left, bottom, right)))
    spec["insideH"] = inside_h
    spec["insideV"] = inside_v
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        v = spec.get(edge)
        if v is None:
            continue
        sz, col, style = (list(v) + ["single"])[:3]
        b.append(
            el(
                "w:" + edge,
                w__val=style,
                w__sz=int(sz),
                w__space="0",
                w__color=col.lstrip("#"),
            )
        )
    tcPr.append(b)


def table_borders(
    table, sz=4, colour=T.RULE, inside_sz=4, inside_colour=T.RULE_SOFT, style="single"
):
    tbl = table._tbl
    tblPr = tbl.tblPr
    old = tblPr.find(qn("w:tblBorders"))
    if old is not None:
        tblPr.remove(old)
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right"):
        b.append(
            el(
                "w:" + edge,
                w__val=style,
                w__sz=int(sz),
                w__space="0",
                w__color=colour.lstrip("#"),
            )
        )
    for edge in ("insideH", "insideV"):
        b.append(
            el(
                "w:" + edge,
                w__val=style,
                w__sz=int(inside_sz),
                w__space="0",
                w__color=inside_colour.lstrip("#"),
            )
        )
    tblPr.append(b)


def no_table_borders(table):
    tblPr = table._tbl.tblPr
    old = tblPr.find(qn("w:tblBorders"))
    if old is not None:
        tblPr.remove(old)
    b = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b.append(
            el("w:" + edge, w__val="none", w__sz="0", w__space="0", w__color="auto")
        )
    tblPr.append(b)


def para_borders(p, top=None, left=None, bottom=None, right=None):
    pPr = p._p.get_or_add_pPr()
    old = pPr.find(qn("w:pBdr"))
    if old is not None:
        pPr.remove(old)
    b = OxmlElement("w:pBdr")
    for edge, v in zip(_EDGES, (top, left, bottom, right)):
        if v is None:
            continue
        sz, col, space = (list(v) + [0])[:3]
        b.append(
            el(
                "w:" + edge,
                w__val="single",
                w__sz=int(sz),
                w__space=int(space),
                w__color=col.lstrip("#"),
            )
        )
    pPr.append(b)


# --------------------------------------------------------------- cell layout
def cell_margins(cell, top=40, left=90, bottom=40, right=90):
    """Cell padding in twips (1/20 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    old = tcPr.find(qn("w:tcMar"))
    if old is not None:
        tcPr.remove(old)
    m = OxmlElement("w:tcMar")
    for edge, v in zip(_EDGES, (top, left, bottom, right)):
        m.append(el("w:" + edge, w__w=int(v), w__type="dxa"))
    tcPr.append(m)


def table_cell_margins(table, top=40, left=90, bottom=40, right=90):
    tblPr = table._tbl.tblPr
    old = tblPr.find(qn("w:tblCellMar"))
    if old is not None:
        tblPr.remove(old)
    m = OxmlElement("w:tblCellMar")
    for edge, v in zip(_EDGES, (top, left, bottom, right)):
        m.append(el("w:" + edge, w__w=int(v), w__type="dxa"))
    tblPr.append(m)


def vmerge(cell, val="continue"):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(el("w:vMerge", w__val=val))


def cell_valign(cell, v="center"):
    cell.vertical_alignment = {
        "top": WD_ALIGN_VERTICAL.TOP,
        "center": WD_ALIGN_VERTICAL.CENTER,
        "bottom": WD_ALIGN_VERTICAL.BOTTOM,
    }[v]


def cell_text_direction(cell, val="btLr"):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(el("w:textDirection", w__val=val))


def row_height(row, mm, rule="atLeast"):
    trPr = row._tr.get_or_add_trPr()
    old = trPr.find(qn("w:trHeight"))
    if old is not None:
        trPr.remove(old)
    trPr.append(el("w:trHeight", w__val=int(mm * 56.7), w__hRule=rule))


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(el("w:tblHeader", w__val="true"))


def cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(el("w:cantSplit"))


def table_layout_fixed(table):
    tblPr = table._tbl.tblPr
    old = tblPr.find(qn("w:tblLayout"))
    if old is not None:
        tblPr.remove(old)
    tblPr.append(el("w:tblLayout", w__type="fixed"))
    table.autofit = False


def table_width_pct(table, pct=100):
    tblPr = table._tbl.tblPr
    old = tblPr.find(qn("w:tblW"))
    if old is not None:
        tblPr.remove(old)
    tblPr.append(el("w:tblW", w__w=int(pct * 50), w__type="pct"))


def table_indent(table, twips):
    tblPr = table._tbl.tblPr
    old = tblPr.find(qn("w:tblInd"))
    if old is not None:
        tblPr.remove(old)
    tblPr.append(el("w:tblInd", w__w=int(twips), w__type="dxa"))


# ------------------------------------------------------------ paragraph prop
def pfmt(
    p,
    before=0,
    after=0,
    line=None,
    align=None,
    keep_next=False,
    keep_lines=True,
    page_break_before=False,
    left_indent=None,
    right_indent=None,
    first_line=None,
    widow=True,
    contextual=False,
):
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    if line is not None:
        pf.line_spacing = line
    if align is not None:
        p.alignment = align
    pf.keep_with_next = keep_next
    pf.keep_together = keep_lines
    pf.page_break_before = page_break_before
    pf.widow_control = widow
    if left_indent is not None:
        pf.left_indent = Pt(left_indent)
    if right_indent is not None:
        pf.right_indent = Pt(right_indent)
    if first_line is not None:
        pf.first_line_indent = Pt(first_line)
    return p


def run(
    p,
    text,
    size=T.SIZE_BODY,
    bold=False,
    italic=False,
    colour=T.INK,
    font=T.FONT_BODY,
    caps=False,
    spacing=None,
    underline=False,
    strike=False,
    superscript=False,
    highlight=None,
):
    r = p.add_run(text)
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.underline = underline
    if strike:
        r.font.strike = True
    if superscript:
        r.font.superscript = True
    r.font.color.rgb = rgb(colour)
    rPr = r._r.get_or_add_rPr()
    # East-Asian + complex-script font mapping so Word never substitutes
    rf = rPr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts")
        rPr.insert(0, rf)
    rf.set(qn("w:ascii"), font)
    rf.set(qn("w:hAnsi"), font)
    rf.set(qn("w:cs"), font)
    if caps:
        rPr.append(el("w:caps", w__val="true"))
    if spacing is not None:  # letter-spacing, twentieths of a point
        rPr.append(el("w:spacing", w__val=int(spacing)))
    if highlight:
        shade(rPr, highlight)
    return r


def tab_stops(p, stops):
    """stops = [(pos_mm, 'left'|'right'|'center'|'decimal', leader or None)]"""
    pPr = p._p.get_or_add_pPr()
    old = pPr.find(qn("w:tabs"))
    if old is not None:
        pPr.remove(old)
    t = OxmlElement("w:tabs")
    for pos, kind, leader in stops:
        a = el("w:tab", w__val=kind, w__pos=int(pos * 56.7))
        if leader:
            a.set(qn("w:leader"), leader)
        t.append(a)
    pPr.append(t)


# ---------------------------------------------------------------- field code
def add_field(
    p,
    instr,
    placeholder="",
    size=T.SIZE_BODY,
    bold=False,
    colour=T.INK,
    font=T.FONT_BODY,
):
    r1 = p.add_run()
    r1.font.name = font
    r1.font.size = Pt(size)
    r1.font.bold = bold
    r1.font.color.rgb = rgb(colour)
    r1._r.append(el("w:fldChar", w__fldCharType="begin"))

    r2 = p.add_run()
    r2.font.name = font
    r2.font.size = Pt(size)
    r2.font.bold = bold
    r2.font.color.rgb = rgb(colour)
    it = OxmlElement("w:instrText")
    it.set(qn("xml:space"), "preserve")
    it.text = instr
    r2._r.append(it)

    r3 = p.add_run()
    r3._r.append(el("w:fldChar", w__fldCharType="separate"))

    r4 = p.add_run(placeholder)
    r4.font.name = font
    r4.font.size = Pt(size)
    r4.font.bold = bold
    r4.font.color.rgb = rgb(colour)

    r5 = p.add_run()
    r5._r.append(el("w:fldChar", w__fldCharType="end"))
    return p


def add_toc(p, levels="1-3", hyperlink=True):
    flags = ' \\o "%s" \\z \\u' % levels
    if hyperlink:
        flags = ' \\o "%s" \\h \\z \\u' % levels
    add_field(
        p,
        "TOC" + flags,
        "Right-click and choose Update Field to build the table of contents.",
        size=T.SIZE_BODY,
        colour=T.GREY,
    )


def add_table_of_figures(p, label="Exhibit"):
    add_field(
        p,
        ' TOC \\h \\z \\c "%s" ' % label,
        "Press Ctrl+A then F9 to build the list of %ss with page numbers."
        % label.lower(),
        size=T.SIZE_BODY,
        colour=T.GREY,
    )


def set_update_fields_on_open(doc):
    settings = doc.settings.element
    old = settings.find(qn("w:updateFields"))
    if old is not None:
        settings.remove(old)
    settings.append(el("w:updateFields", w__val="true"))


def enable_even_odd(doc, on=False):
    settings = doc.settings.element
    old = settings.find(qn("w:evenAndOddHeaders"))
    if old is not None:
        settings.remove(old)
    if on:
        settings.append(el("w:evenAndOddHeaders", w__val="true"))


# ------------------------------------------------------------------ bookmark
_BM = {"n": 1000}


def bookmark(p, name):
    _BM["n"] += 1
    bid = str(_BM["n"])
    s = el("w:bookmarkStart", w__id=bid, w__name=name)
    e = el("w:bookmarkEnd", w__id=bid)
    p._p.insert(0, s)
    p._p.append(e)
    return name


def internal_link(
    p, anchor, text, size=T.SIZE_BODY, colour=T.STEEL, bold=False, underline=False
):
    h = el("w:hyperlink", w__anchor=anchor)
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    rf = OxmlElement("w:rFonts")
    rf.set(qn("w:ascii"), T.FONT_BODY)
    rf.set(qn("w:hAnsi"), T.FONT_BODY)
    rPr.append(rf)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(int(size * 2)))
    rPr.append(sz)
    if bold:
        rPr.append(OxmlElement("w:b"))
    c = OxmlElement("w:color")
    c.set(qn("w:val"), colour.lstrip("#"))
    rPr.append(c)
    if underline:
        u = OxmlElement("w:u")
        u.set(qn("w:val"), "single")
        rPr.append(u)
    r.append(rPr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)
    h.append(r)
    p._p.append(h)


def external_link(p, url, text, size=T.SIZE_BODY, colour=T.STEEL, underline=True):
    part = p.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), r_id)
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    rf = OxmlElement("w:rFonts")
    rf.set(qn("w:ascii"), T.FONT_BODY)
    rf.set(qn("w:hAnsi"), T.FONT_BODY)
    rPr.append(rf)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(int(size * 2)))
    rPr.append(sz)
    c = OxmlElement("w:color")
    c.set(qn("w:val"), colour.lstrip("#"))
    rPr.append(c)
    if underline:
        u = OxmlElement("w:u")
        u.set(qn("w:val"), "single")
        rPr.append(u)
    r.append(rPr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)
    h.append(r)
    p._p.append(h)


# ------------------------------------------------------------------- section
def setup_section(
    sec,
    landscape=False,
    top=T.MARGIN_TOP_MM,
    bottom=T.MARGIN_BOTTOM_MM,
    left=T.MARGIN_LEFT_MM,
    right=T.MARGIN_RIGHT_MM,
    header_dist=9.0,
    footer_dist=9.0,
    gutter=0.0,
):
    if landscape:
        sec.orientation = WD_ORIENT.LANDSCAPE
        sec.page_width = Mm(T.PAGE_H_MM)
        sec.page_height = Mm(T.PAGE_W_MM)
    else:
        sec.orientation = WD_ORIENT.PORTRAIT
        sec.page_width = Mm(T.PAGE_W_MM)
        sec.page_height = Mm(T.PAGE_H_MM)
    sec.top_margin = Mm(top)
    sec.bottom_margin = Mm(bottom)
    sec.left_margin = Mm(left)
    sec.right_margin = Mm(right)
    sec.header_distance = Mm(header_dist)
    sec.footer_distance = Mm(footer_dist)
    sec.gutter = Mm(gutter)
    return sec


def restart_page_numbering(sec, start=1, fmt="decimal"):
    sectPr = sec._sectPr
    old = sectPr.find(qn("w:pgNumType"))
    if old is not None:
        sectPr.remove(old)
    sectPr.append(el("w:pgNumType", w__start=int(start), w__fmt=fmt))


def continue_page_numbering(sec, fmt="decimal"):
    sectPr = sec._sectPr
    old = sectPr.find(qn("w:pgNumType"))
    if old is not None:
        sectPr.remove(old)
    sectPr.append(el("w:pgNumType", w__fmt=fmt))


def unlink_header_footer(sec):
    sec.header.is_linked_to_previous = False
    sec.footer.is_linked_to_previous = False
    try:
        sec.first_page_header.is_linked_to_previous = False
        sec.first_page_footer.is_linked_to_previous = False
    except Exception:
        pass


def clear_container(container):
    for p in list(container.paragraphs):
        p._p.getparent().remove(p._p)
    for t in list(container.tables):
        t._tbl.getparent().remove(t._tbl)


# ------------------------------------------------------------------- styles
def install_base_styles(doc):
    """Body text at the mandated Calibri 9.5 pt; heading styles recoloured
    so Word's navigation pane and generated TOC inherit the house design."""
    st = doc.styles

    n = st["Normal"]
    n.font.name = T.FONT_BODY
    n.font.size = Pt(T.SIZE_BODY)
    n.font.color.rgb = rgb(T.INK)
    rPr = n.element.get_or_add_rPr()
    rf = _get_or_add(rPr, "w:rFonts")
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), T.FONT_BODY)
    n.paragraph_format.space_after = Pt(4)
    n.paragraph_format.space_before = Pt(0)
    n.paragraph_format.line_spacing = 1.14
    n.paragraph_format.widow_control = True

    heads = [
        ("Heading 1", T.SIZE_H2, T.NAVY, True, 14, 5),
        ("Heading 2", T.SIZE_H3, T.NAVY, True, 11, 3),
        ("Heading 3", T.SIZE_H4, T.BLUE, True, 8, 2),
        ("Heading 4", T.SIZE_BODY, T.INK_SOFT, True, 7, 2),
    ]
    for name, size, colour, bold, before, after in heads:
        try:
            s = st[name]
        except KeyError:
            continue
        s.font.name = T.FONT_BODY
        s.font.size = Pt(size)
        s.font.bold = bold
        s.font.color.rgb = rgb(colour)
        srPr = s.element.get_or_add_rPr()
        srf = _get_or_add(srPr, "w:rFonts")
        for a in ("w:ascii", "w:hAnsi", "w:cs"):
            srf.set(qn(a), T.FONT_BODY)
        s.paragraph_format.space_before = Pt(before)
        s.paragraph_format.space_after = Pt(after)
        s.paragraph_format.keep_with_next = True
        s.paragraph_format.keep_together = True
        s.paragraph_format.line_spacing = 1.05
        s.quick_style = True

    # TOC entry styles
    for i, (size, colour, bold, ind) in enumerate(
        [
            (T.SIZE_BODY, T.NAVY, True, 0),
            (T.SIZE_BODY, T.INK, False, 10),
            (T.SIZE_SMALL, T.INK_SOFT, False, 20),
        ],
        start=1,
    ):
        try:
            s = st["TOC %d" % i]
        except KeyError:
            continue
        s.font.name = T.FONT_BODY
        s.font.size = Pt(size)
        s.font.bold = bold
        s.font.color.rgb = rgb(colour)
        s.paragraph_format.left_indent = Pt(ind)
        s.paragraph_format.space_before = Pt(3 if i == 1 else 0)
        s.paragraph_format.space_after = Pt(1)

    try:
        c = st["Caption"]
        c.font.name = T.FONT_BODY
        c.font.size = Pt(T.SIZE_CAPTION)
        c.font.bold = False
        c.font.italic = False
        c.font.color.rgb = rgb(T.GREY)
    except KeyError:
        pass

    try:
        h = st["Hyperlink"]
        h.font.color.rgb = rgb(T.STEEL)
    except KeyError:
        pass


def set_doc_defaults_language(doc, lang="en-GB"):
    styles_el = doc.styles.element
    docDefaults = styles_el.find(qn("w:docDefaults"))
    if docDefaults is None:
        return
    rPrDefault = _get_or_add(docDefaults, "w:rPrDefault")
    rPr = _get_or_add(rPrDefault, "w:rPr")
    old = rPr.find(qn("w:lang"))
    if old is not None:
        rPr.remove(old)
    rPr.append(el("w:lang", w__val=lang, w__eastAsia=lang, w__bidi="ar-SA"))


def set_core_properties(doc, title, subject, keywords, comments, category_str):
    cp = doc.core_properties
    cp.title = title
    cp.subject = subject
    cp.author = "SPSL — ERP Programme Documentation Office"
    cp.last_modified_by = "SPSL — ERP Programme Documentation Office"
    cp.category = category_str
    cp.keywords = keywords
    cp.comments = comments
    cp.language = "en-GB"


def set_compat_and_zoom(doc):
    settings = doc.settings.element
    for tag, attrs in (
        ("w:zoom", {"w__percent": "100"}),
        ("w:defaultTabStop", {"w__val": "425"}),
        ("w:characterSpacingControl", {"w__val": "doNotCompress"}),
    ):
        old = settings.find(qn(tag))
        if old is not None:
            settings.remove(old)
        settings.append(el(tag, **attrs))
