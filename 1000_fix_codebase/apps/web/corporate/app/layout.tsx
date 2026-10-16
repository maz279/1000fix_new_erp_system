import type { Metadata } from "next";
import { tokens } from "../lib/imports";
import { ThemeProvider } from "../components/theme";
import { LanguageProvider } from "../components/language";
import { AuthProvider } from "../components/auth-modal";
import { CorporateNav } from "../components/nav";

export const metadata: Metadata = {
  title: "1000FiX — Corporate B2B Portal",
  description: "Enterprise fleet asset registry, consolidated B2B invoicing and scalable service requests for corporate clients (P04).",
};

// PP7-M03: nonce-CSP (proxy.ts) requires per-request rendering — a
// statically prerendered shell would carry no nonce and strict-dynamic
// would block every chunk at runtime.
export const dynamic = "force-dynamic";

/**
 * Root Layout for Corporate B2B Portal (P04).
 * Pure design-token styling (CFM-01) with:
 * - ThemeProvider (dark/light mode & row density)
 * - LanguageProvider (bilingual English / বাংলা)
 * - AuthProvider (Odoo session management & modal)
 * - Accessible CorporateNav shell
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        style={{
          margin: 0,
          background: tokens["color.surface.canvas"],
          color: tokens["color.text.primary"],
          fontFamily: `${tokens["typography.font.latin.family"]}, ${tokens["typography.font.latin.fallback"]}`,
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <ThemeProvider>
          <LanguageProvider>
            <AuthProvider>
              <CorporateNav />
              <div style={{ flex: 1 }}>{children}</div>
            </AuthProvider>
          </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
