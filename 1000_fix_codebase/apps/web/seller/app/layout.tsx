import type { Metadata } from "next";
import { tokens, uiCopy } from "../lib/imports";
import { ThemeProvider, ThemeToggles } from "../components/theme";

export const metadata: Metadata = {
  title: "1000FiX — Marketplace Seller",
  description: "Seller onboarding, quotes, jobs, scorecards and settlement statements (P07).",
};

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
          <nav style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            padding: "8px 24px",
            borderBottom: `1px solid ${tokens["color.border.default"]}`,
            background: tokens["color.surface.primary"],
          }}>
            <span style={{
              fontSize: tokens["typography.size.300"],
              fontWeight: Number(tokens["typography.weight.semibold"]),
              color: tokens["color.primary.base"],
              letterSpacing: "0.08em",
              textTransform: "uppercase",
              flex: 1,
            }}>
              {uiCopy("nav.portal.p07", "en")}
            </span>
            {[
              ["/", "Dashboard"], ["/jobs", "Jobs"], ["/scorecard", "Scorecard"],
              ["/settlements", "Settlements"],
            ].map(([href, label]) => (
              <a key={href} href={href} style={{
                fontSize: tokens["typography.size.200"],
                color: tokens["color.text.secondary"],
                textDecoration: "none",
              }}>{label}</a>
            ))}
            <ThemeToggles />
          </nav>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
