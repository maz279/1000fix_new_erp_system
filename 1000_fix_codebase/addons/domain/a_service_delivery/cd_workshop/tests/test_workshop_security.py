# Security & Negative Access Tests for cd_workshop (M31).
import pytest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]


class TestWorkshopSecurity:
    def test_security_xml_declares_workshop_groups(self):
        """Verify workshop security groups and multi-company rules in security XML."""
        xml = (MODULE / "security" / "fix_workshop_security.xml").read_text(encoding="utf-8")
        assert "group_fix_workshop_user" in xml
        assert "group_fix_workshop_manager" in xml
        assert "rule_fix_workshop_company" in xml
        assert "rule_fix_workshop_bench_company" in xml
        assert "rule_fix_workshop_job_company" in xml

    def test_ir_model_access_matrix(self):
        """Verify access control list (ACL) denies delete to standard users."""
        csv_text = (MODULE / "security" / "ir.model.access.csv").read_text(encoding="utf-8")
        lines = [line.strip().split(",") for line in csv_text.strip().splitlines() if line.strip()]
        header = lines[0]
        rows = {row[0]: dict(zip(header, row)) for row in lines[1:]}

        # Technician / Bench operator cannot delete jobs or workshops
        assert rows["access_fix_workshop_job_user"]["perm_unlink"] == "0"
        assert rows["access_fix_workshop_user"]["perm_unlink"] == "0"
        assert rows["access_fix_workshop_user"]["perm_create"] == "0"
        assert rows["access_fix_workshop_user"]["perm_write"] == "0"

        # Depot Manager can create and write
        assert rows["access_fix_workshop_mgr"]["perm_create"] == "1"
        assert rows["access_fix_workshop_mgr"]["perm_write"] == "1"
        assert rows["access_fix_workshop_job_mgr"]["perm_unlink"] == "1"

        # Base internal user has strictly read-only access (no write, create, or unlink)
        assert rows["access_fix_workshop_internal_base"]["perm_read"] == "1"
        assert rows["access_fix_workshop_internal_base"]["perm_write"] == "0"
        assert rows["access_fix_workshop_internal_base"]["perm_create"] == "0"
        assert rows["access_fix_workshop_internal_base"]["perm_unlink"] == "0"
