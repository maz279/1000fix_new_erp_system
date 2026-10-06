/// fix_offline — THE one offline engine (AR-010, ADR-024, FL-03).
///
/// Exports the public surface consumed by P02/P09/P11/APP-04:
/// - [Command] — the journal's atomic unit (a command, not a record)
/// - [CommandJournal] — the append-only local store
/// - [SyncEngine] — SP-07 upload-first sync sequence
/// - [IdempotencyLedger] — client-side command-ID tracking
/// - [ConflictDisclosure] — the two-state UI contract (AR-010 §6)
/// - [EvidenceChannel] — SP-09 deferred, non-blocking media sync
/// - [SyncState] — the state machine for UI rendering
export 'src/command.dart';
export 'src/journal.dart';
export 'src/sync_engine.dart';
export 'src/idempotency_ledger.dart';
export 'src/conflict_disclosure.dart';
export 'src/evidence_channel.dart';
export 'src/sync_state.dart';
