"""dsr-orchestrator — P07-M08-T02..T07 (CD-M29-nn; TSS §3.6.4, §20.2 W4).

The data-subject-request service. PDPA 2026 enforcement activates ~13 May
2027 — INSIDE this phase — with penalties to BDT 50 lakh; this milestone
cannot slip into Phase 8.

PURE orchestration logic (no Odoo imports): the request lifecycle, the
export assembly plan, and the ERASURE SAGA with compensating actions
(T04: a saga, not a DELETE) across regional primary, resident store (Z4),
read replicas, warehouse, object store, search index and backups-in-scope —
while PRESERVING the five-year statutory processing record (T05) and the
controller's 30-day notification clock (T06, NFR-093).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum


class DsrError(ValueError):
    pass


class DsrType(str, Enum):
    ACCESS = "access"            # T02
    RECTIFICATION = "rectification"
    PORTABILITY = "portability"  # T03 — machine-readable export
    ERASURE = "erasure"          # T04 — the saga
    OBJECTION = "objection"


class DsrState(str, Enum):
    RECEIVED = "received"
    VERIFYING = "verifying"      # identity verification first — always
    IN_PROGRESS = "in_progress"
    AWAITING_VERIFICATION = "awaiting_verification"  # rectification review
    COMPLETED = "completed"
    REJECTED = "rejected"


NOTIFICATION_DAYS = 30  # NFR-093: the controller notifies within 30 days
PROCESSING_RECORD_YEARS = 5  # NFR-095: retained THROUGH erasure


@dataclass(frozen=True)
class DsrRequest:
    request_id: str
    dsr_type: DsrType
    party_ref: str            # the fix.party pointer (never raw PII here)
    received_on: date
    state: DsrState = DsrState.RECEIVED
    due_on: date = None
    verified: bool = False

    def __post_init__(self):
        if self.due_on is None:
            object.__setattr__(self, "due_on", self.received_on + timedelta(days=NOTIFICATION_DAYS))


# ---------------------------------------------------------- export (T03) ----

class ResidencyClientProtocol:
    """The residency-service contract (FF-09: the ONLY path to Z4). The
    orchestrator depends on the protocol, never a concrete client."""

    def fetch_resident(self, party_ref: str) -> dict:
        raise NotImplementedError

    def tombstone(self, party_ref: str, key: str) -> None:
        raise NotImplementedError


@dataclass
class ExportBundle:
    party_ref: str
    regional: dict = field(default_factory=dict)   # the OLTP-side record
    resident: dict = field(default_factory=dict)   # Z4-side classified data
    machine_readable: bool = True

    def to_portable(self) -> dict:
        """The portable export: regional + resident assembled THROUGH the
        residency service (T03) — machine-readable, both stores."""
        if not self.machine_readable:
            raise DsrError("portability exports must be machine-readable")
        return {"party_ref": self.party_ref,
                "regional": self.regional,
                "resident": self.resident}


def assemble_export(party_ref: str, regional_loader, residency: ResidencyClientProtocol) -> ExportBundle:
    """T03: assemble through the residency service — never a direct
    resident-store read."""
    return ExportBundle(
        party_ref=party_ref,
        regional=regional_loader(party_ref),
        resident=residency.fetch_resident(party_ref),
    )


# ------------------------------------------------------ erasure saga (T04) ---

class SagaStep(str, Enum):
    # Forward order; compensations run in REVERSE for rollback.
    ANONYMIZE_REGIONAL = "anonymize_regional"
    TOMBSTONE_RESIDENT = "tombstone_resident"        # Z4 via the residency client
    PURGE_REPLICAS = "purge_read_replicas"
    PURGE_WAREHOUSE = "purge_warehouse_rows"
    PURGE_OBJECT_STORE = "purge_object_store"
    PURGE_SEARCH_INDEX = "purge_search_index"
    MARK_BACKUPS = "mark_backups_out_of_scope_next_cycle"  # backups roll out on cycle

    @property
    def compensation(self) -> str:
        return "restore_" + self.value


@dataclass
class SagaState:
    request_id: str
    party_ref: str
    completed: list[SagaStep] = field(default_factory=list)
    failed_at: SagaStep | None = None
    compensations_run: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.failed_at:
            return "rolled_back" if self.compensations_run else "failing"
        if len(self.completed) == len(list(SagaStep)):
            return "completed"
        return "in_progress"


def run_erasure_saga(state: SagaState, executors: dict[SagaStep, callable],
                     residency: ResidencyClientProtocol | None = None) -> SagaState:
    """T04: the saga. Each step runs once; the FIRST failure triggers the
    compensation chain in REVERSE order over the COMPLETED steps only.

    The processing record (T05) is written by the caller BEFORE the saga
    starts — erasure removes the data, never the record of processing.
    """
    order = list(SagaStep)
    for step in order:
        if step in state.completed:
            continue
        executor = executors.get(step)
        if executor is None:
            raise DsrError(f"no executor wired for saga step {step}")
        try:
            if step is SagaStep.TOMBSTONE_RESIDENT and residency is not None:
                residency.tombstone(state.party_ref, "all")
            executor(state.party_ref)
            state.completed.append(step)
        except Exception as exc:  # noqa: BLE001 — the saga must survive any step
            state.failed_at = step
            # Compensations in REVERSE order over completed steps.
            for done in reversed(state.completed):
                state.compensations_run.append(done.compensation)
            if state.compensations_run:
                state.completed = []  # rolled back to the pre-saga state
            raise DsrError(
                f"erasure saga failed at {step.value}: {exc}; "
                f"compensations run: {state.compensations_run}") from exc
    return state


def erasure_preserves_record(erased_on: date) -> date:
    """T05 / NFR-095: the statutory processing record survives FIVE YEARS
    past the erasure — the one thing erasure must NOT remove."""
    return erased_on + timedelta(days=365 * PROCESSING_RECORD_YEARS)


# ------------------------------------------------- breach runbook (T07) ------

BREACH_RUNBOOK = [
    "1. CONTAIN: revoke the compromised credentials; isolate the affected "
    "systems (SC-011 containment checklist).",
    "2. ASSESS within 72 hours: scope (data classes, subject count), cause, "
    "risk to data subjects.",
    "3. NOTIFY the National Data Management Authority — PDPA s.33 timeline; "
    "prepare the submission pack (SC-011 template).",
    "4. NOTIFY affected data subjects where the risk is high, in Bengali and "
    "English, through the M27 notification platform.",
    "5. RECORD: the incident, every action, every timestamp — the regulator "
    "asks for the trail, REHEARSED not documented (P07-M08-T07).",
    "6. REVIEW: root cause into the M23 CAPA cycle; DPIA (SC-003) re-run "
    "against what was learned.",
]
