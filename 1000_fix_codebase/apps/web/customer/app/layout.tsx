import type { Metadata } from "next";
import { tokens, uiCopy } from "../lib/imports";
import { ThemeProvider, ThemeToggles } from "../components/theme";

export const metadata: Metadata = {
  title: "1000FiX — কাস্টমার পোর্টাল",
  description: "বুকিং, লাইভ ট্র্যাকিং, ডিভাইস ও সম্মতি — P01 (DE-17: বাংলা-প্রথম)",
};

/**
 * The P01 customer shell — BENGALI-FIRST (DE-17): lang="bn", the Bengali
 * token copy drives the chrome, the Bengali font family wins. Styled
 * from the GENERATED token emission only (CFM-01).
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="bn" suppressHydrationWarning>
      <body style={{
        margin: 0,
        background: tokens["color.surface.canvas"],
        color: tokens["color.text.primary"],
        fontFamily: `${tokens["typography.font.bengali.family"]}, ${tokens["typography.font.latin.family"]}, ${tokens["typography.font.latin.fallback"]}`,
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
              {uiCopy("nav.portal.p01", "bn")}
            </span>
            {[
              ["/", "হোম"], ["/booking", "বুকিং"], ["/tracking", "ট্র্যাকিং"],
              ["/estimates", "অনুমান"], ["/devices", "ডিভাইস"], ["/consent", "সম্মতি"],
              ["/welcome", "✦"],
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
