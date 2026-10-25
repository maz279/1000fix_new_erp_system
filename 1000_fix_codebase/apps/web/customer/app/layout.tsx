import type { Metadata } from "next";
import { Inter, Noto_Sans_Bengali, Sora } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "../components/theme";
import { LanguageProvider } from "../components/language";
import { AuthProvider } from "../components/auth-modal";
import { CustomerShell } from "../components/shell";
import { RumMount } from "../components/rum";

// Self-hosted via next/font (build-time download — no runtime CDN, CSP-safe).
// The token stacks in globals.css consume these variables with the token
// fallback chain behind them (CFM-01 values remain the fallback).
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});
const notoBengali = Noto_Sans_Bengali({
  subsets: ["bengali"],
  variable: "--font-noto-bengali",
  display: "swap",
});
const sora = Sora({
  subsets: ["latin"],
  variable: "--font-sora",
  display: "swap",
});

export const metadata: Metadata = {
  title: "1000FiX কাস্টমার পোর্টাল",
  description: "বুকিং, লাইভ ট্র্যাকিং, ডিভাইস ও সম্মতি — P01",
};

// PP7-M03: nonce-CSP (proxy.ts) requires per-request rendering — a
// statically prerendered shell would carry no nonce and strict-dynamic
// would block every chunk at runtime.
export const dynamic = "force-dynamic";

/**
 * The P01 customer shell — BENGALI-FIRST (DE-17): lang="bn", the Bengali
 * token copy drives the chrome, the Bengali font family wins.
 * Styling: generated R6 token bridge (tokens.css) + the Service-Teal
 * Fluent shell classes in globals.css — ported from the frozen prototype
 * (FIX-UXD-2026-001). Theme (light/dark) and density cascade through
 * html[data-theme] / html[data-density].
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="bn"
      suppressHydrationWarning
      className={`${inter.variable} ${notoBengali.variable} ${sora.variable}`}
    >
      <body>
        <ThemeProvider>
          <LanguageProvider>
            <AuthProvider>
              <RumMount />
              <CustomerShell>{children}</CustomerShell>
            </AuthProvider>
          </LanguageProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
