# ruff: noqa: F811  (the M04 fixtures are imported and used as parameters)
"""M04 capture audit (18 Nov 2026): the shift handover and the counter rating.

Every M04 page already had a "+ New" (13 Nov), but two captures the
specification gives M04 had no record behind them:

- Shift Operations: FR-FRD-022 "record structured handover notes between
  shifts, visible to the incoming team" (owned entity fix.shift.handover,
  with acknowledged_by). A free-text note on the day's checklist named no
  incoming team member and nothing showed it was read.
- Collection & Handover: FR-FRD-029 / AUT-FRD-12, the customer's quick rating
  at handover. M34's survey is raised only when the order CLOSES, so nothing
  at the counter could record it.

Exercised through the workspace endpoints the forms use, as non-admin users.
The high-value cash ID check is in cd_front_desk_finance
(test_m04_high_value_cash).
"""

from __future__ import annotations

import pytest
from odoo.exceptions import AccessError, UserError

from .test_a02_p0_m04 import m04  # noqa: F401
from .test_m04_build2 import _ready_order, screens, ui  # noqa: F401
from .test_m04_submodule_capture import _form_values, _rows, registry  # noqa: F401


def _handover(m, ui, screens, user, shift, to_emp, notes="Two customers promised a call back."):
    cfg = screens["M04-form-shift-handover"]
    return ui.write(
        user,
        model="fix.shift.handover",
        values=_form_values(
            cfg, {"from_shift_id": shift.id, "to_operator_id": to_emp.id, "notes": notes}
        ),
    )


# --------------------------------------------------------- shift handover


def test_the_outgoing_shift_writes_a_handover_the_workspace_lists(m04, ui, screens):
    shift = m04.shift()
    res = _handover(m04, ui, screens, m04.cashier, shift, m04.cashier2_emp)
    assert "error" not in res, res
    ho = m04.env["fix.shift.handover"].browse(res["id"])
    assert ho.name.startswith("SHO/") and ho.state == "handed_over"
    assert ho.handed_over_by_id == m04.cashier and ho.handed_over_at
    assert ho.branch_id == m04.branch and ho.from_operator_id == m04.cashier_emp
    assert ho.operating_unit_id == shift.operating_unit_id
    listed = ui.records(m04.cashier2, model="fix.shift.handover", cols=["name", "state"])
    assert ho.id in {r["id"] for r in listed["rows"]}


def test_a_handover_says_something_and_goes_to_someone_else(m04, ui, screens):
    shift = m04.shift()
    assert "error" in _handover(m04, ui, screens, m04.cashier, shift, m04.cashier2_emp, notes="ok")
    res = _handover(m04, ui, screens, m04.cashier, shift, m04.cashier_emp)
    assert "error" in res and "next team" in res["error"]
    # the stamps are the system's, never typed
    res = ui.write(
        m04.cashier,
        model="fix.shift.handover",
        values={
            "from_shift_id": shift.id,
            "to_operator_id": m04.cashier2_emp.id,
            "notes": "Counter 2 printer jammed all afternoon.",
            "acknowledged_by_id": m04.cashier2.id,
            "state": "acknowledged",
        },
    )
    if "error" not in res:
        ho = m04.env["fix.shift.handover"].browse(res["id"])
        assert ho.state == "handed_over" and not ho.acknowledged_by_id


def test_only_the_incoming_team_member_acknowledges(m04, ui, screens):
    shift = m04.shift()
    ho = m04.env["fix.shift.handover"].browse(
        _handover(m04, ui, screens, m04.cashier, shift, m04.cashier2_emp)["id"]
    )

    def ack(user):
        return ui.action(user, model="fix.shift.handover", ids=[ho.id], method="action_acknowledge")

    res = ack(m04.cashier)
    assert not res["success"] and "incoming team" in res["error"]
    res = ack(m04.manager)
    assert not res["success"]
    assert ack(m04.cashier2)["success"]
    ho.invalidate_recordset()
    assert ho.state == "acknowledged" and ho.acknowledged_by_id == m04.cashier2
    assert ho.acknowledged_at
    # acknowledged = kept as written
    with pytest.raises(UserError, match="not changed"), m04.env.cr.savepoint():
        ho.with_user(m04.cashier).write({"notes": "rewritten afterwards"})
    with pytest.raises(UserError, match="never deleted"), m04.env.cr.savepoint():
        ho.with_user(m04.manager).unlink()
    assert not ack(m04.cashier2)["success"]


def test_an_incoming_member_without_a_login_is_signed_for_by_the_manager(m04, ui, screens):
    no_login = m04.env["hr.employee"].create({"name": "M04 casual counter staff"})
    shift = m04.shift()
    ho = m04.env["fix.shift.handover"].browse(
        _handover(m04, ui, screens, m04.cashier, shift, no_login)["id"]
    )
    res = ui.action(
        m04.cashier2, model="fix.shift.handover", ids=[ho.id], method="action_acknowledge"
    )
    assert not res["success"]
    res = ui.action(
        m04.manager, model="fix.shift.handover", ids=[ho.id], method="action_acknowledge"
    )
    assert res["success"], res


def test_only_front_desk_staff_write_a_handover(m04, ui, screens):
    shift = m04.shift()
    assert "error" in _handover(m04, ui, screens, m04.plain, shift, m04.cashier2_emp)
    with pytest.raises(AccessError):
        m04.env["fix.shift.handover"].with_user(m04.plain).create(
            {
                "from_shift_id": shift.id,
                "to_operator_id": m04.cashier2_emp.id,
                "notes": "Plain users have no front-desk role.",
            }
        )


def test_only_the_writer_corrects_a_handover_before_it_is_read(m04, ui, screens):
    shift = m04.shift()
    ho = m04.env["fix.shift.handover"].browse(
        _handover(m04, ui, screens, m04.cashier, shift, m04.cashier2_emp)["id"]
    )
    ho.with_user(m04.cashier).write({"open_items": "Order for Mr Karim promised by 5 pm."})
    with pytest.raises(UserError, match="wrote"), m04.env.cr.savepoint():
        ho.with_user(m04.cashier2).write({"notes": "the incoming one rewrites it"})


# --------------------------------------------------------- counter rating


def test_the_counter_takes_the_customers_rating_at_handover(m04, ui, screens):
    """A02 pass 2 (M04-06): the customer gives the rating on their own page
    (the counter asks for it); staff never type it."""
    order = _ready_order(m04)
    form = screens["M04-form-rating"]
    listed = ui.records(
        m04.cashier, model="fix.service.order", cols=["name"], domain=form["pickRecord"]["domain"]
    )
    assert order.id in {r["id"] for r in listed["rows"]}
    res = ui.write(
        m04.cashier,
        model="fix.service.order",
        record_id=order.id,
        values={"counter_rating": "4", "counter_feedback": "Quick, polite"},
    )
    assert "error" in res, "staff typed the customer's rating"
    order.with_user(m04.cashier).action_request_counter_rating()
    token = order.sudo().counter_rating_token
    m04.env["fix.service.order"]._fd_take_customer_rating(token, "4", "Quick, polite")
    order.invalidate_recordset()
    assert order.counter_rating == "4" and order.counter_rated_by_id == m04.cashier
    assert order.counter_rated_at
    # rated: off the pick list, and never re-rated
    listed = ui.records(
        m04.cashier, model="fix.service.order", cols=["name"], domain=form["pickRecord"]["domain"]
    )
    assert order.id not in {r["id"] for r in listed["rows"]}
    with pytest.raises(UserError, match="already rated"):
        order.with_user(m04.cashier2).action_request_counter_rating()


def test_a_rating_is_taken_only_at_handover(m04, ui, screens):
    order = _ready_order(m04)
    m04.env.cr.execute("UPDATE fix_service_order SET state = 'in_repair' WHERE id = %s", [order.id])
    order.invalidate_recordset()
    with pytest.raises(UserError, match="handover"):
        order.with_user(m04.cashier).action_request_counter_rating()


def test_the_release_form_still_saves_without_a_rating(m04, ui, screens):
    """The release form does not show the rating: saving the collector's
    name must not be refused for a rating nobody was asked for."""
    order = _ready_order(m04)
    res = ui.write(
        m04.cashier,
        model="fix.service.order",
        record_id=order.id,
        values=_form_values(screens["M04-form-release"], {"recipient_name": "Self"}),
    )
    assert "error" not in res, res
    order.invalidate_recordset()
    assert not order.counter_rated_at


# --------------------------------------------------------- the pages


def test_the_pages_offer_the_captures_the_spec_gives_them(registry):
    """Before: page 4 could not take a rating, page 7 could not record an
    NID, page 8 opened a cash shift (page 6's) and page 9 never listed the
    deposits it captured."""
    rows = _rows(registry)
    chips = registry["chips"]

    def forms(no):
        return {chips.get("M04:" + f) for f in rows[no]["forms"]}

    assert "M04-form-rating" in forms("4")
    assert "M04-form-idcheck" in forms("7")
    assert rows["8"]["create"]["screen"] == "M04-form-shift-handover"
    assert rows["8"]["model"] == "fix.shift.handover"
    assert {"M04-form-shift-handover", "M04-form-shift", "M04-form-checklist"} <= forms("8")
    assert "M04-deposits" in _freg_screens()["9"]


def _freg_screens():
    """{page: screens} of the M04 fragment's sub-module register, read by node."""
    import json
    import shutil
    import subprocess
    from pathlib import Path

    import odoo.addons.cd_p03_portal as portal

    node = shutil.which("node")
    if not node:
        pytest.skip("node is not available to evaluate the M04 fragment")
    src = Path(portal.__file__).parent / "static" / "src" / "a02" / "m04.js"
    probe = (
        "import { pathToFileURL } from 'node:url';\n"
        "import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';\n"
        "import { tmpdir } from 'node:os';\n"
        "import { join } from 'node:path';\n"
        "const file = join(mkdtempSync(join(tmpdir(), 'm04gap')), 'm04.mjs');\n"
        "writeFileSync(file, readFileSync(process.argv[1], 'utf-8'));\n"
        "const M = await import(pathToFileURL(file).href);\n"
        "console.log(JSON.stringify(Object.fromEntries("
        "M.MODULE.freg.sub.map((s) => [s[0], s[3].screens || []]))));\n"
    )
    out = subprocess.run(  # noqa: S603 - fixed argv: the node binary, inline probe, our file
        [node, "--input-type=module", "-e", probe, str(src)],
        capture_output=True,
        encoding="utf-8",
        check=True,
        timeout=60,
    )
    return json.loads(out.stdout)
