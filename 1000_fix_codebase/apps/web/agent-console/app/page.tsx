"use client";

/* P10 unified queue — live conversations across channels, oldest first.
 * Claiming a conversation hands it AI→agent (G4-05); the transcript +
 * customer 360 open on the conversation page. Softphone endpoints come
 * from /contact/softphone (deployment config only — nulls when unset).
 * Every row comes from /contact/conversations; a failed load or claim is
 * shown as an error — nothing is simulated. WCAG 2.2 AA. */
import { useCallback, useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Loading, Stat } from "../lib/imports";
import { callOdoo } from "../lib/api";

export interface Conversation {
  id: number;
  channel: "voice" | "whatsapp" | "chat" | "email" | "in_app";
  state: "new" | "with_ai" | "with_agent" | "resolved_ai" | "resolved_agent";
  intent: string;
  customer: string;
  contact_identity: string;
  started_at: string;
  turns: number;
}

interface Softphone {
  ws_url: string | null;
  sip_realm: string | null;
  click_to_call_prefix: string | null;
  vendor: string | null;
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
  transition: "opacity 0.2s ease, transform 0.1s ease",
};

const channelIcons: Record<string, string> = {
  voice: "📞 Hotline 16743",
  whatsapp: "💬 WhatsApp",
  chat: "🌐 Web Chat",
  email: "✉️ Email",
  in_app: "📱 In-App",
};

interface Notice {
  kind: "success" | "error";
  text: string;
}

export default function QueuePage() {
  const [rows, setRows] = useState<Conversation[]>([]);
  const [softphone, setSoftphone] = useState<Softphone | null>(null);
  const [softphoneError, setSoftphoneError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [claiming, setClaiming] = useState<number | null>(null);
  const [filterChannel, setFilterChannel] = useState<string>("all");

  const reload = useCallback(async () => {
    try {
      const d = await callOdoo<{ conversations?: Conversation[] } | undefined>("/contact/conversations");
      if (!d) throw new Error("The server returned an empty response.");
      setRows(d.conversations ?? []);
      setLoadError(null);
    } catch (e: unknown) {
      setLoadError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    Promise.all([
      reload(),
      callOdoo<{ softphone?: Softphone } | undefined>("/contact/softphone")
        .then((d) => setSoftphone(d?.softphone ?? null))
        .catch((e: Error) => setSoftphoneError(e.message)),
    ]).finally(() => setLoading(false));

    const t = setInterval(reload, 15000);
    return () => clearInterval(t);
  }, [reload]);

  async function claim(c: Conversation) {
    setClaiming(c.id);
    try {
      const d = await callOdoo<
        { conversation?: { id: number; state: Conversation["state"] }; error?: { message: string } } | undefined
      >("/contact/handoff", { conversation_id: c.id, action: "claim" });
      if (!d) throw new Error("The server returned an empty response.");
      if (d.error) {
        setNotice({ kind: "error", text: `Could not claim conversation #${c.id}: ${d.error.message}` });
      } else {
        const state = d.conversation?.state;
        if (state) {
          setRows((prev) => prev.map((r) => (r.id === c.id ? { ...r, state } : r)));
        }
        setNotice({ kind: "success", text: `Conversation #${c.id} claimed — now ${state ?? "updated"}.` });
        await reload();
      }
    } catch (e: unknown) {
      setNotice({
        kind: "error",
        text: `Could not claim conversation #${c.id}: ${e instanceof Error ? e.message : String(e)}`,
      });
    } finally {
      setClaiming(null);
    }
  }

  if (loading) return <Loading />;

  const withAI = rows.filter((r) => r.state === "with_ai").length;
  const withAgent = rows.filter((r) => r.state === "with_agent").length;
  const filteredRows = filterChannel === "all" ? rows : rows.filter((r) => r.channel === filterChannel);

  return (
    <main style={{ padding: "32px 40px", maxWidth: 1400, margin: "0 auto" }}>
      <SectionHead
        title="Unified Contact Centre Queue"
        note="Omnichannel intake across Voice (Hotline 16743), WhatsApp, Web Chat, Email, and In-App (G4-04: the transcript is the record)"
      />

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
        <Stat label="Active Queue" value={rows.length} />
        <Stat label="With AI Lane (M32)" value={withAI} tone="primary" />
        <Stat label="With Live Agent" value={withAgent} />
      </div>

      {loadError && (
        <div
          role="alert"
          style={{
            padding: "12px 18px",
            marginBottom: 20,
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.status.error-bg"],
            color: tokens["color.status.error"],
            fontSize: tokens["typography.size.200"],
            border: `1px solid ${tokens["color.status.error"]}`,
          }}
        >
          Failed to load the conversation queue: {loadError}
          {rows.length > 0 && " — the rows below are from the last successful load."}
        </div>
      )}

      {notice && (
        <div
          role={notice.kind === "error" ? "alert" : "status"}
          aria-live="polite"
          style={{
            padding: "12px 18px",
            marginBottom: 20,
            borderRadius: tokens["dimension.border.radius-sm"],
            background: notice.kind === "error" ? tokens["color.status.error-bg"] : tokens["color.status.success-bg"],
            color: notice.kind === "error" ? tokens["color.status.error"] : tokens["color.status.success"],
            fontSize: tokens["typography.size.200"],
            border: `1px solid ${tokens["color.border.default"]}`,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span>{notice.text}</span>
          <button
            onClick={() => setNotice(null)}
            style={{ background: "none", border: "none", cursor: "pointer", color: "inherit", fontWeight: "bold" }}
            aria-label="Dismiss notification"
          >
            ✕
          </button>
        </div>
      )}

      <section
        aria-label="Telephony softphone configuration"
        style={{
          padding: "12px 18px",
          marginBottom: 20,
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.surface.primary"],
          fontSize: tokens["typography.size.200"],
          color: tokens["color.text.secondary"],
        }}
      >
        <strong style={{ color: tokens["color.text.primary"] }}>Softphone (INT-015): </strong>
        {softphoneError ? (
          <span style={{ color: tokens["color.status.error"] }}>could not load configuration — {softphoneError}</span>
        ) : softphone?.ws_url ? (
          <span>
            configured{softphone.vendor ? ` (${softphone.vendor})` : ""} · {softphone.ws_url}
            {softphone.sip_realm && ` · realm ${softphone.sip_realm}`}
            {softphone.click_to_call_prefix && ` · dial prefix ${softphone.click_to_call_prefix}`}
          </span>
        ) : (
          <span>not configured for this deployment — place calls from your desk phone.</span>
        )}
      </section>

      {/* Channel Filter Tabs */}
      <nav aria-label="Channel selection tabs" style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {[
          ["all", `All Channels (${rows.length})`],
          ["voice", `Voice 16743 (${rows.filter((r) => r.channel === "voice").length})`],
          ["whatsapp", `WhatsApp (${rows.filter((r) => r.channel === "whatsapp").length})`],
          ["chat", `Web Chat (${rows.filter((r) => r.channel === "chat").length})`],
          ["in_app", `In-App (${rows.filter((r) => r.channel === "in_app").length})`],
          ["email", `Email (${rows.filter((r) => r.channel === "email").length})`],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setFilterChannel(key)}
            aria-pressed={filterChannel === key}
            style={{
              padding: "6px 14px",
              border: `1px solid ${filterChannel === key ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
              background: filterChannel === key ? tokens["color.primary.base"] : tokens["color.surface.primary"],
              color: filterChannel === key ? tokens["color.text.inverse"] : tokens["color.text.secondary"],
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: tokens["typography.size.200"],
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            {label}
          </button>
        ))}
      </nav>

      {/* Unified Queue Table */}
      <div style={{ overflowX: "auto", border: `1px solid ${tokens["color.border.default"]}`, borderRadius: tokens["dimension.border.radius-md"] }}>
        <table style={{ width: "100%", borderCollapse: "collapse", background: tokens["color.surface.primary"] }}>
          <thead>
            <tr style={{ background: tokens["color.surface.secondary"] }}>
              {["Waiting Since", "Channel", "Caller / Identity", "NLU Intent", "Turns", "Status", "Actions"].map((h) => (
                <th
                  key={h}
                  scope="col"
                  style={{
                    textAlign: "left",
                    padding: "12px 16px",
                    fontSize: tokens["typography.size.200"],
                    color: tokens["color.text.secondary"],
                    borderBottom: `1px solid ${tokens["color.border.default"]}`,
                    fontWeight: 600,
                  }}
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredRows.map((c) => (
              <tr
                key={c.id}
                style={{
                  borderBottom: `1px solid ${tokens["color.border.default"]}`,
                }}
              >
                <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"] }}>
                  {c.started_at || "—"}
                </td>
                <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"] }}>
                  <span style={{ fontWeight: 500 }}>{channelIcons[c.channel] || c.channel}</span>
                </td>
                <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"] }}>
                  <div style={{ fontWeight: 600 }}>{c.customer || "(Unknown Caller)"}</div>
                  <div style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                    {c.contact_identity}
                  </div>
                </td>
                <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"] }}>
                  <code style={{ background: tokens["color.surface.canvas"], padding: "2px 6px", borderRadius: 4 }}>
                    {c.intent || "unclassified"}
                  </code>
                </td>
                <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"] }}>
                  {c.turns} turns
                </td>
                <td style={{ padding: "12px 16px" }}>
                  <Pill state={c.state} />
                </td>
                <td style={{ padding: "12px 16px" }}>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <a
                      href={`/conversation?id=${c.id}`}
                      style={{
                        ...btn,
                        textDecoration: "none",
                        background: tokens["color.surface.secondary"],
                        color: tokens["color.text.primary"],
                        border: `1px solid ${tokens["color.border.default"]}`,
                      }}
                      aria-label={`Open Customer 360 and Transcript for conversation ${c.id}`}
                    >
                      Open 360
                    </a>
                    {(c.state === "new" || c.state === "with_ai") && (
                      <button
                        style={{ ...btn, opacity: claiming === c.id ? 0.6 : 1 }}
                        disabled={claiming !== null}
                        onClick={() => claim(c)}
                        aria-label={`Claim conversation ${c.id} from AI to live agent`}
                      >
                        {claiming === c.id ? "Claiming…" : "Claim"}
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredRows.length === 0 && (
        <p style={{ color: tokens["color.text.secondary"], marginTop: 24, textAlign: "center" }}>
          {rows.length === 0 ? "No active conversations in the queue." : "No active conversations in this channel."}
        </p>
      )}
    </main>
  );
}
