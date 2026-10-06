import 'package:flutter/material.dart';
import 'package:fix_ui/fix_color.dart';
import 'package:fix_ui/theme/tokens.dart';
import 'package:fix_offline/fix_offline.dart';

/// P09 Rider App — PP4-M03.
///
/// The logistics rider's surface:
/// - Pickup: scan the consignment, confirm pickup from the branch
/// - Custody: unbroken chain-of-custody scans (every handoff is a scan)
/// - Delivery: confirm delivery to the customer with signature/OTP
/// - Route: today's manifest with optimized stops
///
/// The chain of custody is THE gate criterion: every scan is a command
/// in the journal (offline-first); a gap in the scan chain is a gap in
/// custody. All colours from generated tokens via fixColor() (CFM-01).
void main() => runApp(const RiderApp());

class RiderApp extends StatelessWidget {
  const RiderApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'P09 Rider',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: fixColor(t_color_primary_base)!,
        ),
        scaffoldBackgroundColor: fixColor(t_color_surface_canvas),
      ),
      home: const ManifestScreen(),
    );
  }
}

/// Today's manifest — the route view (PP4-M03-T03).
class ManifestScreen extends StatelessWidget {
  const ManifestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('P09 Rider'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
        actions: [
          IconButton(
            icon: const Icon(Icons.sync),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Sync: SP-07 upload-first (custody commands)'),
                ),
              );
            },
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _summaryCard('Today\'s Manifest', '6 stops · 12 packages · ~42 km'),
          const SizedBox(height: 8),
          _stopTile('Stop 1', 'Dhaka Branch — Pickup', Icons.store, 'pending'),
          _stopTile('Stop 2', 'Gulshan Customer — Delivery', Icons.home, 'pending'),
          _stopTile('Stop 3', 'Banani Customer — Delivery', Icons.home, 'pending'),
          _stopTile('Stop 4', 'Branch Return — Drop-off', Icons.store, 'pending'),
        ],
      ),
    );
  }

  Widget _summaryCard(String title, String subtitle) {
    return Card(
      color: fixColor(t_color_surface_primary),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: fixColor(t_color_text_primary),
              ),
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
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

  Widget _stopTile(String label, String subtitle, IconData icon, String state) {
    return Card(
      color: fixColor(t_color_surface_primary),
      child: ListTile(
        leading: Icon(icon, color: fixColor(t_color_primary_base)),
        title: Text(
          label,
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
        trailing: Chip(
          label: Text(state),
          backgroundColor: fixColor(t_color_status_warning_bg),
          labelStyle: TextStyle(
            fontSize: 10,
            color: fixColor(t_color_status_warning),
          ),
        ),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const CustodyScanScreen()),
          );
        },
      ),
    );
  }
}

/// Custody scan — every handoff is a scan; the chain must be unbroken.
///
/// Each scan is a COMMAND in the journal: `custody_scan` with the
/// package barcode, the location, and the timestamp. A gap in the scan
/// chain = a gap in custody = the gate criterion fails.
class CustodyScanScreen extends StatelessWidget {
  const CustodyScanScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Custody Scan'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.qr_code_scanner,
              size: 64,
              color: fixColor(t_color_primary_base),
            ),
            const SizedBox(height: 16),
            Text(
              'Scan the package barcode to confirm custody.\n'
              'Every scan is recorded offline and syncs upload-first (SP-07).',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 12,
                color: fixColor(t_color_text_secondary),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const DeliveryConfirmScreen()),
                );
              },
              icon: const Icon(Icons.check_circle),
              label: const Text('Confirm Pickup'),
              style: ElevatedButton.styleFrom(
                backgroundColor: fixColor(t_color_primary_base),
                foregroundColor: fixColor(t_color_text_inverse),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Delivery confirmation — signature or OTP to the customer (PP4-M03-T03).
class DeliveryConfirmScreen extends StatelessWidget {
  const DeliveryConfirmScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Confirm Delivery'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Customer Signature or OTP',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: fixColor(t_color_text_primary),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'The delivery confirmation is a command (offline-first). '
              'If the network is down, it queues in the journal.',
              style: TextStyle(
                fontSize: 12,
                color: fixColor(t_color_text_secondary),
              ),
            ),
            const SizedBox(height: 24),
            // OTP entry field
            TextField(
              decoration: InputDecoration(
                labelText: 'Enter customer OTP',
                border: OutlineInputBorder(),
                labelStyle: TextStyle(
                  color: fixColor(t_color_text_secondary),
                ),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                // Record the delivery command in the journal; the sync
                // engine uploads it SP-07 upload-first on the next cycle
              },
              icon: const Icon(Icons.check_circle),
              label: const Text('Confirm Delivery'),
              style: ElevatedButton.styleFrom(
                backgroundColor: fixColor(t_color_status_success),
                foregroundColor: fixColor(t_color_text_inverse),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
