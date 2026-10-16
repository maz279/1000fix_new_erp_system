"use client";

/**
 * Service Requests at Scale (PP3-M02-T02) — Create + Track.
 * The create form posts to Odoo ERP via Kong gateway.
 * Server-side validation enforced (AS-09).
 * Dynamically loads fleet devices from /corporate/estate for valid device_id selection (M17).
 * Zero local/mock data (FF-39). Tokens only (CFM-01).
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
}

interface ServiceOrder {
  id: number;
  name: string;
  state: string;
  customer: string;
  device: string;
  opened_at: string;
}

export default function ServiceRequestsPage() {
  const { t } = useLanguage();
  const { user, openLoginModal } = useAuth();

  const categoryId = useId();
  const deviceId = useId();
  const descriptionId = useId();

  const [orders, setOrders] = useState<ServiceOrder[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [authError, setAuthError] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [formCategory, setFormCategory] = useState("standard");
  const [selectedDeviceId, setSelectedDeviceId] = useState<number | "">("");
  const [formDescription, setFormDescription] = useState("");

  const loadData = () => {
    setLoading(true);
    setAuthError(false);
    setError(null);

    Promise.all([
      callOdoo<{ orders: ServiceOrder[]; total: number }>("/corporate/service-requests"),
      callOdoo<{ devices: Device[]; total: number }>("/corporate/estate"),
    ])
      .then(([ordersRes, estateRes]) => {
        setOrders(ordersRes.orders || []);
        const devList = estateRes.devices || [];
        setDevices(devList);
        if (devList.length > 0 && selectedDeviceId === "") {
          setSelectedDeviceId(devList[0].id);
        }
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
    loadData();
  }, [user]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDeviceId) {
      setError("Please select a device from the corporate estate.");
      return;
    }
    if (!formDescription.trim()) {
      setError("Please provide a fault description.");
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      // Contract fix: backend requires device_id, fault_description, customer_id, order_category
      const res = await callOdoo<{ id?: number; error?: { message: string } }>("/corporate/service-requests", {
        order_category: formCategory,
        device_id: Number(selectedDeviceId),
        fault_description: formDescription,
        customer_id: user?.partnerId || 1,
      });

      if (res.error) {
        throw new Error(res.error.message || "Failed to create service request");
      }

      setFormDescription("");
      setShowForm(false);
      setSubmitting(false);
      loadData();
    } catch (err) {
      setError((err as Error).message);
      setSubmitting(false);
    }
  };

  return (
    <main style={{ padding: "32px 24px", maxWidth: 1280, margin: "0 auto" }}>
      {/* Header bar */}
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 16,
          marginBottom: 24,
        }}
      >
        <div>
          <h1
            style={{
              margin: "0 0 6px",
              fontSize: tokens["typography.size.500"],
              color: tokens["color.text.primary"],
            }}
          >
            {t.requestsTitle}
          </h1>
          <p
            style={{
              margin: 0,
              color: tokens["color.text.secondary"],
              fontSize: tokens["typography.size.200"],
            }}
          >
            {t.requestsSubtitle(orders.length)}
          </p>
        </div>

        <button
          onClick={() => setShowForm(!showForm)}
          aria-expanded={showForm}
          style={{
            padding: "10px 20px",
            background: showForm ? tokens["color.surface.secondary"] : tokens["color.primary.base"],
            color: showForm ? tokens["color.text.primary"] : tokens["color.text.inverse"],
            border: showForm ? `1px solid ${tokens["color.border.default"]}` : "none",
            borderRadius: tokens["dimension.border.radius-sm"],
            fontSize: tokens["typography.size.200"],
            fontWeight: Number(tokens["typography.weight.semibold"]),
            cursor: "pointer",
          }}
        >
          {showForm ? t.cancelButton : t.newRequestButton}
        </button>
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

      {/* New Request Creation Form */}
      {showForm && (
        <section
          aria-labelledby="new-request-heading"
          style={{
            padding: 24,
            marginBottom: 32,
            border: `1px solid ${tokens["color.border.default"]}`,
            borderRadius: tokens["dimension.border.radius-md"],
            background: tokens["color.surface.primary"],
            boxShadow: tokens["shadow.md"],
          }}
        >
          <h2
            id="new-request-heading"
            style={{
              margin: "0 0 16px",
              fontSize: tokens["typography.size.400"],
              color: tokens["color.text.primary"],
            }}
          >
            {t.newRequestButton}
          </h2>

          <form onSubmit={submit}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16, marginBottom: 16 }}>
              {/* Category */}
              <div>
                <label
                  htmlFor={categoryId}
                  style={{
                    display: "block",
                    marginBottom: 6,
                    fontSize: tokens["typography.size.200"],
                    fontWeight: Number(tokens["typography.weight.medium"]),
                    color: tokens["color.text.primary"],
                  }}
                >
                  {t.formCategory}
                </label>
                <select
                  id={categoryId}
                  value={formCategory}
                  onChange={(e) => setFormCategory(e.target.value)}
                  style={{
                    padding: "10px 12px",
                    border: `1px solid ${tokens["color.border.default"]}`,
                    borderRadius: tokens["dimension.border.radius-sm"],
                    fontSize: tokens["typography.size.200"],
                    background: tokens["color.surface.canvas"],
                    color: tokens["color.text.primary"],
                    width: "100%",
                    boxSizing: "border-box",
                  }}
                >
                  <option value="standard">{t.catStandard}</option>
                  <option value="warranty">{t.catWarranty}</option>
                  <option value="amc">{t.catAmc}</option>
                </select>
              </div>

              {/* Target Fleet Device */}
              <div>
                <label
                  htmlFor={deviceId}
                  style={{
                    display: "block",
                    marginBottom: 6,
                    fontSize: tokens["typography.size.200"],
                    fontWeight: Number(tokens["typography.weight.medium"]),
                    color: tokens["color.text.primary"],
                  }}
                >
                  {t.formDevice}
                </label>
                <select
                  id={deviceId}
                  value={selectedDeviceId}
                  onChange={(e) => setSelectedDeviceId(Number(e.target.value))}
                  required
                  style={{
                    padding: "10px 12px",
                    border: `1px solid ${tokens["color.border.default"]}`,
                    borderRadius: tokens["dimension.border.radius-sm"],
                    fontSize: tokens["typography.size.200"],
                    background: tokens["color.surface.canvas"],
                    color: tokens["color.text.primary"],
                    width: "100%",
                    boxSizing: "border-box",
                  }}
                >
                  {devices.length === 0 && (
                    <option value="">{t.formDeviceSelectPlaceholder}</option>
                  )}
                  {devices.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.brand} {d.model} ({d.identifier}) — [{d.warranty_status}]
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Fault Description */}
            <div style={{ marginBottom: 20 }}>
              <label
                htmlFor={descriptionId}
                style={{
                  display: "block",
                  marginBottom: 6,
                  fontSize: tokens["typography.size.200"],
                  fontWeight: Number(tokens["typography.weight.medium"]),
                  color: tokens["color.text.primary"],
                }}
              >
                {t.formDescription}
              </label>
              <textarea
                id={descriptionId}
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                rows={3}
                required
                placeholder={t.formDescriptionPlaceholder}
                style={{
                  padding: "10px 12px",
                  border: `1px solid ${tokens["color.border.default"]}`,
                  borderRadius: tokens["dimension.border.radius-sm"],
                  fontSize: tokens["typography.size.200"],
                  background: tokens["color.surface.canvas"],
                  color: tokens["color.text.primary"],
                  width: "100%",
                  resize: "vertical",
                  boxSizing: "border-box",
                }}
              />
            </div>

            <div style={{ display: "flex", gap: 12 }}>
              <button
                type="submit"
                disabled={submitting}
                style={{
                  padding: "10px 24px",
                  background: tokens["color.primary.base"],
                  color: tokens["color.text.inverse"],
                  border: "none",
                  borderRadius: tokens["dimension.border.radius-sm"],
                  fontSize: tokens["typography.size.200"],
                  fontWeight: Number(tokens["typography.weight.semibold"]),
                  cursor: submitting ? "wait" : "pointer",
                  opacity: submitting ? 0.7 : 1,
                }}
              >
                {submitting ? t.submitting : t.formSubmit}
              </button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                style={{
                  padding: "10px 20px",
                  background: "transparent",
                  color: tokens["color.text.secondary"],
                  border: `1px solid ${tokens["color.border.default"]}`,
                  borderRadius: tokens["dimension.border.radius-sm"],
                  fontSize: tokens["typography.size.200"],
                  cursor: "pointer",
                }}
              >
                {t.cancelButton}
              </button>
            </div>
          </form>
        </section>
      )}

      {/* Orders Table */}
      <section aria-labelledby="requests-table-heading">
        <h2 id="requests-table-heading" style={{ display: "none" }}>{t.requestsTitle}</h2>
        <div
          style={{
            border: `1px solid ${tokens["color.border.default"]}`,
            borderRadius: tokens["dimension.border.radius-md"],
            overflow: "hidden",
            background: tokens["color.surface.primary"],
          }}
        >
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <caption style={{ display: "none" }}>{t.requestsTitle}</caption>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                  {t.colOrderRef}
                </th>
                <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                  {t.colCustomer}
                </th>
                <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                  {t.colDevice}
                </th>
                <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                  Status
                </th>
                <th scope="col" style={{ textAlign: "left", padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                  {t.colOpenedDate}
                </th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id} style={{ borderBottom: `1px solid ${tokens["color.border.default"]}` }}>
                  <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"], fontWeight: 600 }}>
                    {o.name}
                  </td>
                  <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.primary"] }}>
                    {o.customer}
                  </td>
                  <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {o.device || "—"}
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
                        background: tokens["color.surface.secondary"],
                        color: tokens["color.text.primary"],
                      }}
                    >
                      {o.state}
                    </span>
                  </td>
                  <td style={{ padding: "12px 16px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
                    {o.opened_at.slice(0, 10)}
                  </td>
                </tr>
              ))}
              {orders.length === 0 && !loading && (
                <tr>
                  <td colSpan={5} style={{ padding: 32, textAlign: "center", color: tokens["color.text.secondary"] }}>
                    {authError ? t.unauthenticatedNotice : t.requestsEmpty}
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
      </section>
    </main>
  );
}
