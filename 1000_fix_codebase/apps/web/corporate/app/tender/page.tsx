import { redirect } from "next/navigation";

/**
 * Retired route: the old singular /tender page was a "not yet available"
 * stub. The live tender & quotation register is /tenders.
 */
export default function RetiredTenderPage() {
  redirect("/tenders");
}
