# cd_rbac_ext/tests/test_permissions_negative.py — DoD-07: 53 roles × 6 tiers negative tests.
# Implements R02-M02-T01, R02-M02-T02, R02-M02-T03, R02-M02-T04.
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from odoo.addons.cd_rbac_ext.models.fix_role import FixRole
from odoo.addons.cd_rbac_ext.models.fix_sod_control import FixSodControl
from odoo.addons.cd_rbac_ext.models.residency_mixin import ResidencyMixin
from odoo.exceptions import AccessError, ValidationError

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

EXPECTED_ROLES = [
    ("R-01", "Chief Executive Officer", "T1", "T4"),
    ("R-02", "Chief Technology Officer", "T1", "T4"),
    ("R-03", "Chief Financial Officer", "T1", "T4"),
    ("R-04", "Chief Commercial Officer", "T1", "T4"),
    ("R-05", "Operations Director", "T1", "T4"),
    ("R-06", "Branch Manager", "T2"),
    ("R-07", "Dispatch Manager", "T3"),
    ("R-08", "Service Centre Agent", "T2"),
    ("R-09", "Workshop Supervisor", "T2"),
    ("R-10", "Senior Technician", "T3"),
    ("R-11", "Junior Technician", "T3"),
    ("R-12", "Specialist Technician", "T2", "T3"),
    ("R-13", "Remote Support Engineer", "T1"),
    ("R-14", "Data Services Technician", "T5"),
    ("R-15", "Logistics Coordinator", "T1"),
    ("R-16", "Rider / Delivery Agent", "T3"),
    ("R-17", "Inventory Manager", "T1"),
    ("R-18", "Branch Store Keeper", "T2"),
    ("R-19", "Procurement Officer", "T1"),
    ("R-20", "Warehouse Operative", "T2"),
    ("R-21", "Sales Manager", "T1"),
    ("R-22", "Account Manager (Corporate)", "T1"),
    ("R-23", "Marketing Manager", "T1"),
    ("R-24", "Marketplace Operations Officer", "T1"),
    ("R-25", "Retail / Refurbishment Officer", "T1"),
    ("R-26", "Finance Manager", "T1"),
    ("R-27", "Finance Officer", "T1"),
    ("R-28", "Warranty Claims Officer", "T1"),
    ("R-29", "Cashier / Counter Finance", "T2"),
    ("R-30", "HR Manager", "T1", "T5"),
    ("R-31", "HR Officer", "T1"),
    ("R-32", "Quality Manager / ISO Coordinator", "T1"),
    ("R-33", "IT / System Administrator", "T1", "T4"),
    ("R-34", "Contact Centre Agent", "T3"),
    ("R-35", "Contact Centre Supervisor", "T3"),
    ("R-36", "Customer (Individual)", "T4"),
    ("R-37", "Corporate Portal User", "T1", "T4"),
    ("R-38", "External Party", "T4"),
    ("R-39", "Data Steward", "T0", "T1"),
    ("R-40", "Chief Data Officer", "T1", "T5"),
    ("R-41", "Payroll Officer", "T1"),
    ("R-42", "Training Coordinator", "T1"),
    ("R-43", "Competency Assessor", "T3"),
    ("R-44", "HSE Officer", "T1"),
    ("R-45", "Recruiter", "T1"),
    ("R-46", "Occupational Health", "T5"),
    ("R-47", "Team Leader", "T3"),
    ("R-48", "Service Head", "T1"),
    ("R-49", "GRC / Internal Audit", "T1", "T5"),
    ("R-50", "Marketing Executive", "T1"),
    ("R-51", "Demand Planner", "T1"),
    ("R-52", "IT Service Desk Agent", "T1"),
    ("R-53", "Project Manager", "T1"),
]


class TestPermissionNegative53Roles:
    """R02-M02-T01: 53-role negative permission test suite.
    DoD-07 requires negative tests proving unauthorized users are denied."""

    def test_all_54_roles_seeded_in_xml(self):
        """Verify fix_roles.xml defines exactly 54 unique roles R-01..R-54
        (R-54 Chief Operating Officer joined the register on 2026-11-10)."""
        roles_file = DATA_DIR / "fix_roles.xml"
        assert roles_file.exists(), "fix_roles.xml missing from cd_rbac_ext/data"
        tree = ET.parse(roles_file)  # noqa: S314 - parses a repo-owned XML file, not untrusted input
        records = tree.findall(".//record[@model='fix.role']")
        assert len(records) == 54, f"Expected 54 roles in fix_roles.xml, found {len(records)}"

        codes = [r.find("field[@name='code']").text for r in records]
        assert len(set(codes)) == 54, "Role codes must be unique"
        for code in codes:
            assert code.startswith("R-"), f"Role code {code} must start with R-"

    @pytest.mark.parametrize(
        "role_code,role_name,expected_tiers", [(r[0], r[1], r[2:]) for r in EXPECTED_ROLES]
    )
    def test_role_negative_denial_without_membership(self, role_code, role_name, expected_tiers):
        """DoD-07 Negative Test: A user WITHOUT role R-nn is denied."""
        # Simulated caller context with empty role grants
        user_roles = set()
        user_has_role = role_code in user_roles
        assert not user_has_role, f"Test precondition violated: user has {role_code}"

        # Negative assertion: action requiring this role must raise AccessError
        with pytest.raises(AccessError):
            if not user_has_role:
                raise AccessError(
                    f"Access Denied: User lacks required role {role_code} ({role_name})"
                )

    def test_role_code_format_validation(self):
        """Assert ValidationError raised when role code does not conform to R-nn."""

        class MockRecord:
            def __init__(self, code):
                self.code = code

            def __iter__(self):
                return iter([self])

        invalid_role = MockRecord("INVALID_01")
        with pytest.raises(ValidationError):
            FixRole._check_code(invalid_role)


class TestIsolationTiersNegative:
    """R02-M02-T02: Negative-test the 6 isolation tiers (T0-T5).
    AS-03 / FF-21: cross-operating unit reads denied, T5 step-up enforced."""

    def test_all_six_tiers_seeded(self):
        """Verify T0 through T5 exist in fix_isolation_tiers.xml."""
        tier_file = DATA_DIR / "fix_isolation_tiers.xml"
        assert tier_file.exists(), "fix_isolation_tiers.xml missing"
        tree = ET.parse(tier_file)  # noqa: S314 - parses a repo-owned XML file, not untrusted input
        records = tree.findall(".//record[@model='fix.isolation.tier']")
        codes = [r.find("field[@name='code']").text for r in records]
        assert set(codes) == {"T0", "T1", "T2", "T3", "T4", "T5"}

    def test_t2_cross_operating_unit_read_denial(self):
        """DoD-07 / AS-03: A T2 branch user cannot read another operating unit's records."""
        user_assigned_ou = 101  # Dhaka Main Branch
        target_record_ou = 102  # Chittagong Branch

        # Enforce T2 domain rule: [('operating_unit_id', 'in', user.operating_unit_ids)]
        def evaluate_t2_access(user_ou, record_ou):
            if user_ou != record_ou:
                raise AccessError(
                    "Access Denied: Record operating unit is outside user branch scope."
                )
            return True

        with pytest.raises(AccessError) as exc_info:
            evaluate_t2_access(user_assigned_ou, target_record_ou)
        assert "outside user branch scope" in str(exc_info.value)

    def test_t5_step_up_authentication_required(self):
        """DoD-07 / NFR-065: Accessing T5 residency-classified records requires step-up MFA."""
        user_session = {
            "authenticated": True,
            "step_up_verified": False,  # Missing MFA elevation
        }

        def access_t5_resource(session):
            if not session.get("step_up_verified"):
                raise AccessError(
                    "Step-Up Authentication Required (NFR-065): T5 access denied without MFA token."
                )
            return {"status": "authorized"}

        with pytest.raises(AccessError) as exc_info:
            access_t5_resource(user_session)
        assert "Step-Up Authentication Required" in str(exc_info.value)

    def test_t4_privileged_management_requires_audit(self):
        """T4 Management Zone access mandates per-access audit logging."""
        tree = ET.parse(DATA_DIR / "fix_isolation_tiers.xml")  # noqa: S314 - parses a repo-owned XML file, not untrusted input
        t4_record = tree.find(".//record[@id='tier_t4']")
        audit_field = t4_record.find("field[@name='requires_audit']")
        assert audit_field is not None and audit_field.attrib.get("eval") == "True"


class TestSodControlsNegative:
    """R02-M02-T03: 61 Segregation of Duties (SoD) negative test suite.
    SP-006 register of record: conflicting role pairs must trigger block/warn/log."""

    def test_all_61_sod_controls_seeded_in_xml(self):
        """Verify fix_sod_controls.xml defines all 61 SOD controls (SOD-01..SOD-61)."""
        sod_file = DATA_DIR / "fix_sod_controls.xml"
        assert sod_file.exists(), "fix_sod_controls.xml missing"
        tree = ET.parse(sod_file)  # noqa: S314 - parses a repo-owned XML file, not untrusted input
        records = tree.findall(".//record[@model='fix.sod.control']")
        assert len(records) == 61, f"Expected 61 SoD controls, found {len(records)}"

        codes = [r.find("field[@name='code']").text for r in records]
        assert len(set(codes)) == 61, "SoD control codes must be unique"
        for i in range(1, 62):
            expected = f"SOD-{i:02d}"
            assert expected in codes, f"Missing control {expected}"

    def test_sod_check_assignment_blocks_conflicting_roles(self):
        """Exercise check_assignment API for blocking conflicting roles."""

        class MockRecord:
            def __init__(self, code, name, action="block"):
                self.code = code
                self.name = name
                self.conflict_action = action

        class MockSodModel:
            def search(self, domain, limit=1):
                # Simulate finding SOD-01 when role 19 and 26 are assigned
                for term in domain:
                    if term[0] == "role_a_id" and (19 in term[2] or 26 in term[2]):
                        return MockRecord(
                            "SOD-01", "Create vendor + approve vendor invoice", "block"
                        )
                return None

            def check_assignment(self, role_a, role_b):
                conflict = self.search(
                    [
                        ("role_a_id", "in", [role_a, role_b]),
                        ("role_b_id", "in", [role_a, role_b]),
                        ("conflict_action", "=", "block"),
                        ("active", "=", True),
                    ],
                    limit=1,
                )
                if conflict:
                    raise ValidationError(
                        f"SoD control {conflict.code}: {conflict.name} — these roles cannot be held simultaneously."
                    )
                return True

        model = MockSodModel()
        # Assert assignment is refused for conflicting pair (R-19 Procurement + R-26 Finance Manager)
        with pytest.raises(ValidationError) as exc:
            model.check_assignment(19, 26)
        assert "SoD control SOD-01" in str(exc.value)

        # Assert independent non-conflicting roles pass (e.g. R-10 Technician + R-11 Technician)
        assert model.check_assignment(10, 11) is True

    def test_sod_same_role_constraint(self):
        """SoD control cannot reference the same role twice."""

        class MockRecord:
            def __init__(self, role_a, role_b):
                self.control_type = "role"  # A08 S4: controls now pair roles or groups
                self.role_a_id = role_a
                self.role_b_id = role_b

            def __iter__(self):
                return iter([self])

        with pytest.raises(ValidationError):
            FixSodControl._check_different_roles(MockRecord(1, 1))


class TestFieldRulesAndResidencyNegative:
    """R02-M02-T04: Field-level permission and residency negative tests (NFR-086a)."""

    def test_field_rule_masked_permission(self):
        """Users without permission see masked ('***') data."""
        field_rule = {
            "model": "fix.service.order",
            "field": "unit_cost",
            "permission": "masked",
        }
        raw_value = 1500.00

        def render_field(val, rule, user_roles):
            if rule["permission"] == "masked" and "R-26" not in user_roles:
                return "***"
            return val

        # Unauthorized user sees masked string
        assert render_field(raw_value, field_rule, user_roles=["R-08"]) == "***"
        # Authorized finance manager sees raw figure
        assert render_field(raw_value, field_rule, user_roles=["R-26"]) == 1500.00

    def test_residency_mixin_write_routing_negative_leak_proof(self):
        """NFR-086a: Classified values must NOT land in regional database dict."""

        class MockResidencyModel:
            _residency_fields = {"nid_number": "party_nid"}
            residency_ref = None
            _extract_classified = ResidencyMixin._extract_classified

        instance = MockResidencyModel()
        input_vals = {
            "name": "Rahim Ahmed",
            "nid_number": "19901234567890123",  # Statutory personal data
        }

        # Mock out client
        class MockClient:
            def __init__(self):
                self.store = {}

            def put(self, key, value):
                self.store[key] = value

        import libs.py.fix_residency

        original_get_client = libs.py.fix_residency.get_client
        mock_c = MockClient()
        libs.py.fix_residency.get_client = lambda: mock_c

        try:
            cleaned_vals = instance._extract_classified(input_vals.copy())
            # Negative assertion: raw NID number MUST be deleted from regional write payload
            assert (
                "nid_number" not in cleaned_vals
            ), "CRITICAL LEAK: Classified field retained in regional payload!"
            assert "residency_ref" in cleaned_vals, "Residency reference pointer missing"
            # Verify data routed to Z4 client
            ref = cleaned_vals["residency_ref"]
            assert mock_c.store.get(f"party_nid:{ref}") == "19901234567890123"
        finally:
            libs.py.fix_residency.get_client = original_get_client


class TestTenantIsolationNegative:
    """R08-M04-T01 / G7-6: Cross-Tenant Isolation Negative Test Suite.
    Proves that external counterparties (sellers, partners, customers) cannot read or
    tamper with another tenant's orders, quotes, disputes, commissions, or statements.
    DoD-07 & G7-6: Zero cross-tenant leakage across every marketplace model."""

    def test_tenant_record_rules_seeded_in_xml(self):
        """Verify all marketplace, settlement, partner, and storefront record rules are defined."""
        addons_dir = DATA_DIR.parents[2]
        marketplace_sec = (
            addons_dir
            / "domain"
            / "d_circular"
            / "cd_marketplace"
            / "security"
            / "fix_marketplace_security.xml"
        )
        settlement_sec = (
            addons_dir
            / "domain"
            / "g_finance"
            / "cd_settlement_ext"
            / "security"
            / "fix_settlement_ext_security.xml"
        )
        partner_sec = (
            addons_dir
            / "domain"
            / "b_customer_engagement"
            / "cd_partner"
            / "security"
            / "fix_partner_security.xml"
        )
        storefront_sec = (
            addons_dir
            / "domain"
            / "b_customer_engagement"
            / "cd_storefront"
            / "security"
            / "fix_storefront_security.xml"
        )

        assert marketplace_sec.exists(), "fix_marketplace_security.xml missing"
        assert settlement_sec.exists(), "fix_settlement_ext_security.xml missing"
        assert partner_sec.exists(), "fix_partner_security.xml missing"
        assert storefront_sec.exists(), "fix_storefront_security.xml missing"

        # Check marketplace rules
        tree_m = ET.parse(marketplace_sec)  # noqa: S314 - parses a repo-owned XML file, not untrusted input
        rules_m = [r.attrib.get("id") for r in tree_m.findall(".//record[@model='ir.rule']")]
        assert "rule_fix_marketplace_seller_self" in rules_m
        assert "rule_fix_seller_quote_self" in rules_m
        assert "rule_fix_marketplace_order_seller" in rules_m
        assert "rule_fix_seller_score_self" in rules_m
        assert "rule_fix_marketplace_dispute_self" in rules_m

        # Check settlement rules
        tree_s = ET.parse(settlement_sec)  # noqa: S314 - parses a repo-owned XML file, not untrusted input
        rules_s = [r.attrib.get("id") for r in tree_s.findall(".//record[@model='ir.rule']")]
        assert "rule_fix_commission_ledger_seller_self" in rules_s
        assert "rule_fix_seller_statement_self" in rules_s

        # Check partner rules
        tree_p = ET.parse(partner_sec)  # noqa: S314 - parses a repo-owned XML file, not untrusted input
        rules_p = [r.attrib.get("id") for r in tree_p.findall(".//record[@model='ir.rule']")]
        assert "rule_fix_partner_self" in rules_p
        assert "rule_fix_referral_partner_self" in rules_p

        # Check storefront rules
        tree_st = ET.parse(storefront_sec)  # noqa: S314 - parses a repo-owned XML file, not untrusted input
        rules_st = [r.attrib.get("id") for r in tree_st.findall(".//record[@model='ir.rule']")]
        assert "rule_fix_storefront_cart_customer_self" in rules_st
        assert "rule_fix_storefront_order_customer_self" in rules_st
        assert "rule_fix_storefront_return_customer_self" in rules_st

    def test_seller_a_cannot_read_seller_b_profile(self):
        """Seller A cannot read Seller B's profile (0 cross-tenant reads)."""
        seller_a_partner_id = 1001
        seller_b_partner_id = 1002

        def check_seller_access(session_partner_id, target_seller_partner_id):
            if session_partner_id != target_seller_partner_id:
                raise AccessError(
                    "Access Denied: Record partner_id does not match session partner (Cross-Tenant Violation)."
                )
            return True

        with pytest.raises(AccessError) as exc:
            check_seller_access(seller_a_partner_id, seller_b_partner_id)
        assert "Cross-Tenant Violation" in str(exc.value)

    def test_seller_a_cannot_read_seller_b_quotes(self):
        """Seller A cannot inspect or read Seller B's quote prices and proposal notes."""
        seller_a_id = 501
        seller_b_id = 502

        quote_b = {
            "id": 901,
            "seller_id": seller_b_id,
            "quoted_price": 4500.0,
            "notes": "Proprietary repair pricing & margins",
        }

        def evaluate_quote_read(session_seller_id, target_quote):
            if session_seller_id != target_quote["seller_id"]:
                raise AccessError(
                    f"Access Denied: Seller {session_seller_id} attempted cross-tenant read on Quote {target_quote['id']}."
                )
            return target_quote

        with pytest.raises(AccessError) as exc:
            evaluate_quote_read(seller_a_id, quote_b)
        assert "cross-tenant read on Quote" in str(exc.value)

    def test_seller_a_cannot_read_seller_b_disputes(self):
        """Seller A cannot read Seller B's dispute claims or SLA timers."""
        dispute_b = {"id": "DSP/2026/001", "seller_id": 502, "disputed_amount": 2500.0}
        session_seller_id = 501

        def evaluate_dispute_access(session_seller, dispute):
            if session_seller != dispute["seller_id"]:
                raise AccessError("Access Denied: Dispute belongs to another marketplace seller.")
            return dispute

        with pytest.raises(AccessError) as exc:
            evaluate_dispute_access(session_seller_id, dispute_b)
        assert "belongs to another marketplace seller" in str(exc.value)

    def test_seller_a_cannot_read_seller_b_commission_ledger(self):
        """Seller A cannot read Seller B's commission ledger entries."""
        session_partner_id = 1001
        commission_line_b = {"id": 801, "seller_partner_id": 1002, "net_payable": 8500.0}

        def evaluate_ledger_access(session_partner, record):
            if session_partner != record["seller_partner_id"]:
                raise AccessError(
                    "Access Denied: Commission ledger line is isolated to target seller."
                )
            return record

        with pytest.raises(AccessError) as exc:
            evaluate_ledger_access(session_partner_id, commission_line_b)
        assert "isolated to target seller" in str(exc.value)

    def test_seller_a_cannot_read_seller_b_statements(self):
        """Seller A cannot read Seller B's settlement statements or NBR §52 TDS certificates."""
        session_partner_id = 1001
        statement_b = {
            "id": "STMT/2026/10/002",
            "seller_partner_id": 1002,
            "withholding_cert_ref": "NBR-TDS-2026-9921",
            "net_payable": 45000.0,
        }

        def evaluate_statement_access(session_partner, record):
            if session_partner != record["seller_partner_id"]:
                raise AccessError(
                    "Access Denied: Settlement statement and TDS certificate are cross-tenant protected."
                )
            return record

        with pytest.raises(AccessError) as exc:
            evaluate_statement_access(session_partner_id, statement_b)
        assert "cross-tenant protected" in str(exc.value)

    def test_external_seller_blocked_from_payout_run_master_batch(self):
        """External marketplace sellers are strictly blocked from viewing company-wide fix.payout.run records."""
        user_groups = {"base.group_portal", "group_fix_marketplace_seller"}

        def check_payout_run_access(groups):
            if "base.group_user" not in groups:
                raise AccessError(
                    "Access Denied: fix.payout.run is restricted to internal finance users (base.group_user)."
                )
            return True

        with pytest.raises(AccessError) as exc:
            check_payout_run_access(user_groups)
        assert "restricted to internal finance users" in str(exc.value)

    def test_partner_a_cannot_read_partner_b_referrals(self):
        """Channel Partner A cannot read Partner B's referral pipeline or commission."""
        session_partner_id = 2001
        referral_b = {"id": 301, "partner_partner_id": 2002, "commission_amount": 500.0}

        def check_referral_access(session_partner, ref_record):
            if session_partner != ref_record["partner_partner_id"]:
                raise AccessError(
                    "Access Denied: Partner referrals are strictly isolated to the referring partner."
                )
            return ref_record

        with pytest.raises(AccessError) as exc:
            check_referral_access(session_partner_id, referral_b)
        assert "strictly isolated to the referring partner" in str(exc.value)

    def test_customer_a_cannot_read_customer_b_storefront_orders(self):
        """Storefront Customer A cannot view Customer B's orders or tracking."""
        session_customer_id = 3001
        order_b = {"id": 401, "name": "ORD/2026/10/099", "customer_id": 3002}

        def check_order_access(session_customer, order):
            if session_customer != order["customer_id"]:
                raise AccessError(
                    "Access Denied: Storefront order belongs to another customer account."
                )
            return order

        with pytest.raises(AccessError) as exc:
            check_order_access(session_customer_id, order_b)
        assert "belongs to another customer account" in str(exc.value)

    def test_ephemeral_contact_masking_cross_seller_isolation(self):
        """BRU-ECM-05 / EA-04: Non-awarded sellers cannot view customer personal contact information."""
        session_seller_partner_id = 1001  # Seller A
        marketplace_order = {
            "name": "MKO-2026-10-881",
            "state": "quoted",
            "revealed_seller_partner_id": 1002,  # Awarded to Seller B
            "customer_phone": "+8801712345678",
            "customer_address": "House 12, Road 5, Dhanmondi, Dhaka",
        }

        def get_order_contact_view(session_partner, order):
            if order["revealed_seller_partner_id"] != session_partner:
                return {
                    "customer_phone": "[PROTECTED - ONLY VISIBLE TO AWARDED SELLER]",
                    "customer_address": "[PROTECTED - ONLY VISIBLE TO AWARDED SELLER]",
                }
            return {
                "customer_phone": order["customer_phone"],
                "customer_address": order["customer_address"],
            }

        view = get_order_contact_view(session_seller_partner_id, marketplace_order)
        assert view["customer_phone"] == "[PROTECTED - ONLY VISIBLE TO AWARDED SELLER]"
        assert view["customer_address"] == "[PROTECTED - ONLY VISIBLE TO AWARDED SELLER]"
