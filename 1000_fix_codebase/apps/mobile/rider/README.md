# P09 Rider (R4) — PP1 scaffold

Consumes the generated `fix_ui` tokens via a path dependency. Flutter SDK is
not installed on this workstation (PP1 pre-flight, 2026-10-06): `flutter
analyze` is **environment-blocked** here — run it on a machine with the fvm-
pinned Flutter 3.44 before merging PP4 work. The scaffold references only
`fix_ui/theme/tokens.dart` constants, never hand-authored colours.
