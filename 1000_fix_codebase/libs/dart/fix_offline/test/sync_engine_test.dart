import 'package:fix_offline/fix_offline.dart';

class FakeTransport implements SyncTransport {
  final List<String> callOrder = [];
  final Map<String, Map<String, dynamic>> ackMap;
  final Map<String, String> rejMap;
  final String nextToken;
  final List<Map<String, dynamic>> deltas;

  FakeTransport({
    this.ackMap = const {},
    this.rejMap = const {},
    this.nextToken = 'tok-server-002',
    this.deltas = const [],
  });

  @override
  Future<BatchResult> upload(List<Command> commands) async {
    callOrder.add('upload');
    return BatchResult(
      acknowledged: ackMap,
      rejected: rejMap,
      checksum: 'sha256-batch-chk-12345',
    );
  }

  @override
  Future<({String token, List<Map<String, dynamic>> deltas})> download(String lastToken) async {
    callOrder.add('download');
    return (token: nextToken, deltas: deltas);
  }
}

void main() async {
  print('Running sync_engine_test.dart...');

  final store = InMemoryJournalStore();
  final journal = CommandJournal(store);
  final ledger = InMemoryIdempotencyLedger();

  await journal.record(
    commandId: 'cmd-sync-001',
    model: 'fix.job',
    recordId: 50,
    operation: 'complete_job',
    payload: {'notes': 'Compressor replaced and tested'},
  );

  final transport = FakeTransport(
    ackMap: {
      'cmd-sync-001': {'status': 'completed', 'updated_at': '2026-10-17T10:00:00Z'}
    },
    rejMap: {},
  );

  final engine = SyncEngine(journal, ledger, transport);

  // Run sync
  final result = await engine.sync();

  // Verify SP-07: upload must precede download
  assert(transport.callOrder.length == 2);
  assert(transport.callOrder[0] == 'upload');
  assert(transport.callOrder[1] == 'download');

  assert(result.acknowledged == 1);
  assert(result.rejected == 0);

  // Verify Idempotency ledger recorded it (DI-05)
  final hasRecorded = await ledger.has('cmd-sync-001');
  assert(hasRecorded == true);

  // Two-state conflict disclosure contract
  final disclosure = ConflictDisclosure();
  assert(disclosure.isNotYetSynced('cmd-sync-002') == false);

  print('All sync engine tests passed.');
}
