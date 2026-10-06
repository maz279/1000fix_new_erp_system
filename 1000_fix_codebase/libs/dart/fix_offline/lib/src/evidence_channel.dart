/// EvidenceChannel — SP-09 deferred, non-blocking media sync (AR-010 §8).
///
/// A 40 MB photo backlog must NOT delay a job status change. Evidence
/// (photos, videos, voice notes) syncs on a separate low-priority,
/// resumable channel. The state sync never waits for media.
library;

/// An evidence item queued for deferred upload.
class EvidenceItem {
  final String id;
  final String commandId; // The parent command this evidence belongs to
  final String filePath; // Local file path
  final int sizeBytes;
  final EvidenceType type;
  final DateTime capturedAt;

  const EvidenceItem({
    required this.id,
    required this.commandId,
    required this.filePath,
    required this.sizeBytes,
    required this.type,
    required this.capturedAt,
  });
}

enum EvidenceType { photo, video, voiceNote, document }

/// Abstract evidence transport — the Flutter app injects multipart upload.
abstract class EvidenceTransport {
  /// Upload a single evidence item. Returns the server's reference.
  Future<String> upload(EvidenceItem item);

  /// Resume a partial upload from a byte offset.
  Future<String> resume(EvidenceItem item, int offset);

  /// Get the current byte offset for a partially-uploaded item.
  Future<int> getOffset(EvidenceItem item);
}

/// The deferred evidence channel.
///
/// SP-09: evidence uploads NEVER block state sync. The channel runs on
/// its own schedule (or opportunistically when connectivity allows),
/// resumes from byte offsets, and can be paused/cancelled.
class EvidenceChannel {
  final EvidenceTransport _transport;
  final List<EvidenceItem> _queue = [];
  final Set<String> _uploaded = {};
  bool _paused = false;

  EvidenceChannel(this._transport);

  /// Queue an evidence item for deferred upload (non-blocking).
  void enqueue(EvidenceItem item) {
    if (!_uploaded.contains(item.id)) {
      _queue.add(item);
    }
  }

  /// The current queue size (pending items).
  int get queueLength => _queue.length;

  /// Whether the channel is paused.
  bool get isPaused => _paused;

  /// Pause the channel (e.g., on expensive connectivity).
  void pause() => _paused = true;

  /// Resume the channel.
  void resume() => _paused = false;

  /// Process the queue — upload pending items, resuming partials.
  /// Returns the number successfully uploaded.
  Future<int> process() async {
    if (_paused) return 0;
    int uploaded = 0;
    final items = List<EvidenceItem>.from(_queue);
    for (final item in items) {
      try {
        final offset = await _transport.getOffset(item);
        final ref = offset > 0
            ? await _transport.resume(item, offset)
            : await _transport.upload(item);
        _uploaded.add(item.id);
        _queue.remove(item);
        uploaded++;
        // The server reference would be attached to the parent command's
        // evidence list in a full implementation
      } catch (_) {
        // SP-09: a failed evidence upload NEVER blocks the channel or
        // the state sync — just leave it in the queue for the next pass
        break; // Stop on first failure; retry next process() call
      }
    }
    return uploaded;
  }

  /// Whether an item has been successfully uploaded.
  bool isUploaded(String id) => _uploaded.contains(id);
}
