"use client";

// PP7-M04 — mounts the RUM/OTel seam on the client (D18). The seam is
// inert unless NEXT_PUBLIC_OTEL_ENDPOINT is configured at build time.
import { useEffect } from "react";
import { installRum } from "../lib/imports";

export function RumMount() {
  useEffect(() => {
    installRum();
  }, []);
  return null;
}
