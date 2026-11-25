import type { Metadata } from "next";
import Link from "next/link";
import { tokens } from "../lib/imports";
import { ThemeProvider, ThemeToggles } from "../components/theme";
import { AuthProvider, AuthGate, AuthStatus } from "../components/auth-gate";

export const metadata: Metadata = {
  title: "1000FiX — Analytics & Executive",
  description:
    "Executive, branch, technician, finance, warranty and people dashboards, the 95-KPI register, data governance and model monitoring — staff-only (P06).",
};

// PP7-M03: nonce-CSP (proxy.ts) requires per-request rendering — a
// statically prerendered shell would carry no nonce and strict-dynamic
// would block every chunk at runtime.
export const dynamic = "force-dynamic";

const NAV = [
  { href: "/dashboards", en: "Dashboards", bn: "ড্যাশবোর্ড" },
  { href: "/kpi-register", en: "KPI register", bn: "কেপিআই রেজিস্টার" },
  { href: "/governance", en: "Data governance", bn: "ডেটা গভর্নেন্স" },
  { href: "/models", en: "Model monitoring", bn: "মডেল মনিটরিং" },
];

/** The P06 analytics shell — generated tokens only (CFM-01). */
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
              aria-label="Analytics portal navigation"
              style={{
                display: "flex",
                alignItems: "center",
                gap: 14,
                flexWrap: "wrap",
                padding: "8px 24px",
                borderBottom: `1px solid ${tokens["color.border.default"]}`,
                background: tokens["color.surface.primary"],
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
                  marginRight: "auto",
                  whiteSpace: "nowrap",
                }}
              >
                Analytics &amp; Executive
              </Link>
              {NAV.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  style={{
                    fontSize: tokens["typography.size.200"],
                    color: tokens["color.text.secondary"],
                    textDecoration: "none",
                    whiteSpace: "nowrap",
                  }}
                  title={item.bn}
                >
                  {item.en}
                </Link>
              ))}
              <span style={{ color: tokens["color.border.default"] }}>|</span>
              <AuthStatus />
              <ThemeToggles />
            </nav>
            <AuthGate>{children}</AuthGate>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
