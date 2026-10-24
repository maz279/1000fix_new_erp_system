"use client";

/**
 * Consolidated Invoices Screen (PP3-M02-T01 / R05-M02-T01) — Multi-Job B2B Invoices.
 * ALL monetary values are backend-computed BN-007-formatted strings —
 * the portal renders, never calculates (AS-10/03 §8).
 * Zero local/mock data (FF-39). Tokens only (CFM-01).
 * Features:
 * - State filter tabs (Issued, Paid, Draft, Credited)
 * - Search filter (invoice #, customer)
 * - Bilingual support (English / বাংলা)
 * - Accessible table markup (WCAG 2.2 AA)
 */
import { useEffect, useState, useId } from "react";
import { tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { useAuth } from "../../components/auth-modal";

interface Invoice {
  id: number;
  invoice_no: string;
  customer: string;
  invoice_date: string;
  state: string;
  gross_bdt: string;
  vat_bdt: string;
  net_bdt: string;
}

const statePills: Record<string, { bg: string; fg: string }> = {
  issued: { bg: tokens["color.status.info-bg"], fg: tokens["color.status.info"] },
  paid: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  draft: { bg: tokens["color.status.neutral-bg"], fg: tokens["color.status.neutral"] },
  credited: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
};

export default function InvoicesPage() {
  const { t } = useLanguage();
  const { user, openLoginModal } = useAuth();
  const searchInputId = useId();

  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [stateFilter, setStateFilter] = useState<string>("all");

  const loadInvoices = () => {
    setLoading(true);
    setAuthError(false);
    setError(null);

    callOdoo<{ invoices: Invoice[]; total: number }>("/corporate/invoices/consolidated")
      .then((data) => {
        setInvoices(data.invoices || []);
        setLoading(false);
      })
      .catch((e: Error) => {
        const msg = e.message || "";
        if (
          msg.includes("Session expired") ||
          msg.includes("Odoo Session Expired") ||
          msg.includes("Unexpected token") ||
          msg.includes("is not valid JSON") ||
          msg.includes("<!DOCTYPE") ||
          !user
        ) {
          setAuthError(true);
        } else {
          setError(msg);
        }
        setLoading(false);
      });
  };

  useEffect(() => {
    loadInvoices();
  }, [user]);

  const filteredInvoices = invoices.filter((inv) => {
    const matchesSearch =
      inv.invoice_no.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inv.customer.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesState = stateFilter === "all" || inv.state.toLowerCase() === stateFilter.toLowerCase();
    return matchesSearch && matchesState;
  });

  return (
    <main style={{ padding: "32px 24px", maxWidth: 1280, margin: "0 auto" }}>
      {/* Page Header */}
      <div style={{ marginBottom: 24 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
          <div>
            <h1
              style={{
                margin: "0 0 6px",
                fontSize: tokens["typography.size.500"],
                color: tokens["color.text.primary"],
              }}
            >
              {t.invoicesTitle}
            </h1>
            <p
              style={{
                margin: "0 0 8px",
                color: tokens["color.text.secondary"],
                fontSize: tokens["typography.size.200"],
              }}
            >
              {t.invoicesSubtitle(invoices.length)}
            </p>
            <p
              style={{
                margin: 0,
                color: tokens["color.text.secondary"],
                fontSize: tokens["typography.size.100"],
              }}
            >
              ℹ️ {t.invoicesFinancialNote}
            </p>
          </div>

        </div>
      </div>

      {/* Unauthenticated Banner */}
      {authError && (
        <div
          role="alert"
          style={{
            padding: 20,
            marginBottom: 24,
            background: tokens["color.surface.primary"],
            border: `1px solid ${tokens["color.primary.base"]}`,
            borderRadius: tokens["dimension.border.radius-md"],
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div>
            <strong style={{ color: tokens["color.text.primary"], fontSize: tokens["typography.size.300"] }}>
              🔐 {t.unauthenticatedNotice}
            </strong>
          </div>
          <button
            onClick={openLoginModal}
            style={{
              padding: "8px 16px",
              background: tokens["color.primary.base"],
              color: tokens["color.text.inverse"],
              border: "none",
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: tokens["typography.size.200"],
              cursor: "pointer",
            }}
          >
            {t.unauthenticatedSignInBtn}
          </button>
        </div>
      )}

      {error && (
        <div
          role="alert"
          style={{
            padding: 12,
            marginBottom: 20,
            background: tokens["color.status.error-bg"],
            color: tokens["color.status.error"],
            border: `1px solid ${tokens["color.status.error"]}`,
            borderRadius: tokens["dimension.border.radius-sm"],
            fontSize: tokens["typography.size.200"],
          }}
        >
          ⚠️ {t.errorPrefix} {error}
        </div>
      )}

      {/* Search & State Filter Controls */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 16,
          marginBottom: 20,
        }}
      >
        {/* Search Input */}
        <div style={{ flex: "1 1 320px", maxWidth: 440 }}>
          <label htmlFor={searchInputId} style={{ display: "none" }}>
            Search invoices
          </label>
          <input
            id={searchInputId}
            type="search"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by invoice # or corporate entity..."
            style={{
              width: "100%",
              padding: "10px 14px",
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: tokens["typography.size.200"],
              background: tokens["color.surface.canvas"],
              color: tokens["color.text.primary"],
              boxSizing: "border-box",
            }}
          />
        </div>

        {/* State Filter Tabs */}
        <div
          role="radiogroup"
          aria-label="Filter by invoice status"
          style={{ display: "flex", flexWrap: "wrap", gap: 8 }}
        >
          {[
            { key: "all", label: t.invoicesFilterAll },
            { key: "issued", label: t.invoicesFilterIssued },
            { key: "paid", label: t.invoicesFilterPaid },
            { key: "draft", label: t.invoicesFilterDraft },
          ].map((f) => {
            const isSelected = stateFilter === f.key;
            return (
              <button
                key={f.key}
                type="button"
                role="radio"
                aria-checked={isSelected}
                onClick={() => setStateFilter(f.key)}
                style={{
                  padding: "6px 14px",
                  fontSize: tokens["typography.size.200"],
                  fontWeight: isSelected
                    ? Number(tokens["typography.weight.semibold"])
                    : Number(tokens["typography.weight.medium"]),
                  color: isSelected ? tokens["color.text.inverse"] : tokens["color.text.secondary"],
                  background: isSelected ? tokens["color.primary.base"] : tokens["color.surface.primary"],
                  border: `1px solid ${isSelected ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
                  borderRadius: tokens["dimension.border.radius-sm"],
                  cursor: "pointer",
                }}
              >
                {f.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Invoices Table */}
      <div
        style={{
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-md"],
          overflow: "hidden",
          background: tokens["color.surface.primary"],
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <caption style={{ display: "none" }}>{t.invoicesTitle}</caption>
          <thead>
            <tr style={{ background: tokens["color.surface.secondary"] }}>
              <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colInvoiceNo}
              </th>
              <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colCustomer}
              </th>
              <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colDate}
              </th>
              <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colState}
              </th>
              <th scope="col" style={{ textAlign: "right", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colGross}
              </th>
              <th scope="col" style={{ textAlign: "right", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colVat}
              </th>
              <th scope="col" style={{ textAlign: "right", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colNet}
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredInvoices.map((inv) => {
              const pill = statePills[inv.state] || statePills.draft;
              return (
                <tr key={inv.id} style={{ borderBottom: `1px solid ${tokens["color.border.default"]}` }}>
                  <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"], fontWeight: 600 }}>
                    {inv.invoice_no}
                  </td>
                  <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>
                    {inv.customer}
                  </td>
                  <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {inv.invoice_date}
                  </td>
                  <td style={{ padding: "12px 16px" }}>
                    <span
                      style={{
                        display: "inline-block",
                        padding: "3px 10px",
                        borderRadius: tokens["dimension.border.radius-pill"],
                        fontSize: tokens["typography.size.100"],
                        fontWeight: 600,
                        textTransform: "uppercase",
                        letterSpacing: "0.04em",
                        background: pill.bg,
                        color: pill.fg,
                      }}
                    >
                      {inv.state}
                    </span>
                  </td>
                  <td style={{ padding: "12px 16px", textAlign: "right", fontVariantNumeric: "tabular-nums", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>
                    {inv.gross_bdt}
                  </td>
                  <td style={{ padding: "12px 16px", textAlign: "right", fontVariantNumeric: "tabular-nums", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {inv.vat_bdt}
                  </td>
                  <td style={{ padding: "12px 16px", textAlign: "right", fontVariantNumeric: "tabular-nums", fontSize: tokens["typography.size.200"], fontWeight: 600, color: tokens["color.text.primary"] }}>
                    {inv.net_bdt}
                  </td>
                </tr>
              );
            })}
            {filteredInvoices.length === 0 && !loading && (
              <tr>
                <td colSpan={7} style={{ padding: 32, textAlign: "center", color: tokens["color.text.secondary"] }}>
                  {authError ? t.unauthenticatedNotice : t.invoicesEmpty}
                </td>
              </tr>
            )}
            {loading && (
              <tr>
                <td colSpan={7} style={{ padding: 32, textAlign: "center", color: tokens["color.text.secondary"] }}>
                  {t.loading}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </main>
  );
}
