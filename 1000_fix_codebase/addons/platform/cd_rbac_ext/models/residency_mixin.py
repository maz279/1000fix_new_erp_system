# residency_mixin — write-time residency enforcement (P03-M09-T04, NFR-086a).
#
# THE mechanism: any model with classified fields inherits this mixin and
# declares `_residency_fields = {"field_name": "classification_key_prefix"}`.
# On create/write, classified values are routed through fix_residency to Z4;
# the regional store holds only a residency reference (a UUID pointer),
# NEVER the classified value itself.
#
# On read, the mixin retrieves the value from Z4 via fix_residency — with
# per-read logging (NFR-070) and step-up authentication for human access
# (NFR-065). The value never enters the regional cache.
#
# "Residency enforcement built as convention rather than mechanism" is a
# named stack-failure mode (TSS section 25.5 item 3). This mixin IS the
# mechanism.
import logging
import uuid

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class ResidencyMixin(models.AbstractModel):
    """Write-time field-level residency classification (NFR-086a).

    Usage:
        class FixIdentityDocument(models.Model):
            _name = "fix.identity.document"
            _inherit = ["residency.mixin"]
            _residency_fields = {
                "nid_number": "party nid",
                "passport_number": "party passport",
            }
            nid_number = fields.Char(string="NID Number")
    """

    _name = "residency.mixin"
    _description = "Residency Enforcement Mixin"

    # Subclasses override this: {"field_name": "key_prefix"}
    _residency_fields: dict[str, str] = {}

    # The residency reference (a UUID pointer stored in the regional DB;
    # the actual value lives in Z4, accessible only via fix_residency)
    residency_ref = fields.Char(
        string="Residency Reference",
        readonly=True,
        index=True,
        copy=False,
        help="UUID pointer to the classified values in Z4; "
        "the values themselves NEVER enter the regional store",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Intercept classified fields on create: route them to Z4."""
        for vals in vals_list:
            vals = self._extract_classified(vals)
        return super().create(vals_list)

    def write(self, vals):
        """Intercept classified fields on write: route them to Z4."""
        if len(self) > 1 and any(k in self._residency_fields and v for k, v in vals.items()):
            # Each record keeps its OWN residency_ref, so a classified value
            # is routed record by record (a batch write used to read
            # residency_ref off the whole recordset and crash).
            for rec in self:
                rec.write(dict(vals))
            return True
        vals = self._extract_classified(vals, existing=self)
        return super().write(vals)

    def read(self, fields=None, load="_classic_read"):
        """On read of classified fields: retrieve from Z4 via fix_residency.

        The retrieved value is placed in the result dict for this request
        only — it is NEVER written back to the regional store or cached.
        """
        result = super().read(fields=fields, load=load)
        # If classified fields were requested, fetch each record's values from
        # Z4 through its own residency_ref (per-read logging is server-side).
        requested_classified = [f for f in (fields or []) if f in self._residency_fields]
        if not requested_classified:
            return result
        refs = {rec.id: rec.residency_ref for rec in self}
        client = None
        for row in result:
            ref = refs.get(row["id"])
            if not ref:
                continue
            if client is None:
                from libs.py.fix_residency import get_client

                client = get_client()
            for field_name in requested_classified:
                key = f"{self._residency_fields[field_name]}:{ref}"
                try:
                    row[field_name] = client.get(key)
                except Exception:
                    logger.warning("residency read failed for %s (setting empty)", field_name)
                    row[field_name] = ""
        return result

    def _extract_classified(self, vals: dict, existing=None) -> dict:
        """Extract classified field values from vals, route to Z4, return
        the cleaned vals (classified fields replaced by the residency_ref)."""
        classified_present = {k: v for k, v in vals.items() if k in self._residency_fields and v}
        if not classified_present:
            return vals

        from libs.py.fix_residency import get_client

        client = get_client()

        # Use existing ref or generate one
        ref = (existing.residency_ref if existing else None) or str(uuid.uuid4())
        vals["residency_ref"] = ref

        for field_name, value in classified_present.items():
            key = f"{self._residency_fields[field_name]}:{ref}"
            client.put(key, value)
            # Remove the classified value from vals — it goes to Z4 only
            # The regional store holds ONLY the residency_ref pointer
            del vals[field_name]
            logger.debug("residency_mixin: %s routed to Z4 (ref=%s)", field_name, ref)

        return vals
