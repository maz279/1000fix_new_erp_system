"use client";

/**
 * Brand remittance & reconciliation — approved vs advised vs money received,
 * with mismatches FLAGGED (never auto-adjusted). A remittance advice is the
 * brand's word; Odoo settles the claim only when an officer records the money
 * received against a bank reference.
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

interface ReconRow {
  id: number;
  claim_no: string;
  state: string;
  expected_bdt: string;
  received_bdt: string;
  advised_bdt: string;
  mismatch: boolean;
  variance_bdt: string;
}

interface Summary {
  totals?: {
    approved_bdt?: string;
    remitted_bdt?: string;
    advised_bdt?: string;
    outstanding_bdt?: string;
  };
  reconciliation?: { mismatches?: number; variance_bdt?: string };
}

export default function ReconciliationPage() {
  const { ready, error: scopeError, brandId, brand } = useBrand();
  const [rows, setRows] = useState<ReconRow[]>([]);
  const [summary, setSummary] = useState<Summary>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [mismatchOnly, setMismatchOnly] = useState(false);
  const [claimId, setClaimId] = useState("");
  const [amount, setAmount] = useState("");
  const [bankRef, setBankRef] = useState("");

  const load = useCallback(async () => {
    if (brandId == null) return;
    const [r, s] = await Promise.all([
      callOdoo<{ reconciliation?: ReconRow[]; error?: { message: string } }>(
        "/brand/portal/reconciliation",
        { brand_id: brandId }
      ),
      callOdoo<Summary>("/brand/portal/summary", { brand_id: brandId }),
    ]);
    if (r.error) setError(r.error.message);
    else {
      setRows(r.reconciliation ?? []);
      setSummary(s);
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

  const filtered = useMemo(
    () => (mismatchOnly ? rows.filter((r) => r.mismatch) : rows),
    [rows, mismatchOnly]
  );

  const submitAdvice = async (e: FormEvent) => {
    e.preventDefault();
    if (brandId == null || !claimId) return;
    setBusy(true);
    setError(null);
    try {
      const d = await callOdoo<{
        remittance?: { claim_no: string; mismatch: boolean; status: string };
        error?: { message: string };
      }>("/brand/portal/reconciliation", {
        brand_id: brandId,
        claim_id: Number(claimId),
        amount: Number(amount),
        bank_ref: bankRef,
      });
      if (d.error) throw new Error(d.error.message);
      setNotice(
        `${d.remittance?.claim_no} advice noted${d.remittance?.mismatch ? " — MISMATCH FLAGGED (advice ≠ approved)" : ""}`
      );
      setClaimId("");
      setAmount("");
      setBankRef("");
      await load();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const exportCsv = () =>
    downloadCsv(
      `1000fix-brand-reconciliation-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Claim", "State", "Approved (BDT)", "Advised (BDT)", "Received (BDT)", "Variance (BDT)", "Mismatch"],
      rows.map((r) => [
        r.claim_no,
        r.state,
        r.expected_bdt,
        r.advised_bdt,
        r.received_bdt,
        r.variance_bdt,
        r.mismatch ? "FLAGGED" : "",
      ])
    );

  if (!ready) return <Loading label="Resolving your brand access…" />;
  if (scopeError) return <LoadError what="brand access" message={scopeError} />;
  if (brandId == null) return <LoadError what="brand access" message="No brand is linked to this account." />;
  if (loading) return <Loading label="Loading reconciliation…" />;
  if (error && rows.length === 0) return <LoadError what="reconciliation" message={error} />;

  const totals = summary.totals ?? {};
  const mismatches = summary.reconciliation?.mismatches ?? 0;

  return (
    <main style={pageStyle}>
      <PageHeader
        title={`${brand?.name ?? "Brand"} — remittance reconciliation`}
        subtitle="Approved vs advised vs money received. A mismatch is flagged and stands until a human clears it — never auto-adjusted."
        actions={
          <button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>
            ⬇ Export CSV
          </button>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label="Approved" value={`৳ ${totals.approved_bdt ?? "0.00"}`} tone="success" />
        <StatCard label="Advised" value={`৳ ${totals.advised_bdt ?? "0.00"}`} tone="warning" />
        <StatCard label="Received" value={`৳ ${totals.remitted_bdt ?? "0.00"}`} tone="success" />
        <StatCard label="Outstanding" value={`৳ ${totals.outstanding_bdt ?? "0.00"}`} tone="warning" />
        <StatCard label="Mismatches" value={mismatches} note={`variance ৳ ${summary.reconciliation?.variance_bdt ?? "0.00"}`} tone={mismatches ? "error" : "success"} />
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

      <Panel title="Remittance advice">
        <form onSubmit={submitAdvice} style={{ padding: 16, display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
          <div>
            <label htmlFor="advice-claim" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>Claim</label>
            <select id="advice-claim" required value={claimId} onChange={(e) => setClaimId(e.target.value)} style={{ ...selectStyle, minWidth: 220 }}>
              <option value="">Select an approved claim…</option>
              {rows.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.claim_no} — approved ৳{r.expected_bdt}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label htmlFor="advice-amount" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>Advised amount</label>
            <input id="advice-amount" type="number" min={0} step="0.01" required value={amount} onChange={(e) => setAmount(e.target.value)} placeholder="৳" style={{ ...selectStyle, width: 150 }} />
          </div>
          <div>
            <label htmlFor="advice-ref" style={{ display: "block", marginBottom: 4, fontSize: 12, fontWeight: 600 }}>Bank / remittance ref</label>
            <input id="advice-ref" required value={bankRef} onChange={(e) => setBankRef(e.target.value)} placeholder="Bank reference" style={{ ...selectStyle, width: 200 }} />
          </div>
          <button type="submit" disabled={busy} style={{ ...primaryLinkStyle, border: "none", cursor: busy ? "wait" : "pointer", opacity: busy ? 0.7 : 1 }}>
            {busy ? "Recording…" : "Record advice"}
          </button>
        </form>
        <p style={{ margin: 0, padding: "0 16px 14px", fontSize: 11.5, color: tokens["color.text.secondary"] }}>
          An advice records what your brand says it will remit; the claim is settled only when 1000 FiX
          records the money received against a bank reference.
        </p>
      </Panel>

      <div style={{ display: "flex", gap: 12, alignItems: "center", margin: "16px 0 12px" }}>
        <label style={{ display: "inline-flex", alignItems: "center", gap: 8, fontSize: 12.5 }}>
          <input type="checkbox" checked={mismatchOnly} onChange={(e) => setMismatchOnly(e.target.checked)} />
          Mismatches only
        </label>
        <span style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>
          {filtered.length} of {rows.length} approved/remitted claims
        </span>
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Claim</th>
                <th style={thStyle}>State</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Approved</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Advised</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Received</th>
                <th style={{ ...thStyle, textAlign: "right" }}>Variance</th>
                <th style={thStyle}>Match</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((r) => (
                <tr key={r.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{r.claim_no}</td>
                  <td style={tdStyle}><StateBadge state={r.state} /></td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {r.expected_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {r.advised_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums" }}>৳ {r.received_bdt}</td>
                  <td style={{ ...tdStyle, textAlign: "right", fontVariantNumeric: "tabular-nums", color: r.mismatch ? tokens["color.status.error"] : tokens["color.text.primary"] }}>
                    ৳ {r.variance_bdt}
                  </td>
                  <td style={tdStyle}>
                    {r.mismatch ? (
                      <Badge tone="error">flagged</Badge>
                    ) : r.state === "remitted" ? (
                      <Badge tone="success">matched</Badge>
                    ) : (
                      "—"
                    )}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 26 }}>
                    No approved / remitted claims in this view.
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
