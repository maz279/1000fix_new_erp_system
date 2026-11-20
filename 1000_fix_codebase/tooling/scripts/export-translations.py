"""export-translations — regenerate i18n/<module>.pot and i18n/bn_BD.po from
the Odoo runtime (supersedes extract-translations.py).

Odoo's PO reader needs "#. module:" and "#: model:..." lines on every entry.
The hand-extracted templates had neither: once the bn_BD language was active
they crashed the translation loader at install, and they could never have
translated a field label. This script asks the runtime what is translatable,
keeps every existing Bengali translation (by msgid) and reports what is new.

Run INSIDE an Odoo shell on a database with the modules installed:

    FIX_MODULES=cd_vendor_ext,cd_requisition \\
        odoo-bin shell -c <conf> -d <db> < tooling/scripts/export-translations.py

FIX_MODULES omitted = every installed cd_* module. New, untranslated msgids
are left empty and listed; FF-25 (check_translations.py) blocks the merge
until they are translated.
"""
import io
import os
import sys
from pathlib import Path

import polib

from odoo.tools.translate import trans_export

env = globals().get("env")  # injected by `odoo-bin shell`
if env is None:
    sys.exit("run inside `odoo-bin shell` (see the module docstring)")

ADDONS = Path(__file__).resolve().parents[2] / "addons" if "__file__" in globals() \
    else Path.cwd() / "addons"
if not ADDONS.is_dir():
    ADDONS = Path(os.environ.get("FIX_ADDONS", "addons")).resolve()

wanted = [m for m in os.environ.get("FIX_MODULES", "").split(",") if m]
installed = env["ir.module.module"].search(
    [("name", "=like", "cd\\_%"), ("state", "=", "installed")]).mapped("name")
modules = wanted or installed
dirs = {p.parent.name: p.parent for p in ADDONS.rglob("__manifest__.py")}


def split_occurrences(path):
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#: ") and " " in line[3:]:
            lines += ["#: " + ref for ref in line[3:].split()]
        else:
            lines.append(line)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


todo = {}
for mod in modules:
    buf = io.BytesIO()
    if mod not in dirs or not trans_export(False, [mod], buf, "po", env):
        continue
    text = buf.getvalue().decode()
    pot = polib.pofile(text, wrapwidth=0)
    if not [e for e in pot if e.msgid]:
        continue
    i18n = dirs[mod] / "i18n"
    i18n.mkdir(exist_ok=True)
    old_po = i18n / "bn_BD.po"
    known = ({e.msgid: e.msgstr for e in polib.pofile(str(old_po)) if e.msgstr}
             if old_po.exists() else {})
    for stale in i18n.glob("*.pot"):
        stale.unlink()
    pot.header = (f"Translation template for {mod} — exported from the Odoo 19 runtime "
                  "(tooling/scripts/export-translations.py).\n"
                  "Bengali (bn_BD) is the first-class locale (AS-12, DE-17, TR-07).")
    pot.metadata = {"Project-Id-Version": "1000FiX ERP 19.0", "Language": "",
                    "Content-Type": "text/plain; charset=UTF-8",
                    "Content-Transfer-Encoding": "8bit"}
    for e in pot:
        e.msgstr = ""
    pot.save(str(i18n / f"{mod}.pot"))
    split_occurrences(i18n / f"{mod}.pot")
    po = polib.pofile(text, wrapwidth=0)
    po.header = (f"Bengali (Bangladesh) translation for {mod}.\n"
                 "100% coverage - FF-24/FF-25 block below 100% (AS-12, DE-17, TR-07).")
    po.metadata = {"Project-Id-Version": "1000FiX ERP 19.0", "Language": "bn_BD",
                   "Content-Type": "text/plain; charset=UTF-8",
                   "Content-Transfer-Encoding": "8bit",
                   "Plural-Forms": "nplurals=2; plural=(n != 1);"}
    for e in po:
        e.msgstr = known.get(e.msgid, "")
        if e.msgid and not e.msgstr:
            todo.setdefault(mod, []).append(e.msgid)
    po.save(str(old_po))
    split_occurrences(old_po)

print(f"export-translations: {len(modules)} module(s); "
      f"{sum(len(v) for v in todo.values())} msgid(s) need Bengali")
for mod, ids in sorted(todo.items()):
    print(f"  {mod}: {len(ids)} new - e.g. {ids[0]!r}")
