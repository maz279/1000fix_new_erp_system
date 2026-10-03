# -*- coding: utf-8 -*-
"""
build_library — generate the complete 1000FiX ERP Guide Book Library.

    python build_library.py [--only M01,P02] [--jobs 8] [--clean]

Produces, under <out>/:
    00_Start_Here/                GB-000 master index
    01_Modules/<A..K>/            67 module guide books + 11 category guide books
    02_Portals_and_Applications/  12 portal guide books + the suite guide book

Component guide books are independent of one another, so they are generated
in parallel; the category volumes and the master index are generated after,
because they aggregate across the whole set.
"""
import argparse
import io
import json
import os
import pathlib
import re
import shutil
import sys
import time
import traceback
from collections import OrderedDict, Counter
from multiprocessing import Pool, cpu_count

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import theme as T
import catalogue as C
from findings import Findings
from guidebook import GuideBook
from groupbook import CategoryBook
from masterbook import MasterIndex

SCRATCH = os.path.dirname(os.path.abspath(__file__))
LIB_BASE = os.path.dirname(SCRATCH)          # .../marketing/ERP_Guide_Book_Library
MARKETING_BASE = os.path.dirname(LIB_BASE)   # .../marketing
DEFAULT_OUT = LIB_BASE


def _confined(path, base):
    """Resolve path and refuse anything that escapes base (path traversal)."""
    rp = os.path.realpath(os.path.abspath(path))
    rb = os.path.realpath(base)
    try:
        inside = os.path.commonpath([rp, rb]) == rb
    except ValueError:                       # different drives / mixed forms
        inside = False
    if not inside:
        raise SystemExit("refusing path outside %s: %s" % (rb, path))
    return rp
EXDIR = os.path.join(SCRATCH, "_exhibits")
os.makedirs(EXDIR, exist_ok=True)

FOLDER_STRUCTURE = """
ERP_Guide_Book_Library/
│
├── 00_Start_Here/
│     GB-000_ERP_Guide_Book_Library_Master_Index.docx
│
├── 01_Modules/
│   ├── A_Service_Delivery_and_Operations/
│   │     CAT-A_..._Category_Guide_Book.docx
│   │     M01_...  M02_...  M03_...  M04_...  M05_...  M06_...  M31_...
│   ├── B_Customer_Engagement_and_Experience/
│   ├── C_Commercial_Pricing_and_Revenue/
│   ├── D_Circular_and_Asset_Based_Business/
│   ├── E_Supply_Chain_and_Inventory/
│   ├── F_Asset_Equipment_and_Facilities/
│   ├── G_Finance_and_Treasury/
│   ├── H_People_and_Workforce/
│   ├── I_Governance_Risk_Quality_and_Knowledge/
│   ├── J_Data_Analytics_and_Intelligence/
│   └── K_Platform_and_Technology/
│
└── 02_Portals_and_Applications/
      PORTALS_Portal_and_Application_Suite_Guide_Book.docx
      P01_...  P02_...  P03_...  P04_...  P05_...  P06_...
      P07_...  P08_...  P09_...  P10_...  P11_...  P12_...

Each category folder holds its category guide book first, then one guide book
for every module in that category. Portals are not filed under a module
category: a portal is a surface, not a module, and filing it as one would
repeat the classification error the v2.0 architecture exists to correct.
""".strip("\n").split("\n")


REGISTER = OrderedDict([
    ("Modules specified", (67, "02-02 §2")),
    ("Portals specified", (12, "04-00 §2")),
    ("Functional requirements", (2930, "02-02 §3, measured 2026-08-13")),
    ("Build effort (person-weeks)", (1513, "02-02 §3, measured 2026-08-13")),
])


def register_comparison(specs):
    measured = {
        "Modules specified": len([s for s in specs if not s.is_portal]),
        "Portals specified": len([s for s in specs if s.is_portal]),
        "Functional requirements": sum(s.req_count for s in specs),
        "Build effort (person-weeks)":
            int(round(sum(s.effort_pw or 0 for s in specs))),
    }
    rows = []
    for k, (reg, src) in REGISTER.items():
        m = measured[k]
        d = m - reg
        note = ("Agrees with the register."
                if d == 0 else
                "The measured figure is %+d (%+.1f%%) against the register. "
                "Under RG-06 the measured figure stands and the register is "
                "what needs correcting." % (d, 100.0 * d / reg if reg else 0))
        rows.append([k, "%s  (%s)" % ("{:,}".format(reg), src),
                     "{:,}".format(m), "%+d" % d, note])
    return rows


def write_readme(root, specs):
    lines = [
        "# 1000FiX ERP Guide Book Library",
        "",
        "**%s · %s · issued %s**" % (T.PROGRAMME, T.EDITION, T.ISSUE_DATE),
        "",
        "`CONFIDENTIAL — Internal Use Only`",
        "",
        "This folder holds the complete guide book library for the 1000FiX ERP:",
        "one Microsoft Word guide book for every module and every portal, one for",
        "every category, one for the portal suite, and a master index.",
        "",
        "**Start with** `00_Start_Here/GB-000_ERP_Guide_Book_Library_Master_Index.docx`.",
        "It is the authoritative index; this file is only a signpost for Explorer.",
        "",
        "| Level | Where | Count |",
        "|---|---|---:|",
        "| Master index | `00_Start_Here/` | 1 |",
        "| Category guide books | `01_Modules/<category>/` | 11 |",
        "| Module guide books | `01_Modules/<category>/` | %d |"
        % len([s for s in specs if not s.is_portal]),
        "| Portal suite guide book | `02_Portals_and_Applications/` | 1 |",
        "| Portal guide books | `02_Portals_and_Applications/` | %d |"
        % len([s for s in specs if s.is_portal]),
        "",
        "## Opening a guide book",
        "",
        "Every volume carries a Word table of contents, a list of exhibits and a",
        "list of tables, all built from fields. Word is set to update them on open;",
        "if a contents page still shows placeholder text, press **Ctrl+A** then **F9**.",
        "",
        "## Typography",
        "",
        "Body text is Calibri 9.5 pt throughout, as the house standard requires.",
        "Reference tables of seven columns or more are set at 8.5 pt so that they",
        "fit the A4 text column; that is the only permitted deviation.",
        "",
        "---",
        "",
        "*1000FiX Services Limited · Hotline 16743 · ISO 9001:2015 Certified*",
        "",
    ]
    # normalize + validate: confine the write to MARKETING_BASE
    readme = os.path.realpath(os.path.join(root, "README.md"))
    allowed_root = os.path.realpath(MARKETING_BASE)
    if not readme.startswith(allowed_root + os.sep):
        raise SystemExit("README path escapes the marketing library root")
    pathlib.Path(readme).write_text("\n".join(lines), encoding="utf-8")


# --------------------------------------------------------------- worker
_W = {}


def _init(root):
    """Each worker re-reads the source set once; specs are not picklable-cheap."""
    specs = C.discover()
    _W["specs"] = specs
    _W["index"] = C.build_index(specs)
    _W["findings"] = Findings(specs)
    _W["root"] = root


def _one(uid):
    specs = _W["specs"]
    s = next(x for x in specs if x.uid == uid)
    root = _W["root"]
    outdir = (os.path.join(root, "02_Portals_and_Applications") if s.is_portal
              else os.path.join(root, "01_Modules",
                                C.OUT_CATEGORY_FOLDER[s.category]))
    t = time.time()
    try:
        gb = GuideBook(s, _W["index"], C.peers_for(specs, s), EXDIR, outdir,
                       findings=_W["findings"].for_uid(uid))
        path = gb.build()
        return {"ok": True, "uid": uid, "path": path,
                "kb": round(os.path.getsize(path) / 1024.0, 1),
                "secs": round(time.time() - t, 1),
                "reqs": s.req_count, "category": s.category,
                "kind": "portal" if s.is_portal else "module",
                "name": s.name,
                "exhibits": len([v for v in gb.exhibits.values()
                                 if isinstance(v, str) and v.endswith(".png")])}
    except Exception:
        return {"ok": False, "uid": uid, "trace": traceback.format_exc()}


def _one_cat(letter):
    specs = _W["specs"]
    root = _W["root"]
    groups = C.category_groups(specs)
    group = groups.get(letter, [])
    if letter == "P":
        outdir = os.path.join(root, "02_Portals_and_Applications")
        overview = None
    else:
        outdir = os.path.join(root, "01_Modules", C.OUT_CATEGORY_FOLDER[letter])
        overview = os.path.join(C.SRC_MODULES, C.CATEGORY_FOLDER[letter],
                                "_CATEGORY_OVERVIEW.md")
    t = time.time()
    try:
        cb = CategoryBook(letter, group, _W["index"], overview, outdir, EXDIR,
                          findings=_W["findings"])
        path = cb.build()
        return {"ok": True, "uid": "CAT-%s" % letter, "path": path,
                "kb": round(os.path.getsize(path) / 1024.0, 1),
                "secs": round(time.time() - t, 1),
                "reqs": sum(s.req_count for s in group), "category": letter,
                "kind": "suite" if letter == "P" else "category",
                "name": T.cat_name(letter),
                "exhibits": len([v for v in cb.exhibits.values() if v])}
    except Exception:
        return {"ok": False, "uid": "CAT-%s" % letter,
                "trace": traceback.format_exc()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--only", default="")
    ap.add_argument("--jobs", type=int, default=max(1, min(10, cpu_count() - 2)))
    ap.add_argument("--skip-modules", action="store_true")
    ap.add_argument("--skip-categories", action="store_true")
    ap.add_argument("--skip-master", action="store_true")
    ap.add_argument("--clean", action="store_true")
    args = ap.parse_args()

    only = {x.strip().upper() for x in args.only.split(",") if x.strip()}
    root = _confined(args.out, MARKETING_BASE)
    t0 = time.time()

    print("reading specifications …")
    specs = C.discover()
    index = C.build_index(specs)
    groups = C.category_groups(specs)
    fnd = Findings(specs)
    print("  %d specifications  (%d modules, %d portals)"
          % (len(specs), len([s for s in specs if not s.is_portal]),
             len([s for s in specs if s.is_portal])))
    print("  %d integrity findings across %d components"
          % (sum(fnd.summary().values()), len(fnd.per)))
    print("  building with %d parallel workers\n" % args.jobs)

    if args.clean and os.path.isdir(root):
        shutil.rmtree(root)
    for sub in ["00_Start_Here", "01_Modules", "02_Portals_and_Applications"]:
        os.makedirs(os.path.join(root, sub), exist_ok=True)
    for letter, folder in C.OUT_CATEGORY_FOLDER.items():
        os.makedirs(os.path.join(root, "01_Modules", folder), exist_ok=True)

    manifest, failures = [], []
    uids = [s.uid for s in specs if not only or s.uid in only]
    cats = [c for c in list(C.CATEGORY_FOLDER.keys()) + ["P"]
            if not only or ("CAT-%s" % c) in only]

    pool = Pool(processes=args.jobs, initializer=_init, initargs=(root,))
    try:
        if not args.skip_modules and uids:
            done = 0
            for r in pool.imap_unordered(_one, uids):
                done += 1
                if r["ok"]:
                    manifest.append(r)
                    print("  [%3d/%3d] %-5s %7.1f KB %5.1fs  %s"
                          % (done, len(uids), r["uid"], r["kb"], r["secs"],
                             os.path.basename(r["path"])))
                else:
                    failures.append((r["uid"], r["trace"]))
                    print("  [%3d/%3d] %-5s FAILED" % (done, len(uids), r["uid"]))

        if not args.skip_categories and cats:
            for r in pool.imap_unordered(_one_cat, cats):
                if r["ok"]:
                    manifest.append(r)
                    print("  [cat]     %-7s %7.1f KB %5.1fs  %s"
                          % (r["uid"], r["kb"], r["secs"],
                             os.path.basename(r["path"])))
                else:
                    failures.append((r["uid"], r["trace"]))
                    print("  [cat]     %-7s FAILED" % r["uid"])
    finally:
        pool.close()
        pool.join()

    if not args.skip_master:
        t = time.time()
        try:
            mi = MasterIndex(specs, index, groups,
                             os.path.join(root, "00_Start_Here"), EXDIR,
                             FOLDER_STRUCTURE, register_comparison(specs),
                             findings=fnd)
            path = mi.build()
            manifest.append({"ok": True, "uid": "GB-000", "path": path,
                             "kb": round(os.path.getsize(path) / 1024.0, 1),
                             "secs": round(time.time() - t, 1),
                             "reqs": sum(s.req_count for s in specs),
                             "category": "-", "kind": "index",
                             "name": "Library Master Index",
                             "exhibits": len([v for v in mi.exhibits.values() if v])})
            print("  [index]   GB-000  %7.1f KB %5.1fs  %s"
                  % (manifest[-1]["kb"], manifest[-1]["secs"],
                     os.path.basename(path)))
        except Exception:
            failures.append(("GB-000", traceback.format_exc()))
            print("  [index]   GB-000  FAILED")

    write_readme(root, specs)
    manifest_path = os.path.realpath(os.path.join(SCRATCH, "_manifest.json"))
    if not manifest_path.startswith(os.path.realpath(SCRATCH) + os.sep):
        raise SystemExit("manifest path escapes the generator scratch dir")
    pathlib.Path(manifest_path).write_text(json.dumps(
        {"generated": T.ISSUE_DATE, "root": root,
         "documents": [{k: v for k, v in m.items() if k != "trace"}
                       for m in manifest]}, indent=1), encoding="utf-8")

    tot_kb = sum(m["kb"] for m in manifest)
    kinds = Counter(m["kind"] for m in manifest)
    print("\n%d documents  ·  %.1f MB  ·  %.1f min" %
          (len(manifest), tot_kb / 1024.0, (time.time() - t0) / 60.0))
    print("  " + "  ".join("%s=%d" % (k, v) for k, v in sorted(kinds.items())))
    if failures:
        print("\n%d FAILURES" % len(failures))
        for uid, tb in failures:
            print("=" * 74)
            print(uid)
            print(tb)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
