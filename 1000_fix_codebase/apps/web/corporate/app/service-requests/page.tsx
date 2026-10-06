"use client";

/* Service Requests at Scale (PP3-M02-T02) — create + track.
 *
 * The create form posts to the API which validates server-side (AS-09:
 * the portal is a shell; the model gates the rules). The list renders
 * from the API — zero local data.
 */
import { useEffect, useState } from "react";
import { tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface ServiceOrder {
  id: number;
  name: string;
  state: string;
  customer: string;
  device: string;
  opened_at: string;
}

export default function ServiceRequestsPage() {
  const [orders, setOrders] = useState<ServiceOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formCategory, setFormCategory] = useState("standard");
  const [formDescription, setFormDescription] = useState("");

  const load = () => {
    callOdoo<{ orders: ServiceOrder[] }>("/corporate/service-requests")
      .then((data) => {
        setOrders(data.orders || []);
        setLoading(false);
      })
      .catch((e: Error) => {
        setError(e.message);
        setLoading(false);
      });
  };

  useEffect(load, []);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await callOdoo("/corporate/service-requests", {
        order_category: formCategory,
        description: formDescription,
        customer_id: 1, // The corporate customer — the OIDC token carries the real ID
      });
      setFormDescription("");
      setShowForm(false);
      load();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  if (loading) {
    return <main style={{ padding: 48, color: tokens["color.text.secondary"] }}>Loading requests…</main>;
  }

  return (
    <main style={{ padding: 32 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 24 }}>
        <h1 style={{
          margin: 0,
          fontSize: tokens["typography.size.500"],
          color: tokens["color.text.primary"],
          flex: 1,
        }}>Service Requests</h1>
        <button
          onClick={() => setShowForm(!showForm)}
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
          {showForm ? "Cancel" : "+ New Request"}
        </button>
      </div>

      {error && (
        <div style={{
          padding: 12, marginBottom: 16,
          background: tokens["color.status.error-bg"],
          color: tokens["color.status.error"],
          borderRadius: tokens["dimension.border.radius-sm"],
          fontSize: tokens["typography.size.200"],
        }}>{error}</div>
      )}

      {showForm && (
        <form onSubmit={submit} style={{
          padding: 16, marginBottom: 24,
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-md"],
          background: tokens["color.surface.primary"],
        }}>
          <div style={{ marginBottom: 12 }}>
            <label style={{
              display: "block", marginBottom: 4,
              fontSize: tokens["typography.size.200"],
              color: tokens["color.text.secondary"],
            }}>Category</label>
            <select value={formCategory} onChange={(e) => setFormCategory(e.target.value)}
              style={{
                padding: "8px 12px",
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-sm"],
                fontSize: tokens["typography.size.200"],
                width: "100%",
              }}>
              <option value="standard">Standard</option>
              <option value="warranty">Warranty</option>
              <option value="amc">AMC</option>
            </select>
          </div>
          <div style={{ marginBottom: 12 }}>
            <label style={{
              display: "block", marginBottom: 4,
              fontSize: tokens["typography.size.200"],
              color: tokens["color.text.secondary"],
            }}>Description</label>
            <textarea value={formDescription}
              onChange={(e) => setFormDescription(e.target.value)}
              rows={3}
              style={{
                padding: "8px 12px",
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-sm"],
                fontSize: tokens["typography.size.200"],
                width: "100%",
                resize: "vertical",
              }}
              placeholder="Describe the issue…"
            />
          </div>
          <button type="submit" style={{
            padding: "8px 24px",
            background: tokens["color.primary.base"],
            color: tokens["color.text.inverse"],
            border: "none",
            borderRadius: tokens["dimension.border.radius-sm"],
            fontSize: tokens["typography.size.200"],
            cursor: "pointer",
          }}>Submit Request</button>
        </form>
      )}

      <div style={{
        border: `1px solid ${tokens["color.border.default"]}`,
        borderRadius: tokens["dimension.border.radius-md"],
        overflow: "hidden",
      }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ background: tokens["color.surface.secondary"] }}>
              {["Order", "Customer", "Device", "State", "Opened"].map((h) => (
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
            {orders.map((o) => (
              <tr key={o.id} style={{ borderBottom: `1px solid ${tokens["color.border.default"]}` }}>
                <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>{o.name}</td>
                <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>{o.customer}</td>
                <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>{o.device}</td>
                <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>{o.state}</td>
                <td style={{ padding: "8px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>{o.opened_at.slice(0, 10)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
