import type { Metadata } from "next";
import { tokens, uiCopy } from "../lib/imports";
import { ThemeProvider, ThemeToggles } from "../components/theme";

export const metadata: Metadata = {
  title: "1000FiX — Vendor Portal",
  description: "PO acknowledgement, delivery confirmation and invoice submission feeding the three-way match (P05).",
};

// PP7-M03: nonce-CSP (proxy.ts) requires per-request rendering — a
// statically prerendered shell would carry no nonce and strict-dynamic
// would block every chunk at runtime.
export const dynamic = "force-dynamic";

/** The P05 vendor shell — generated tokens only (CFM-01). */
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
              {uiCopy("nav.portal.p05", "en")}
            </span>
            {[
              ["/", "Purchase Orders"], ["/invoices", "Invoices"],
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
