/**
 * Moved 2026-10-23: the Service-Teal Fluent shell implementation now lives
 * per-app (apps/web/customer/components/shell-chrome.tsx) because it imports
 * next/link + next/navigation, which do not resolve from this directory —
 * module resolution walks up from the importing file, and no next install
 * exists above libs/. This lib keeps the framework-free pieces: the
 * generated nav payload (nav.generated.ts) and the shell's type contract
 * below (apps import these alongside their app-local Shell).
 */

export type ShellLocale = "bn" | "en";

export interface ShellSection {
  href: string;
  en: string;
  bn: string;
  icon: string;
}

export interface ShellCopy {
  searchPlaceholder: string;
  portalZone: string;
  erpZone: string;
  systemZone: string;
  home: string;
  recents: string;
  online: string;
  offline: string;
  company: string;
  opsLabel: string;
  portalsLabel: string;
  tellmePages: string;
  tellmeModules: string;
  tellmeScreens: string;
  tellmeEmpty: string;
  closeTab: string;
}
