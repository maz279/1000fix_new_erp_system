"use client";

/* OIDC callback page (PP3-M01) — receives the authorization code from
 * Keycloak and exchanges it for tokens. On success, redirects to the
 * estate page; on failure, shows the error.
 */
import { useEffect, useState } from "react";
import { tokens } from "../../../lib/imports";
import { exchangeCode } from "../../../lib/auth";

export default function AuthCallback() {
  const [status, setStatus] = useState<"exchanging" | "success" | "error">("exchanging");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const url = new URL(window.location.href);
    const code = url.searchParams.get("code");
    const errorParam = url.searchParams.get("error");

    if (errorParam) {
      setError(`Keycloak returned: ${errorParam}`);
      setStatus("error");
      return;
    }
    if (!code) {
      setError("No authorization code in the callback URL");
      setStatus("error");
      return;
    }

    exchangeCode(code)
      .then(() => {
        setStatus("success");
        // Redirect to the estate page after a brief flash
        setTimeout(() => { window.location.href = "/estate"; }, 500);
      })
      .catch((e: Error) => {
        setError(e.message);
        setStatus("error");
      });
  }, []);

  return (
    <main style={{
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      height: "100vh",
      background: tokens["color.surface.canvas"],
    }}>
      <div style={{
        padding: 32,
        borderRadius: tokens["dimension.border.radius-md"],
        background: tokens["color.surface.primary"],
        border: `1px solid ${tokens["color.border.default"]}`,
        textAlign: "center",
      }}>
        {status === "exchanging" && (
          <p style={{ color: tokens["color.text.secondary"] }}>Exchanging authorization code…</p>
        )}
        {status === "success" && (
          <>
            <p style={{ color: tokens["color.status.success"], fontWeight: 600 }}>✓ Authenticated</p>
            <p style={{ color: tokens["color.text.secondary"], fontSize: 12 }}>Redirecting…</p>
          </>
        )}
        {status === "error" && (
          <>
            <p style={{ color: tokens["color.status.error"], fontWeight: 600 }}>Authentication failed</p>
            <p style={{ color: tokens["color.text.secondary"], fontSize: 12 }}>{error}</p>
          </>
        )}
      </div>
    </main>
  );
}
