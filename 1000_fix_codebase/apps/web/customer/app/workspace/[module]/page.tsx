import { redirect } from "next/navigation";

/**
 * Retired route: the embedded ERP workspace is not part of the customer
 * portal. Old bookmarks land on the customer dashboard instead of an
 * operations surface.
 */
export default function RetiredWorkspacePage() {
  redirect("/dashboard");
}
