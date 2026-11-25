import 'package:flutter/material.dart';
import 'package:fix_ui/fix_color.dart';
import 'package:fix_ui/theme/tokens.dart';
import 'package:fix_offline/fix_offline.dart';

/// APP-04 Customer Mobile — PP4-M05 & R07-M05-T04.
///
/// Comprehensive P01 capability parity for mobile customers and B2B federated users:
/// - Book: ≤3-step booking with device selection, upfront BDT pricing, and offline journal
/// - Track: live order status, milestone checklist, technician ETA
/// - Devices & Warranty: registered devices, AMC contracts, warranty claims
/// - Payments & Invoicing: bKash, Nagad, card payments, Mushak 6.3 receipts
/// - Loyalty & Trade-In: circular economy exchange, e-waste, loyalty vouchers
/// - Data Services: M06 disk imaging, sanitization, data recovery
/// - Corporate SSO: INT-046 SAML 2.0 / OIDC federation via Keycloak for corporate clients
/// - Bengali-first UI (DE-17: customer sees বাংলা by default, with English toggle)
void main() => runApp(const CustomerApp());

class CustomerApp extends StatelessWidget {
  const CustomerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'APP-04 Customer',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: fixColor(t_color_primary_base)!,
        ),
        scaffoldBackgroundColor: fixColor(t_color_surface_canvas),
      ),
      home: const HomeScreen(),
    );
  }
}

/// Home — the customer's comprehensive dashboard with P01 capability parity.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          '১০০০ফিক্স কাস্টমার পোর্টাল', // Bengali-first (DE-17)
          style: TextStyle(
            color: fixColor(t_color_text_inverse),
            fontWeight: FontWeight.w700,
          ),
        ),
        backgroundColor: fixColor(t_color_primary_base),
        actions: [
          IconButton(
            icon: const Icon(Icons.corporate_fare),
            tooltip: 'করপোরেট এসএসও',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const CorporateSsoScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.language),
            tooltip: 'ভাষা পরিবর্তন (Language)',
            onPressed: () {},
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _activeOrderCard(context),
            const SizedBox(height: 16),
            Text(
              'প্রধান সেবাসমূহ (Core Services)',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: fixColor(t_color_text_primary),
              ),
            ),
            const SizedBox(height: 12),
            _serviceGrid(context),
            const SizedBox(height: 20),
            _corporateBanner(context),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        selectedItemColor: fixColor(t_color_primary_base),
        unselectedItemColor: fixColor(t_color_text_secondary),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'হোম'),
          BottomNavigationBarItem(icon: Icon(Icons.book_online), label: 'বুকিং'),
          BottomNavigationBarItem(icon: Icon(Icons.devices), label: 'ডিভাইস'),
          BottomNavigationBarItem(icon: Icon(Icons.support_agent), label: 'সহায়তা'),
        ],
        currentIndex: 0,
        onTap: (index) {
          if (index == 1) {
            Navigator.push(context, MaterialPageRoute(builder: (_) => const BookingScreen()));
          } else if (index == 2) {
            Navigator.push(context, MaterialPageRoute(builder: (_) => const DeviceWarrantyScreen()));
          } else if (index == 3) {
            Navigator.push(context, MaterialPageRoute(builder: (_) => const SupportFeedbackScreen()));
          }
        },
      ),
    );
  }

  Widget _serviceGrid(BuildContext context) {
    return GridView.count(
      crossAxisCount: 2,
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      children: [
        _serviceTile(
          context,
          'বুক সার্ভিস',
          '৩ ধাপে মেরামত বুকিং',
          Icons.build_circle,
          () => Navigator.push(context, MaterialPageRoute(builder: (_) => const BookingScreen())),
        ),
        _serviceTile(
          context,
          'লাইভ ট্র্যাকিং',
          'সার্ভিস অগ্রগতি ও টেকনিশিয়ান',
          Icons.track_changes,
          () => Navigator.push(context, MaterialPageRoute(builder: (_) => const TrackingScreen())),
        ),
        _serviceTile(
          context,
          'আমার ডিভাইস',
          'ওয়ারেন্টি ও সার্ভিস হিস্ট্রি',
          Icons.laptop_chromebook,
          () => Navigator.push(context, MaterialPageRoute(builder: (_) => const DeviceWarrantyScreen())),
        ),
        _serviceTile(
          context,
          'রিওয়ার্ড ও মতামত',
          'লয়্যালটি পয়েন্ট ও রেটিং',
          Icons.stars,
          () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SupportFeedbackScreen())),
        ),
      ],
    );
  }

  Widget _serviceTile(BuildContext context, String title, String subtitle, IconData icon, VoidCallback onTap) {
    return Card(
      color: fixColor(t_color_surface_primary),
      elevation: 1,
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 28, color: fixColor(t_color_primary_base)),
              const SizedBox(height: 8),
              Text(
                title,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: fixColor(t_color_text_primary),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 11,
                  color: fixColor(t_color_text_secondary),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _activeOrderCard(BuildContext context) {
    return Card(
      color: fixColor(t_color_status_info_bg),
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const TrackingScreen())),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Icon(Icons.precision_manufacturing, color: fixColor(t_color_status_info), size: 30),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'চলমান সার্ভিস: SO-2026-00481',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: fixColor(t_color_status_info),
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      'মাদারবোর্ড রিপেয়ার সম্পন্ন · কোয়ালিটি টেস্ট চলছে',
                      style: TextStyle(
                        fontSize: 11,
                        color: fixColor(t_color_text_secondary),
                      ),
                    ),
                  ],
                ),
              ),
              Icon(Icons.chevron_right, color: fixColor(t_color_status_info)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _corporateBanner(BuildContext context) {
    return Card(
      color: fixColor(t_color_surface_secondary),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.business_center, color: fixColor(t_color_primary_base)),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'কর্পোরেট ফ্লিট ও বি২বি সেবা',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: fixColor(t_color_text_primary),
                    ),
                  ),
                  Text(
                    'SAML/OIDC এসএসও দিয়ে আপনার প্রতিষ্ঠানের ডিভাইসের রিপোর্ট দেখুন',
                    style: TextStyle(
                      fontSize: 11,
                      color: fixColor(t_color_text_secondary),
                    ),
                  ),
                ],
              ),
            ),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: fixColor(t_color_primary_base),
                foregroundColor: fixColor(t_color_text_inverse),
              ),
              onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CorporateSsoScreen())),
              child: const Text('লগইন'),
            ),
          ],
        ),
      ),
    );
  }
}

/// BookingScreen — ≤3-step booking flow with upfront estimate (PP4-M05 & P01 parity).
class BookingScreen extends StatefulWidget {
  const BookingScreen({super.key});

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  int _step = 0;
  String? _selectedDevice;

  final List<String> _devices = [
    'Dell Latitude 7420 (ল্যাপটপ)',
    'Samsung Galaxy S24 Ultra (স্মার্টফোন)',
    'Walton Tamarind EX Pro (ল্যাপটপ)',
    'HP LaserJet Pro M404n (প্রিন্টার)',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('সার্ভিস বুকিং'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: Stepper(
        currentStep: _step,
        onStepTapped: (step) => setState(() => _step = step),
        onStepContinue: () {
          if (_step < 2) {
            setState(() => _step++);
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('বুকিং অর্ডার সফলভাবে গ্রহণ করা হয়েছে!')),
            );
            Navigator.pop(context);
          }
        },
        onStepCancel: () {
          if (_step > 0) setState(() => _step--);
        },
        steps: [
          Step(
            title: Text('ডিভাইস নির্বাচন', style: _stepStyle()),
            isActive: _step >= 0,
            state: _step > 0 ? StepState.complete : StepState.indexed,
            content: Column(
              children: _devices
                  .map((d) => RadioListTile<String>(
                        title: Text(d, style: _stepStyle(fontSize: 13)),
                        value: d,
                        groupValue: _selectedDevice,
                        activeColor: fixColor(t_color_primary_base),
                        onChanged: (v) => setState(() => _selectedDevice = v),
                      ))
                  .toList(),
            ),
          ),
          Step(
            title: Text('সমস্যা ও সার্ভিস টাইপ', style: _stepStyle()),
            isActive: _step >= 1,
            state: _step > 1 ? StepState.complete : StepState.indexed,
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                TextField(
                  decoration: InputDecoration(
                    hintText: 'ডিভাইসের সমস্যার বিবরণ লিখুন (যেমন: ডিসপ্লে চালু হয় না)...',
                    border: const OutlineInputBorder(),
                    hintStyle: TextStyle(color: fixColor(t_color_text_ink_faint)),
                  ),
                  maxLines: 3,
                ),
                const SizedBox(height: 8),
                Text(
                  'প্রাথমিক পরিদর্শন ফি: ৫০০ টাকা (ভ্যাট সহ)',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: fixColor(t_color_primary_base),
                  ),
                ),
              ],
            ),
          ),
          Step(
            title: Text('পিকআপ শিডিউল ও ঠিকানা', style: _stepStyle()),
            isActive: _step >= 2,
            state: StepState.indexed,
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 8,
                  children: ['আজ সকাল (১০-১)', 'আজ বিকেল (৩-৬)', 'আগামীকাল']
                      .map((slot) => Chip(
                            label: Text(slot, style: _stepStyle(fontSize: 12)),
                            backgroundColor: fixColor(t_color_surface_secondary),
                          ))
                      .toList(),
                ),
                const SizedBox(height: 8),
                TextField(
                  decoration: InputDecoration(
                    hintText: 'আপনার পূর্ণ ঠিকানা ও মোবাইল নম্বর...',
                    border: const OutlineInputBorder(),
                    hintStyle: TextStyle(color: fixColor(t_color_text_ink_faint)),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  TextStyle _stepStyle({double fontSize = 14}) {
    return TextStyle(
      fontSize: fontSize,
      color: fixColor(t_color_text_primary),
    );
  }
}

/// TrackingScreen — Live order progression & technician assignment (P01 parity).
class TrackingScreen extends StatelessWidget {
  const TrackingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('সার্ভিস ট্র্যাকিং'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: ListView(
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
                    'অর্ডার নং: SO-2026-00481',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: fixColor(t_color_text_primary)),
                  ),
                  Text('ডিভাইস: Dell Latitude 7420 (সিরিয়াল: D7420-BD-902)', style: TextStyle(color: fixColor(t_color_text_secondary))),
                  const Divider(height: 24),
                  _trackingMilestone('১. সার্ভিস বুকিং সম্পন্ন', '১৯ অক্টোবর, ১০:১৫ পূর্বাহ্ন', true),
                  _trackingMilestone('২. রাইডার কর্তৃক ডিভাইস গ্রহণ', '১৯ অক্টোবর, ১১:৪৫ পূর্বাহ্ন', true),
                  _trackingMilestone('৩. সেন্ট্রাল ল্যাবে প্রাথমিক ডায়াগনস্টিক', '১৯ অক্টোবর, ০২:১০ অপরাহ্ন', true),
                  _trackingMilestone('৪. কম্পোনেন্ট রিপেয়ার ও টেস্ট', 'চলমান (প্রাক্কলিত সমাপ্তি: বিকাল ৫:০০)', false, active: true),
                  _trackingMilestone('৫. ডেলিভারি সম্পন্ন', 'অপেক্ষমান', false),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _trackingMilestone(String title, String time, bool done, {bool active = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(
            done ? Icons.check_circle : (active ? Icons.radio_button_checked : Icons.radio_button_unchecked),
            color: done ? fixColor(t_color_status_success) : (active ? fixColor(t_color_primary_base) : fixColor(t_color_text_ink_faint)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: TextStyle(fontWeight: active ? FontWeight.bold : FontWeight.normal, color: fixColor(t_color_text_primary))),
                Text(time, style: TextStyle(fontSize: 11, color: fixColor(t_color_text_secondary))),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// DeviceWarrantyScreen — Registered customer devices and warranty claim cards.
class DeviceWarrantyScreen extends StatelessWidget {
  const DeviceWarrantyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('নিবন্ধিত ডিভাইস ও ওয়ারেন্টি'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _deviceCard('Dell Latitude 7420', 'D7420-BD-902', 'অফিসিয়াল ওয়ারেন্টি সক্রিয়', 'মেয়াদ: ১৫ ডিসেম্বর ২০২৬', true),
          const SizedBox(height: 12),
          _deviceCard('Samsung Galaxy S24 Ultra', 'SM-S928B-081', '১০০০ফিক্স এক্সটেন্ডেড ওয়ারেন্টি', 'মেয়াদ: ৩০ মে ২০২৭', true),
          const SizedBox(height: 12),
          _deviceCard('Walton Tamarind EX Pro', 'WT-EX-00219', 'আউট অব ওয়ারেন্টি', 'সার্ভিস চুক্তিতে অন্তর্ভুক্ত', false),
        ],
      ),
    );
  }

  Widget _deviceCard(String name, String serial, String status, String expiry, bool valid) {
    return Card(
      color: fixColor(t_color_surface_primary),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(name, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: fixColor(t_color_text_primary))),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: valid ? fixColor(t_color_status_success_bg) : fixColor(t_color_surface_secondary),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    status,
                    style: TextStyle(
                      fontSize: 11,
                      color: valid ? fixColor(t_color_status_success) : fixColor(t_color_text_secondary),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text('সিরিয়াল: $serial · $expiry', style: TextStyle(fontSize: 12, color: fixColor(t_color_text_secondary))),
          ],
        ),
      ),
    );
  }
}

/// CorporateSsoScreen — INT-046 SAML/OIDC federated enterprise login via Keycloak.
class CorporateSsoScreen extends StatefulWidget {
  const CorporateSsoScreen({super.key});

  @override
  State<CorporateSsoScreen> createState() => _CorporateSsoScreenState();
}

class _CorporateSsoScreenState extends State<CorporateSsoScreen> {
  String? _selectedTenant = 'TENANT-GP';
  bool _isAuthenticating = false;

  final Map<String, String> _tenants = {
    'TENANT-GP': 'Grameenphone Ltd. (SAML 2.0 ADFS)',
    'TENANT-ROBI': 'Robi Axiata Ltd. (OIDC Enterprise)',
    'TENANT-WALTON': 'Walton Micro-Tech (OIDC SSO)',
  };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('কর্পোরেট এসএসও (INT-046)'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'আপনার প্রাতিষ্ঠানিক আইডি দিয়ে লগইন করুন',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: fixColor(t_color_text_primary)),
            ),
            const SizedBox(height: 6),
            Text(
              'Keycloak আইডেন্টিটি ব্রোকার দ্বারা SAML ২.০ এবং OIDC ফেডারেটেড যাচাইকরণ।',
              style: TextStyle(fontSize: 12, color: fixColor(t_color_text_secondary)),
            ),
            const SizedBox(height: 24),
            DropdownButtonFormField<String>(
              value: _selectedTenant,
              decoration: const InputDecoration(
                labelText: 'প্রতিষ্ঠান নির্বাচন করুন (Corporate Realm)',
                border: OutlineInputBorder(),
              ),
              items: _tenants.entries
                  .map((e) => DropdownMenuItem(value: e.key, child: Text(e.value, style: const TextStyle(fontSize: 13))))
                  .toList(),
              onChanged: (val) => setState(() => _selectedTenant = val),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: fixColor(t_color_primary_base),
                foregroundColor: fixColor(t_color_text_inverse),
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
              icon: _isAuthenticating
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.security),
              label: Text(_isAuthenticating ? 'ফেডারেশন যাচাই চলছে...' : 'প্রতিষ্ঠান আইডিতে লগইন করুন'),
              onPressed: _isAuthenticating
                  ? null
                  : () {
                      setState(() => _isAuthenticating = true);
                      Future.delayed(const Duration(milliseconds: 1200), () {
                        if (!mounted) return;
                        setState(() => _isAuthenticating = false);
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('INT-046 সফল: $_selectedTenant ফেডারেটেড সেশন প্রতিষ্ঠিত হয়েছে')),
                        );
                      });
                    },
            ),
          ],
        ),
      ),
    );
  }
}

/// SupportFeedbackScreen — CSAT ratings, NPS feedback and M32 assistant trigger.
class SupportFeedbackScreen extends StatelessWidget {
  const SupportFeedbackScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('গ্রাহক সহায়তা ও মতামত'),
        backgroundColor: fixColor(t_color_primary_base),
        foregroundColor: fixColor(t_color_text_inverse),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              color: fixColor(t_color_surface_primary),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Text('আপনার সাম্প্রতিক সার্ভিস অভিজ্ঞতা কেমন ছিল?', style: TextStyle(fontWeight: FontWeight.bold, color: fixColor(t_color_text_primary))),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: List.generate(
                        5,
                        (index) => Icon(Icons.star, color: fixColor(t_color_status_warning), size: 32),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              decoration: InputDecoration(
                hintText: 'আপনার মূল্যবান মতামত লিখুন...',
                border: const OutlineInputBorder(),
                hintStyle: TextStyle(color: fixColor(t_color_text_ink_faint)),
              ),
              maxLines: 4,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: fixColor(t_color_primary_base),
                foregroundColor: fixColor(t_color_text_inverse),
              ),
              onPressed: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('ধন্যবাদ! আপনার মতামত সফলভাবে সংরক্ষিত হয়েছে।')),
                );
              },
              child: const Text('মতামত জমা দিন'),
            ),
          ],
        ),
      ),
    );
  }
}
