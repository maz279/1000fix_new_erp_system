"use client";

/**
 * Brand claim queue — submitted claims for the resolved brand, evidence
 * completeness and the brand's own decision (approve / partial / reject with
 * a reason). The decision rides the model's action_decide; the portal never
 * writes the state directly.
 */
import { useCallback, useEffect, useMemo, useState, type FormEvent } from "react";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useBrand } from "../../components/brand-context";
import {
  Badge,
  PageHeader,
  Panel,
  StateBadge,
  StatCard,
  downloadCsv,
  linkButtonStyle,
  pageStyle,
  primaryLinkStyle,
  selectStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Claim {
  id: number;
  claim_no: string;
  state: string;
  amount_bdt: string;
  approved_bdt: string;
  submitted_at: string | null;
  decided_at: string | null;
  rejection_reason: string;
  evidence_complete: boolean;
  missing_evidence: string;
}

type Decision = "approve" | "reject";

/** Odoo datetimes are UTC "YYYY-MM-DD HH:MM:SS"; Date.parse needs the T/Z form. */
function ageDays(submittedAt: string | null): number | null {
  if (!submittedAt) return null;
  const raw = submittedAt.includes("T") ? submittedAt : `${submittedAt.replace(" ", "T")}Z`;
  const then = Date.parse(raw);
  if (Number.isNaN(then)) return null;
  return Math.max(0, Math.floor((Date.now() - then) / 86_400_000));
}

export default function BrandClaimsPage() {
  const { ready, error: scopeError, brandId, brand } = useBrand();
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [decisionFor, setDecisionFor] = useState<Claim | null>(null);
  const [decision, setDecision] = useState<Decision>("approve");
  const [approvedAmount, setApprovedAmount] = useState("");
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);
  const [stateFilter, setStateFilter] = useState("all");
  const [query, setQuery] = useState("");

  const load = useCallback(async () => {
    if (brandId == null) return;
    const d = await callOdoo<{ claims?: Claim[]; error?: { message: string } }>(
      "/brand/portal/claims",
      { brand_id: brandId }
    );
    if (d.error) setError(d.error.message);
    else {
      setClaims(d.claims ?? []);
      setError(null);
    }
  }, [brandId]);

  useEffect(() => {
    if (!ready || brandId == null) return;
    setLoading(true);
    load()
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [ready, brandId, load]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return claims.filter((c) => {
      const matchesState = stateFilter === "all" || c.state === stateFilter;
      const matchesQuery = !q || c.claim_no.toLowerCase().includes(q);
      return matchesState && matchesQuery;
    });
  }, [claims, stateFilter, query]);

  const openDecision = (claim: Claim, mode: Decision) => {
    setDecisionFor(claim);
    setDecision(mode);
    setApprovedAmount(mode === "approve" ? claim.approved_bdt.replace(/,/g, "") || "" : "");
    setReason("");
    setNotice(null);
  };

  const submitDecision = async (e: FormEvent) => {
    e.preventDefault();
    if (!decisionFor || brandId == null) return;
    if (decision === "reject" && !reason.trim()) {
      setError("A rejection needs a reason.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const params: Record<string, unknown> = {
        brand_id: brandId,
        claim_id: decisionFor.id,
        decision,
        reason: reason.trim(),
      };
      if (decision === "approve" && approvedAmount.trim()) {
        params.approved_amount = Number(approvedAmount);
      }
      const d = await callOdoo<{ claim?: { state: string }; error?: { message: string } }>(
        "/brand/portal/claims",
        params
      );
      if (d.error) throw new Error(d.error.message);
      setNotice(`${decisionFor.claim_no}: ${d.claim?.state ?? decision}`);
      setDecisionFor(null);
      await load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const exportCsv = () =>
    downloadCsv(
      `1000fix-brand-claims-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Claim", "State", "Claimed (BDT)", "Approved (BDT)", "Submitted", "Age (days)", "Decided", "Evidence complete", "Missing evidence", "Rejection reason"],
      claims.map((c) => [
        c.claim_no,
        c.state,
        c.amount_bdt,
        c.approved_bdt,
        c.submitted_at ?? "",
        ["submitted", "in_review"].includes(c.state) ? String(ageDays(c.submitted_at) ?? "") : "",
        c.decided_at ?? "",
        c.evidence_complete ? "Yes" : "No",
        c.missing_evidence,
        c.rejection_reason,
      ])
    );

  if (!ready) return <Loading label="Resolving your brand access…" />;
  if (scopeError) return <LoadError what="brand access" message={scopeError} />;
  if (brandId == null) return <LoadError what="brand access" message="No brand is linked to this account." />;
  if (loading) return <Loading label="Loading the claim queue…" />;
  if (error && claims.length === 0) return <LoadError what="claims" message={error} />;

  const awaiting = claims.filter((c) => ["submitted", "in_review"].includes(c.state)).length;
  const approved = claims.filter((c) => ["approved", "partially_approved", "remitted", "closed"].includes(c.state)).length;
  const rejected = claims.filter((c) => c.state === "rejected").length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title={`${brand?.name ?? "Brand"} claims`}
        subtitle="Submitted claims await the brand's decision; the evidence pack must be complete before a decision is defensible."
        actions={
          <button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>
            ⬇ Export CSV
          </button>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Claims" value={claims.length} tone="primary" />
        <StatCard label="Awaiting decision" value={awaiting} tone="warning" />
        <StatCard label="Approved / remitted" value={approved} tone="success" />
        <StatCard label="Rejected" value={rejected} tone={rejected ? "error" : "neutral"} />
      </section>

      {notice && (
        <div role="status" style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.success-bg"], color: tokens["color.status.success"], fontSize: 12.5 }}>
          {notice}
        </div>
      )}
      {error && (
        <div role="alert" style={{ marginBottom: 12, padding: "8px 12px", borderRadius: tokens["dimension.border.radius-sm"], background: tokens["color.status.error-bg"], color: tokens["color.status.error"], fontSize: 12.5 }}>
          {error}
        </div>
      )}

      {decisionFor && (
        <Panel title={`${decision === "approve" ? "Approve" : "Reject"} — ${decisionFor.claim_no}`}>
          <form onSubmit={submitDecision} style={{ padding: 16, display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
            {decision === "approve" && (
              <div>
                <label htmlFor="approved-amount" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>
                  Approved amount (leave blank for the full claim)
                </label>
                <input
                  id="approved-amount"
                  type="number"
                  min={0}
                  step="0.01"
                  value={approvedAmount}
                  onChange={(e) => setApprovedAmount(e.target.value)}
                  placeholder={`Claim ৳${decisionFor.amount_bdt}`}
                  style={{ ...selectStyle, width: 180 }}
                />
              </div>
            )}
            <div style={{ flex: "1 1 280px" }}>
              <label htmlFor="decision-reason" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>
                {decision === "reject" ? "Rejection reason (required)" : "Note (optional)"}
              </label>
              <input
                id="decision-reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder={decision === "reject" ? "Why is this claim rejected?" : "OEM reference / note"}
                style={{ ...selectStyle, width: "100%" }}
              />
            </div>
            <button type="submit" disabled={busy} style={{ ...primaryLinkStyle, border: "none", cursor: busy ? "wait" : "pointer", opacity: busy ? 0.7 : 1 }}>
              {busy ? "Recording…" : decision === "approve" ? "Approve claim" : "Reject claim"}
            </button>
            <button type="button" onClick={() => setDecisionFor(null)} style={{ ...linkButtonStyle, cursor: "pointer" }}>
              Cancel
            </button>
          </form>
        </Panel>
      )}

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", margin: "16px 0 12px" }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search claim no…"
          aria-label="Search claims"
          style={{ ...selectStyle, flex: "1 1 260px", maxWidth: 360 }}
        />
        <select value={stateFilter} onChange={(e) => setStateFilter(e.target.value)} aria-label="Claim state" style={selectStyle}>
          <option value="all">All states</option>
          <option value="submitted">Submitted</option>
          <option value="in_review">In review</option>
          <option value="approved">Approved</option>
          <option value="partially_approved">Partially approved</option>
          <option value="rejected">Rejected</option>
          <option value="remitted">Remitted</option>
        </select>
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
          {filtered.length} of {claims.length} claims
        </span>
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Claim</th>
                <th style={thStyle}>Submitted</th>
                <th style={thStyle}>Age</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Claimed</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Approved</th>
                <th style={thStyle}>Evidence</th>
                <th style={thStyle}>State</th>
                <th style={thStyle}>Decision</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => (
                <tr key={c.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{c.claim_no}</td>
                  <td style={tdStyle}>{c.submitted_at ? c.submitted_at.slice(0, 10) : "—"}</td>
                  <td
                    style={{
                      ...tdStyle,
                      fontVariantNumeric: "tabular-nums",
                      color:
                        ["submitted", "in_review"].includes(c.state) && (ageDays(c.submitted_at) ?? 0) > 14
                          ? tokens["color.status.error"]
                          : tokens["color.text.secondary"],
                    }}
                  >
                    {["submitted", "in_review"].includes(c.state) && ageDays(c.submitted_at) != null
                      ? `${ageDays(c.submitted_at)} d`
                      : "—"}
                  </td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {c.amount_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {c.approved_bdt}</td>
                  <td style={tdStyle}>
                    {c.evidence_complete ? (
                      <Badge tone="success">complete</Badge>
                    ) : (
                      <span title={c.missing_evidence} style={{ color: tokens["color.status.warning"], fontSize: 11.5 }}>
                        missing: {c.missing_evidence || "?"}
                      </span>
                    )}
                  </td>
                  <td style={tdStyle}><StateBadge state={c.state} /></td>
                  <td style={tdStyle}>
                    {["submitted", "in_review"].includes(c.state) ? (
                      <span style={{ display: "flex", gap: 6 }}>
                        <button type="button" onClick={() => openDecision(c, "approve")} style={{ ...linkButtonStyle, padding: "4px 10px", borderColor: tokens["color.status.success"], color: tokens["color.status.success"], cursor: "pointer" }}>
                          Approve
                        </button>
                        <button type="button" onClick={() => openDecision(c, "reject")} style={{ ...linkButtonStyle, padding: "4px 10px", borderColor: tokens["color.status.error"], color: tokens["color.status.error"], cursor: "pointer" }}>
                          Reject
                        </button>
                      </span>
                    ) : c.rejection_reason ? (
                      <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>{c.rejection_reason}</span>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={8} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 26 }}>
                    No claims in this filter.
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
