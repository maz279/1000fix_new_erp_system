"""A05 printable documents (A05 ERP audit XC-10 / M13-24 / M14-18 / M18-18,
20 Nov 2026).

The circular-economy records existed with no printable output: a rental went
out with no agreement, condition report or deposit receipt in the customer's
hand; a seller was paid with no purchase voucher or declaration; a refurbished
unit was sold with no warranty card or buyer disclosure; e-waste left with no
Form-1 manifest, and no disposal certificate or DoE return could be printed.

Each is now a QWeb PDF (report/p03_a05_documents.xml) printed through the same
mechanism as the commercial documents: an ir.actions.report served at
/report/pdf/<report>/<id>, handed out by /p03/doc/print_url, with the
commercial document standard's blocks (cd_doc_suite: letterhead, company BIN,
party, meta table, SL / code / qty / unit / amount lines, totals, amount in
words, signatures) through the A02 document base (models/p03_a02_documents.py:
the payload is built here, the template computes nothing). Labels are
bilingual (English / Bengali). The domain models are read at run time, so the
workspace module keeps its dependencies (AS-09).
"""

from odoo import models
from odoo.exceptions import UserError
from odoo.tools import html2plaintext

from ...models.p03_a02_documents import _label, _words, fmt_money, fmt_qty

# bilingual labels (English / Bengali), the A05 documents' own
BN = {
    "Agreement No.": "চুক্তি নং",
    "Date": "তারিখ",
    "Branch": "শাখা",
    "Rental Period": "ভাড়ার মেয়াদ",
    "Customer": "গ্রাহক",
    "Seller": "বিক্রেতা",
    "Buyer": "ক্রেতা",
    "Equipment": "যন্ত্রপাতি",
    "Security Deposit": "জামানত",
    "Terms": "শর্তাবলি",
    "Signed": "স্বাক্ষরিত",
    "Receipt No.": "রসিদ নং",
    "Report No.": "প্রতিবেদন নং",
    "Inspector": "পরিদর্শক",
    "Photographs": "ছবি",
    "Voucher No.": "ভাউচার নং",
    "Job Card No.": "জব কার্ড নং",
    "Warranty No.": "ওয়ারেন্টি নং",
    "Manifest No.": "ম্যানিফেস্ট নং",
    "Certificate No.": "সনদ নং",
    "Return No.": "রিটার্ন নং",
    "Period": "সময়কাল",
    "Total Weight (kg)": "মোট ওজন (কেজি)",
    "Grand Total (BDT)": "সর্বমোট (টাকা)",
    "Net Payable (BDT)": "নিট প্রদেয় (টাকা)",
    "Deposit Received (BDT)": "জামানত গৃহীত (টাকা)",
}


def bl(text):
    """'English / বাংলা' for the labels the A05 documents know."""
    bn = BN.get(text)
    return "%s / %s" % (text, bn) if bn else text


def _mask(value, keep=4):
    value = (value or "").strip()
    if not value:
        return ""
    return "X" * max(len(value) - keep, 0) + value[-keep:]


def _data_uri(att):
    """An image attachment as a data URI wkhtmltopdf can embed, or ''."""
    if not att or not (att.mimetype or "").startswith("image/"):
        return ""
    raw = att.datas
    if not raw:
        return ""
    if isinstance(raw, bytes):
        raw = raw.decode()
    return "data:%s;base64,%s" % (att.mimetype, raw)


class P03A05DocumentBase(models.AbstractModel):
    _name = "report.cd_p03_portal.a05_document_base"
    _inherit = "report.cd_p03_portal.a02_document_base"
    _description = "A05 Printable Document Payloads"

    def _base(self, record, title, chip=""):
        p = super()._base(record, title, chip)
        p["photos"] = []
        p["policy"] = ""
        return p

    def _sku_code(self, sku):
        item = sku.catalogue_item_id if sku and "catalogue_item_id" in sku._fields else None
        tmpl = item.product_tmpl_id if item and "product_tmpl_id" in item._fields else None
        return (tmpl.default_code if tmpl else "") or ""


# ============================================================== M13 rental
class P03A05RentalAgreement(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a05_rental_agreement"
    _inherit = "report.cd_p03_portal.a05_document_base"
    _description = "Rental Agreement"

    _doc_model = "fix.rental.reservation"

    def _payload(self, res):
        if res.state == "cancelled":
            chip = "CANCELLED"
        else:
            chip = (
                _label(res, "agreement_state").upper() if "agreement_state" in res._fields else ""
            )
        p = self._base(res, "RENTAL AGREEMENT / ভাড়া চুক্তি", chip)
        p["watermark"] = (
            "CANCELLED"
            if res.state == "cancelled"
            else ("" if res.signed_at else "DRAFT — NOT SIGNED")
        )
        p["party_label"] = bl("Customer")
        p["bill_to"] = self._party(res.customer_id)
        meta = [
            (bl("Agreement No."), res.name or ""),
            (bl("Date"), self._d(res.date_from)),
            (
                bl("Rental Period"),
                "%s to %s (%s day(s))"
                % (self._d(res.date_from), self._d(res.date_to), res.duration_days or 0),
            ),
        ]
        if res.branch_id:
            meta.append((bl("Branch"), res.branch_id.name))
        if "agreement_version" in res._fields and res.agreement_version:
            meta.append(("Agreement Version / সংস্করণ", str(res.agreement_version)))
        meta.append(("Delivery / ডেলিভারি", _label(res, "delivery_method")))
        p["meta"] = meta
        sku = res.rental_sku_id
        asset = res.rental_asset_id
        days = res.duration_days or 0
        charge = res.rental_charge or 0.0
        lines = [
            {
                "sl": 1,
                "code": self._sku_code(sku) or (asset.name or ""),
                "type": "Rental charge / ভাড়া",
                "description": (sku.name if sku else "") or (asset.name or "Rental equipment"),
                "serial": asset.serial_no or "" if asset else "",
                "qty": fmt_qty(days),
                "uom": "Day(s)",
                "price": fmt_money(charge / days) if days else fmt_money(charge),
                "disc": "",
                "disc_pct": "",
                "amount": fmt_money(charge),
            }
        ]
        waiver = res.waiver_fee if "waiver_fee" in res._fields else 0.0
        if waiver:
            lines.append(
                {
                    "sl": 2,
                    "code": "WAIVER",
                    "type": "Damage waiver / ক্ষতি মওকুফ",
                    "description": res.waiver_plan_id.name or "Damage waiver",
                    "serial": "",
                    "qty": "1",
                    "uom": "Plan",
                    "price": fmt_money(waiver),
                    "disc": "",
                    "disc_pct": "",
                    "amount": fmt_money(waiver),
                }
            )
        p["lines"] = lines
        total = charge + (waiver or 0.0)
        p["totals"] = [
            ("Total Items / Qty", "%d / %s" % (len(lines), fmt_qty(days)), ""),
            ("Amount (excl. VAT)", fmt_money(total), ""),
            (bl("Grand Total (BDT)"), fmt_money(total), "grand"),
        ]
        p["words"] = _words(total)
        equipment = [
            ("Unit / ইউনিট", asset.name or "" if asset else "To be allocated at dispatch"),
            ("Serial No. / সিরিয়াল", asset.serial_no or "" if asset else ""),
            ("Category / শ্রেণি", _label(asset, "category") if asset else ""),
            ("Condition at Dispatch / অবস্থা", _label(asset, "condition_grade") if asset else ""),
        ]
        if res.kit_id:
            equipment.append(
                ("Kit & Accessories / আনুষঙ্গিক", res.kit_id.accessories or res.kit_id.name)
            )
        deposit = [
            (bl("Security Deposit"), fmt_money(res.deposit_collected)),
            ("Held as / ধরন", "Refundable security deposit (a liability, not income)"),
        ]
        if res.deposit_bond_ref:
            deposit.append(("Bond Ref. / বন্ড", res.deposit_bond_ref))
        multiplier = (
            self.env["ir.config_parameter"].sudo().get_param("cd_rental_asset.late_fee_multiplier")
            or "1.5"
        )
        grace = (
            self.env["ir.config_parameter"].sudo().get_param("cd_rental_asset.late_fee_grace_days")
            or "0"
        )
        terms = [
            (
                "Late Return / বিলম্বে ফেরত",
                "%s x the daily rate per day late after %s grace day(s), plus VAT."
                % (multiplier, grace),
            ),
            (
                "Damage / ক্ষতি",
                "Assessed against the outbound and return condition reports; recovered from "
                "the deposit first, the excess invoiced.",
            ),
        ]
        if res.liability_cap_amount:
            terms.append(("Liability Cap / দায়সীমা", fmt_money(res.liability_cap_amount)))
        if "waiver_plan_id" in res._fields and res.waiver_plan_id:
            plan = res.waiver_plan_id
            terms.append(
                (
                    "Damage Waiver Plan",
                    "%s — excess %s; exclusions: %s"
                    % (plan.name, fmt_money(plan.excess_amount), plan.exclusions or "none stated"),
                )
            )
        if res.special_terms:
            terms.append(("Special Terms / বিশেষ শর্ত", res.special_terms))
        if res.stamp_duty_cert_no:
            terms.append(("Stamp Duty Cert. / স্ট্যাম্প", res.stamp_duty_cert_no))
        signed = [
            (bl("Signed"), self._dt(res.signed_at) if res.signed_at else "Not signed"),
            ("Signature Ref. / স্বাক্ষর রেফ.", res.signature_ref or ""),
            ("Terms Hash / শর্তের হ্যাশ", res.agreement_terms_hash or ""),
        ]
        p["blocks"] = [
            {"title": bl("Equipment"), "rows": equipment},
            {"title": bl("Security Deposit"), "rows": deposit},
            {"title": bl("Terms"), "rows": terms},
            {"title": "Customer e-signature / গ্রাহকের ই-স্বাক্ষর", "rows": signed},
        ]
        p["notes"] = [
            "VAT on the rental is charged on the NBR Mushak 6.3 issued for this rental "
            "(M51); the deposit is not a supply and carries no VAT.",
            "ভাড়ার উপর ভ্যাট মূসক ৬.৩ অনুযায়ী প্রযোজ্য; জামানত ফেরতযোগ্য এবং ভ্যাটমুক্ত।",
        ]
        p["sign"] = [
            "Customer / গ্রাহক — signature & date",
            "For 1000FiX Services Ltd. — Authorised Signature",
        ]
        return p


class P03A05ConditionReport(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a05_condition_report"
    _inherit = "report.cd_p03_portal.a05_document_base"
    _description = "Rental Condition Report"

    _doc_model = "fix.rental.condition"

    _TITLES = {
        "pre_delivery": "CONDITION REPORT — OUTBOUND / অবস্থা প্রতিবেদন (প্রেরণ)",
        "post_return": "CONDITION REPORT — RETURN / অবস্থা প্রতিবেদন (ফেরত)",
        "swap_out": "CONDITION REPORT — SWAP OUT / অবস্থা প্রতিবেদন (বদল)",
        "swap_in": "CONDITION REPORT — SWAP IN / অবস্থা প্রতিবেদন (বদল)",
    }

    def _checklist(self, cond):
        def yes(flag):
            return "Yes / হ্যাঁ" if flag else "No / না"

        return [
            ("Grade / গ্রেড", (cond.grade or "").upper()),
            ("Battery Health % / ব্যাটারি", str(cond.battery_health_pct or 0)),
            ("Charge Cycles", str(cond.charge_cycles or 0)),
            ("Charger Present / চার্জার", yes(cond.charger_ok)),
            ("Case / Bag Present / কেস", yes(cond.case_ok)),
            ("Screen Intact / স্ক্রিন", yes(cond.screen_ok)),
            ("Ports & Connectors / পোর্ট", yes(cond.ports_ok)),
            ("Body Condition / বডি", _label(cond, "body_condition_rating")),
            ("Maintenance Required", yes(cond.maintenance_required)),
            ("Notes / মন্তব্য", cond.notes or ""),
        ]

    def _payload(self, cond):
        res = cond.reservation_id
        p = self._base(
            cond,
            self._TITLES.get(cond.report_type, "CONDITION REPORT"),
            _label(cond, "report_type").upper(),
        )
        p["party_label"] = bl("Customer")
        p["bill_to"] = self._party(res.customer_id) if res else {"name": "—"}
        asset = cond.rental_asset_id or res.rental_asset_id
        p["meta"] = [
            (bl("Report No."), cond.name or ""),
            (bl("Date"), self._d(cond.reported_on)),
            ("Rental / ভাড়া", res.name or ""),
            ("Unit / ইউনিট", asset.name or "" if asset else ""),
            ("Serial No. / সিরিয়াল", asset.serial_no or "" if asset else ""),
            (bl("Inspector"), cond.inspector_id.name or ""),
        ]
        p["blocks"] = [{"title": "Checklist / চেকলিস্ট", "rows": self._checklist(cond)}]
        # out and in side by side: every condition report of the rental
        reports = (
            res.condition_ids.sorted(lambda c: (c.reported_on or c.create_date, c.id))
            if res
            else cond
        )
        p["tables"] = [
            {
                "title": "Outbound vs return / প্রেরণ বনাম ফেরত",
                "cols": [
                    "Report",
                    "Stage",
                    "Date",
                    "Grade",
                    "Battery %",
                    "Screen",
                    "Ports",
                    "Photos",
                ],
                "rows": [
                    [
                        r.name or "",
                        _label(r, "report_type"),
                        self._d(r.reported_on),
                        (r.grade or "").upper(),
                        str(r.battery_health_pct or 0),
                        "OK" if r.screen_ok else "Damaged",
                        "OK" if r.ports_ok else "Fault",
                        str(len(r.photo_ids)) if "photo_ids" in r._fields else "",
                    ]
                    for r in reports
                ],
            }
        ]
        photos = []
        if "photo_ids" in cond._fields:
            for photo in cond.photo_ids.sorted(lambda f: (f.sequence, f.id)):
                photos.append(
                    {
                        "src": _data_uri(photo.attachment_id),
                        "caption": "%s · %s · SHA-256 %s"
                        % (
                            _label(photo, "view_code"),
                            self._dt(photo.captured_at),
                            (photo.sha256 or "")[:16],
                        ),
                    }
                )
        p["photos"] = photos
        p["photos_title"] = "%s (%d)" % (bl("Photographs"), len(photos))
        p["notes"] = [
            "Photographs are sealed at capture (SHA-256); the digest printed is the "
            "stored one. This report and its counterpart are the evidence for any "
            "damage assessment.",
        ]
        p["sign"] = [
            "Inspected by / পরিদর্শক",
            "Customer / গ্রাহক — agreed condition, signature & date",
        ]
        return p


class P03A05DepositReceipt(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a05_deposit_receipt"
    _inherit = "report.cd_p03_portal.a05_document_base"
    _description = "Rental Security Deposit Receipt"

    _doc_model = "fix.rental.deposit"

    _TITLES = {
        "collect": "SECURITY DEPOSIT RECEIPT / জামানত রসিদ",
        "refund": "SECURITY DEPOSIT REFUND ADVICE / জামানত ফেরত",
        "deduction": "DEPOSIT DEDUCTION ADVICE / জামানত কর্তন",
        "forfeit": "DEPOSIT FORFEIT ADVICE / জামানত বাজেয়াপ্ত",
    }

    def _payload(self, move):
        res = move.reservation_id
        p = self._base(
            move, self._TITLES.get(move.kind, "DEPOSIT"), _label(move, "gl_state").upper()
        )
        p["watermark"] = "" if move.gl_state in ("posted", "refund_queued") else "NOT IN THE BOOKS"
        p["party_label"] = bl("Customer")
        p["bill_to"] = self._party(move.customer_id or res.customer_id)
        p["meta"] = [
            (bl("Receipt No."), move.name or ""),
            (bl("Date"), self._d(move.date)),
            ("Rental / ভাড়া", res.name or ""),
            ("Method / মাধ্যম", _label(move, "method")),
            ("Reference / রেফারেন্স", move.reference or ""),
        ]
        if res.branch_id:
            p["meta"].append((bl("Branch"), res.branch_id.name))
        p["lines"] = [
            {
                "sl": 1,
                "code": "DEPOSIT",
                "type": _label(move, "kind"),
                "description": "Refundable security deposit — rental %s" % (res.name or ""),
                "serial": res.rental_asset_id.serial_no or "" if res.rental_asset_id else "",
                "qty": "1",
                "uom": "",
                "price": fmt_money(move.amount),
                "disc": "",
                "disc_pct": "",
                "amount": fmt_money(move.amount),
            }
        ]
        label = bl("Deposit Received (BDT)") if move.kind == "collect" else bl("Grand Total (BDT)")
        p["totals"] = [(label, fmt_money(move.amount), "grand")]
        p["words"] = _words(move.amount)
        p["notes"] = [
            "A security deposit is held as a liability and refunded on return, less "
            "approved deductions; it is not a sale and carries no VAT.",
            "জামানত একটি দায়, বিক্রয় নয়; ফেরতের সময় অনুমোদিত কর্তন বাদে ফেরত দেওয়া হবে।",
        ]
        if move.note:
            p["notes"].append(move.note)
        p["sign"] = ["Received by (Cashier) / ক্যাশিয়ার", "Customer / গ্রাহক"]
        return p


# ============================================================== M14 trade-in
_DECLARATION = (
    "I, the seller, declare that I am the lawful owner of the device described above; "
    "that it is not stolen, financed, blacklisted or subject to any claim; that I have "
    "removed my accounts and consent to the secure erasure of all data on it; and that "
    "the information I have given is true. I transfer ownership to 1000FiX Services Ltd. "
    "for the purchase value stated."
)
_DECLARATION_BN = (
    "আমি, বিক্রেতা, ঘোষণা করছি যে উপরে বর্ণিত ডিভাইসটির আমি বৈধ মালিক; এটি চুরি, কিস্তি, "
    "কালো তালিকাভুক্ত বা কোনো দাবির অধীন নয়; আমি আমার অ্যাকাউন্ট সরিয়েছি এবং সকল তথ্য "
    "নিরাপদে মুছে ফেলায় সম্মতি দিচ্ছি; প্রদত্ত তথ্য সত্য। উল্লিখিত মূল্যে ডিভাইসটির মালিকানা "
    "1000FiX Services Ltd.-এর নিকট হস্তান্তর করছি।"
)


class P03A05TradeinVoucher(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a05_tradein_voucher"
    _inherit = "report.cd_p03_portal.a05_document_base"
    _description = "Trade-In Purchase Voucher & Seller Declaration"

    _doc_model = "fix.tradein.request"

    def _imei(self, req):
        cleared = req.provenance_ids.filtered(lambda r: r.imei)
        if cleared:
            return cleared[-1].imei
        device = req.device_id
        for name in ("imei", "imei_1", "serial_number", "serial_no"):
            if device and name in device._fields and device[name]:
                return device[name]
        return ""

    def _payload(self, req):
        if req.state in ("draft", "offered", "rejected"):
            raise UserError(
                "Trade-in %s has no accepted offer: there is no purchase voucher yet." % req.name
            )
        p = self._base(
            req,
            "TRADE-IN PURCHASE VOUCHER & SELLER DECLARATION / ট্রেড-ইন ক্রয় ভাউচার ও বিক্রেতার ঘোষণা",
            _label(req, "payout_approval_state").upper(),
        )
        p["party_label"] = bl("Seller")
        p["bill_to"] = self._party(req.customer_id)
        p["party_bin_label"] = "Seller e-TIN"
        if req.taxpayer_tin:
            p["bill_to"]["bin"] = req.taxpayer_tin
        value = req.graded_value or req.accepted_offer_value or req.offered_value or 0.0
        tds = req.tds_amount or 0.0
        net = req.net_payout or (value - tds)
        p["meta"] = [
            (bl("Voucher No."), req.name or ""),
            (bl("Date"), self._dt(req.accepted_at)),
            ("Seller NID / এনআইডি", _mask(req.customer_nid)),
            (
                "Settlement / পরিশোধ",
                _label(req, "settlement_method") if "settlement_method" in req._fields else "",
            ),
            ("Payout Approval / অনুমোদন", _label(req, "payout_approval_state")),
        ]
        if req.operating_unit_id:
            p["meta"].append((bl("Branch"), req.operating_unit_id.name))
        p["lines"] = [
            {
                "sl": 1,
                "code": req.device_model_id.display_name or "" if req.device_model_id else "",
                "type": "Used device purchased / পুরাতন ডিভাইস ক্রয়",
                "description": req.device_id.display_name
                or req.device_model_id.display_name
                or "Device",
                "serial": self._imei(req),
                "qty": "1",
                "uom": "Unit",
                "price": fmt_money(value),
                "disc": "",
                "disc_pct": "",
                "amount": fmt_money(value),
            }
        ]
        totals = [("Purchase Value / ক্রয়মূল্য", fmt_money(value), "")]
        if tds:
            totals.append(
                (
                    "Less: TDS withheld",
                    fmt_money(tds),
                    "",
                    "%g%%" % (req.tds_effective_rate_pct or 0),
                )
            )
        totals.append((bl("Net Payable (BDT)"), fmt_money(net), "grand"))
        p["totals"] = totals
        p["words"] = _words(net)
        provenance = [
            ("IMEI / Serial", self._imei(req)),
            (
                "Provenance Check / উৎস যাচাই",
                ", ".join(_label(r, "state") for r in req.provenance_ids) or "Not checked",
            ),
            ("Accepted Offer / গৃহীত প্রস্তাব", fmt_money(req.accepted_offer_value)),
        ]
        if req.revision_accepted_value:
            provenance.append(("Revised Value Accepted", fmt_money(req.revision_accepted_value)))
        p["blocks"] = [
            {"title": "Device & provenance / ডিভাইস ও উৎস", "rows": provenance},
            {
                "title": "Seller declaration / বিক্রেতার ঘোষণা",
                "rows": [("Declaration", _DECLARATION), ("ঘোষণা", _DECLARATION_BN)],
            },
        ]
        p["notes"] = [
            "Purchase of a used device from an individual: not a taxable supply by the "
            "seller. TDS is withheld only where M51 determines it applies.",
        ]
        p["sign"] = [
            "Seller / বিক্রেতা — signature & date",
            "Purchasing Officer / ক্রয় কর্মকর্তা",
            "For 1000FiX Services Ltd. — Authorised Signature",
        ]
        return p


class P03A05RefurbJobCard(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a05_refurb_job_card"
    _inherit = "report.cd_p03_portal.a05_document_base"
    _description = "Refurbishment Job Card"

    _doc_model = "fix.refurbishment"

    def _payload(self, step):
        req = step.tradein_id
        p = self._base(
            step, "REFURBISHMENT JOB CARD / রিফার্বিশমেন্ট জব কার্ড", _label(req, "state").upper()
        )
        p["party_label"] = "Unit / ইউনিট"
        p["bill_to"] = {
            "name": req.device_id.display_name or req.device_model_id.display_name or req.name
        }
        p["meta"] = [
            (bl("Job Card No."), req.name or ""),
            ("Step / ধাপ", "%s (%s)" % (step.name or "", _label(step, "step"))),
            ("Technician / টেকনিশিয়ান", step.technician_id.name or ""),
            ("Started / শুরু", self._dt(step.started_at)),
            ("Completed / সম্পন্ন", self._dt(step.completed_at)),
            (
                "Wipe Certificate / ডেটা মুছে ফেলার সনদ",
                req.wipe_certificate_id.name or "None — gate closed",
            ),
        ]
        steps = req.refurbishment_ids.sorted(lambda s: s.id)
        p["lines"] = [
            {
                "sl": i,
                "code": s.step or "",
                "type": _label(s, "state"),
                "description": "%s%s" % (s.name or "", (" — " + s.notes) if s.notes else ""),
                "serial": "",
                "qty": "1",
                "uom": "Step",
                "price": fmt_money(s.total_cost),
                "disc": "",
                "disc_pct": "",
                "amount": fmt_money(s.total_cost),
            }
            for i, s in enumerate(steps, 1)
        ]
        p["totals"] = [
            ("Parts / যন্ত্রাংশ", fmt_money(req.parts_cost), ""),
            ("Labour / শ্রম", fmt_money(req.labour_cost), ""),
            ("Refurbishment Cost / মোট খরচ", fmt_money(req.refurbishment_cost), "grand"),
        ]
        qa = (
            self.env["fix.refurb.qa"]
            .sudo()
            .search([("tradein_id", "=", req.id)], order="id desc", limit=1)
            if "fix.refurb.qa" in self.env
            else None
        )
        if qa:
            p["blocks"].append(
                {
                    "title": "Quality check / মান যাচাই",
                    "rows": [
                        ("QA No.", qa.name or ""),
                        ("Result / ফলাফল", _label(qa, "qa_state")),
                        ("Tests Passed", "%s / %s" % (qa.tests_passed, qa.tests_total)),
                        ("Battery Health %", str(qa.battery_health_pct or 0)),
                    ],
                }
            )
            if "test_ids" in qa._fields:
                p["tables"].append(
                    {
                        "title": "QA tests / পরীক্ষা",
                        "cols": ["Test", "Expected", "Measured", "Outcome"],
                        "rows": [
                            [
                                _label(t, "test_code"),
                                t.expected or "",
                                t.measured or "",
                                _label(t, "outcome"),
                            ]
                            for t in qa.test_ids
                        ],
                    }
                )
        p["notes"] = [
            "No refurbishment step starts before the M06 wipe certificate is verified "
            "(Journey 9 gate)."
        ]
        p["sign"] = ["Technician / টেকনিশিয়ান", "QA Inspector / পরিদর্শক", "Refurb Supervisor"]
        return p


class P03A05ResaleWarranty(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a05_resale_warranty"
    _inherit = "report.cd_p03_portal.a05_document_base"
    _description = "Resale Warranty Card & Buyer Disclosure"

    _doc_model = "fix.tradein.warranty"

    def _disclosure(self, req):
        """The buyer disclosure the trade-in record generates (stream S2,
        buyer_disclosure_html, BRU-TRF-15); until that field exists, the
        record's own grading facts."""
        if "buyer_disclosure_html" in req._fields and (req.buyer_disclosure_html or "").strip():
            text = html2plaintext(req.buyer_disclosure_html or "")
            return [("Disclosure / প্রকাশ", text)], True
        rows = [
            ("Grade / গ্রেড", _label(req, "grade")),
            ("Battery Health % / ব্যাটারি", str(req.battery_health_pct or 0)),
            ("Repairs / মেরামত", ", ".join(req.refurbishment_ids.mapped("name")) or "None"),
            ("Data Wipe Certificate / সনদ", req.wipe_certificate_id.name or ""),
            ("Provenance / উৎস", "Second-hand device bought in from a verified seller"),
        ]
        return rows, False

    def _payload(self, warranty):
        req = warranty.tradein_id
        chip = _label(warranty, "state").upper()
        p = self._base(
            warranty, "RESALE WARRANTY CARD & BUYER DISCLOSURE / ওয়ারেন্টি কার্ড ও ক্রেতা প্রকাশ", chip
        )
        p["watermark"] = "VOID" if warranty.state in ("void", "voided") else ""
        p["party_label"] = bl("Buyer")
        p["bill_to"] = {"name": warranty.graded_stock_ref or "Refurbished unit buyer"}
        p["meta"] = [
            (bl("Warranty No."), warranty.name or ""),
            ("Stock Unit / স্টক ইউনিট", warranty.graded_stock_ref or ""),
            (
                "Device / ডিভাইস",
                req.device_id.display_name or req.device_model_id.display_name or "",
            ),
            ("Starts / শুরু", self._d(warranty.start_date)),
            ("Ends / শেষ", self._d(warranty.end_date)),
            ("Months / মাস", str(warranty.months or 0)),
        ]
        rows, generated = self._disclosure(req)
        p["blocks"] = [
            {"title": "Buyer disclosure / ক্রেতার জন্য প্রকাশ", "rows": rows},
            {
                "title": "Warranty terms / ওয়ারেন্টি শর্ত",
                "rows": [
                    (
                        "Terms",
                        warranty.terms
                        or "Standard refurbished-unit warranty; physical and liquid damage excluded.",
                    )
                ],
            },
        ]
        p["notes"] = [
            "This is a refurbished (second-hand) device, graded and tested by 1000FiX. "
            "Keep this card: it is required for a warranty claim. Hotline 16743.",
            "এটি একটি রিফার্বিশড (পুরাতন) ডিভাইস। ওয়ারেন্টি দাবির জন্য এই কার্ডটি সংরক্ষণ করুন।",
        ]
        if not generated:
            p["notes"].append(
                "Disclosure printed from the unit's grading record; the generated "
                "disclosure report replaces it once recorded."
            )
        p["sign"] = [
            "Buyer / ক্রেতা — received & read",
            "For 1000FiX Services Ltd. — Authorised Signature",
        ]
        return p


# ============================================================== M18 e-waste
class P03A05EwasteManifest(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a05_ewaste_manifest"
    _inherit = "report.cd_p03_portal.a05_document_base"
    _description = "E-Waste Transfer Manifest (Form-1) & Hazmat Declaration"

    _doc_model = "fix.ewaste.manifest"

    def _payload(self, man):
        p = self._base(
            man,
            "E-WASTE TRANSFER MANIFEST (FORM-1) / ই-বর্জ্য স্থানান্তর ম্যানিফেস্ট (ফর্ম-১)",
            "HAZARDOUS" if man.hazardous else "",
        )
        partner = man.partner_id
        p["party_label"] = "Consignee (Recycler) / গ্রহীতা (রিসাইক্লার)"
        p["bill_to"] = (
            self._party(partner.partner_id)
            if partner and partner.partner_id
            else {"name": partner.name or "—"}
        )
        if partner and not p["bill_to"].get("name"):
            p["bill_to"]["name"] = partner.name
        p["meta"] = [
            (bl("Manifest No."), man.name or ""),
            (bl("Date"), self._d(man.issued_on)),
            ("Batch / ব্যাচ", man.batch_id.name or ""),
            ("Recycler Licence / লাইসেন্স", man.licence_no or ""),
            ("Licence Valid To / মেয়াদ", self._d(man.licence_valid_to)),
            ("Destination / গন্তব্য", man.destination_country_id.name or "Bangladesh"),
        ]
        if man.basel_pic_id:
            p["meta"].append(("Basel PIC", man.basel_pic_id.display_name))
        lines = man.line_ids.sorted(lambda ln: ln.id)
        p["lines"] = [
            {
                "sl": i,
                "code": (ln.collection_id.name or ln.battery_id.name or "")
                if (ln.collection_id or ln.battery_id)
                else "",
                "type": ("Hazardous" if ln.hazardous else "Non-hazardous")
                + (" · UN %s" % ln.un_number if ln.un_number else ""),
                "description": "%s%s"
                % (ln.description or "", (" · " + ln.material_type) if ln.material_type else ""),
                "serial": ln.wipe_certificate_id.name or "" if ln.wipe_certificate_id else "",
                "qty": fmt_qty(ln.weight_kg),
                "uom": "kg",
                "price": "",
                "disc": "",
                "disc_pct": "",
                "amount": "",
            }
            for i, ln in enumerate(lines, 1)
        ]
        p["totals"] = [
            ("Items / আইটেম", str(man.item_count or len(lines)), ""),
            (bl("Total Weight (kg)"), fmt_qty(man.total_weight_kg), "grand"),
        ]
        generator = self._company_block(man.company_id)
        p["blocks"] = [
            {
                "title": "Generator / consignor — উৎপাদক / প্রেরক",
                "rows": [
                    ("Name", generator.get("name") or ""),
                    ("Address", generator.get("address") or ""),
                    ("BIN", generator.get("bin") or ""),
                ],
            }
        ]
        if man.hazardous:
            p["blocks"].append(
                {
                    "title": "Hazardous material declaration / বিপজ্জনক দ্রব্যের ঘোষণা",
                    "rows": [
                        (
                            "Declaration",
                            man.hazmat_declaration
                            or "Hazardous items listed above (UN numbers as shown).",
                        )
                    ],
                }
            )
        p["notes"] = [
            "Issued under the Hazardous Waste (E-waste) Management Rules 2021 (S.R.O. 187/2021), "
            "Form-1. Data-bearing items carry their M06 destruction certificate number.",
        ]
        p["sign"] = [
            "Generator / প্রেরক — signature & seal",
            "Transporter / পরিবহনকারী",
            "Recycler / গ্রহীতা — received, weight & date",
        ]
        return p


class P03A05DisposalCertificate(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a05_disposal_certificate"
    _inherit = "report.cd_p03_portal.a05_document_base"
    _description = "E-Waste Disposal / Recycling Certificate"

    _doc_model = "fix.ewaste.certificate"

    def _payload(self, cert):
        issued = cert.state == "issued"
        p = self._base(
            cert,
            "DISPOSAL / RECYCLING CERTIFICATE / নিষ্পত্তি ও পুনর্চক্রায়ন সনদ",
            _label(cert, "state").upper(),
        )
        p["watermark"] = "" if issued else ("REVOKED" if cert.state == "revoked" else "NOT ISSUED")
        items = cert.collection_ids or cert.collection_id
        customers = items.mapped("customer_id")
        p["party_label"] = "Issued To / প্রাপক"
        p["bill_to"] = (
            self._party(customers[:1]) if len(customers) == 1 else {"name": "Items listed below"}
        )
        p["meta"] = [
            (bl("Certificate No."), cert.name or ""),
            ("Recycler Certificate No.", cert.certificate_no or ""),
            (bl("Date"), self._d(cert.issued_on)),
            ("Batch / ব্যাচ", cert.batch_id.name or ""),
            ("Recycler / রিসাইক্লার", cert.partner_id.name or ""),
        ]
        p["lines"] = [
            {
                "sl": i,
                "code": c.name or "",
                "type": _label(c, "material_type"),
                "description": c.device_id.display_name or c.customer_id.name or "",
                "serial": c.wipe_certificate_id.name or "" if c.wipe_certificate_id else "",
                "qty": fmt_qty(c.weight_kg),
                "uom": "kg",
                "price": "",
                "disc": "",
                "disc_pct": "",
                "amount": "",
            }
            for i, c in enumerate(items, 1)
        ]
        p["totals"] = [
            ("Items / আইটেম", str(len(items)), ""),
            ("Weight Stated by Recycler (kg)", fmt_qty(cert.recycler_stated_weight_kg), ""),
            (bl("Total Weight (kg)"), fmt_qty(cert.weight_kg), "grand"),
        ]
        p["notes"] = [
            "This certifies that the items above were received and processed by the "
            "licensed recycler named, under its certificate number shown."
            if issued
            else "NOT A CERTIFICATE: it has not been issued, or it was revoked."
        ]
        if cert.state == "revoked" and cert.revoke_reason:
            p["notes"].append("Revoked: %s" % cert.revoke_reason)
        p["sign"] = [
            "Quality Manager / মান ব্যবস্থাপক",
            "For 1000FiX Services Ltd. — Authorised Signature",
        ]
        return p


class P03A05DoeReturn(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a05_doe_return"
    _inherit = "report.cd_p03_portal.a05_document_base"
    _description = "Statutory E-Waste Return (DoE)"

    _doc_model = "fix.ewaste.return"

    def _payload(self, ret):
        p = self._base(
            ret, "STATUTORY E-WASTE RETURN / ই-বর্জ্য বিধিবদ্ধ রিটার্ন", _label(ret, "state").upper()
        )
        p["watermark"] = "" if ret.state in ("submitted", "accepted") else "DRAFT"
        p["party_label"] = "Authority / কর্তৃপক্ষ"
        p["bill_to"] = {"name": _label(ret, "authority")}
        p["meta"] = [
            (bl("Return No."), ret.name or ""),
            (bl("Period"), ret.period or ""),
            ("Form / ফর্ম", _label(ret, "form_type")),
            ("Due / নির্ধারিত তারিখ", self._d(ret.due_date)),
            ("Submitted / দাখিল", self._d(ret.submitted_on)),
            ("Reference / রেফারেন্স", ret.reference or ""),
            ("Acknowledgement / প্রাপ্তিস্বীকার", ret.authority_ack_ref or ""),
        ]
        if ret.registration_id:
            p["meta"].append(("DoE Registration", ret.registration_id.display_name))
        p["blocks"] = [
            {
                "title": "Return figures / রিটার্নের হিসাব",
                "rows": [
                    ("Schedule-1 Category", _label(ret, "schedule_1_category")),
                    ("Collected (tonnes) / সংগৃহীত", "%.3f" % (ret.total_tonnage_collected or 0.0)),
                    ("Recycled (tonnes) / পুনর্চক্রায়িত", "%.3f" % (ret.total_tonnage_recycled or 0.0)),
                    ("Recovery % / পুনরুদ্ধার", "%.2f" % (ret.recovery_rate_pct or 0.0)),
                    ("Nil Return Reason", ret.nil_return_reason or ""),
                ],
            }
        ]
        p["notes"] = [
            "Figures are the mass balance computed from the period's collections and "
            "processed batches; a submitted return is frozen."
        ]
        p["sign"] = [
            "Prepared by (Quality Manager)",
            "Approved by (CFO)",
            "Authority Acknowledgement",
        ]
        return p
