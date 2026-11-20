"""A04 ERP audit (20 Nov 2026), stream B4: what a marketplace commission now
needs before it is awarded, earned and accrued (set up as the superuser -
configuration and the customer's payment, not the behaviour under test):

  M12-F4  a seller commission scheme in force (M53) before any award;
  M12-F1  the customer's money received in M20: a confirmed fix.ar.receipt
          of the order's customer linked to the order; the accrual debits that
          collection (role marketplace_collections), never the cash
          "clearing" role;
  M12-F9  the declared M51 marketplace VAT model (D-03, agent): output VAT on
          the commission is booked and deducted from the seller's share.
"""

import itertools

from odoo import fields

_SEQ = itertools.count(1)

COLLECTIONS_PARAM = "cd_settlement_ext.account_code.marketplace_collections"
VAT_PARAM = "cd_billing_engine.account_code.vat_output"
VAT_CODE = "209902"
VAT_RATE = 15.0


def seller_scheme(env, company=None, rate=0.0):
    """The seller commission scheme in force (rate 0: the order's own rate)."""
    company = company or env.company
    Scheme = env["fix.commission.scheme"].sudo()
    today = fields.Date.context_today(Scheme)
    found = Scheme._find("seller", today, company)
    if found:
        return found
    return Scheme.create(
        {
            "name": "B4 seller scheme %d" % next(_SEQ),
            "company_id": company.id,
            "scheme_type": "seller",
            "commission_rate": rate,
            "date_from": today.replace(day=1),
        }
    )


def marketplace_vat_model(env, company=None, rate=VAT_RATE):
    """The declared M51 agent position of `company` (its adviser / CFO
    sign-off is M51's own suite), and the output VAT account it posts to."""
    company = company or env.company
    Model = env["fix.marketplace.tax.model"].sudo()
    on = fields.Date.context_today(Model)
    found = Model.search(
        [("company_id", "=", company.id), ("state", "=", "active"), ("date_from", "<=", on)],
        limit=1,
    )
    if not found:
        found = Model.create(
            {
                "company_id": company.id,
                "model": "agent",
                "rate": rate,
                "external_opinion_ref": "B4-D03-%d" % next(_SEQ),
                "date_from": "2026-01-01",
            }
        )
        env.flush_all()
        env.cr.execute(
            "UPDATE fix_marketplace_tax_model SET state='active', signoff_state='signed', "
            "verify_with_adviser=false WHERE id=%s",
            (found.id,),
        )
        env.invalidate_all()
    Account = env["account.account"].sudo().with_company(company)
    if not Account.search([("code", "=", VAT_CODE), ("company_ids", "in", company.id)], limit=1):
        Account.create(
            {
                "code": VAT_CODE,
                "name": "B4 VAT Output",
                "account_type": "liability_current",
                "company_ids": [(6, 0, company.ids)],
            }
        )
    env["ir.config_parameter"].sudo().set_param(VAT_PARAM, VAT_CODE)
    return found


def marketplace_accrual_ready(env, company=None, collections_code="101000"):
    """VAT position and collections role only: for ledger rows raised by hand
    whose typed TDS must stand (no scheme in force re-measures it)."""
    company = company or env.company
    marketplace_vat_model(env, company)
    env["ir.config_parameter"].sudo().set_param(COLLECTIONS_PARAM, collections_code)


def marketplace_ready(env, company=None, collections_code="101000"):
    """Scheme, VAT position and the collections account role of `company`."""
    company = company or env.company
    seller_scheme(env, company)
    marketplace_vat_model(env, company)
    env["ir.config_parameter"].sudo().set_param(COLLECTIONS_PARAM, collections_code)


def paid_order(env, seller_partner, gross, rate, company=None, operating_unit=None):
    """A commissioned marketplace order of `gross` at `rate` whose customer
    paid it into M20 (a confirmed receipt), the source a ledger row needs."""
    company = company or env.company
    customer = env["res.partner"].sudo().create({"name": "B4 MKT customer %d" % next(_SEQ)})
    order = (
        env["fix.marketplace.order"]
        .sudo()
        .create(
            {
                "company_id": company.id,
                "operating_unit_id": operating_unit.id if operating_unit else False,
                "customer_id": customer.id,
                "description": "B4 marketplace job",
                "customer_consent": True,
                "consent_method": "signed",
            }
        )
    )
    receipt = (
        env["fix.ar.receipt"]
        .sudo()
        .create(
            {
                "company_id": company.id,
                "customer_id": customer.id,
                "amount": gross,
                "method": "bkash",
                "reference": "B4-MKT-%d" % next(_SEQ),
                "state": "confirmed",
            }
        )
    )
    order._guarded().write(
        {
            "state": "commissioned",
            "awarded_price": gross,
            "commission_rate": rate,
            "commission_amount": round(gross * rate, 2),
            "customer_receipt_id": receipt.id,
            "customer_paid_at": fields.Datetime.now(),
        }
    )
    return order


def link_paid_order(row):
    """Give a hand-raised ledger row its paid source order (same payee,
    gross and rate), as commission.earned would have."""
    row = row.sudo()
    order = paid_order(
        row.env,
        row.seller_partner_id,
        row.gross_amount,
        row.commission_rate,
        company=row.company_id,
        operating_unit=row.operating_unit_id or None,
    )
    row._guarded().write({"marketplace_order_id": order.id})
    return order


def link_receipt(env, order, amount=None):
    """Link a confirmed M20 receipt of the order's customer to an order that
    reached the ledger through its own workflow."""
    order = order.sudo()
    receipt = (
        env["fix.ar.receipt"]
        .sudo()
        .create(
            {
                "company_id": order.company_id.id,
                "customer_id": order.customer_id.id,
                "amount": amount if amount is not None else order.awarded_price,
                "method": "bkash",
                "reference": "B4-MKT-%d" % next(_SEQ),
                "state": "confirmed",
            }
        )
    )
    order._guarded().write({"customer_receipt_id": receipt.id})
    return receipt
