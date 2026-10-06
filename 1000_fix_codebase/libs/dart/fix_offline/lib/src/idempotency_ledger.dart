/// IdempotencyLedger — client-side command deduplication (AR-010 §4.4, DI-05).
///
/// The server maintains its own ledger keyed on `command_id`; on repeat,
/// it returns the original result. This is the CLIENT side: it tracks
/// which command IDs the server has acknowledged so we never re-send
/// a command the server already processed (even if the ack was lost).
library;

import 'command.dart';

/// The client-side idempotency ledger.
class IdempotencyLedger {
  /// commandId → the server's result (the authoritative record state).
  final Map<String, Map<String, dynamic>> _entries = {};

  /// Record an acknowledged command's result.
  void record(String commandId, Map<String, dynamic> result) {
    _entries[commandId] = result;
  }

  /// Whether the server has already acknowledged this command.
  bool has(String commandId) => _entries.containsKey(commandId);

  /// The server's original result for this command (or null if unknown).
  Map<String, dynamic>? result(String commandId) => _entries[commandId];

  /// The number of tracked acknowledgements.
  int get count => _entries.length;

  /// Filter a list of pending commands to only those the ledger hasn't
  /// seen (i.e., strip commands the server already processed).
  List<Command> deduplicate(List<Command> commands) {
    return commands.where((c) => !has(c.commandId)).toList();
  }

  /// Clear the ledger (remote revocation).
  void clear() => _entries.clear();
}
