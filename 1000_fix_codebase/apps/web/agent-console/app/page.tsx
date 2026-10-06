"use client";

/* P10 unified queue — live conversations across channels, oldest first.
 * Claiming a conversation hands it AI→agent (G4-05); the transcript +
 * customer 360 open on the conversation page. Softphone endpoints come
 * from /contact/softphone (deployment config only — nulls when unset). */
import { useCallback, useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Loading, LoadError, Stat } from "../lib/imports";
import { callOdoo } from "../lib/api";

interface Conversation {
  id: number; channel: string; state: string; intent: string;
  customer: string; contact_identity: string; started_at: string; turns: number;
}
interface Softphone {
  ws_url: string | null; sip_realm: string | null;
  click_to_call_prefix: string | null; vendor: string | null;
}

const btn: React.CSSProperties = {
  padding: "8px 16px",
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
  background: tokens["color.primary.base"],
  color: tokens["color.text.inverse"],
};

export default function QueuePage() {
  const [rows, setRows] = useState<Conversation[]>([]);
  const [softphone, setSoftphone] = useState<Softphone | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const reload = useCallback(async () => {
    const d = await callOdoo<{ conversations?: Conversation[] }>("/contact/conversations");
    setRows(d.conversations || []);
  }, []);

  useEffect(() => {
    Promise.all([
      reload(),
      callOdoo<{ softphone?: Softphone }>("/contact/softphone").then((d) => setSoftphone(d.softphone || null)),
    ]).then(() => setLoading(false)).catch((e: Error) => setError(e.message));
    const t = setInterval(reload, 15000); // live queue refresh
    return () => clearInterval(t);
  }, [reload]);

  async function claim(c: Conversation) {
    const d = await callOdoo<{ conversation?: { state: string }; error?: { message: string } }>(
      "/contact/handoff", { conversation_id: c.id, action: "claim" });
    setNotice(d.error ? d.error.message : `Conversation #${c.id} claimed`);
    if (!d.error) reload();
  }

  if (loading) return <Loading />;
  if (error) return <LoadError what="queue" message={error} />;

  const withAI = rows.filter((r) => r.state === "with_ai").length;

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="Unified Queue"
        note="All channels, oldest first — hotline 16743, WhatsApp, chat, email, in-app (G4-04: the transcript is the record)"
      />
      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Stat label="Live" value={rows.length} />
        <Stat label="With AI" value={withAI} tone="primary" />
      </div>
      {notice && (
        <p role="status" style={{
          padding: "10px 14px", marginBottom: 16,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.status.info-bg"],
          color: tokens["color.status.info"],
          fontSize: tokens["typography.size.200"],
        }}>{notice}</p>
      )}

      {softphone && (
        <section style={{
          padding: "10px 14px", marginBottom: 16,
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.surface.primary"],
          fontSize: tokens["typography.size.200"],
          color: tokens["color.text.secondary"],
        }}>
          Softphone seam:{" "}
          {softphone.vendor ? `vendor ${softphone.vendor}` : "no vendor configured"}
          {softphone.ws_url ? " · WebSocket connected" : " · no WebSocket (click-to-copy fallback)"}
          {softphone.click_to_call_prefix ? ` · dial prefix ${softphone.click_to_call_prefix}` : ""}
        </section>
      )}

      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: tokens["color.surface.secondary"] }}>
            {["Waiting since", "Channel", "Customer", "Intent", "Turns", "State", ""].map((h) => (
              <th key={h} style={{
                textAlign: "left", padding: "8px 16px",
                fontSize: tokens["typography.size.200"],
                color: tokens["color.text.secondary"],
                borderBottom: `1px solid ${tokens["color.border.default"]}`,
              }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((c) => (
            <tr key={c.id} style={{ borderBottom: `1px solid ${tokens["color.border.default"]}` }}>
              <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"] }}>
                {c.started_at.slice(11, 16)}
              </td>
              <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"] }}>{c.channel}</td>
              <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"] }}>
                {c.customer || c.contact_identity || "(unknown)"}
              </td>
              <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"] }}>{c.intent || "—"}</td>
              <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"] }}>{c.turns}</td>
              <td style={{ padding: "8px 16px" }}><Pill state={c.state} /></td>
              <td style={{ padding: "8px 16px", display: "flex", gap: 8 }}>
                <a href={`/conversation?id=${c.id}`} style={{
                  ...btn, textDecoration: "none",
                  background: tokens["color.surface.secondary"],
                  color: tokens["color.text.primary"],
                }}>Open 360</a>
                {(c.state === "new" || c.state === "with_ai") && (
                  <button style={btn} onClick={() => claim(c)}>Claim</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length === 0 && (
        <p style={{ color: tokens["color.text.secondary"], marginTop: 16 }}>Queue is clear.</p>
      )}
    </main>
  );
}
