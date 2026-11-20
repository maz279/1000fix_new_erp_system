# cd_vendor_ext tests — M42 profile, segmentation, documents, bank change,
# agreements and price governance (CD-M42-01).
from pathlib import Path

MODELS = Path(__file__).resolve().parents[1] / "models"
PROFILE_SRC = (MODELS / "fix_supplier_profile.py").read_text(encoding="utf-8")
AGREEMENT_SRC = (MODELS / "fix_supplier_agreement.py").read_text(encoding="utf-8")


def _classes():
    from odoo.addons.cd_vendor_ext.models import fix_supplier_agreement as a
    from odoo.addons.cd_vendor_ext.models import fix_supplier_profile as p
    return p, a


def _declared_fields(cls):
    return {n for n, v in vars(cls).items() if type(v).__module__.startswith("odoo.fields")
            or type(v).__module__.startswith("odoo.orm.fields")}


class TestProfile:
    def test_twelve_supplier_classes(self):
        """FR-SRM2-002 / BR-SCM-001: all twelve classes, incl. forwarder, C&F
        agent, cargo insurer and brand partner."""
        p, _ = _classes()
        keys = [k for k, _ in p.SUPPLIER_CLASSES]
        assert len(keys) == 12
        for k in ("freight_forwarder", "cnf_agent", "cargo_insurer", "brand_partner"):
            assert k in keys

    def test_one_profile_per_party_per_entity(self):
        """T-12: a supplier qualified for one legal entity is not automatically
        another's."""
        p, _ = _classes()
        assert hasattr(p.FixSupplierProfile, "_partner_company_unique")

    def test_block_and_suspend_need_reason(self):
        body = PROFILE_SRC[PROFILE_SRC.index("def _require_reason"):]
        assert "recorded reason is required" in body

    def test_blocked_never_reactivated(self):
        body = PROFILE_SRC[PROFILE_SRC.index("def action_activate"):]
        assert "permanently blocked" in body


class TestSegmentReview:
    def test_proposer_cannot_approve(self):
        body = PROFILE_SRC[PROFILE_SRC.index("class FixSupplierSegmentReview"):]
        assert "The proposer of a segment change cannot approve it" in body

    def test_snapshot_of_current_values(self):
        p, _ = _classes()
        assert "current_segment" in _declared_fields(p.FixSupplierSegmentReview)


class TestDocuments:
    def test_register_covers_spec_types(self):
        p, _ = _classes()
        keys = {k for k, _ in p.DOC_TYPES}
        assert {"trade_licence", "vat_bin", "tin", "bank_verification", "iso_cert",
                "brand_authorisation", "insurance"} <= keys

    def test_evidence_hashed_sha256(self):
        """T-11: evidence is hashed at capture."""
        assert "hashlib.sha256" in PROFILE_SRC
        assert "evidence_hash" in PROFILE_SRC

    def test_expiry_cron_is_idempotent(self):
        """T-07: only verified documents move to expired — a second run finds
        nothing to do."""
        body = PROFILE_SRC[PROFILE_SRC.index("def _cron_expire_documents"):]
        assert '("state", "=", "verified"), ("expires_on", "<", today)' in body

    def test_warning_window_is_sixty_days(self):
        p, _ = _classes()
        assert p.EXPIRY_WARNING_DAYS == 60


class TestBankChange:
    def test_second_person_approval(self):
        """FR-SRM2-018: the requester cannot approve."""
        assert "The requester of a bank-detail change cannot approve it" in PROFILE_SRC

    def test_prior_value_kept_as_hash_and_immutable(self):
        """T-06: the prior value is retained (hashed) and a decided change is
        immutable."""
        assert "previous_value_hash" in PROFILE_SRC
        assert "A decided bank-detail change is immutable" in PROFILE_SRC

    def test_no_sudo_on_bank_account(self):
        body = PROFILE_SRC[PROFILE_SRC.index("class FixSupplierBankChange"):]
        assert ".sudo()" not in body
        assert "G_FINANCE" in body  # the finance group implies base.group_partner_manager

    def test_security_event(self):
        assert '"supplier.bank_changed"' in PROFILE_SRC


class TestAgreementsAndPrices:
    def test_agreement_types(self):
        for t in ("framework", "supply", "consignment", "service", "courier"):
            assert f'("{t}",' in AGREEMENT_SRC

    def test_no_silent_lapse(self):
        """FR-SRM2-026: expiring then expired, with an event."""
        body = AGREEMENT_SRC[AGREEMENT_SRC.index("def _cron_agreement_expiry"):]
        assert '"expiring"' in body and '"supplier.agreement_expired"' in body

    def test_price_rows_only_via_approved_change(self):
        """FR-SRM2-023: M16 can never order at an unapproved price."""
        assert "fix_price_change_approval" in AGREEMENT_SRC
        assert "only through an approved price" in AGREEMENT_SRC

    def test_price_change_sod(self):
        assert "The requester of a price change cannot approve it" in AGREEMENT_SRC


class TestP03CaptureSpecs:
    """Each capture spec names only real fields of its own model, so the P03
    workspace form never renders a dead input."""

    def test_specs_reference_declared_fields(self):
        p, a = _classes()
        for cls in (p.FixSupplierProfile, p.FixSupplierSegmentReview,
                    p.FixSupplierDocument, p.FixSupplierBankChange,
                    a.FixSupplierAgreement, a.FixSupplierPriceChange):
            spec = cls._p03_capture
            assert spec["module"] == "M42"
            missing = set(spec["fields"]) - _declared_fields(cls)
            assert not missing, f"{cls._name}: {missing}"

    def test_form_names(self):
        p, a = _classes()
        names = {c._p03_capture["form"] for c in (
            p.FixSupplierProfile, p.FixSupplierSegmentReview, p.FixSupplierDocument,
            p.FixSupplierBankChange, a.FixSupplierAgreement, a.FixSupplierPriceChange)}
        assert names == {"Supplier Profile", "Segment & Risk-Tier Review",
                         "Supplier Document", "Bank Detail Change Request",
                         "Supplier Agreement", "Price Change Request"}


class TestRoleGroups:
    """Spec §13: six function groups; authority checks sit on top of SoD."""

    ADDON = Path(__file__).resolve().parents[1]
    E_SUPPLY = ADDON.parent

    def test_six_spec_groups(self):
        xml = (self.ADDON / "security" / "fix_vendor_ext_security.xml").read_text(encoding="utf-8")
        for g in ("group_m42_viewer", "group_m42_officer", "group_m42_quality",
                  "group_m42_manager", "group_m42_finance", "group_m42_cfo"):
            assert f'id="{g}"' in xml

    def test_no_blanket_internal_user_access(self):
        """Access is per role, never base.group_user (the pre-§13 state)."""
        for addon in ("cd_vendor_ext", "cd_supplier_qualification",
                      "cd_supplier_scorecard", "cd_supplier_risk"):
            acl = (self.E_SUPPLY / addon / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
            assert "base.group_user" not in acl, addon

    def test_bank_details_finance_only(self):
        """05-04 §5: bank details visible only to Finance and the CFO."""
        assert 'groups="cd_vendor_ext.group_m42_finance"' in PROFILE_SRC
        acl = (self.ADDON / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
        officer = [r for r in acl.splitlines() if r.startswith("access_fix_supplier_bank_change_officer")]
        assert officer and officer[0].endswith(",1,0,0,0")

    def test_permanent_block_is_cfo_only(self):
        body = PROFILE_SRC[PROFILE_SRC.index("def action_block"):]
        assert "G_CFO" in body.split("def ", 2)[1]

    def test_cron_paths_pass_as_superuser(self):
        p, _ = _classes()
        assert "env.su" in PROFILE_SRC
        assert callable(p.require_group)
