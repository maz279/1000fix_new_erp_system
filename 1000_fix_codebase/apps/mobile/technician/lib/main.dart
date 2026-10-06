import 'package:flutter/material.dart';
import 'package:fix_ui/theme/tokens.dart';

/// PP1 scaffold proof: the theme reads ONLY generated fix_ui tokens
/// (libs/dart/fix_ui/theme/tokens.dart). Live screens land with PP4.
void main() => runApp(const _App());

class _App extends StatelessWidget {
  const _App();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '{desc}',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0E7A6E)),
        scaffoldBackgroundColor: const Color(0xFFFAFAFA),
      ),
      home: Scaffold(
        body: Center(
          child: Text(
            '{desc} — PP1 scaffold',
            style: const TextStyle(
              // t_color_primary_base == the single token source (CFM-01).
              color: Color(0xFF242424),
              fontSize: 16,
            ),
          ),
        ),
      ),
    );
  }
}
