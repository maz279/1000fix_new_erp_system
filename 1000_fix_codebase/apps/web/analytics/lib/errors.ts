/**
 * Error classification for analytics API calls.
 *
 * Odoo answers an expired/missing session on a JSON-RPC route with an
 * error envelope (`code: 100`, name `odoo.http.SessionExpiredException`,
 * message "Odoo Session Expired"). The shared ApiClient surfaces that as
 * an ApiError whose `code` is the raw envelope code. The page shows a
 * sign-in message for it instead of a generic failure.
 */
import { ApiError } from "./imports";

export interface DescribedError {
  sessionExpired: boolean;
  message: string;
}

export function describeError(e: unknown): DescribedError {
  const message = e instanceof Error ? e.message : String(e);
  const code = e instanceof ApiError ? String(e.code) : "";
  const status = e instanceof ApiError ? e.status : 0;
  const sessionExpired =
    code === "100" ||
    status === 401 ||
    /session expired|sessionexpired/i.test(message);
  return { sessionExpired, message };
}
