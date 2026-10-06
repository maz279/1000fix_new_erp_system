"use client";

/* Estate screen (PP3-M01-T02) — the corporate asset estate.
 *
 * Renders from the API through the corporate api wrapper (P-11: no raw
 * fetch, no direct Odoo access). Status badges are token-driven (A4).
 * Zero local data — every row comes from /corporate/estate.
 */
import { useEffect, useState } from "react";
import { tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

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
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // The api wrapper routes through the gateway; no raw fetch here.
    callOdoo<{ devices: Device[] }>("/corporate/estate")
      .then((data) => {
        setDevices(data.devices || []);
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <main style={{ padding: 48, color: tokens["color.text.secondary"] }}>
        Loading estate…
      </main>
    );
  }
  if (error) {
    return (
      <main style={{ padding: 48, color: tokens["color.status.error"] }}>
        Failed to load estate: {error}
      </main>
    );
  }

  return (
    <main style={{ padding: 32 }}>
      <h1 style={{
        margin: "0 0 8px",
        fontSize: tokens["typography.size.500"],
        color: tokens["color.text.primary"],
      }}>
        Corporate Estate
      </h1>
      <p style={{
        margin: "0 0 24px",
        color: tokens["color.text.secondary"],
        fontSize: tokens["typography.size.200"],
      }}>
        {devices.length} devices across the corporate estate
      </p>

      <div style={{
        border: `1px solid ${tokens["color.border.default"]}`,
        borderRadius: tokens["dimension.border.radius-md"],
        overflow: "hidden",
      }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: tokens["color.surface.secondary"] }}>
              {["Brand", "Model", "Identifier", "Warranty", "End Date"].map((h) => (
                <th key={h} style={{
                  textAlign: "left",
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
            {devices.map((d) => {
              const pill = pillColors[d.warranty_status] || pillColors.voided;
              return (
                <tr key={d.id} style={{
                  borderBottom: `1px solid ${tokens["color.border.default"]}`,
                }}>
                  <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>{d.brand}</td>
                  <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>{d.model}</td>
                  <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>{d.identifier}</td>
                  <td style={{ padding: "8px 16px" }}>
                    <span style={{
                      display: "inline-block",
                      padding: "2px 8px",
                      borderRadius: tokens["dimension.border.radius-pill"],
                      fontSize: tokens["typography.size.100"],
                      fontWeight: Number(tokens["typography.weight.medium"]),
                      textTransform: "uppercase",
                      letterSpacing: "0.04em",
                      background: pill.bg,
                      color: pill.fg,
                    }}>{d.warranty_status}</span>
                  </td>
                  <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {d.warranty_end || "—"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </main>
  );
}
