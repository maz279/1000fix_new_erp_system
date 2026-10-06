/// SyncState — the state machine for UI rendering (AR-010 §4.2).
///
/// The sync engine's state as the UI sees it: idle, syncing, offline,
/// or error. The UI renders a status bar/pill from this; the states
/// are mutually exclusive and drive the visual language.
library;

enum SyncPhase {
  /// No sync in progress; the journal may have pending commands.
  idle,

  /// A sync cycle is running (uploading commands, downloading deltas).
  syncing,

  /// The device is offline (network unreachable); commands accumulate.
  offline,

  /// The last sync failed (server error, timeout); commands are safe.
  error,
}

/// The sync state snapshot the UI renders.
class SyncState {
  final SyncPhase phase;
  final DateTime? lastSyncAt;
  final int pendingCount;
  final int rejectedCount;
  final String? errorMessage;

  const SyncState({
    this.phase = SyncPhase.idle,
    this.lastSyncAt,
    this.pendingCount = 0,
    this.rejectedCount = 0,
    this.errorMessage,
  });

  /// Whether the UI should show a "pending" badge.
  bool get hasPending => pendingCount > 0;

  /// Whether the UI should show a "rejected" warning.
  bool get hasRejections => rejectedCount > 0;

  /// The badge label for the sync status bar.
  String get label {
    switch (phase) {
      case SyncPhase.idle:
        return hasPending ? '$pendingCount pending' : 'Synced';
      case SyncPhase.syncing:
        return 'Syncing…';
      case SyncPhase.offline:
        return 'Offline — $pendingCount queued';
      case SyncPhase.error:
        return 'Sync failed — $pendingCount queued';
    }
  }

  SyncState copyWith({
    SyncPhase? phase,
    DateTime? lastSyncAt,
    int? pendingCount,
    int? rejectedCount,
    String? errorMessage,
  }) =>
      SyncState(
        phase: phase ?? this.phase,
        lastSyncAt: lastSyncAt ?? this.lastSyncAt,
        pendingCount: pendingCount ?? this.pendingCount,
        rejectedCount: rejectedCount ?? this.rejectedCount,
        errorMessage: errorMessage ?? this.errorMessage,
      );
}
