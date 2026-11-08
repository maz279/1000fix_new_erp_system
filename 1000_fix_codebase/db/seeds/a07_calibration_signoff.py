"""A07 decision B9 (8 Nov 2026): calibration by role, accepted by a second person.

Run in `odoo-bin shell`. Turns on the two M45 switches the business chose:
- cd_equipment_register.calibration_requires_role: only a Calibration Technician
  or a Quality Manager records a calibration;
- cd_equipment_register.usage_decision_required: a passing calibration certifies
  the instrument only once a Quality Manager other than its recorder accepts it.

Every passing calibration still awaiting acceptance is then put in the Quality
Managers' to-do list, so no instrument silently stops being certified. It refuses
to switch on while no Quality Manager or no Calibration Technician is appointed.

Set FIX_A07_COMMIT=1 to keep the result; otherwise it rolls back and reports.
"""

# ruff: noqa: F821  (odoo-bin shell provides env)
import os

ROLES = (
    "cd_equipment_register.group_quality_manager",
    "cd_equipment_register.group_calibration_technician",
)
Params = env["ir.config_parameter"].sudo()
for xmlid in ROLES:
    holders = env.ref(xmlid).sudo().all_user_ids.filtered(lambda u: u.active and not u.share)
    print("a07-calibration-signoff:", xmlid, "holders:", len(holders))
    if not holders:
        raise SystemExit(f"appoint {xmlid} before switching on")

for key in (
    "cd_equipment_register.calibration_requires_role",
    "cd_equipment_register.usage_decision_required",
):
    print(f"  {key}: {Params.get_param(key)!r} -> True")
    Params.set_param(key, "True")

Calibration = env["fix.calibration"]
asked = Calibration.action_ask_pending_decisions()
todos = (
    env["mail.activity"]
    .sudo()
    .search_count(
        [("res_model", "=", "fix.calibration"), ("summary", "=like", "Usage decision needed%")]
    )
)
waiting = Calibration.sudo().search(
    [("decision_state", "=", "pending"), ("result", "in", ["pass", "adjusted"])]
)
print("  passing calibrations awaiting acceptance:", asked, "| to-dos:", todos)
print("  instruments now waiting:", sorted(set(waiting.mapped("equipment_id.name"))))
if os.environ.get("FIX_A07_COMMIT") == "1":
    env.cr.commit()
    print("committed")
else:
    env.cr.rollback()
    print("rolled back (set FIX_A07_COMMIT=1 to keep)")
