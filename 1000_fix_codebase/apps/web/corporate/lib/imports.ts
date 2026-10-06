/**
 * Import barrel — re-exports the generated artefacts so every page uses
 * the same short path regardless of nesting depth.
 *
 * Pages import from `../../lib/imports` (or `../../../lib/imports` for
 * deeper nesting) instead of counting `../` levels to libs/.
 */
export { tokens } from "../../../../libs/ts/ui/src/tokens/tokens.generated";
export { uiCopy } from "../../../../libs/ts/api-client/src/ui-copy";
export { ApiClient, ApiError } from "../../../../libs/ts/api-client/src/index";