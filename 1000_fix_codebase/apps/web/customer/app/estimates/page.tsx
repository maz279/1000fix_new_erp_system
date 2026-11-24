"use client";

/* P01 estimate approval — customer approval enforcement (Dual Language: Bengali-first + English).
 * Mushak 6.3 breakdown preview & Proof reference (OTP id / e-sign ref) enforced server-side (BRU-SRM-07).
 * Gate rejections render inline; money arrives formatted (AS-10).
 * Accessible dialog modal replaces window.prompt().
 * Tokens only (CFM-01) — no hand-authored colors. */
import { useCallback, useEffect, useState, useId } from "react";
import { tokens, SectionHead, DataTable, Loading, LoadError, Pill } from "../../lib/imports";
import type { Column } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { RequireAuth } from "../../components/require-auth";
import { useAuth } from "../../components/auth-modal";

interface Estimate {
  id: number;
  order_ref: string;
  device?: string;
  version: number;
  parts_total_bdt: string;
  labour_total_bdt: string;
  diagnostic_total_bdt: string;
  discount_bdt: string;
  vat_rate: number;
  vat_amount_bdt: string;
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

const inputStyle: React.CSSProperties = {
  width: "100%",
  boxSizing: "border-box",
  padding: 10,
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
};

function EstimatesPageContent() {
  const { t, locale } = useLanguage();
  const { user } = useAuth();
  const [rows, setRows] = useState<Estimate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // Approval Modal State (Replaces window.prompt)
  const [approvingEstimate, setApprovingEstimate] = useState<Estimate | null>(null);
  const [approvalRef, setApprovalRef] = useState("");
  const [approveBusy, setApproveBusy] = useState(false);
  const [approveError, setApproveError] = useState<string | null>(null);

  const approvalRefInputId = useId();

  const reload = useCallback(async () => {
    const d = await callOdoo<{ estimates: Estimate[] }>("/customer/estimates");
    setRows(d.estimates || []);
  }, []);

  useEffect(() => {
    reload()
      .then(() => setLoading(false))
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, [reload, user]);

  // Escape key listener for approval modal
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setApprovingEstimate(null);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  async function handleApproveSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!approvingEstimate) return;
    if (!approvalRef.trim()) {
      setApproveError(locale === "bn" ? "অনুমোদন রেফারেন্স বা ওটিপি আইডি আবশ্যক" : "Approval reference or OTP ID is required");
      return;
    }
    setApproveBusy(true);
    setApproveError(null);
    try {
      const d = await callOdoo<{ estimate?: { state: string }; error?: { message: string } }>(
        "/customer/estimates", {
          estimate_id: approvingEstimate.id,
          action: "approve",
          approval_ref: approvalRef.trim(),
        });
      if (d.error) {
        setApproveError(d.error.message);
      } else {
        setNotice(t.estimatesNoticeDone);
        setApprovingEstimate(null);
        setApprovalRef("");
        reload();
      }
    } catch (err) {
      setApproveError((err as Error).message);
    } finally {
      setApproveBusy(false);
    }
  }

  async function handleReject(e: Estimate) {
    const d = await callOdoo<{ estimate?: { state: string }; error?: { message: string } }>(
      "/customer/estimates", {
        estimate_id: e.id,
        action: "reject",
      });
    setNotice(d.error ? d.error.message : (locale === "bn" ? "এস্টিমেট প্রত্যাখ্যাত হয়েছে" : "Estimate rejected"));
    if (!d.error) reload();
  }

  if (loading) return <Loading label={t.loading} />;
  if (error) return <LoadError what={t.loadErrorTitle(locale === "bn" ? "অনুমান" : "Estimates")} message={error} />;

  const columns: Column<Estimate>[] = [
    { header: t.estimatesColOrder, cell: (e) => e.order_ref },
    { header: t.estimatesColVersion, cell: (e) => `v${e.version}` },
    {
      header: locale === "bn" ? "ডিভাইস" : "Device",
      cell: (e) => e.device || "—",
    },
    {
      header: t.estimatesColTotal,
      cell: (e) => <span style={{ fontVariantNumeric: "tabular-nums", fontWeight: 600 }}>৳ {e.grand_total_bdt}</span>,
    },
    { header: t.estimatesColExpiry, cell: (e) => e.expiry || "—" },
    {
      header: t.estimatesColAction,
      cell: (e) => (
        <span style={{ display: "flex", gap: 8 }}>
          <button
            style={{ ...btn, background: tokens["color.primary.base"], color: tokens["color.text.inverse"] }}
            onClick={() => {
              setApprovingEstimate(e);
              setApprovalRef(`OTP-${Date.now().toString().slice(-6)}`);
              setApproveError(null);
            }}
          >
            {t.estimatesApprove}
          </button>
          <button
            style={{ ...btn, background: tokens["color.status.error-bg"], color: tokens["color.status.error"] }}
            onClick={() => handleReject(e)}
          >
            {t.estimatesReject}
          </button>
        </span>
      ),
    },
  ];

  return (
    <main style={{ padding: 32, maxWidth: 900 }}>
      <SectionHead
        title={t.estimatesTitle}
        note={t.estimatesSubtitle}
      />
      {notice && (
        <p
          role="status"
          style={{
            padding: "10px 14px",
            marginBottom: 16,
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.status.info-bg"],
            color: tokens["color.status.info"],
            fontSize: tokens["typography.size.200"],
          }}
        >
          {notice}
        </p>
      )}

      {rows.length === 0 ? (
        <p style={{ color: tokens["color.text.secondary"], marginTop: 16 }}>{t.estimatesEmpty}</p>
      ) : (
        <DataTable rows={rows} columns={columns} keyOf={(e) => e.id} />
      )}

      <p style={{ marginTop: 16, fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
        {t.estimatesLegend}
      </p>

      {/* ACCESSIBLE ESTIMATE APPROVAL & MUSHAK 6.3 MODAL */}
      {approvingEstimate && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="approve-modal-title"
          style={{
            position: "fixed",
            inset: 0,
            display: "grid",
            placeItems: "center",
            background: "rgba(0, 0, 0, 0.5)",
            backdropFilter: "blur(3px)",
            zIndex: 1000,
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) setApprovingEstimate(null);
          }}
        >
          <div
            style={{
              maxWidth: 520,
              width: "100%",
              margin: 16,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.25)",
              padding: 24,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <h3 id="approve-modal-title" style={{ margin: 0, fontSize: tokens["typography.size.300"], color: tokens["color.primary.base"] }}>
                {t.estimatesApproveModalTitle}
              </h3>
              <button
                type="button"
                onClick={() => setApprovingEstimate(null)}
                aria-label={locale === "bn" ? "বন্ধ করুন" : "Close"}
                style={{ background: "transparent", border: "none", color: tokens["color.text.secondary"], fontSize: tokens["typography.size.400"], cursor: "pointer" }}
              >
                ✕
              </button>
            </div>

            <p style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.100"], margin: "0 0 16px" }}>
              {t.estimatesMushakTitle}
            </p>

            {/* MUSHAK 6.3 TAX BREAKDOWN TABLE */}
            <div
              style={{
                background: tokens["color.surface.secondary"],
                borderRadius: tokens["dimension.border.radius-sm"],
                padding: 16,
                marginBottom: 16,
                display: "grid",
                gridTemplateColumns: "1fr auto",
                gap: "8px 16px",
                fontSize: tokens["typography.size.200"],
              }}
            >
              <span>{t.estimatesPartsTotal}:</span>
              <strong style={{ fontVariantNumeric: "tabular-nums" }}>৳ {approvingEstimate.parts_total_bdt || "0.00"}</strong>

              <span>{t.estimatesLabourTotal}:</span>
              <strong style={{ fontVariantNumeric: "tabular-nums" }}>৳ {approvingEstimate.labour_total_bdt || "0.00"}</strong>

              <span>{t.estimatesDiagnosticTotal}:</span>
              <strong style={{ fontVariantNumeric: "tabular-nums" }}>৳ {approvingEstimate.diagnostic_total_bdt || "0.00"}</strong>

              <span>{t.estimatesDiscount}:</span>
              <span style={{ color: tokens["color.status.success"], fontVariantNumeric: "tabular-nums" }}>
                - ৳ {approvingEstimate.discount_bdt || "0.00"}
              </span>

              <span>{t.estimatesVatRate}:</span>
              <span style={{ fontVariantNumeric: "tabular-nums" }}>৳ {approvingEstimate.vat_amount_bdt || "0.00"}</span>

              <div style={{ gridColumn: "1 / -1", height: 1, background: tokens["color.border.default"], margin: "6px 0" }} />

              <span style={{ fontWeight: 700, fontSize: tokens["typography.size.300"] }}>{t.estimatesGrandTotal}:</span>
              <strong style={{ fontWeight: 700, fontSize: tokens["typography.size.300"], color: tokens["color.primary.base"], fontVariantNumeric: "tabular-nums" }}>
                ৳ {approvingEstimate.grand_total_bdt}
              </strong>
            </div>

            <form onSubmit={handleApproveSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div>
                <label
                  htmlFor={approvalRefInputId}
                  style={{ display: "block", marginBottom: 6, fontSize: tokens["typography.size.200"], fontWeight: 500 }}
                >
                  {t.estimatesApprovalRefLabel} *
                </label>
                <input
                  id={approvalRefInputId}
                  type="text"
                  required
                  value={approvalRef}
                  onChange={(e) => setApprovalRef(e.target.value)}
                  placeholder={t.estimatesApprovalRefPlaceholder}
                  style={inputStyle}
                />
                <small style={{ color: tokens["color.text.secondary"], display: "block", marginTop: 4 }}>
                  {locale === "bn"
                    ? "বিটিআরসি ও বিআরইউ-এসআরএম-০৭ অনুযায়ী গ্রাহকের যাচাইযোগ্য ওটিপি আইডি বা ডিজিটাল স্বাক্ষর অপরিহার্য।"
                    : "BRU-SRM-07: A verifiable OTP ID or digital signature reference is legally mandated."}
                </small>
              </div>

              {approveError && (
                <p role="alert" style={{ margin: 0, padding: "8px 12px", background: tokens["color.status.error-bg"], color: tokens["color.status.error"], borderRadius: tokens["dimension.border.radius-sm"], fontSize: tokens["typography.size.200"] }}>
                  {approveError}
                </p>
              )}

              <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
                <button
                  type="button"
                  style={{ ...btn, background: tokens["color.surface.canvas"], color: tokens["color.text.secondary"], border: `1px solid ${tokens["color.border.default"]}` }}
                  onClick={() => setApprovingEstimate(null)}
                >
                  {locale === "bn" ? "বাতিল" : "Cancel"}
                </button>
                <button
                  type="submit"
                  disabled={approveBusy}
                  style={{
                    ...btn,
                    background: tokens["color.primary.base"],
                    color: tokens["color.text.inverse"],
                    fontWeight: 600,
                  }}
                >
                  {approveBusy ? (locale === "bn" ? "অনুমোদন হচ্ছে…" : "Approving…") : t.estimatesConfirmApprove}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}

export default function EstimatesPage() {
  return (
    <RequireAuth>
      <EstimatesPageContent />
    </RequireAuth>
  );
}
