import type { Metadata } from "next";
import { Inter, Noto_Sans_Bengali, Sora } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "../components/theme";
import { LanguageProvider } from "../components/language";
import { AuthProvider } from "../components/auth-modal";
import { CustomerShell } from "../components/shell";
import { RumMount } from "../components/rum";
import { tokens } from "../lib/imports";

// Self-hosted via next/font (build-time download — no runtime CDN, CSP-safe).
// The token stacks in globals.css consume these variables with the token
// fallback chain behind them (CFM-01 values remain the fallback).
const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});
// DE-17: the Bengali face this shell loads must be the one the design system
// names. next/font/google needs a statically analysable import, so the token
// cannot pick the loader — it pins it instead: change
// typography.font.bengali.family in tokens.json and this fails the build rather
// than letting the rendered font drift away from the design system (re-audit
// 2026-10-31; the layout and the token had no link at all).
const BENGALI_FAMILY = tokens["typography.font.bengali.family"];
// next/font requires the fallback list as explicit literals (a computed array
// fails the page compile — caught by the 2026-10-31 A03 audit, portal was 500).
// The DE-17 guard below keeps these literals welded to the token.
const BENGALI_FALLBACK_TOKEN = "'SolaimanLipi', 'Kalpurush', 'Nikosh', sans-serif";
if (BENGALI_FAMILY !== "Noto Sans Bengali") {
  throw new Error(
    `DE-17: this shell loads Noto Sans Bengali, but the design token names ` +
      `"${BENGALI_FAMILY}" — update the loader and this guard together.`,
  );
}
if (tokens["typography.font.bengali.fallback"] !== BENGALI_FALLBACK_TOKEN) {
  throw new Error(
    `DE-17: the Bengali fallback token drifted from the layout literals ` +
      `(${tokens["typography.font.bengali.fallback"]}) — update both together.`,
  );
}
const notoBengali = Noto_Sans_Bengali({
  subsets: ["bengali"],
  variable: "--font-noto-bengali",
  display: "swap",
  fallback: ["SolaimanLipi", "Kalpurush", "Nikosh", "sans-serif"],
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
