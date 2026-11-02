# S2 — the Consent Enforcement API (A03 gap-plan Part IV, service S2).
#
# WHY this file exists. Before it, every caller re-implemented "is this party
# consented?" its own way:
#   * M35 campaign launch (_consented) filtered by CHANNEL ONLY and ignored
#     the processing purpose entirely, so a party who had opted in to
#     service_updates on SMS was treated as consenting to marketing SMS;
#   * M27 notification templates carried a consent_class that nothing read;
#   * M10 voucher and expiry sends checked nothing at all.
# Three implementations of one legal obligation is three places for it to be
# wrong, and the middle one was.
#
# This is THE check. Re-implementing it elsewhere is a review-blocking defect
# (gap-plan Part IV rule: "any module needing one of these capabilities must
# consume the service").
#
# The model is extended rather than wrapped so that the service travels with
# the register it reads: there is no way to have fix.consent installed and
# the decision procedure missing.
from odoo import api, models
from odoo.exceptions import ValidationError

# Which STORED channel values satisfy a request for a given channel.
#
# The 'marketing' umbrella is a blanket all-channel marketing opt-in, so it
# only ever satisfies the marketing purpose. A party who accepted marketing on
# every channel has NOT thereby consented to having their call recorded, and
# the channel-only check this service replaces would have said they had.
_CHANNEL_FAMILY = {
    "sms": ("sms",),
    "whatsapp": ("whatsapp",),
    "email": ("email",),
    "push": ("push",),
    "voice": ("voice",),
}
_MARKETING_UMBRELLA = "marketing"

# A basis other than consent is lawful, but it must be DECLARED by the caller
# and recorded — never inferred here. PDPO s.19 / GDPR Art. 6 shape.
NON_CONSENT_BASES = {
    "contract": "Performance of a contract",
    "legal_obligation": "Compliance with a legal obligation",
    "vital_interest": "Protection of a vital interest",
}

# Purposes that exist to serve an order the customer themselves placed. Kept
# as data rather than hard-coded into callers so the lawful-basis argument is
# auditable in one place; the caller still has to pass basis= explicitly.
TRANSACTIONAL_PURPOSES = {"service_updates"}


class FixConsentService(models.Model):
    """The decision procedure over the consent register."""

    _inherit = "fix.consent"

    # ---- helpers ---------------------------------------------------------
    @api.model
    def _consent_channels_for(self, purpose: str, channel: str) -> tuple:
        """The stored channel values that can satisfy (purpose, channel)."""
        family = list(_CHANNEL_FAMILY.get(channel, (channel,)))
        if purpose == "marketing":
            family.append(_MARKETING_UMBRELLA)
        return tuple(family)

    @api.model
    def _decisive_row(self, rows):
        """The consent decision currently in force, out of a party's history.

        The LATEST decision wins: a withdrawal supersedes an older grant, and
        a fresh grant after a withdrawal re-permits. 'superseded' rows are the
        historical grants the append-only chain preserves (T-09) and are never
        decisive — the withdrawal that superseded them is.
        """
        # Ordered by timestamp, with the ROW ID as the tie-break. Two
        # decisions taken in the same second are a real pattern -- a portal
        # form that withdraws and re-grants in one submission -- and leaving
        # the winner to search order would make the verdict arbitrary.
        decisive, decisive_key = None, None
        for row in rows:
            if row.state == "superseded":
                continue
            when = row.date_withdrawn or row.date_granted or row.create_date
            key = (when, row.id)
            if decisive_key is None or (when and key > decisive_key):
                decisive, decisive_key = row, key
        return decisive

    # ---- the API ---------------------------------------------------------
    @api.model
    def consent_check(self, partner, purpose, channel, basis="consent", company=None):
        """THE consent decision. One call, one verdict, fully explained.

        Args:
            partner: a res.partner record or id. Falsy means an unidentified
                contact, which cannot be consent-checked at all — that is a
                refusal, not a pass.
            purpose: a fix.consent purpose value (the PROCESSING purpose, not
                the message type).
            channel: the delivery channel the caller is about to use.
            basis: 'consent' (default) or one of NON_CONSENT_BASES. A
                non-consent basis is permitted but is echoed in the verdict so
                the delivery log can prove what was relied on.
            company: restrict to this company's register (defaults to the
                environment company; company-less rows always count).

        Returns a verdict dict. It never raises, so each caller decides
        whether a refusal is an exception (consent_assert) or a suppression
        (the delivery log's 'suppressed' state):

            allowed      bool
            decision     granted | withdrawn | expired | absent
                         | basis_declared | unidentified | history_only
            reason       human-readable, safe to log and to show an agent
            consent_id   the decisive fix.consent row, or False
            basis        what was relied on
            purpose, channel, partner_id   echoed back for the audit row
        """
        partner_id = getattr(partner, "id", partner) or False
        verdict = {
            "allowed": False,
            "decision": "absent",
            "reason": "",
            "consent_id": False,
            "basis": basis,
            "purpose": purpose,
            "channel": channel,
            "partner_id": partner_id,
        }
        if basis != "consent":
            if basis not in NON_CONSENT_BASES:
                verdict["reason"] = "Unknown lawful basis %r. Declare one of: consent, %s." % (
                    basis,
                    ", ".join(sorted(NON_CONSENT_BASES)),
                )
                return verdict
            verdict.update(
                allowed=True,
                decision="basis_declared",
                reason="Processed under a declared non-consent basis: %s. The "
                "declaration is recorded; it is not a consent record." % NON_CONSENT_BASES[basis],
            )
            return verdict
        if not partner_id:
            verdict.update(
                decision="unidentified",
                reason="No party is identified on this contact, so consent cannot "
                "be verified. An unverifiable consent is not a consent.",
            )
            return verdict

        channels = self._consent_channels_for(purpose, channel)
        company_id = getattr(company, "id", company) or self.env.company.id
        rows = self.sudo().search(
            [
                ("partner_id", "=", partner_id),
                ("purpose", "=", purpose),
                ("channel", "in", list(channels)),
                ("company_id", "in", [company_id, False]),
            ]
        )
        if not rows:
            verdict["reason"] = (
                "No consent record for purpose '%s' on channel '%s'. Absence of "
                "a record is a refusal, not a permission." % (purpose, channel)
            )
            return verdict

        decisive = self._decisive_row(rows)
        if decisive is None:
            verdict.update(
                decision="history_only",
                reason="Only superseded consent history exists for purpose '%s' "
                "on channel '%s' — no decision is currently in force." % (purpose, channel),
            )
            return verdict

        verdict["consent_id"] = decisive.id
        verdict["decision"] = decisive.state
        if decisive.state == "granted":
            verdict.update(
                allowed=True,
                reason="Consent granted %s for '%s' on '%s' against notice %s."
                % (
                    decisive.date_granted or decisive.create_date,
                    purpose,
                    decisive.channel,
                    decisive.notice_version_id.version or "(none)",
                ),
            )
        elif decisive.state == "withdrawn":
            verdict["reason"] = (
                "Consent for '%s' on '%s' was withdrawn %s and has not been "
                "re-granted." % (purpose, channel, decisive.date_withdrawn)
            )
        else:
            verdict["reason"] = "Consent for '%s' on '%s' is %s." % (
                purpose,
                channel,
                decisive.state,
            )
        return verdict

    @api.model
    def consent_check_bulk(self, partners, purpose, channel, company=None):
        """The same decision over a recordset, in a bounded number of queries.

        Campaign launch resolves tens of thousands of recipients; calling
        consent_check() per party would issue one search each. Returns

            (allowed_partners, excluded_verdicts_by_partner_id)

        so the caller can report WHY it excluded a party rather than only how
        many it excluded — which is what a regulator asks for.
        """
        Partner = self.env["res.partner"]
        partners = partners if partners else Partner
        if not partners:
            return Partner, {}
        channels = self._consent_channels_for(purpose, channel)
        company_id = getattr(company, "id", company) or self.env.company.id
        rows = self.sudo().search(
            [
                ("partner_id", "in", partners.ids),
                ("purpose", "=", purpose),
                ("channel", "in", list(channels)),
                ("company_id", "in", [company_id, False]),
            ]
        )
        by_partner = {}
        for row in rows:
            by_partner.setdefault(row.partner_id.id, []).append(row)
        allowed_ids, excluded = [], {}
        for partner in partners:
            decisive = self._decisive_row(by_partner.get(partner.id, []))
            if decisive is not None and decisive.state == "granted":
                allowed_ids.append(partner.id)
                continue
            state = decisive.state if decisive is not None else "absent"
            excluded[partner.id] = {
                "allowed": False,
                "decision": state,
                "consent_id": decisive.id if decisive is not None else False,
                "reason": (
                    "No consent record for purpose '%s' on channel '%s'." % (purpose, channel)
                    if state == "absent"
                    else "Latest consent decision for '%s' on '%s' is %s."
                    % (purpose, channel, state)
                ),
                "basis": "consent",
                "purpose": purpose,
                "channel": channel,
                "partner_id": partner.id,
            }
        return Partner.browse(allowed_ids), excluded

    @api.model
    def consent_assert(self, partner, purpose, channel, basis="consent", what="This send"):
        """consent_check() as a gate: raises, with the explained reason.

        For callers whose correct behaviour on a refusal is to stop rather
        than to suppress and carry on — call recording, for instance.
        """
        verdict = self.consent_check(partner, purpose, channel, basis=basis)
        if not verdict["allowed"]:
            raise ValidationError(
                "%s is refused on consent grounds. %s" % (what, verdict["reason"])
            )
        return verdict
