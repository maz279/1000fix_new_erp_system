# -*- coding: utf-8 -*-
"""
audit — mechanical inspection of the produced Word documents.

Checks the artefacts, not the source: coverage, structure, typography,
navigation fields, image integrity, table geometry, content fidelity
against the parsed source, and text hygiene.

    python audit.py [--root DIR] [--json out.json]
"""

import argparse
import io
import json
import os
import pathlib
import re
import sys
import zipfile
from collections import Counter, OrderedDict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from docx import Document

import theme as T
import catalogue as C
import mdparse as MD

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = NS["w"]

ALLOWED_FONTS = {T.FONT_BODY, T.FONT_MONO}
A4_W_EMU = int(round(T.PAGE_W_MM * 36000))
A4_H_EMU = int(round(T.PAGE_H_MM * 36000))
CONTENT_TWIPS = int(round(T.CONTENT_W_MM * 56.6929))

SEV = ("BLOCKER", "MAJOR", "MINOR", "INFO")


class DocAudit(object):
    def __init__(self, path, spec=None):
        self.path = path
        self.name = os.path.basename(path)
        self.spec = spec
        self.findings = []
        self.stats = OrderedDict()

    def add(self, sev, code, msg):
        self.findings.append({"severity": sev, "code": code, "message": msg})

    # ------------------------------------------------------------------ run
    def run(self):
        try:
            self.z = zipfile.ZipFile(self.path)
        except Exception as e:
            self.add("BLOCKER", "A-00", "File is not a readable .docx: %s" % e)
            return self
        try:
            self.doc = Document(self.path)
        except Exception as e:
            self.add("BLOCKER", "A-00", "python-docx cannot open the file: %s" % e)
            return self
        self.xml = self.z.read("word/document.xml").decode("utf-8", "replace")

        self._geometry()
        self._typography()
        self._navigation()
        self._headers_footers()
        self._images()
        self._tables()
        self._headings()
        self._hygiene()
        self._properties()
        if self.spec is not None:
            self._fidelity()
        return self

    # ------------------------------------------------------------- checks
    def _geometry(self):
        secs = self.doc.sections
        self.stats["sections"] = len(secs)
        for i, s in enumerate(secs):
            if (
                abs(int(s.page_width) - A4_W_EMU) > 20000
                or abs(int(s.page_height) - A4_H_EMU) > 20000
            ):
                self.add(
                    "MAJOR",
                    "A-01",
                    "Section %d is not A4 (%.1f × %.1f mm)"
                    % (i, int(s.page_width) / 36000.0, int(s.page_height) / 36000.0),
                )
        body = [s for s in secs[1:]] or secs
        for i, s in enumerate(body):
            cw = int(s.page_width) - int(s.left_margin) - int(s.right_margin)
            if abs(cw / 36000.0 - T.CONTENT_W_MM) > 1.0:
                self.add(
                    "MINOR",
                    "A-02",
                    "Body section %d text column is %.1f mm, expected %.1f mm"
                    % (i + 1, cw / 36000.0, T.CONTENT_W_MM),
                )

    def _typography(self):
        fonts = Counter(re.findall(r'w:ascii="([^"]+)"', self.xml))
        self.stats["fonts"] = dict(fonts)
        bad = {f: n for f, n in fonts.items() if f not in ALLOWED_FONTS}
        if bad:
            self.add(
                "MAJOR",
                "A-10",
                "Fonts outside the house set are used: %s"
                % ", ".join("%s×%d" % (k, v) for k, v in bad.items()),
            )

        sizes = Counter(
            int(v) / 2.0 for v in re.findall(r'<w:sz w:val="(\d+)"/>', self.xml)
        )
        self.stats["sizes"] = {str(k): v for k, v in sorted(sizes.items())}
        body_runs = sizes.get(T.SIZE_BODY, 0)
        if body_runs == 0:
            self.add(
                "MAJOR",
                "A-11",
                "No run is set at the house body size " "of %.1f pt" % T.SIZE_BODY,
            )
        # A visible run below 6.5 pt is a defect; an empty spacer run is not,
        # so the check looks at runs that actually carry text.
        tiny = Counter()
        for p in self.doc.paragraphs:
            for r in p.runs:
                if r.text.strip() and r.font.size and r.font.size.pt < 6.5:
                    tiny[r.font.size.pt] += 1
        for t in self.doc.tables:
            for row in t.rows:
                for c in row.cells:
                    for p in c.paragraphs:
                        for r in p.runs:
                            if r.text.strip() and r.font.size and r.font.size.pt < 6.5:
                                tiny[r.font.size.pt] += 1
        if tiny:
            self.add(
                "MINOR",
                "A-12",
                "Visible runs below 6.5 pt: %s"
                % ", ".join("%.1f pt ×%d" % (k, v) for k, v in sorted(tiny.items())),
            )

        n = self.doc.styles["Normal"]
        if n.font.name != T.FONT_BODY:
            self.add(
                "MAJOR",
                "A-13",
                "Normal style font is %r, expected %r" % (n.font.name, T.FONT_BODY),
            )
        if n.font.size is None or abs(n.font.size.pt - T.SIZE_BODY) > 0.01:
            self.add(
                "MAJOR",
                "A-14",
                "Normal style size is %s, expected %.1f pt"
                % (n.font.size.pt if n.font.size else None, T.SIZE_BODY),
            )

    def _navigation(self):
        instr = re.findall(r"<w:instrText[^>]*>([^<]*)</w:instrText>", self.xml)
        joined = " ".join(instr)
        self.stats["fields"] = len(instr)
        if "TOC" not in joined:
            self.add("MAJOR", "A-20", "No table-of-contents field found")
        if 'TOC \\h \\z \\c "Exhibit"' not in joined.replace("  ", " "):
            if "Exhibit" not in joined:
                self.add("MINOR", "A-21", "No list-of-exhibits field found")
        if "SEQ Exhibit" not in joined:
            self.add("MINOR", "A-22", "No numbered exhibit captions found")
        settings = self.z.read("word/settings.xml").decode("utf-8", "replace")
        if "updateFields" not in settings:
            self.add("MINOR", "A-23", "Fields are not set to update on open")

    def _headers_footers(self):
        names = self.z.namelist()
        heads = [n for n in names if re.match(r"word/header\d+\.xml", n)]
        foots = [n for n in names if re.match(r"word/footer\d+\.xml", n)]
        self.stats["headers"] = len(heads)
        self.stats["footers"] = len(foots)
        if not heads:
            self.add("MAJOR", "A-30", "No header part in the document")
        if not foots:
            self.add("MAJOR", "A-31", "No footer part in the document")
        foot_xml = " ".join(self.z.read(f).decode("utf-8", "replace") for f in foots)
        if "PAGE" not in foot_xml:
            self.add("MAJOR", "A-32", "Footer carries no page-number field")
        if "NUMPAGES" not in foot_xml:
            self.add("MINOR", "A-33", "Footer carries no total-pages field")
        if "CONFIDENTIAL" not in foot_xml:
            self.add("MINOR", "A-34", "Footer carries no classification marking")

    def _images(self):
        media = [n for n in self.z.namelist() if n.startswith("word/media/")]
        self.stats["images"] = len(media)
        empty = [n for n in media if self.z.getinfo(n).file_size == 0]
        if empty:
            self.add(
                "BLOCKER", "A-40", "Zero-byte embedded images: %s" % ", ".join(empty)
            )
        rels = self.z.read("word/_rels/document.xml.rels").decode("utf-8", "replace")
        ids = set(re.findall(r'r:embed="([^"]+)"', self.xml))
        declared = set(re.findall(r'Id="([^"]+)"[^>]*media/', rels))
        missing = ids - declared
        if missing:
            self.add(
                "BLOCKER",
                "A-41",
                "%d image references have no relationship" % len(missing),
            )
        wide = 0
        for ext in re.findall(r'<wp:extent cx="(\d+)" cy="(\d+)"', self.xml):
            if int(ext[0]) > int(T.CONTENT_W_MM * 36000) + 40000:
                wide += 1
        if wide:
            self.add(
                "MAJOR", "A-42", "%d image(s) are wider than the text column" % wide
            )

    def _tables(self):
        tbls = self.doc.tables
        self.stats["tables"] = len(tbls)
        overwide, empty = 0, 0
        for t in tbls:
            grid = t._tbl.find("{%s}tblGrid" % W)
            if grid is not None:
                total = 0
                for gc in grid.findall("{%s}gridCol" % W):
                    try:
                        total += int(gc.get("{%s}w" % W))
                    except (TypeError, ValueError):
                        pass
                if total > CONTENT_TWIPS * 1.03:
                    overwide += 1
            if len(t.rows) == 0:
                empty += 1
        if overwide:
            self.add(
                "MAJOR",
                "A-50",
                "%d table(s) declare a grid wider than the text column" % overwide,
            )
        if empty:
            self.add("MINOR", "A-51", "%d table(s) have no rows" % empty)

    def _headings(self):
        used = Counter(p.style.name for p in self.doc.paragraphs if p.style is not None)
        h = sum(v for k, v in used.items() if k.startswith("Heading"))
        self.stats["headings"] = h
        self.stats["paragraphs"] = len(self.doc.paragraphs)
        if h < 8:
            self.add(
                "MAJOR",
                "A-60",
                "Only %d heading-styled paragraphs — the navigation pane "
                "and the table of contents will be almost empty" % h,
            )

    # Only patterns that indicate a *formatting* leak. Ordinary English words
    # ("None of these findings…") and the verbatim ASCII diagrams reproduced
    # from the source are excluded, otherwise the check cries wolf on every
    # document and stops being read.
    HYGIENE = [
        # A cell reading exactly "None" is valid English — a transition with no
        # guard, a category with no members. A leak looks like "Wave None" or
        # "None person-weeks", i.e. None adjacent to the label it should have
        # replaced.
        (
            r"(?i)\b(?:wave|priority|owner|effort|code|value|target|baseline|"
            r"count|status|category)\s*[:=]?\s+(?:None|nan|NaN)\b"
            r"|\b(?:None|nan|NaN)\s+(?:person-weeks|PW|requirements|%)",
            "A-70",
            "a 'None' / 'nan' value leaked into a generated phrase",
        ),
        (r"%[sdfr]\b", "A-72", "an unformatted %s / %d placeholder remains"),
        (r"\{\d*\}", "A-73", "an unformatted {} placeholder remains"),
        (r"\*\*", "A-74", "raw markdown bold markers survive in prose"),
        (
            r"\[[^\]]{1,60}\]\([^)]{1,120}\)",
            "A-75",
            "a raw markdown link survives in the text",
        ),
        (r" {3,}", "A-76", "a run of non-breaking spaces survives"),
    ]

    @staticmethod
    def _is_mono(par):
        """True for a paragraph set in the monospaced face — a diagram panel,
        whose contents are reproduced verbatim and must not be linted."""
        for r in par.runs:
            if r.font.name == T.FONT_MONO:
                return True
        return False

    def _collect_prose(self):
        chunks = []
        for p in self.doc.paragraphs:
            if p.text.strip() and not self._is_mono(p):
                chunks.append(p.text)
        for t in self.doc.tables:
            for row in t.rows:
                for c in row.cells:
                    for p in c.paragraphs:
                        if p.text.strip() and not self._is_mono(p):
                            chunks.append(p.text)
        return chunks

    def _hygiene(self):
        chunks = self._collect_prose()
        self.stats["chars"] = sum(len(c) for c in chunks)
        self.stats["prose_blocks"] = len(chunks)
        for pat, code, msg in self.HYGIENE:
            hits = []
            rx = re.compile(pat, re.M)
            for c in chunks:
                hits.extend(rx.findall(c))
            if hits:
                sample = Counter(str(h) for h in hits).most_common(3)
                self.add(
                    "MINOR",
                    code,
                    "%s (%d occurrence%s: %s)"
                    % (
                        msg,
                        len(hits),
                        "" if len(hits) == 1 else "s",
                        ", ".join(repr(s) for s, _ in sample),
                    ),
                )

    def _properties(self):
        cp = self.doc.core_properties
        for attr in ("title", "subject", "author", "keywords", "category"):
            if not getattr(cp, attr, None):
                self.add("MINOR", "A-80", "Core property %r is not set" % attr)

    def _fidelity(self):
        """Content fidelity against the parsed source specification."""
        s = self.spec
        text = "\n".join(p.text for p in self.doc.paragraphs)
        tbl_text = []
        for t in self.doc.tables:
            for row in t.rows:
                tbl_text.append(" | ".join(c.text for c in row.cells))
        all_text = text + "\n" + "\n".join(tbl_text)

        # every section title present
        missing = []
        for n in range(1, 20):
            title = s.sec_title(n)
            if not title:
                continue
            probe = re.sub(r"\s+", " ", MD.plain(title)).strip()
            if probe and probe.lower() not in all_text.lower():
                missing.append("§%d %s" % (n, probe))
        if missing:
            self.add(
                "MAJOR",
                "A-90",
                "%d source section heading(s) not found in the document: %s"
                % (len(missing), "; ".join(missing[:6])),
            )

        # every requirement identifier present
        want = {r["id"] for r in s.reqs}
        have = set(re.findall(r"\bFR-[A-Z0-9]{2,5}-\d{3}\b", all_text))
        lost = want - have
        if lost:
            self.add(
                "BLOCKER",
                "A-91",
                "%d requirement identifier(s) from the source are missing "
                "from the document: %s" % (len(lost), ", ".join(sorted(lost)[:10])),
            )

        # every business rule identifier present
        rwant = {r["id"] for r in s.rules if r["id"]}
        rwant = {re.sub(r"[^A-Z0-9-]", "", x) for x in rwant}
        rwant = {x for x in rwant if re.match(r"^(BRU|PRU)-", x)}
        rhave = set(re.findall(r"\b(?:BRU|PRU)-[A-Z0-9]{2,5}-\d{2,3}\b", all_text))
        rlost = rwant - rhave
        if rlost:
            self.add(
                "MAJOR",
                "A-92",
                "%d rule identifier(s) missing: %s"
                % (len(rlost), ", ".join(sorted(rlost)[:8])),
            )

        # table count sanity — the source tables should all be reproduced
        src_tables = len([b for b in s.blocks if b["t"] == "table"])
        self.stats["source_tables"] = src_tables
        if self.stats.get("tables", 0) < src_tables:
            self.add(
                "MAJOR",
                "A-93",
                "Document has %d tables but the source has %d"
                % (self.stats.get("tables", 0), src_tables),
            )

        # code blocks (state machines) reproduced
        src_code = len([b for b in s.blocks if b["t"] == "code"])
        if src_code:
            got = all_text.count("STATE MACHINE — AS SPECIFIED")
            if got < src_code:
                self.add(
                    "MINOR",
                    "A-94",
                    "%d fenced diagram(s) in the source, %d reproduced "
                    "as diagram panels" % (src_code, got),
                )


def _confined(path, base):
    """Resolve path and refuse anything that escapes base (path traversal)."""
    rp = os.path.realpath(os.path.abspath(path))
    rb = os.path.realpath(base)
    try:
        inside = os.path.commonpath([rp, rb]) == rb
    except ValueError:  # different drives / mixed forms
        inside = False
    if not inside:
        raise SystemExit("refusing path outside %s: %s" % (rb, path))
    return rp


def main():
    gen_dir = os.path.dirname(os.path.abspath(__file__))
    lib_base = os.path.dirname(gen_dir)  # .../marketing/ERP_Guide_Book_Library
    mkt_base = os.path.dirname(lib_base)  # .../marketing
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=lib_base)
    ap.add_argument("--json", default=os.path.join(gen_dir, "_audit.json"))
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    args.root = _confined(args.root, mkt_base)
    args.json = _confined(args.json, mkt_base)

    print("loading source specifications …")
    specs = C.discover()
    by_uid = {s.uid: s for s in specs}

    docs = []
    for dirpath, _dirs, files in os.walk(args.root):
        for f in sorted(files):
            if f.lower().endswith(".docx") and not f.startswith("~$"):
                docs.append(os.path.join(dirpath, f))
    docs.sort()
    print("auditing %d documents in %s\n" % (len(docs), args.root))

    # ---- coverage
    coverage = []
    found_uids = set()
    for d in docs:
        m = re.match(r"^([MP]\d\d)_", os.path.basename(d))
        if m:
            found_uids.add(m.group(1))
    missing = sorted(set(by_uid) - found_uids)
    extra = sorted(found_uids - set(by_uid))
    if missing:
        coverage.append(
            (
                "BLOCKER",
                "A-C1",
                "%d component(s) have no guide book: %s"
                % (len(missing), ", ".join(missing)),
            )
        )
    if extra:
        coverage.append(
            (
                "MINOR",
                "A-C2",
                "Guide books exist for unknown components: %s" % ", ".join(extra),
            )
        )
    for letter in C.OUT_CATEGORY_FOLDER:
        want = os.path.join(args.root, "01_Modules", C.OUT_CATEGORY_FOLDER[letter])
        cat = [f for f in os.listdir(want)] if os.path.isdir(want) else []
        if not any(f.startswith("CAT-%s_" % letter) for f in cat):
            coverage.append(
                ("MAJOR", "A-C3", "Category %s has no category guide book" % letter)
            )
    psuite = os.path.join(args.root, "02_Portals_and_Applications")
    if not (
        os.path.isdir(psuite)
        and any(f.startswith("PORTALS_") for f in os.listdir(psuite))
    ):
        coverage.append(("MAJOR", "A-C4", "No portal suite guide book"))
    if not os.path.isfile(
        os.path.join(
            args.root,
            "00_Start_Here",
            "GB-000_ERP_Guide_Book_Library_Master_Index.docx",
        )
    ):
        coverage.append(("MAJOR", "A-C5", "No master index"))

    results, totals = [], Counter()
    for d in docs:
        m = re.match(r"^([MP]\d\d)_", os.path.basename(d))
        spec = by_uid.get(m.group(1)) if m else None
        a = DocAudit(d, spec).run()
        results.append(a)
        for f in a.findings:
            totals[f["severity"]] += 1
        flag = "".join(
            "%s%d " % (s[0], sum(1 for f in a.findings if f["severity"] == s))
            for s in SEV
            if any(f["severity"] == s for f in a.findings)
        )
        print(
            "%-64s %5d KB %3dp %3dt %3di  %s"
            % (
                a.name[:64],
                os.path.getsize(d) / 1024,
                a.stats.get("paragraphs", 0),
                a.stats.get("tables", 0),
                a.stats.get("images", 0),
                flag or "clean",
            )
        )
        if args.verbose:
            for f in a.findings:
                print("        %-8s %-5s %s" % (f["severity"], f["code"], f["message"]))

    print("\n" + "=" * 78)
    print("COVERAGE")
    if coverage:
        for sev, code, msg in coverage:
            print("  %-8s %-5s %s" % (sev, code, msg))
            totals[sev] += 1
    else:
        print("  complete — every component, category and index accounted for")

    print("\nFINDINGS BY CODE")
    bycode = Counter()
    for a in results:
        for f in a.findings:
            bycode[(f["severity"], f["code"])] += 1
    for (sev, code), n in sorted(bycode.items()):
        sample = next(
            f["message"] for a in results for f in a.findings if f["code"] == code
        )
        print("  %-8s %-5s ×%-4d %s" % (sev, code, n, sample[:96]))

    print("\nTOTALS  " + "  ".join("%s=%d" % (s, totals.get(s, 0)) for s in SEV))
    print("documents audited: %d" % len(results))

    json_path = os.path.realpath(args.json)
    if not json_path.startswith(os.path.realpath(mkt_base) + os.sep):
        raise SystemExit("audit report path escapes the marketing directory")
    pathlib.Path(json_path).write_text(
        json.dumps(
            {
                "root": args.root,
                "coverage": [
                    {"severity": s, "code": c, "message": m} for s, c, m in coverage
                ],
                "documents": [
                    {
                        "file": os.path.relpath(a.path, args.root).replace("\\", "/"),
                        "stats": a.stats,
                        "findings": a.findings,
                    }
                    for a in results
                ],
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print("\nwritten: %s" % args.json)
    return 1 if totals.get("BLOCKER") else 0


if __name__ == "__main__":
    sys.exit(main())
