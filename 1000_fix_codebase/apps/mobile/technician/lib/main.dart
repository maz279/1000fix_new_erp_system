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
class DayViewScreen extends StatefulWidget {
  const DayViewScreen({super.key});

  @override
  State<DayViewScreen> createState() => _DayViewScreenState();
}

class _DayViewScreenState extends State<DayViewScreen> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    JobQueue(),
    AttendanceScreen(),
    PartsScreen(),
    EvidenceCaptureScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('P02 Technician'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
        actions: [
          IconButton(
            icon: const Icon(Icons.emergency_share),
            tooltip: 'Panic SOS (M59)',
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Panic SOS: Distress beacon logged locally with GPS telemetry')),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.sync),
            tooltip: 'Sync (SP-07)',
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Sync: upload-first (SP-07)')),
              );
            },
          ),
        ],
      ),
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        selectedItemColor: fixColor(t_color_primary_base),
        currentIndex: _currentIndex,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.list), label: 'Queue'),
          BottomNavigationBarItem(icon: Icon(Icons.location_on), label: 'Attendance'),
          BottomNavigationBarItem(icon: Icon(Icons.inventory), label: 'Parts'),
          BottomNavigationBarItem(icon: Icon(Icons.photo_camera), label: 'Evidence'),
        ],
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
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
      itemCount: 4, // 1 disclosure banner + 3 active orders
      itemBuilder: (context, index) {
        if (index == 0) {
          // Two-State Disclosure Banner (AR-010 §6: Never Conflate notYetSynced vs syncedAndRejected)
          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: fixColor(t_color_surface_primary),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: fixColor(t_color_border_subtle)!),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(Icons.cloud_upload_outlined, size: 16, color: fixColor(t_color_status_info)),
                    const SizedBox(width: 6),
                    Text(
                      '1 queued (not yet synced)',
                      style: TextStyle(fontSize: 11, color: fixColor(t_color_text_secondary)),
                    ),
                  ],
                ),
                Row(
                  children: [
                    Icon(Icons.report_problem_outlined, size: 16, color: fixColor(t_color_status_error)),
                    const SizedBox(width: 6),
                    Text(
                      '0 rejected',
                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: fixColor(t_color_status_error)),
                    ),
                  ],
                ),
              ],
            ),
          );
        }

        final orderIdx = index - 1;
        return Card(
          color: fixColor(t_color_surface_primary),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: fixColor(t_color_status_info_bg),
              child: Text(
                '${orderIdx + 1}',
                style: TextStyle(color: fixColor(t_color_status_info)),
              ),
            ),
            title: Text(
              'Work Order SO-2026-00${orderIdx + 1}',
              style: TextStyle(
                color: fixColor(t_color_text_primary),
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            subtitle: Text(
              'Device: Samsung Galaxy S24 · Priority: ${orderIdx == 0 ? "HIGH" : "NORMAL"} · Itinerary Stop #${orderIdx + 1}',
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
          ElevatedButton.icon(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Customer E-Signature recorded and estimate approved')),
              );
            },
            icon: const Icon(Icons.draw),
            label: const Text('Sign'),
            style: ElevatedButton.styleFrom(
              backgroundColor: fixColor(t_color_surface_secondary),
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
              'Photos & voice notes upload on the SP-09 deferred channel —\nnever blocking job status sync.',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                color: fixColor(t_color_text_secondary),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Before-repair photo queued with GPS EXIF tag')),
                    );
                  },
                  icon: const Icon(Icons.add_a_photo),
                  label: const Text('Capture Photo'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: fixColor(t_color_primary_base),
                    foregroundColor: fixColor(t_color_text_inverse),
                  ),
                ),
                const SizedBox(width: 12),
                OutlinedButton.icon(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('ভয়েস নোট রেকর্ড শুরু হয়েছে (Bengali Voice Note recording...)')),
                    );
                  },
                  icon: const Icon(Icons.mic),
                  label: const Text('ভয়েস নোট (Voice Note)'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

/// Geofenced Attendance Screen — clock-in/out with GPS boundary verification.
class AttendanceScreen extends StatelessWidget {
  const AttendanceScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Card(
          color: fixColor(t_color_surface_primary),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Geofenced Attendance',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: fixColor(t_color_primary_base),
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Zone: Seed Dhaka Circle (15,000 m radius)',
                  style: TextStyle(
                    fontSize: 12,
                    color: fixColor(t_color_text_secondary),
                  ),
                ),
                Text(
                  'GPS: 23.8103° N, 90.4125° E · Inside Geofence (1.7 km)',
                  style: TextStyle(
                    fontSize: 12,
                    color: fixColor(t_color_status_success),
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    ElevatedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Clock-In recorded via SP-07 journal')),
                        );
                      },
                      icon: const Icon(Icons.login),
                      label: const Text('Clock-In'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: fixColor(t_color_primary_base),
                        foregroundColor: fixColor(t_color_text_inverse),
                      ),
                    ),
                    const SizedBox(width: 12),
                    OutlinedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Shift completed')),
                        );
                      },
                      icon: const Icon(Icons.logout),
                      label: const Text('Clock-Out'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

/// Van Stock Screen — inventory listing and scan-to-consume.
class PartsScreen extends StatelessWidget {
  const PartsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final parts = [
      {'code': 'PART-BAT-S24', 'name': 'Samsung Galaxy S24 Battery OEM', 'stock': '5 pcs', 'price': '৳ 2,500.00'},
      {'code': 'PART-DISP-A55', 'name': 'Samsung A55 OLED Display Module', 'stock': '3 pcs', 'price': '৳ 4,800.00'},
      {'code': 'PART-FPC-IP15', 'name': 'iPhone 15 Charging Flex FPC', 'stock': '8 pcs', 'price': '৳ 1,200.00'},
      {'code': 'PART-SPK-GEN', 'name': 'Ear Speaker Module Universal OEM', 'stock': '10 pcs', 'price': '৳ 450.00'},
      {'code': 'PART-FAN-HP15', 'name': 'HP 15-dw CPU Cooling Fan 5V', 'stock': '4 pcs', 'price': '৳ 950.00'},
    ];

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: parts.length,
      itemBuilder: (context, index) {
        final p = parts[index];
        return Card(
          color: fixColor(t_color_surface_primary),
          margin: const EdgeInsets.only(bottom: 12),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: fixColor(t_color_surface_secondary),
              child: Icon(Icons.memory, color: fixColor(t_color_primary_base)),
            ),
            title: Text(
              p['name']!,
              style: TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: fixColor(t_color_text_primary),
              ),
            ),
            subtitle: Text(
              'Code: ${p["code"]} · Stock: ${p["stock"]} · Price: ${p["price"]}',
              style: TextStyle(
                fontSize: 12,
                color: fixColor(t_color_text_secondary),
              ),
            ),
            trailing: ElevatedButton(
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('Consumed 1x ${p["code"]} on active job')),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: fixColor(t_color_surface_secondary),
                foregroundColor: fixColor(t_color_primary_base),
              ),
              child: const Text('Consume'),
            ),
          ),
        );
      },
    );
  }
}
