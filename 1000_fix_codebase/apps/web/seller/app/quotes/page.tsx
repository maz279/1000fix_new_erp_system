"use client";

/* P07 Seller Quotes Board — the seller's own submitted quotes from
 * /seller/quotes (list mode: no order_id). Prices arrive as backend
 * BN-007 strings (AS-10); counts are of the rows the backend returned.
 * WCAG 2.2 AA compliant. */
import { useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Loading, LoadError, Stat } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface QuoteItem {
  id: number;
  order_name: string;
  price_bdt: string;
  eta_days: number;
  state: string;
}

// fix.seller.quote.state values (cd_marketplace)
const FILTERS = [
  ["all", "All"],
  ["submitted", "Submitted"],
  ["selected", "Selected"],
  ["not_selected", "Not selected"],
] as const;

export default function SellerQuotesPage() {
  const [quotes, setQuotes] = useState<QuoteItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<string>("all");

  useEffect(() => {
    callOdoo<{ quotes?: QuoteItem[]; error?: { message: string } } | undefined>("/seller/quotes")
      .then((d) => {
        if (!d) setError("The server returned an empty response.");
        else if (d.error) setError(d.error.message);
        else setQuotes(d.quotes ?? []);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Loading />;
  if (error) return <LoadError what="quotes" message={error} />;

  const filteredQuotes = filter === "all" ? quotes : quotes.filter((q) => q.state === filter);
  const submittedCount = quotes.filter((q) => q.state === "submitted").length;

  return (
    <main style={{ padding: 32, maxWidth: 1000, margin: "0 auto" }}>
      <SectionHead
        title="Seller Quotes"
        note="Quotes you have submitted on marketplace repair jobs (M12) — submit new quotes from the Jobs board"
      />

      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <Stat label="Total Quotes" value={quotes.length} />
        <Stat label="Awaiting Decision" value={submittedCount} tone="primary" />
      </div>

      <div
        style={{ display: "flex", gap: 8, marginBottom: 16, alignItems: "center", flexWrap: "wrap" }}
        role="group"
        aria-label="Filter Quotes by Status"
      >
        <span style={{ fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
          Filter:
        </span>
        {FILTERS.map(([st, label]) => (
          <button
            key={st}
            type="button"
            aria-pressed={filter === st}
            onClick={() => setFilter(st)}
            style={{
              padding: "6px 14px",
              border: `1px solid ${
                filter === st ? tokens["color.primary.base"] : tokens["color.border.default"]
              }`,
              background:
                filter === st ? tokens["color.primary.base"] : tokens["color.surface.primary"],
              color:
                filter === st ? tokens["color.text.inverse"] : tokens["color.text.primary"],
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: tokens["typography.size.200"],
              cursor: "pointer",
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {quotes.length === 0 ? (
        <p style={{ color: tokens["color.text.secondary"] }}>
          You have not submitted any quotes yet. Open the{" "}
          <a href="/jobs" style={{ color: tokens["color.primary.base"] }}>Jobs</a> board to quote on open repair jobs.
        </p>
      ) : filteredQuotes.length === 0 ? (
        <p style={{ color: tokens["color.text.secondary"] }}>No quotes in this state.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {filteredQuotes.map((q) => (
            <article
              key={q.id}
              style={{
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-md"],
                background: tokens["color.surface.primary"],
                padding: 20,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  marginBottom: 8,
                }}
              >
                <strong style={{ fontSize: tokens["typography.size.300"] }}>{q.order_name || `Quote #${q.id}`}</strong>
                <Pill state={q.state} />
              </div>
              <div style={{ display: "flex", gap: 24, fontSize: tokens["typography.size.200"], flexWrap: "wrap" }}>
                <div>
                  Quoted:{" "}
                  <strong style={{ color: tokens["color.primary.base"], fontVariantNumeric: "tabular-nums" }}>
                    ৳ {q.price_bdt}
                  </strong>
                </div>
                <div>
                  ETA: <span>{q.eta_days} {q.eta_days === 1 ? "day" : "days"}</span>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </main>
  );
}
