/// ConflictDisclosure — the two-state UI contract (AR-010 §6).
///
/// THE rule: "not yet synced" and "synced-and-rejected" are two different
/// states that must NEVER be conflated. A technician who cannot tell the
/// difference will redo work or lose it.
///
/// - NotYetSynced: the command is in the journal, the sync hasn't run or
///   the network was down. The work is SAFE — it will upload next sync.
///   UI: show a "pending" indicator (e.g. a clock icon).
///
/// - SyncedAndRejected: the server saw the command and refused it. The
///   work is NOT going to apply. The user MUST see the rejection reason
///   and decide what to do.
///   UI: show a "rejected" indicator (e.g. a red badge with the reason).
library;

import 'command.dart';

/// The two-state disclosure (AR-010 §6.1–§6.3).
enum DisclosureState {
  /// The command is in the journal but hasn't reached the server.
  /// The work is safe; it will upload on the next sync.
  notYetSynced,

  /// The server saw the command and rejected it.
  /// The work will NOT apply; the user must see the reason.
  syncedAndRejected,
}

/// A single conflict disclosure item for the UI.
class Disclosure {
  /// The command this disclosure is about.
  final Command command;

  /// Which of the two states this is.
  final DisclosureState state;

  /// The rejection reason (only for syncedAndRejected).
  final String? reason;

  const Disclosure({
    required this.command,
    required this.state,
    this.reason,
  });

  /// What the UI shows as the badge label.
  String get label {
    switch (state) {
      case DisclosureState.notYetSynced:
        return 'Pending sync';
      case DisclosureState.syncedAndRejected:
        return 'Rejected: ${reason ?? "unknown reason"}';
    }
  }

  /// Whether the user needs to take action.
  bool get requiresAction => state == DisclosureState.syncedAndRejected;
}

/// Build disclosures from a list of journal commands.
class ConflictDisclosure {
  /// Build the disclosure list for UI rendering.
  ///
  /// Takes ALL non-acknowledged commands from the journal and classifies
  /// each into the correct two-state bucket. The UI renders these as
  /// badges/warnings — the states must be visually distinct.
  static List<Disclosure> build(List<Command> commands) {
    return commands
        .where((c) =>
            c.status == CommandStatus.pending ||
            c.status == CommandStatus.inFlight ||
            c.status == CommandStatus.rejected)
        .map((c) {
          switch (c.status) {
            case CommandStatus.pending:
            case CommandStatus.inFlight:
              return Disclosure(
                command: c,
                state: DisclosureState.notYetSynced,
              );
            case CommandStatus.rejected:
              return Disclosure(
                command: c,
                state: DisclosureState.syncedAndRejected,
                reason: c.rejectionReason,
              );
            case CommandStatus.acknowledged:
              // Shouldn't reach here (filtered above), but be safe
              return const Disclosure(
                command: Command(
                  commandId: '',
                  model: '',
                  operation: '',
                  payload: {},
                  createdAt: null,
                ),
                state: DisclosureState.notYetSynced,
              );
          }
        })
        .toList();
  }

  /// Whether any disclosure requires user action (a rejection exists).
  static bool hasRejections(List<Command> commands) {
    return commands.any((c) => c.status == CommandStatus.rejected);
  }

  /// The count of each state for a summary badge.
  static ({int pending, int rejected}) counts(List<Command> commands) {
    return (
      pending: commands
          .where((c) =>
              c.status == CommandStatus.pending ||
              c.status == CommandStatus.inFlight)
          .length,
      rejected: commands
          .where((c) => c.status == CommandStatus.rejected)
          .length,
    );
  }
}
