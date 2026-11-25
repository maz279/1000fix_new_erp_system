"""A08 M20-F4 / CD-M20-04 (2026-11-23): the billable-event queue beyond
closed service orders.

working/A2/FINDINGS.md M20-F4: the queue declared subscription and brand_claim
sources but the intake drained only service_order.closed and the generate
action refused every other source, so subscription/AMC money and approved
warranty recoveries could never be invoiced from the queue, and the
delivered-but-unbilled reconciliation never counted them.

This suite proves the fix:
  * a due subscription cycle becomes exactly one queue row (period in the
    description) and a re-run creates none;
  * a recoverable claim becomes one row addressed to the brand partner;
  * the leakage reconciliation counts a due period with no invoice;
  * invoicing a queue row still goes through the source module's own path
    (fix.subscription.charge._create_invoice), never a new shortcut;
  * a cancelled queue row does not reappear.

``odoo_env`` rolls back after each test.
"""

import uuid
from datetime import timedelta
from types import SimpleNamespace

import pytest
from odoo import fields

pytestmark = [pytest.mark.financial]

TAG = uuid.uuid4().hex[:6].upper()


@pytest.fixture
def world(odoo_env):
    """A private company, its operating unit and a customer: the subscription
    stream's world (the claim test uses cd_warranty_claims' ``w`` fixture)."""
    env = odoo_env
    company = env["res.company"].create({"name": "M20 Streams %s Co" % TAG})
    envc = env(context=dict(env.context, allowed_company_ids=company.ids))
    ou = envc["operating.unit"].create(
        {
            "name": "OU Streams %s" % TAG,
            "code": "ST-%s" % TAG[:4],
            "company_id": company.id,
            "partner_id": company.partner_id.id,
        }
    )
    customer = envc["res.partner"].create({"name": "Streams Customer %s" % TAG})
    today = fields.Date.context_today(envc["fix.subscription"])
    return SimpleNamespace(env=envc, company=company, ou=ou, customer=customer, today=today)


def _sub(world, amount=3000.0, **kw):
    """An active monthly subscription whose next cycle starts today: due
    (subscriptions bill in advance) and ending inside the term."""
    vals = {
        "name": "M20 stream sub %s" % TAG,
        "company_id": world.company.id,
        "customer_id": world.customer.id,
        "operating_unit_id": world.ou.id,
        "plan": "standard",
        "billing_cycle": "monthly",
        "recurring_amount": amount,
        "start_date": world.today,
        "next_invoice_date": world.today,
        "state": "active",
    }
    vals.update(kw)
    return world.env["fix.subscription"].create(vals)


def _rows(world, sub):
    return (
        world.env["fix.billable.event"]
        .sudo()
        .search(
            [
                ("source_type", "=", "subscription"),
                ("source_model", "=", "fix.subscription"),
                ("source_id", "=", sub.id),
            ],
            order="period_start",
        )
    )


def _charges(world, sub):
    return (
        world.env["fix.subscription.charge"]
        .sudo()
        .search([("subscription_id", "=", sub.id)], order="id")
    )


def _invoices(world, sub):
    charges = _charges(world, sub)
    return (
        world.env["fix.ar.invoice"]
        .sudo()
        .search(
            [
                ("source_model", "=", "fix.subscription.charge"),
                ("source_id", "in", charges.ids),
            ],
            order="id",
        )
    )


# ------------------------------------------------------------------ (a)
def test_a_due_subscription_period_queues_exactly_once(world):
    sub = _sub(world)
    Queue = world.env["fix.billable.event"].sudo()
    Queue._cron_intake_streams()

    rows = _rows(world, sub)
    assert len(rows) == 1
    row = rows
    assert row.state == "new"
    assert row.period_start == sub.next_invoice_date
    assert sub.next_invoice_date <= row.period_end
    # the period is in the description, as finance sees it
    assert str(row.period_start) in (row.description or "")
    assert str(row.period_end) in (row.description or "")
    assert row.amount == 3000.0
    assert row.company_id == world.company
    assert row.customer_id == world.customer
    # intake queues the candidate only; nothing is invoiced yet
    assert not _charges(world, sub)
    assert not _invoices(world, sub)

    # a re-run for the same (stream, document, period) is a no-op
    Queue._cron_intake_streams()
    assert len(_rows(world, sub)) == 1


# ------------------------------------------------------------------ (b)
def test_a_recoverable_claim_queues_to_the_brand_partner(w):
    env = w.env
    oem = env["res.partner"].create({"name": "OEM %s" % w.brand.name, "ref": w.brand.code})
    claim = w.full_pack(w.claim(amount=12500.0))
    claim.with_user(w.clerk).action_submit()
    claim.action_decide(approved=True)  # the brand-API path (superuser only)
    claim.invalidate_recordset()
    assert claim.state == "approved" and claim.approved_amount == 12500.0
    assert not env["fix.a04.claim.consumers"]._claim_invoices(claim)

    Queue = env["fix.billable.event"].sudo()
    Queue._cron_intake_streams()
    rows = Queue.search([("source_type", "=", "brand_claim"), ("source_id", "=", claim.id)])
    assert len(rows) == 1
    row = rows
    assert row.customer_id == oem  # the brand's billing partner, not the device owner
    assert row.amount == 12500.0
    assert claim.claim_no in (row.description or "")
    # nothing is invoiced until the queue's own action runs
    assert (
        not env["fix.ar.invoice"]
        .sudo()
        .search([("source_model", "=", claim._name), ("source_id", "=", claim.id)])
    )

    row.action_generate_invoice()
    assert row.state == "invoiced" and row.invoice_id
    assert row.invoice_id.customer_id == oem
    assert row.invoice_id.state == "draft"
    assert len(env["fix.a04.claim.consumers"]._claim_invoices(claim)) == 1

    # a replay (intake and generation) never raises a second invoice
    Queue._cron_intake_streams()
    assert (
        Queue.search_count([("source_type", "=", "brand_claim"), ("source_id", "=", claim.id)]) == 1
    )
    row.action_generate_invoice()
    assert len(env["fix.a04.claim.consumers"]._claim_invoices(claim)) == 1


def test_a_claim_without_an_oem_billing_partner_is_queued_not_crashing(w):
    """A brand with no legal entity is a finance follow-up, not a cron crash.

    The hourly intake used to raise AttributeError on customer=False
    (``'bool' object has no attribute 'id'``), so one unlinked brand stopped
    every subscription, contract and claim intake in the same run.
    """
    env = w.env
    claim = w.full_pack(w.claim(brand_rec=w.other_brand, amount=5000.0))
    claim.with_user(w.clerk).action_submit()
    claim.action_decide(approved=True)
    claim.invalidate_recordset()
    assert claim.state == "approved"
    assert not w.other_brand.billing_partner()

    Queue = env["fix.billable.event"].sudo()
    Queue._cron_intake_streams()
    row = Queue.search([("source_type", "=", "brand_claim"), ("source_id", "=", claim.id)])
    assert len(row) == 1
    assert not row.customer_id
    assert "link the brand's legal entity" in (row.amount_note or "")


def test_a_claim_the_side_consumer_already_invoiced_is_registered(w):
    """The finding's other half: an invoice the A04 C7 consumer raised is
    registered on a queue row with state=invoiced - visible to the stream's
    KPI and never raised a second time."""
    env = w.env
    oem = env["res.partner"].create({"name": "OEM %s" % w.brand.name, "ref": w.brand.code})
    claim = w.full_pack(w.claim(amount=9000.0))
    claim.with_user(w.clerk).action_submit()
    claim.action_decide(approved=True)
    claim.invalidate_recordset()
    env["fix.a04.claim.consumers"].sudo().consume_warranty_claim_decided(
        {"aggregate": claim._name, "aggregate_id": claim.id, "payload": {}}
    )
    (invoice,) = env["fix.a04.claim.consumers"]._claim_invoices(claim)
    assert invoice.customer_id == oem and invoice.state == "draft"

    Queue = env["fix.billable.event"].sudo()
    Queue._cron_intake_streams()
    row = Queue.search([("source_type", "=", "brand_claim"), ("source_id", "=", claim.id)])
    assert len(row) == 1
    assert row.state == "invoiced" and row.invoice_id == invoice
    row.action_generate_invoice()  # a replay is a no-op
    assert len(env["fix.a04.claim.consumers"]._claim_invoices(claim)) == 1


# ------------------------------------------------------------------ (c)
def test_the_unbilled_reconciliation_counts_a_period_with_no_invoice(world):
    from odoo.addons.cd_billing_engine.models.fix_ar_engine import compute_leakage

    sub = _sub(world)
    start = sub.next_invoice_date
    leak = compute_leakage(world.env, company_id=world.company.id)
    mine = [
        row
        for row in leak["unbilled_periods"]
        if row["source_model"] == "fix.subscription" and row["source_id"] == sub.id
    ]
    assert len(mine) == 1
    assert mine[0]["period_start"] == str(start)
    assert mine[0]["amount"] == 3000.0
    assert "periods without an invoice" in leak["basis"]

    # queue it, invoice it through the queue, and the period is no longer a gap
    Queue = world.env["fix.billable.event"].sudo()
    Queue._cron_intake_streams()
    _rows(world, sub).action_generate_invoice()
    leak = compute_leakage(world.env, company_id=world.company.id)
    assert not [
        row
        for row in leak["unbilled_periods"]
        if row["source_model"] == "fix.subscription"
        and row["source_id"] == sub.id
        and row["period_start"] == str(start)
    ]


# ------------------------------------------------------------------ (c) daily
def test_the_daily_reconciliation_raises_and_clears_a_period_exception(world):
    sub = _sub(world)
    Ubx = world.env["fix.ar.unbilled.exception"].sudo()
    Ubx._cron_reconcile()
    exc = Ubx.search([("source_model", "=", "fix.subscription"), ("source_id", "=", sub.id)])
    assert len(exc) == 1
    assert exc.source_module == "subscription"
    assert exc.detected_by == "reconciliation"
    assert exc.estimated_value == 3000.0
    assert exc.state in ("open", "escalated")

    Queue = world.env["fix.billable.event"].sudo()
    Queue._cron_intake_streams()
    _rows(world, sub).action_generate_invoice()
    Ubx._cron_reconcile()
    exc.invalidate_recordset()
    assert exc.state == "resolved" and exc.resolution == "invoiced" and exc.invoice_id


# ------------------------------------------------------------------ (d)
def test_invoicing_goes_through_the_source_modules_generate_path(world):
    sub = _sub(world)
    Queue = world.env["fix.billable.event"].sudo()
    Queue._cron_intake_streams()
    row = _rows(world, sub)
    assert row.state == "new" and not _invoices(world, sub)

    row.action_generate_invoice()
    (charge,) = _charges(world, sub)
    assert row.state == "invoiced"
    assert row.invoice_id == charge.invoice_id
    # the existing subscription path made it: the charge and its invoice
    assert row.invoice_id.source_model == charge._name
    assert row.invoice_id.source_id == charge.id
    assert (row.invoice_id.manual_reason or "").startswith("Subscription cycle charge")
    assert row.invoice_id.state == "draft"  # issue stays finance's own action

    # the subscription's own billing run will not re-bill the cycle
    assert sub.next_invoice_date > row.period_end


# ------------------------------------------------------------------ (e)
def test_a_cancelled_queue_row_does_not_reappear(world):
    sub = _sub(world)
    Queue = world.env["fix.billable.event"].sudo()
    Queue._cron_intake_streams()
    row = _rows(world, sub)
    assert row.state == "new"

    row.action_cancel()
    assert row.state == "cancelled"

    Queue._cron_intake_streams()
    rows = _rows(world, sub)
    assert len(rows) == 1
    assert rows.state == "cancelled"
    assert not _invoices(world, sub)


# ------------------------------------------------------------------ every
def test_every_missed_cycle_of_a_due_subscription_is_queued(world):
    """FR-ARB-002: one queue row per due period - a subscription the billing
    run missed for a quarter still owes three cycles, not only the next."""
    start = world.today - timedelta(days=95)
    sub = _sub(world, start_date=start, next_invoice_date=start)
    Queue = world.env["fix.billable.event"].sudo()
    Queue._cron_intake_streams()
    rows = _rows(world, sub)
    assert len(rows) >= 2
    assert len(set(rows.mapped("period_start"))) == len(rows)
    assert rows[0].period_start == start


# ------------------------------------------------------------------ contract
def _contract(world):
    """An active AMC contract whose first monthly period has ended (the
    walker suite's world, on the private company)."""
    env = world.env
    officer = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Stream contract officer %s" % TAG,
                "login": "stream_contract_%s" % TAG,
                "group_ids": [
                    (
                        6,
                        0,
                        [
                            env.ref("base.group_user").id,
                            env.ref("cd_contract_core.group_contract_officer").id,
                        ],
                    )
                ],
                "assigned_operating_unit_ids": [(6, 0, world.ou.ids)],
                "default_operating_unit_id": world.ou.id,
            }
        )
    )
    contract = (
        env["fix.contract"]
        .with_user(officer)
        .create(
            {
                "name": "Stream AMC %s" % TAG,
                "family": "amc",
                "customer_id": world.customer.id,
                "operating_unit_id": world.ou.id,
                "date_start": world.today - timedelta(days=35),
                "date_end": world.today + timedelta(days=300),
                "annual_value": 120000.0,
                "stamp_duty_cert_no": "SD-%s" % TAG,
                "stamp_duty_amount": 300.0,
                "has_signed_contract_doc": True,
            }
        )
    )
    contract.sudo().action_activate()
    contract.invalidate_recordset()
    assert contract.state == "active"
    return contract


def test_a_due_contract_period_queues_and_invoices_through_the_walker(world):
    contract = _contract(world)
    Queue = world.env["fix.billable.event"].sudo()
    Queue._cron_intake_streams()
    rows = Queue.search(
        [
            ("source_type", "=", "contract_period"),
            ("source_model", "=", "fix.contract"),
            ("source_id", "=", contract.id),
        ],
        order="period_start",
    )
    assert len(rows) == 1  # one ended monthly period (the second is still running)
    row = rows
    assert str(row.period_start) in (row.description or "")
    assert str(row.period_end) in (row.description or "")
    assert row.amount > 0

    row.action_generate_invoice()
    assert row.state == "invoiced" and row.invoice_id
    assert row.invoice_id.source_model == "fix.contract.billing.period"
    assert row.invoice_id.state == "draft"
    assert contract.billed_through_date == row.period_end


# ------------------------------------------------------------------ no price
def test_a_period_without_a_price_queues_at_zero_with_a_note(world):
    sub = _sub(world, recurring_amount=0.0)
    Queue = world.env["fix.billable.event"].sudo()
    Queue._cron_intake_streams()
    row = _rows(world, sub)
    assert len(row) == 1
    assert row.amount == 0.0
    assert "recurring amount" in (row.amount_note or "")
    assert "FR-ARB-002/003" in (row.amount_note or "")
    row.action_generate_invoice()
    assert row.state == "failed"
    assert "no agreed recurring amount" in (row.last_error or "")
    assert "FR-ARB-002/003" in (row.last_error or "")
