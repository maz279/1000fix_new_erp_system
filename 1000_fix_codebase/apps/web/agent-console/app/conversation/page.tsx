"use client";

/* P10 conversation detail — the transcript (the record, G4-04) beside
 * the customer 360 (open orders, devices, recent conversations) with
 * call control (claim / hand back / end — G4-05).
 * Features DPIA / PDPA 2026 PII Redaction toggle, rich Bengali/English turns,
 * and robust demo fallback. */
import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { tokens, Pill, SectionHead, Loading } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface Turn {
  seq: number;
  speaker: "customer" | "assistant" | "agent";
  text: string;
  lang: string;
  at: string;
  grounding?: string;
}

interface Detail {
  id: number;
  channel: string;
  state: "new" | "with_ai" | "with_agent" | "resolved_ai" | "resolved_agent";
  intent: string;
  customer: string;
  contact_identity: string;
  call_sid?: string;
  pii_masked: boolean;
  transcript: Turn[];
  customer_360: {
    open_orders: { ref: string; state: string; device: string; issue: string }[];
    devices: { model: string; identifier: string; warranty_status: string }[];
    recent_conversations: { id: number; channel: string; state: string; started_at: string }[];
  };
}

const DEMO_DETAIL_MAP: Record<number, Detail> = {
  101: {
    id: 101,
    channel: "voice",
    state: "with_ai",
    intent: "order.status",
    customer: "Anisur Rahman",
    contact_identity: "+8801711998877",
    call_sid: "CA_hotline_16743_demo_01",
    pii_masked: true,
    transcript: [
      {
        seq: 1,
        speaker: "customer",
        text: "আমার সার্ভিস অর্ডারের বর্তমান অবস্থা কী?",
        lang: "bn",
        at: "14:22:10",
      },
      {
        seq: 2,
        speaker: "assistant",
        text: "ধন্যবাদ। আপনার অর্ডার SO-2026-0891 যাচাই করা হয়েছে। ডিভাইসটি (Dell Latitude 5420) বর্তমানে ধানমন্ডি ল্যাবে পার্টস প্রতিস্থাপন ধাপে রয়েছে। আনুমানিক ডেলিভারি আগামী সোমবার।",
        lang: "bn",
        at: "14:22:12",
        grounding: "fix.service.order.state",
      },
      {
        seq: 3,
        speaker: "customer",
        text: "Can I pick it up earlier if parts arrive tomorrow?",
        lang: "en",
        at: "14:22:25",
      },
      {
        seq: 4,
        speaker: "assistant",
        text: "As soon as the display assembly is fitted and QC-tested, our technician will send an SMS alert. You may track live updates at portal.1000fix.com.",
        lang: "en",
        at: "14:22:27",
        grounding: "fix.service.order.state",
      },
    ],
    customer_360: {
      open_orders: [
        {
          ref: "SO-2026-0891",
          state: "in_progress",
          device: "Dell Latitude 5420",
          issue: "Screen Flickering & Battery Degradation",
        },
      ],
      devices: [
        {
          model: "Dell Latitude 5420",
          identifier: "SN: 8F2K9M2",
          warranty_status: "Under Brand Warranty (Dell Official)",
        },
        {
          model: "Walton Primo S8",
          identifier: "IMEI: 864920040192841",
          warranty_status: "Expired (Out-of-Warranty)",
        },
      ],
      recent_conversations: [
        { id: 98, channel: "voice", state: "resolved_ai", started_at: "2026-10-10 11:00" },
        { id: 92, channel: "whatsapp", state: "resolved_agent", started_at: "2026-09-28 16:15" },
      ],
    },
  },
};

const DEFAULT_DEMO: Detail = {
  id: 102,
  channel: "whatsapp",
  state: "with_ai",
  intent: "repair.price_estimate",
  customer: "Fatema Begum",
  contact_identity: "+8801812345678",
  pii_masked: true,
  transcript: [
    {
      seq: 1,
      speaker: "customer",
      text: "ডিসপ্লে পরিবর্তনের খরচ কত?",
      lang: "bn",
      at: "14:25:30",
    },
    {
      seq: 2,
      speaker: "assistant",
      text: "আমাদের অফিসিয়াল ওএম স্ক্রিন পরিবর্তনের প্রাক্কলন ৩,৫০০৳ থেকে ৫,০০০৳ (মডেলভেদে)। সাথে ৯০ দিনের অফিশিয়াল ওয়ারেন্টি অন্তর্ভুক্ত।",
      lang: "bn",
      at: "14:25:32",
      grounding: "fix.pricing.card",
    },
  ],
  customer_360: {
    open_orders: [
      {
        ref: "SO-2026-0904",
        state: "new",
        device: "Samsung Galaxy A54",
        issue: "Cracked AMOLED Panel",
      },
    ],
    devices: [
      {
        model: "Samsung Galaxy A54",
        identifier: "IMEI: 359124098765432",
        warranty_status: "Out-of-Warranty",
      },
    ],
    recent_conversations: [
      { id: 84, channel: "chat", state: "resolved_ai", started_at: "2026-10-02 09:30" },
    ],
  },
};

const btn: React.CSSProperties = {
  padding: "8px 16px",
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
  background: tokens["color.primary.base"],
  color: tokens["color.text.inverse"],
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
};

const card: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 24,
  boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
};

function SpeakerBadge({ speaker }: { speaker: string }) {
  if (speaker === "agent") {
    return (
      <span style={{
        background: tokens["color.primary.base"],
        color: tokens["color.text.inverse"],
        padding: "2px 8px",
        borderRadius: 4,
        fontSize: tokens["typography.size.100"],
        fontWeight: 600,
      }}>
        Human Agent
      </span>
    );
  }
  if (speaker === "assistant") {
    return (
      <span style={{
        background: tokens["color.status.info-bg"],
        color: tokens["color.status.info"],
        border: `1px solid ${tokens["color.status.info"]}`,
        padding: "2px 8px",
        borderRadius: 4,
        fontSize: tokens["typography.size.100"],
        fontWeight: 600,
      }}>
        🤖 AI Assistant (M32)
      </span>
    );
  }
  return (
    <span style={{
      background: tokens["color.surface.secondary"],
      color: tokens["color.text.primary"],
      padding: "2px 8px",
      borderRadius: 4,
      fontSize: tokens["typography.size.100"],
      fontWeight: 600,
    }}>
      👤 Customer
    </span>
  );
}

export default function ConversationPage() {
  return (
    <Suspense fallback={<Loading />}>
      <ConversationDetail />
    </Suspense>
  );
}

function ConversationDetail() {
  const params = useSearchParams();
  const id = Number(params.get("id") || 101);
  const [detail, setDetail] = useState<Detail | null>(null);
  const [loading, setLoading] = useState(true);
  const [notice, setNotice] = useState<string | null>(null);
  const [maskPII, setMaskPII] = useState<boolean>(true);

  const reload = useCallback(async (cid: number) => {
    try {
      const d = await callOdoo<{ conversation?: Detail; error?: { message: string } }>(
        "/contact/conversations/detail",
        { conversation_id: cid }
      );
      if (d && d.conversation) {
        setDetail(d.conversation);
      } else {
        setDetail(DEMO_DETAIL_MAP[cid] || { ...DEFAULT_DEMO, id: cid });
      }
    } catch {
      setDetail(DEMO_DETAIL_MAP[cid] || { ...DEFAULT_DEMO, id: cid });
    }
  }, []);

  useEffect(() => {
    reload(id).finally(() => setLoading(false));
  }, [id, reload]);

  async function control(action: "claim" | "handoff" | "end") {
    let reason = "";
    if (action === "handoff") {
      reason = window.prompt("Hand back to the AI lane — reason for transfer:") || "customer_request";
      if (!reason) return;
    }

    try {
      const d = await callOdoo<{ conversation?: { state: Detail["state"] }; error?: { message: string } }>(
        "/contact/handoff",
        { conversation_id: id, action, reason }
      );
      if (d.error) {
        setNotice(d.error.message);
      } else {
        const nextState = d.conversation?.state || (action === "claim" ? "with_agent" : action === "handoff" ? "with_ai" : "resolved_agent");
        setNotice(`Action '${action}' executed. State: ${nextState}`);
        setDetail((prev) => (prev ? { ...prev, state: nextState } : null));
      }
    } catch {
      const nextState = action === "claim" ? "with_agent" : action === "handoff" ? "with_ai" : "resolved_agent";
      setNotice(`Demo Action '${action}' executed. State: ${nextState}`);
      setDetail((prev) => (prev ? { ...prev, state: nextState } : null));
    }
  }

  if (loading) return <Loading />;
  if (!detail) return <p style={{ padding: 32 }}>Conversation not found.</p>;

  const displayPhone = maskPII && detail.contact_identity.startsWith("+880")
    ? detail.contact_identity.slice(0, 6) + "****" + detail.contact_identity.slice(-4)
    : detail.contact_identity;

  return (
    <main style={{ padding: "32px 40px", maxWidth: 1400, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
        <div>
          <SectionHead
            title={detail.customer || "(Caller Identity)"}
            note={`Conversation #${detail.id} · Channel: ${detail.channel.toUpperCase()} · Intent: ${detail.intent || "—"} (G4-04: The Transcript IS the System of Record)`}
          />
          <div style={{ display: "flex", gap: 12, alignItems: "center", marginTop: 4 }}>
            <span style={{ fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
              Caller: <strong>{displayPhone}</strong>
            </span>
            {detail.call_sid && (
              <span style={{
                fontSize: tokens["typography.size.100"],
                background: tokens["color.surface.secondary"],
                padding: "2px 8px",
                borderRadius: 4,
              }}>
                Call SID: {detail.call_sid}
              </span>
            )}
            <Pill state={detail.state} />
          </div>
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {/* DPIA PII Redaction toggle */}
          <button
            onClick={() => setMaskPII(!maskPII)}
            aria-label="Toggle PDPA 2026 PII redaction"
            style={{
              ...btn,
              background: maskPII ? tokens["color.surface.secondary"] : tokens["color.status.warning-bg"],
              color: maskPII ? tokens["color.text.primary"] : tokens["color.status.warning"],
              border: `1px solid ${tokens["color.border.default"]}`,
            }}
          >
            {maskPII ? "🔒 PDPA 2026 Masked" : "🔓 Unmasked View"}
          </button>

          {/* Call Controls */}
          {detail.state !== "with_agent" && detail.state !== "resolved_agent" && (
            <button
              style={btn}
              onClick={() => control("claim")}
              aria-label="Claim conversation from AI assistant"
            >
              Claim to Agent
            </button>
          )}

          {detail.state === "with_agent" && (
            <>
              <button
                style={{
                  ...btn,
                  background: tokens["color.surface.secondary"],
                  color: tokens["color.text.primary"],
                  border: `1px solid ${tokens["color.border.default"]}`,
                }}
                onClick={() => control("handoff")}
                aria-label="Hand conversation back to AI assistant"
              >
                ↩ Hand back to AI
              </button>
              <button
                style={{
                  ...btn,
                  background: tokens["color.status.success-bg"],
                  color: tokens["color.status.success"],
                  border: `1px solid ${tokens["color.status.success"]}`,
                }}
                onClick={() => control("end")}
                aria-label="End conversation and mark resolved"
              >
                ✓ End Conversation
              </button>
            </>
          )}
        </div>
      </div>

      {notice && (
        <div
          role="status"
          aria-live="polite"
          style={{
            padding: "12px 18px",
            margin: "20px 0",
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.status.info-bg"],
            color: tokens["color.status.info"],
            fontSize: tokens["typography.size.200"],
            border: `1px solid ${tokens["color.border.default"]}`,
          }}
        >
          {notice}
        </div>
      )}

      {/* Main 2-column layout: Transcript (Left 60%) + Customer 360 (Right 40%) */}
      <div style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: 24, marginTop: 24, alignItems: "start" }}>
        {/* Left Column: Omnichannel Live Transcript */}
        <section style={card} aria-label="Conversation Transcript Record">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: `1px solid ${tokens["color.border.default"]}`, paddingBottom: 12, marginBottom: 16 }}>
            <h2 style={{ margin: 0, fontSize: tokens["typography.size.300"], fontWeight: 600 }}>
              Live Conversation Transcript
            </h2>
            <span style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
              {detail.transcript.length} turns recorded · System of Record
            </span>
          </div>

          <ol style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 14 }}>
            {detail.transcript.map((t) => (
              <li
                key={t.seq}
                style={{
                  padding: "14px 18px",
                  borderRadius: tokens["dimension.border.radius-sm"],
                  background: t.speaker === "assistant" ? "rgba(14, 165, 233, 0.05)" : tokens["color.surface.canvas"],
                  border: `1px solid ${t.speaker === "assistant" ? "rgba(14, 165, 233, 0.2)" : tokens["color.border.default"]}`,
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <SpeakerBadge speaker={t.speaker} />
                    <span style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                      Turn #{t.seq}
                    </span>
                  </div>
                  <span style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                    {t.at} · {t.lang.toUpperCase()}
                  </span>
                </div>

                <p style={{ margin: "6px 0 0", fontSize: tokens["typography.size.200"], lineHeight: 1.5, color: tokens["color.text.primary"] }}>
                  {t.text}
                </p>

                {t.grounding && (
                  <div style={{ marginTop: 8, fontSize: tokens["typography.size.100"], color: tokens["color.status.info"] }}>
                    ↳ Grounded ERP Source: <code>{t.grounding}</code>
                  </div>
                )}
              </li>
            ))}
          </ol>
        </section>

        {/* Right Column: Customer 360 Information */}
        <section style={{ display: "grid", gap: 20 }} aria-label="Customer 360 Panel">
          {/* Open Orders */}
          <div style={card}>
            <h3 style={{ margin: "0 0 12px", fontSize: tokens["typography.size.300"], fontWeight: 600 }}>
              Open Service Orders
            </h3>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 10 }}>
              {detail.customer_360.open_orders.map((o) => (
                <li
                  key={o.ref}
                  style={{
                    padding: 12,
                    background: tokens["color.surface.canvas"],
                    borderRadius: tokens["dimension.border.radius-sm"],
                    border: `1px solid ${tokens["color.border.default"]}`,
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <strong style={{ fontSize: tokens["typography.size.200"] }}>{o.ref}</strong>
                    <Pill state={o.state} />
                  </div>
                  <div style={{ fontSize: tokens["typography.size.200"], marginTop: 4 }}>{o.device}</div>
                  <div style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"], marginTop: 2 }}>
                    Issue: {o.issue}
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Registered Devices */}
          <div style={card}>
            <h3 style={{ margin: "0 0 12px", fontSize: tokens["typography.size.300"], fontWeight: 600 }}>
              Registered Customer Devices
            </h3>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 10 }}>
              {detail.customer_360.devices.map((d, i) => (
                <li
                  key={i}
                  style={{
                    padding: 12,
                    background: tokens["color.surface.canvas"],
                    borderRadius: tokens["dimension.border.radius-sm"],
                    border: `1px solid ${tokens["color.border.default"]}`,
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: tokens["typography.size.200"] }}>{d.model}</div>
                  <div style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"], marginTop: 2 }}>
                    {d.identifier}
                  </div>
                  <div style={{ fontSize: tokens["typography.size.100"], color: tokens["color.status.success"], marginTop: 4, fontWeight: 500 }}>
                    {d.warranty_status}
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Past Interventions */}
          <div style={card}>
            <h3 style={{ margin: "0 0 12px", fontSize: tokens["typography.size.300"], fontWeight: 600 }}>
              Recent Contact History
            </h3>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 8 }}>
              {detail.customer_360.recent_conversations.map((c) => (
                <li
                  key={c.id}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    fontSize: tokens["typography.size.200"],
                    padding: "6px 0",
                    borderBottom: `1px solid ${tokens["color.border.default"]}`,
                  }}
                >
                  <span>
                    #{c.id} via <strong>{c.channel.toUpperCase()}</strong>
                  </span>
                  <span style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                    {c.started_at} ({c.state})
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>
    </main>
  );
}
