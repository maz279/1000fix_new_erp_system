import type { NextConfig } from "next";
import path from "node:path";

/** PP1 scaffold — monorepo root lifts Turbopack's module boundary (see corporate). */
const nextConfig: NextConfig = {
  reactStrictMode: true,
  // R01 re-audit 2026-10-22: standalone server for the portal Docker image
  // (next start works locally, but the image ships .next/standalone only).
  output: "standalone",
  outputFileTracingRoot: path.join(__dirname, "../../.."),
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
