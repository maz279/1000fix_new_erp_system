# fix.ledger.takeon — party matching at validate (2026-11-10 fix_real audit).
#
# The per-line matcher read only the first 5,000 keyed parties, so on the
# real master (27,000 parties) a ledger row whose party sorted beyond that
# window found no match and the import created a duplicate party for it.
# Matching now runs over name indexes of the whole live master.
from __future__ import annotations

import base64
import io
import uuid

import pytest

pytestmark = [pytest.mark.financial]

U = uuid.uuid4().hex[:6].upper()


def _ledger(rows) -> str:
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Partner", "Debit", "Credit", "Balance"])
    for row in rows:
        ws.append(list(row))
    buf = io.BytesIO()
    wb.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


def _validated(env, rows):
    batch = env["fix.ledger.takeon.batch"].create(
        {
            "name": "TEST matching %s" % U,
            "import_ref": "LEDGER-MATCH-%s" % U,
            "takeon_date": "2026-11-01",
            "source_file": _ledger(rows),
            "source_filename": "matching_test.xlsx",
        }
    )
    batch.action_stage()
    batch.action_validate()
    return batch


def _line(batch, needle):
    return batch.line_ids.filtered(lambda ln: needle in (ln.raw_name or ""))


class TestLedgerTakeonMatching:
    def test_a_party_sorting_last_in_a_large_master_is_still_matched(self, odoo_env):
        """`ZZZ…` sorts after every other party name: the old 5,000-row
        window never reached it once the master outgrew the window."""
        Partner = odoo_env["res.partner"]
        party = Partner.create(
            {"name": "ZZZ Probe Traders %s Ltd." % U, "legacy_reference": "CUSTX-%s-1" % U}
        )
        # the ledger spells it without the full stop: only the NORMALISED
        # name matches, which is the branch that used the window
        batch = _validated(odoo_env, [("ZZZ Probe Traders %s Ltd" % U, 1500, 0, 1500)])
        line = _line(batch, "ZZZ Probe Traders")
        assert line.line_state == "linked"
        assert line.matched_partner_id == party

    def test_exact_name_match_ignores_case_and_wildcard_characters(self, odoo_env):
        """`=ilike` treated % and _ in a ledger name as wildcards; the index
        compares the name itself."""
        Partner = odoo_env["res.partner"]
        real = Partner.create({"name": "A_B Trading %s" % U})
        Partner.create({"name": "AXB Trading %s" % U})  # would match 'A_B' as a pattern
        batch = _validated(odoo_env, [("a_b trading %s" % U.lower(), 900, 0, 900)])
        line = _line(batch, "a_b trading")
        assert line.line_state == "linked"
        assert line.matched_partner_id == real

    def test_several_parties_with_one_name_link_to_the_oldest_and_say_so(self, odoo_env):
        Partner = odoo_env["res.partner"]
        first = Partner.create({"name": "Md Twin Name %s" % U})
        Partner.create({"name": "Md Twin Name %s" % U})
        batch = _validated(odoo_env, [("Md Twin Name %s" % U, 0, 250, -250)])
        line = _line(batch, "Md Twin Name")
        assert line.matched_partner_id == first
        assert "2 live parties carry this name" in (line.notes or "")

    def test_unknown_party_with_a_balance_is_importable_and_zero_is_quarantined(self, odoo_env):
        batch = _validated(
            odoo_env,
            [
                ("Nobody Knows %s Enterprise" % U, 700, 0, 700),
                ("Nobody Owes %s Enterprise" % U, 500, 500, 0),
            ],
        )
        assert _line(batch, "Nobody Knows").line_state == "staged"
        zero = _line(batch, "Nobody Owes")
        assert zero.line_state == "quarantined"
        assert "zero balance" in zero.notes
