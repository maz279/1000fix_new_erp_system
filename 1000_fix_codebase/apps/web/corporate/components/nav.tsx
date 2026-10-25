"use client";

/**
 * Corporate Navigation Bar.
 * Responsive, accessible shell navigation with:
 * - Active route indicators
 * - Bilingual support (English / বাংলা)
 * - Dark mode & density controls
 * - Odoo session authentication controls
 * - Direct cross-portal links to Customer (:3000) and the Odoo ERP P03
 *   workspace (:8069) — both resolved to the BROWSING hostname after
 *   mount so the per-hostname session cookie jar is shared.
 * Tokens only (CFM-01) — no hand-authored colors.
 */
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { tokens } from "../lib/imports";
import { useLanguage, LanguageToggle } from "./language";
import { useAuth } from "./auth-modal";
import { ThemeToggles } from "./theme";

export function CorporateNav() {
  const pathname = usePathname();
  const { t } = useLanguage();
  const { user, openLoginModal, logoutUser } = useAuth();
  // Mount-resolved browsing hostname: cross-app links must share the
  // per-hostname cookie jar (cookies ignore ports, not hostnames).
  const [hostName, setHostName] = useState<string | null>(null);
  useEffect(() => {
    setHostName(window.location.hostname);
  }, []);
  const customerHref = `http://${hostName ?? "127.0.0.1"}:3000/`;
  const odooHref = `http://${hostName ?? "127.0.0.1"}:8069/odoo/action-cd_p03_portal.action_p03_workspace`;

  const navLinks = [
    { href: "/", label: t.navOverview },
    { href: "/estate", label: t.navEstate },
    { href: "/invoices", label: t.navInvoices },
    { href: "/service-requests", label: t.navRequests },
  ];

  return (
    <header role="banner">
      <nav
        aria-label="Main Corporate Navigation"
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          gap: 16,
          padding: "10px 24px",
          borderBottom: `1px solid ${tokens["color.border.default"]}`,
          background: tokens["color.surface.primary"],
        }}
      >
        {/* Brand & ISO Certification */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginRight: 16 }}>
          <Link
            href="/"
            style={{
              fontSize: tokens["typography.size.300"],
              fontWeight: Number(tokens["typography.weight.bold"]),
              color: tokens["color.primary.base"],
              letterSpacing: "0.06em",
              textTransform: "uppercase",
              textDecoration: "none",
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
            }}
          >
            {t.isoBadge}
          </span>
        </div>

        {/* Primary Route Links */}
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginRight: "auto" }}>
          {navLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={isActive ? "page" : undefined}
                style={{
                  fontSize: tokens["typography.size.200"],
                  fontWeight: isActive
                    ? Number(tokens["typography.weight.semibold"])
                    : Number(tokens["typography.weight.medium"]),
                  color: isActive ? tokens["color.primary.base"] : tokens["color.text.secondary"],
                  textDecoration: "none",
                  padding: "6px 12px",
                  borderRadius: tokens["dimension.border.radius-sm"],
                  background: isActive ? tokens["color.surface.secondary"] : "transparent",
                  transition: "background-color 0.15s ease",
                }}
              >
                {link.label}
              </Link>
            );
          })}
        </div>

        {/* Cross-Portal & Utility Links */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <a
            href={customerHref}
            target="_blank"
            rel="noreferrer"
            aria-label="Open Customer Portal in new tab"
            style={{
              fontSize: tokens["typography.size.100"],
              color: tokens["color.primary.base"],
              textDecoration: "none",
              fontWeight: 600,
            }}
          >
            {t.navCustomerPortal}
          </a>

          <a
            href={odooHref}
            target="_blank"
            rel="noreferrer"
            aria-label="Open Odoo ERP backend in new tab"
            style={{
              fontSize: tokens["typography.size.100"],
              color: tokens["color.primary.base"],
              textDecoration: "none",
              fontWeight: 600,
            }}
          >
            {t.navOdooErp}
          </a>

          <span
            style={{
              fontSize: tokens["typography.size.100"],
              color: tokens["color.text.secondary"],
              fontWeight: 600,
            }}
          >
            📞 16743
          </span>

          <span style={{ color: tokens["color.border.default"] }}>|</span>

          {/* Language Switcher */}
          <LanguageToggle />

          {/* Theme & Density Controls */}
          <ThemeToggles />

          {/* Authentication State & Actions */}
          {user ? (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span
                style={{
                  fontSize: tokens["typography.size.100"],
                  background: tokens["color.surface.secondary"],
                  color: tokens["color.text.primary"],
                  padding: "4px 10px",
                  borderRadius: tokens["dimension.border.radius-pill"],
                  fontWeight: 600,
                }}
              >
                👤 {user.name} ({user.username})
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
            <button
              onClick={openLoginModal}
              style={{
                padding: "6px 14px",
                fontSize: tokens["typography.size.200"],
                fontWeight: Number(tokens["typography.weight.semibold"]),
                color: tokens["color.text.inverse"],
                background: tokens["color.primary.base"],
                border: "none",
                borderRadius: tokens["dimension.border.radius-sm"],
                cursor: "pointer",
              }}
            >
              🔐 {t.signIn}
            </button>
          )}
        </div>
      </nav>
    </header>
  );
}
