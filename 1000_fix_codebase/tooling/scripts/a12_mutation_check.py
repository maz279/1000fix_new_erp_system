"""A12 P2 mutation check: re-introduce a defect, require the suite to go red.

One guard per finding family is flipped, the owning suite runs, and the
file is restored whatever happens (try/finally). A mutation that leaves
the suite GREEN means the suite does not actually pin the fix.
Run:  FIX_TEST_DB=fix_test_a12mut python tooling/scripts/a12_mutation_check.py [ids...]
"""

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")

MUTATIONS = [
    {
        "id": "X3",
        "label": "two-person DOFA ruling",
        "file": "addons/platform/cd_entity_config/models/fix_dofa_threshold.py",
        "old": "            if not self.env.su:\n                acting = self.env.user",
        "new": "            if False:\n                acting = self.env.user",
        "test": "addons/platform/cd_entity_config/tests/test_a12_m30_controls.py",
    },
    {
        "id": "X1",
        "label": "requester/beneficiary refusal",
        "file": "addons/platform/cd_rbac_ext/models/fix_access_ops.py",
        "old": "    def _assert_decider(self, rec):\n        if not self._approver_authority(rec):",
        "new": "    def _assert_decider(self, rec):\n        if False:",
        "test": "addons/platform/cd_rbac_ext/tests/test_a12_m29_controls.py",
    },
    {
        "id": "P1-4",
        "label": "checkout gateway gate",
        "file": "addons/domain/b_customer_engagement/cd_storefront/models/fix_storefront.py",
        "old": '        if payment_rail and payment_rail != "cod":',
        "new": '        if False and payment_rail and payment_rail != "cod":',
        "test": "addons/domain/b_customer_engagement/cd_storefront/tests/test_a12_checkout_gateway_gate.py",
    },
    {
        "id": "M28-1",
        "label": "webhook host allow-list",
        "file": "addons/domain/i_governance/cd_itsm/models/fix_integration.py",
        "old": "    def _host_allowed(host, allowlist):\n        if not host:\n            return False",
        "new": "    def _host_allowed(host, allowlist):\n        if not host:\n            return False\n        return True",
        "test": "addons/domain/i_governance/cd_itsm/tests/test_a12_m28_controls.py",
    },
    {
        "id": "P1-2",
        "label": "MDM steward routed approval",
        "file": "addons/platform/cd_mdm_core/models/fix_mdm_steward_approval.py",
        "old": "        if not self._approval_task() and not self.env.su:",
        "new": "        if False:",
        "test": "addons/platform/cd_mdm_core/tests/test_a12_m64_controls.py",
    },
    {
        "id": "P2-flag",
        "label": "SLA escalation kill switch",
        "file": "addons/domain/i_governance/cd_itsm/models/fix_itsm.py",
        "old": '        if self.env["fix.feature.flag"].is_disabled("itsm.sla_auto_escalate"):',
        "new": '        if False and self.env["fix.feature.flag"].is_disabled("itsm.sla_auto_escalate"):',
        "test": "addons/domain/i_governance/cd_itsm/tests/test_a12_flag_kill_switch.py",
    },
]


def run_suite(test_path):
    env = dict(os.environ)
    env["FIX_TEST_DB"] = os.environ.get("MUT_DB", "fix_test_a12mut")
    env["PYTHONUTF8"] = "1"
    r = subprocess.run(
        [
            PY,
            "-m",
            "pytest",
            test_path,
            "-p",
            "no:cacheprovider",
            "--no-header",
            "-W",
            "ignore",
            "-q",
            "--tb=no",
        ],
        env=env,
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=420,
    )
    tail = (r.stdout or "").strip().split("\n")[-1]
    return r.returncode, tail


def main(argv):
    wanted = set(argv[1:]) or None
    reds = greens = 0
    for m in MUTATIONS:
        if wanted and m["id"] not in wanted:
            continue
        path = os.path.join(ROOT, m["file"])
        with open(path, encoding="utf-8") as fh:
            src = fh.read()
        if src.count(m["old"]) != 1:
            print("SKIP  %s (%s): anchor not unique/found" % (m["id"], m["label"]))
            continue
        with open(path + ".bak", "w", encoding="utf-8", newline="") as fh:
            fh.write(src)
        try:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(src.replace(m["old"], m["new"]))
            rc, tail = run_suite(os.path.join(ROOT, m["test"]))
        finally:
            shutil.copyfile(path + ".bak", path)
            os.remove(path + ".bak")
        went_red = rc != 0
        reds += went_red
        greens += not went_red
        print("%s  %-6s %s  ->  %s" % ("RED  " if went_red else "GREEN", m["id"], m["label"], tail))
    print("mutations red: %d, green: %d" % (reds, greens))
    return 0 if greens == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
