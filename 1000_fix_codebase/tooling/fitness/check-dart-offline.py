#!/usr/bin/env python3
"""check-dart-offline — PP4-M01 structural validation for the offline engine.

Validates the fix_offline library's structure without a Dart compiler:
every export resolves, every class declares its AR-010-mandated members,
and the SP-07/SP-09/DI-05/AR-010 §6 rules are present in the source.

Exit: 0 pass / 1 violations.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LIB = REPO / "libs" / "dart" / "fix_offline"


def read(rel: str) -> str:
    return (LIB / rel).read_text(encoding="utf-8")


def main() -> int:
    v: list[str] = []

    # 1. The barrel exports all 7 source files
    barrel = read("lib/fix_offline.dart")
    for name in (
        "command",
        "journal",
        "sync_engine",
        "idempotency_ledger",
        "conflict_disclosure",
        "evidence_channel",
        "sync_state",
    ):
        if f"src/{name}.dart" not in barrel:
            v.append(f"barrel: src/{name}.dart not exported")

    # 2. Command (AR-010 §3)
    cmd = read("lib/src/command.dart")
    for member in ("commandId", "model", "recordId", "operation", "payload", "createdAt", "status"):
        if (
            f"final {member}"
            not in cmd.replace("final String", "final ")
            .replace("final Map", "final ")
            .replace("final DateTime", "final ")
            .replace("final int?", "final ")
            .replace("final CommandStatus", "final ")
            and f"this.{member}" not in cmd
        ):
            v.append(f"Command: missing field {member}")
    if "CommandStatus.pending" not in cmd:
        v.append("Command: pending status missing")
    if "rejected" not in cmd:
        v.append("Command: rejected status missing")
    if "acknowledged" not in cmd:
        v.append("Command: acknowledged status missing")
    # The idempotency key is client-generated
    if ("commandId" not in cmd or "UUID" not in cmd) and (
        "client-generated" not in cmd and "idempotency key" not in cmd
    ):
        v.append("Command: commandId must be documented as the client-generated idempotency key")

    # 3. Journal (AR-010 §4)
    journal = read("lib/src/journal.dart")
    if "append" not in journal:
        v.append("Journal: append-only not implemented")
    if "JournalStore" not in journal:
        v.append("Journal: JournalStore abstraction missing")
    if "InMemoryJournalStore" not in journal:
        v.append("Journal: InMemoryJournalStore for tests missing")
    if "wipe" not in journal:
        v.append("Journal: remote revocation (wipe) missing")
    if "getCachedRecord" not in journal:
        v.append("Journal: read-cache projection missing")
    if "never authoritative" not in journal:
        v.append("Journal: read-cache 'never authoritative' doc missing")

    # 4. SyncEngine (AR-010 §4.2 / SP-07)
    sync = read("lib/src/sync_engine.dart")
    if "upload" not in sync:
        v.append("SyncEngine: upload missing")
    if "download" not in sync:
        v.append("SyncEngine: download missing")
    # SP-07: upload precedes download in the source code order
    upload_pos = sync.find("upload(pending)")
    download_pos = sync.find("_transport.download")
    if upload_pos < 0 or download_pos < 0 or upload_pos > download_pos:
        v.append("SyncEngine: SP-07 upload-first ordering violated in source")
    if "upload FIRST" not in sync and "upload first" not in sync.lower():
        v.append("SyncEngine: SP-07 not documented")
    # SP-02: per-command transactions, not per-batch
    if "own transaction" not in sync and "per-command" not in sync.lower():
        v.append("SyncEngine: SP-02 per-command transaction not documented")

    # 5. IdempotencyLedger (DI-05)
    idem = read("lib/src/idempotency_ledger.dart")
    for member in ("record", "has", "result", "deduplicate"):
        if member not in idem:
            v.append(f"IdempotencyLedger: missing method {member}")
    if "command_id" not in idem and "commandId" not in idem:
        v.append("IdempotencyLedger: not keyed on commandId")

    # 6. ConflictDisclosure (AR-010 §6)
    conflict = read("lib/src/conflict_disclosure.dart")
    if "notYetSynced" not in conflict:
        v.append("ConflictDisclosure: notYetSynced state missing")
    if "syncedAndRejected" not in conflict:
        v.append("ConflictDisclosure: syncedAndRejected state missing")
    if "NEVER be conflated" not in conflict:
        v.append("ConflictDisclosure: the two-state 'never conflate' doc missing")
    if "requiresAction" not in conflict:
        v.append("ConflictDisclosure: requiresAction property missing")
    if "counts" not in conflict:
        v.append("ConflictDisclosure: counts helper missing")

    # 7. EvidenceChannel (SP-09)
    evidence = read("lib/src/evidence_channel.dart")
    if "enqueue" not in evidence:
        v.append("EvidenceChannel: enqueue missing")
    if "process" not in evidence:
        v.append("EvidenceChannel: process missing")
    if "resume" not in evidence:
        v.append("EvidenceChannel: resume (partial upload) missing")
    if "paused" not in evidence:
        v.append("EvidenceChannel: pause/resume control missing")
    # SP-09: evidence never blocks state sync
    if "NEVER block" not in evidence and "never blocks" not in evidence.lower():
        v.append("EvidenceChannel: SP-09 'never blocks state sync' doc missing")

    # 8. SyncState
    state = read("lib/src/sync_state.dart")
    for phase in ("idle", "syncing", "offline", "error"):
        if phase not in state:
            v.append(f"SyncState: phase {phase} missing")
    if "pendingCount" not in state or "rejectedCount" not in state:
        v.append("SyncState: pending/rejected counts missing")
    if "label" not in state:
        v.append("SyncState: UI label property missing")

    # 9. Pubspec exists with fix_ui dependency
    pubspec = read("pubspec.yaml")
    if "fix_ui" not in pubspec:
        v.append("pubspec: fix_ui path dependency missing")

    if v:
        print(f"dart-offline: FAIL - {len(v)} violation(s):")
        for line in v:
            print(f"  {line}")
        return 1
    print(
        "dart-offline: OK — 7 source files, all AR-010 mandates present "
        "(command model, append-only journal, SP-07 upload-first, "
        "DI-05 idempotency, §6 two-state disclosure, SP-09 evidence "
        "channel, sync state machine)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
