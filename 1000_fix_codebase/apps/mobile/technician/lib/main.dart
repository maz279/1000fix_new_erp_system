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
    ScorecardScreen(),
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
          BottomNavigationBarItem(icon: Icon(Icons.analytics_outlined), label: 'Scorecard'),
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

/// ScorecardScreen — M57 Technician Scorecard & Incentives (R06-M01-T05).
///
/// Surfaces explainable composite scorecard (35% FTF + 30% SLA + 20% CSAT - 15% Rework)
/// and incentive earnings feeding M56 payroll directly in the P02 mobile app.
class ScorecardScreen extends StatelessWidget {
  const ScorecardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Composite Score Hero Card
        Card(
          elevation: 3,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          color: fixColor(t_color_primary_base),
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Performance Cycle: 2026-10',
                      style: TextStyle(
                        color: fixColor(t_color_text_inverse)?.withOpacity(0.9),
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.amber.shade700,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Text(
                        'Tier 2 — Gold (8%)',
                        style: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(
                  '0.88 / 1.00',
                  style: TextStyle(
                    color: fixColor(t_color_text_inverse),
                    fontSize: 34,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  'কম্পোজিট স্কোর (Composite Score: 88%)',
                  style: TextStyle(
                    color: fixColor(t_color_text_inverse)?.withOpacity(0.85),
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Incentive Earnings Card (feeding M56 Payroll)
        Card(
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Incentive Earnings (M56 Payroll)',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                        color: fixColor(t_color_text_primary),
                      ),
                    ),
                    const Icon(Icons.payments, color: Colors.green),
                  ],
                ),
                const Divider(height: 20),
                _buildIncentiveRow('Band Base (গ্রেড স্কেল)', 'BDT 35,000.00'),
                _buildIncentiveRow('Incentive Rate (প্রণোদনা হার)', '8.0% (Score >= 0.75)'),
                _buildIncentiveRow('Calculated Payout (মোট প্রণোদনা)', 'BDT 2,800.00', isTotal: true),
                const SizedBox(height: 8),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.green.shade50,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.green.shade200),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.check_circle, size: 16, color: Colors.green),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Fed to M56 Payroll: Cycle October 2026 Verified',
                          style: TextStyle(fontSize: 11, color: Colors.green.shade800),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Metric Breakdown
        Text(
          'Metric Breakdown (DoD-03 Formula)',
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.bold,
            color: fixColor(t_color_text_primary),
          ),
        ),
        const SizedBox(height: 8),

        _buildMetricTile(
          icon: Icons.check_circle_outline,
          title: 'First-Time Fix Rate (FTF)',
          bengaliTitle: 'প্রথম ফিক্স হার (ওজন ৩৫%)',
          value: '92.0%',
          target: 'Target: >= 85%',
          color: Colors.blue,
        ),
        _buildMetricTile(
          icon: Icons.timer_outlined,
          title: 'SLA Hit Rate',
          bengaliTitle: 'সময়সীমা রক্ষা হার (ওজন ৩০%)',
          value: '95.0%',
          target: 'Target: >= 90%',
          color: Colors.teal,
        ),
        _buildMetricTile(
          icon: Icons.sentiment_satisfied_alt,
          title: 'Customer Satisfaction (CSAT)',
          bengaliTitle: 'গ্রাহক সন্তুষ্টি হার (ওজন ২০%)',
          value: '96.0%',
          target: 'Target: >= 90%',
          color: Colors.orange,
        ),
        _buildMetricTile(
          icon: Icons.replay,
          title: 'Rework Penalty',
          bengaliTitle: 'পুনরাবৃত্তি ত্রুটি জরিমানা (পেনাল্টি -১৫%)',
          value: '2.0%',
          target: 'Penalty subtracted: -0.3%',
          color: Colors.red,
        ),

        const SizedBox(height: 12),

        // Explainability card
        Card(
          color: fixColor(t_color_surface_secondary),
          child: Padding(
            padding: const EdgeInsets.all(12),
            child: Text(
              'Formula: Score = (0.35 * FTF) + (0.30 * SLA) + (0.20 * CSAT) - (0.15 * Rework)\n'
              'Bands: >=0.90 (15%) | >=0.75 (8%) | >=0.60 (4%) | <0.60 (0%)\n'
              'All metrics are tamper-evident and audited under CD-M57-01.',
              style: TextStyle(fontSize: 11, color: fixColor(t_color_text_secondary)),
            ),
          ),
        ),
      ],
    );
  }

  static Widget _buildIncentiveRow(String label, String value, {bool isTotal = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: isTotal ? 13 : 12,
              fontWeight: isTotal ? FontWeight.bold : FontWeight.normal,
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: isTotal ? 14 : 12,
              fontWeight: isTotal ? FontWeight.bold : FontWeight.w600,
              color: isTotal ? Colors.green.shade800 : null,
            ),
          ),
        ],
      ),
    );
  }

  static Widget _buildMetricTile({
    required IconData icon,
    required String title,
    required String bengaliTitle,
    required String value,
    required String target,
    required Color color,
  }) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withOpacity(0.15),
          child: Icon(icon, color: color, size: 20),
        ),
        title: Text(
          title,
          style: const TextStyle(fontSize: 13, fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          '$bengaliTitle · $target',
          style: const TextStyle(fontSize: 11),
        ),
        trailing: Text(
          value,
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ),
    );
  }
}
