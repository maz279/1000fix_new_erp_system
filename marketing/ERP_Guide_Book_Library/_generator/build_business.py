# -*- coding: utf-8 -*-
"""
build_business — rebuild the business-reader guide books for a category.

    python build_business.py            # every module with a content pack
    python build_business.py M01        # just one

Reads the module specifications, renders the exhibits, assembles the Word
files and reports what it produced. Nothing is written outside the category's
output folder and the exhibit cache.
"""

import io
import os
import sys
import time
from collections import OrderedDict
import traceback

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import spec as S  # noqa: E402
import bizcontent  # noqa: E402
from bizbook import BusinessGuideBook  # noqa: E402
from bizcatbook import CategoryGuideBook  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SPEC_DIR = os.path.join(
    ROOT, "1000fix_ERP_Module", "03_Modules", "A_Service_Delivery_and_Operations"
)
OUT_DIR = os.path.join(HERE, "..", "01_Modules", "A_Service_Delivery_and_Operations")
EX_DIR = os.path.join(HERE, "_exhibits_biz")

ORDER = ["M01", "M02", "M03", "M04", "M05", "M06", "M31"]


def specs():
    found = {}
    for f in sorted(os.listdir(SPEC_DIR)):
        if not f.endswith(".md") or not f.startswith("M"):
            continue
        sp = S.Spec(os.path.join(SPEC_DIR, f))
        found[sp.uid] = sp
    return found


def main(argv):
    args = [a.upper() for a in argv[1:]]
    want_cat = (not args) or any(a.startswith("CAT") for a in args)
    wanted = [a for a in args if not a.startswith("CAT")] or (ORDER if not args else [])
    all_specs = specs()
    ok, failed = [], []

    for uid in wanted:
        sp = all_specs.get(uid)
        if sp is None:
            print("  %-4s  no specification found — skipped" % uid)
            continue
        try:
            content = bizcontent.load(uid)
        except KeyError as e:
            print("  %-4s  %s" % (uid, e))
            failed.append(uid)
            continue

        t0 = time.time()
        try:
            gb = BusinessGuideBook(sp, content, EX_DIR, os.path.abspath(OUT_DIR))
            gb.build_exhibits()
            path = gb.build()
        except Exception:
            print("  %-4s  FAILED" % uid)
            traceback.print_exc()
            failed.append(uid)
            continue

        kb = os.path.getsize(path) / 1024.0
        print(
            "  %-4s  %-52s %7.0f KB  %2d exhibits  %4.1fs"
            % (uid, os.path.basename(path), kb, len(gb.ex), time.time() - t0)
        )
        ok.append(path)

    # The category book is built last, because it measures the modules.
    if want_cat:
        try:
            from bizcontent import cat_a

            ordered = OrderedDict((u, all_specs[u]) for u in ORDER if u in all_specs)
            t0 = time.time()
            cb = CategoryGuideBook(
                "A", ordered, cat_a.CONTENT, EX_DIR, os.path.abspath(OUT_DIR)
            )
            cb.build_exhibits()
            path = cb.build()
            print(
                "  %-4s  %-52s %7.0f KB  %2d exhibits  %4.1fs"
                % (
                    "CAT",
                    os.path.basename(path),
                    os.path.getsize(path) / 1024.0,
                    len(cb.ex),
                    time.time() - t0,
                )
            )
            ok.append(path)
        except Exception:
            print("  CAT   FAILED")
            traceback.print_exc()
            failed.append("CAT-A")

    print("\n%d built, %d failed" % (len(ok), len(failed)))
    if failed:
        print("failed: %s" % ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
