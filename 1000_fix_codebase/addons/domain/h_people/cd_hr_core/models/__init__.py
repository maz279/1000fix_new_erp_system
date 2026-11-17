# cd_hr_core models.
# ruff: noqa: I001
# fix_people_approval first: the A09 models inherit its mixin; the M21 shared
# helpers (fix_hr_controls_common) before the models that use their mixin.
from . import fix_people_approval, fix_hr_controls_common, fix_hr_settings
from . import fix_hr_core, fix_hr_ops, res_users_people
from . import fix_people_interfaces, fix_leave_controls
from . import fix_hr_contract_controls, fix_hr_movement_controls, fix_hr_disciplinary

# the identity residency before the master controls (they import its IDENTITY)
from . import fix_hr_exit_controls, fix_hr_document_controls, fix_hr_identity_residency
from . import fix_hr_master_controls, fix_hr_exit_lifecycles, fix_hr_cleanup_report
from . import fix_hr_cost_centre

# M21 capture audit 2026-11-17: job architecture, privacy-notice acknowledgement,
# exit interview (extends hr.employee, fix.org.position and fix.hr.exit: last)
from . import fix_hr_capture
