import type { NextConfig } from "next";
import path from "node:path";

/**
 * P04 Corporate B2B (R2) — PP1 scaffold config.
 * Next 16: proxy.ts replaces middleware.ts; Cache Components are explicit
 * ('use cache') — neither used yet at scaffold stage.
 *
 * Monorepo: the workspace root lifts Turbopack's module boundary so the app
 * compiles the generated libs (libs/ts/ui tokens, libs/ts/api-client) in-tree
 * instead of vendoring copies.
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
