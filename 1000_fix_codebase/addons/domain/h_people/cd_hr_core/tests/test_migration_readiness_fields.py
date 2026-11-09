# EMP-MIG-RPT-001 R7 — the 2026-11-09 employee-migration capability audit
# measured `sex` and `passport_no` absent from the live hr.employee master,
# and `marital` required with no unrecorded value (a 504-row legacy extract
# carries no marital data). These tests pin the migration-readiness slice.
import pytest


def test_sex_field_present_with_bd_categories(odoo_env):
    emp = odoo_env["hr.employee"]
    values = {value for value, _label in emp._fields["sex"].selection}
    assert values.issuperset({"male", "female", "third_gender", "unspecified"})
    fresh = emp.create({"name": "Default Sex Check", "employee_code": "E-SEXP-05"})
    assert fresh.sex == "unspecified"


def test_passport_no_field_present(odoo_env):
    emp = odoo_env["hr.employee"].create(
        {"name": "Rashedul Karim", "employee_code": "E-SEXP-01", "passport_no": "BR0934567"}
    )
    assert emp.passport_no == "BR0934567"


def test_marital_accepts_unspecified_migration_default(odoo_env):
    # The real-employee load (504 rows) has no marital data: create must
    # succeed with the honest 'unspecified' value, not a fabricated status.
    emp = odoo_env["hr.employee"].create(
        {"name": "Shirin Sultana", "employee_code": "E-SEXP-02", "marital": "unspecified"}
    )
    assert emp.marital == "unspecified"


def test_marital_unspecified_is_replaced_by_enrichment(odoo_env):
    emp = odoo_env["hr.employee"].create(
        {"name": "Kamrul Hasan", "employee_code": "E-SEXP-03", "marital": "unspecified"}
    )
    emp.write({"marital": "married"})
    assert emp.marital == "married"


def test_invalid_sex_value_rejected(odoo_env):
    with pytest.raises(ValueError):
        odoo_env["hr.employee"].create(
            {"name": "Bad Value", "employee_code": "E-SEXP-04", "sex": "alien"}
        )
