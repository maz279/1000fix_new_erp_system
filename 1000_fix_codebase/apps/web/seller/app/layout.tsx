import type { Metadata } from "next";
import { tokens, uiCopy } from "../lib/imports";
import { ThemeProvider, ThemeToggles } from "../components/theme";
import { AuthProvider, AuthGate, AuthStatus } from "../components/auth-gate";

export const metadata: Metadata = {
  title: "1000FiX — Marketplace Seller Portal (P07)",
  description: "Seller onboarding, quotes, jobs, scorecards, settlement statements, and 48h SLA disputes (P07).",
};

// PP7-M03: nonce-CSP (proxy.ts) requires per-request rendering — a
// statically prerendered shell would carry no nonce and strict-dynamic
// would block every chunk at runtime.
export const dynamic = "force-dynamic";

/** The P07 seller shell — generated tokens only (CFM-01). */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body style={{
        margin: 0,
        background: tokens["color.surface.canvas"],
        color: tokens["color.text.primary"],
        fontFamily: `${tokens["typography.font.latin.family"]}, ${tokens["typography.font.latin.fallback"]}`,
      }}>
        <ThemeProvider>
          <AuthProvider>
            <nav style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              padding: "8px 24px",
              borderBottom: `1px solid ${tokens["color.border.default"]}`,
              background: tokens["color.surface.primary"],
              flexWrap: "wrap",
            }}>
              <span style={{
                fontSize: tokens["typography.size.300"],
                fontWeight: Number(tokens["typography.weight.semibold"]),
                color: tokens["color.primary.base"],
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                marginRight: 16,
              }}>
                {uiCopy("nav.portal.p07", "en")}
              </span>
              {[
                ["/", "Dashboard"],
                ["/onboarding", "Onboarding (KYC)"],
                ["/jobs", "Jobs"],
                ["/quotes", "Quotes"],
                ["/scorecard", "Scorecard"],
                ["/settlements", "Settlements"],
                ["/statements", "Statements (§52)"],
                ["/disputes", "Disputes (48h SLA)"],
              ].map(([href, label]) => (
                <a key={href} href={href} style={{
                  fontSize: tokens["typography.size.200"],
                  color: tokens["color.text.secondary"],
                  textDecoration: "none",
                  padding: "4px 8px",
                }}>{label}</a>
              ))}
              <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 12 }}>
                <AuthStatus />
                <ThemeToggles />
              </div>
            </nav>
            <AuthGate>{children}</AuthGate>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
