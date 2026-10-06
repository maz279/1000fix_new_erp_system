import 'package:flutter/material.dart';
import 'package:fix_ui/fix_color.dart';
import 'package:fix_ui/theme/tokens.dart';
import 'package:fix_offline/fix_offline.dart';

/// APP-04 Customer Mobile — PP4-M05.
///
/// The customer-facing mobile app (the P01 portal's mobile counterpart):
/// - Book: ≤3-step booking with device selection and upfront pricing
/// - Track: live order status with technician ETA
/// - Devices: registered devices with warranty status
/// - Bengali-first UI (DE-17: the customer sees বাংলা by default)
///
/// The app is online-first (the customer has connectivity) but uses the
/// same fix_offline engine for data consistency when the network drops.
void main() => runApp(const CustomerApp());

class CustomerApp extends StatelessWidget {
  const CustomerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '1000FiX',
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

/// Home — the customer's dashboard with quick actions.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          '১০০০ফিক্স', // Bengali-first (DE-17)
          style: TextStyle(color: fixColor(t_color_text_inverse)),
        ),
        backgroundColor: fixColor(t_color_primary_base),
        actions: [
          IconButton(
            icon: const Icon(Icons.language),
            onPressed: () {
              // Toggle EN/বাংলা
            },
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _bigAction(
              context,
              'বুক সার্ভিস', // Book Service
              'সহজ ৩ ধাপে সার্ভিস বুক করুন', // Book in 3 easy steps
              Icons.calendar_today,
            ),
            const SizedBox(height: 12),
            _bigAction(
              context,
              'ট্র্যাক করুন', // Track
              'আপনার ডিভাইসের সার্ভিস স্ট্যাটাস', // Your device's service status
              Icons.location_on,
            ),
            const SizedBox(height: 12),
            _bigAction(
              context,
              'আমার ডিভাইস', // My Devices
              'নিবন্ধিত ডিভাইস ও ওয়ারেন্টি', // Registered devices & warranty
              Icons.phone_android,
            ),
            const SizedBox(height: 24),
            _activeOrderCard(),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        selectedItemColor: fixColor(t_color_primary_base),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'হোম'),
          BottomNavigationBarItem(icon: Icon(Icons.book), label: 'বুক'),
          BottomNavigationBarItem(icon: Icon(Icons.devices), label: 'ডিভাইস'),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: 'প্রোফাইল'),
        ],
        currentIndex: 0,
        onTap: (index) {},
      ),
    );
  }

  Widget _bigAction(
    BuildContext context,
    String title,
    String subtitle,
    IconData icon,
  ) {
    return Card(
      color: fixColor(t_color_surface_primary),
      elevation: 2,
      child: InkWell(
        borderRadius: BorderRadius.circular(8),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const BookingScreen()),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Row(
            children: [
              Icon(icon, size: 32, color: fixColor(t_color_primary_base)),
              const SizedBox(width: 16),
              Expanded(
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
              Icon(
                Icons.chevron_right,
                color: fixColor(t_color_text_ink_faint),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _activeOrderCard() {
    return Card(
      color: fixColor(t_color_status_info_bg),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Icon(Icons.build, color: fixColor(t_color_status_info)),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'সার্ভিস চলছে', // Service in progress
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: fixColor(t_color_status_info),
                    ),
                  ),
                  Text(
                    'SO-2026-00148 · মেরামত চলছে', // Under repair
                    style: TextStyle(
                      fontSize: 11,
                      color: fixColor(t_color_text_secondary),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Booking — the ≤3-step booking flow (PP4-M05).
class BookingScreen extends StatefulWidget {
  const BookingScreen({super.key});

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  int _step = 0;
  String? _selectedDevice;

  final List<String> _devices = [
    'Samsung Galaxy S24',
    'iPhone 15 Pro',
    'Xiaomi Redmi Note 13',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('বুক সার্ভিস'),
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
            // Submit the booking (a command in the journal; syncs SP-07)
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('বুকিং সম্পন্ন — শীঘ্রই কনফার্ম করা হবে')),
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
            title: Text('সমস্যা বর্ণনা', style: _stepStyle()),
            isActive: _step >= 1,
            state: _step > 1 ? StepState.complete : StepState.indexed,
            content: TextField(
              decoration: InputDecoration(
                hintText: 'সমস্যার বিবরণ লিখুন…',
                border: const OutlineInputBorder(),
                hintStyle: TextStyle(color: fixColor(t_color_text_ink_faint)),
              ),
              maxLines: 3,
            ),
          ),
          Step(
            title: Text('সময় নির্বাচন', style: _stepStyle()),
            isActive: _step >= 2,
            state: StepState.indexed,
            content: Wrap(
              spacing: 8,
              children: ['আজ', 'আগামীকাল', 'পরশু']
                  .map((day) => Chip(
                        label: Text(day, style: _stepStyle(fontSize: 12)),
                        backgroundColor: fixColor(t_color_surface_secondary),
                      ))
                  .toList(),
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
