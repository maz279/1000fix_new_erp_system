import 'package:flutter/material.dart';
import 'package:fix_ui/fix_color.dart';
import 'package:fix_ui/theme/tokens.dart';
import 'package:fix_offline/fix_offline.dart';

/// P09 Rider App — PP4-M03 / R04-M02-T06.
///
/// The logistics rider's surface:
/// - Pickup: scan the consignment, confirm pickup from the branch
/// - Custody: unbroken chain-of-custody scans (every handoff is a scan)
/// - Delivery: confirm delivery to the customer with signature/OTP
/// - Route: today's manifest with optimized stops
///
/// WCAG 2.2 AA Compliance:
/// - Target size >= 48x48 on all touch controls
/// - Contrast ratio >= 4.5:1 on text elements
/// - Screen-reader semantic announcements via Semantics widgets
/// - Full bilingual Bengali (bn_BD) & English parity with dynamic toggle.
void main() => runApp(const RiderApp());

class LocaleNotifier extends ValueNotifier<String> {
  LocaleNotifier() : super('bn_BD');
  void toggle() => value = value == 'bn_BD' ? 'en' : 'bn_BD';
}

final riderLocaleNotifier = LocaleNotifier();

class RiderStrings {
  static const Map<String, Map<String, String>> localized = {
    'en': {
      'app_title': 'P09 Rider',
      'sync_tooltip': 'Synchronize offline journal',
      'sync_message': 'Sync: SP-07 upload-first (custody commands)',
      'manifest_title': "Today's Manifest",
      'manifest_subtitle': '6 stops · 12 packages · ~42 km',
      'stop1_title': 'Stop 1: Dhaka Branch — Pickup',
      'stop1_desc': 'Collect repaired appliances and batch consignments',
      'stop2_title': 'Stop 2: Gulshan Customer — Delivery',
      'stop2_desc': 'Delivery of repaired smartphone to customer',
      'stop3_title': 'Stop 3: Banani Customer — Delivery',
      'stop3_desc': 'Laptop return after workshop servicing',
      'stop4_title': 'Stop 4: Branch Return — Drop-off',
      'stop4_desc': 'Consignment return & intake scan',
      'pending': 'Pending',
      'custody_scan_title': 'Custody Scan',
      'custody_instruction': 'Scan the package barcode to confirm custody.\nEvery scan is recorded offline and syncs upload-first (SP-07).',
      'confirm_pickup': 'Confirm Pickup',
      'delivery_title': 'Confirm Delivery',
      'otp_heading': 'Customer Signature or OTP',
      'delivery_desc': 'The delivery confirmation is a command (offline-first). If the network is down, it queues in the journal.',
      'enter_otp': 'Enter customer OTP',
      'confirm_delivery': 'Confirm Delivery',
      'toggle_lang': 'বাংলা',
    },
    'bn_BD': {
      'app_title': 'P09 রাইডার পোর্টাল',
      'sync_tooltip': 'অফলাইন জার্নাল সিঙ্ক করুন',
      'sync_message': 'সিঙ্ক: SP-07 আপলোড-ফার্স্ট (কাস্টডি কমান্ড)',
      'manifest_title': 'আজকের ডেলিভারি তালিকা (মেনিফেস্ট)',
      'manifest_subtitle': '৬টি গন্তব্য · ১২টি পার্সেল · ~৪২ কি.মি.',
      'stop1_title': 'স্টপ ১: ঢাকা শাখা — পার্সেল সংগ্রহ (পিকআপ)',
      'stop1_desc': 'মেরামতকৃত সরঞ্জাম এবং ব্যাচ পার্সেল গ্রহণ',
      'stop2_title': 'স্টপ ২: গুলশান গ্রাহক — ডেলিভারি',
      'stop2_desc': 'গ্রাহকের নিকট মেরামতকৃত স্মার্টফোন হস্তান্তর',
      'stop3_title': 'স্টপ ৩: বনানী গ্রাহক — ডেলিভারি',
      'stop3_desc': 'ওয়ার্কশপ সার্ভিসিং শেষে ল্যাপটপ ফেরত প্রদান',
      'stop4_title': 'স্টপ ৪: শাখা ড্রপ-অফ — রিটার্ন',
      'stop4_desc': 'শাখা ট্রানজিট ও রিটার্ন ইনটেক স্ক্যান',
      'pending': 'অপেক্ষমান',
      'custody_scan_title': 'কাস্টডি স্ক্যান (হেফাজত যাচাই)',
      'custody_instruction': 'পার্সেল হেফাজত নিশ্চিত করতে বারকোড স্ক্যান করুন।\nপ্রতিটি স্ক্যান অফলাইনে সংরক্ষিত হয় এবং স্বয়ংক্রিয়ভাবে সিঙ্ক হয়।',
      'confirm_pickup': 'পিকআপ নিশ্চিত করুন',
      'delivery_title': 'ডেলিভারি নিশ্চিতকরণ',
      'otp_heading': 'গ্রাহক স্বাক্ষর বা ওটিপি (OTP)',
      'delivery_desc': 'ডেলিভারি নিশ্চিতকরণ একটি অফলাইন-ফার্স্ট কমান্ড। নেটওয়ার্ক না থাকলে এটি স্থানীয় জার্নালে সংরক্ষিত থাকবে।',
      'enter_otp': 'গ্রাহকের ওটিপি (OTP) লিখুন',
      'confirm_delivery': 'ডেলিভারি সম্পন্ন করুন',
      'toggle_lang': 'English',
    },
  };

  static String tr(String key, String lang) {
    return localized[lang]?[key] ?? localized['en']?[key] ?? key;
  }
}

class RiderApp extends StatelessWidget {
  const RiderApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<String>(
      valueListenable: riderLocaleNotifier,
      builder: (context, currentLang, _) {
        return MaterialApp(
          title: RiderStrings.tr('app_title', currentLang),
          theme: ThemeData(
            colorScheme: ColorScheme.fromSeed(
              seedColor: fixColor(t_color_primary_base)!,
            ),
            scaffoldBackgroundColor: fixColor(t_color_surface_canvas),
          ),
          home: ManifestScreen(currentLang: currentLang),
        );
      },
    );
  }
}

/// Today's manifest — the route view (PP4-M03-T03).
class ManifestScreen extends StatelessWidget {
  final String currentLang;
  const ManifestScreen({super.key, required this.currentLang});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(RiderStrings.tr('app_title', currentLang)),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
        actions: [
          Semantics(
            label: 'Change language',
            button: true,
            child: TextButton(
              style: TextButton.styleFrom(
                minimumSize: const Size(48, 48),
                foregroundColor: fixColor(t_color_text_inverse),
              ),
              onPressed: () => riderLocaleNotifier.toggle(),
              child: Text(
                RiderStrings.tr('toggle_lang', currentLang),
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ),
          Semantics(
            label: RiderStrings.tr('sync_tooltip', currentLang),
            button: true,
            child: IconButton(
              icon: const Icon(Icons.sync),
              tooltip: RiderStrings.tr('sync_tooltip', currentLang),
              constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(RiderStrings.tr('sync_message', currentLang)),
                  ),
                );
              },
            ),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _summaryCard(
            RiderStrings.tr('manifest_title', currentLang),
            RiderStrings.tr('manifest_subtitle', currentLang),
          ),
          const SizedBox(height: 8),
          _stopTile(context, RiderStrings.tr('stop1_title', currentLang),
              RiderStrings.tr('stop1_desc', currentLang), Icons.store, RiderStrings.tr('pending', currentLang)),
          _stopTile(context, RiderStrings.tr('stop2_title', currentLang),
              RiderStrings.tr('stop2_desc', currentLang), Icons.home, RiderStrings.tr('pending', currentLang)),
          _stopTile(context, RiderStrings.tr('stop3_title', currentLang),
              RiderStrings.tr('stop3_desc', currentLang), Icons.home, RiderStrings.tr('pending', currentLang)),
          _stopTile(context, RiderStrings.tr('stop4_title', currentLang),
              RiderStrings.tr('stop4_desc', currentLang), Icons.store, RiderStrings.tr('pending', currentLang)),
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

  Widget _stopTile(BuildContext context, String label, String subtitle, IconData icon, String state) {
    return Card(
      color: fixColor(t_color_surface_primary),
      child: Semantics(
        label: '$label: $subtitle, status: $state',
        button: true,
        child: ListTile(
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          leading: Icon(icon, color: fixColor(t_color_primary_base), size: 28),
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
              MaterialPageRoute(builder: (_) => CustodyScanScreen(currentLang: currentLang)),
            );
          },
        ),
      ),
    );
  }
}

/// Custody scan — every handoff is a scan; the chain must be unbroken.
class CustodyScanScreen extends StatelessWidget {
  final String currentLang;
  const CustodyScanScreen({super.key, required this.currentLang});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(RiderStrings.tr('custody_scan_title', currentLang)),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.qr_code_scanner,
                size: 72,
                color: fixColor(t_color_primary_base),
              ),
              const SizedBox(height: 16),
              Text(
                RiderStrings.tr('custody_instruction', currentLang),
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 13,
                  color: fixColor(t_color_text_secondary),
                ),
              ),
              const SizedBox(height: 32),
              Semantics(
                label: RiderStrings.tr('confirm_pickup', currentLang),
                button: true,
                child: ElevatedButton.icon(
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (_) => DeliveryConfirmScreen(currentLang: currentLang)),
                    );
                  },
                  icon: const Icon(Icons.check_circle),
                  label: Text(RiderStrings.tr('confirm_pickup', currentLang)),
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(200, 48),
                    backgroundColor: fixColor(t_color_primary_base),
                    foregroundColor: fixColor(t_color_text_inverse),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Delivery confirmation — signature or OTP to the customer (PP4-M03-T03).
class DeliveryConfirmScreen extends StatelessWidget {
  final String currentLang;
  const DeliveryConfirmScreen({super.key, required this.currentLang});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(RiderStrings.tr('delivery_title', currentLang)),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              RiderStrings.tr('otp_heading', currentLang),
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: fixColor(t_color_text_primary),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              RiderStrings.tr('delivery_desc', currentLang),
              style: TextStyle(
                fontSize: 12,
                color: fixColor(t_color_text_secondary),
              ),
            ),
            const SizedBox(height: 24),
            Semantics(
              label: RiderStrings.tr('enter_otp', currentLang),
              textField: true,
              child: TextField(
                decoration: InputDecoration(
                  labelText: RiderStrings.tr('enter_otp', currentLang),
                  border: const OutlineInputBorder(),
                  labelStyle: TextStyle(
                    color: fixColor(t_color_text_secondary),
                  ),
                ),
                keyboardType: TextInputType.number,
              ),
            ),
            const SizedBox(height: 24),
            Semantics(
              label: RiderStrings.tr('confirm_delivery', currentLang),
              button: true,
              child: ElevatedButton.icon(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(RiderStrings.tr('confirm_delivery', currentLang)),
                    ),
                  );
                },
                icon: const Icon(Icons.check_circle),
                label: Text(RiderStrings.tr('confirm_delivery', currentLang)),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(double.infinity, 48),
                  backgroundColor: fixColor(t_color_status_success),
                  foregroundColor: fixColor(t_color_text_inverse),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
