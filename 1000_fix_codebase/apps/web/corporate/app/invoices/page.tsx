"use client";

/* Consolidated Invoices (PP3-M02-T01) — multi-job B2B invoices.
 *
 * ALL monetary values are backend-computed BN-007-formatted strings —
 * the portal renders, never calculates (AS-10/03 §8). Totals equal
 * the backend's numbers; no client arithmetic.
 */
import { useEffect, useState } from "react";
import { tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

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
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ invoices: Invoice[] }>("/corporate/invoices/consolidated")
      .then((data) => {
        setInvoices(data.invoices || []);
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <main style={{ padding: 48, color: tokens["color.text.secondary"] }}>Loading invoices…</main>;
  }
  if (error) {
    return <main style={{ padding: 48, color: tokens["color.status.error"] }}>Error: {error}</main>;
  }

  return (
    <main style={{ padding: 32 }}>
      <h1 style={{
        margin: "0 0 8px",
        fontSize: tokens["typography.size.500"],
        color: tokens["color.text.primary"],
      }}>Consolidated Invoices</h1>
      <p style={{
        margin: "0 0 24px",
        color: tokens["color.text.secondary"],
        fontSize: tokens["typography.size.200"],
      }}>
        {invoices.length} invoices — totals are backend-computed (AS-10; the portal never calculates money)
      </p>

      <div style={{
        border: `1px solid ${tokens["color.border.default"]}`,
        borderRadius: tokens["dimension.border.radius-md"],
        overflow: "hidden",
      }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: tokens["color.surface.secondary"] }}>
              {["Invoice", "Customer", "Date", "State", "Gross (৳)", "VAT (৳)", "Net (৳)"].map((h) => (
                <th key={h} style={{
                  textAlign: h.includes("(৳)") ? "right" : "left",
                  padding: "8px 16px",
                  fontSize: tokens["typography.size.200"],
                  fontWeight: Number(tokens["typography.weight.medium"]),
                  color: tokens["color.text.secondary"],
                  borderBottom: `1px solid ${tokens["color.border.default"]}`,
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => {
              const pill = statePills[inv.state] || statePills.draft;
              return (
                <tr key={inv.id} style={{
                  borderBottom: `1px solid ${tokens["color.border.default"]}`,
                }}>
                  <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>{inv.invoice_no}</td>
                  <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>{inv.customer}</td>
                  <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>{inv.invoice_date}</td>
                  <td style={{ padding: "8px 16px" }}>
                    <span style={{
                      display: "inline-block",
                      padding: "2px 8px",
                      borderRadius: tokens["dimension.border.radius-pill"],
                      fontSize: tokens["typography.size.100"],
                      fontWeight: Number(tokens["typography.weight.medium"]),
                      textTransform: "uppercase",
                      background: pill.bg,
                      color: pill.fg,
                    }}>{inv.state}</span>
                  </td>
                  {/* Money: backend strings, right-aligned, tabular numbers */}
                  <td style={{ padding: "8px 16px", textAlign: "right", fontVariantNumeric: "tabular-nums", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>{inv.gross_bdt}</td>
                  <td style={{ padding: "8px 16px", textAlign: "right", fontVariantNumeric: "tabular-nums", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>{inv.vat_bdt}</td>
                  <td style={{ padding: "8px 16px", textAlign: "right", fontVariantNumeric: "tabular-nums", fontSize: tokens["typography.size.200"], fontWeight: Number(tokens["typography.weight.medium"]), color: tokens["color.text.primary"] }}>{inv.net_bdt}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </main>
  );
}
