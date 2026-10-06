"use client";

/* P07 jobs board — open marketplace orders with the seller's own quote
 * visible (EA-05: never the other quotes). Quote submission posts to
 * /seller/quotes; the KYC + price + open-job gates are server-side and
 * their rejections render inline (AS-09). */
import { useCallback, useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Loading, LoadError, Stat } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface MyQuote { id: number; price_bdt: string; eta_days: number; state: string }
interface Job {
  id: number; name: string; description: string; budget_bdt: string;
  state: string; my_quote: MyQuote | null;
}

const card: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 20,
  marginBottom: 12,
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
};
const inputStyle: React.CSSProperties = {
  padding: 8,
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
  width: 120,
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [quoteFor, setQuoteFor] = useState<Job | null>(null);

  const reload = useCallback(async () => {
    const d = await callOdoo<{ orders?: Job[]; error?: { message: string } }>("/seller/orders");
    if (d.error) setError(d.error.message);
    else setJobs(d.orders || []);
  }, []);

  useEffect(() => {
    reload().then(() => setLoading(false)).catch((e: Error) => setError(e.message));
  }, [reload]);

  async function submitQuote(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!quoteFor) return;
    const form = new FormData(e.currentTarget);
    const d = await callOdoo<{ quote?: { id: number; state: string }; error?: { message: string } }>(
      "/seller/quotes", {
        order_id: quoteFor.id,
        quoted_price: Number(form.get("price")),
        eta_days: Number(form.get("eta") || 3),
        notes: String(form.get("notes") || ""),
      });
    setNotice(d.error ? d.error.message : `Quote submitted (${d.quote?.state})`);
    setQuoteFor(null);
    if (!d.error) reload();
  }

  if (loading) return <Loading />;
  if (error) return <LoadError what="jobs board" message={error} />;

  const quoted = jobs.filter((j) => j.my_quote).length;

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="Open Jobs"
        note="Quote on open marketplace orders — your own quote is visible, never the others (EA-05)"
      />
      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Stat label="Open jobs" value={jobs.length} />
        <Stat label="My quotes" value={quoted} tone="primary" />
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
      {jobs.map((j) => (
        <section key={j.id} style={card}>
          <header style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <strong style={{ flex: 1 }}>{j.name}</strong>
            <Pill state={j.state} />
          </header>
          <p style={{
            margin: "8px 0", color: tokens["color.text.secondary"],
            fontSize: tokens["typography.size.200"],
          }}>{j.description}</p>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <span style={{ fontVariantNumeric: "tabular-nums" }}>
              Budget ৳ {j.budget_bdt}
            </span>
            {j.my_quote ? (
              <span>
                My quote: <Pill state={j.my_quote.state} />{" "}
                ৳ {j.my_quote.price_bdt} · {j.my_quote.eta_days}d
              </span>
            ) : (
              <button style={btn} onClick={() => setQuoteFor(j)}>Quote</button>
            )}
          </div>

          {quoteFor?.id === j.id && (
            <form onSubmit={submitQuote} style={{
              marginTop: 12, display: "flex", gap: 8, alignItems: "center",
              padding: 12, background: tokens["color.surface.canvas"],
              borderRadius: tokens["dimension.border.radius-sm"],
            }}>
              <input name="price" type="number" min={1} step="0.01" required
                placeholder="Price ৳" style={inputStyle} aria-label="Quoted price" />
              <input name="eta" type="number" min={1} defaultValue={3}
                placeholder="ETA days" style={inputStyle} aria-label="ETA days" />
              <input name="notes" placeholder="Notes" style={{ ...inputStyle, width: 240 }} aria-label="Notes" />
              <button type="submit" style={btn}>Submit quote</button>
              <button type="button" style={{ ...btn, background: tokens["color.surface.secondary"], color: tokens["color.text.secondary"] }}
                onClick={() => setQuoteFor(null)}>Cancel</button>
            </form>
          )}
        </section>
      ))}
      {jobs.length === 0 && (
        <p style={{ color: tokens["color.text.secondary"] }}>No open jobs right now.</p>
      )}
    </main>
  );
}
