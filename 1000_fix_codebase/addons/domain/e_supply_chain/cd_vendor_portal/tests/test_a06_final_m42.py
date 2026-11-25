# A06 final pass, M42 controls: the scorer never approves, screening must be
# cleared rather than merely not hit, block and sanctions clearance belong to the
# CFO or CEO, a critical risk after activation counts, the CAR verifier is not its
# actioner, verification needs the file itself, the PO category gate and the
# review cadence. Each attack runs as a non-admin user with the real role; each
# control also has its proper path. Rolled back.
import base64
import types
from datetime import timedelta

import pytest
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.exceptions import UserError

GS = "cd_vendor_portal.group_fix_supplier_steward"
GSA = "cd_vendor_portal.group_fix_supplier_approver"
GB = "cd_requisition.group_fix_procurement_buyer"
T4 = "cd_entity_config.group_dofa_tier_4"
T5 = "cd_entity_config.group_dofa_tier_5"
DOCS = ("trade_licence", "tin", "vat")
REQUIRED = ("sanctions", "coi", "abac")
PDF = base64.b64encode(b"%PDF-1.4 a06 final test document")
PDF2 = base64.b64encode(b"%PDF-1.4 another document altogether")
PARAM_TYPES = "cd_vendor_portal.required_screening_types"
PARAM_TIERS = "cd_vendor_portal.qualification_tier_by_risk"
PARAM_CATEGORY = "cd_vendor_portal.po_category_gate"
PARAM_CADENCE = "cd_vendor_portal.review_cadence_months"


def _user(env, login, groups=()):
    ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    return (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": login,
                "login": login,
                "group_ids": [
                    (6, 0, [env.ref("base.group_user").id] + [env.ref(g).id for g in groups])
                ],
                "assigned_operating_unit_ids": [(6, 0, ou.ids)],
                "default_operating_unit_id": ou.id,
            }
        )
    )


@pytest.fixture
def c(odoo_env):
    env = odoo_env
    x = types.SimpleNamespace(env=env, n=0)
    x.today = fields.Date.context_today(env["fix.supplier"])
    x.ou = env["operating.unit"].search([("company_id", "=", env.company.id)], limit=1)
    x.plain = _user(env, "a06f42_plain")
    x.steward = _user(env, "a06f42_steward", [GS])
    x.steward2 = _user(env, "a06f42_steward2", [GS])
    x.approver = _user(env, "a06f42_approver", [GSA])
    x.approver2 = _user(env, "a06f42_approver2", [GSA])
    x.cfo = _user(env, "a06f42_cfo", [T4])
    x.ceo = _user(env, "a06f42_ceo", [T5])
    x.cfo_approver = _user(env, "a06f42_cfo_approver", [GSA, T4])
    x.buyer = _user(env, "a06f42_buyer", [GB])
    x.categ = env["product.category"].create({"name": "A06F42 Parts"})
    x.child = env["product.category"].create({"name": "A06F42 Sub", "parent_id": x.categ.id})
    x.other = env["product.category"].create({"name": "A06F42 Stationery"})
    x.prod = env["product.product"].create({"name": "A06F42 Part", "categ_id": x.child.id})
    x.pen = env["product.product"].create({"name": "A06F42 Pen", "categ_id": x.other.id})
    return x


def supplier(c, **kw):
    c.n += 1
    partner = c.env["res.partner"].create({"name": "A06F42 Supplier %d" % c.n, "is_company": True})
    vals = {"name": partner.name, "partner_id": partner.id}
    vals.update(kw)
    return c.env["fix.supplier"].with_user(c.steward).create(vals)


def docs(c, s):
    out = c.env["fix.supplier.document"]
    for doc_type in DOCS:
        out |= (
            c.env["fix.supplier.document"]
            .with_user(c.steward)
            .create(
                {
                    "supplier_id": s.id,
                    "doc_type": doc_type,
                    "number": "%s-%s" % (doc_type, s.id),
                    "file": PDF,
                    "file_filename": "%s.pdf" % doc_type,
                    "valid_to": c.today + timedelta(days=365),
                }
            )
        )
    out.with_user(c.steward2).action_verify()
    return out


def screen(c, s, types_=REQUIRED):
    out = c.env["fix.supplier.screening"]
    for key in types_:
        rec = (
            c.env["fix.supplier.screening"]
            .with_user(c.steward)
            .create({"supplier_id": s.id, "screening_type": key, "result": "clear"})
        )
        # A06 P20: a second person clears what the steward recorded
        rec.with_user(c.approver).action_clear()
        out |= rec
    return out


def qual(c, s, score=80, approve=True):
    q = (
        c.env["fix.supplier.qualification"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "score": score})
    )
    if approve:
        q.with_user(c.steward).action_start()
        q.with_user(c.approver).action_approve()
    return q


def gate(c, s, q):
    return (
        c.env["fix.supplier.activation"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "qualification_id": q.id})
    )


def active_supplier(c, **kw):
    s = supplier(c, **kw)
    docs(c, s)
    screen(c, s)
    gate(c, s, qual(c, s)).with_user(c.approver).action_activate()
    assert s.status == "active"
    return s


def hit(c, s, key="sanctions", flag=True):
    rec = (
        c.env["fix.supplier.screening"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "screening_type": key, "result": "hit"})
    )
    if flag:
        rec.with_user(c.steward2).action_flag()
    return rec


def risk(c, s, likelihood=5, impact=5):
    return (
        c.env["fix.supplier.risk"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "likelihood": likelihood, "impact": impact})
    )


# ------------------------------------------------- B3: scorer is not approver
def test_b3_an_approver_who_edits_the_score_cannot_approve_it(c):
    s = supplier(c)
    q = qual(c, s, score=40, approve=False)
    q.with_user(c.steward).action_start()
    assert q.scored_by_id == c.steward
    q.with_user(c.approver).write({"score": 95})
    assert q.scored_by_id == c.approver
    with pytest.raises(UserError, match="Segregation of duties"):
        q.with_user(c.approver).action_approve()
    assert q.state == "in_review"
    q.with_user(c.approver2).action_approve()
    assert q.state == "approved" and q.approved_by_id == c.approver2


def test_b3_the_form_echoing_the_score_stamps_nobody(c):
    q = qual(c, supplier(c), approve=False)
    q.with_user(c.approver).write({"score": 80.0, "notes": "reviewed the file"})
    assert q.scored_by_id == c.steward


def test_b3_the_scorer_stamp_cannot_be_typed(c):
    q = qual(c, supplier(c), approve=False)
    with pytest.raises(UserError, match="changes only through its workflow"):
        q.with_user(c.approver).write({"scored_by_id": c.steward2.id})


def test_b3_risk_tier_authority_is_off_until_configured(c):
    s = supplier(c, segment="strategic")
    qual(c, s)  # any Supplier Approver, by default
    assert s.status == "qualified"


def test_b3_configured_tier_is_required_of_a_strategic_supplier(c):
    c.env["ir.config_parameter"].sudo().set_param(PARAM_TIERS, "strategic:tier_4,critical:tier_4")
    s = supplier(c, segment="strategic")
    q = qual(c, s, approve=False)
    q.with_user(c.steward).action_start()
    with pytest.raises(UserError, match="tier 4"):
        q.with_user(c.approver).action_approve()
    q.with_user(c.cfo_approver).action_approve()
    assert q.state == "approved"
    # the band of an open risk counts as well
    t = supplier(c)
    risk(c, t)
    r = qual(c, t, approve=False)
    r.with_user(c.steward).action_start()
    with pytest.raises(UserError, match="tier 4"):
        r.with_user(c.approver).action_approve()
    # a low-risk transactional supplier is untouched
    qual(c, supplier(c))


# ------------------------------------------------- B4: cleared screening
def test_b4_no_screening_does_not_activate(c):
    s = supplier(c)
    docs(c, s)
    q = qual(c, s)
    with pytest.raises(UserError, match="no cleared Sanctions List screening"):
        gate(c, s, q).with_user(c.approver).action_activate()
    assert s.status == "qualified"


@pytest.mark.parametrize("missing", REQUIRED)
def test_b4_each_required_type_is_required(c, missing):
    s = supplier(c)
    docs(c, s)
    screen(c, s, [k for k in REQUIRED if k != missing])
    with pytest.raises(UserError, match="no cleared"):
        gate(c, s, qual(c, s)).with_user(c.approver).action_activate()
    assert s.status == "qualified"


def test_b4_a_pending_screening_does_not_count(c):
    s = supplier(c)
    docs(c, s)
    screen(c, s, ("coi", "abac"))
    c.env["fix.supplier.screening"].with_user(c.steward).create(
        {"supplier_id": s.id, "screening_type": "sanctions", "result": "pending"}
    )
    with pytest.raises(UserError, match="no cleared Sanctions"):
        gate(c, s, qual(c, s)).with_user(c.approver).action_activate()


def test_b4_all_cleared_activates_and_pep_is_not_required_by_default(c):
    assert active_supplier(c).status == "active"


def test_b4_the_types_are_configuration(c):
    c.env["ir.config_parameter"].sudo().set_param(PARAM_TYPES, "pep")
    s = supplier(c)
    docs(c, s)
    screen(c, s)
    with pytest.raises(UserError, match="no cleared PEP"):
        gate(c, s, qual(c, s)).with_user(c.approver).action_activate()
    c.env["ir.config_parameter"].sudo().set_param(PARAM_TYPES, "none")
    t = supplier(c)
    docs(c, t)
    gate(c, t, qual(c, t)).with_user(c.approver).action_activate()
    assert t.status == "active"


def test_b4_a_supplier_already_active_is_not_suspended_for_missing_screening(c):
    """The upgrade rule: only a new activation asks for it."""
    c.env["ir.config_parameter"].sudo().set_param(PARAM_TYPES, "none")
    s = supplier(c)
    docs(c, s)
    gate(c, s, qual(c, s)).with_user(c.approver).action_activate()
    c.env["ir.config_parameter"].sudo().set_param(PARAM_TYPES, "sanctions,coi,abac")
    assert not c.env["fix.purchase.order"]._fix_vendor_blockers(s.partner_id)
    c.env["fix.supplier"]._cron_lifecycle_sweep()
    assert s.status == "active"


# ------------------------------------------------- B5: CFO / CEO authority
@pytest.mark.parametrize("who", ["steward", "approver", "plain"])
def test_b5_only_cfo_or_ceo_blocks(c, who):
    s = active_supplier(c)
    with pytest.raises(UserError, match="Blocking a supplier needs"):
        s.with_user(getattr(c, who)).action_block(reason="Counterfeit batch reported")
    assert s.status == "active"


@pytest.mark.parametrize("who", ["cfo", "ceo"])
def test_b5_cfo_or_ceo_blocks_without_steward_rights(c, who):
    s = active_supplier(c)
    s.with_user(getattr(c, who)).action_block(reason="Counterfeit batch reported")
    assert s.status == "deactivated" and s.status_changed_by_id == getattr(c, who)


def test_b5_a_steward_still_suspends(c):
    s = active_supplier(c)
    s.with_user(c.steward).action_suspend(reason="Quality problem under review")
    assert s.status == "suspended"


def test_b5_a_flagged_sanctions_hit_blocks_whatever_the_status(c):
    for s in (active_supplier(c), supplier(c)):
        hit(c, s)
        assert s.status == "deactivated"


def test_b5_another_kind_of_hit_still_suspends(c):
    s = active_supplier(c)
    hit(c, s, key="abac")
    assert s.status == "suspended"


def test_b5_clearing_a_sanctions_hit_takes_cfo_authority_and_not_its_raiser(c):
    s = active_supplier(c)
    rec = hit(c, s)
    reason = "Name match only, passport differs: file 2211"
    with pytest.raises(UserError, match="Clearing a sanctions hit needs"):
        rec.with_user(c.approver).action_clear_hit(reason=reason)
    for who in (c.steward, c.steward2):  # recorded and flagged it, and now hold the authority
        who.write({"group_ids": [(4, c.env.ref(T4).id)]})
        with pytest.raises(UserError, match="Segregation of duties"):
            rec.with_user(who).action_clear_hit(reason=reason)
    assert rec.state == "flagged"
    rec.with_user(c.cfo).action_clear_hit(reason=reason)
    assert rec.state == "cleared" and rec.cleared_by_id == c.cfo and rec.result == "hit"
    assert s.status == "deactivated"  # clearing does not reinstate


def test_b5_a_blocked_supplier_returns_only_by_cfo_reinstatement(c):
    s = active_supplier(c)
    rec = hit(c, s)
    rec.with_user(c.cfo).action_clear_hit(reason="Name match only, passport differs: file 2211")
    s.with_user(c.steward).action_request_reinstatement(reason="False positive, cleared by CFO")
    with pytest.raises(UserError, match="CFO authority"):
        s.with_user(c.approver).action_approve_reinstatement()
    s.with_user(c.cfo_approver).action_approve_reinstatement()
    assert s.status == "active"


def test_b5_other_hits_are_still_cleared_by_an_approver(c):
    s = active_supplier(c)
    rec = hit(c, s, key="abac")
    with pytest.raises(UserError, match="Clearing a screening hit needs"):
        rec.with_user(c.steward).action_clear_hit(reason="Declaration corrected: file 2212")
    rec.with_user(c.approver).action_clear_hit(reason="Declaration corrected: file 2212")
    assert rec.state == "cleared"


# ------------------------------------------------- B7: critical risk after activation
def test_b7_a_critical_risk_stops_orders_at_once_and_the_sweep_suspends(c):
    s = active_supplier(c)
    Order = c.env["fix.purchase.order"]
    assert not Order._fix_vendor_blockers(s.partner_id)
    rec = risk(c, s)
    assert any("critical open risk" in p for p in Order._fix_vendor_blockers(s.partner_id))
    assert s.status == "active"
    out = c.env["fix.supplier"]._cron_lifecycle_sweep()
    assert s.id in out["suspended"] and s.status == "suspended"
    assert rec.name in s.status_reason


def test_b7_lower_and_mitigated_risks_do_not(c):
    s = active_supplier(c)
    risk(c, s, likelihood=3, impact=4)  # high, not critical
    mitigated = risk(c, s)
    mitigated.with_user(c.steward).write({"mitigation": "Second source contracted"})
    mitigated.with_user(c.steward).action_mitigate()
    assert not c.env["fix.purchase.order"]._fix_vendor_blockers(s.partner_id)
    c.env["fix.supplier"]._cron_lifecycle_sweep()
    assert s.status == "active"


# ------------------------------------------------- B8: CAR verifier
def _car(c, s):
    return (
        c.env["fix.supplier.car"]
        .with_user(c.steward)
        .create(
            {
                "supplier_id": s.id,
                "issue": "Late deliveries",
                "severity": "minor",
                "action_plan": "Weekly dispatch review",
                "due_date": c.today + timedelta(days=30),
            }
        )
    )


def test_b8_the_steward_who_actioned_a_car_cannot_close_it(c):
    car = _car(c, supplier(c))
    car.with_user(c.steward2).action_action()
    assert car.actioned_by_id == c.steward2
    with pytest.raises(UserError, match="Segregation of duties"):
        car.with_user(c.steward2).action_close()
    with pytest.raises(UserError, match="Segregation of duties"):
        car.with_user(c.steward).action_close()  # the raiser, as before
    with pytest.raises(UserError, match="changes only through its workflow"):
        car.with_user(c.steward2).write({"actioned_by_id": c.approver.id})
    assert car.state == "actioned"
    car.with_user(c.approver).action_close()
    assert car.state == "closed" and car.closed_by_id == c.approver


# ------------------------------------------------- B10: the file itself
def test_b10_a_typed_reference_is_not_a_file(c):
    s = supplier(c)
    doc = (
        c.env["fix.supplier.document"]
        .with_user(c.steward)
        .create(
            {
                "supplier_id": s.id,
                "doc_type": "tin",
                "number": "TIN-1",
                "file_ref": "dms://suppliers/typed",
            }
        )
    )
    with pytest.raises(UserError, match="uploaded file"):
        doc.with_user(c.steward2).action_verify()
    assert doc.state == "pending"
    doc.with_user(c.steward).write({"file": PDF, "file_filename": "tin.pdf"})
    doc.with_user(c.steward2).action_verify()
    assert doc.state == "valid" and doc.is_valid


def test_b10_a_number_is_still_required(c):
    doc = (
        c.env["fix.supplier.document"]
        .with_user(c.steward)
        .create({"supplier_id": supplier(c).id, "doc_type": "tin", "file": PDF})
    )
    with pytest.raises(UserError, match="number"):
        doc.with_user(c.steward2).action_verify()


def test_b10_another_file_returns_it_to_pending_but_the_form_echo_does_not(c):
    s = active_supplier(c)
    doc = s.env["fix.supplier.document"].search(
        [("supplier_id", "=", s.id), ("doc_type", "=", "tin")]
    )
    doc.with_user(c.steward).write({"file": PDF.decode(), "file_filename": "tin.pdf"})
    assert doc.state == "valid" and s.status == "active"
    doc.with_user(c.steward).write({"file": PDF2.decode()})
    assert doc.state == "pending" and not doc.verified_by_id
    assert s.status == "suspended"


def test_b10_removing_the_file_returns_it_to_pending(c):
    s = active_supplier(c)
    doc = s.env["fix.supplier.document"].search(
        [("supplier_id", "=", s.id), ("doc_type", "=", "vat")]
    )
    doc.with_user(c.steward).write({"file": False})
    assert doc.state == "pending"


def test_b10_a_document_verified_before_this_rule_stays_valid(c):
    """No stored row breaks: a valid document with only a typed reference."""
    s = supplier(c)
    doc = c.env["fix.supplier.document"].create(
        {
            "supplier_id": s.id,
            "doc_type": "tin",
            "number": "OLD-1",
            "file_ref": "dms://old",
            "state": "valid",
        }
    )
    assert doc.is_valid


# ------------------------------------------------- B14: PO category gate
def _po(c, vendor, product):
    return (
        c.env["fix.purchase.order"]
        .with_user(c.buyer)
        .create(
            {
                "operating_unit_id": c.ou.id,
                "vendor_id": vendor.id,
                "no_requisition_exception": False,
                "line_ids": [(0, 0, {"product_id": product.id, "qty_ordered": 1, "unit_price": 9})],
            }
        )
    )


def _ask(c, po):
    po.sudo().action_record_requisition_exception(reason="A06F42 test PO, no requisition")
    po.with_user(c.buyer).action_submit_for_approval(justification="A06F42 stock")


def test_b14_gate_is_on_by_default(c):
    # A06 P08 (lead default, owner O4): on unless the parameter says "0"
    c.env["ir.config_parameter"].sudo().search([("key", "=", PARAM_CATEGORY)]).unlink()
    s = active_supplier(c)
    tier2 = _user(c.env, "a06f42_t2", ["cd_entity_config.group_dofa_tier_2"])
    assert tier2
    with pytest.raises(UserError, match="BRU-PRO-02"):
        _ask(c, _po(c, s.partner_id, c.pen))


def test_b14_switched_on_it_compares_the_po_with_the_approved_categories(c):
    c.env["ir.config_parameter"].sudo().set_param(PARAM_CATEGORY, "1")
    _user(c.env, "a06f42_t2", ["cd_entity_config.group_dofa_tier_2"])
    s = active_supplier(c)
    # fail closed: nothing approved, nothing supplied
    with pytest.raises(UserError, match="BRU-PRO-02"):
        _ask(c, _po(c, s.partner_id, c.prod))
    # A06 P08: the categories come from an approved qualification, not a typed edit
    with pytest.raises(UserError):
        s.with_user(c.steward).write({"approved_category_ids": [(6, 0, c.categ.ids)]})
    q = (
        c.env["fix.supplier.qualification"]
        .with_user(c.steward)
        .create({"supplier_id": s.id, "score": 90, "category_ids": [(6, 0, c.categ.ids)]})
    )
    q.with_user(c.steward).action_start()
    q.with_user(c.approver).action_approve()
    _ask(c, _po(c, s.partner_id, c.prod))  # a child of the approved category
    with pytest.raises(UserError, match="A06F42 Stationery"):
        _ask(c, _po(c, s.partner_id, c.pen))


# ------------------------------------------------- B15: review cadence
def test_b15_cadence_schedules_a_review_once_by_segment(c):
    Supplier = c.env["fix.supplier"]
    s = active_supplier(c, segment="strategic")
    p = active_supplier(c, segment="preferred")
    t = active_supplier(c, segment="transactional")
    s.write({"onboarded_on": c.today - relativedelta(months=4)})
    p.write({"onboarded_on": c.today - relativedelta(months=4)})
    t.write({"onboarded_on": c.today - relativedelta(years=4)})
    made = Supplier._cron_review_cadence()
    mine = made.filtered(lambda r: r.supplier_id in (s | p | t))
    assert mine.supplier_id == s and mine.review_type == "quarterly"
    assert mine.state == "scheduled"
    assert not Supplier._cron_review_cadence().filtered(lambda r: r.supplier_id == s)  # once
    p.write({"onboarded_on": c.today - relativedelta(months=7)})
    half = Supplier._cron_review_cadence().filtered(lambda r: r.supplier_id == p)
    assert half.review_type == "half_yearly"


def test_b15_the_next_review_counts_from_the_last_held(c):
    Supplier = c.env["fix.supplier"]
    s = active_supplier(c, segment="strategic")
    s.write({"onboarded_on": c.today - relativedelta(months=4)})
    review = Supplier._cron_review_cadence().filtered(lambda r: r.supplier_id == s)
    review.with_user(c.steward).write({"review_date": c.today - relativedelta(months=1)})
    review.with_user(c.steward).action_complete()
    assert not Supplier._cron_review_cadence().filtered(lambda r: r.supplier_id == s)
    review.sudo().write({"review_date": c.today - relativedelta(months=3)})
    assert Supplier._cron_review_cadence().filtered(lambda r: r.supplier_id == s)


def test_b15_a_suspended_supplier_gets_no_review_and_cadence_is_configuration(c):
    Supplier = c.env["fix.supplier"]
    s = active_supplier(c, segment="strategic")
    s.write({"onboarded_on": c.today - relativedelta(months=4)})
    s.with_user(c.steward).action_suspend(reason="Quality problem under review")
    assert not Supplier._cron_review_cadence().filtered(lambda r: r.supplier_id == s)
    t = active_supplier(c, segment="transactional")
    t.write({"onboarded_on": c.today - relativedelta(months=13)})
    c.env["ir.config_parameter"].sudo().set_param(PARAM_CADENCE, "transactional:12")
    annual = Supplier._cron_review_cadence().filtered(lambda r: r.supplier_id == t)
    assert annual.review_type == "annual"
