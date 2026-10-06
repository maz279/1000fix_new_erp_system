/// Command — the journal's atomic unit (AR-010 §3).
///
/// A command is an intent ("set status to in_repair"), NOT a record
/// snapshot. The journal stores commands; the server's reply is the
/// authoritative record state. This distinction is the foundation of
/// the engine: commands can be replayed, reordered and deduplicated;
/// records cannot.
library;

import 'dart:convert';

/// A command's lifecycle in the journal.
enum CommandStatus {
  /// Created locally, not yet sent (offline or sync pending).
  pending,

  /// Sent to the server, awaiting acknowledgement.
  inFlight,

  /// Acknowledged by the server — the idempotency ledger has the result.
  acknowledged,

  /// Rejected by the server — the conflict disclosure shows this to the user.
  /// NEVER conflated with "pending" (AR-010 §6: not-yet-synced ≠ rejected).
  rejected,
}

/// A single offline command (AR-010 §3.1).
class Command {
  /// Client-generated UUID v4 — the idempotency key. The server uses this
  /// to deduplicate: on repeat, it returns the original result (DI-05).
  final String commandId;

  /// The target model (e.g. "fix.service.order").
  final String model;

  /// The target record's server ID (null for creates).
  final int? recordId;

  /// The operation type (create, write, action).
  final String operation;

  /// The payload — a JSON-encodable map. For `write`, the field:value
  /// pairs to set. For `action`, the action name and kwargs.
  final Map<String, dynamic> payload;

  /// When the command was created (client clock, ISO-8601).
  final DateTime createdAt;

  /// The current status in the journal.
  final CommandStatus status;

  /// The server's response for acknowledged commands (the record state).
  final Map<String, dynamic>? serverResult;

  /// The server's rejection reason for rejected commands.
  final String? rejectionReason;

  const Command({
    required this.commandId,
    required this.model,
    this.recordId,
    required this.operation,
    required this.payload,
    required this.createdAt,
    this.status = CommandStatus.pending,
    this.serverResult,
    this.rejectionReason,
  });

  /// Serialize to JSON for the wire and the journal.
  Map<String, dynamic> toJson() => {
    'command_id': commandId,
    'model': model,
    'record_id': recordId,
    'operation': operation,
    'payload': payload,
    'created_at': createdAt.toIso8601String(),
    'status': status.name,
    if (serverResult != null) 'server_result': serverResult,
    if (rejectionReason != null) 'rejection_reason': rejectionReason,
  };

  /// Deserialize from JSON.
  factory Command.fromJson(Map<String, dynamic> json) => Command(
    commandId: json['command_id'] as String,
    model: json['model'] as String,
    recordId: json['record_id'] as int?,
    operation: json['operation'] as String,
    payload: (json['payload'] as Map<String, dynamic>?)
        ?.map((k, v) => MapEntry(k, v)) ?? {},
    createdAt: DateTime.parse(json['created_at'] as String),
    status: CommandStatus.values.firstWhere(
      (s) => s.name == json['status'],
      orElse: () => CommandStatus.pending,
    ),
    serverResult: json['server_result'] as Map<String, dynamic>?,
    rejectionReason: json['rejection_reason'] as String?,
  );

  /// A copy with a new status (immutable update).
  Command withStatus(
    CommandStatus newStatus, {
    Map<String, dynamic>? result,
    String? reason,
  }) =>
    Command(
      commandId: commandId,
      model: model,
      recordId: recordId,
      operation: operation,
      payload: payload,
      createdAt: createdAt,
      status: newStatus,
      serverResult: result ?? serverResult,
      rejectionReason: reason ?? rejectionReason,
    );

  /// The wire format for upload — just the fields the server needs.
  Map<String, dynamic> toWire() => {
    'command_id': commandId,
    'model': model,
    'record_id': recordId,
    'operation': operation,
    'payload': json.encode(payload),
    'created_at': createdAt.toIso8601String(),
  };

  @override
  String toString() =>
    'Command($commandId, $model/$recordId, $operation, ${status.name})';
}
