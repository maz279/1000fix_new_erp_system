# A08 · M20 AR, Invoicing & Collections — models the generic workspace screens may read,
# and the workflow methods they may call (/p03/model/records, /p03/model/action).
# Each entry: model -> {"order", "limit", "actions"}. Reads also need the
# user's own read access on the model (accounting/payroll groups apply).
#
# The fifteen original M20 screens are bespoke (/p03/ar/* in p03_ar_api.py);
# the credit-control Hold button runs fix.credit.profile.action_toggle_hold
# through /p03/ar/credit-profile/save. The generic surfaces below serve the
# A08 additions: invoice close-out (action_register_paid) and the customer
# VDS certificates (Mushak 6.6 received).
import datetime

SURFACES = {
    "fix.ar.invoice": {
        "order": "invoice_date desc, id desc",
        "limit": 200,
        "actions": {"action_register_paid"},
    },
    "fix.vds.certificate.received": {
        "order": "certificate_date desc, id desc",
        "limit": 200,
        "actions": {"action_verify", "action_settle", "action_cancel"},
    },
}


def _period_of(value):
    if not value:
        return None
    if isinstance(value, str):
        value = datetime.date.fromisoformat(value[:10])
    return value.strftime("%Y-%m")


def vds_claim_register(env, date_from=None, date_to=None, **params):
    """VDS received per VAT period (the Mushak 9.1 VDS adjustment working):
    certificates by state, read with the caller's own access rights."""
    Cert = env["fix.vds.certificate.received"]
    domain = [("company_id", "in", env.companies.ids), ("state", "!=", "cancelled")]
    p_from, p_to = _period_of(date_from), _period_of(date_to)
    if p_from:
        domain.append(("period", ">=", p_from))
    if p_to:
        domain.append(("period", "<=", p_to))
    rows_by_period = {}
    for cert in Cert.search(domain, order="period"):
        row = rows_by_period.setdefault(
            cert.period,
            {
                "period": cert.period,
                "certificates": 0,
                "draft": 0.0,
                "verified": 0.0,
                "settled": 0.0,
                "claimed": 0.0,
                "total": 0.0,
            },
        )
        row["certificates"] += 1
        row[cert.state] += cert.vds_amount
        row["total"] += cert.vds_amount
    rows = [
        {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()}
        for r in rows_by_period.values()
    ]
    cols = ["period", "certificates", "draft", "verified", "settled", "claimed", "total"]
    totals = {"period": "Total"}
    for c in cols[1:]:
        totals[c] = round(sum(r[c] for r in rows), 2)
    return {
        "title": "VDS received (Mushak 6.6) by VAT period",
        "cols": cols,
        "labels": {
            "period": "VAT Period",
            "certificates": "Certificates",
            "draft": "Draft",
            "verified": "Verified",
            "settled": "Settled — to claim in 9.1",
            "claimed": "Claimed in 9.1",
            "total": "Total VDS",
        },
        "rows": rows,
        "totals": totals if rows else None,
        "empty": "No VDS certificates recorded for these periods.",
        "notes": [
            "Settled certificates have cleared the receivable (Dr VDS receivable / Cr AR) "
            "and await the Mushak 9.1 VDS adjustment; the tax return marks them claimed.",
        ],
    }


REPORTS = {"vds_claim_register": vds_claim_register}


def kpis(env):
    """VDS settled but not yet claimed in a 9.1 return (BDT)."""
    certs = env["fix.vds.certificate.received"].search(
        [("company_id", "in", env.companies.ids), ("state", "=", "settled")]
    )
    return {"vds_unclaimed": round(sum(certs.mapped("vds_amount")), 2)}
