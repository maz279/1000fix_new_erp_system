"use client";

/* P10 conversation detail — the transcript (the record, G4-04) beside
 * the customer 360 (open orders, devices, recent conversations) with
 * call control (claim / hand back / end — G4-05). Uses a Suspense-
 * friendly client read of the query string. */
import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { tokens, Pill, SectionHead, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface Turn { seq: number; speaker: string; text: string; lang: string; at: string }
interface Detail {
  id: number; channel: string; state: string; intent: string; customer: string;
  transcript: Turn[];
  customer_360: {
    open_orders: { ref: string; state: string; device: string }[];
    devices: { model: string; identifier: string; warranty_status: string }[];
    recent_conversations: { id: number; channel: string; state: string; started_at: string }[];
  };
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
const card: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 20,
};

function Speaker({ s }: { s: string }) {
  const isAgent = s === "agent";
  const isAI = s === "assistant";
  return (
    <strong style={{
      color: isAgent ? tokens["color.primary.base"]
        : isAI ? tokens["color.status.info"] : tokens["color.text.secondary"],
    }}>
      {isAgent ? "Agent" : isAI ? "Assistant" : s === "customer" ? "Customer" : s}
    </strong>
  );
}

export default function ConversationPage() {
  // useSearchParams needs a Suspense boundary for static prerender
  return (
    <Suspense fallback={<Loading />}>
      <ConversationDetail />
    </Suspense>
  );
}

function ConversationDetail() {
  const params = useSearchParams();
  const id = Number(params.get("id") || 0);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const reload = useCallback(async (cid: number) => {
    const d = await callOdoo<{ conversation?: Detail; error?: { message: string } }>(
      "/contact/conversations/detail", { conversation_id: cid });
    if (d.error) setError(d.error.message);
    else setDetail(d.conversation || null);
  }, []);

  useEffect(() => {
    if (!id) { setError("Missing ?id="); setLoading(false); return; }
    reload(id).then(() => setLoading(false)).catch((e: Error) => setError(e.message));
  }, [id, reload]);

  async function control(action: "claim" | "handoff" | "end") {
    let reason = "";
    if (action === "handoff") {
      reason = window.prompt("Hand back to the AI lane — reason:") || "";
      if (!reason) return;
    }
    const d = await callOdoo<{ conversation?: { state: string }; error?: { message: string } }>(
      "/contact/handoff", { conversation_id: id, action, reason });
    setNotice(d.error ? d.error.message : `Conversation #${id}: ${d.conversation?.state}`);
    if (!d.error) reload(id);
  }

  if (loading) return <Loading />;
  if (error) return <LoadError what="conversation" message={error} />;
  if (!detail) return <LoadError what="conversation" message="not found" />;

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title={detail.customer || "(unknown caller)"}
        note={`#${detail.id} · ${detail.channel} · intent ${detail.intent || "—"} — the transcript IS the record (G4-04)`}
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

      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {detail.state !== "with_agent" && detail.state !== "resolved_agent" ? (
          <button style={btn} onClick={() => control("claim")}>Claim</button>
        ) : null}
        {detail.state === "with_agent" && (
          <>
            <button style={{ ...btn, background: tokens["color.surface.secondary"], color: tokens["color.text.primary"] }}
              onClick={() => control("handoff")}>Hand back to AI</button>
            <button style={{ ...btn, background: tokens["color.status.success-bg"], color: tokens["color.status.success"] }}
              onClick={() => control("end")}>End conversation</button>
          </>
        )}
        <Pill state={detail.state} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: 16, alignItems: "start" }}>
        <section style={card}>
          <strong>Transcript</strong>
          <ul style={{ listStyle: "none", padding: 0, margin: "12px 0 0", display: "grid", gap: 10 }}>
            {detail.transcript.map((t) => (
              <li key={t.seq} style={{
                padding: 10, borderRadius: tokens["dimension.border.radius-sm"],
                background: tokens["color.surface.canvas"],
                fontSize: tokens["typography.size.200"],
              }}>
                <Speaker s={t.speaker} /> — {t.text}
                <div style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.100"] }}>
                  {t.at} · {t.lang}
                </div>
              </li>
            ))}
            {detail.transcript.length === 0 && (
              <li style={{ color: tokens["color.text.secondary"] }}>No turns recorded.</li>
            )}
          </ul>
        </section>

        <section style={{ ...card, display: "grid", gap: 16 }}>
          <div>
            <strong>Open orders</strong>
            <ul style={{ margin: "8px 0 0", paddingLeft: 16, fontSize: tokens["typography.size.200"] }}>
              {detail.customer_360.open_orders.map((o) => (
                <li key={o.ref}>{o.ref} — {o.device} <Pill state={o.state} /></li>
              ))}
              {detail.customer_360.open_orders.length === 0 && <li>None</li>}
            </ul>
          </div>
          <div>
            <strong>Devices</strong>
            <ul style={{ margin: "8px 0 0", paddingLeft: 16, fontSize: tokens["typography.size.200"] }}>
              {detail.customer_360.devices.map((d, i) => (
                <li key={i}>{d.model} ({d.identifier}) — {d.warranty_status}</li>
              ))}
              {detail.customer_360.devices.length === 0 && <li>None</li>}
            </ul>
          </div>
          <div>
            <strong>Recent conversations</strong>
            <ul style={{ margin: "8px 0 0", paddingLeft: 16, fontSize: tokens["typography.size.200"] }}>
              {detail.customer_360.recent_conversations.map((c) => (
                <li key={c.id}>#{c.id} {c.channel} — {c.state}</li>
              ))}
              {detail.customer_360.recent_conversations.length === 0 && <li>None</li>}
            </ul>
          </div>
        </section>
      </div>
    </main>
  );
}
