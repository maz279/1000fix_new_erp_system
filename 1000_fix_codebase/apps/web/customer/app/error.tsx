"use client";

import { useLanguage } from "@/components/language";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <main className="fx-page" style={{ display: "flex", justifyContent: "center", paddingTop: 48 }}>
      <div className="load-error" style={{ maxWidth: 520 }}>
        <h4>{locale === "bn" ? "⚠️ কিছু একটা ভুল হয়েছে" : "⚠️ Something went wrong"}</h4>
        <p className="mono" style={{ fontSize: 11 }}>
          {error.digest ? `digest: ${error.digest}` : error.message}
        </p>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-primary" onClick={() => reset()}>
            আবার চেষ্টা করুন / Try again
          </button>
          <a className="btn" href="/">{locale === "bn" ? "হোম" : "Home"}</a>
        </div>
      </div>
    </main>
  );
}
