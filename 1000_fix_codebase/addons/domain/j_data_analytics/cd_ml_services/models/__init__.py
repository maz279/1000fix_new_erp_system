# cd_ml_services models.
# ruff: noqa: I001
# Odoo load order matters: fix_ml_m48_gate _inherits fix.ml.model, which
# fix_ml_services defines, so it is imported last (A07 ERP audit 2026-11-20 M48-02).
from . import fix_ml_assurance, fix_ml_governance, fix_ml_services, fix_ml_validation
from . import fix_ml_events, fix_ml_m48_gate
