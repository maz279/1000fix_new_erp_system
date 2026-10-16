"use client";

/**
 * Customer Portal Responsive Navigation Bar.
 * Dual-language aware (DE-17: Bengali default + English toggle).
 * Authenticated customer identity indicator & theme toggles.
 * Tokens only (CFM-01) — no hand-authored colors.
 */
import { tokens } from "../lib/imports";
import { useLanguage, LanguageToggle } from "./language";
import { ThemeToggles } from "./theme";
import { AuthControls } from "./auth-modal";

export function CustomerNavbar() {
  const { t, locale } = useLanguage();

  const navLinks = [
    ["/", t.navHome],
    ["/booking", t.navBooking],
    ["/tracking", t.navTracking],
    ["/estimates", t.navEstimates],
    ["/devices", t.navDevices],
    ["/consent", t.navConsent],
    ["/technician", t.navTechnician],
    ["/welcome", t.navWelcome],
  ];

  return (
    <nav
      style={{
        display: "flex",
        alignItems: "center",
        flexWrap: "wrap",
        gap: 12,
        padding: "10px 24px",
        borderBottom: `1px solid ${tokens["color.border.default"]}`,
        background: tokens["color.surface.primary"],
      }}
    >
      <a
        href="/"
        style={{
          fontSize: tokens["typography.size.300"],
          fontWeight: Number(tokens["typography.weight.bold"]),
          color: tokens["color.primary.base"],
          letterSpacing: "0.06em",
          textTransform: "uppercase",
          textDecoration: "none",
          marginRight: 8,
        }}
      >
        {t.portalTitle}
      </a>

      <span
        style={{
          fontSize: tokens["typography.size.100"],
          background: tokens["color.surface.secondary"],
          padding: "2px 8px",
          borderRadius: 4,
          color: tokens["color.primary.base"],
          fontWeight: 600,
          marginRight: "auto",
        }}
      >
        {t.isoBadge}
      </span>

      <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        {navLinks.map(([href, label]) => (
          <a
            key={href}
            href={href}
            style={{
              fontSize: tokens["typography.size.200"],
              color: tokens["color.text.secondary"],
              textDecoration: "none",
              padding: "4px 6px",
              borderRadius: tokens["dimension.border.radius-sm"],
            }}
          >
            {label}
          </a>
        ))}

        <span style={{ color: tokens["color.border.default"] }}>|</span>

        <a
          href="http://127.0.0.1:3001/"
          target="_blank"
          rel="noreferrer"
          style={{
            fontSize: tokens["typography.size.100"],
            color: tokens["color.primary.base"],
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          {t.navCorporate}
        </a>

        <a
          href="http://127.0.0.1:8069/odoo"
          target="_blank"
          rel="noreferrer"
          style={{
            fontSize: tokens["typography.size.100"],
            color: tokens["color.primary.base"],
            textDecoration: "none",
            fontWeight: 600,
          }}
        >
          {t.navOperations}
        </a>

        <span
          style={{
            fontSize: tokens["typography.size.100"],
            color: tokens["color.text.secondary"],
            fontWeight: 600,
          }}
        >
          {t.navHotline}
        </span>

        <LanguageToggle />
        <ThemeToggles />
        <AuthControls />
      </div>
    </nav>
  );
}
