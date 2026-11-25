"use client";

/**
 * Staff-only gate for the P02 technician workbench.
 *
 * The customer portal is for customers; the technician workbench is an
 * internal surface that happens to be co-hosted. It renders only when the
 * current Odoo session belongs to an INTERNAL user (staff who signed in on
 * Odoo directly — the portal's own sign-in refuses staff). A customer with a
 * portal session is sent back to the dashboard. The technician API relay
 * enforces the same rule server-side, so this is a UI boundary, not the
 * security boundary.
 */
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Loading } from "../lib/imports";
import { getStaffSession } from "../lib/auth";
import { useLanguage } from "./language";

export function StaffOnly({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { locale } = useLanguage();
  const [state, setState] = useState<"checking" | "allowed" | "denied">("checking");

  useEffect(() => {
    let active = true;
    getStaffSession().then((s) => {
      if (!active) return;
      if (s.internal) {
        setState("allowed");
      } else {
        setState("denied");
        router.replace("/dashboard");
      }
    });
    return () => {
      active = false;
    };
  }, [router]);

  if (state === "allowed") return <>{children}</>;

  return (
    <Loading
      label={
        state === "checking"
          ? locale === "bn"
            ? "কর্মী সেশন যাচাই হচ্ছে…"
            : "Verifying staff session…"
          : locale === "bn"
            ? "এই পাতাটি কর্মীদের জন্য — ড্যাশবোর্ডে ফেরত যাচ্ছে…"
            : "This workbench is for staff — returning to your dashboard…"
      }
    />
  );
}
