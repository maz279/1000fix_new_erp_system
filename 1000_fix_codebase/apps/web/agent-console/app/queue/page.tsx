"use client";

/**
 * P10 unified queue — live conversations across channels, sorted by risk:
 * breached first, then routing priority, then longest wait. Claiming hands
 * the contact AI→agent (G4-05) and opens the workspace. Every row comes
 * from /contact/portal/queue; a failed load or claim is shown as an error —
 * nothing is simulated.
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { tokens, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import {
  Badge,
  CHANNEL_LABEL,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  downloadCsv,
  fmtDhaka,
  linkButtonStyle,
  pageStyle,
  primaryLinkStyle,
  selectStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface QueueRow {
  id: number;
  channel: string;
  state: string;
  intent: string;
  customer: string;
  contact_identity: string;
  started_at: string;
  waiting_minutes: number;
  turns: number;
  agent: string;
  agent_id: number | null;
  queued_at: string;
  answered_at: string;
  sla_due_at: string;
  sla_breached: boolean;
  priority: number;
  work_state: string;
  entitlement: string;
  handoff_reason: string;
}

interface Summary {
  active?: number;
  waiting_for_agent?: number;
  oldest_waiting_minutes?: number;
  sla_breached?: number;
  resolved_today?: number;
  by_state?: Record<string, number>;
  by_channel?: Record<string, number>;
  generated_at?: string;
}

interface Softphone {
  ws_url: string | null;
  sip_realm: string | null;
  click_to_call_prefix: string | null;
  vendor: string | null;
}

interface Notice {
  kind: "success" | "error";
  text: string;
}

/** Odoo datetimes are UTC "YYYY-MM-DD HH:MM:SS"; Date.parse needs T/Z. */
function utcMs(value: string): number | null {
  if (!value) return null;
  const raw = value.includes("T") ? value : `${value.replace(" ", "T")}Z`;
  const t = Date.parse(raw);
  return Number.isNaN(t) ? null : t;
}

function slaChip(row: QueueRow): { text: string; tone: "neutral" | "success" | "warning" | "error" } {
  if (row.answered_at) return { text: "answered", tone: "neutral" };
  if (!row.sla_due_at) return { text: "no SLA clock", tone: "neutral" };
  const due = utcMs(row.sla_due_at);
  if (due == null) return { text: "—", tone: "neutral" };
  const diff = Math.round((due - Date.now()) / 60_000);
  if (diff < 0) return { text: `breached ${Math.abs(diff)}m`, tone: "error" };
  if (diff <= 5) return { text: `due in ${diff}m`, tone: "warning" };
  return { text: `due in ${diff}m`, tone: "success" };
}

export default function QueuePage() {
  const router = useRouter();
  const [rows, setRows] = useState<QueueRow[]>([]);
  const [summary, setSummary] = useState<Summary>({});
  const [softphone, setSoftphone] = useState<Softphone | null>(null);
  const [softphoneError, setSoftphoneError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [notice, setNotice] = useState<Notice | null>(null);
  const [claiming, setClaiming] = useState<number | null>(null);
  const [channel, setChannel] = useState<string>("all");
  const [stateFilter, setStateFilter] = useState<string>("all");
  const [breachesOnly, setBreachesOnly] = useState(false);
  const [query, setQuery] = useState("");
  const [updatedAt, setUpdatedAt] = useState<Date | null>(null);

  const reload = useCallback(async () => {
    try {
      const [q, s] = await Promise.all([
        callOdoo<{ conversations?: QueueRow[]; total?: number }>("/contact/portal/queue"),
        callOdoo<Summary>("/contact/portal/summary"),
      ]);
      setRows(q.conversations ?? []);
      setSummary(s);
      setUpdatedAt(new Date());
      setLoadError(null);
    } catch (e: unknown) {
      setLoadError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    void reload().finally(() => setLoading(false));
    callOdoo<{ softphone?: Softphone }>("/contact/softphone")
      .then((d) => setSoftphone(d?.softphone ?? null))
      .catch((e: Error) => setSoftphoneError(e.message));
    const t = setInterval(() => void reload(), 15_000);
    return () => clearInterval(t);
  }, [reload]);

  async function claim(row: QueueRow) {
    setClaiming(row.id);
    setNotice(null);
    try {
      const d = await callOdoo<{ conversation?: { id: number; state: string }; error?: { message: string } }>(
        "/contact/handoff",
        { conversation_id: row.id, action: "claim" }
      );
      if (d.error) {
        setNotice({ kind: "error", text: `Could not claim #${row.id}: ${d.error.message}` });
        return;
      }
      router.push(`/conversation?id=${row.id}`);
    } catch (e: unknown) {
      setNotice({ kind: "error", text: `Could not claim #${row.id}: ${e instanceof Error ? e.message : String(e)}` });
    } finally {
      setClaiming(null);
    }
  }

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return rows
      .filter((r) => (channel === "all" ? true : r.channel === channel))
      .filter((r) => (stateFilter === "all" ? true : r.state === stateFilter))
      .filter((r) => (breachesOnly ? r.sla_breached : true))
      .filter((r) =>
        !q
          ? true
          : `${r.id} ${r.customer} ${r.contact_identity} ${r.intent}`.toLowerCase().includes(q)
      )
      .sort(
        (a, b) =>
          Number(b.sla_breached) - Number(a.sla_breached) ||
          b.priority - a.priority ||
          b.waiting_minutes - a.waiting_minutes
      );
  }, [rows, channel, stateFilter, breachesOnly, query]);

  const exportCsv = () =>
    downloadCsv(
      `1000fix-contact-queue-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Conversation", "Channel", "State", "Customer", "Identity", "Intent", "Waiting (min)", "SLA due", "Breached", "Priority", "Agent", "Turns"],
      visible.map((r) => [
        String(r.id),
        r.channel,
        r.state,
        r.customer,
        r.contact_identity,
        r.intent,
        String(r.waiting_minutes),
        r.sla_due_at,
        r.sla_breached ? "YES" : "",
        String(r.priority),
        r.agent,
        String(r.turns),
      ])
    );

  if (loading) return <Loading />;
  if (loadError && rows.length === 0) return <LoadError what="the conversation queue" message={loadError} />;

  const withAI = summary.by_state?.with_ai ?? rows.filter((r) => r.state === "with_ai").length;
  const withAgent = summary.by_state?.with_agent ?? rows.filter((r) => r.state === "with_agent").length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Unified contact queue"
        subtitle={
          <>
            Voice (hotline 16743), WhatsApp, web chat, email and in-app contacts in one queue. Sorted by SLA
            breach, routing priority and longest wait — not arrival order.
          </>
        }
        actions={
          <>
            <button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>
              ⬇ Export CSV
            </button>
          </>
        }
      />

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
          gap: 12,
          marginBottom: 16,
        }}
      >
        <StatCard label="Active" value={summary.active ?? rows.length} tone="primary" note={`${withAI} with AI · ${withAgent} with agent`} />
        <StatCard label="Waiting for agent" value={summary.waiting_for_agent ?? 0} tone="warning" />
        <StatCard
          label="SLA breached"
          value={summary.sla_breached ?? 0}
          tone={(summary.sla_breached ?? 0) > 0 ? "error" : "success"}
        />
        <StatCard label="Oldest wait" value={`${summary.oldest_waiting_minutes ?? 0} min`} />
        <StatCard label="Resolved today" value={summary.resolved_today ?? 0} tone="success" />
      </section>

      {loadError && (
        <div role="alert" style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.error-bg"], color: tokens["color.status.error"], fontSize: 12.5 }}>
          Queue refresh failed: {loadError} — the rows below are from the last successful load.
        </div>
      )}
      {notice && (
        <div role={notice.kind === "error" ? "alert" : "status"} style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: notice.kind === "error" ? tokens["color.status.error-bg"] : tokens["color.status.success-bg"], color: notice.kind === "error" ? tokens["color.status.error"] : tokens["color.status.success"], fontSize: 12.5 }}>
          {notice.text}
        </div>
      )}

      <section
        aria-label="Softphone configuration"
        style={{
          padding: "10px 14px",
          marginBottom: 16,
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.surface.primary"],
          fontSize: 12,
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

      <nav aria-label="Channel filters" style={{ display: "flex", gap: 8, marginBottom: 12, flexWrap: "wrap" }}>
        {[
          ["all", `All channels (${rows.length})`],
          ["voice", `Voice 16743 (${rows.filter((r) => r.channel === "voice").length})`],
          ["whatsapp", `WhatsApp (${rows.filter((r) => r.channel === "whatsapp").length})`],
          ["chat", `Web chat (${rows.filter((r) => r.channel === "chat").length})`],
          ["in_app", `In-app (${rows.filter((r) => r.channel === "in_app").length})`],
          ["email", `Email (${rows.filter((r) => r.channel === "email").length})`],
        ].map(([key, label]) => (
          <button
            key={key}
            type="button"
            onClick={() => setChannel(key)}
            aria-pressed={channel === key}
            style={{
              padding: "6px 13px",
              border: `1px solid ${channel === key ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
              background: channel === key ? tokens["color.primary.base"] : tokens["color.surface.primary"],
              color: channel === key ? tokens["color.text.inverse"] : tokens["color.text.secondary"],
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: 12,
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            {label}
          </button>
        ))}
      </nav>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", marginBottom: 12 }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search customer, identity, intent or #id…"
          aria-label="Search the queue"
          style={{ ...selectStyle, flex: "1 1 280px", maxWidth: 420 }}
        />
        <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} aria-label="Conversation state" style={selectStyle}>
          <option value="all">All states</option>
          <option value="new">New</option>
          <option value="with_ai">With AI</option>
          <option value="with_agent">With agent</option>
        </select>
        <label style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12.5 }}>
          <input type="checkbox" checked={breachesOnly} onChange={(e) => setBreachesOnly(e.target.checked)} />
          SLA breached only
        </label>
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
          {visible.length} of {rows.length} · {updatedAt ? `updated ${updatedAt.toLocaleTimeString()}` : "loading"} · refreshes every 15s
        </span>
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Conversation</th>
                <th style={thStyle}>Waiting / SLA</th>
                <th style={thStyle}>Channel</th>
                <th style={thStyle}>Caller / identity</th>
                <th style={thStyle}>Intent</th>
                <th style={thStyle}>Priority</th>
                <th style={thStyle}>Agent</th>
                <th style={thStyle}>Turns</th>
                <th style={thStyle}>State</th>
                <th style={thStyle}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {visible.map((r) => {
                const sla = slaChip(r);
                return (
                  <tr key={r.id}>
                    <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11.5 }}>#{r.id}</td>
                    <td style={tdStyle}>
                      <div style={{ fontWeight: 600 }}>{r.waiting_minutes} min</div>
                      <div style={{ marginTop: 4 }}>
                        <Badge tone={sla.tone}>{sla.text}</Badge>
                      </div>
                    </td>
                    <td style={tdStyle}>{CHANNEL_LABEL[r.channel] ?? r.channel}</td>
                    <td style={tdStyle}>
                      <div style={{ fontWeight: 600 }}>{r.customer || "(Unidentified caller)"}</div>
                      <div style={{ fontSize: 11, color: tokens["color.text.secondary"] }}>
                        {r.contact_identity || "no identity on record"}
                      </div>
                    </td>
                    <td style={tdStyle}>
                      <code style={{ background: tokens["color.surface.canvas"], padding: "2px 6px", borderRadius: 4, fontSize: 11.5 }}>
                        {r.intent || "unclassified"}
                      </code>
                    </td>
                    <td style={tdStyle}>
                      {r.priority > 0 ? <Badge tone={r.priority >= 3 ? "error" : "info"}>P{r.priority}</Badge> : "—"}
                    </td>
                    <td style={tdStyle}>{r.agent || "—"}</td>
                    <td style={tdStyle}>{r.turns}</td>
                    <td style={tdStyle}><StateBadge state={r.state} /></td>
                    <td style={tdStyle}>
                      <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap" }}>
                        <a
                          href={`/conversation?id=${r.id}`}
                          style={{ ...linkButtonStyle, padding: "5px 10px", textDecoration: "none" }}
                          aria-label={`Open conversation ${r.id}`}
                        >
                          Open 360
                        </a>
                        {(r.state === "new" || r.state === "with_ai") && (
                          <button
                            type="button"
                            onClick={() => claim(r)}
                            disabled={claiming !== null}
                            style={{ ...primaryLinkStyle, padding: "5px 12px", border: "none", cursor: claiming ? "wait" : "pointer", opacity: claiming === r.id ? 0.6 : 1 }}
                            aria-label={`Claim conversation ${r.id} from the AI lane`}
                          >
                            {claiming === r.id ? "Claiming…" : "Claim"}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
              {visible.length === 0 && (
                <tr>
                  <td colSpan={10} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 28 }}>
                    {rows.length === 0
                      ? "No active conversations in the queue."
                      : "No conversations match these filters."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <p style={{ marginTop: 12, fontSize: 11, color: tokens["color.text.secondary"] }}>
        The queue is the team queue. Claiming records you as the handling agent; SLA due times come from the
        first-response policy instance on each contact. Generated{" "}
        {summary.generated_at ? fmtDhaka(summary.generated_at) : "—"}.
      </p>
    </main>
  );
}
