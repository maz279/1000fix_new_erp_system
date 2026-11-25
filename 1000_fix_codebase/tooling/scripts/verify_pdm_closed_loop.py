"""1000FiX ERP v2.0 - Milestone R09-M03 Task T02.
Verify predictive-maintenance closed loop:
Sensor Telemetry Degradation -> Failure Prediction -> Preventive Work Order
-> M02 Dispatch Scoring -> Field Resolution -> Completion Telemetry & Health Restoration.

GV-009: every stage status is MEASURED in this run or reported UNMEASURED with the
reason - nothing is hard-coded. What is observable locally, without creating
records on the running Odoo:

- stage 2: whether services/ml-gateway exposes a predictive-maintenance inference
  entry point at all (introspection of the imported module);
- stage 3: whether fix.predictive.maintenance.action_create_preventive_wo raises a
  preventive request (a fix.iot.action with preventive_request=True) and the M63 apply
  method fix.iot.action.action_approve publishes `predictive_maintenance.wo_created`
  for it (AST of the addon source; A07 ERP audit M48-03 moved the publish to the
  approval), and whether any consumer in addons/ or services/ turns that event into
  a work order (source scan);
- stage 4: M02 dispatch ranking, executed in-process through ml_gateway.rank_technicians
  on fixture candidates, checked against the certification gate and feature dominance.

Stages 1, 5 and 6 need the Odoo runtime, a field technician and the live IoT pipeline;
they are UNMEASURED here, so the overall verdict can never be PASS from a local run.
Exit code: 0 PASS, 1 FAIL, 2 INCOMPLETE.
"""

import ast
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add services and addons to path for pure Python model execution
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "services" / "ml-gateway" / "src"))

try:
    import ml_gateway
except ImportError:
    ml_gateway = None

EVIDENCE_PATH = (
    REPO_ROOT / "docs" / "traceability" / "evidence" / "r09-m03-pdm-closed-loop-evidence.json"
)
PDM_MODEL_FILE = (
    REPO_ROOT
    / "addons"
    / "domain"
    / "j_data_analytics"
    / "cd_stream_registry"
    / "models"
    / "fix_stream_registry.py"
)
# A07 ERP audit (2026-11-20) M48-03: the request is raised on the prediction, and
# the work-order event is published when the M63 approver approves the request.
APPROVAL_MODEL_FILE = PDM_MODEL_FILE.with_name("fix_iot_ops.py")
CONSUMER_SCAN_ROOTS = [REPO_ROOT / "addons", REPO_ROOT / "services"]
CONSUMER_SCAN_SUFFIXES = {".py", ".js", ".ts", ".go", ".xml"}
CONSUMER_SCAN_SKIP_DIRS = {"node_modules", "__pycache__", "tests", "test", ".venv", "dist"}

WO_EVENT = "predictive_maintenance.wo_created"
PDM_MODEL = "fix.predictive.maintenance"
PDM_ACTION = "action_create_preventive_wo"
APPROVAL_MODEL = "fix.iot.action"
APPROVAL_ACTION = "action_approve"
REQUEST_FLAG = "preventive_request"
PDM_NAME_TOKENS = {"predict", "prediction", "failure", "maintenance", "pdm", "rul", "anomaly"}

EXIT_CODES = {"PASS": 0, "FAIL": 1, "INCOMPLETE": 2}

STAGE_ORDER = [
    "1_sensor_degradation_telemetry",
    "2_ml_failure_prediction",
    "3_preventive_wo_creation",
    "4_m02_dispatch_scoring_ranking",
    "5_field_execution_resolution",
    "6_post_maintenance_telemetry_restoration",
]

# Fixture INPUTS for the in-process M02 ranking (stage 4). The expected outcome is
# not hard-coded: it is derived from the certification gate and feature dominance.
DISPATCH_FIXTURE = [
    {
        "technician_id": "TECH-DH-014",
        "certification_active": True,
        "historical_ftf": 0.95,
        "historical_sla": 0.98,
        "workload_today": 1,
    },
    {
        "technician_id": "TECH-DH-022",
        "certification_active": True,
        "historical_ftf": 0.84,
        "historical_sla": 0.89,
        "workload_today": 3,
    },
    {
        "technician_id": "TECH-DH-039",
        "certification_active": False,
        "historical_ftf": 0.92,
        "historical_sla": 0.95,
        "workload_today": 0,
    },
]
DISPATCH_CONTEXT = {
    "device_type": "industrial_bga",
    "brand": "Hakko_Den-On",
    "branch": "OU-DHK-01",
    "priority": "urgent",
}


def overall_verdict(statuses: list[str]) -> str:
    if not statuses:
        return "INCOMPLETE"
    if "FAIL" in statuses:
        return "FAIL"
    if any(s != "PASS" for s in statuses):
        return "INCOMPLETE"
    return "PASS"


def _dominates(a: dict, b: dict) -> bool:
    """True if certified `a` is at least as good as certified `b` on every feature and
    strictly better on one (certified vs uncertified is the separate gate check)."""
    if not (a["certification_active"] and b["certification_active"]):
        return False
    ge = (
        a["historical_ftf"] >= b["historical_ftf"]
        and a["historical_sla"] >= b["historical_sla"]
        and a["workload_today"] <= b["workload_today"]
    )
    strict = (
        a["historical_ftf"] > b["historical_ftf"]
        or a["historical_sla"] > b["historical_sla"]
        or a["workload_today"] < b["workload_today"]
    )
    return ge and strict


class PredictiveMaintenanceClosedLoopVerifier:
    def __init__(self):
        self.evidence_path = EVIDENCE_PATH
        self.audit_log = []
        self.stages: dict[str, dict] = {}

    def log_step(self, stage: str, details: dict):
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "stage": stage,
            "details": details,
        }
        self.audit_log.append(entry)
        print(f"[{entry['timestamp']}] [STAGE: {stage}] {details.get('summary', '')}")

    def _record(self, stage: str, status: str, summary: str, **observed) -> None:
        self.stages[stage] = {"stage": stage, "status": status, "summary": summary, **observed}
        self.log_step(stage, {"summary": f"[{status}] {summary}", **observed})

    # ------------------------------------------------------------------
    # Stage 1: telemetry ingestion (Odoo runtime only)
    # ------------------------------------------------------------------
    def stage_telemetry(self) -> None:
        self._record(
            STAGE_ORDER[0],
            "UNMEASURED",
            "Telemetry ingestion runs through fix.iot.telemetry / "
            "fix.iot.device.action_telemetry_received inside the Odoo runtime; this verifier "
            "creates no records on the running Odoo and there is no in-process ingestion path.",
        )

    # ------------------------------------------------------------------
    # Stage 2: M48 failure-prediction inference entry point
    # ------------------------------------------------------------------
    def stage_prediction(self) -> None:
        stage = STAGE_ORDER[1]
        if ml_gateway is None:
            self._record(stage, "FAIL", "services/ml-gateway (ml_gateway) could not be imported.")
            return
        public = sorted(
            name
            for name in dir(ml_gateway)
            if not name.startswith("_")
            and callable(getattr(ml_gateway, name))
            and getattr(getattr(ml_gateway, name), "__module__", None) == ml_gateway.__name__
        )
        candidates = [
            name
            for name in public
            if PDM_NAME_TOKENS & {tok.lower() for tok in name.split("_")}
            or "Predict" in name
            or "Failure" in name
        ]
        if not candidates:
            self._record(
                stage,
                "FAIL",
                "services/ml-gateway exposes no predictive-maintenance / failure-prediction "
                "inference entry point; no failure prediction can be produced.",
                ml_gateway_public_callables=public,
            )
            return
        self._record(
            stage,
            "UNMEASURED",
            "Possible PdM inference entry point(s) found but this verifier has no invocation "
            "contract for them - extend the verifier to call and check them.",
            candidates=candidates,
        )

    # ------------------------------------------------------------------
    # Stage 3: preventive work-order trigger (static wiring + consumer scan)
    # ------------------------------------------------------------------
    @staticmethod
    def _method(path: Path, model: str, method: str) -> tuple[ast.FunctionDef | None, str]:
        """The AST of `model.method` in `path`, or None and why it was not found."""
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as exc:
            return None, f"cannot parse {path.name}: {exc}"
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            names = {
                stmt.targets[0].id: stmt.value.value
                for stmt in node.body
                if isinstance(stmt, ast.Assign)
                and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Name)
                and isinstance(stmt.value, ast.Constant)
            }
            if names.get("_name") != model:
                continue
            for fn in node.body:
                if isinstance(fn, ast.FunctionDef) and fn.name == method:
                    return fn, ""
            return None, f"{model} has no {method} method"
        return None, f"model {model} not found in {path.name}"

    @staticmethod
    def _publishes_event(node: ast.AST) -> bool:
        """A call `publish(..., WO_EVENT, ...)` (the event name as a literal argument)."""
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Call):
                continue
            func = sub.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            if "publish" not in name:
                continue
            if any(isinstance(a, ast.Constant) and a.value == WO_EVENT for a in sub.args):
                return True
        return False

    def _publisher_wired(self) -> tuple[bool, str]:
        # 1. the prediction raises a preventive request (an action marked as one)
        request, why = self._method(PDM_MODEL_FILE, PDM_MODEL, PDM_ACTION)
        if request is None:
            return False, why
        marks_request = any(
            isinstance(sub, ast.Dict)
            and any(
                isinstance(k, ast.Constant)
                and k.value == REQUEST_FLAG
                and isinstance(v, ast.Constant)
                and v.value is True
                for k, v in zip(sub.keys, sub.values, strict=False)
            )
            for sub in ast.walk(request)
        )
        if not marks_request:
            return False, f"{PDM_MODEL}.{PDM_ACTION} does not raise a {REQUEST_FLAG} action"
        # 2. approving that request publishes the work-order event, under the flag
        approve, why = self._method(APPROVAL_MODEL_FILE, APPROVAL_MODEL, APPROVAL_ACTION)
        if approve is None:
            return False, why
        guarded = any(
            isinstance(sub, ast.If)
            and REQUEST_FLAG in ast.unparse(sub.test)
            and any(self._publishes_event(stmt) for stmt in sub.body)
            for sub in ast.walk(approve)
        )
        if not guarded:
            return False, (
                f"{APPROVAL_MODEL}.{APPROVAL_ACTION} does not publish {WO_EVENT} for an "
                f"approved {REQUEST_FLAG}"
            )
        return True, (
            f"{PDM_MODEL}.{PDM_ACTION} raises a {REQUEST_FLAG} action and "
            f"{APPROVAL_MODEL}.{APPROVAL_ACTION} publishes {WO_EVENT} when it is approved"
        )

    def _event_consumers(self) -> list[str]:
        found: list[str] = []
        publishers = {PDM_MODEL_FILE.resolve(), APPROVAL_MODEL_FILE.resolve()}
        for root in CONSUMER_SCAN_ROOTS:
            if not root.is_dir():
                continue
            for path in root.rglob("*"):
                if path.suffix not in CONSUMER_SCAN_SUFFIXES or not path.is_file():
                    continue
                if CONSUMER_SCAN_SKIP_DIRS & set(path.relative_to(root).parts[:-1]):
                    continue
                if path.resolve() in publishers:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if WO_EVENT in text:
                    found.append(str(path.relative_to(REPO_ROOT)).replace("\\", "/"))
        return sorted(found)

    def stage_work_order(self) -> None:
        stage = STAGE_ORDER[2]
        wired, wiring_detail = self._publisher_wired()
        consumers = self._event_consumers()
        problems = []
        if not wired:
            problems.append(wiring_detail)
        if not consumers:
            problems.append(
                f"no consumer of {WO_EVENT} in addons/ or services/ - the action only sets "
                "work_order_created=True and publishes the event; no preventive work order "
                "record is created"
            )
        if problems:
            self._record(
                stage,
                "FAIL",
                "; ".join(problems),
                publisher_wiring=wiring_detail,
                consumers=consumers,
            )
            return
        self._record(
            stage,
            "UNMEASURED",
            "Publisher and consumer wiring present in source; creating the work order needs the "
            "Odoo runtime (not exercised - no records are created on the running Odoo).",
            publisher_wiring=wiring_detail,
            consumers=consumers,
        )

    # ------------------------------------------------------------------
    # Stage 4: M02 dispatch ranking (in-process)
    # ------------------------------------------------------------------
    def stage_dispatch(self) -> dict | None:
        stage = STAGE_ORDER[3]
        if ml_gateway is None:
            self._record(stage, "FAIL", "services/ml-gateway (ml_gateway) could not be imported.")
            return None
        try:
            features = [
                ml_gateway.DispatchFeatures(**DISPATCH_CONTEXT, **cand) for cand in DISPATCH_FIXTURE
            ]
            ranked = list(ml_gateway.rank_technicians(features))
        except Exception as exc:  # product code failure is a FAIL, not a crash
            self._record(stage, "FAIL", f"rank_technicians raised {type(exc).__name__}: {exc}")
            return None

        by_id = {c["technician_id"]: c for c in DISPATCH_FIXTURE}
        order = [s.technician_id for s in ranked]
        scores = {s.technician_id: s.score for s in ranked}
        problems: list[str] = []
        if sorted(order) != sorted(by_id):
            problems.append(f"ranking returned {order}, expected all of {sorted(by_id)}")
        else:
            if any(ranked[i].score < ranked[i + 1].score for i in range(len(ranked) - 1)):
                problems.append("ranking is not ordered by descending score")
            position = {tid: i for i, tid in enumerate(order)}
            certified = [t for t, c in by_id.items() if c["certification_active"]]
            uncertified = [t for t, c in by_id.items() if not c["certification_active"]]
            for u in uncertified:
                if scores[u] >= 0:
                    problems.append(f"uncertified {u} has non-negative score {scores[u]}")
                for c in certified:
                    if position[u] < position[c]:
                        problems.append(f"uncertified {u} ranked above certified {c}")
            for a in by_id:
                for b in by_id:
                    if a != b and _dominates(by_id[a], by_id[b]) and position[a] > position[b]:
                        problems.append(f"{a} dominates {b} on every feature but ranks below it")
            if order and not by_id[order[0]]["certification_active"]:
                problems.append(f"top-ranked {order[0]} is not certified")

        top = ranked[0] if ranked else None
        dispatch = {
            "selected_technician": top.technician_id if top else None,
            "dispatch_score": top.score if top else None,
            "score_factors": top.factors if top else None,
            "rankings": [{"tech": s.technician_id, "score": s.score} for s in ranked],
            "candidates_ranked": len(ranked),
        }
        status = "FAIL" if problems else "PASS"
        summary = (
            "; ".join(problems)
            if problems
            else f"rank_technicians ranked {len(ranked)} candidates; certification gate and "
            f"dominance order hold; top = {dispatch['selected_technician']}"
        )
        self._record(stage, status, summary, **dispatch)
        return dispatch

    # ------------------------------------------------------------------
    # Stages 5-6: field execution and post-repair telemetry (live only)
    # ------------------------------------------------------------------
    def stage_field_and_restoration(self) -> None:
        self._record(
            STAGE_ORDER[4],
            "UNMEASURED",
            "Field execution needs a technician completing the preventive work order on a live "
            "runtime (technician app / fix.service.order); no in-process path exists.",
        )
        self._record(
            STAGE_ORDER[5],
            "UNMEASURED",
            "Post-repair health restoration needs fresh telemetry from the live IoT pipeline "
            "for the repaired equipment; not observable locally.",
        )

    def run(self) -> dict:
        print("======================================================================")
        print("R09-M03-T02: Verifying Predictive-Maintenance Closed Loop")
        print("Standard: P11 Traceability / M02 Field Dispatch / M48 IoT Integration")
        print("======================================================================")

        self.stage_telemetry()
        self.stage_prediction()
        self.stage_work_order()
        dispatch = self.stage_dispatch()
        self.stage_field_and_restoration()

        stages = [self.stages[name] for name in STAGE_ORDER]
        statuses = [s["status"] for s in stages]
        verdict = overall_verdict(statuses)
        counts = {k: statuses.count(k) for k in ("PASS", "FAIL", "UNMEASURED")}
        finding = (
            f"{counts['PASS']} stage(s) PASS, {counts['FAIL']} FAIL, "
            f"{counts['UNMEASURED']} UNMEASURED of {len(stages)}. "
            + " | ".join(f"{s['stage']}: {s['summary']}" for s in stages if s["status"] != "PASS")
        )

        evidence = {
            "milestone": "R09-M03",
            "task": "R09-M03-T02",
            "standard": "Closed-Loop Predictive Maintenance / M02 Dispatch / M48 IoT Integration",
            "timestamp": datetime.now(UTC).isoformat(),
            "verdict": verdict,
            "status": verdict,
            "closed_loop_verified": verdict == "PASS",
            "stage_counts": counts,
            "stages": stages,
            "stages_completed": [s["stage"] for s in stages if s["status"] == "PASS"],
            "technician_dispatch": dispatch,
            "dispatch_fixture_inputs": {
                "context": DISPATCH_CONTEXT,
                "candidates": DISPATCH_FIXTURE,
            },
            "audit_log": self.audit_log,
            "finding": finding,
        }

        self.evidence_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.evidence_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(evidence, f, indent=2)

        print(f"\n[{verdict}] {finding}")
        print(f"Evidence written to: {self.evidence_path}")
        return evidence


if __name__ == "__main__":
    verifier = PredictiveMaintenanceClosedLoopVerifier()
    res = verifier.run()
    sys.exit(EXIT_CODES.get(res.get("verdict"), 2))
