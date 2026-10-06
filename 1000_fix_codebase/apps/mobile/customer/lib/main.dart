import 'package:flutter/material.dart';
import 'package:fix_ui/fix_color.dart';
import 'package:fix_ui/theme/tokens.dart';

/// PP1 scaffold proof: every colour comes from the generated token strings
/// (t_* constants) via fixColor() — no hand-authored hex (CFM-01).
/// Live screens land with PP5.
void main() => runApp(const _App());

class _App extends StatelessWidget {
  const _App();

  @override
  Widget build(BuildContext context) {
    final brand = fixColor(t_color_primary_base)!;
    return MaterialApp(
      title: 'APP-04 Customer',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: brand),
        scaffoldBackgroundColor: fixColor(t_color_surface_canvas),
      ),
      home: Scaffold(
        body: Center(
          child: Text(
            'APP-04 Customer — PP1 scaffold',
            style: TextStyle(color: fixColor(t_color_text_primary)),
          ),
        ),
      ),
    );
  }
}
