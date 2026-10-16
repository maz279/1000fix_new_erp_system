import type { NextConfig } from "next";
import path from "node:path";

/**
 * P05 Vendor (R2) — PP5 scaffold config.
 *
 * Production builds consolidate into a single initial JS bundle: the
 * ZCode in-app browser pane (Chromium 146/Electron 41) fails to commit
 * any page whose HTML carries ~7+ script resources (bisected live:
 * 6 script tags render, 8 do not — the pane's network layer, not the
 * app). One bundle ≈ one script tag, well inside every environment's
 * limits; the total payload is unchanged.
 */
const nextConfig: NextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: path.join(__dirname, "../../.."),
  // EP-12: loopback-only in dev; production origins come from env at deploy.
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "X-Frame-Options", value: "DENY" },
          // PP7-M03 (D17): HSTS preload + minimal permissions. Honoured by
          // browsers over TLS; harmless on the http dev serves.
          { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(self), payment=()" },
        ],
      },
    ];
  },
};

export default nextConfig;
