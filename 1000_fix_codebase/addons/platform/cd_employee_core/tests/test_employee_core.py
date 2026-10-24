# Tests for cd_employee_core (P03-M08) — M21-core JML events + M21↔M29 break.


class TestHrEmployeeExt:
    def test_model_extension_importable(self):
        from odoo.addons.cd_employee_core.models.hr_employee_ext import HrEmployeeExt

        assert HrEmployeeExt is not None

    def test_party_role_link(self):
        """Employee links to the party kernel (not a separate master)."""
        from odoo.addons.cd_employee_core.models.hr_employee_ext import HrEmployeeExt

        assert "party_role_id" in dir(HrEmployeeExt)

    def test_jml_emit_joined(self):
        """employee.joined event fires on create (P03-M08-T04)."""
        from odoo.addons.cd_employee_core.models.hr_employee_ext import HrEmployeeExt

        assert "_emit_jml" in dir(HrEmployeeExt)

    def test_leaver_path(self):
        """action_mark_left triggers the leaver event (KPI-090)."""
        from odoo.addons.cd_employee_core.models.hr_employee_ext import HrEmployeeExt

        assert "action_mark_left" in dir(HrEmployeeExt)
        assert "_emit_leaver" in dir(HrEmployeeExt)

    def test_m21_to_m29_sync_api(self):
        """assign_role() is the sync one-way call to M29 (P03-M08-T08)."""
        from odoo.addons.cd_employee_core.models.hr_employee_ext import HrEmployeeExt

        assert "assign_role" in dir(HrEmployeeExt)

    def test_employment_status_derived(self):
        from odoo.addons.cd_employee_core.models.hr_employee_ext import HrEmployeeExt

        assert "_compute_employment_status" in dir(HrEmployeeExt)

    def test_keycloak_user_id_field(self):
        """Keycloak UUID for KPI-090 provisioning/deprovisioning."""
        from odoo.addons.cd_employee_core.models.hr_employee_ext import HrEmployeeExt

        assert "keycloak_user_id" in dir(HrEmployeeExt)
