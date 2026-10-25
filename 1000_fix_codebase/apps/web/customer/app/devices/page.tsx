"use client";

/* P01 devices — registered devices, M17 history timeline, device registration & ownership transfer (Dual Language).
 * All rows from /customer/devices (P-11); writes via /customer/devices (action="register") and /customer/ownership/transfer.
 * Tokens only (CFM-01) — no hand-authored colors. */
import { useEffect, useState, useId } from "react";
import { tokens, Pill, SectionHead, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { useAuth } from "../../components/auth-modal";

interface HistoryEntry { event: string; description: string; date: string }
interface Device {
  id: number;
  brand: string;
  model: string;
  identifier: string;
  serial_number?: string;
  imei_1?: string;
  warranty_status: string;
  state: string;
  history: HistoryEntry[];
}

interface DeviceModel {
  id: number;
  name: string;
  brand: string;
  device_type: string;
}

const card: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 20,
};

const actionBtn: React.CSSProperties = {
  padding: "6px 14px",
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.secondary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
  fontSize: tokens["typography.size.200"],
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

export default function DevicesPage() {
  const { t, locale } = useLanguage();
  const { user, openLoginModal } = useAuth();
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  
  // Ownership Transfer Modal State
  const [transferFor, setTransferFor] = useState<Device | null>(null);
  const transferInputId = useId();

  // Register New Device Modal State
  const [isRegisterOpen, setIsRegisterOpen] = useState(false);
  const [models, setModels] = useState<DeviceModel[]>([]);
  const [selectedModelId, setSelectedModelId] = useState<number | null>(null);
  const [serialNumber, setSerialNumber] = useState("");
  const [imei, setImei] = useState("");
  const [purchaseChannel, setPurchaseChannel] = useState("brand_store");
  const [regBusy, setRegBusy] = useState(false);
  const [regError, setRegError] = useState<string | null>(null);

  const modelSelectId = useId();
  const serialInputId = useId();
  const imeiInputId = useId();
  const channelSelectId = useId();

  async function reload() {
    const d = await callOdoo<{ devices: Device[] }>("/customer/devices");
    setDevices(d.devices || []);
  }

  useEffect(() => {
    reload()
      .then(() => setLoading(false))
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, [user]);

  // Load models catalogue on opening registration modal
  useEffect(() => {
    if (isRegisterOpen && models.length === 0) {
      callOdoo<{ models: DeviceModel[] }>("/customer/models")
        .then((res) => {
          const list = res.models || [];
          setModels(list);
          if (list.length > 0) setSelectedModelId(list[0].id);
        })
        .catch((e: Error) => setRegError(e.message));
    }
  }, [isRegisterOpen, models.length]);

  async function doRegister(e: React.FormEvent) {
    e.preventDefault();
    if (!selectedModelId) return;
    setRegBusy(true);
    setRegError(null);
    try {
      const res = await callOdoo<{ registered?: boolean; error?: { message: string } }>(
        "/customer/devices", {
          action: "register",
          device_model_id: selectedModelId,
          serial_number: serialNumber.trim(),
          imei_1: imei.trim(),
          purchase_channel: purchaseChannel,
        });
      if (res.error) {
        setRegError(res.error.message);
      } else {
        setNotice(t.devicesRegisterSuccess);
        setIsRegisterOpen(false);
        setSerialNumber("");
        setImei("");
        reload();
      }
    } catch (err) {
      setRegError((err as Error).message);
    } finally {
      setRegBusy(false);
    }
  }

  async function doTransfer(toPartnerId: number) {
    if (!transferFor) return;
    const d = await callOdoo<{ transferred?: boolean; error?: { message: string } }>(
      "/customer/ownership/transfer", {
        device_id: transferFor.id,
        to_partner_id: toPartnerId,
      });
    setNotice(d.error ? d.error.message : t.devicesTransferNoticeSuccess);
    setTransferFor(null);
    if (!d.error) reload();
  }

  // Escape key listener for dialog modals
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setTransferFor(null);
        setIsRegisterOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  if (loading) return <Loading label={t.loading} />;
  if (error) return <LoadError what={t.loadErrorTitle(locale === "bn" ? "ডিভাইস" : "Devices")} message={error} />;

  return (
    <main style={{ padding: 32, maxWidth: 900 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: 16 }}>
        <SectionHead
          title={t.devicesTitle}
          note={t.devicesSubtitle(devices.length)}
        />
        <button
          onClick={() => {
            if (!user) openLoginModal();
            else setIsRegisterOpen(true);
          }}
          style={{
            padding: "8px 18px",
            background: tokens["color.primary.base"],
            color: tokens["color.text.inverse"],
            border: "none",
            borderRadius: tokens["dimension.border.radius-sm"],
            cursor: "pointer",
            fontSize: tokens["typography.size.200"],
            fontWeight: Number(tokens["typography.weight.semibold"]),
          }}
        >
          {t.devicesBtnRegister}
        </button>
      </div>

      {notice && (
        <p
          role="status"
          style={{
            padding: "10px 14px",
            marginTop: 16,
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

      {/* Device Cards List */}
      <div style={{ display: "grid", gap: 16, marginTop: 16 }}>
        {devices.map((d) => (
          <section key={d.id} style={card}>
            <header style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
              <strong style={{ fontSize: tokens["typography.size.300"], flex: 1 }}>
                {d.brand} {d.model}
              </strong>
              <Pill state={d.warranty_status} />
              <button style={actionBtn} onClick={() => setTransferFor(d)}>
                {t.devicesBtnTransfer}
              </button>
            </header>
            <div style={{ display: "flex", gap: 16, flexWrap: "wrap", margin: "8px 0" }}>
              <span style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
                {t.devicesIdentifier(d.identifier)}
              </span>
              {d.serial_number && (
                <span style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
                  SN: {d.serial_number}
                </span>
              )}
              {d.imei_1 && (
                <span style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
                  IMEI: {d.imei_1}
                </span>
              )}
            </div>
            <details style={{ marginTop: 8 }}>
              <summary style={{ cursor: "pointer", color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
                {t.devicesHistorySummary(d.history.length)}
              </summary>
              <ul style={{ margin: "8px 0 0", paddingLeft: 20, color: tokens["color.text.primary"], fontSize: tokens["typography.size.200"] }}>
                {d.history.map((h, i) => (
                  <li key={i} style={{ marginBottom: 4 }}>
                    <span style={{ color: tokens["color.text.secondary"] }}>{h.date}</span> — {h.description || h.event}
                  </li>
                ))}
                {d.history.length === 0 && <li>{t.devicesHistoryEmpty}</li>}
              </ul>
            </details>
          </section>
        ))}
        {devices.length === 0 && (
          <div style={{ ...card, textAlign: "center", padding: 32 }}>
            <p style={{ color: tokens["color.text.secondary"], marginBottom: 16 }}>{t.devicesEmpty}</p>
            <button
              onClick={() => {
                if (!user) openLoginModal();
                else setIsRegisterOpen(true);
              }}
              style={{
                padding: "8px 18px",
                background: tokens["color.primary.base"],
                color: tokens["color.text.inverse"],
                border: "none",
                borderRadius: tokens["dimension.border.radius-sm"],
                cursor: "pointer",
                fontSize: tokens["typography.size.200"],
                fontWeight: Number(tokens["typography.weight.medium"]),
              }}
            >
              {t.devicesBtnRegister}
            </button>
          </div>
        )}
      </div>

      {/* REGISTER NEW DEVICE MODAL */}
      {isRegisterOpen && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="register-device-title"
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
            if (e.target === e.currentTarget) setIsRegisterOpen(false);
          }}
        >
          <div style={{ ...card, maxWidth: 500, width: "100%", margin: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
              <h3 id="register-device-title" style={{ margin: 0, fontSize: tokens["typography.size.300"], color: tokens["color.primary.base"] }}>
                {t.devicesRegisterTitle}
              </h3>
              <button
                type="button"
                onClick={() => setIsRegisterOpen(false)}
                aria-label={locale === "bn" ? "বন্ধ করুন" : "Close"}
                style={{ background: "transparent", border: "none", color: tokens["color.text.secondary"], fontSize: tokens["typography.size.400"], cursor: "pointer" }}
              >
                ✕
              </button>
            </div>
            <p style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.100"], margin: "0 0 16px" }}>
              {t.devicesRegisterDesc}
            </p>

            <form onSubmit={doRegister} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              <div>
                <label htmlFor={modelSelectId} style={{ display: "block", marginBottom: 6, fontSize: tokens["typography.size.200"], fontWeight: 500 }}>
                  {t.devicesRegisterModelLabel} *
                </label>
                <select
                  id={modelSelectId}
                  required
                  value={selectedModelId ?? ""}
                  onChange={(e) => setSelectedModelId(Number(e.target.value))}
                  style={inputStyle}
                >
                  <option value="">{locale === "bn" ? "মডেল নির্বাচন করুন…" : "Choose device model…"}</option>
                  {models.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.brand} {m.name} ({m.device_type})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor={serialInputId} style={{ display: "block", marginBottom: 6, fontSize: tokens["typography.size.200"], fontWeight: 500 }}>
                  {t.devicesRegisterSerialLabel}
                </label>
                <input
                  id={serialInputId}
                  type="text"
                  value={serialNumber}
                  onChange={(e) => setSerialNumber(e.target.value)}
                  placeholder="e.g. SN-8849201"
                  style={inputStyle}
                />
              </div>

              <div>
                <label htmlFor={imeiInputId} style={{ display: "block", marginBottom: 6, fontSize: tokens["typography.size.200"], fontWeight: 500 }}>
                  {t.devicesRegisterImeiLabel}
                </label>
                <input
                  id={imeiInputId}
                  type="text"
                  maxLength={15}
                  value={imei}
                  onChange={(e) => setImei(e.target.value)}
                  placeholder="e.g. 864201099210011"
                  style={inputStyle}
                />
                <small style={{ color: tokens["color.text.secondary"], display: "block", marginTop: 4 }}>
                  {locale === "bn" ? "সিরিয়াল বা আইএমইআই এর যেকোনো একটি আবশ্যক।" : "At least Serial Number or IMEI 1 is required."}
                </small>
              </div>

              <div>
                <label htmlFor={channelSelectId} style={{ display: "block", marginBottom: 6, fontSize: tokens["typography.size.200"], fontWeight: 500 }}>
                  {t.devicesRegisterChannelLabel}
                </label>
                <select
                  id={channelSelectId}
                  value={purchaseChannel}
                  onChange={(e) => setPurchaseChannel(e.target.value)}
                  style={inputStyle}
                >
                  <option value="brand_store">{locale === "bn" ? "ব্র্যান্ড শোরুম" : "Brand Store"}</option>
                  <option value="partner">{locale === "bn" ? "অনুমোদিত ডিলার" : "Authorized Partner"}</option>
                  <option value="online">{locale === "bn" ? "অনলাইন ই-কমার্স" : "Online E-Commerce"}</option>
                </select>
              </div>

              {regError && (
                <p role="alert" style={{ margin: 0, padding: "8px 12px", background: tokens["color.status.error-bg"], color: tokens["color.status.error"], borderRadius: tokens["dimension.border.radius-sm"], fontSize: tokens["typography.size.200"] }}>
                  {regError}
                </p>
              )}

              <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 8 }}>
                <button
                  type="button"
                  style={actionBtn}
                  onClick={() => setIsRegisterOpen(false)}
                >
                  {locale === "bn" ? "বাতিল" : "Cancel"}
                </button>
                <button
                  type="submit"
                  disabled={regBusy}
                  style={{
                    ...actionBtn,
                    background: tokens["color.primary.base"],
                    color: tokens["color.text.inverse"],
                    border: "none",
                    fontWeight: 600,
                  }}
                >
                  {regBusy ? (locale === "bn" ? "সংরক্ষণ হচ্ছে…" : "Registering…") : t.devicesRegisterBtnSubmit}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* OWNERSHIP TRANSFER MODAL */}
      {transferFor && (
        <div
          role="dialog"
          aria-modal="true"
          aria-labelledby="transfer-modal-title"
          style={{
            position: "fixed",
            inset: 0,
            display: "grid",
            placeItems: "center",
            background: "rgba(0, 0, 0, 0.4)",
            backdropFilter: "blur(2px)",
            zIndex: 1000,
          }}
          onClick={(e) => {
            if (e.target === e.currentTarget) setTransferFor(null);
          }}
        >
          <div style={{ ...card, maxWidth: 440, margin: 16 }}>
            <h3 id="transfer-modal-title" style={{ margin: "0 0 8px", fontSize: tokens["typography.size.300"] }}>
              {t.devicesTransferTitle(transferFor.brand, transferFor.model)}
            </h3>
            <p style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"], margin: "0 0 12px" }}>
              {t.devicesTransferDesc}
            </p>
            <form onSubmit={(e) => {
              e.preventDefault();
              const data = new FormData(e.currentTarget);
              doTransfer(Number(data.get("to")));
            }}>
              <label
                htmlFor={transferInputId}
                style={{ display: "block", marginBottom: 4, fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}
              >
                {t.devicesTransferPlaceholder}
              </label>
              <input
                id={transferInputId}
                name="to"
                type="number"
                required
                placeholder={t.devicesTransferPlaceholder}
                style={inputStyle}
              />
              <div style={{ display: "flex", gap: 8, marginTop: 16, justifyContent: "flex-end" }}>
                <button type="button" style={actionBtn} onClick={() => setTransferFor(null)}>
                  {t.devicesTransferCancel}
                </button>
                <button
                  type="submit"
                  style={{
                    ...actionBtn,
                    background: tokens["color.primary.base"],
                    color: tokens["color.text.inverse"],
                    border: "none",
                    fontWeight: 600,
                  }}
                >
                  {t.devicesTransferConfirm}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}
