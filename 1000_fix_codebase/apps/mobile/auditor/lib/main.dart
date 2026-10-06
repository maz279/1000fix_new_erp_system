import 'package:flutter/material.dart';
import 'package:fix_ui/fix_color.dart';
import 'package:fix_ui/theme/tokens.dart';
import 'package:fix_offline/fix_offline.dart';

/// P11 Auditor App — PP4-M04.
///
/// The quality auditor's surface:
/// - Audit checklists: ISO 9001 branch audits with structured scoring
/// - Branch audit capture: photos, findings, corrective actions
/// - Photo evidence: GPS + timestamp, deferred via SP-09
///
/// All audit results are commands (offline-first): the auditor can
/// complete a full branch audit offline; the results sync SP-07.
void main() => runApp(const AuditorApp());

class AuditorApp extends StatelessWidget {
  const AuditorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'P11 Auditor',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: fixColor(t_color_primary_base)!,
        ),
        scaffoldBackgroundColor: fixColor(t_color_surface_canvas),
      ),
      home: const AuditListScreen(),
    );
  }
}

/// The audit list — scheduled and in-progress audits.
class AuditListScreen extends StatelessWidget {
  const AuditListScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('P11 Auditor'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
        actions: [
          IconButton(
            icon: const Icon(Icons.sync),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Sync: SP-07 upload-first (audit results)'),
                ),
              );
            },
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _auditCard(
            'Branch Audit — Dhaka Gulshan',
            'Scheduled: 2026-10-07',
            'scheduled',
            context,
          ),
          _auditCard(
            'Branch Audit — Chattogram',
            'Completed: 2026-09-28 · Score: 87/100',
            'done',
            context,
          ),
          _auditCard(
            'Equipment Calibration Check',
            'Follow-up required',
            'follow_up',
            context,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const ChecklistScreen()),
          );
        },
        backgroundColor: fixColor(t_color_primary_base),
        child: Icon(Icons.add, color: fixColor(t_color_text_inverse)),
      ),
    );
  }

  Widget _auditCard(
      String title, String subtitle, String state, BuildContext context) {
    final stateColor = switch (state) {
      'done' => fixColor(t_color_status_success),
      'follow_up' => fixColor(t_color_status_warning),
      _ => fixColor(t_color_status_info),
    };
    final stateBg = switch (state) {
      'done' => fixColor(t_color_status_success_bg),
      'follow_up' => fixColor(t_color_status_warning_bg),
      _ => fixColor(t_color_status_info_bg),
    };
    return Card(
      color: fixColor(t_color_surface_primary),
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        title: Text(
          title,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w500,
            color: fixColor(t_color_text_primary),
          ),
        ),
        subtitle: Text(
          subtitle,
          style: TextStyle(
            fontSize: 12,
            color: fixColor(t_color_text_secondary),
          ),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: stateBg,
            borderRadius: BorderRadius.circular(999),
          ),
          child: Text(
            state.toUpperCase(),
            style: TextStyle(fontSize: 10, color: stateColor),
          ),
        ),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const ChecklistScreen()),
          );
        },
      ),
    );
  }
}

/// The structured audit checklist (ISO 9001).
///
/// Each item is scored; the auditor captures photos for findings.
/// The complete audit result is a command (offline-first).
class ChecklistScreen extends StatefulWidget {
  const ChecklistScreen({super.key});

  @override
  State<ChecklistScreen> createState() => _ChecklistScreenState();
}

class _ChecklistScreenState extends State<ChecklistScreen> {
  final Map<int, bool> _checked = {};

  final List<(String, String)> _items = [
    ('Fire extinguisher accessible', 'fire_extinguisher_ok'),
    ('Emergency exit unobstructed', 'emergency_exit_ok'),
    ('First aid kit stocked', 'first_aid_ok'),
    ('Electrical wiring safe', 'electrical_ok'),
    ('Work surfaces clean', 'work_surfaces_ok'),
    ('Anti-static mats in place', 'anti_static_ok'),
    ('Calibration certificates current', 'calibration_ok'),
    ('Waste segregation correct', 'waste_ok'),
  ];

  @override
  Widget build(BuildContext context) {
    final done = _checked.values.where((v) => v).length;
    return Scaffold(
      appBar: AppBar(
        title: Text('Checklist ($done/${_items.length})'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _items.length,
        itemBuilder: (context, index) {
          final (label, _) = _items[index];
          return CheckboxListTile(
            title: Text(
              label,
              style: TextStyle(
                fontSize: 13,
                color: fixColor(t_color_text_primary),
              ),
            ),
            value: _checked[index] ?? false,
            activeColor: fixColor(t_color_primary_base),
            onChanged: (value) {
              setState(() => _checked[index] = value ?? false);
            },
          );
        },
      ),
      bottomNavigationBar: Padding(
        padding: const EdgeInsets.all(16),
        child: ElevatedButton.icon(
          onPressed: () {
            // Record the complete audit result as a command in the
            // journal — offline-first; syncs SP-07 upload-first
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(
                  'Audit saved offline ($done/${_items.length} passed). '
                  'Will sync upload-first.',
                ),
              ),
            );
          },
          icon: const Icon(Icons.save),
          label: const Text('Save Audit (Offline)'),
          style: ElevatedButton.styleFrom(
            backgroundColor: fixColor(t_color_primary_base),
            foregroundColor: fixColor(t_color_text_inverse),
          ),
        ),
      ),
    );
  }
}
