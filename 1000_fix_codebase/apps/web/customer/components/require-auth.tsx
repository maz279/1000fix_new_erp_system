"use client";

/**
 * Customer-account route guard.
 *
 * The first hop (proxy.ts) redirects a visitor with no Odoo session cookie
 * before the page renders. This component is the authoritative check: it asks
 * Odoo (via /web/session/get_session_info) whether the cookie maps to a real
 * customer, and only then renders the protected page. Expired/revoked
 * sessions are sent to /login with a return path; backend outages are shown
 * as an outage, never disguised as "session expired".
 */
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Loading, LoadError } from "../lib/imports";
import { useAuth } from "./auth-modal";
import { useLanguage } from "./language";

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, authReady, backendReachable, refreshUser } = useAuth();
  const { locale } = useLanguage();
  const router = useRouter();
  const pathname = usePathname();
  const [checking, setChecking] = useState(true);
  const [retryToken, setRetryToken] = useState(0);

  useEffect(() => {
    let active = true;
    setChecking(true);
    refreshUser().finally(() => {
      if (active) setChecking(false);
    });
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [retryToken]);

  // Redirect only after both the provider's and the local check finished.
  useEffect(() => {
    if (checking || !authReady) return;
    if (!user && backendReachable !== false) {
      const next = pathname || "/dashboard";
      router.replace(`/login?next=${encodeURIComponent(next)}`);
    }
  }, [checking, authReady, user, backendReachable, pathname, router]);

  if (checking || !authReady) {
    return <Loading label={locale === "bn" ? "সেশন যাচাই হচ্ছে…" : "Verifying your session…"} />;
  }

  if (backendReachable === false) {
    return (
      <LoadError
        what={locale === "bn" ? "ব্যাকএন্ড সংযোগ" : "Backend connection"}
        message={
          locale === "bn"
            ? "সার্ভিস ব্যাকএন্ডে পৌঁছানো যাচ্ছে না। কিছুক্ষণ পর আবার চেষ্টা করুন।"
            : "The service backend is unreachable. Please try again shortly."
        }
      />
    );
  }

  if (!user) {
    // The redirect effect is about to run; render a neutral state, never the
    // protected content.
    return <Loading label={locale === "bn" ? "লগইনে নিয়ে যাচ্ছে…" : "Redirecting to sign in…"} />;
  }

  return <>{children}</>;
}
