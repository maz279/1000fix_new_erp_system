/**
 * Import barrel — re-exports the generated artefacts so every page uses
 * the same short path regardless of nesting depth (PP3 pattern).
 * Extended at PP5 with the shared UI atoms from libs/ts/ui.
 */
export { tokens } from "../../../../libs/ts/ui/src/tokens/tokens.generated";
export { uiCopy } from "../../../../libs/ts/api-client/src/ui-copy";
export { ApiClient, ApiError } from "../../../../libs/ts/api-client/src/index";
export {
  Pill, Stat, SectionHead, DataTable, Loading, LoadError,
} from "../../../../libs/ts/ui/src/components";
export type { Column } from "../../../../libs/ts/ui/src/components";
export { LandingShell } from "../../../../libs/ts/ui/src/landing";
export {
  isValidId, maskId, bn007, BIN_13, NID_10, NID_17, ETIN_12,
} from "../../../../libs/ts/ui/src/masks";
export type { StatutoryId } from "../../../../libs/ts/ui/src/masks";
// PP7-M04: the RUM/OTel seam (inert without NEXT_PUBLIC_OTEL_ENDPOINT).
export { installRum } from "../../../../libs/ts/ui/src/observability";
