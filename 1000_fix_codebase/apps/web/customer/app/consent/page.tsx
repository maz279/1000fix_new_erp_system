"use client";

/* P01 PDPA consent dashboard — grant/withdraw per channel with the
 * status VISIBLE (the PP0 audit gap closed). A grant needs its proof
 * reference (an unverifiable grant is not a grant — server-enforced,
 * surfaced here inline). */
import { useCallback, useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface ConsentRow {
  id: number;
  channel: string;
  state: string;
  date_granted: string;
  date_withdrawn: string | null;
  proof: string;
}

const CHANNEL_BN: Record<string, string> = {
  sms: "এসএমএস", whatsapp: "হোয়াটসঅ্যাপ", email: "ইমেইল",
  push: "পুশ নোটিফিকেশন", marketing: "মার্কেটিং (সব চ্যানেল)",
};
// the LATEST decision per channel drives the dashboard state
const CHANNELS = ["sms", "whatsapp", "email", "push", "marketing"];

const card: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 20,
  display: "flex", alignItems: "center", gap: 16,
};
const btn: React.CSSProperties = {
  padding: "8px 16px",
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
};

export default function ConsentPage() {
  const [rows, setRows] = useState<ConsentRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const reload = useCallback(async () => {
    const d = await callOdoo<{ consents: ConsentRow[] }>("/customer/consent");
    setRows(d.consents || []);
  }, []);

  useEffect(() => {
    reload()
      .then(() => setLoading(false))
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, [reload]);

  function latestFor(channel: string): ConsentRow | null {
    const ch = rows.filter((r) => r.channel === channel);
    return ch.length ? ch[0] : null;
  }

  async function act(action: "grant" | "withdraw", channel: string) {
    let params: Record<string, unknown> = { action, channel };
    if (action === "grant") {
      const proof = window.prompt(
        "সম্মতির প্রমাণ দিন (OTP আইডি / ই-সাইন রেফারেন্স / স্বাক্ষরিত ফর্ম আইডি)");
      if (!proof) return; // no proof, no grant — the server rejects anyway
      params.proof = proof;
    }
    const d = await callOdoo<{ consent?: { state: string }; error?: { message: string } }>(
      "/customer/consent", params);
    setNotice(d.error ? d.error.message : "সম্মতি সংরক্ষিত হয়েছে");
    if (!d.error) reload();
  }

  if (loading) return <Loading label="লোড হচ্ছে…" />;
  if (error) return <LoadError what="সম্মতি" message={error} />;

  return (
    <main style={{ padding: 32, maxWidth: 760 }}>
      <SectionHead
        title="সম্মতি ড্যাশবোর্ড"
        note="প্রতি চ্যানেলে সম্মতি দিন বা প্রত্যাহার করুন — প্রত্যাহারের রেকর্ড স্থায়ীভাবে থাকে (BTRC/DND)"
      />
      {notice && (
        <p role="status" style={{
          padding: "10px 14px", marginBottom: 16,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.status.info-bg"],
          color: tokens["color.status.info"],
          fontSize: tokens["typography.size.200"],
        }}>{notice}</p>
      )}
      <div style={{ display: "grid", gap: 12 }}>
        {CHANNELS.map((channel) => {
          const latest = latestFor(channel);
          const granted = latest?.state === "granted";
          return (
            <div key={channel} style={card}>
              <div style={{ flex: 1 }}>
                <strong>{CHANNEL_BN[channel]}</strong>
                <div style={{
                  marginTop: 4, fontSize: tokens["typography.size.200"],
                  color: tokens["color.text.secondary"],
                }}>
                  {latest
                    ? (granted
                        ? `দেওয়া হয়েছে — ${latest.date_granted} (প্রমাণ: ${latest.proof})`
                        : `প্রত্যাহার — ${latest.date_withdrawn || latest.date_granted}`)
                    : "কোনো সম্মতি নেই"}
                </div>
              </div>
              {granted ? (
                <button style={{ ...btn, background: tokens["color.status.error-bg"], color: tokens["color.status.error"] }}
                  onClick={() => act("withdraw", channel)}>
                  প্রত্যাহার
                </button>
              ) : (
                <button style={{ ...btn, background: tokens["color.primary.base"], color: tokens["color.text.inverse"] }}
                  onClick={() => act("grant", channel)}>
                  সম্মতি দিন
                </button>
              )}
              {latest && <Pill state={latest.state} />}
            </div>
          );
        })}
      </div>
    </main>
  );
}
