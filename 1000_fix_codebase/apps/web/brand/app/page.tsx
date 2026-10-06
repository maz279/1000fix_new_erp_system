"use client";

/* P08 claims — the brand's claim queue with decision capture.
 * PER-BRAND ISOLATION: brand_id is required on every call (the server
 * refuses unscoped reads); it is picked once and held in sessionStorage.
 * Decisions ride the model's action_decide (SoD-11 companion). */
import { useCallback, useEffect, useState } from "react";
import { tokens, Pill, SectionHead, DataTable, Loading, LoadError, Stat } from "../lib/imports";
import type { Column } from "../lib/imports";
import { callOdoo } from "../lib/api";

interface Claim {
  id: number; claim_no: string; state: string; amount_bdt: string;
  submitted_at: string | null; decided_at: string | null;
  rejection_reason: string; evidence_complete: boolean; missing_evidence: string;
}

const inputStyle: React.CSSProperties = {
  padding: 10,
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
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

export default function BrandClaimsPage() {
  const [brandId, setBrandId] = useState<number | null>(null);
  const [brandInput, setBrandInput] = useState("");
  const [claims, setClaims] = useState<Claim[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const load = useCallback(async (bid: number) => {
    setLoading(true);
    try {
      const d = await callOdoo<{ claims?: Claim[]; error?: { message: string } }>(
        "/brand/claims", { brand_id: bid });
      if (d.error) setError(d.error.message);
      else { setClaims(d.claims || []); setError(null); }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const saved = window.sessionStorage.getItem("fix_brand_id");
    if (saved) {
      const bid = Number(saved);
      setBrandId(bid);
      load(bid);
    }
  }, [load]);

  function pickBrand(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const bid = Number(brandInput);
    if (!bid) return;
    window.sessionStorage.setItem("fix_brand_id", String(bid));
    setBrandId(bid);
    load(bid);
  }

  async function decide(c: Claim, decision: "approve" | "reject") {
    let reason = "";
    if (decision === "reject") {
      reason = window.prompt(`Rejection reason for ${c.claim_no}:`) || "";
      if (!reason) return;
    }
    const d = await callOdoo<{ claim?: { state: string }; error?: { message: string } }>(
      "/brand/claims", {
        brand_id: brandId, claim_id: c.id, decision, reason,
      });
    setNotice(d.error ? d.error.message : `${c.claim_no}: ${d.claim?.state}`);
    if (!d.error && brandId) load(brandId);
  }

  if (brandId == null) {
    return (
      <main style={{ padding: 32, maxWidth: 480 }}>
        <SectionHead
          title="Select your brand"
          note="Per-brand isolation: every request carries brand_id — the server refuses unscoped reads"
        />
        <form onSubmit={pickBrand}>
          <input type="number" required value={brandInput}
            onChange={(e) => setBrandInput(e.target.value)}
            placeholder="Brand ID" style={inputStyle} aria-label="Brand ID" />
          <button type="submit" style={{ ...btn, marginLeft: 8 }}>Open claims</button>
        </form>
      </main>
    );
  }

  const submitted = claims.filter((c) => c.state === "submitted").length;
  const columns: Column<Claim>[] = [
    { header: "Claim", cell: (c) => c.claim_no },
    { header: "Amount (BDT)", cell: (c) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{c.amount_bdt}</span> },
    { header: "Submitted", cell: (c) => c.submitted_at?.slice(0, 10) || "—" },
    { header: "State", cell: (c) => <Pill state={c.state} /> },
    {
      header: "Evidence",
      cell: (c) => c.evidence_complete
        ? <Pill state="matched" label="complete" />
        : <span title={c.missing_evidence} style={{ color: tokens["color.status.warning"] }}>
            missing: {c.missing_evidence || "?"}
          </span>,
    },
    {
      header: "Decision",
      cell: (c) => c.state === "submitted" ? (
        <span style={{ display: "flex", gap: 8 }}>
          <button style={{ ...btn, background: tokens["color.status.success-bg"], color: tokens["color.status.success"] }}
            onClick={() => decide(c, "approve")}>Approve</button>
          <button style={{ ...btn, background: tokens["color.status.error-bg"], color: tokens["color.status.error"] }}
            onClick={() => decide(c, "reject")}>Reject</button>
        </span>
      ) : c.rejection_reason ? c.rejection_reason : "—",
    },
  ];

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title={`Claims — brand #${brandId}`}
        note="Submitted claims await the brand's decision; the evidence pack is the rule set's local half (T05)"
      />
      <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Stat label="Claims" value={claims.length} />
        <Stat label="Awaiting decision" value={submitted} tone="primary" />
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
      {loading ? <Loading /> : error ? <LoadError what="claims" message={error} /> : (
        <DataTable rows={claims} columns={columns} />
      )}
    </main>
  );
}
