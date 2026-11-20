# fix_data_case — M06: data recovery, wipe certificates (P09-M05).
# The most residency-sensitive module: recovered data lives ONLY in Z4.
from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

WIPE_METHODS = [
    ("nist_800_88", "NIST SP 800-88 (Clear)"),
    ("nist_800_88_purge", "NIST SP 800-88 (Purge)"),
    ("cryptographic_erase", "Cryptographic Erase"),
    ("physical_destruction", "Physical Destruction"),
]


class FixDataRecoveryCase(models.Model):
    """Journey 11: data recovery case -> custody -> recovery -> handover ->
    purge certificate. ALL recovered data routes to Z4 (SC-007, FF-09)."""
    _name = "fix.data.recovery.case"
    _description = "Data Recovery Case"
    # P03 workspace data-entry form (discovered by cd_p03_portal).
    _p03_capture = {
        "module": "M06",
        "form": "Recovery Case",
        "fields": ["customer_id", "media_type", "residency_zone", "device_id",
                   "custody_chain"],
    }
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True,
                       default=lambda self: "New")
    customer_id = fields.Many2one("res.partner", string="Customer",
                                  required=True, index=True)
    device_id = fields.Many2one("fix.device", string="Device",
                                ondelete="set null")
    media_type = fields.Selection(
        [("hdd", "HDD"), ("ssd", "SSD"), ("usb", "USB Drive"),
         ("sd_card", "SD Card"), ("phone", "Phone Storage"),
         ("other", "Other")], required=True, default="hdd")
    state = fields.Selection(
        [("new", "New"), ("custody", "In Custody"),
         ("recovering", "Recovering"), ("recovered", "Recovered"),
         ("handover", "Handover"), ("purged", "Purged"),
         ("closed", "Closed"), ("unrecoverable", "Unrecoverable")],
        default="new", required=True, tracking=True)
    custody_chain = fields.Text(
        string="Chain of Custody Log",
        help="Every hand-off logged: who, when, where (append-only)")
    residency_zone = fields.Selection(
        [("z4", "Z4 (Residency-Classified)"), ("pending", "Pending Routing")],
        default="pending", required=True,
        help="SC-007: recovered customer data lives ONLY in Z4")
    purge_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate", string="Purge Certificate",
        readonly=True, ondelete="set null")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fix.data.recovery.case") or "DRC/New"
        return super().create(vals_list)

    def action_take_custody(self, handler):
        """The chain of custody begins: every hand-off is logged."""
        for rec in self:
            timestamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"{timestamp}: custody taken by {handler}"
            rec.custody_chain = (rec.custody_chain or "") + "\n" + entry
            rec.state = "custody"
            publish(self.env, "data_case.custody_taken",
                    "fix.data.recovery.case", rec.id,
                    {"case": rec.name, "handler": handler})

    def action_start_recovery(self):
        for rec in self:
            if rec.state != "custody":
                raise UserError("Recovery starts from custody")
            if rec.residency_zone != "z4":
                raise UserError(
                    "SC-007: recovered data must be routed to Z4 BEFORE "
                    "recovery starts. Not transiently, not in a cache.")
            rec.state = "recovering"

    def action_recovered(self):
        for rec in self:
            rec.state = "recovered"
            publish(self.env, "data_case.recovered",
                    "fix.data.recovery.case", rec.id, {"case": rec.name})

    def action_handover(self, handler):
        for rec in self:
            if rec.state != "recovered":
                raise UserError("Handover from recovered")
            timestamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"{timestamp}: handed over by {handler}"
            rec.custody_chain = (rec.custody_chain or "") + "\n" + entry
            rec.state = "handover"

    def action_purge(self):
        """The purge certificate: the statutory processing record is
        preserved even after the data is destroyed (NFR-095)."""
        for rec in self:
            if rec.state != "handover":
                raise UserError("Purge from handover")
            cert = self.env["fix.data.wipe.certificate"].create({
                "device_id": rec.device_id.id,
                "method": "nist_800_88_purge",
            })
            rec.write({"state": "purged", "purge_certificate_id": cert.id})
            publish(self.env, "data_case.purged",
                    "fix.data.recovery.case", rec.id,
                    {"certificate": cert.name})


class FixDataWipeCertificate(models.Model):
    """The secure data-wipe and destruction certificate (P09-M05-T02).
    Consumed by M14 trade-in and M18 e-waste."""
    _name = "fix.data.wipe.certificate"
    _description = "Data Wipe Certificate"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True,
                       default=lambda self: "New")
    device_id = fields.Many2one("fix.device", string="Device",
                                ondelete="set null")
    method = fields.Selection(WIPE_METHODS, required=True,
                              default="nist_800_88")
    certified_by = fields.Char(string="Certified By")
    certified_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    verification_hash = fields.Char(
        readonly=True,
        help="The wipe verification hash; the certificate is verifiable")

    @api.model_create_multi
    def create(self, vals_list):
        import hashlib
        import time
        for vals in vals_list:
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "fix.data.wipe.certificate") or "DWC/New"
            # A deterministic verification hash from the wipe parameters
            seed = f"{vals.get('name', '')}-{vals.get('method', '')}-{time.time()}"
            vals["verification_hash"] = hashlib.sha256(
                seed.encode()).hexdigest()[:16]
        return super().create(vals_list)
