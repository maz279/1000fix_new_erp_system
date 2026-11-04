# A06 follow-up 2 - M15-2 (probe m15_83): write-offs and adjustments above
# the controller's limit are routed M63 approvals on the DOFA ladder by
# value (BRU-INV-11/24: above BDT 25,000 the CFO, Tier 4); and S0: the
# duplicated initial-count baseline is archived on Finance authority.
import pytest
from odoo.exceptions import AccessError, UserError, ValidationError

from .conftest import IC, SK

REFUSED = (UserError, AccessError, ValidationError)
FINANCE_ADMIN = "account.group_account_manager"


def refused(inv, fn, match=None):
    with pytest.raises(REFUSED, match=match), inv.env.cr.savepoint():
        fn()
        inv.env.flush_all()


def _big(inv, qty=10.0, cost=50000.0):
    part = inv.env["fix.spare.part"].create(
        {"name": "big", "part_number": "A6D-" + inv.tag, "unit_cost": cost}
    )
    inv.stock(part, inv.central, qty, cost)
    return part


def _count_to_approval(inv, part, counted, user):
    count = inv.count(user, counted, part=part)
    count.with_user(user).action_submit()
    count.line_ids.with_user(user).write({"recount_qty": counted})
    count.with_user(user).write({"reason_code": "loss", "reason_note": "shelf found empty"})
    count.with_user(user).action_submit()
    assert count.state == "to_approve"
    return count


def test_m15_83_models_route_large_write_offs_through_m63(inv):
    for model in ("fix.stock.count", "fix.stock.quarantine"):
        records = inv.env[model]
        assert records._approval_routed and hasattr(records, "action_request_approval")
        assert "approval_state" in records._fields and "dofa_approved" in records._fields


def test_m15_02a_large_adjustment_needs_the_routed_cfo_approval(inv):
    big = _big(inv)
    cfo = inv.cfo()
    count = _count_to_approval(inv, big, 0.0, inv.keeper)
    count.with_user(inv.controller).action_approve()
    assert (count.state, count.approval_state, count.dofa_tier_required) == (
        "to_dofa",
        "pending",
        "tier_4",
    )
    assert count.approval_request_id.amount == 500000.0
    assert inv.qty(big, inv.central) == 10.0  # nothing applied yet
    # the controller's approval alone does not apply it, nor a direct call
    refused(inv, lambda: count.with_user(inv.controller).action_dofa_approve(), "inbox")
    refused(inv, lambda: count.with_user(cfo).action_dofa_approve(), "inbox")
    inv.approve_in_inbox(count, cfo)
    assert count.state == "posted" and inv.qty(big, inv.central) == 0.0
    assert (count.dofa_approved_by, count.dofa_approved_amount) == (cfo, 500000.0)


def test_m15_02b_counter_requester_and_controller_never_decide_it(inv):
    big = _big(inv)
    counter_cfo = inv.cfo(SK)  # the counter also holds the CFO band
    controller_cfo = inv.cfo(IC)
    other_cfo = inv.cfo()
    count = _count_to_approval(inv, big, 0.0, counter_cfo)
    count.with_user(controller_cfo).action_approve()
    assigned = count.approval_request_id.task_ids.mapped("assigned_user_id")
    assert counter_cfo not in assigned and controller_cfo not in assigned
    assert other_cfo in assigned
    with pytest.raises(AssertionError):
        inv.approve_in_inbox(count, counter_cfo)
    inv.approve_in_inbox(count, other_cfo)
    assert count.state == "posted"


def test_m15_02c_approval_is_pinned_to_its_value(inv):
    big = _big(inv)
    cfo = inv.cfo()
    count = _count_to_approval(inv, big, 0.0, inv.keeper)
    count.with_user(inv.controller).action_approve()
    inv.approve_in_inbox(count, cfo)
    assert count.dofa_approved_amount == count._writeoff_value() == 500000.0
    # had the value grown after the approval, the approval would not cover it
    snap = count.line_ids._snapshot()
    snap.write({"unit_cost": 60000.0})
    with pytest.raises(ValidationError, match="approved for 500000"):
        count._dofa_assert_approved("The write-off")


def test_m15_02d_cfo_rejection_cancels_and_moves_nothing(inv):
    big = _big(inv)
    cfo = inv.cfo()
    count = _count_to_approval(inv, big, 0.0, inv.keeper)
    count.with_user(inv.controller).action_approve()
    task = count.approval_request_id.task_ids.filtered(lambda t: t.assigned_user_id == cfo)
    task.with_user(cfo).action_reject(comment="recount the shelf first")
    assert count.state == "cancelled" and inv.qty(big, inv.central) == 10.0


def test_m15_02e_below_the_controller_limit_two_persons_suffice(inv):
    count = _count_to_approval(inv, inv.part, 9.0, inv.keeper)  # BDT 500
    count.with_user(inv.controller).action_approve()
    assert count.state == "posted" and count.approval_state == "none"
    assert inv.qty(inv.part, inv.central) == 9.0


def test_m15_02f_limit_and_ceiling_are_configuration(inv):
    Param = inv.env["ir.config_parameter"].sudo()
    Param.set_param("cd_inventory.writeoff_dofa_controller_max", "1000000")
    big = _big(inv)
    count = _count_to_approval(inv, big, 0.0, inv.keeper)
    count.with_user(inv.controller).action_approve()
    assert count.state == "posted"  # within the raised controller limit
    Param.set_param("cd_inventory.writeoff_dofa_controller_max", "25000")
    Param.set_param("cd_inventory.writeoff_dofa_cfo_max", "100000")
    q = inv.quarantine(inv.keeper, qty=3.0)  # BDT 1,500: two persons
    assert q._dofa_current_tier() == "tier_0"
    big2 = inv.env["fix.spare.part"].create(
        {"name": "big2", "part_number": "A6E-" + inv.tag, "unit_cost": 50000.0}
    )
    inv.stock(big2, inv.central, 3.0, 50000.0)
    q2 = inv.quarantine(inv.keeper, qty=3.0, part=big2)  # BDT 150,000 > CFO ceiling
    assert q2._dofa_current_tier() == "tier_5"


def test_m15_24b_large_scrap_needs_the_routed_cfo_approval(inv):
    big = _big(inv)
    cfo = inv.cfo()
    q = inv.quarantine(inv.keeper, qty=2.0, part=big)
    q.with_user(inv.keeper).action_request_scrap()
    q.with_user(inv.controller).action_approve_scrap()
    assert q.state == "scrap_dofa" and inv.qty(big, inv.central, status="quarantine") == 2.0
    with pytest.raises(AssertionError):
        inv.approve_in_inbox(q, inv.keeper)  # the quarantiner gets no task
    inv.approve_in_inbox(q, cfo)
    assert q.state == "scrapped" and inv.qty(big, inv.central, status="quarantine") == 0.0
    assert q.dofa_approved_amount == 100000.0


# =================================================================== S0 archive
@pytest.fixture
def baseline(inv):
    env = inv.env
    company = env["res.company"].create({"name": "A06 S0 Co " + inv.tag})
    Suspense = env["fix.inventory.valuation.suspense"]

    def row(part, qty, cost, ref):
        return Suspense.create(
            {
                "company_id": company.id,
                "product_id": part.id,
                "quantity": qty,
                "unit_cost": cost,
                "entry_type": "initial_count",
                "name": ref,
            }
        )

    groups = {
        "a": [row(inv.part, 10.0, 500.0, "VAL-INIT-A-" + inv.tag) for _ in range(4)],
        "b": [row(inv.spart, 2.0, 8000.0, "VAL-INIT-B-" + inv.tag) for _ in range(4)],
        "single": [row(inv.part, 1.0, 100.0, "VAL-INIT-C-" + inv.tag)],
    }
    finance = inv.user("finance", FINANCE_ADMIN)
    return inv, company, groups, finance


def test_s0_archive_requires_finance_authority_and_reference(baseline):
    inv, company, _groups, finance = baseline
    Suspense = inv.env["fix.inventory.valuation.suspense"]
    for user in (inv.keeper, inv.controller):
        refused(
            inv,
            lambda u=user: Suspense.with_user(u).action_archive_duplicate_baseline(
                company.id, "FIN-1"
            ),
            "Accounting Administrator",
        )
    refused(
        inv,
        lambda: Suspense.with_user(finance).action_archive_duplicate_baseline(company.id, " "),
        "Finance approval reference",
    )


def test_s0_archive_keeps_one_row_per_group_and_records_the_authority(baseline):
    inv, company, groups, finance = baseline
    Suspense = inv.env["fix.inventory.valuation.suspense"]
    before = Suspense.get_baseline_integrity([company.id])["companies"][0]
    assert before["dedup_available"] and before["duplicate_extra_rows"] == 6
    out = Suspense.with_user(finance).action_archive_duplicate_baseline(company.id, "FIN/2026/77")
    assert (out["archived_rows"], out["archived_value"], out["groups"]) == (6, 63000.0, 2)
    for key in ("a", "b"):
        keep, *extras = groups[key]
        assert keep.status == "pending_gl_cutover"
        for extra in extras:
            assert (
                extra.status,
                extra.archive_ref,
                extra.archived_by_id,
                extra.duplicate_of_id,
            ) == (
                "archived",
                "FIN/2026/77",
                finance,
                keep,
            )
            assert extra.exists()  # archived, never deleted
    assert groups["single"][0].status == "pending_gl_cutover"
    after = Suspense.get_baseline_integrity([company.id])["companies"][0]
    assert not after["dedup_available"] and after["baseline_total"] == 5000.0 + 16000.0 + 100.0
    assert inv.events("inventory.baseline_deduplicated") >= 1
    # idempotent
    again = Suspense.with_user(finance).action_archive_duplicate_baseline(company.id, "FIN/2026/78")
    assert again["archived_rows"] == 0
    assert {e.archive_ref for e in groups["a"][1:]} == {"FIN/2026/77"}
    # the M19 cutover reads only pending rows: the archived copies are not cleared
    pending = Suspense.search(
        [("company_id", "=", company.id), ("status", "=", "pending_gl_cutover")]
    )
    assert round(sum(pending.mapped("total_valuation")), 2) == 21100.0
    # nobody retypes the archive evidence
    refused(inv, lambda: groups["a"][1].with_user(finance).write({"status": "pending_gl_cutover"}))


def test_s0_archive_refused_when_a_copy_was_reconciled(baseline):
    inv, company, groups, finance = baseline
    groups["a"][0].action_reconcile_to_gl("JV/CUTOVER/1")  # trusted cutover path
    Suspense = inv.env["fix.inventory.valuation.suspense"]
    assert not Suspense.get_baseline_integrity([company.id])["companies"][0]["dedup_available"]
    refused(
        inv,
        lambda: Suspense.with_user(finance).action_archive_duplicate_baseline(company.id, "FIN-9"),
        "reconciled",
    )
    assert {e.status for e in groups["b"]} == {"pending_gl_cutover"}  # nothing archived
