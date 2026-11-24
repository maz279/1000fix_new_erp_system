"use client";

/**
 * Service requests at scale — create one request across many devices, or
 * track the account's existing orders.
 *
 * The backend validates every device against the session's commercial
 * partner, writes the whole batch atomically and applies priority at intake.
 * This page never trusts client-side ownership and never computes money.
 */
import { useEffect, useMemo, useState, type CSSProperties, type FormEvent } from "react";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { RequireAuth } from "../../components/require-auth";
import {
  PageHeader,
  Panel,
  StatePill,
  StatCard,
  linkButtonStyle,
  pageStyle,
  primaryLinkStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Device {
  id: number;
  brand: string;
  model: string;
  identifier: string;
  serial_number: string;
  site: string;
  warranty_status: string;
}

interface ServiceOrder {
  id: number;
  name: string;
  state: string;
  customer: string;
  device: string;
  serial_number: string;
  site: string;
  priority: string;
  service_type: string;
  technician: string;
  response_deadline: string;
  resolution_deadline: string;
  opened_at: string;
}

const label = (v: string) => v.replace(/_/g, " ");

function RequestsContent() {
  const { locale } = useLanguage();
  const bn = locale === "bn";
  const [orders, setOrders] = useState<ServiceOrder[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);

  const [selected, setSelected] = useState<number[]>([]);
  const [category, setCategory] = useState("standard");
  const [priority, setPriority] = useState("normal");
  const [fault, setFault] = useState("");
  const [filter, setFilter] = useState("all");
  const [query, setQuery] = useState("");

  const load = () => {
    setLoading(true);
    setError(null);
    Promise.all([
      callOdoo<{ orders: ServiceOrder[] }>("/corporate/service-requests"),
      callOdoo<{ devices: Device[] }>("/corporate/estate"),
    ])
      .then(([o, e]) => {
        setOrders(o.orders || []);
        const list = e.devices || [];
        setDevices(list);
        // Preselect devices handed over from the estate page (?devices=1,2)
        if (typeof window !== "undefined") {
          const raw = new URLSearchParams(window.location.search).get("devices");
          if (raw) {
            const ids = raw
              .split(",")
              .map((v) => Number(v))
              .filter((v) => list.some((d) => d.id === v));
            if (ids.length) {
              setSelected(ids);
              setShowForm(true);
            }
          }
        }
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    load();
  }, []);

  const toggle = (id: number) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (selected.length === 0) {
      setError(bn ? "কমপক্ষে একটি ডিভাইস নির্বাচন করুন।" : "Select at least one device.");
      return;
    }
    if (!fault.trim()) {
      setError(bn ? "ত্রুটির বিবরণ লিখুন।" : "Describe the fault.");
      return;
    }
    setSubmitting(true);
    setError(null);
    setNotice(null);
    try {
      const res = await callOdoo<{ created?: { name: string }[]; error?: { message: string } }>(
        "/corporate/service-requests",
        {
          device_ids: selected,
          order_category: category,
          priority,
          fault_description: fault,
        }
      );
      if (res.error) throw new Error(res.error.message);
      const names = (res.created || []).map((c) => c.name).join(", ");
      setNotice(
        bn
          ? `${selected.length}টি সার্ভিস অনুরোধ তৈরি হয়েছে${names ? `: ${names}` : ""}।`
          : `${selected.length} service request${selected.length === 1 ? "" : "s"} created${names ? `: ${names}` : ""}.`
      );
      setSelected([]);
      setFault("");
      setShowForm(false);
      load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setSubmitting(false);
    }
  };

  const filtered = useMemo(
    () =>
      orders.filter((o) => {
        const q = query.trim().toLowerCase();
        const matchesQuery =
          !q ||
          o.name.toLowerCase().includes(q) ||
          (o.device || "").toLowerCase().includes(q) ||
          (o.serial_number || "").toLowerCase().includes(q) ||
          (o.site || "").toLowerCase().includes(q);
        const matchesFilter =
          filter === "all" ||
          (filter === "open" && !["delivered", "closed", "cancelled"].includes(o.state)) ||
          (filter === "priority" && ["high", "urgent"].includes(o.priority)) ||
          o.state === filter;
        return matchesQuery && matchesFilter;
      }),
    [orders, query, filter]
  );

  if (loading) return <Loading label={bn ? "সার্ভিস অনুরোধ লোড হচ্ছে…" : "Loading service requests…"} />;
  if (error && orders.length === 0) return <LoadError what={bn ? "সার্ভিস অনুরোধ" : "Service requests"} message={error} />;

  const open = orders.filter((o) => !["delivered", "closed", "cancelled"].includes(o.state)).length;
  const high = orders.filter((o) => ["high", "urgent"].includes(o.priority) && !["delivered", "closed", "cancelled"].includes(o.state)).length;
  const delivered = orders.filter((o) => ["delivered", "closed"].includes(o.state)).length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title={bn ? "সার্ভিস অনুরোধ" : "Service requests"}
        subtitle={
          bn
            ? "একাধিক ডিভাইসের জন্য একসাথে অনুরোধ তৈরি করুন, প্রায়োরিটি নির্ধারণ করুন এবং এসএলএ ডেডলাইনের সাথে ট্র্যাক করুন।"
            : "Raise one request across many devices, set priority and track it against the SLA deadlines."
        }
        actions={
          <button
            type="button"
            onClick={() => setShowForm((v) => !v)}
            aria-expanded={showForm}
            style={{ ...primaryLinkStyle, cursor: "pointer", border: "none" }}
          >
            {showForm ? (bn ? "ফর্ম বন্ধ" : "Close form") : `+ ${bn ? "নতুন অনুরোধ" : "New request"}`}
          </button>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label={bn ? "খোলা" : "Open"} value={open} tone="primary" />
        <StatCard label={bn ? "উচ্চ/জরুরি" : "High / urgent"} value={high} tone={high ? "error" : "neutral"} />
        <StatCard label={bn ? "সম্পন্ন" : "Delivered / closed"} value={delivered} tone="success" />
        <StatCard label={bn ? "মোট" : "Total requests"} value={orders.length} />
      </section>

      {notice && (
        <div role="status" style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.success-bg"], color: tokens["color.status.success"], border: `1px solid ${tokens["color.status.success"]}`, fontSize: 12.5 }}>
          {notice}
        </div>
      )}
      {error && (
        <div role="alert" style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.error-bg"], color: tokens["color.status.error"], border: `1px solid ${tokens["color.status.error"]}`, fontSize: 12.5 }}>
          {error}
        </div>
      )}

      {showForm && (
        <Panel title={bn ? "নতুন সার্ভিস অনুরোধ" : "New service request"}>
          <form onSubmit={submit} style={{ padding: 16, display: "flex", flexDirection: "column", gap: 14 }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
              <div>
                <label htmlFor="req-category" style={{ display: "block", marginBottom: 5, fontSize: 12, fontWeight: 600 }}>{bn ? "শ্রেণি" : "Category"}</label>
                <select id="req-category" value={category} onChange={(e) => setCategory(e.target.value)} style={selectStyle}>
                  <option value="standard">{bn ? "স্ট্যান্ডার্ড" : "Standard"}</option>
                  <option value="warranty">{bn ? "ওয়ারেন্টি" : "Warranty"}</option>
                  <option value="amc">{bn ? "এএমসি" : "AMC"}</option>
                </select>
              </div>
              <div>
                <label htmlFor="req-priority" style={{ display: "block", marginBottom: 5, fontSize: 12, fontWeight: 600 }}>{bn ? "প্রায়োরিটি" : "Priority"}</label>
                <select id="req-priority" value={priority} onChange={(e) => setPriority(e.target.value)} style={selectStyle}>
                  <option value="normal">{bn ? "সাধারণ" : "Normal"}</option>
                  <option value="high">{bn ? "উচ্চ" : "High"}</option>
                  <option value="urgent">{bn ? "জরুরি" : "Urgent"}</option>
                </select>
              </div>
            </div>

            <div>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
                <strong style={{ fontSize: 12 }}>{bn ? "ডিভাইস নির্বাচন" : "Select devices"}</strong>
                <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
                  {selected.length} {bn ? "নির্বাচিত" : "selected"}
                </span>
              </div>
              <div style={{ maxHeight: 230, overflowY: "auto", border: `1px solid ${tokens["color.border.default"]}`, borderRadius: tokens["dimension.border.radius-sm"] }}>
                {devices.map((d) => (
                  <label
                    key={d.id}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 10,
                      padding: "7px 10px",
                      borderBottom: `1px solid ${tokens["color.border.default"]}`,
                      fontSize: 12.5,
                      cursor: "pointer",
                    }}
                  >
                    <input type="checkbox" checked={selected.includes(d.id)} onChange={() => toggle(d.id)} />
                    <span style={{ flex: 1 }}>
                      {d.brand} {d.model}
                      <span style={{ color: tokens["color.text.secondary"] }}>
                        {" · "}{d.serial_number || d.identifier || "—"}
                        {d.site ? ` · ${d.site}` : ""}
                      </span>
                    </span>
                    <StatePill state={d.warranty_status} />
                  </label>
                ))}
                {devices.length === 0 && (
                  <div style={{ padding: 14, fontSize: 12, color: tokens["color.text.secondary"] }}>
                    {bn ? "আপনার বহরে কোনো ডিভাইস নেই।" : "No devices in your estate."}
                  </div>
                )}
              </div>
            </div>

            <div>
              <label htmlFor="req-fault" style={{ display: "block", marginBottom: 5, fontSize: 12, fontWeight: 600 }}>{bn ? "ত্রুটির বিবরণ" : "Fault description"}</label>
              <textarea
                id="req-fault"
                value={fault}
                onChange={(e) => setFault(e.target.value)}
                rows={3}
                required
                placeholder={bn ? "কী সমস্যা হচ্ছে, কখন শুরু, কোনো ত্রুটি কোড…" : "What is failing, when it started, any error code…"}
                style={{ ...selectStyle, height: "auto", resize: "vertical" }}
              />
            </div>

            <div style={{ display: "flex", gap: 10 }}>
              <button type="submit" disabled={submitting} style={{ ...primaryLinkStyle, border: "none", cursor: submitting ? "wait" : "pointer", opacity: submitting ? 0.7 : 1 }}>
                {submitting
                  ? bn ? "তৈরি হচ্ছে…" : "Creating…"
                  : bn ? `${selected.length || ""} অনুরোধ তৈরি করুন`.trim() : `Create request${selected.length === 1 ? "" : "s"}`}
              </button>
              <button type="button" onClick={() => setShowForm(false)} style={{ ...linkButtonStyle, cursor: "pointer" }}>
                {bn ? "বাতিল" : "Cancel"}
              </button>
            </div>
          </form>
        </Panel>
      )}

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", margin: "16px 0 12px" }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={bn ? "রেফারেন্স, ডিভাইস বা সাইট খুঁজুন…" : "Reference, device or site…"}
          style={{ ...selectStyle, flex: "1 1 260px", maxWidth: 400, height: 34 }}
        />
        {[
          { key: "all", en: "All", bn: "সব" },
          { key: "open", en: "Open", bn: "খোলা" },
          { key: "priority", en: "High/urgent", bn: "উচ্চ/জরুরি" },
          { key: "ready", en: "Ready", bn: "প্রস্তুত" },
        ].map((f) => (
          <button
            key={f.key}
            type="button"
            aria-pressed={filter === f.key}
            onClick={() => setFilter(f.key)}
            style={{
              padding: "6px 12px",
              fontSize: tokens["typography.size.200"],
              borderRadius: tokens["dimension.border.radius-sm"],
              border: `1px solid ${filter === f.key ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
              background: filter === f.key ? tokens["color.primary.base"] : tokens["color.surface.primary"],
              color: filter === f.key ? tokens["color.text.inverse"] : tokens["color.text.secondary"],
              cursor: "pointer",
            }}
          >
            {bn ? f.bn : f.en}
          </button>
        ))}
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>{bn ? "রেফারেন্স" : "Reference"}</th>
                <th style={thStyle}>{bn ? "ডিভাইস / সাইট" : "Device / site"}</th>
                <th style={thStyle}>{bn ? "চ্যানেল" : "Channel"}</th>
                <th style={thStyle}>{bn ? "প্রায়োরিটি" : "Priority"}</th>
                <th style={thStyle}>{bn ? "অবস্থা" : "Status"}</th>
                <th style={thStyle}>{bn ? "রেসপন্স ডেডলাইন" : "Response deadline"}</th>
                <th style={thStyle}>{bn ? "খোলা হয়েছে" : "Opened"}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((o) => (
                <tr key={o.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{o.name}</td>
                  <td style={tdStyle}>
                    {o.device || "—"}
                    {o.site ? <span style={{ color: tokens["color.text.secondary"] }}> · {o.site}</span> : null}
                    {o.serial_number ? <div style={{ fontSize: 10.5, fontFamily: "monospace", color: tokens["color.text.secondary"] }}>{o.serial_number}</div> : null}
                  </td>
                  <td style={tdStyle}>{label(o.service_type)}</td>
                  <td style={tdStyle}><StatePill state={o.priority} /></td>
                  <td style={tdStyle}><StatePill state={o.state} /></td>
                  <td style={tdStyle}>{o.response_deadline ? o.response_deadline.slice(0, 16) : "—"}</td>
                  <td style={tdStyle}>{o.opened_at ? o.opened_at.slice(0, 10) : "—"}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 28 }}>
                    {bn ? "কোনো অনুরোধ নেই — উপরের ‘নতুন অনুরোধ’ থেকে শুরু করুন।" : "No requests — start with “New request” above."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>
    </main>
  );
}

const selectStyle: CSSProperties = {
  width: "100%",
  boxSizing: "border-box",
  padding: "8px 10px",
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  background: tokens["color.surface.primary"],
  color: tokens["color.text.primary"],
  fontSize: tokens["typography.size.200"],
};

export default function ServiceRequestsPage() {
  return (
    <RequireAuth>
      <RequestsContent />
    </RequireAuth>
  );
}
