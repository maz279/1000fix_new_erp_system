import os

updates = [
    (
        "m21.py",
        '"fix.employment.contract": {\n        "order": "employee_id, joining_date desc",\n        "limit": 400,\n        "actions": set(),\n    }',
        '"fix.employment.contract": {\n        "order": "employee_id, joining_date desc",\n        "limit": 400,\n        "actions": {"action_activate", "action_terminate", "action_request_legal_signoff", "action_approve_legal_signoff", "action_generate_contract_document"},\n    }',
    ),
    (
        "m22.py",
        '"fix.certification": {"order": "expires_on", "limit": 500, "actions": set()},\n    "fix.training.course": {"order": "code", "limit": 200, "actions": set()},\n    "fix.training.enrollment": {\n        "order": "id desc",\n        "limit": 500,\n        "actions": set(),\n    }',
        '"fix.certification": {"order": "expires_on", "limit": 500, "actions": {"action_grant", "action_mark_expired"}},\n    "fix.training.course": {"order": "code", "limit": 200, "actions": {"action_enroll"}},\n    "fix.training.enrollment": {\n        "order": "id desc",\n        "limit": 500,\n        "actions": {"action_pass"},\n    }',
    ),
    (
        "m55.py",
        '"fix.biometric.device": {\n        "order": "name",\n        "limit": 100,\n        "actions": set(),\n    },\n    "fix.shift.template": {"order": "name", "limit": 100, "actions": set()},\n    "fix.roster.slot": {\n        "order": "date desc, employee_id",\n        "limit": 500,\n        "actions": set(),\n    },\n    "fix.leave.request": {\n        "order": "date_from desc, id desc",\n        "limit": 300,\n        "actions": set(),\n    }',
        '"fix.biometric.device": {\n        "order": "name",\n        "limit": 100,\n        "actions": {"action_ingest_punch"},\n    },\n    "fix.shift.template": {"order": "name", "limit": 100, "actions": set()},\n    "fix.roster.slot": {\n        "order": "date desc, employee_id",\n        "limit": 500,\n        "actions": set(),\n    },\n    "fix.leave.request": {\n        "order": "date_from desc, id desc",\n        "limit": 300,\n        "actions": {"action_approve"},\n    }',
    ),
    (
        "m56.py",
        '"fix.payslip": {\n        "order": "period_id desc, employee_id",\n        "limit": 500,\n        "actions": set(),\n    }',
        '"fix.payslip": {\n        "order": "period_id desc, employee_id",\n        "limit": 500,\n        "actions": {"action_compute_separation", "action_compute_retrenchment"},\n    }',
    ),
    (
        "m57.py",
        '"fix.performance.scorecard": {"order": "period desc, employee_id", "limit": 400, "actions": set()}',
        '"fix.performance.scorecard": {"order": "period desc, employee_id", "limit": 400, "actions": {"action_publish"}}',
    ),
    (
        "m57.py",
        '"fix.incentive.run": {\n        "order": "period desc, id desc",\n        "limit": 100,\n        "actions": set(),\n    }',
        '"fix.incentive.run": {\n        "order": "period desc, id desc",\n        "limit": 100,\n        "actions": {"action_compute", "action_apply"},\n    }',
    ),
    (
        "m58.py",
        '"fix.job.requisition": {\n        "order": "id desc",\n        "limit": 300,\n        "actions": set(),\n    },\n    "fix.candidate": {"order": "id desc", "limit": 500, "actions": set()}',
        '"fix.job.requisition": {\n        "order": "id desc",\n        "limit": 300,\n        "actions": {"action_open", "action_hired"},\n    },\n    "fix.candidate": {"order": "id desc", "limit": 500, "actions": {"action_screen", "action_interview", "action_offer", "action_hire"}}',
    ),
    (
        "m58.py",
        '"fix.onboarding.plan": {"order": "joined_date desc, id desc", "limit": 300, "actions": set()}',
        '"fix.onboarding.plan": {"order": "joined_date desc, id desc", "limit": 300, "actions": {"action_start", "action_complete"}}',
    ),
    (
        "m59.py",
        '"fix.statutory.accident.register": {"order": "accident_date desc", "limit": 300, "actions": set()}',
        '"fix.statutory.accident.register": {"order": "accident_date desc", "limit": 300, "actions": {"action_notify_dife"}}',
    ),
    (
        "m59.py",
        '"fix.safety.committee": {"order": "formation_date desc", "limit": 100, "actions": set()},\n    "fix.hse.health": {"order": "record_date desc, id desc", "limit": 300, "actions": set()},\n    "fix.safety.inspection": {"order": "id desc", "limit": 400, "actions": set()}',
        '"fix.safety.committee": {"order": "formation_date desc", "limit": 100, "actions": {"action_record_meeting"}},\n    "fix.hse.health": {"order": "record_date desc, id desc", "limit": 300, "actions": {"action_close"}},\n    "fix.safety.inspection": {"order": "id desc", "limit": 400, "actions": {"action_complete"}}',
    ),
    (
        "m59.py",
        '"fix.ppe.register": {"order": "name", "limit": 500, "actions": set()}',
        '"fix.ppe.register": {"order": "name", "limit": 500, "actions": {"check_replenishment"}}',
    ),
]

for fname, target, repl in updates:
    p = os.path.join("addons", "platform", "cd_p03_portal", "controllers", "a09", fname)
    with open(p, encoding="utf-8") as f:
        content = f.read()

    norm_content = content.replace("\r\n", "\n")
    norm_target = target.replace("\r\n", "\n")
    norm_repl = repl.replace("\r\n", "\n")

    if norm_target in norm_content:
        norm_content = norm_content.replace(norm_target, norm_repl, 1)
        with open(p, "w", encoding="utf-8") as f:
            f.write(norm_content)
        print(f"Updated {fname}")
    else:
        # Check if already updated
        if norm_repl in norm_content:
            print(f"Already updated {fname}")
        else:
            print(f"FAILED to match target in {fname}")
