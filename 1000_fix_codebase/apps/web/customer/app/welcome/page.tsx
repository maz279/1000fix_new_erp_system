import { redirect } from "next/navigation";

/**
 * Retired route: the old "12 portals" directory exposed the whole estate
 * (and the ERP entry points) to customers. The customer portal's public
 * front door is "/".
 */
export default function RetiredWelcomePage() {
  redirect("/");
}
