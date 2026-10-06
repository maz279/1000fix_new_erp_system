import 'dart:ui';

/// fixColor — the R4 bridge from generated token STRINGS to Dart Colors.
///
/// The token source emits `const String` values (DTCG parity across all five
/// realisations). Flutter apps must consume colours through this helper —
/// hand-authored hex literals in app code are a CFM-01 violation.
Color? fixColor(String? tokenHex) {
  if (tokenHex == null) return null;
  var h = tokenHex.replaceFirst('#', '').trim();
  if (h.length == 6) h = 'FF$h';
  if (h.length != 8) return null;
  final v = int.tryParse(h, radix: 16);
  if (v == null) return null;
  return Color(v);
}
