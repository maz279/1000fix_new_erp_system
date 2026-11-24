"use client";

/**
 * Brand dashboard — the brand's claim posture: state mix, claimed/approved/
 * remitted/outstanding totals, reconciliation mismatch flags and the recent
 * claim queue. The brand is resolved from the session by the server.
 */
import { useEffect, useState } from "react";
import Link from "next/link";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useBrand } from "../../components/brand-context";
import {
  Badge,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  linkButtonStyle,
  pageStyle,
  primaryLinkStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Summary {
  brand?: { id: number; name: string; code: string };
  claims_by_state?: Record<string, number>;
  total_claims?: number;
  awaiting_decision?: number;
  totals?: {
    claimed_bdt?: string;
    approved_bdt?: string;
    remitted_bdt?: string;
    outstanding_bdt?: string;
  };
  reconciliation?: { mismatches?: number; variance_bdt?: string };
  generated_at?: string;
  error?: { message: string };
}

interface Claim {
  id: number;
  claim_no: string;
  state: string;
  amount_bdt: string;
  approved_bdt: string;
  submitted_at: string | null;
  evidence_complete: boolean;
  missing_evidence: string;
}

/** Odoo datetimes are UTC "YYYY-MM-DD HH:MM:SS"; Date.parse needs the T/Z form. */
function ageDays(submittedAt: string | null): number | null {
  if (!submittedAt) return null;
  const raw = submittedAt.includes("T") ? submittedAt : `${submittedAt.replace(" ", "T")}Z`;
  const then = Date.parse(raw);
  if (Number.isNaN(then)) return null;
  return Math.max(0, Math.floor((Date.now() - then) / 86_400_000));
}

export default function BrandDashboardPage() {
  const { ready, error: scopeError, brandId, brand } = useBrand();
  const [summary, setSummary] = useState<Summary | null>(null);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ready || brandId == null) return;
    let active = true;
    setLoading(true);
    Promise.all([
      callOdoo<Summary>("/brand/portal/summary", { brand_id: brandId }),
      callOdoo<{ claims?: Claim[] }>("/brand/portal/claims", { brand_id: brandId }).catch(() => ({ claims: [] })),
    ])
      .then(([s, c]) => {
        if (!active) return;
        if (s.error) setError(s.error.message);
        else setSummary(s);
        setClaims(c.claims ?? []);
        setLoading(false);
      })
      .catch((e: Error) => {
        if (!active) return;
        setError(e.message);
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [ready, brandId]);

  if (!ready) return <Loading label="Resolving your brand access…" />;
  if (scopeError) return <LoadError what="brand access" message={scopeError} />;
  if (brandId == null) return <LoadError what="brand access" message="No brand is linked to this account." />;
  if (loading) return <Loading label="Loading the brand claim posture…" />;
  if (error || !summary) return <LoadError what="brand summary" message={error || "No summary returned."} />;

  const totals = summary.totals ?? {};
  const mismatches = summary.reconciliation?.mismatches ?? 0;
  const awaitingClaims = claims.filter((c) => ["submitted", "in_review"].includes(c.state));
  const ages = awaitingClaims
    .map((c) => ageDays(c.submitted_at))
    .filter((d): d is number => d != null);
  const oldest = ages.length ? Math.max(...ages) : null;
  const aging = {
    fresh: ages.filter((d) => d <= 7).length,
    watch: ages.filter((d) => d > 7 && d <= 14).length,
    overdue: ages.filter((d) => d > 14).length,
  };

  return (
    <main style={pageStyle}>
      <PageHeader
        title={`${brand?.name ?? summary.brand?.name ?? "Brand"} — claim posture`}
        subtitle="Claimed, approved, remitted and outstanding amounts with the state mix and reconciliation flags."
        actions={
          <>
            <Link href="/claims" style={{ ...primaryLinkStyle, textDecoration: "none" }}>
              Claim queue
            </Link>
            <Link href="/reconciliation" style={{ ...linkButtonStyle, textDecoration: "none" }}>
              Reconciliation
            </Link>
          </>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Total claims" value={summary.total_claims ?? 0} tone="primary" />
        <StatCard label="Awaiting decision" value={summary.awaiting_decision ?? 0} tone="warning" />
        <StatCard label="Claimed" value={`৳ ${totals.claimed_bdt ?? "0.00"}`} />
        <StatCard label="Approved" value={`৳ ${totals.approved_bdt ?? "0.00"}`} tone="success" />
        <StatCard label="Remitted" value={`৳ ${totals.remitted_bdt ?? "0.00"}`} tone="success" />
        <StatCard label="Outstanding" value={`৳ ${totals.outstanding_bdt ?? "0.00"}`} tone="warning" />
        <StatCard
          label="Mismatches"
          value={mismatches}
          note={`variance ৳ ${summary.reconciliation?.variance_bdt ?? "0.00"}`}
          tone={mismatches ? "error" : "success"}
        />
      </section>

      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
        {Object.entries(summary.claims_by_state ?? {}).map(([state, count]) => (
          <span
            key={state}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              padding: "5px 10px",
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-pill"],
              fontSize: 12,
              background: tokens["color.surface.primary"],
            }}
          >
            <StateBadge state={state} />
            <b>{count}</b>
          </span>
        ))}
      </div>

      <Panel title="Decision aging (SLA watch)">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 12, padding: 16 }}>
          <StatCard
            label="Oldest awaiting"
            value={oldest == null ? "—" : `${oldest} days`}
            tone={oldest != null && oldest > 14 ? "error" : oldest != null && oldest > 7 ? "warning" : "neutral"}
          />
          <StatCard label="0–7 days" value={aging.fresh} tone="success" />
          <StatCard label="8–14 days" value={aging.watch} tone={aging.watch ? "warning" : "neutral"} />
          <StatCard label="15+ days" value={aging.overdue} tone={aging.overdue ? "error" : "neutral"} />
        </div>
        <p style={{ margin: 0, padding: "0 16px 14px", fontSize: 11.5, color: tokens["color.text.secondary"] }}>
          Aging runs from the claim&apos;s submitted timestamp for claims still awaiting the brand&apos;s
          decision. Anything past 14 days should be escalated to the warranty desk on 16743.
        </p>
      </Panel>

      <Panel
        title="Recent claims"
        actions={
          <Link href="/claims" style={{ fontSize: 12, color: tokens["color.primary.base"], textDecoration: "none", fontWeight: 600 }}>
            View all
          </Link>
        }
      >
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Claim</th>
                <th style={thStyle}>Submitted</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Claimed</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Approved</th>
                <th style={thStyle}>Evidence</th>
                <th style={thStyle}>State</th>
              </tr>
            </thead>
            <tbody>
              {claims.slice(0, 6).map((c) => (
                <tr key={c.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{c.claim_no}</td>
                  <td style={tdStyle}>{c.submitted_at ? c.submitted_at.slice(0, 10) : "—"}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {c.amount_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {c.approved_bdt}</td>
                  <td style={tdStyle}>
                    {c.evidence_complete ? (
                      <Badge tone="success">complete</Badge>
                    ) : (
                      <Badge tone="warning">missing: {c.missing_evidence || "?"}</Badge>
                    )}
                  </td>
                  <td style={tdStyle}><StateBadge state={c.state} /></td>
                </tr>
              ))}
              {claims.length === 0 && (
                <tr>
                  <td colSpan={6} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 24 }}>
                    No claims recorded for this brand yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <p style={{ marginTop: 12, fontSize: 11, color: tokens["color.text.secondary"] }}>
        Generated {summary.generated_at ? summary.generated_at.slice(0, 16) : "—"} from the live claim
        estate. Admins and staff never act as the brand here; decisions are recorded against the brand user.
      </p>
    </main>
  );
}
