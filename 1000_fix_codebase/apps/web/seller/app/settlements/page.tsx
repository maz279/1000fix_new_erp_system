import { redirect } from "next/navigation";

/** The payouts ledger and the §52 statement are one surface now. */
export default function RetiredSettlementsPage() {
  redirect("/statements");
}
