"""Shared set-up for the A04 ERP audit (20 Nov 2026) M12 rules, as the
trusted superuser (configuration, not the behaviour under test):

  M12-F4  a job is awarded only once Finance configured the seller commission
          scheme in force (M53 fix.commission.scheme);
  M12-F1  commission is earned only on the customer's money received in M20.
"""

import itertools

from odoo import fields

_SEQ = itertools.count(1)


def seller_scheme(env, rate=0.0, tds_rate=0.0, company=None):
    """The seller commission scheme in force (rate 0 = the order's tier rate)."""
    Scheme = env.get("fix.commission.scheme")
    if Scheme is None:
        return None
    company = company or env.company
    today = fields.Date.context_today(env["res.partner"])
    found = Scheme.sudo()._find("seller", today, company)
    if found:
        return found
    return Scheme.sudo().create(
        {
            "name": "B4 seller scheme %d" % next(_SEQ),
            "company_id": company.id,
            "scheme_type": "seller",
            "commission_rate": rate,
            "tds_rate": tds_rate,
            "date_from": today.replace(day=1),
        }
    )


def customer_receipt(env, order, amount=None, method="bkash"):
    """A confirmed M20 receipt of the order's customer, linked to the order."""
    order = order.sudo()
    receipt = (
        env["fix.ar.receipt"]
        .sudo()
        .create(
            {
                "customer_id": order.customer_id.id,
                "amount": amount if amount is not None else order.awarded_price,
                "method": method,
                "reference": "MKT-B4-%s-%d" % (order.id, next(_SEQ)),
                "state": "confirmed",
            }
        )
    )
    order.action_record_customer_receipt(receipt)
    return receipt
