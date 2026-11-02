"use client";

// This app configures no "@/" path alias (tsconfig has no `paths`), and every
// other file imports relatively; the alias here never compiled (FF re-audit
// 2026-10-31 — the error boundary was the only "@/" user in the app).
import { useLanguage } from "../components/language";

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  // `locale` was referenced three times but never bound — the error boundary
  // threw a ReferenceError of its own, so a runtime error showed a crash
  // instead of this fallback.
  const { locale } = useLanguage();
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
