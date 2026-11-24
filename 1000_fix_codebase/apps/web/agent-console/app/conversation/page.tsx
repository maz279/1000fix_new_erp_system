"use client";

/**
 * P10 conversation workspace — the transcript (the record, G4-04) beside the
 * customer 360, with the agent's real actions: claim from the AI lane, record
 * a reply turn, hand back with a reason, or close through the mandatory
 * wrap-up gate (disposition + substantive notes + FCR, REQ-27.1).
 *
 * Every read/write goes through the staff portal API; the model's transitions
 * decide, so nothing here invents a state. A failed load or action is shown
 * as an error — nothing is simulated.
 */
import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { tokens, Loading } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  Badge,
  CHANNEL_LABEL,
  Panel,
  StateBadge,
  fmtDhaka,
  linkButtonStyle,
  pageStyle,
  primaryLinkStyle,
  selectStyle,
  tdStyle,
  textareaStyle,
  thStyle,
} from "../../components/ui";

type ConvState = "new" | "with_ai" | "with_agent" | "resolved_ai" | "resolved_agent" | "abandoned";

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
  contact_identity: string;
  agent: string;
  agent_id: number | null;
  queued_at: string;
  started_at: string;
  answered_at: string;
  ended_at: string;
  sla_due_at: string;
  handoff_reason: string;
  ai_resolved: boolean;
  disposition: { id: number; code: string; name: string } | null;
  wrapup_notes: string;
  fcr: boolean;
  priority: number;
  entitlement: string;
  transcript: Turn[];
  customer_360: {
    open_orders: { ref: string; state: string; device: string }[];
    devices: { model: string; identifier: string; warranty_status: string }[];
    recent_conversations: { id: number; channel: string; state: string; started_at: string }[];
  };
}

interface Disposition {
  id: number;
  code: string;
  name: string;
  category: string;
  is_resolved: boolean;
}

interface Notice {
  kind: "success" | "error";
  text: string;
}

function utcMs(value: string): number | null {
  if (!value) return null;
  const raw = value.includes("T") ? value : `${value.replace(" ", "T")}Z`;
  const t = Date.parse(raw);
  return Number.isNaN(t) ? null : t;
}

function SlaBadge({ due, answered }: { due: string; answered: string }) {
  if (answered) return <Badge tone="success">answered</Badge>;
  if (!due) return <Badge tone="neutral">no SLA clock</Badge>;
  const dueMs = utcMs(due);
  if (dueMs == null) return <Badge tone="neutral">—</Badge>;
  const diff = Math.round((dueMs - Date.now()) / 60_000);
  if (diff < 0) return <Badge tone="error">breached {Math.abs(diff)}m</Badge>;
  return <Badge tone={diff <= 5 ? "warning" : "success"}>due in {diff}m</Badge>;
}

function SpeakerBadge({ speaker }: { speaker: string }) {
  if (speaker === "agent") return <Badge tone="primary">Human agent</Badge>;
  if (speaker === "ai") return <Badge tone="info">AI assistant</Badge>;
  return <Badge tone="neutral">Customer</Badge>;
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
    <main style={pageStyle}>
      <p role="alert" style={{ color: tokens["color.status.error"], fontSize: 13 }}>
        {message}
      </p>
      <a href="/queue" style={{ color: tokens["color.primary.base"], fontSize: 13 }}>
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
  const [dispositions, setDispositions] = useState<Disposition[]>([]);
  const [loading, setLoading] = useState(id !== null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [busy, setBusy] = useState(false);
  const [handoffOpen, setHandoffOpen] = useState(false);
  const [handoffReason, setHandoffReason] = useState("");
  const [wrapupOpen, setWrapupOpen] = useState(false);
  const [dispositionId, setDispositionId] = useState("");
  const [wrapupNotes, setWrapupNotes] = useState("");
  const [fcr, setFcr] = useState(false);
  const [wrapupError, setWrapupError] = useState<string | null>(null);
  const [reply, setReply] = useState("");
  const [replyLang, setReplyLang] = useState("bn");
  const [replyError, setReplyError] = useState<string | null>(null);
  const endRef = useRef<HTMLDivElement>(null);

  const reload = useCallback(async (cid: number) => {
    try {
      const d = await callOdoo<{ conversation?: Detail; error?: { message: string } }>(
        "/contact/portal/conversation",
        { conversation_id: cid }
      );
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

  useEffect(() => {
    callOdoo<{ dispositions?: Disposition[]; error?: { message: string } }>("/contact/portal/dispositions")
      .then((d) => setDispositions(d.dispositions ?? []))
      .catch(() => setDispositions([]));
  }, []);

  async function control(action: "claim" | "handoff", reason = "") {
    if (id === null) return;
    setBusy(true);
    setNotice(null);
    try {
      const d = await callOdoo<{ conversation?: { id: number; state: ConvState }; error?: { message: string } }>(
        "/contact/handoff",
        { conversation_id: id, action, reason }
      );
      if (d.error) {
        setNotice({ kind: "error", text: `Could not ${action} this conversation: ${d.error.message}` });
        return;
      }
      setNotice({ kind: "success", text: `Done — conversation is now ${d.conversation?.state ?? "updated"}.` });
      setHandoffOpen(false);
      setHandoffReason("");
      await reload(id);
    } catch (e: unknown) {
      setNotice({ kind: "error", text: `Could not ${action} this conversation: ${e instanceof Error ? e.message : String(e)}` });
    } finally {
      setBusy(false);
    }
  }

  async function submitHandoff(e: React.FormEvent) {
    e.preventDefault();
    const reason = handoffReason.trim();
    if (!reason) return;
    await control("handoff", reason);
  }

  async function submitReply(e: React.FormEvent) {
    e.preventDefault();
    if (id === null || !reply.trim()) return;
    setBusy(true);
    setReplyError(null);
    try {
      const d = await callOdoo<{
        turn?: Turn;
        conversation?: { id: number; state: ConvState };
        error?: { message: string };
      }>("/contact/portal/reply", { conversation_id: id, text: reply.trim(), lang: replyLang });
      if (d.error) throw new Error(d.error.message);
      if (d.turn) {
        setDetail((prev) => (prev ? { ...prev, transcript: [...prev.transcript, d.turn as Turn] } : prev));
      }
      setReply("");
      setNotice({ kind: "success", text: "Reply recorded on the transcript." });
      window.setTimeout(() => endRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    } catch (err) {
      setReplyError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function submitWrapup(e: React.FormEvent) {
    e.preventDefault();
    if (id === null || !dispositionId || wrapupNotes.trim().length < 20) return;
    setBusy(true);
    setWrapupError(null);
    try {
      const d = await callOdoo<{
        conversation?: { id: number; state: ConvState; disposition: string; fcr: boolean };
        error?: { message: string };
      }>("/contact/portal/wrapup", {
        conversation_id: id,
        disposition_id: Number(dispositionId),
        wrapup_notes: wrapupNotes.trim(),
        fcr,
      });
      if (d.error) throw new Error(d.error.message);
      setNotice({ kind: "success", text: `Conversation closed — ${d.conversation?.state ?? "resolved"}.` });
      setWrapupOpen(false);
      await reload(id);
    } catch (err) {
      setWrapupError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (id === null) return <ErrorMain message="No conversation selected — open one from the queue." />;
  if (loading) return <Loading />;
  if (loadError || !detail) {
    return <ErrorMain message={`Failed to load conversation #${id}: ${loadError ?? "not found"}`} />;
  }

  const { open_orders, devices, recent_conversations } = detail.customer_360;
  const active = ["new", "with_ai", "with_agent"].includes(detail.state);

  return (
    <main style={pageStyle}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16, marginBottom: 18 }}>
        <div>
          <a href="/queue" style={{ fontSize: 12, color: tokens["color.text.secondary"], textDecoration: "none" }}>
            ← Queue
          </a>
          <h1 style={{ margin: "6px 0 6px", fontSize: tokens["typography.size.500"], color: tokens["color.text.primary"] }}>
            {detail.customer || "(Unidentified caller)"}
          </h1>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center", fontSize: 12.5, color: tokens["color.text.secondary"] }}>
            <span>Conversation #{detail.id}</span>
            <span>· {CHANNEL_LABEL[detail.channel] ?? detail.channel}</span>
            <span>· {detail.contact_identity || "no identity"}</span>
            <StateBadge state={detail.state} />
            <SlaBadge due={detail.sla_due_at} answered={detail.answered_at} />
            {detail.priority > 0 && <Badge tone={detail.priority >= 3 ? "error" : "info"}>P{detail.priority}</Badge>}
          </div>
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          {(detail.state === "new" || detail.state === "with_ai") && (
            <button type="button" style={primaryLinkStyle} disabled={busy} onClick={() => void control("claim")}>
              Claim to agent
            </button>
          )}
          {detail.state === "with_agent" && (
            <>
              <button type="button" style={linkButtonStyle} disabled={busy} onClick={() => setHandoffOpen(true)}>
                ↩ Hand back to AI
              </button>
              <button
                type="button"
                style={{ ...primaryLinkStyle, background: tokens["color.status.success"], border: "none", cursor: busy ? "wait" : "pointer" }}
                disabled={busy}
                onClick={() => {
                  setWrapupOpen(true);
                  setWrapupError(null);
                }}
              >
                ✓ Wrap up &amp; close
              </button>
            </>
          )}
        </div>
      </div>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 14 }}>
        <Badge tone="info">Intent: {detail.intent || "unclassified"}</Badge>
        <Badge tone="neutral">Agent: {detail.agent || "unclaimed"}</Badge>
        {detail.handoff_reason && <Badge tone="warning">Handoff: {detail.handoff_reason}</Badge>}
        {detail.entitlement && <Badge tone="neutral">Entitlement: {detail.entitlement}</Badge>}
        {detail.ai_resolved && <Badge tone="success">AI-resolved</Badge>}
      </div>

      {notice && (
        <div
          role={notice.kind === "error" ? "alert" : "status"}
          style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: notice.kind === "error" ? tokens["color.status.error-bg"] : tokens["color.status.success-bg"], color: notice.kind === "error" ? tokens["color.status.error"] : tokens["color.status.success"], fontSize: 12.5 }}
        >
          {notice.text}
        </div>
      )}

      {detail.state === "with_agent" && handoffOpen && (
        <form onSubmit={submitHandoff} style={{ marginBottom: 14, padding: 14, border: `1px solid ${tokens["color.border.default"]}`, borderRadius: tokens["dimension.border.radius-md"], background: tokens["color.surface.primary"], display: "flex", gap: 10, alignItems: "flex-end", flexWrap: "wrap" }}>
          <div style={{ flex: "1 1 320px" }}>
            <label htmlFor="handoff-reason" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>
              Reason for handing back to the AI lane (recorded on the conversation)
            </label>
            <input
              id="handoff-reason"
              type="text"
              required
              autoFocus
              value={handoffReason}
              onChange={(e) => setHandoffReason(e.target.value)}
              style={{ ...selectStyle, width: "100%", boxSizing: "border-box" }}
            />
          </div>
          <button type="submit" style={primaryLinkStyle} disabled={busy || !handoffReason.trim()}>
            Hand back
          </button>
          <button type="button" style={linkButtonStyle} disabled={busy} onClick={() => { setHandoffOpen(false); setHandoffReason(""); }}>
            Cancel
          </button>
        </form>
      )}

      {detail.state === "with_agent" && wrapupOpen && (
        <Panel title="Wrap-up — closes the conversation">
          <form onSubmit={submitWrapup} style={{ padding: 16, display: "grid", gap: 12 }}>
            <p style={{ margin: 0, fontSize: 12, color: tokens["color.text.secondary"] }}>
              A conversation cannot close without a disposition, notes of at least 20 characters, and the FCR
              answer (REQ-27.1). Voice calls also need a verified recording digest on the call record.
            </p>
            <div>
              <label htmlFor="wrapup-disposition" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>
                Disposition (required)
              </label>
              <select
                id="wrapup-disposition"
                required
                value={dispositionId}
                onChange={(e) => setDispositionId(e.target.value)}
                style={{ ...selectStyle, minWidth: 320 }}
              >
                <option value="">Select a disposition code…</option>
                {dispositions.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.code} — {d.name}
                  </option>
                ))}
              </select>
              {dispositions.length === 0 && (
                <span style={{ marginLeft: 10, fontSize: 11.5, color: tokens["color.status.warning"] }}>
                  No active disposition codes — ask a supervisor to configure the register.
                </span>
              )}
            </div>
            <div>
              <label htmlFor="wrapup-notes" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>
                Wrap-up notes (required, 20+ characters)
              </label>
              <textarea
                id="wrapup-notes"
                required
                value={wrapupNotes}
                onChange={(e) => setWrapupNotes(e.target.value)}
                placeholder="What was agreed? What is the next step?"
                style={textareaStyle}
              />
              <span style={{ fontSize: 11.5, color: wrapupNotes.trim().length < 20 ? tokens["color.status.warning"] : tokens["color.text.secondary"] }}>
                {wrapupNotes.trim().length} / 20 minimum
              </span>
            </div>
            <label style={{ display: "inline-flex", alignItems: "center", gap: 8, fontSize: 12.5 }}>
              <input type="checkbox" checked={fcr} onChange={(e) => setFcr(e.target.checked)} />
              First-contact resolution (FCR)
            </label>
            {wrapupError && (
              <p role="alert" style={{ margin: 0, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.error-bg"], color: tokens["color.status.error"], fontSize: 12.5 }}>
                {wrapupError}
              </p>
            )}
            <div style={{ display: "flex", gap: 8 }}>
              <button
                type="submit"
                style={{ ...primaryLinkStyle, border: "none", cursor: busy ? "wait" : "pointer", opacity: busy || dispositionId === "" || wrapupNotes.trim().length < 20 ? 0.6 : 1 }}
                disabled={busy || dispositionId === "" || wrapupNotes.trim().length < 20}
              >
                {busy ? "Closing…" : "Close conversation"}
              </button>
              <button type="button" style={linkButtonStyle} disabled={busy} onClick={() => setWrapupOpen(false)}>
                Cancel
              </button>
            </div>
          </form>
        </Panel>
      )}

      <div style={{ display: "grid", gridTemplateColumns: "3fr 2fr", gap: 20, alignItems: "start", marginTop: 16 }}>
        <Panel title="Conversation transcript" actions={<span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>{detail.transcript.length} turns</span>}>
          <div style={{ padding: 16 }}>
            {detail.transcript.length === 0 ? (
              <p style={{ margin: 0, fontSize: 12.5, color: tokens["color.text.secondary"] }}>No turns recorded yet.</p>
            ) : (
              <ol style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 12 }}>
                {detail.transcript.map((t) => (
                  <li
                    key={t.seq}
                    style={{
                      padding: 12,
                      borderRadius: tokens["dimension.border.radius-sm"],
                      background: t.speaker === "ai" ? tokens["color.status.info-bg"] : t.speaker === "agent" ? tokens["color.status.success-bg"] : tokens["color.surface.canvas"],
                      border: `1px solid ${tokens["color.border.default"]}`,
                    }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4, gap: 8 }}>
                      <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                        <SpeakerBadge speaker={t.speaker} />
                        <span style={{ fontSize: 11, color: tokens["color.text.secondary"] }}>Turn #{t.seq}</span>
                      </div>
                      <span style={{ fontSize: 11, color: tokens["color.text.secondary"] }}>
                        {fmtDhaka(t.at)}{t.lang ? ` · ${t.lang.toUpperCase()}` : ""}
                      </span>
                    </div>
                    <p style={{ margin: 0, fontSize: 13, lineHeight: 1.5 }}>{t.text}</p>
                  </li>
                ))}
              </ol>
            )}
            <div ref={endRef} />

            {detail.state === "with_agent" ? (
              <form onSubmit={submitReply} style={{ marginTop: 16, paddingTop: 14, borderTop: `1px solid ${tokens["color.border.default"]}` }}>
                <label htmlFor="reply-text" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>
                  Agent reply
                </label>
                <textarea
                  id="reply-text"
                  value={reply}
                  onChange={(e) => setReply(e.target.value)}
                  onKeyDown={(e) => {
                    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                      e.preventDefault();
                      void submitReply(e);
                    }
                  }}
                  placeholder="Type the reply. Ctrl/Cmd+Enter records it."
                  style={textareaStyle}
                />
                <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 8, flexWrap: "wrap" }}>
                  <select value={replyLang} onChange={(e) => setReplyLang(e.target.value)} aria-label="Reply language" style={selectStyle}>
                    <option value="bn">বাংলা</option>
                    <option value="en">English</option>
                  </select>
                  <button type="submit" style={{ ...primaryLinkStyle, border: "none", cursor: busy || !reply.trim() ? "not-allowed" : "pointer", opacity: busy || !reply.trim() ? 0.6 : 1 }} disabled={busy || !reply.trim()}>
                    {busy ? "Recording…" : "Record reply"}
                  </button>
                  <span style={{ fontSize: 11, color: tokens["color.text.secondary"] }}>
                    {reply.length} chars · recorded as an agent turn on the transcript (the system of record)
                  </span>
                </div>
                {replyError && (
                  <p role="alert" style={{ margin: "8px 0 0", fontSize: 12.5, color: tokens["color.status.error"] }}>
                    {replyError}
                  </p>
                )}
              </form>
            ) : active ? (
              <p style={{ margin: "14px 0 0", fontSize: 12, color: tokens["color.text.secondary"] }}>
                Claim the conversation from the {detail.state === "with_ai" ? "AI lane" : "queue"} to reply.
              </p>
            ) : null}
          </div>
        </Panel>

        <section style={{ display: "grid", gap: 16 }} aria-label="Customer 360 and wrap-up record">
          {!active && (
            <Panel title="Wrap-up record">
              <div style={{ padding: 16, display: "grid", gap: 8, fontSize: 12.5 }}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <span style={{ color: tokens["color.text.secondary"] }}>Disposition</span>
                  <strong>{detail.disposition ? `${detail.disposition.code} — ${detail.disposition.name}` : "—"}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <span style={{ color: tokens["color.text.secondary"] }}>FCR</span>
                  <strong>{detail.fcr ? "Yes" : "No"}</strong>
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 10 }}>
                  <span style={{ color: tokens["color.text.secondary"] }}>Closed</span>
                  <strong>{detail.ended_at ? fmtDhaka(detail.ended_at) : "—"}</strong>
                </div>
                <p style={{ margin: "4px 0 0", color: tokens["color.text.secondary"], lineHeight: 1.5 }}>
                  {detail.wrapup_notes || "No wrap-up notes on record."}
                </p>
              </div>
            </Panel>
          )}

          <Panel title="Service orders">
            <div style={{ padding: 16 }}>
              {open_orders.length === 0 ? (
                <p style={{ margin: 0, fontSize: 12.5, color: tokens["color.text.secondary"] }}>No service orders for this customer.</p>
              ) : (
                <table style={{ width: "100%", borderCollapse: "collapse" }}>
                  <thead>
                    <tr><th style={thStyle}>Order</th><th style={thStyle}>State</th><th style={thStyle}>Device</th></tr>
                  </thead>
                  <tbody>
                    {open_orders.map((o) => (
                      <tr key={o.ref}>
                        <td style={{ ...tdStyle, fontWeight: 600 }}>{o.ref}</td>
                        <td style={tdStyle}><StateBadge state={o.state} /></td>
                        <td style={tdStyle}>{o.device || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </Panel>

          <Panel title="Registered devices">
            <div style={{ padding: 16 }}>
              {devices.length === 0 ? (
                <p style={{ margin: 0, fontSize: 12.5, color: tokens["color.text.secondary"] }}>No registered devices.</p>
              ) : (
                <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 8 }}>
                  {devices.map((d, i) => (
                    <li key={`${d.identifier}-${i}`} style={{ padding: 10, background: tokens["color.surface.canvas"], borderRadius: tokens["dimension.border.radius-sm"], border: `1px solid ${tokens["color.border.default"]}` }}>
                      <div style={{ fontWeight: 600, fontSize: 12.5 }}>{d.model || "(unknown model)"}</div>
                      <div style={{ fontSize: 11, color: tokens["color.text.secondary"] }}>{d.identifier}</div>
                      <div style={{ fontSize: 11, color: tokens["color.text.secondary"], marginTop: 2 }}>Warranty: {d.warranty_status}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </Panel>

          <Panel title="Recent contact history">
            <div style={{ padding: 16 }}>
              {recent_conversations.length === 0 ? (
                <p style={{ margin: 0, fontSize: 12.5, color: tokens["color.text.secondary"] }}>No other conversations on record.</p>
              ) : (
                <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 6 }}>
                  {recent_conversations.map((c) => (
                    <li key={c.id} style={{ display: "flex", justifyContent: "space-between", gap: 10, alignItems: "center", fontSize: 12, padding: "6px 0", borderTop: `1px solid ${tokens["color.border.default"]}` }}>
                      <a href={`/conversation?id=${c.id}`} style={{ color: tokens["color.primary.base"] }}>
                        #{c.id} · {c.channel}
                      </a>
                      <span style={{ fontSize: 11, color: tokens["color.text.secondary"] }}>
                        {fmtDhaka(c.started_at)} ({c.state})
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </Panel>
        </section>
      </div>
    </main>
  );
}
