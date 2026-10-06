"use client";

/* P01 estimate approval — the customer documents their approval
 * (BRU-SRM-07: OTP id / e-sign ref), then the model's action_approve
 * enforces the hard gates server-side. Gate rejections render inline —
 * visible, never warned (G-series). Money arrives as BN-007 strings
 * (AS-10); this page never computes it. */
import { useCallback, useEffect, useState } from "react";
import { tokens, SectionHead, DataTable, Loading, LoadError, Pill } from "../../lib/imports";
import type { Column } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface Estimate {
  id: number;
  order_ref: string;
  version: number;
  grand_total_bdt: string;
  expiry: string;
  customer_approval_ref: string;
}

const btn: React.CSSProperties = {
  padding: "8px 16px",
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
};

export default function EstimatesPage() {
  const [rows, setRows] = useState<Estimate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const reload = useCallback(async () => {
    const d = await callOdoo<{ estimates: Estimate[] }>("/customer/estimates");
    setRows(d.estimates || []);
  }, []);

  useEffect(() => {
    reload()
      .then(() => setLoading(false))
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, [reload]);

  async function act(e: Estimate, action: "approve" | "reject") {
    let approvalRef = "";
    if (action === "approve") {
      approvalRef = window.prompt(
        "অনুমোদনের প্রমাণ দিন (OTP আইডি / ই-সাইন রেফারেন্স)") || "";
      if (!approvalRef) return;
    }
    const d = await callOdoo<{ estimate?: { state: string }; error?: { message: string } }>(
      "/customer/estimates", {
        estimate_id: e.id, action, approval_ref: approvalRef,
      });
    setNotice(d.error ? d.error.message : "সম্পন্ন হয়েছে");
    if (!d.error) reload();
  }

  if (loading) return <Loading label="লোড হচ্ছে…" />;
  if (error) return <LoadError what="অনুমান" message={error} />;

  const columns: Column<Estimate>[] = [
    { header: "অর্ডার", cell: (e) => e.order_ref },
    { header: "ভার্সন", cell: (e) => `v${e.version}` },
    { header: "মোট (৳)", cell: (e) => <span style={{ fontVariantNumeric: "tabular-nums" }}>{e.grand_total_bdt}</span> },
    { header: "মেয়াদ", cell: (e) => e.expiry || "—" },
    {
      header: "পদক্ষেপ",
      cell: (e) => (
        <span style={{ display: "flex", gap: 8 }}>
          <button style={{ ...btn, background: tokens["color.primary.base"], color: tokens["color.text.inverse"] }}
            onClick={() => act(e, "approve")}>অনুমোদন</button>
          <button style={{ ...btn, background: tokens["color.status.error-bg"], color: tokens["color.status.error"] }}
            onClick={() => act(e, "reject")}>বাতিল</button>
        </span>
      ),
    },
  ];

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="অনুমান অনুমোদন"
        note="৫,০০০ ৳ এর বেশি হলে লিখিত অনুমোদন আবশ্যক; ২৫,০০০ ৳ এর বেশি হলে ব্রাঞ্চ ম্যানেজারেরও অনুমোদন লাগবে (BRU-SRM-07/08)"
      />
      {notice && (
        <p role="status" style={{
          padding: "10px 14px", marginBottom: 16,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.status.info-bg"],
          color: tokens["color.status.info"],
          fontSize: tokens["typography.size.200"],
        }}>{notice}</p>
      )}
      {rows.length === 0
        ? <p style={{ color: tokens["color.text.secondary"] }}>এই মুহূর্তে অপেক্ষমান কোনো অনুমান নেই।</p>
        : <DataTable rows={rows} columns={columns} />}
      <p style={{ marginTop: 16, fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
        <Pill state="sent" /> = আপনার অনুমোদনের অপেক্ষায়
      </p>
    </main>
  );
}
