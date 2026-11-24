"use client";

/**
 * Corporate B2B navigation.
 *
 * Customer-account scope only: overview, fleet estate, contracts & SLA,
 * invoices & statements, service requests, tenders & quotations, reports and
 * the account record. There is no back-office/ERP link — the corporate portal
 * is not an operations entry point.
 */
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { tokens } from "../lib/imports";
import { useLanguage, LanguageToggle } from "./language";
import { useAuth } from "./auth-modal";
import { ThemeToggles } from "./theme";

const NAV_ITEMS = [
  { href: "/dashboard", en: "Overview", bn: "সারসংক্ষেপ" },
  { href: "/estate", en: "Fleet estate", bn: "ডিভাইস বহর" },
  { href: "/contracts", en: "Contracts & SLA", bn: "চুক্তি ও এসএলএ" },
  { href: "/invoices", en: "Invoices & statements", bn: "ইনভয়েস ও স্টেটমেন্ট" },
  { href: "/service-requests", en: "Service requests", bn: "সার্ভিস রিকোয়েস্ট" },
  { href: "/tenders", en: "Tenders & quotes", bn: "টেন্ডার ও কোটেশন" },
  { href: "/reports", en: "Reports", bn: "রিপোর্ট" },
  { href: "/account", en: "Account", bn: "অ্যাকাউন্ট" },
];

export function CorporateNav() {
  const pathname = usePathname();
  const { t, locale } = useLanguage();
  const { user, logoutUser } = useAuth();
  const [hostName, setHostName] = useState<string | null>(null);

  useEffect(() => {
    setHostName(window.location.hostname);
  }, []);
  const customerHref = `http://${hostName ?? "127.0.0.1"}:3000/`;
  const bn = locale === "bn";

  return (
    <header role="banner">
      <nav
        aria-label="Corporate portal navigation"
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          gap: 12,
          padding: "10px 24px",
          borderBottom: `1px solid ${tokens["color.border.default"]}`,
          background: tokens["color.surface.primary"],
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginRight: 8 }}>
          <Link
            href="/"
            style={{
              fontSize: tokens["typography.size.300"],
              fontWeight: Number(tokens["typography.weight.bold"]),
              color: tokens["color.primary.base"],
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              textDecoration: "none",
              whiteSpace: "nowrap",
            }}
          >
            {t.portalTitle}
          </Link>
          <span
            style={{
              fontSize: tokens["typography.size.100"],
              background: tokens["color.surface.secondary"],
              padding: "2px 8px",
              borderRadius: tokens["dimension.border.radius-sm"],
              color: tokens["color.primary.base"],
              fontWeight: 600,
              letterSpacing: "0.04em",
              whiteSpace: "nowrap",
            }}
          >
            {t.isoBadge}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 2, flexWrap: "wrap", marginRight: "auto" }}>
          {NAV_ITEMS.map((item) => {
            const isActive =
              pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(`${item.href}/`));
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                style={{
                  fontSize: tokens["typography.size.200"],
                  fontWeight: isActive
                    ? Number(tokens["typography.weight.semibold"])
                    : Number(tokens["typography.weight.medium"]),
                  color: isActive ? tokens["color.primary.base"] : tokens["color.text.secondary"],
                  textDecoration: "none",
                  padding: "6px 9px",
                  borderRadius: tokens["dimension.border.radius-sm"],
                  background: isActive ? tokens["color.surface.secondary"] : "transparent",
                  whiteSpace: "nowrap",
                }}
              >
                {bn ? item.bn : item.en}
              </Link>
            );
          })}
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
          <a
            href={customerHref}
            target="_blank"
            rel="noreferrer"
            style={{
              fontSize: tokens["typography.size.100"],
              color: tokens["color.primary.base"],
              textDecoration: "none",
              fontWeight: 600,
            }}
          >
            {t.navCustomerPortal} ↗
          </a>
          <span style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"], fontWeight: 600 }}>
            📞 16743
          </span>
          <span style={{ color: tokens["color.border.default"] }}>|</span>
          <LanguageToggle />
          <ThemeToggles />
          {user ? (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span
                title={user.username}
                style={{
                  fontSize: tokens["typography.size.100"],
                  background: tokens["color.surface.secondary"],
                  color: tokens["color.text.primary"],
                  padding: "4px 10px",
                  borderRadius: tokens["dimension.border.radius-pill"],
                  fontWeight: 600,
                  maxWidth: 180,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                👤 {user.name}
              </span>
              <button
                onClick={logoutUser}
                style={{
                  padding: "4px 10px",
                  fontSize: tokens["typography.size.200"],
                  color: tokens["color.status.error"],
                  background: "transparent",
                  border: `1px solid ${tokens["color.status.error"]}`,
                  borderRadius: tokens["dimension.border.radius-sm"],
                  cursor: "pointer",
                }}
              >
                {t.signOut}
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              style={{
                padding: "6px 14px",
                fontSize: tokens["typography.size.200"],
                fontWeight: Number(tokens["typography.weight.semibold"]),
                color: tokens["color.text.inverse"],
                background: tokens["color.primary.base"],
                border: "none",
                borderRadius: tokens["dimension.border.radius-sm"],
                textDecoration: "none",
              }}
            >
              🔐 {t.signIn}
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
}
