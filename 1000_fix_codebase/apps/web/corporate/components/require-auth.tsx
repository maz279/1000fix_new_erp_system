"use client";

/**
 * Corporate-account route guard. The proxy is the first hop; this component
 * asks Odoo (through the same-origin bridge) whether the cookie maps to a
 * real corporate client before rendering protected content. Backend outages
 * are shown as outages, never as "session expired".
 */
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Loading, LoadError } from "../lib/imports";
import { useAuth } from "./auth-modal";
import { useLanguage } from "./language";

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, authReady, backendReachable, refreshUser } = useAuth();
  const { t } = useLanguage();
  const router = useRouter();
  const pathname = usePathname();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    let active = true;
    refreshUser().finally(() => {
      if (active) setChecking(false);
    });
    return () => {
      active = false;
    };
  }, [refreshUser]);

  useEffect(() => {
    if (checking || !authReady) return;
    if (!user && backendReachable !== false) {
      router.replace(`/login?next=${encodeURIComponent(pathname || "/dashboard")}`);
    }
  }, [checking, authReady, user, backendReachable, pathname, router]);

  if (checking || !authReady) return <Loading label={t.loading} />;

  if (backendReachable === false) {
    return <LoadError what={t.errorPrefix} message={t.unauthenticatedNotice} />;
  }

  if (!user) return <Loading label={t.loading} />;

  return <>{children}</>;
}
