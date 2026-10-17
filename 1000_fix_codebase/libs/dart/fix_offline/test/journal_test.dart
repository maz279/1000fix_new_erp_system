import 'package:fix_offline/fix_offline.dart';

void main() {
  // Pure Dart unit test suite for CommandJournal and SQLCipher configuration
  print('Running journal_test.dart...');

  testInMemoryJournal();
  testSqlCipherConfig();
  print('All journal tests passed.');
}

void testInMemoryJournal() async {
  final store = InMemoryJournalStore();
  final journal = CommandJournal(store);

  // 1. Record commands (append-only)
  final cmd1 = await journal.record(
    commandId: 'cmd-uuid-001',
    model: 'fix.job',
    recordId: 101,
    operation: 'start_job',
    payload: {'technician_id': 5, 'odometer': 12450},
  );

  assert(cmd1.status == CommandStatus.pending);
  assert(cmd1.commandId == 'cmd-uuid-001');

  final pending = await journal.pending();
  assert(pending.length == 1);
  assert(pending.first.commandId == 'cmd-uuid-001');

  // 2. Mark in-flight
  await journal.markInFlight('cmd-uuid-001');
  final inFlight = await journal.inFlight();
  assert(inFlight.length == 1);

  // 3. Acknowledge with server result
  await journal.acknowledge('cmd-uuid-001', {'state': 'in_progress', 'server_version': 2});
  final cached = await journal.cachedRecord('fix.job', 101);
  assert(cached != null);
  assert(cached!['state'] == 'in_progress');

  // 4. Remote revocation wipe
  await journal.revoke();
  final afterRevoke = await journal.pending();
  assert(afterRevoke.isEmpty);
  final cacheAfterRevoke = await journal.cachedRecord('fix.job', 101);
  assert(cacheAfterRevoke == null);
}

void testSqlCipherConfig() {
  final config = SqlCipherConfig(
    dbPath: '/data/user/0/com.fix1000.technician/databases/fix_offline_enc.db',
    deviceSecret: 'dev_sec_999',
    serverKey: 'srv_key_888',
    cipherPageSize: 4096,
    kdfIter: 256000,
  );

  assert(config.pragmaKey.startsWith('x\''));
  assert(config.pragmaKey.endsWith('\''));
  assert(config.pragmaKey.length == 67); // x' + 64 hex chars + '

  final store = SqlCipherJournalStore(config);
  assert(store.schemaSql.contains('PRAGMA cipher_page_size = 4096;'));
  assert(store.schemaSql.contains('CREATE TABLE IF NOT EXISTS offline_journal_commands'));
  assert(store.schemaSql.contains('CREATE TABLE IF NOT EXISTS offline_read_cache'));
  assert(store.schemaSql.contains('CREATE TABLE IF NOT EXISTS offline_evidence_queue'));
}
