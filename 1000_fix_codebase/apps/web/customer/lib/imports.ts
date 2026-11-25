/**
 * Import barrel — re-exports the generated artefacts so every page uses
 * the same short path regardless of nesting depth (PP3 pattern).
 * Extended at PP5 with the shared UI atoms from libs/ts/ui.
 */
export { tokens } from "../../../../libs/ts/ui/src/tokens/tokens.generated";
// NOTE (2026-11-24): uiCopy (the platform-wide copy dictionary) is not
// re-exported here — it carries every ERP module label and has no consumer in
// the customer app. The customer shell's copy is app-local (components/shell.tsx).
export { ApiClient, ApiError, pingHealth } from "../../../../libs/ts/api-client/src/index";
export {
  Pill, Stat, SectionHead, DataTable, Loading, LoadError,
} from "../../../../libs/ts/ui/src/components";
export type { Column } from "../../../../libs/ts/ui/src/components";
// D365 shell types (lib) + implementation (app-local — imports next/link).
export type { ShellSection, ShellCopy, ShellLocale } from "../../../../libs/ts/ui/src/shell";
export { Shell } from "../components/shell-chrome";
// NOTE (2026-11-24): the generated ERP navigation payload (nav.generated:
// 67 modules / 823 screens) and the 12-portal LandingShell are deliberately
// NOT exported here. The customer portal must not ship the ERP module tree
// or the estate directory to the browser; customer sections are declared in
// components/shell.tsx.
export {
  isValidId, maskId, bn007, BIN_13, NID_10, NID_17, ETIN_12,
} from "../../../../libs/ts/ui/src/masks";
export type { StatutoryId } from "../../../../libs/ts/ui/src/masks";
// PP7-M04: the RUM/OTel seam (inert without NEXT_PUBLIC_OTEL_ENDPOINT).
export { installRum } from "../../../../libs/ts/ui/src/observability";
