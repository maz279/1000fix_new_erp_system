"""A02 printable documents (A02 ERP audit X-17, 20 Nov 2026).

Five A02 documents existed as records with no printable output: the counter
sale's customer receipt, the data wipe certificate, the field service report,
the consignment delivery note / waybill and the workshop job card / repair
report. Each is now a QWeb PDF (report/p03_a02_documents.xml) printed through
the same mechanism as the commercial documents: an ir.actions.report served
at /report/pdf/<report>/<id> and handed out by /p03/doc/print_url, with the
commercial document standard's blocks (cd_doc_suite: letterhead, company BIN,
Bill To / customer, meta table, SL / code / qty / unit / disc / VAT lines,
totals, amount in words, signatures).

The payload of each document is built here from the record's own stored
fields (every field verified on the ORM, 19 Nov 2026), never computed in the
template. These report models depend on no domain module at load time: the
domain models are read at run time, so the workspace module keeps its
dependencies (AS-09).

The counter receipt never prints the counter's internal reference as the NBR
number (A02 ERP audit X-04): the statutory Mushak 6.3 number and the VAT are
the posted ones (cd_front_desk_finance: mushak_id, vat_taxable_amount,
vat_output_amount). Until the sale has posted, the receipt says the Mushak 6.3
is pending and carries no VAT split.
"""

from datetime import datetime

import pytz
from odoo import models
from odoo.exceptions import UserError

DHAKA = "Asia/Dhaka"
WALK_IN = "Walk-in customer"

# 80 mm roll length (mm): the cd_doc_suite receipt measurements
_BASE_MM, _TEAR_MM, _LINE_MM, _META_MM, _NOTE_MM, _MIN_MM = 44, 6, 5, 3.5, 5, 80


def fmt_money(value):
    return f"{float(value or 0.0):,.2f}"


def fmt_qty(value):
    value = float(value or 0.0)
    return ("%d" % value) if value == int(value) else ("%g" % value)


def _label(record, field):
    """The display label of a selection value, as the model declares it."""
    value = record[field]
    if not value:
        return ""
    return dict(record._fields[field]._description_selection(record.env)).get(value, value)


def _words(amount):
    try:
        from odoo.addons.cd_tax_engine_bd.models.statutory_format import amount_in_words

        return amount_in_words(amount) if amount else ""
    except Exception:  # words never break a print
        return ""


class P03A02DocumentBase(models.AbstractModel):
    _name = "report.cd_p03_portal.a02_document_base"
    _description = "A02 Printable Document Payloads"

    _doc_model = None

    # ------------------------------------------------------------- helpers
    def _tz(self):
        return pytz.timezone(self.env.context.get("tz") or self.env.user.tz or DHAKA)

    def _dt(self, stamp):
        if not stamp:
            return ""
        return pytz.utc.localize(stamp).astimezone(self._tz()).strftime("%d-%b-%Y %I:%M %p")

    def _d(self, day):
        return day.strftime("%d-%b-%Y") if day else ""

    def _company_block(self, company):
        Mixin = self.env.get("fix.doc.print.mixin")
        if Mixin is not None:
            return Mixin.sudo().with_company(company)._fix_doc_company_block()
        return {"name": company.name, "address": "", "bin": company.vat or "", "banks": []}

    def _party(self, partner, label=None, address=None):
        partner = partner.sudo() if partner else partner
        if not partner:
            return {"name": WALK_IN}
        commercial = partner.commercial_partner_id
        addr = address or ", ".join(
            x
            for x in (
                partner.street,
                partner.street2,
                partner.city,
                partner.country_id.name if partner.country_id else "",
            )
            if x
        )
        return {
            "name": partner.name,
            "phone": partner.phone or "",
            "email": partner.email or "",
            "address": addr,
            "bin": commercial.vat or "",
        }

    def _base(self, record, title, chip=""):
        return {
            "title": title,
            "chip": chip,
            "mushak": False,
            "watermark": "",
            "company": self._company_block(record.company_id),
            "bill_to": {"name": WALK_IN},
            "meta": [],
            "lines": [],
            "totals": [],
            "blocks": [],
            "tables": [],
            "notes": [],
            "no_payable_line": True,
            "sign": [],
            "printed_at": datetime.now(pytz.utc)
            .astimezone(self._tz())
            .strftime("%d-%b-%Y %I:%M %p"),
            "printed_by": self.env.user.name,
        }

    def _payload(self, record):
        raise NotImplementedError

    def _records(self, docids):
        if not self._doc_model or self._doc_model not in self.env:
            raise UserError("This document is not available on this server.")
        records = self.env[self._doc_model].browse(docids).exists()
        records.check_access("read")
        return records

    def _get_report_values(self, docids, data=None):
        records = self._records(docids)
        payloads = {rec.id: self._payload(rec.sudo()) for rec in records}
        return {
            "doc_ids": records.ids,
            "doc_model": self._doc_model,
            "docs": records,
            "payloads": payloads,
            "page_height": max([self._height(p) for p in payloads.values()] or [_MIN_MM]),
        }

    def _height(self, p):
        mm = _BASE_MM + _TEAR_MM + _LINE_MM * len([ln for ln in p["lines"] if "sl" in ln])
        mm += _META_MM * len(p["meta"]) + _NOTE_MM * min(len(p["notes"]), 3)
        mm += 3 * (1 + len(p["company"].get("address") or "") // 44)
        return int(max(round(mm), _MIN_MM))


# ---------------------------------------------------------------- counter sale
class P03A02CounterReceipt(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a02_counter_receipt"
    _inherit = "report.cd_p03_portal.a02_document_base"
    _description = "Counter Sale Customer Receipt"

    _doc_model = "fix.counter.sale"

    def _payload(self, sale):
        if sale.state == "draft":
            raise UserError("Sale %s is not confirmed: there is no receipt yet." % sale.name)
        product = sale.product_id
        posted = "mushak_id" in sale._fields and bool(sale.mushak_id)
        split = posted and bool(sale.vat_treatment_summary)
        taxable = sale.vat_taxable_amount if split else 0.0
        vat = sale.vat_output_amount if split else 0.0
        rate = round(100.0 * vat / taxable, 2) if split and taxable else 0.0
        chip = {"confirmed": "CONFIRMED", "refunded": "REFUNDED"}.get(sale.state, "")
        p = self._base(sale, "CASH MEMO / TAX INVOICE" if posted else "COUNTER SALE RECEIPT", chip)
        p["mushak"] = posted
        p["watermark"] = "REFUNDED" if sale.state == "refunded" else ""
        p["bill_to"] = self._party(sale.customer_id)
        method = _label(sale, "payment_method")
        meta = [
            ("Receipt No.", sale.name or ""),
            ("Date", self._dt(sale.confirmed_at or sale.sale_date)),
            (
                "Mushak 6.3 No.",
                sale.mushak_id.mushak_no
                if posted
                else "Pending: issued when the sale posts to the books",
            ),
        ]
        if sale.branch_id:
            meta.append(("Branch", sale.branch_id.name))
        meta.append(("Payment Method", method))
        if sale.transaction_ref:
            meta.append(("TrxID / Slip No.", sale.transaction_ref))
        seller = sale.sold_by.name or sale.confirmed_by.name
        if seller:
            meta.append(("Sales Person", seller))
        if sale.state == "refunded":
            note = "mushak_note_id" in sale._fields and sale.mushak_note_id
            meta.append(("Refunded", self._dt(sale.refund_approved_at)))
            if note:
                meta.append(("Mushak 6.7 No.", note.mushak_no or ""))
        p["meta"] = meta
        p["vat_columns"] = split
        p["lines"] = [
            {
                "sl": 1,
                "code": product.default_code or "",
                "type": "Counter sale",
                "description": product.name or "",
                "serial": sale.serial_or_warranty_ref or "",
                "qty": fmt_qty(sale.quantity),
                "uom": product.uom_id.name or "",
                "price": fmt_money(sale.unit_price),
                "disc": "",
                "disc_pct": "",
                "amount": fmt_money(taxable if split else sale.total),
                "vat_rate": ("%g%%" % rate) if split else "",
                "vat": fmt_money(vat) if split else "",
                "total": fmt_money(sale.total),
            }
        ]
        totals = [("Total Items / Qty", "1 / %s" % fmt_qty(sale.quantity), "")]
        if split:
            totals += [
                ("Taxable Value", fmt_money(taxable), ""),
                ("VAT", fmt_money(vat), "", "%g%%" % rate),
            ]
        totals.append(("Grand Total (BDT)", fmt_money(sale.total), "grand"))
        if sale.payment_method == "cash" and sale.tendered_amount:
            totals.append(("Cash Tendered", fmt_money(sale.tendered_amount), ""))
            totals.append(("Change Due", fmt_money(sale.change_due), ""))
        p["totals"] = totals
        p["words"] = _words(sale.total)
        notes = ["Counter prices include VAT."]
        if split:
            notes.append(
                "VAT under Mushak 6.3 No. %s: %s."
                % (sale.mushak_id.mushak_no, sale.vat_treatment_summary)
            )
        else:
            notes.append(
                "The NBR Mushak 6.3 is issued with its VAT when this sale posts to the books; "
                "it is printed on the receipt from then on."
            )
        p["notes"] = notes
        p["sign"] = ["Received by (Customer)", "For 1000FiX Services Ltd. — Authorised Signature"]
        return p


class P03A02CounterReceipt80(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a02_counter_receipt_80"
    _inherit = "report.cd_p03_portal.report_a02_counter_receipt"
    _description = "Counter Sale Customer Receipt (80 mm)"


# ---------------------------------------------------------- data wipe certificate
class P03A02WipeCertificate(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a02_wipe_certificate"
    _inherit = "report.cd_p03_portal.a02_document_base"
    _description = "Data Sanitization Certificate"

    _doc_model = "fix.data.wipe.certificate"

    def _payload(self, cert):
        verified = cert.sanitization_status == "verified"
        p = self._base(
            cert, "DATA SANITIZATION CERTIFICATE", _label(cert, "sanitization_status").upper()
        )
        p["watermark"] = "" if verified else "NOT VERIFIED"
        request = cert.wipe_request_id
        p["party_label"] = "Issued To"
        p["bill_to"] = self._party(request.customer_id) if request.customer_id else {"name": "—"}
        p["meta"] = [
            ("Certificate No.", cert.name or ""),
            ("Certified At", self._dt(cert.certified_at)),
            ("Status", _label(cert, "sanitization_status")),
        ]
        if request:
            p["meta"].append(("Wipe Request", request.name or ""))
        media = [
            ("Device", cert.device_id.display_name or ""),
            ("Storage Media Serial No.", cert.serial_number or ""),
        ]
        # A02 pass 2 M06-04 / M06-09: a case purge certifies the lab's copy;
        # a destruction names its witness
        if "purpose" in cert._fields:
            media.insert(0, ("Certifies", _label(cert, "purpose")))
            if cert.purpose == "case_purge":
                media.append(("Data Recovery Case", cert.case_id.name or ""))
                media.append(("Lab Copy / Key Destroyed", cert.lab_storage_ref or ""))
            if cert.destruction_witness_id:
                media.append(("Destruction Witnessed By", cert.destruction_witness_id.name))
        if request.media_description:
            media.append(("Media", request.media_description))
        p["blocks"] = [
            {"title": "Media sanitized", "rows": media},
            {
                "title": "Sanitization",
                "rows": [
                    ("Method", _label(cert, "method")),
                    # A02 pass 2 M06-09 (D16): the standard the method meets
                    ("Standard", cert.standard_ref if "standard_ref" in cert._fields else ""),
                    ("Wipe Tool / Version", cert.tool_name or ""),
                    ("Sectors Overwritten", f"{cert.sector_count or 0:,}"),
                    ("Duration (s)", f"{cert.duration_seconds or 0:,}"),
                    ("Verification Hash", cert.verification_hash or ""),
                ],
            },
            {
                "title": "Verification",
                "rows": [
                    ("Certifying Technician", cert.technician_id.name or ""),
                    ("Certified By", cert.certified_by or ""),
                    ("Verified By", cert.verified_by_id.name or ""),
                    ("Verified At", self._dt(cert.verified_at)),
                    (
                        "Evidence Unchanged Since Verification",
                        "Yes" if cert.evidence_intact else "No",
                    ),
                    ("Final Disposition", _label(request, "disposition") if request else ""),
                ],
            },
        ]
        p["notes"] = [
            "This certifies that the storage media above was sanitized by the stated method; "
            "the verification hash is the wipe tool's own output."
            if verified
            else "NOT A CERTIFICATE: the sanitization has not been verified."
        ]
        p["sign"] = [
            "Certifying Technician",
            "Verified by",
            "For 1000FiX Services Ltd. — Authorised Signature",
        ]
        return p


# ---------------------------------------------------------- field service report
class P03A02FieldServiceReport(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a02_field_service"
    _inherit = "report.cd_p03_portal.a02_document_base"
    _description = "Field Service Report"

    _doc_model = "fix.field.order"

    def _payload(self, fo):
        p = self._base(fo, "FIELD SERVICE REPORT", _label(fo, "state").upper())
        order = fo.order_id
        p["party_label"] = "Customer"
        p["bill_to"] = self._party(order.customer_id, address=fo.customer_address or None)
        meta = [("Field Order", fo.name or "")]
        if order:
            meta.append(("Service Order", order.name or ""))
        meta += [
            ("Technician", fo.technician_id.name or ""),
            ("Scheduled", self._dt(fo.scheduled_start)),
            ("Arrived", self._dt(fo.arrived_at)),
            ("Work Started", self._dt(fo.started_work_at)),
            ("Completed", self._dt(fo.completed_at)),
        ]
        p["meta"] = meta
        site = [
            ("Site Address", fo.customer_address or ""),
            ("District / Thana", " / ".join(x for x in (fo.district_name, fo.thana_name) if x)),
        ]
        if fo.hse_site_hazard_note:
            site.append(("Site Hazards", fo.hse_site_hazard_note))
        p["blocks"] = [
            {"title": "Site", "rows": site},
            {"title": "Work carried out", "rows": [("Summary", fo.work_summary or "")]},
        ]
        parts = fo.part_line_ids
        # A02 ERP audit pass 2 M02-14: the customer's report shows what each
        # fitted part is charged at - the approved estimate's price (the cost
        # of a part is not its price)
        estimate = (
            order._fix_governing_estimate().filtered(lambda e: e.state == "approved")
            if order
            else None
        )
        prices = {}
        for ln in estimate.line_ids if estimate else []:
            prices.setdefault(ln.product_id.id, ln.unit_price)
        rows = []
        for i, line in enumerate(parts, 1):
            price = prices.get(line.product_id.id)
            rows.append(
                [
                    i,
                    line.part_number or line.product_id.default_code or "",
                    line.product_id.name or "",
                    line.lot_serial_number or "",
                    fmt_qty(line.quantity),
                    fmt_money(price) if price is not None else "-",
                    fmt_money(price * line.quantity) if price is not None else "-",
                    _label(line, "state"),
                ]
            )
        p["tables"] = [
            {
                "title": "Parts fitted",
                "cols": [
                    "SL",
                    "Part No.",
                    "Description",
                    "Serial / Lot",
                    "Qty",
                    "Unit Price (BDT)",
                    "Amount (BDT)",
                    "Status",
                ],
                "rows": rows,
            }
        ]
        if estimate:
            p["blocks"].append(
                {
                    "title": "Charges",
                    "rows": [
                        ("Approved Estimate", estimate.display_name or ""),
                        ("Estimate Total incl. VAT (BDT)", fmt_money(estimate.grand_total)),
                    ],
                }
            )
        signoff = [
            ("Handover OTP Verified", "Yes" if fo.customer_otp_verified else "No"),
            ("Signed By", fo.customer_signature_signer or ""),
            ("Signed At", self._dt(fo.customer_signature_at)),
            ("On-Site Rating", (fo.customer_rating + " / 5") if fo.customer_rating else ""),
        ]
        if fo.onsite_collection_amount:
            signoff += [
                ("Collected On Site (BDT)", fmt_money(fo.onsite_collection_amount)),
                ("Payment Method", _label(fo, "onsite_payment_method")),
                ("TrxID", fo.onsite_payment_trx_id or ""),
                ("On-Site Receipt No.", fo.onsite_receipt_no or ""),
            ]
        p["blocks"].append({"title": "Customer sign-off", "rows": signoff})
        p["notes"].append(
            "Customer declaration: the work above was carried out at my premises, the device "
            "was tested in my presence and handed back working, and the parts listed were "
            "fitted. Parts removed were returned to me or taken away with my consent."
        )
        signature = fo.customer_signature_attachment_id.sudo()
        if signature and signature.datas and (signature.mimetype or "").startswith("image/"):
            p["images"] = [
                {
                    "title": "Customer signature (%s)" % (fo.customer_signature_signer or ""),
                    "src": "data:%s;base64,%s"
                    % (
                        signature.mimetype,
                        signature.datas.decode()
                        if isinstance(signature.datas, bytes)
                        else signature.datas,
                    ),
                }
            ]
        p["sign"] = ["Customer — signature & date", "Field Engineer"]
        return p


# ------------------------------------------------- consignment delivery note
class P03A02ConsignmentNote(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a02_consignment_note"
    _inherit = "report.cd_p03_portal.a02_document_base"
    _description = "Consignment Delivery Note / Waybill"

    _doc_model = "fix.consignment"

    # A02 ERP audit pass 2 M02-14: the declared-value band a courier or
    # rider handles the parcel under
    _VALUE_BANDS = (
        (5000, "up to BDT 5,000"),
        (20000, "BDT 5,001-20,000"),
        (50000, "BDT 20,001-50,000"),
    )

    def _value_band(self, value):
        for ceiling, label in self._VALUE_BANDS:
            if (value or 0.0) <= ceiling:
                return label
        return "above BDT 50,000 (high value)"

    def _payload(self, cons):
        p = self._base(cons, "DELIVERY NOTE / WAYBILL", _label(cons, "state").upper())
        order = cons.service_order_id
        p["qr"] = cons.name or ""
        p["party_label"] = "Deliver To"
        if cons.dest_branch_id:
            p["bill_to"] = {"name": cons.dest_branch_id.name}
        elif order.customer_id:
            p["bill_to"] = self._party(order.customer_id)
        else:
            p["bill_to"] = {"name": cons.recipient_name or "—"}
        p["meta"] = [
            ("Consignment No.", cons.name or ""),
            ("Type", _label(cons, "consignment_type")),
            ("Scheduled", self._dt(cons.scheduled_date)),
            ("Origin", cons.origin_branch_id.name or ""),
            ("Destination", cons.dest_branch_id.name or ""),
            ("Courier", cons.courier_partner_id.name or ""),
            ("Rider", cons.rider_id.name or ""),
            ("Vehicle", cons.vehicle_registration or ""),
        ]
        bookings = (
            self.env["fix.courier.booking"].sudo().search([("consignment_id", "=", cons.id)])
            if "fix.courier.booking" in self.env
            else []
        )
        awbs = ", ".join(b.awb_no for b in bookings if b.awb_no)
        if awbs:
            p["meta"].append(("AWB / Tracking No.", awbs))
        if cons.consignment_type == "pickup" and order.customer_id:
            p["meta"].append(("Pickup From", self._party(order.customer_id)["address"] or ""))
        cod = getattr(cons, "cod_amount", 0.0) or 0.0
        p["meta"].append(
            ("Amount To Collect (BDT)", fmt_money(cod) if cod > 0.005 else "Nothing (prepaid)")
        )
        p["meta"].append(("Value Band", self._value_band(cons.declared_value_bdt)))
        device = order.device_id
        p["lines"] = []
        if order:
            p["tables"].append(
                {
                    "title": "Contents",
                    "cols": ["SL", "Service Order", "Device", "Serial", "Qty"],
                    "rows": [
                        [
                            1,
                            order.name or "",
                            device.display_name or "",
                            device.serial_number or "" if device else "",
                            "1",
                        ]
                    ],
                }
            )
        package = [
            ("Packaging", _label(cons, "packaging_type")),
            ("Outbound Seal No.", cons.outbound_seal_number or ""),
            ("Security Bag Barcode", cons.security_bag_barcode or ""),
            ("Actual Weight (kg)", fmt_qty(cons.actual_weight_kg)),
            (
                "Dimensions (cm)",
                "%s x %s x %s"
                % (fmt_qty(cons.length_cm), fmt_qty(cons.width_cm), fmt_qty(cons.height_cm)),
            ),
            ("Chargeable Weight (kg)", fmt_qty(cons.chargeable_weight_kg)),
            ("Declared Value (BDT)", fmt_money(cons.declared_value_bdt)),
            ("Transit Insurance", "Yes" if cons.insurance_flag else "No"),
        ]
        if cons.restricted_item:
            package.append(("Restricted Item", _label(cons, "restricted_item_class") or "Yes"))
        p["blocks"] = [{"title": "Package", "rows": package}]
        p["tables"].append(
            {
                "title": "Custody chain",
                "cols": ["Step", "Scanned At", "Location", "Scanned By", "Exception"],
                "rows": [
                    [
                        _label(scan, "step"),
                        self._dt(scan.scanned_at),
                        scan.location_branch_id.name or "",
                        scan.scanned_by.name or scan.scanned_by_user_id.name or "",
                        scan.exception_reason or "",
                    ]
                    for scan in cons.custody_ids.sorted(
                        lambda s: (s.scanned_at or s.create_date, s.id)
                    )
                ],
            }
        )
        pod = [
            ("Recipient", cons.recipient_name or ""),
            ("Delivered At", self._dt(cons.delivered_at)),
            ("POD Verified At", self._dt(cons.pod_verified_at)),
            ("POD Verified By", cons.pod_verified_by.name or ""),
        ]
        p["blocks"].append({"title": "Proof of delivery", "rows": pod})
        p["sign"] = [
            "Dispatched by (Origin)",
            "Rider / Courier",
            "Received by — name, signature & date",
        ]
        return p


# ------------------------------------------------- workshop job card / report
class P03A02WorkshopJobCard(models.AbstractModel):
    _name = "report.cd_p03_portal.report_a02_workshop_job"
    _inherit = "report.cd_p03_portal.a02_document_base"
    _description = "Workshop Job Card / Repair Report"

    _doc_model = "fix.workshop.job"

    def _payload(self, job):
        p = self._base(job, "WORKSHOP JOB CARD / REPAIR REPORT", _label(job, "state").upper())
        p["party_label"] = "Customer"
        p["bill_to"] = self._party(job.customer_id) if job.customer_id else {"name": "—"}
        p["meta"] = [
            ("Job Ref.", job.name or ""),
            ("Service Order", job.order_id.name or job.order_reference or ""),
            ("Booked In", self._dt(job.bookin_at or job.intake_date)),
            ("Technician", job.technician_id.name or ""),
            ("Bench", job.bench_id.display_name or ""),
            ("Repair Level", _label(job, "repair_level")),
            ("Priority", _label(job, "priority")),
            ("Completed", self._dt(job.completed_at)),
        ]
        p["service_item"] = " · ".join(
            x
            for x in (job.device_id.display_name, job.device_serial and "S/N " + job.device_serial)
            if x
        )
        p["blocks"] = [
            {
                "title": "Book-in",
                "rows": [
                    ("Reported Fault", job.fault_description or ""),
                    ("Condition at Book-In", job.bookin_condition or ""),
                    (
                        "Accessories",
                        "None received"
                        if job.bookin_no_accessories
                        else (job.bookin_accessories or ""),
                    ),
                    (
                        "Liquid Contact Indicator",
                        "Tripped" if job.bookin_lci_tripped else "Not tripped",
                    ),
                ],
            },
            {
                "title": "Diagnosis & repair",
                "rows": [
                    ("Diagnosis", job.diagnostic_findings or ""),
                    ("Repair Actions", job.repair_action_summary or ""),
                ],
            },
            {
                "title": "Quality control",
                "rows": [
                    (
                        "QC Result",
                        "Passed"
                        if job.qc_passed
                        else ("Pending" if not job.qc_inspected_at else "Failed"),
                    ),
                    (
                        "Inspected By",
                        job.qc_inspector_id.name or job.qc_inspector_user_id.name or "",
                    ),
                    ("Inspected At", self._dt(job.qc_inspected_at)),
                    ("QC Notes", job.qc_notes or ""),
                ],
            },
            # A02 pass 2 M31-10: the burn-in and the rework are part of the
            # repair record
            {
                "title": "Burn-in & rework",
                "rows": [
                    ("Test Protocol", job.protocol_id.display_name or ""),
                    ("Burn-In Started", self._dt(job.burn_in_started_at)),
                    ("Burn-In Completed", self._dt(job.burn_in_completed_at)),
                    ("Burn-In Minutes", "%.0f" % (job.burn_in_actual_minutes or 0.0)),
                    ("Thermal / Stress Crashes", str(job.thermal_crash_count or 0)),
                    (
                        "Burn-In Result",
                        "Passed"
                        if job.burn_in_passed
                        else ("Not run" if not job.burn_in_started_at else "Not passed"),
                    ),
                    ("Rework Loops", str(len(job.rework_ids))),
                ],
            },
        ]
        if not self.env.context.get("customer_copy"):
            # A02 pass 2 M31-10: the internal cost roll-up (the job card is
            # the workshop's record; the customer's copy leaves it out)
            p["blocks"].append(
                {
                    "title": "Internal cost roll-up (BDT)",
                    "rows": [
                        ("Parts Fitted", fmt_money(job.parts_total)),
                        ("Labour", fmt_money(job.labour_cost)),
                        ("Consumables", fmt_money(job.consumables_total)),
                        ("Total Direct Cost", fmt_money(job.total_repair_cost)),
                        ("Estimated Cost", fmt_money(job.estimated_cost)),
                        ("Full Cost (cost sheet)", fmt_money(job.full_cost)),
                    ],
                }
            )
        # A02 pass 2 M31-10: only the parts fitted on the bench (consumed);
        # a drafted, reserved or released line was printed as fitted
        fitted = job.part_line_ids.filtered(lambda ln: ln.reservation_state == "consumed")
        p["tables"] = [
            {
                "title": "Parts fitted",
                "cols": ["SL", "Part No.", "Description", "Fitted Serial", "Qty"],
                "rows": [
                    [
                        i,
                        line.part_number or line.product_id.default_code or "",
                        line.part_name or line.product_id.name or "",
                        line.fitted_serial_number or line.lot_serial_number or "",
                        fmt_qty(line.quantity),
                    ]
                    for i, line in enumerate(fitted, 1)
                ],
            },
            {
                "title": "Tests",
                "cols": ["Test", "Measured", "Limits", "Result", "Tested At"],
                "rows": [
                    [
                        t.test_name or t.step_id.display_name or "",
                        ("%g %s" % (t.measured_value, t.unit or "")).strip()
                        if t.has_limits
                        else "",
                        ("%g – %g %s" % (t.lower_limit, t.upper_limit, t.unit or "")).strip()
                        if t.has_limits
                        else "",
                        "Pass" if t.passed else "Fail",
                        self._dt(t.tested_at),
                    ]
                    for t in job.test_result_ids
                ],
            },
        ]
        p["sign"] = ["Technician", "QC Inspector", "Customer — received in good condition"]
        return p


# ---------------------------------------------------- data recovery documents
class P03A02DataCaseFile(models.AbstractModel):
    """A02 pass 2 M06-10: the case's paper trail in one document - the intake
    receipt, the chain-of-custody form (every hand-off with both people) and
    the hand-over receipt."""

    _name = "report.cd_p03_portal.report_a02_data_case"
    _inherit = "report.cd_p03_portal.a02_document_base"
    _description = "Data Recovery Case File (intake, custody, hand-over)"

    _doc_model = "fix.data.recovery.case"

    def _payload(self, case):
        p = self._base(case, "DATA RECOVERY CASE FILE", _label(case, "state").upper())
        p["party_label"] = "Customer"
        p["bill_to"] = self._party(case.customer_id) if case.customer_id else {"name": "-"}
        p["meta"] = [
            ("Case No.", case.name or ""),
            ("Media Received", self._dt(case.received_at)),
            ("Media", _label(case, "media_type")),
            ("Media Serial No.", case.media_serial_number or ""),
        ]
        units = case.media_unit_ids
        recovered = "%d / %.2f" % (case.recovered_files_count or 0, case.recovered_volume_gb or 0.0)
        p["blocks"] = [
            {
                "title": "Intake receipt",
                "rows": [
                    ("Reported Failure", case.failure_symptoms or ""),
                    ("Data the Customer Needs", case.target_data_description or ""),
                    ("Sealed Bags", ", ".join(units.mapped("seal_number")) or "-"),
                    ("Customer Declarations", case.customer_declarations or ""),
                ],
            },
            {
                "title": "Hand-over receipt",
                "rows": [
                    ("Handed Over At", self._dt(case.handover_at)),
                    ("Recipient", case.handover_recipient_id.display_name or ""),
                    ("Recipient Verified By", _label(case, "handover_verification_method")),
                    ("Verification", case.handover_verification_ref or ""),
                    ("Target Drive S/N", case.encrypted_target_serial or ""),
                    ("Recovered Files / GB", recovered),
                ],
            },
        ]
        p["tables"] = [
            {
                "title": "Chain of custody",
                "cols": ["SL", "When", "Action", "Recorded By", "Second Person", "What"],
                "rows": [
                    [
                        i,
                        self._dt(ev.event_at),
                        _label(ev, "action"),
                        ev.actor_id.name or "",
                        ev.witness_id.name or "",
                        ev.description or "",
                    ]
                    for i, ev in enumerate(case.custody_event_ids.sorted("id"), 1)
                ],
            }
        ]
        p["sign"] = ["Received from the customer", "Lab custodian", "Customer - data received"]
        return p


class P03A02DataQuote(models.AbstractModel):
    """A02 pass 2 M06-10: the data-recovery quotation the customer accepts."""

    _name = "report.cd_p03_portal.report_a02_data_quote"
    _inherit = "report.cd_p03_portal.a02_document_base"
    _description = "Data Recovery Quotation"

    _doc_model = "fix.data.quote"

    def _payload(self, quote):
        p = self._base(quote, "DATA RECOVERY QUOTATION", _label(quote, "state").upper())
        customer = quote.customer_id if "customer_id" in quote._fields else None
        customer = customer or quote.case_id.customer_id
        p["party_label"] = "Quoted To"
        p["bill_to"] = self._party(customer) if customer else {"name": "-"}
        p["meta"] = [
            ("Quotation No.", quote.name or ""),
            ("Case No.", quote.case_id.name or ""),
            ("Valid Until", self._d(quote.valid_until)),
            ("Sent", self._dt(quote.sent_at)),
        ]
        p["blocks"] = [
            {
                "title": "Price and terms",
                "rows": [
                    ("Scope", quote.description or ""),
                    ("Recovery Fee (BDT, before VAT)", fmt_money(quote.amount)),
                    ("Donor Fee, non-refundable (BDT)", fmt_money(quote.donor_fee_bdt)),
                    ("No Data, No Fee", "Yes" if quote.no_data_no_fee_applies else "No"),
                    ("Accepted", self._dt(quote.accepted_at)),
                    ("Acceptance", _label(quote, "acceptance_channel")),
                ],
            }
        ]
        p["notes"] = [
            "Under no-data-no-fee the recovery fee is due only when the data you need is "
            "recovered; the donor fee is due in every case."
        ]
        p["sign"] = ["For 1000FiX Services Ltd.", "Customer - accepted"]
        return p
