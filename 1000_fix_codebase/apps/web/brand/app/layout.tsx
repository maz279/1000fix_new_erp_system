import type { Metadata } from "next";
import Link from "next/link";
import { tokens } from "../lib/imports";
import { ThemeProvider, ThemeToggles } from "../components/theme";
import { AuthProvider, AuthGate, AuthStatus } from "../components/auth-gate";
import { BrandProvider, BrandSelect } from "../components/brand-context";

export const metadata: Metadata = {
  title: "1000FiX — Brand Partner Portal (P08)",
  description:
    "Warranty claim decisions, remittance reconciliation and brand claim posture for OEM partners (P08).",
};

// PP7-M03: nonce-CSP (proxy.ts) requires per-request rendering — a
// statically prerendered shell would carry no nonce and strict-dynamic
// would block every chunk at runtime.
export const dynamic = "force-dynamic";

const NAV = [
  { href: "/dashboard", en: "Dashboard", bn: "ড্যাশবোর্ড" },
  { href: "/claims", en: "Claims", bn: "দাবি" },
  { href: "/reconciliation", en: "Reconciliation", bn: "রিকনসিলিয়েশন" },
  { href: "/account", en: "Brand access", bn: "ব্র্যান্ড অ্যাক্সেস" },
];

/** The P08 brand partner shell — generated tokens only (CFM-01). */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        style={{
          margin: 0,
          background: tokens["color.surface.canvas"],
          color: tokens["color.text.primary"],
          fontFamily: `${tokens["typography.font.latin.family"]}, ${tokens["typography.font.latin.fallback"]}`,
        }}
      >
        <ThemeProvider>
          <AuthProvider>
            <BrandProvider>
            <nav
              aria-label="Brand partner navigation"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
                padding: "8px 24px",
                borderBottom: `1px solid ${tokens["color.border.default"]}`,
                background: tokens["color.surface.primary"],
                flexWrap: "wrap",
              }}
            >
              <Link
                href="/"
                style={{
                  fontSize: tokens["typography.size.300"],
                  fontWeight: Number(tokens["typography.weight.semibold"]),
                  color: tokens["color.primary.base"],
                  letterSpacing: "0.08em",
                  textTransform: "uppercase",
                  textDecoration: "none",
                  marginRight: 8,
                  whiteSpace: "nowrap",
                }}
              >
                Brand Partner
              </Link>
              {NAV.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  title={item.bn}
                  style={{
                    fontSize: tokens["typography.size.200"],
                    color: tokens["color.text.secondary"],
                    textDecoration: "none",
                    padding: "4px",
                    whiteSpace: "nowrap",
                  }}
                >
                  {item.en}
                </Link>
              ))}
              <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 12 }}>
                <BrandSelect />
                <AuthStatus />
                <ThemeToggles />
              </div>
            </nav>
            <AuthGate>{children}</AuthGate>
            </BrandProvider>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
