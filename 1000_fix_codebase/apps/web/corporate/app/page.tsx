"use client";

/**
 * P04 Corporate B2B Executive Overview Dashboard.
 * Renders real operational KPIs, quick enterprise actions, and recent activity
 * fetched live from Odoo ERP via the Kong gateway.
 * Zero dummy/mock data (FF-39). Tokens only (CFM-01).
 */
import { useEffect, useState } from "react";
import Link from "next/link";
import { tokens } from "../lib/imports";
import { callOdoo } from "../lib/api";
import { useLanguage } from "../components/language";
import { useAuth } from "../components/auth-modal";

interface Device {
  id: number;
  brand: string;
  model: string;
  identifier: string;
  warranty_status: string;
  warranty_end: string | null;
}

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

interface ServiceOrder {
  id: number;
  name: string;
  state: string;
  customer: string;
  device: string;
  opened_at: string;
}

const pillColors: Record<string, { bg: string; fg: string }> = {
  active: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  expired: { bg: tokens["color.status.error-bg"], fg: tokens["color.status.error"] },
  pending: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
  voided: { bg: tokens["color.status.neutral-bg"], fg: tokens["color.status.neutral"] },
  issued: { bg: tokens["color.status.info-bg"], fg: tokens["color.status.info"] },
  paid: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  draft: { bg: tokens["color.status.neutral-bg"], fg: tokens["color.status.neutral"] },
  credited: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
};

export default function CorporateHomePage() {
  const { t } = useLanguage();
  const { user, openLoginModal } = useAuth();

  const [devices, setDevices] = useState<Device[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [orders, setOrders] = useState<ServiceOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setAuthError(false);
    setErrorMsg(null);

    try {
      const [estateRes, invoicesRes, ordersRes] = await Promise.all([
        callOdoo<{ devices: Device[]; total: number }>("/corporate/estate").catch((err) => {
          throw err;
        }),
        callOdoo<{ invoices: Invoice[]; total: number }>("/corporate/invoices/consolidated").catch((err) => {
          throw err;
        }),
        callOdoo<{ orders: ServiceOrder[]; total: number }>("/corporate/service-requests").catch((err) => {
          throw err;
        }),
      ]);

      setDevices(estateRes.devices || []);
      setInvoices(invoicesRes.invoices || []);
      setOrders(ordersRes.orders || []);
      setLoading(false);
    } catch (err: unknown) {
      const msg = (err as Error).message || "";
      if (
        msg.includes("Session expired") ||
        msg.includes("Odoo Session Expired") ||
        msg.includes("network") ||
        msg.includes("Unexpected token") ||
        msg.includes("is not valid JSON") ||
        msg.includes("<!DOCTYPE") ||
        !user
      ) {
        setAuthError(true);
      } else {
        setErrorMsg(msg);
      }
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [user]);

  const activeWarrantyCount = devices.filter((d) => d.warranty_status === "active").length;

  return (
    <main style={{ padding: "32px 24px", maxWidth: 1280, margin: "0 auto" }}>
      {/* Hero / Executive Header */}
      <section
        aria-labelledby="overview-heading"
        style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "space-between",
          alignItems: "flex-start",
          gap: 16,
          marginBottom: 32,
          paddingBottom: 24,
          borderBottom: `1px solid ${tokens["color.border.default"]}`,
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
            <span
              style={{
                color: tokens["color.primary.base"],
                fontWeight: Number(tokens["typography.weight.bold"]),
                fontSize: tokens["typography.size.200"],
                letterSpacing: "0.08em",
                textTransform: "uppercase",
              }}
            >
              {t.enterpriseBadge}
            </span>
            <span
              style={{
                fontSize: tokens["typography.size.100"],
                background: tokens["color.surface.secondary"],
                color: tokens["color.primary.base"],
                padding: "2px 8px",
                borderRadius: tokens["dimension.border.radius-sm"],
                fontWeight: 600,
              }}
            >
              {t.slaBadge}
            </span>
          </div>
          <h1
            id="overview-heading"
            style={{
              margin: "0 0 8px",
              fontSize: tokens["typography.size.600"],
              lineHeight: tokens["typography.lineHeight.step-600"],
              color: tokens["color.text.primary"],
            }}
          >
            {t.overviewTitle}
          </h1>
          <p
            style={{
              margin: 0,
              maxWidth: "75ch",
              color: tokens["color.text.secondary"],
              fontSize: tokens["typography.size.300"],
              lineHeight: tokens["typography.lineHeight.normal"],
            }}
          >
            {t.overviewSubtitle}
          </p>
        </div>

        <div style={{ display: "flex", gap: 12 }}>
          <Link
            href="/service-requests"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              padding: "10px 18px",
              background: tokens["color.primary.base"],
              color: tokens["color.text.inverse"],
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: tokens["typography.size.200"],
              fontWeight: Number(tokens["typography.weight.semibold"]),
              textDecoration: "none",
            }}
          >
            + {t.actionNewRequest}
          </Link>
          <Link
            href="/estate"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 6,
              padding: "10px 18px",
              background: tokens["color.surface.primary"],
              color: tokens["color.text.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: tokens["typography.size.200"],
              fontWeight: Number(tokens["typography.weight.medium"]),
              textDecoration: "none",
            }}
          >
            🔍 {t.navEstate}
          </Link>
        </div>
      </section>

      {/* Unauthenticated or Session Error Banner */}
      {authError && (
        <section
          role="alert"
          style={{
            padding: 24,
            marginBottom: 32,
            background: tokens["color.surface.primary"],
            border: `1px solid ${tokens["color.primary.base"]}`,
            borderRadius: tokens["dimension.border.radius-md"],
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 16,
            boxShadow: tokens["shadow.md"],
          }}
        >
          <div>
            <h2 style={{ margin: "0 0 6px", color: tokens["color.text.primary"], fontSize: tokens["typography.size.300"] }}>
              🔐 {t.unauthenticatedNotice}
            </h2>
            <p style={{ margin: 0, color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
              Connect with your corporate user or administrator account to stream real fleet records from the Odoo backend.
            </p>
          </div>
          <button
            onClick={openLoginModal}
            style={{
              padding: "10px 20px",
              background: tokens["color.primary.base"],
              color: tokens["color.text.inverse"],
              border: "none",
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: tokens["typography.size.200"],
              fontWeight: Number(tokens["typography.weight.semibold"]),
              cursor: "pointer",
            }}
          >
            {t.unauthenticatedSignInBtn}
          </button>
        </section>
      )}

      {errorMsg && (
        <div
          role="alert"
          style={{
            padding: 16,
            marginBottom: 24,
            background: tokens["color.status.error-bg"],
            color: tokens["color.status.error"],
            border: `1px solid ${tokens["color.status.error"]}`,
            borderRadius: tokens["dimension.border.radius-sm"],
          }}
        >
          {t.errorPrefix} {errorMsg}
        </div>
      )}

      {/* KPI Cards Grid */}
      <section aria-label="Key Performance Indicators" style={{ marginBottom: 32 }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>
          {/* Card 1: Total Fleet */}
          <article
            style={{
              padding: 20,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
            }}
          >
            <div style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"], marginBottom: 6 }}>
              📱 {t.kpiFleetTotal}
            </div>
            <div style={{ fontSize: tokens["typography.size.600"], fontWeight: Number(tokens["typography.weight.bold"]), color: tokens["color.text.primary"] }}>
              {loading ? "…" : devices.length}
            </div>
            <div style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"], marginTop: 4 }}>
              Across corporate branches
            </div>
          </article>

          {/* Card 2: Active Warranties */}
          <article
            style={{
              padding: 20,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
            }}
          >
            <div style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"], marginBottom: 6 }}>
              🛡️ {t.kpiActiveWarranty}
            </div>
            <div style={{ fontSize: tokens["typography.size.600"], fontWeight: Number(tokens["typography.weight.bold"]), color: tokens["color.status.success"] }}>
              {loading ? "…" : activeWarrantyCount}
            </div>
            <div style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"], marginTop: 4 }}>
              OEM & AMC covered assets
            </div>
          </article>

          {/* Card 3: Open Service Requests */}
          <article
            style={{
              padding: 20,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
            }}
          >
            <div style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"], marginBottom: 6 }}>
              ⚙️ {t.kpiOpenOrders}
            </div>
            <div style={{ fontSize: tokens["typography.size.600"], fontWeight: Number(tokens["typography.weight.bold"]), color: tokens["color.primary.base"] }}>
              {loading ? "…" : orders.length}
            </div>
            <div style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"], marginTop: 4 }}>
              Active in repair workflow
            </div>
          </article>

          {/* Card 4: Consolidated Invoices */}
          <article
            style={{
              padding: 20,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
            }}
          >
            <div style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"], marginBottom: 6 }}>
              📄 {t.kpiInvoicesTotal}
            </div>
            <div style={{ fontSize: tokens["typography.size.600"], fontWeight: Number(tokens["typography.weight.bold"]), color: tokens["color.text.primary"] }}>
              {loading ? "…" : invoices.length}
            </div>
            <div style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"], marginTop: 4 }}>
              Tax invoices on file
            </div>
          </article>
        </div>
      </section>

      {/* Quick Enterprise Actions */}
      <section aria-labelledby="quick-actions-heading" style={{ marginBottom: 36 }}>
        <h2
          id="quick-actions-heading"
          style={{
            margin: "0 0 16px",
            fontSize: tokens["typography.size.400"],
            color: tokens["color.text.primary"],
            fontWeight: Number(tokens["typography.weight.semibold"]),
          }}
        >
          {t.quickActionsTitle}
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16 }}>
          <Link
            href="/service-requests"
            style={{
              padding: 20,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              textDecoration: "none",
              color: "inherit",
              display: "block",
            }}
          >
            <div style={{ fontSize: 24, marginBottom: 8 }}>📝</div>
            <h3 style={{ margin: "0 0 6px", fontSize: tokens["typography.size.300"], color: tokens["color.text.primary"] }}>
              {t.actionNewRequest}
            </h3>
            <p style={{ margin: 0, fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"], lineHeight: tokens["typography.lineHeight.normal"] }}>
              {t.actionNewRequestDesc}
            </p>
          </Link>

          <Link
            href="/estate"
            style={{
              padding: 20,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              textDecoration: "none",
              color: "inherit",
              display: "block",
            }}
          >
            <div style={{ fontSize: 24, marginBottom: 8 }}>🏢</div>
            <h3 style={{ margin: "0 0 6px", fontSize: tokens["typography.size.300"], color: tokens["color.text.primary"] }}>
              {t.actionViewEstate}
            </h3>
            <p style={{ margin: 0, fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"], lineHeight: tokens["typography.lineHeight.normal"] }}>
              {t.actionViewEstateDesc}
            </p>
          </Link>

          <Link
            href="/invoices"
            style={{
              padding: 20,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              textDecoration: "none",
              color: "inherit",
              display: "block",
            }}
          >
            <div style={{ fontSize: 24, marginBottom: 8 }}>🧾</div>
            <h3 style={{ margin: "0 0 6px", fontSize: tokens["typography.size.300"], color: tokens["color.text.primary"] }}>
              {t.actionViewInvoices}
            </h3>
            <p style={{ margin: 0, fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"], lineHeight: tokens["typography.lineHeight.normal"] }}>
              {t.actionViewInvoicesDesc}
            </p>
          </Link>

          <div
            style={{
              padding: 20,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
            }}
          >
            <div style={{ fontSize: 24, marginBottom: 8 }}>📞</div>
            <h3 style={{ margin: "0 0 6px", fontSize: tokens["typography.size.300"], color: tokens["color.text.primary"] }}>
              {t.actionSupport}
            </h3>
            <p style={{ margin: 0, fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"], lineHeight: tokens["typography.lineHeight.normal"] }}>
              {t.actionSupportDesc}
            </p>
          </div>
        </div>
      </section>

      {/* Two Column Operational Tables */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(460px, 1fr))", gap: 24 }}>
        {/* Recent Service Requests */}
        <section aria-labelledby="recent-requests-heading">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <h2
              id="recent-requests-heading"
              style={{
                margin: 0,
                fontSize: tokens["typography.size.400"],
                color: tokens["color.text.primary"],
                fontWeight: Number(tokens["typography.weight.semibold"]),
              }}
            >
              {t.recentOrdersTitle}
            </h2>
            <Link
              href="/service-requests"
              style={{
                fontSize: tokens["typography.size.200"],
                color: tokens["color.primary.base"],
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              {t.viewAll}
            </Link>
          </div>

          <div
            style={{
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              overflow: "hidden",
              background: tokens["color.surface.primary"],
            }}
          >
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <caption style={{ display: "none" }}>{t.recentOrdersTitle}</caption>
              <thead>
                <tr style={{ background: tokens["color.surface.secondary"] }}>
                  <th scope="col" style={{ textAlign: "left", padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {t.colOrderRef}
                  </th>
                  <th scope="col" style={{ textAlign: "left", padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {t.colDevice}
                  </th>
                  <th scope="col" style={{ textAlign: "left", padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    Status
                  </th>
                  <th scope="col" style={{ textAlign: "left", padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {t.colOpenedDate}
                  </th>
                </tr>
              </thead>
              <tbody>
                {orders.slice(0, 5).map((o) => (
                  <tr key={o.id} style={{ borderBottom: `1px solid ${tokens["color.border.default"]}` }}>
                    <td style={{ padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"], fontWeight: 600 }}>
                      {o.name}
                    </td>
                    <td style={{ padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                      {o.device || "—"}
                    </td>
                    <td style={{ padding: "10px 16px" }}>
                      <span
                        style={{
                          display: "inline-block",
                          padding: "2px 8px",
                          borderRadius: tokens["dimension.border.radius-pill"],
                          fontSize: tokens["typography.size.100"],
                          fontWeight: 600,
                          textTransform: "uppercase",
                          background: tokens["color.surface.secondary"],
                          color: tokens["color.text.primary"],
                        }}
                      >
                        {o.state}
                      </span>
                    </td>
                    <td style={{ padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                      {o.opened_at.slice(0, 10)}
                    </td>
                  </tr>
                ))}
                {orders.length === 0 && !loading && (
                  <tr>
                    <td colSpan={4} style={{ padding: 24, textAlign: "center", color: tokens["color.text.secondary"] }}>
                      {authError ? t.unauthenticatedNotice : t.requestsEmpty}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Recent Invoices */}
        <section aria-labelledby="recent-invoices-heading">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
            <h2
              id="recent-invoices-heading"
              style={{
                margin: 0,
                fontSize: tokens["typography.size.400"],
                color: tokens["color.text.primary"],
                fontWeight: Number(tokens["typography.weight.semibold"]),
              }}
            >
              {t.recentInvoicesTitle}
            </h2>
            <Link
              href="/invoices"
              style={{
                fontSize: tokens["typography.size.200"],
                color: tokens["color.primary.base"],
                textDecoration: "none",
                fontWeight: 600,
              }}
            >
              {t.viewAll}
            </Link>
          </div>

          <div
            style={{
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              overflow: "hidden",
              background: tokens["color.surface.primary"],
            }}
          >
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <caption style={{ display: "none" }}>{t.recentInvoicesTitle}</caption>
              <thead>
                <tr style={{ background: tokens["color.surface.secondary"] }}>
                  <th scope="col" style={{ textAlign: "left", padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {t.colInvoiceNo}
                  </th>
                  <th scope="col" style={{ textAlign: "left", padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {t.colDate}
                  </th>
                  <th scope="col" style={{ textAlign: "left", padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {t.colState}
                  </th>
                  <th scope="col" style={{ textAlign: "right", padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {t.colNet}
                  </th>
                </tr>
              </thead>
              <tbody>
                {invoices.slice(0, 5).map((inv) => {
                  const pill = pillColors[inv.state] || pillColors.draft;
                  return (
                    <tr key={inv.id} style={{ borderBottom: `1px solid ${tokens["color.border.default"]}` }}>
                      <td style={{ padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"], fontWeight: 600 }}>
                        {inv.invoice_no}
                      </td>
                      <td style={{ padding: "10px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                        {inv.invoice_date}
                      </td>
                      <td style={{ padding: "10px 16px" }}>
                        <span
                          style={{
                            display: "inline-block",
                            padding: "2px 8px",
                            borderRadius: tokens["dimension.border.radius-pill"],
                            fontSize: tokens["typography.size.100"],
                            fontWeight: 600,
                            textTransform: "uppercase",
                            background: pill.bg,
                            color: pill.fg,
                          }}
                        >
                          {inv.state}
                        </span>
                      </td>
                      <td
                        style={{
                          padding: "10px 16px",
                          textAlign: "right",
                          fontSize: tokens["typography.size.200"],
                          fontWeight: 600,
                          color: tokens["color.text.primary"],
                          fontVariantNumeric: "tabular-nums",
                        }}
                      >
                        {inv.net_bdt}
                      </td>
                    </tr>
                  );
                })}
                {invoices.length === 0 && !loading && (
                  <tr>
                    <td colSpan={4} style={{ padding: 24, textAlign: "center", color: tokens["color.text.secondary"] }}>
                      {authError ? t.unauthenticatedNotice : t.invoicesEmpty}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </main>
  );
}
