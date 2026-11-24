/**
 * Import barrel — re-exports the generated artefacts so every page uses
 * the same short path regardless of nesting depth.
 *
 * Pages import from `../../lib/imports` (or `../../../lib/imports` for
 * deeper nesting) instead of counting `../` levels to libs/.
 */
export { tokens } from "../../../../libs/ts/ui/src/tokens/tokens.generated";
// NOTE (2026-11-24): uiCopy (the platform-wide copy dictionary carrying every
// ERP module label) is not re-exported — the corporate portal has no consumer
// and must not ship the ERP module tree to the browser.
export { ApiClient, ApiError } from "../../../../libs/ts/api-client/src/index";
export {
  Pill, Stat, SectionHead, DataTable, Loading, LoadError,
} from "../../../../libs/ts/ui/src/components";
export type { Column } from "../../../../libs/ts/ui/src/components";
