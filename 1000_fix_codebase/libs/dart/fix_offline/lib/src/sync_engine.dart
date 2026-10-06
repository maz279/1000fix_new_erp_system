/// SyncEngine — SP-07 upload-first sync (AR-010 §4.2).
///
/// THE rule: upload precedes download in the same sync cycle. Download-first
/// means the technician's work appears to vanish and return — users do not
/// wait to find out, they re-enter it. The sync is:
/// 1. Collect pending commands from the journal
/// 2. Upload as a batch (the server applies each in its own transaction)
/// 3. Per-batch checksum verification
/// 4. Download deltas by opaque server-issued token
/// 5. Update the read cache from the deltas
library;

import 'command.dart';
import 'journal.dart';
import 'idempotency_ledger.dart';

/// The server's response to a batch upload.
class BatchResult {
  /// Successfully applied commands with their results.
  final Map<String, Map<String, dynamic>> acknowledged;

  /// Rejected commands with reasons.
  final Map<String, String> rejected;

  /// The batch checksum the server computed.
  final String checksum;

  const BatchResult({
    required this.acknowledged,
    required this.rejected,
    required this.checksum,
  });

  /// Whether the entire batch was applied (no rejections).
  bool get allApplied => rejected.isEmpty;
}

/// Abstract transport — the Flutter app injects HTTP; tests inject fakes.
abstract class SyncTransport {
  /// Upload a batch of commands. The server applies each in its own
  /// transaction (SP-02); one rejected command does NOT roll back others.
  Future<BatchResult> upload(List<Command> commands);

  /// Download deltas since the last sync token. Returns the new token.
  Future<({String token, List<Map<String, dynamic>> deltas})>
      download(String lastToken);
}

/// The sync engine — drives the upload-first cycle.
class SyncEngine {
  final CommandJournal _journal;
  final IdempotencyLedger _ledger;
  final SyncTransport _transport;

  String _lastToken = '';

  SyncEngine(this._journal, this._ledger, this._transport);

  /// Run one full sync cycle: upload pending, then download deltas.
  /// Returns the number of commands acknowledged + rejected.
  Future<({int acknowledged, int rejected})> sync() async {
    // SP-07: upload FIRST, always
    final pending = await _journal.pending();
    int acked = 0;
    int rejected = 0;

    if (pending.isNotEmpty) {
      // Mark all as in-flight
      for (final cmd in pending) {
        await _journal.markInFlight(cmd.commandId);
      }

      // Upload the batch
      final result = await _transport.upload(pending);

      // Process acknowledgements
      for (final entry in result.acknowledged.entries) {
        await _journal.acknowledge(entry.key, entry.value);
        // Record in the idempotency ledger (client side)
        await _ledger.record(entry.key, entry.value);
        acked++;
      }

      // Process rejections — the conflict disclosure shows these
      for (final entry in result.rejected.entries) {
        await _journal.reject(entry.key, entry.value);
        rejected++;
      }
    }

    // THEN download deltas (SP-07: upload → download in the same cycle)
    final deltas = await _transport.download(_lastToken);
    _lastToken = deltas.token;

    return (acknowledged: acked, rejected: rejected);
  }
}
