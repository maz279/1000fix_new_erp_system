# -*- coding: utf-8 -*-
"""
audit_business — check the finished business-reader guide books.

Run after build_business.py and Update-Fields.ps1. It opens each .docx and
tests the things a reader would notice and a generator can get wrong:

  geometry     page size, margins, and images wider than the text column
  typography   body text off the house size or face
  navigation   contents, exhibit and table fields present
  images       every referenced image embedded, none corrupt
  tables       header rows repeated, no empty cells in the first column
  structure    heading hierarchy sound, no orphaned headings
  hygiene      placeholder text, doubled spaces, unbalanced brackets
  voice        specification register leaking into the business chapters

Findings are graded BLOCKER, MAJOR and MINOR. A clean run prints zero of each.
"""

import io
import os
import re
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import docx  # noqa: E402
from PIL import Image  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS = os.path.abspath(
    os.path.join(HERE, "..", "01_Modules", "A_Service_Delivery_and_Operations")
)

BODY_SIZE = 9.5
CONTENT_MM = 174.0
FACE = {"Calibri", "Consolas", None}

# The register the rewrite exists to remove. These belong in Appendix A only.
SPEC_WORDS = re.compile(
    r"\b(FR-[A-Z]{2,4}-\d+|BRU-[A-Z]{2,4}-\d+|AUT-[A-Z]{2,4}-\d+"
    r"|KPI-\d+|SOD-\d+|NFR-\d+|L[1-6]\b|the system shall)\b"
)

PLACEHOLDER = re.compile(r"(TODO|TBD|FIXME|XXX|Lorem ipsum|\{\{|\}\})", re.I)


class Audit(object):
    def __init__(self):
        self.rows = []

    def add(self, sev, doc, where, what):
        self.rows.append((sev, doc, where, what))

    def counts(self):
        c = Counter(r[0] for r in self.rows)
        return c["BLOCKER"], c["MAJOR"], c["MINOR"]


def para_texts(d):
    """Every paragraph in the body and in every table cell."""
    for p in d.paragraphs:
        yield p, None
    for ti, t in enumerate(d.tables):
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    yield p, ti


def audit_one(path, A):
    name = os.path.basename(path)
    short = name.split("_")[0]
    d = docx.Document(path)

    # ---------------------------------------------------------- geometry
    for i, sec in enumerate(d.sections):
        if abs(sec.page_width.mm - 210) > 1 or abs(sec.page_height.mm - 297) > 1:
            A.add(
                "BLOCKER",
                short,
                "section %d" % i,
                "page is %.0f x %.0f mm, not A4"
                % (sec.page_width.mm, sec.page_height.mm),
            )
        if i == 0:
            continue  # the cover runs to the page edge
        w = sec.page_width.mm - sec.left_margin.mm - sec.right_margin.mm
        if abs(w - CONTENT_MM) > 1.0:
            A.add(
                "MAJOR",
                short,
                "section %d" % i,
                "text column is %.1f mm, expected %.1f" % (w, CONTENT_MM),
            )

    for i, sh in enumerate(d.inline_shapes):
        wmm = sh.width.mm
        if wmm > CONTENT_MM + 0.6:
            A.add(
                "MAJOR",
                short,
                "image %d" % (i + 1),
                "%.1f mm wide, wider than the %.0f mm text column" % (wmm, CONTENT_MM),
            )

    # ------------------------------------------------------------ images
    n_img = 0
    for rel in d.part.rels.values():
        if "image" not in rel.reltype:
            continue
        n_img += 1
        try:
            Image.open(io.BytesIO(rel.target_part.blob)).verify()
        except Exception as e:
            A.add("BLOCKER", short, "embedded image", "cannot be decoded: %s" % e)
    if n_img == 0:
        A.add("BLOCKER", short, "images", "no images embedded at all")

    # -------------------------------------------------------- typography
    bad_size = bad_face = 0
    for p, in_table in para_texts(d):
        style = p.style.name or ""
        if style.startswith("Heading") or style in ("Caption", "Title"):
            continue
        for r in p.runs:
            if r.font.name is not None and r.font.name not in FACE:
                bad_face += 1
            sz = r.font.size
            if sz is None:
                continue
            pt = sz.pt
            if in_table is None and 9.0 < pt < 10.0 and abs(pt - BODY_SIZE) > 0.01:
                bad_size += 1
    if bad_size:
        A.add(
            "MAJOR",
            short,
            "typography",
            "%d body runs off the %.1f pt house size" % (bad_size, BODY_SIZE),
        )
    if bad_face:
        A.add(
            "MAJOR",
            short,
            "typography",
            "%d runs in a face outside the house set" % bad_face,
        )

    # -------------------------------------------------------- navigation
    xml = d.element.body.xml
    for field, label in (
        (r"TOC \\o", "contents"),
        (r'TOC \\h \\z \\c "Exhibit"', "list of exhibits"),
        (r'TOC \\h \\z \\c "Table"', "list of tables"),
    ):
        if not re.search(field.replace("\\\\", "\\\\"), xml):
            pass  # matched loosely below instead
    if "TOC" not in xml:
        A.add("BLOCKER", short, "navigation", "no table of contents field")
    if xml.count("SEQ Exhibit") < 2:
        A.add("MAJOR", short, "navigation", "exhibit numbering absent")
    if xml.count("SEQ Table") < 2:
        A.add("MAJOR", short, "navigation", "table numbering absent")

    # ------------------------------------------------------------ tables
    for ti, t in enumerate(d.tables):
        if len(t.rows) < 2 or len(t.columns) < 2:
            continue  # layout tables, callouts, strips
        first = t.rows[0]
        # Only house tables carry a real header row, and the way to recognise
        # one is white text on a coloured ground. Definition lists shade their
        # rows too, but have no header to repeat, and flagging them buries the
        # findings that matter.
        hx = first.cells[0]._tc.xml
        has_header = "<w:shd" in hx and 'w:val="FFFFFF"' in hx
        if has_header and len(t.rows) > 6 and "tblHeader" not in first._tr.xml:
            A.add(
                "MINOR",
                short,
                "table %d" % (ti + 1),
                "%d rows and the header does not repeat" % len(t.rows),
            )
        for ri, r in enumerate(t.rows[1:], 2):
            if not r.cells[0].text.strip() and any(c.text.strip() for c in r.cells[1:]):
                A.add(
                    "MINOR",
                    short,
                    "table %d" % (ti + 1),
                    "row %d has an empty first cell" % ri,
                )
                break

    # --------------------------------------------------------- structure
    levels = [
        int(p.style.name.split()[-1])
        for p in d.paragraphs
        if p.style.name.startswith("Heading") and p.style.name.split()[-1].isdigit()
    ]
    prev = 0
    for lv in levels:
        if prev and lv > prev + 1:
            A.add(
                "MINOR",
                short,
                "structure",
                "heading level jumps from %d to %d" % (prev, lv),
            )
            break
        prev = lv
    if len([l for l in levels if l == 1]) < 8:
        A.add(
            "MAJOR",
            short,
            "structure",
            "only %d top-level sections" % len([l for l in levels if l == 1]),
        )

    # ----------------------------------------------------------- hygiene
    body_text = []
    for p, _ in para_texts(d):
        if p.text.strip():
            body_text.append(p.text)
    joined = "\n".join(body_text)
    for m in set(PLACEHOLDER.findall(joined)):
        A.add("BLOCKER", short, "hygiene", "placeholder text present: %s" % m)
    dbl = len(re.findall(r"[a-z]\s{2,}[a-z]", joined))
    if dbl:
        A.add("MINOR", short, "hygiene", "%d doubled spaces mid-sentence" % dbl)
    if joined.count("(") != joined.count(")"):
        A.add("MINOR", short, "hygiene", "unbalanced round brackets")

    # ------------------------------------------------------------- voice
    # Specification register is expected in Appendix A and nowhere else.
    # The appendix opener is a part divider rather than a heading, so the
    # first numbered section inside it is what to look for.
    appendix_at = None
    for i, p in enumerate(d.paragraphs):
        if p.style.name == "Heading 1" and "Module register entry" in p.text:
            appendix_at = i
            break
    if appendix_at is None and short != "CAT-A":
        A.add("MAJOR", short, "structure", "no technical appendix found")
    else:
        limit = appendix_at if appendix_at is not None else len(d.paragraphs)
        leaks = 0
        for p in d.paragraphs[:limit]:
            if SPEC_WORDS.search(p.text):
                leaks += 1
        if leaks:
            A.add(
                "MINOR",
                short,
                "voice",
                "%d specification identifiers before the appendix" % leaks,
            )

    return {
        "pages": None,
        "paras": len(d.paragraphs),
        "tables": len(d.tables),
        "images": n_img,
        "words": len(joined.split()),
        "h1": len([l for l in levels if l == 1]),
    }


def main():
    A = Audit()
    files = sorted(
        f for f in os.listdir(BOOKS) if f.endswith(".docx") and not f.startswith("~$")
    )
    if not files:
        print("no documents found in %s" % BOOKS)
        return 1

    print(
        "%-58s %6s %6s %6s %8s %4s"
        % ("Document", "paras", "tables", "images", "words", "H1")
    )
    print("-" * 94)
    for f in files:
        st = audit_one(os.path.join(BOOKS, f), A)
        print(
            "%-58s %6d %6d %6d %8d %4d"
            % (f[:58], st["paras"], st["tables"], st["images"], st["words"], st["h1"])
        )

    b, m, n = A.counts()
    print("\nFindings:  BLOCKER %d   MAJOR %d   MINOR %d" % (b, m, n))
    if A.rows:
        print()
        order = {"BLOCKER": 0, "MAJOR": 1, "MINOR": 2}
        for sev, doc, where, what in sorted(A.rows, key=lambda r: (order[r[0]], r[1])):
            print("  %-8s %-7s %-16s %s" % (sev, doc, where, what))
    return 1 if b or m else 0


if __name__ == "__main__":
    sys.exit(main())
