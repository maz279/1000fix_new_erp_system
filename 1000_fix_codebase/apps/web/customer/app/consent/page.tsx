"use client";

/* P01 PDPA consent dashboard — grant/withdraw per channel (Dual Language: Bengali-first + English).
 * A grant requires verifiable proof (OTP id / e-sign ref / signed form ID) enforced server-side.
 * Replaces window.prompt with accessible in-DOM dialog modal.
 * Tokens only (CFM-01) — no hand-authored colors. */
import { useCallback, useEffect, useState, useId } from "react";
import { tokens, Pill, SectionHead, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { RequireAuth } from "../../components/require-auth";
import { useAuth } from "../../components/auth-modal";

interface ConsentRow {
  id: number;
  channel: string;
  state: string;
  date_granted: string;
  date_withdrawn: string | null;
  proof: string;
}

const CHANNELS = ["sms", "whatsapp", "email", "push", "marketing"];

const card: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 20,
  display: "flex",
  alignItems: "center",
  gap: 16,
};

const btn: React.CSSProperties = {
  padding: "8px 16px",
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  boxSizing: "border-box",
  padding: 10,
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
};

function ConsentPageContent() {
  const { t, locale } = useLanguage();
  const { user } = useAuth();
  const [rows, setRows] = useState<ConsentRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // Accessible Grant Modal State (Replaces window.prompt)
  const [grantingChannel, setGrantingChannel] = useState<string | null>(null);
  const [proofInput, setProofInput] = useState("");
  const [grantBusy, setGrantBusy] = useState(false);
  const [grantError, setGrantError] = useState<string | null>(null);

  const proofInputId = useId();

  const channelNames: Record<string, string> = {
    sms: t.channelSms,
    whatsapp: t.channelWhatsapp,
    email: t.channelEmail,
    push: t.channelPush,
    marketing: t.channelMarketing,
  };

  const reload = useCallback(async () => {
    const d = await callOdoo<{ consents: ConsentRow[] }>("/customer/consent");
    setRows(d.consents || []);
  }, []);

  useEffect(() => {
    reload()
      .then(() => setLoading(false))
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, [reload, user]);

  // Escape key listener for modal
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setGrantingChannel(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  function latestFor(channel: string): ConsentRow | null {
    const ch = rows.filter((r) => r.channel === channel);
    return ch.length ? ch[0] : null;
  }

  async function handleGrantSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!grantingChannel || !proofInput.trim()) {
      setGrantError(locale === "bn" ? "সম্মতির প্রমাণ আবশ্যক" : "Consent proof is required");
      return;
    }
    setGrantBusy(true);
    setGrantError(null);
    try {
      const d = await callOdoo<{ consent?: { state: string }; error?: { message: string } }>(
        "/customer/consent", {
          action: "grant",
          channel: grantingChannel,
          proof: proofInput.trim(),
        });
      if (d.error) {
        setGrantError(d.error.message);
      } else {
        setNotice(t.consentNoticeSaved);
        setGrantingChannel(null);
        setProofInput("");
        reload();
      }
    } catch (err) {
      setGrantError((err as Error).message);
    } finally {
      setGrantBusy(false);
    }
  }

  async function handleWithdraw(channel: string) {
    const d = await callOdoo<{ consent?: { state: string }; error?: { message: string } }>(
      "/customer/consent", {
        action: "withdraw",
        channel,
      });
    setNotice(d.error ? d.error.message : t.consentNoticeSaved);
    if (!d.error) reload();
  }

  if (loading) return <Loading label={t.loading} />;
  if (error) return <LoadError what={t.loadErrorTitle(locale === "bn" ? "সম্মতি" : "Consent")} message={error} />;

  return (
    <main style={{ padding: 32, maxWidth: 800 }}>
      <SectionHead
        title={t.consentTitle}
        note={t.consentSubtitle}
      />
      {notice && (
        <p
          role="status"
          style={{
            padding: "10px 14px",
            marginBottom: 16,
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.status.info-bg"],
            color: tokens["color.status.info"],
            fontSize: tokens["typography.size.200"],
          }}
        >
          {notice}
        </p>
      )}

      <div style={{ display: "grid", gap: 12, marginTop: 16 }}>
        {CHANNELS.map((channel) => {
          const latest = latestFor(channel);
          const granted = latest?.state === "granted";
          return (
            <div key={channel} style={card}>
              <div style={{ flex: 1 }}>
                <strong style={{ fontSize: tokens["typography.size.300"] }}>
                  {channelNames[channel] || channel}
                </strong>
                <div
                  style={{
                    marginTop: 4,
                    fontSize: tokens["typography.size.200"],
                    color: tokens["color.text.secondary"],
                  }}
                >
                  {latest
                    ? (granted
                        ? t.consentGrantedWithProof(latest.date_granted, latest.proof)
                        : t.consentWithdrawn(latest.date_withdrawn || latest.date_granted))
                    : t.consentNone}
                </div>
              </div>
              {granted ? (
                <button
                  style={{ ...btn, background: tokens["color.status.error-bg"], color: tokens["color.status.error"] }}
                  onClick={() => handleWithdraw(channel)}
                >
                  {t.consentBtnWithdraw}
                </button>
              ) : (
                <button
                  style={{ ...btn, background: tokens["color.primary.base"], color: tokens["color.text.inverse"] }}
                  onClick={() => {
                    setGrantingChannel(channel);
                    setProofInput(`OTP-CONSENT-${Date.now().toString().slice(-6)}`);
                    setGrantError(null);
                  }}
                >
                  {t.consentBtnGrant}
                </button>
              )}
              {latest && <Pill state={latest.state} />}
            </div>
          );
        })}
      </div>

      {/* ACCESSIBLE GRANT CONSENT MODAL */}
      {grantingChannel && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="consent-modal-title"
          style={{
            position: "fixed",
            inset: 0,
            display: "grid",
            placeItems: "center",
            background: "rgba(0, 0, 0, 0.5)",
            backdropFilter: "blur(3px)",
            zIndex: 1000,
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) setGrantingChannel(null);
          }}
        >
          <div
            style={{
              maxWidth: 480,
              width: "100%",
              margin: 16,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.25)",
              padding: 24,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <h3 id="consent-modal-title" style={{ margin: 0, fontSize: tokens["typography.size.300"], color: tokens["color.primary.base"] }}>
                {t.consentModalTitle}
              </h3>
              <button
                type="button"
                onClick={() => setGrantingChannel(null)}
                aria-label={locale === "bn" ? "বন্ধ করুন" : "Close"}
                style={{ background: "transparent", border: "none", color: tokens["color.text.secondary"], fontSize: tokens["typography.size.400"], cursor: "pointer" }}
              >
                ✕
              </button>
            </div>

            <p style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"], margin: "0 0 16px" }}>
              {channelNames[grantingChannel] || grantingChannel} — {locale === "bn" ? "চ্যানেলে নোটিফিকেশন ও যোগাযোগ সম্মতি প্রদান:" : "channel communication consent:"}
            </p>

            <form onSubmit={handleGrantSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div>
                <label
                  htmlFor={proofInputId}
                  style={{ display: "block", marginBottom: 6, fontSize: tokens["typography.size.200"], fontWeight: 500 }}
                >
                  {t.consentProofLabel} *
                </label>
                <input
                  id={proofInputId}
                  type="text"
                  required
                  value={proofInput}
                  onChange={(e) => setProofInput(e.target.value)}
                  placeholder="e.g. OTP-CONSENT-884912"
                  style={inputStyle}
                />
                <small style={{ color: tokens["color.text.secondary"], display: "block", marginTop: 4 }}>
                  {locale === "bn"
                    ? "ডিজিটাল নিরাপত্তা ও পিডিপিএ আইন অনুযায়ী গ্রাহক সম্মতির স্থায়ী রেকর্ড সংরক্ষিত থাকে।"
                    : "Under PDPA / BTRC compliance, verifiable consent proofs are permanently recorded in the audit trail."}
                </small>
              </div>

              {grantError && (
                <p role="alert" style={{ margin: 0, padding: "8px 12px", background: tokens["color.status.error-bg"], color: tokens["color.status.error"], borderRadius: tokens["dimension.border.radius-sm"], fontSize: tokens["typography.size.200"] }}>
                  {grantError}
                </p>
              )}

              <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
                <button
                  type="button"
                  style={{ ...btn, background: tokens["color.surface.canvas"], color: tokens["color.text.secondary"], border: `1px solid ${tokens["color.border.default"]}` }}
                  onClick={() => setGrantingChannel(null)}
                >
                  {locale === "bn" ? "বাতিল" : "Cancel"}
                </button>
                <button
                  type="submit"
                  disabled={grantBusy}
                  style={{
                    ...btn,
                    background: tokens["color.primary.base"],
                    color: tokens["color.text.inverse"],
                    fontWeight: 600,
                  }}
                >
                  {grantBusy ? (locale === "bn" ? "সংরক্ষণ হচ্ছে…" : "Saving…") : t.consentConfirmGrant}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}

export default function ConsentPage() {
  return (
    <RequireAuth>
      <ConsentPageContent />
    </RequireAuth>
  );
}
