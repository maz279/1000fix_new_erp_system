import type { Metadata } from "next";
import { tokens, uiCopy } from "../lib/imports";
import { ThemeProvider } from "../components/theme";
import { LanguageProvider } from "../components/language";
import { AuthProvider } from "../components/auth-modal";
import { CustomerNavbar } from "../components/nav";
import { RumMount } from "../components/rum";

export const metadata: Metadata = {
  title: "1000FiX — কাস্টমার পোর্টাল / Customer Portal",
  description: "বুকিং, লাইভ ট্র্যাকিং, ডিভাইস ও সম্মতি — P01 (DE-17: বাংলা-প্রথম / Bengali-first dual language)",
};

// PP7-M03: nonce-CSP (proxy.ts) requires per-request rendering — a
// statically prerendered shell would carry no nonce and strict-dynamic
// would block every chunk at runtime.
export const dynamic = "force-dynamic";

/**
 * The P01 customer shell — BENGALI-FIRST (DE-17): lang="bn", the Bengali
 * token copy drives the chrome, the Bengali font family wins. Styled
 * from the GENERATED token emission only (CFM-01).
 * Features dual language support (Bangla ⇄ English) with persistent toggle,
 * accessible keyboard navigation, and real authenticated Odoo session wiring.
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  // Retains uiCopy call with "bn" for token parity and fitness contracts
  const _initialCopy = uiCopy("nav.portal.p01", "bn");

  return (
    <html lang="bn" suppressHydrationWarning data-initial-copy={_initialCopy}>
      <body style={{
        margin: 0,
        background: tokens["color.surface.canvas"],
        color: tokens["color.text.primary"],
        fontFamily: `${tokens["typography.font.bengali.family"]}, ${tokens["typography.font.latin.family"]}, ${tokens["typography.font.latin.fallback"]}`,
      }}>
        <ThemeProvider>
          <LanguageProvider>
            <AuthProvider>
              <RumMount />
              <CustomerNavbar />
              {children}
            </AuthProvider>
          </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
