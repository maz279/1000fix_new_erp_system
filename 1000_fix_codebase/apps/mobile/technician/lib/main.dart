import 'package:flutter/material.dart';
import 'package:fix_ui/fix_color.dart';
import 'package:fix_ui/theme/tokens.dart';

/// PP1 scaffold proof: every colour comes from the generated token strings
/// (t_* constants) via fixColor() — no hand-authored hex (CFM-01).
/// Live screens land with PP4.
void main() => runApp(const _App());

class _App extends StatelessWidget {
  const _App();

  @override
  Widget build(BuildContext context) {
    final brand = fixColor(t_color_primary_base)!;
    return MaterialApp(
      title: 'P02 Technician',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: brand),
        scaffoldBackgroundColor: fixColor(t_color_surface_canvas),
      ),
      home: Scaffold(
        body: Center(
          child: Text(
            'P02 Technician — PP1 scaffold',
            style: TextStyle(color: fixColor(t_color_text_primary)),
          ),
        ),
      ),
    );
  }
}
