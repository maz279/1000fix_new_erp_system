/// CommandJournal — the append-only local store (AR-010 §4).
///
/// The journal is the ONLY local truth (AR-010 §3: "commands, not
/// records"). The read cache is never authoritative — it's a projection
/// of the last-known server state. In the Flutter implementation this
/// sits over SQLCipher; the interface is pure Dart so the engine logic
/// is testable without a database.
library;

import 'command.dart';

/// Abstract storage interface — the Flutter app injects SQLCipher; tests
/// inject an in-memory implementation.
abstract class JournalStore {
  /// Append a command (never modify — append-only).
  Future<void> append(Command command);

  /// Get all commands for a model, ordered by creation time.
  Future<List<Command>> getByModel(String model);

  /// Get pending commands (not yet sent), across all models, oldest first.
  Future<List<Command>> getPending();

  /// Get in-flight commands (sent but not acknowledged).
  Future<List<Command>> getInFlight();

  /// Update a command's status (the only mutation allowed).
  Future<void> updateStatus(String commandId, Command command);

  /// Get the last acknowledged server state for a record (the read cache).
  Future<Map<String, dynamic>?> getCachedRecord(String model, int recordId);

  /// Cache a record's server state (the projection).
  Future<void> cacheRecord(String model, int recordId, Map<String, dynamic> data);

  /// Wipe the entire journal (remote revocation — AR-010 §3.1).
  Future<void> wipe();
}

/// In-memory implementation for tests and non-persistent contexts.
class InMemoryJournalStore implements JournalStore {
  final List<Command> _commands = [];
  final Map<String, Map<int, Map<String, dynamic>>> _cache = {};

  @override
  Future<void> append(Command command) async {
    _commands.add(command);
  }

  @override
  Future<List<Command>> getByModel(String model) async {
    return _commands.where((c) => c.model == model).toList()
      ..sort((a, b) => a.createdAt.compareTo(b.createdAt));
  }

  @override
  Future<List<Command>> getPending() async {
    return _commands.where((c) => c.status == CommandStatus.pending).toList()
      ..sort((a, b) => a.createdAt.compareTo(b.createdAt));
  }

  @override
  Future<List<Command>> getInFlight() async {
    return _commands.where((c) => c.status == CommandStatus.inFlight).toList();
  }

  @override
  Future<void> updateStatus(String commandId, Command command) async {
    final idx = _commands.indexWhere((c) => c.commandId == commandId);
    if (idx >= 0) _commands[idx] = command;
  }

  @override
  Future<Map<String, dynamic>?> getCachedRecord(
      String model, int recordId) async {
    return _cache[model]?[recordId];
  }

  @override
  Future<void> cacheRecord(
      String model, int recordId, Map<String, dynamic> data) async {
    _cache.putIfAbsent(model, () => {});
    _cache[model]![recordId] = data;
  }

  @override
  Future<void> wipe() async {
    _commands.clear();
    _cache.clear();
  }
}

/// The command journal — the single local truth.
class CommandJournal {
  final JournalStore _store;

  CommandJournal(this._store);

  /// Record a new command (append-only — the ONLY way data enters).
  Future<Command> record({
    required String commandId,
    required String model,
    int? recordId,
    required String operation,
    required Map<String, dynamic> payload,
  }) async {
    final command = Command(
      commandId: commandId,
      model: model,
      recordId: recordId,
      operation: operation,
      payload: payload,
      createdAt: DateTime.now(),
    );
    await _store.append(command);
    return command;
  }

  /// Pending commands, oldest first — what the sync engine uploads.
  Future<List<Command>> pending() => _store.getPending();

  /// In-flight commands — what we're waiting on.
  Future<List<Command>> inFlight() => _store.getInFlight();

  /// Mark a command as acknowledged (the server accepted it).
  ///
  /// If the command is not in the pending or in-flight list (an idempotent
  /// retry — the server already acknowledged it), this is a no-op (DI-05).
  Future<void> acknowledge(
      String commandId, Map<String, dynamic> serverResult) async {
    final commands = await _store.getPending();
    // Also check in-flight
    final all = [...commands, ...await _store.getInFlight()];
    Command? cmd;
    for (final c in all) {
      if (c.commandId == commandId) {
        cmd = c;
        break;
      }
    }
    if (cmd == null) return; // Idempotent retry — already acknowledged (DI-05)
    await _store.updateStatus(
      commandId,
      cmd.withStatus(CommandStatus.acknowledged, result: serverResult),
    );
    // Cache the record state for the read projection
    if (cmd.recordId != null) {
      await _store.cacheRecord(cmd.model, cmd.recordId!, serverResult);
    }
  }

  /// Mark a command as rejected — the conflict disclosure shows this.
  ///
  /// Idempotent-safe: if the command is already processed, a no-op.
  Future<void> reject(String commandId, String reason) async {
    final all = [
      ...await _store.getPending(),
      ...await _store.getInFlight(),
    ];
    Command? cmd;
    for (final c in all) {
      if (c.commandId == commandId) {
        cmd = c;
        break;
      }
    }
    if (cmd == null) return; // Idempotent retry
    await _store.updateStatus(
      commandId,
      cmd.withStatus(CommandStatus.rejected, reason: reason),
    );
  }

  /// Mark a command as in-flight (the sync engine sends it).
  /// Idempotent-safe: if the command is not pending, a no-op.
  Future<void> markInFlight(String commandId) async {
    final pending = await _store.getPending();
    Command? cmd;
    for (final c in pending) {
      if (c.commandId == commandId) {
        cmd = c;
        break;
      }
    }
    if (cmd == null) return; // Already in-flight or processed
    await _store.updateStatus(
      commandId,
      cmd.withStatus(CommandStatus.inFlight),
    );
  }

  /// The cached record state (the read projection — never authoritative).
  Future<Map<String, dynamic>?> cachedRecord(String model, int recordId) =>
      _store.getCachedRecord(model, recordId);

  /// Remote revocation — wipe the journal (AR-010 §3.1: keyed from device
  /// credentials + a server-issued key; wiping is the kill switch).
  Future<void> revoke() => _store.wipe();
}
