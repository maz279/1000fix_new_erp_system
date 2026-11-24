import type { Metadata } from "next";
import Link from "next/link";
import { tokens } from "../lib/imports";
import { ThemeProvider, ThemeToggles } from "../components/theme";
import { AuthProvider, AuthGate, AuthStatus } from "../components/auth-gate";

export const metadata: Metadata = {
  title: "1000FiX — Marketplace Seller Portal (P07)",
  description:
    "Seller onboarding and KYC, job board and quotes, stock and listings, scorecard, payouts and statements, and 48h SLA disputes (P07).",
};

// PP7-M03: nonce-CSP (proxy.ts) requires per-request rendering — a
// statically prerendered shell would carry no nonce and strict-dynamic
// would block every chunk at runtime.
export const dynamic = "force-dynamic";

const NAV = [
  { href: "/dashboard", en: "Dashboard", bn: "ড্যাশবোর্ড" },
  { href: "/onboarding", en: "Onboarding & KYC", bn: "অনবোর্ডিং ও কেওয়াইসি" },
  { href: "/jobs", en: "Job board", bn: "জব বোর্ড" },
  { href: "/quotes", en: "My quotes", bn: "আমার কোটেশন" },
  { href: "/stock", en: "Stock & listings", bn: "স্টক ও লিস্টিং" },
  { href: "/scorecard", en: "Scorecard", bn: "স্কোরকার্ড" },
  { href: "/statements", en: "Payouts & statements", bn: "পেমেন্ট ও স্টেটমেন্ট" },
  { href: "/disputes", en: "Disputes (48h SLA)", bn: "বিরোধ (৪৮ ঘণ্টা)" },
];

/** The P07 seller shell — generated tokens only (CFM-01). */
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
            <nav
              aria-label="Seller portal navigation"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
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
                Seller Portal
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
                    padding: "4px 4px",
                    whiteSpace: "nowrap",
                  }}
                >
                  {item.en}
                </Link>
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
