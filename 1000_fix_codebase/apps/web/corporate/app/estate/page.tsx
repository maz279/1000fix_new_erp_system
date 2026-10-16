"use client";

/**
 * Corporate Estate Screen (PP3-M01-T02) — Enterprise Asset Registry.
 * Renders fleet assets from /corporate/estate via Kong gateway.
 * Zero local/mock data (FF-39). Tokens only (CFM-01).
 * Features:
 * - Live search filter (brand, model, serial/IMEI)
 * - Warranty coverage filter pills
 * - Bilingual support (English / বাংলা)
 * - Accessible table markup with proper scope and ARIA attributes
 */
import { useEffect, useState, useId } from "react";
import { tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { useAuth } from "../../components/auth-modal";

interface Device {
  id: number;
  brand: string;
  model: string;
  identifier: string;
  warranty_status: string;
  warranty_end: string | null;
}

const pillColors: Record<string, { bg: string; fg: string }> = {
  active: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  expired: { bg: tokens["color.status.error-bg"], fg: tokens["color.status.error"] },
  pending: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
  voided: { bg: tokens["color.status.neutral-bg"], fg: tokens["color.status.neutral"] },
};

export default function EstatePage() {
  const { t } = useLanguage();
  const { user, openLoginModal } = useAuth();
  const searchInputId = useId();

  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [searchTerm, setSearchTerm] = useState("");
  const [warrantyFilter, setWarrantyFilter] = useState<string>("all");

  const loadEstate = () => {
    setLoading(true);
    setAuthError(false);
    setError(null);

    callOdoo<{ devices: Device[]; total: number }>("/corporate/estate")
      .then((data) => {
        setDevices(data.devices || []);
        setLoading(false);
      })
      .catch((e: Error) => {
        const msg = e.message || "";
        if (msg.includes("Session expired") || msg.includes("Odoo Session Expired")) {
          setAuthError(true);
        } else {
          setError(msg);
        }
        setLoading(false);
      });
  };

  useEffect(() => {
    loadEstate();
  }, [user]);

  // Filtered devices
  const filteredDevices = devices.filter((d) => {
    const matchesSearch =
      d.brand.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
      d.identifier.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesWarranty =
      warrantyFilter === "all" || d.warranty_status.toLowerCase() === warrantyFilter.toLowerCase();
    return matchesSearch && matchesWarranty;
  });

  return (
    <main style={{ padding: "32px 24px", maxWidth: 1280, margin: "0 auto" }}>
      {/* Page Header */}
      <div style={{ marginBottom: 24 }}>
        <h1
          style={{
            margin: "0 0 6px",
            fontSize: tokens["typography.size.500"],
            color: tokens["color.text.primary"],
          }}
        >
          {t.estateTitle}
        </h1>
        <p
          style={{
            margin: 0,
            color: tokens["color.text.secondary"],
            fontSize: tokens["typography.size.200"],
          }}
        >
          {t.estateSubtitle(devices.length)}
        </p>
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

      {/* Search & Filter Controls */}
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
            {t.estateSearchPlaceholder}
          </label>
          <input
            id={searchInputId}
            type="search"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder={t.estateSearchPlaceholder}
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

        {/* Warranty Filter Tabs */}
        <div
          role="radiogroup"
          aria-label="Filter by warranty coverage"
          style={{ display: "flex", flexWrap: "wrap", gap: 8 }}
        >
          {[
            { key: "all", label: t.estateFilterAll },
            { key: "active", label: t.estateFilterActive },
            { key: "expired", label: t.estateFilterExpired },
            { key: "pending", label: t.estateFilterPending },
          ].map((f) => {
            const isSelected = warrantyFilter === f.key;
            return (
              <button
                key={f.key}
                type="button"
                role="radio"
                aria-checked={isSelected}
                onClick={() => setWarrantyFilter(f.key)}
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

      {/* Estate Devices Table */}
      <div
        style={{
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-md"],
          overflow: "hidden",
          background: tokens["color.surface.primary"],
        }}
      >
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <caption style={{ display: "none" }}>{t.estateTitle}</caption>
          <thead>
            <tr style={{ background: tokens["color.surface.secondary"] }}>
              <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colBrand}
              </th>
              <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colModel}
              </th>
              <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colIdentifier}
              </th>
              <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colWarranty}
              </th>
              <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                {t.colEndDate}
              </th>
            </tr>
          </thead>
          <tbody>
            {filteredDevices.map((d) => {
              const pill = pillColors[d.warranty_status] || pillColors.voided;
              return (
                <tr key={d.id} style={{ borderBottom: `1px solid ${tokens["color.border.default"]}` }}>
                  <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"], fontWeight: 600 }}>
                    {d.brand}
                  </td>
                  <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>
                    {d.model}
                  </td>
                  <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"], fontFamily: "monospace" }}>
                    {d.identifier}
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
                      {d.warranty_status}
                    </span>
                  </td>
                  <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {d.warranty_end || "—"}
                  </td>
                </tr>
              );
            })}
            {filteredDevices.length === 0 && !loading && (
              <tr>
                <td colSpan={5} style={{ padding: 32, textAlign: "center", color: tokens["color.text.secondary"] }}>
                  {authError ? t.unauthenticatedNotice : t.estateEmpty}
                </td>
              </tr>
            )}
            {loading && (
              <tr>
                <td colSpan={5} style={{ padding: 32, textAlign: "center", color: tokens["color.text.secondary"] }}>
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
