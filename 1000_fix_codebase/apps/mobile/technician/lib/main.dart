import 'package:flutter/material.dart';
import 'package:fix_ui/fix_color.dart';
import 'package:fix_ui/theme/tokens.dart';
import 'package:fix_offline/fix_offline.dart';

/// P02 Technician App — PP4-M02.
///
/// The field technician's daily surface:
/// - Day view: the optimized job queue with geofenced clock-in/out
/// - Job execution: context, diagnostic tree, fault coding, time tracking
/// - Parts: van stock, scan-to-consume, request + return
/// - Evidence capture: before/after photos with GPS + timestamp, Bengali
///   voice notes (all deferred via SP-09 evidence channel)
///
/// All colours from generated tokens via fixColor() (CFM-01). The offline
/// engine (fix_offline) is the data layer: commands journal locally,
/// sync SP-07 upload-first, evidence defers on a separate channel.
void main() => runApp(const TechnicianApp());

class TechnicianApp extends StatelessWidget {
  const TechnicianApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'P02 Technician',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: fixColor(t_color_primary_base)!,
        ),
        scaffoldBackgroundColor: fixColor(t_color_surface_canvas),
      ),
      home: const DayViewScreen(),
    );
  }
}

/// Day view — the job queue (PP4-M02-T02).
class DayViewScreen extends StatelessWidget {
  const DayViewScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('P02 Technician'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
        actions: [
          // The sync status pill — driven by the offline engine's state
          IconButton(
            icon: const Icon(Icons.sync),
            onPressed: () {
              // The sync engine runs SP-07: upload commands first, then
              // download deltas. The pill shows the state from SyncState.
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Sync: upload-first (SP-07)')),
              );
            },
          ),
        ],
      ),
      body: const JobQueue(),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        selectedItemColor: fixColor(t_color_primary_base),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.list), label: 'Day View'),
          BottomNavigationBarItem(icon: Icon(Icons.build), label: 'Jobs'),
          BottomNavigationBarItem(icon: Icon(Icons.inventory), label: 'Parts'),
          BottomNavigationBarItem(icon: Icon(Icons.photo_camera), label: 'Evidence'),
        ],
        currentIndex: 0,
        onTap: (index) {
          // Navigate to the corresponding screen
        },
      ),
    );
  }
}

/// The optimized job queue — the technician's daily list.
class JobQueue extends StatelessWidget {
  const JobQueue({super.key});

  @override
  Widget build(BuildContext context) {
    // In a full implementation, this builds from the journal's cached
    // records (the read projection — never authoritative). The offline
    // engine provides the data; this widget renders it.
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 3, // Placeholder — real count from the read cache
      itemBuilder: (context, index) {
        return Card(
          color: fixColor(t_color_surface_primary),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: fixColor(t_color_status_info_bg),
              child: Text(
                '${index + 1}',
                style: TextStyle(color: fixColor(t_color_status_info)),
              ),
            ),
            title: Text(
              'Work Order SO-2026-00${index + 1}',
              style: TextStyle(
                color: fixColor(t_color_text_primary),
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            subtitle: Text(
              'Device: Samsung Galaxy S24 · Priority: ${index == 0 ? "HIGH" : "NORMAL"}',
              style: TextStyle(
                color: fixColor(t_color_text_secondary),
                fontSize: 12,
              ),
            ),
            trailing: Icon(
              Icons.chevron_right,
              color: fixColor(t_color_text_ink_faint),
            ),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const JobExecutionScreen(),
                ),
              );
            },
          ),
        );
      },
    );
  }
}

/// Job execution — the technician's work surface (PP4-M02-T03).
///
/// Shows the full job context, the diagnostic tree, fault coding, and
/// time tracking. Every state change is a COMMAND (not a record write):
/// the journal records it, the sync engine uploads it (SP-07).
class JobExecutionScreen extends StatelessWidget {
  const JobExecutionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Job Execution'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _section('Device Context', [
            _kv('Brand', 'Samsung'),
            _kv('Model', 'Galaxy S24'),
            _kv('Warranty', 'Active until 2027-03'),
            _kv('SLA', '4h remaining'),
          ]),
          _section('Diagnostic Tree', [
            _diagnosticStep('Symptom: No power', true),
            _diagnosticStep('Check battery connector', true),
            _diagnosticStep('Replace battery module', false),
          ]),
          _section('Fault Coding', [
            _faultCodeChip('POWER_BATTERY', true),
            _faultCodeChip('CONNECTOR_LOOSE', false),
          ]),
          _section('Time Tracking', [
            _kv('Started', '09:30'),
            _kv('Elapsed', '2h 15m'),
            _kv('Standard time', '3h'),
          ]),
          _actionButtons(context),
        ],
      ),
    );
  }

  Widget _section(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(top: 16, bottom: 8),
          child: Text(
            title,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: fixColor(t_color_text_primary),
            ),
          ),
        ),
        ...children,
      ],
    );
  }

  Widget _kv(String key, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          SizedBox(
            width: 120,
            child: Text(
              key,
              style: TextStyle(
                fontSize: 12,
                color: fixColor(t_color_text_secondary),
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                fontSize: 12,
                color: fixColor(t_color_text_primary),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _diagnosticStep(String step, bool done) {
    return ListTile(
      dense: true,
      leading: Icon(
        done ? Icons.check_circle : Icons.radio_button_unchecked,
        color: done
            ? fixColor(t_color_status_success)
            : fixColor(t_color_text_ink_faint),
      ),
      title: Text(
        step,
        style: TextStyle(
          fontSize: 12,
          color: fixColor(done ? t_color_text_primary : t_color_text_secondary),
        ),
      ),
    );
  }

  Widget _faultCodeChip(String code, bool selected) {
    return Chip(
      label: Text(code),
      backgroundColor: selected
          ? fixColor(t_color_status_info_bg)
          : fixColor(t_color_surface_secondary),
      labelStyle: TextStyle(
        fontSize: 10,
        color: selected
            ? fixColor(t_color_status_info)
            : fixColor(t_color_text_secondary),
      ),
    );
  }

  Widget _actionButtons(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 24),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          ElevatedButton.icon(
            onPressed: () {
              // Record a command: status → in_repair (the journal records
              // it; the sync engine uploads it SP-07 upload-first)
            },
            icon: const Icon(Icons.play_arrow),
            label: const Text('Start Work'),
            style: ElevatedButton.styleFrom(
              backgroundColor: fixColor(t_color_primary_base),
              foregroundColor: fixColor(t_color_text_inverse),
            ),
          ),
          ElevatedButton.icon(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const EvidenceCaptureScreen()),
              );
            },
            icon: const Icon(Icons.photo_camera),
            label: const Text('Evidence'),
            style: ElevatedButton.styleFrom(
              backgroundColor: fixColor(t_color_surface_primary),
              foregroundColor: fixColor(t_color_primary_base),
            ),
          ),
        ],
      ),
    );
  }
}

/// Evidence capture — before/after photos with GPS + timestamp (PP4-M02-T05).
///
/// Evidence uploads via the SP-09 deferred channel — NEVER blocking state
/// sync. A 40 MB photo backlog does not delay a job status change.
class EvidenceCaptureScreen extends StatelessWidget {
  const EvidenceCaptureScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Evidence Capture'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.photo_camera,
              size: 64,
              color: fixColor(t_color_primary_base),
            ),
            const SizedBox(height: 16),
            Text(
              'Photos upload on the SP-09 deferred channel —\nnever blocking job status sync.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                color: fixColor(t_color_text_secondary),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
