import type { Metadata } from "next";
import { tokens, uiCopy } from "../lib/imports";
import { ThemeProvider, ThemeToggles } from "../components/theme";

export const metadata: Metadata = {
  title: "1000FiX — Corporate B2B Portal",
  description: "Estate, consolidated invoicing and service requests for corporate clients (P04).",
};

/**
 * The shell styles itself from the GENERATED R2 token emission only — no
 * hand-authored colours (CFM-01). Dark mode and density switch via the
 * ThemeProvider which toggles data-theme/data-density attributes; the
 * token custom properties cascade.
 */
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
              {uiCopy("nav.portal.p04", "en")}
            </span>
            <a href="/estate" style={{
              fontSize: tokens["typography.size.200"],
              color: tokens["color.text.secondary"],
              textDecoration: "none",
            }}>Estate</a>
            <a href="/invoices" style={{
              fontSize: tokens["typography.size.200"],
              color: tokens["color.text.secondary"],
              textDecoration: "none",
            }}>Invoices</a>
            <a href="/service-requests" style={{
              fontSize: tokens["typography.size.200"],
              color: tokens["color.text.secondary"],
              textDecoration: "none",
            }}>Requests</a>
            <ThemeToggles />
          </nav>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
