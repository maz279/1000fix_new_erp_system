"use client";

/* P10 conversation detail — the transcript (the record, G4-04) beside
 * the customer 360 (open orders, devices, recent conversations) with
 * call control (claim / hand back / end — G4-05).
 * Everything renders from /contact/conversations/detail; call control goes
 * through /contact/handoff and the UI only changes state on a confirmed
 * backend answer. A missing id, a failed load or a failed action is shown
 * as an error — nothing is simulated. */
import { Suspense, useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { tokens, Pill, SectionHead, Loading } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

type ConvState = "new" | "with_ai" | "with_agent" | "resolved_ai" | "resolved_agent";

interface Turn {
  seq: number;
  speaker: "customer" | "ai" | "agent";
  text: string;
  lang: string;
  at: string;
}

interface Detail {
  id: number;
  channel: string;
  state: ConvState;
  intent: string;
  customer: string;
  transcript: Turn[];
  customer_360: {
    open_orders: { ref: string; state: string; device: string }[];
    devices: { model: string; identifier: string; warranty_status: string }[];
    recent_conversations: { id: number; channel: string; state: string; started_at: string }[];
  };
}

interface Notice {
  kind: "success" | "error";
  text: string;
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
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
};

const secondaryBtn: React.CSSProperties = {
  ...btn,
  background: tokens["color.surface.secondary"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
};

const card: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 24,
  boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
};

const emptyText: React.CSSProperties = {
  margin: 0,
  fontSize: tokens["typography.size.200"],
  color: tokens["color.text.secondary"],
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
  if (speaker === "ai") {
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
        AI Assistant (M32)
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
      Customer
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

function ErrorMain({ message }: { message: string }) {
  return (
    <main style={{ padding: "32px 40px", maxWidth: 1400, margin: "0 auto" }}>
      <p role="alert" style={{ color: tokens["color.status.error"], fontSize: tokens["typography.size.200"] }}>
        {message}
      </p>
      <a href="/" style={{ color: tokens["color.primary.base"], fontSize: tokens["typography.size.200"] }}>
        ← Back to the queue
      </a>
    </main>
  );
}

function ConversationDetail() {
  const params = useSearchParams();
  const rawId = params.get("id");
  const id = rawId && /^\d+$/.test(rawId) ? Number(rawId) : null;

  const [detail, setDetail] = useState<Detail | null>(null);
  const [loading, setLoading] = useState(id !== null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [busy, setBusy] = useState(false);
  const [handoffOpen, setHandoffOpen] = useState(false);
  const [handoffReason, setHandoffReason] = useState("");

  const reload = useCallback(async (cid: number) => {
    try {
      const d = await callOdoo<{ conversation?: Detail; error?: { message: string } } | undefined>(
        "/contact/conversations/detail",
        { conversation_id: cid }
      );
      if (!d) throw new Error("The server returned an empty response.");
      if (d.error) {
        setLoadError(d.error.message);
        setDetail(null);
      } else if (d.conversation) {
        setDetail(d.conversation);
        setLoadError(null);
      } else {
        setLoadError("The server returned no conversation.");
        setDetail(null);
      }
    } catch (e: unknown) {
      setLoadError(e instanceof Error ? e.message : String(e));
      setDetail(null);
    }
  }, []);

  useEffect(() => {
    if (id === null) return;
    setLoading(true);
    reload(id).finally(() => setLoading(false));
  }, [id, reload]);

  async function control(action: "claim" | "handoff" | "end", reason = "") {
    if (id === null) return;
    setBusy(true);
    try {
      const d = await callOdoo<
        { conversation?: { id: number; state: ConvState }; error?: { message: string } } | undefined
      >("/contact/handoff", { conversation_id: id, action, reason });
      if (!d) throw new Error("The server returned an empty response.");
      if (d.error) {
        setNotice({ kind: "error", text: `Could not ${action} this conversation: ${d.error.message}` });
        return;
      }
      const nextState = d.conversation?.state;
      if (nextState) {
        setDetail((prev) => (prev ? { ...prev, state: nextState } : prev));
      }
      setNotice({ kind: "success", text: `Done — conversation is now ${nextState ?? "updated"}.` });
      setHandoffOpen(false);
      setHandoffReason("");
    } catch (e: unknown) {
      setNotice({
        kind: "error",
        text: `Could not ${action} this conversation: ${e instanceof Error ? e.message : String(e)}`,
      });
    } finally {
      setBusy(false);
    }
  }

  function submitHandoff(e: React.FormEvent) {
    e.preventDefault();
    const reason = handoffReason.trim();
    if (!reason) return;
    void control("handoff", reason);
  }

  if (id === null) {
    return <ErrorMain message="No conversation selected — open one from the queue." />;
  }
  if (loading) return <Loading />;
  if (loadError || !detail) {
    return <ErrorMain message={`Failed to load conversation #${id}: ${loadError ?? "not found"}`} />;
  }

  const { open_orders, devices, recent_conversations } = detail.customer_360;

  return (
    <main style={{ padding: "32px 40px", maxWidth: 1400, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
        <div>
          <SectionHead
            title={detail.customer || "(Unidentified customer)"}
            note={`Conversation #${detail.id} · Channel: ${detail.channel.toUpperCase()} · Intent: ${detail.intent || "—"} (G4-04: the transcript is the system of record)`}
          />
          <div style={{ marginTop: 4 }}>
            <Pill state={detail.state} />
          </div>
        </div>

        {/* Call Controls */}
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          {(detail.state === "new" || detail.state === "with_ai") && (
            <button
              style={btn}
              disabled={busy}
              onClick={() => control("claim")}
              aria-label="Claim conversation from AI assistant"
            >
              Claim to Agent
            </button>
          )}

          {detail.state === "with_agent" && !handoffOpen && (
            <>
              <button
                style={secondaryBtn}
                disabled={busy}
                onClick={() => setHandoffOpen(true)}
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
                disabled={busy}
                onClick={() => control("end")}
                aria-label="End conversation and mark resolved"
              >
                ✓ End Conversation
              </button>
            </>
          )}
        </div>
      </div>

      {detail.state === "with_agent" && handoffOpen && (
        <form
          onSubmit={submitHandoff}
          aria-label="Hand back to AI"
          style={{ ...card, marginTop: 20, padding: 16, display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}
        >
          <div style={{ flex: "1 1 320px" }}>
            <label
              htmlFor="handoff-reason"
              style={{ display: "block", marginBottom: 6, fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}
            >
              Reason for handing back to the AI lane (recorded on the conversation)
            </label>
            <input
              id="handoff-reason"
              type="text"
              required
              autoFocus
              value={handoffReason}
              onChange={(e) => setHandoffReason(e.target.value)}
              style={{
                width: "100%",
                boxSizing: "border-box",
                padding: "8px 12px",
                background: tokens["color.surface.canvas"],
                color: tokens["color.text.primary"],
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-sm"],
                fontSize: tokens["typography.size.200"],
              }}
            />
          </div>
          <button type="submit" style={btn} disabled={busy || !handoffReason.trim()}>
            {busy ? "Handing back…" : "Hand back"}
          </button>
          <button
            type="button"
            style={secondaryBtn}
            disabled={busy}
            onClick={() => {
              setHandoffOpen(false);
              setHandoffReason("");
            }}
          >
            Cancel
          </button>
        </form>
      )}

      {notice && (
        <div
          role={notice.kind === "error" ? "alert" : "status"}
          aria-live="polite"
          style={{
            padding: "12px 18px",
            margin: "20px 0",
            borderRadius: tokens["dimension.border.radius-sm"],
            background: notice.kind === "error" ? tokens["color.status.error-bg"] : tokens["color.status.success-bg"],
            color: notice.kind === "error" ? tokens["color.status.error"] : tokens["color.status.success"],
            fontSize: tokens["typography.size.200"],
            border: `1px solid ${tokens["color.border.default"]}`,
          }}
        >
          {notice.text}
        </div>
      )}

      {/* Main 2-column layout: Transcript (Left 60%) + Customer 360 (Right 40%) */}
      <div style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: 24, marginTop: 24, alignItems: "start" }}>
        <section style={card} aria-label="Conversation Transcript Record">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: `1px solid ${tokens["color.border.default"]}`, paddingBottom: 12, marginBottom: 16 }}>
            <h2 style={{ margin: 0, fontSize: tokens["typography.size.300"], fontWeight: 600 }}>
              Conversation Transcript
            </h2>
            <span style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
              {detail.transcript.length} turns recorded
            </span>
          </div>

          {detail.transcript.length === 0 ? (
            <p style={emptyText}>No turns recorded yet.</p>
          ) : (
            <ol style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 14 }}>
              {detail.transcript.map((t) => (
                <li
                  key={t.seq}
                  style={{
                    padding: "14px 18px",
                    borderRadius: tokens["dimension.border.radius-sm"],
                    background: t.speaker === "ai" ? tokens["color.status.info-bg"] : tokens["color.surface.canvas"],
                    border: `1px solid ${tokens["color.border.default"]}`,
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
                      {t.at}{t.lang ? ` · ${t.lang.toUpperCase()}` : ""}
                    </span>
                  </div>
                  <p style={{ margin: "6px 0 0", fontSize: tokens["typography.size.200"], lineHeight: 1.5, color: tokens["color.text.primary"] }}>
                    {t.text}
                  </p>
                </li>
              ))}
            </ol>
          )}
        </section>

        <section style={{ display: "grid", gap: 20 }} aria-label="Customer 360 Panel">
          <div style={card}>
            <h3 style={{ margin: "0 0 12px", fontSize: tokens["typography.size.300"], fontWeight: 600 }}>
              Service Orders
            </h3>
            {open_orders.length === 0 ? (
              <p style={emptyText}>No service orders for this customer.</p>
            ) : (
              <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 10 }}>
                {open_orders.map((o) => (
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
                    {o.device && <div style={{ fontSize: tokens["typography.size.200"], marginTop: 4 }}>{o.device}</div>}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div style={card}>
            <h3 style={{ margin: "0 0 12px", fontSize: tokens["typography.size.300"], fontWeight: 600 }}>
              Registered Customer Devices
            </h3>
            {devices.length === 0 ? (
              <p style={emptyText}>No registered devices.</p>
            ) : (
              <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 10 }}>
                {devices.map((d, i) => (
                  <li
                    key={`${d.identifier}-${i}`}
                    style={{
                      padding: 12,
                      background: tokens["color.surface.canvas"],
                      borderRadius: tokens["dimension.border.radius-sm"],
                      border: `1px solid ${tokens["color.border.default"]}`,
                    }}
                  >
                    <div style={{ fontWeight: 600, fontSize: tokens["typography.size.200"] }}>{d.model || "(Unknown model)"}</div>
                    <div style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"], marginTop: 2 }}>
                      {d.identifier}
                    </div>
                    <div style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"], marginTop: 4, fontWeight: 500 }}>
                      Warranty: {d.warranty_status}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div style={card}>
            <h3 style={{ margin: "0 0 12px", fontSize: tokens["typography.size.300"], fontWeight: 600 }}>
              Recent Contact History
            </h3>
            {recent_conversations.length === 0 ? (
              <p style={emptyText}>No other conversations on record.</p>
            ) : (
              <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 8 }}>
                {recent_conversations.map((c) => (
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
                    <a href={`/conversation?id=${c.id}`} style={{ color: tokens["color.primary.base"] }}>
                      #{c.id} via <strong>{c.channel.toUpperCase()}</strong>
                    </a>
                    <span style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                      {c.started_at} ({c.state})
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}
