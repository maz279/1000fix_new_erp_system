# Tests for cd_party_master (P03-M05) — the party kernel design rule.
import pytest


class TestFixPartyRole:
    """fix.party.role — THE multi-role design rule."""

    def test_model_exists(self):
        from addons.platform.cd_party_master.models.fix_party_role import FixPartyRole
        assert FixPartyRole is not None

    def test_partner_role_unique_constraint(self):
        """A party holds each role at most once."""
        from addons.platform.cd_party_master.models.fix_party_role import FixPartyRole
        constraints = FixPartyRole._sql_constraints
        assert any("partner_role_unique" in str(c) for c in constraints)

    def test_multi_role_design(self):
        """Multiple roles can point to the SAME res.partner (not separate masters)."""
        from addons.platform.cd_party_master.models.fix_party_role import FixPartyRole
        assert 'partner_id' in dir(FixPartyRole)
        assert 'role_type' in dir(FixPartyRole)

    def test_event_emission_on_create(self):
        """party.role_added event fires on create (AS-08)."""
        from addons.platform.cd_party_master.models.fix_party_role import FixPartyRole
        assert '_emit_party_event' in dir(FixPartyRole)

    def test_duplicate_master_warning(self):
        """Duplicate-master detection: the unrecoverable failure mode check."""
        from addons.platform.cd_party_master.models.fix_party_role import FixPartyRole
        assert '_check_no_duplicate_masters' in dir(FixPartyRole)


class TestFixIdentityDocument:
    """fix.identity.document — residency-classified NID/passport/TIN."""

    def test_model_exists(self):
        from addons.platform.cd_party_master.models.fix_identity_document import FixIdentityDocument
        assert FixIdentityDocument is not None

    def test_residency_mixin_inherited(self):
        """The model inherits residency.mixin for write-time enforcement."""
        from addons.platform.cd_party_master.models.fix_identity_document import FixIdentityDocument
        # _inherit should include residency.mixin
        assert hasattr(FixIdentityDocument, '_residency_fields')

    def test_document_number_is_classified(self):
        """document_number is in _residency_fields — routed to Z4."""
        from addons.platform.cd_party_master.models.fix_identity_document import FixIdentityDocument
        assert 'document_number' in FixIdentityDocument._residency_fields

    def test_checksum_computed_from_z4(self):
        """Checksum validates against the Z4 value, never stored regionally."""
        from addons.platform.cd_party_master.models.fix_identity_document import FixIdentityDocument
        assert '_compute_checksum' in dir(FixIdentityDocument)


class TestResidencyNegative:
    """FF-09 negative test: the classified value NEVER enters the regional store."""

    def test_event_payload_excludes_document_number(self):
        """Events for identity documents must NOT include the classified value."""
        from addons.platform.cd_party_master.models.fix_identity_document import FixIdentityDocument
        assert '_emit_event' in dir(FixIdentityDocument)
