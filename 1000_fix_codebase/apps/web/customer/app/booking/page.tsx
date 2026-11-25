"use client";

/* P01 <=3-step booking with appointment slots & service modes (Dual Language: Bengali-first + English).
 * Step 1: Device Selection
 * Step 2: Fault details, Service Mode, Nearest Branch & Appointment Slot (Morning/Afternoon/Evening)
 * Step 3: Review & Confirmation → POST /customer/bookings
 * The model validates server-side (AS-09); rejections render inline (never a silent warn).
 * Tokens only (CFM-01) — no hand-authored colors. */
import { useEffect, useState, useId } from "react";
import { tokens, SectionHead } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { RequireAuth } from "../../components/require-auth";
import { useAuth } from "../../components/auth-modal";

interface Device {
  id: number;
  brand: string;
  model: string;
  identifier: string;
}

interface Branch {
  id: number;
  name: string;
}

interface BookingResponse {
  id: number;
  ref: string;
  state: string;
  service_type: string;
  branch: string;
}

const stepStyle: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 24,
  marginTop: 16,
};

const primaryBtn: React.CSSProperties = {
  padding: "10px 24px",
  background: tokens["color.primary.base"],
  color: tokens["color.text.inverse"],
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
  cursor: "pointer",
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  boxSizing: "border-box",
  padding: 10,
  marginTop: 6,
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
};

function BookingPageContent() {
  const { t, locale } = useLanguage();
  const { user, openLoginModal } = useAuth();
  
  const [step, setStep] = useState(1);
  const [devices, setDevices] = useState<Device[]>([]);
  const [branches, setBranches] = useState<Branch[]>([]);
  const [deviceId, setDeviceId] = useState<number | null>(null);

  // Step 2 Intake & Appointment Slots
  const [serviceType, setServiceType] = useState<"walk_in" | "collection" | "onsite">("walk_in");
  const [branchId, setBranchId] = useState<number | null>(null);
  const [slotDate, setSlotDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split("T")[0];
  });
  const [slot, setSlot] = useState<"morning" | "afternoon" | "evening">("morning");
  const [category, setCategory] = useState("standard");
  const [fault, setFault] = useState("");

  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<BookingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const categorySelectId = useId();
  const faultTextareaId = useId();
  const serviceTypeSelectId = useId();
  const branchSelectId = useId();
  const dateInputId = useId();

  const categories = [
    ["standard", t.bookingCatStandard],
    ["warranty", t.bookingCatWarranty],
    ["amc", t.bookingCatAmc],
  ] as const;

  // Load customer devices
  useEffect(() => {
    callOdoo<{ devices: Device[] }>("/customer/devices")
      .then((d) => {
        const list = d.devices || [];
        setDevices(list);
        if (list.length > 0 && !deviceId) setDeviceId(list[0].id);
      })
      .catch((e: Error) => setError(e.message));
  }, [user]);

  // Load active service branches
  useEffect(() => {
    callOdoo<{ branches: Branch[] }>("/customer/branches")
      .then((d) => {
        const list = d.branches || [];
        setBranches(list);
        if (list.length > 0 && !branchId) setBranchId(list[0].id);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      const d = await callOdoo<{ booking?: BookingResponse; error?: { message: string } }>(
        "/customer/bookings", {
          device_id: deviceId,
          fault_description: fault,
          order_category: category,
          service_type: serviceType,
          branch_id: branchId,
          slot: slot,
          slot_date: slotDate,
        });
      if (d.error) setError(d.error.message);
      else setResult(d.booking || null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (result) {
    return (
      <main style={{ padding: 32, maxWidth: 720 }}>
        <SectionHead title={t.bookingSuccessTitle} note={t.bookingSuccessRef(result.ref)} />
        <div
          style={{
            marginTop: 20,
            padding: 20,
            background: tokens["color.surface.primary"],
            border: `1px solid ${tokens["color.border.default"]}`,
            borderRadius: tokens["dimension.border.radius-md"],
          }}
        >
          <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: 10, fontSize: tokens["typography.size.200"] }}>
            <span style={{ color: tokens["color.text.secondary"] }}>{locale === "bn" ? "অর্ডার আইডি:" : "Order ID:"}</span>
            <strong>{result.ref}</strong>
            <span style={{ color: tokens["color.text.secondary"] }}>{t.bookingServiceTypeLabel}:</span>
            <span>{result.service_type === "walk_in" ? t.bookingModeWalkIn : result.service_type === "collection" ? t.bookingModeCollection : t.bookingModeOnsite}</span>
            <span style={{ color: tokens["color.text.secondary"] }}>{t.bookingBranchLabel}:</span>
            <span>{result.branch}</span>
          </div>

          <div style={{ marginTop: 20, display: "flex", gap: 12 }}>
            <a
              href={`/tracking?order_id=${result.id}&ref=${result.ref}`}
              style={{
                ...primaryBtn,
                textDecoration: "none",
                display: "inline-block",
                textAlign: "center",
              }}
            >
              🚀 {t.bookingSuccessTrackingLink}
            </a>
            <button
              onClick={() => {
                setResult(null);
                setStep(1);
                setFault("");
              }}
              style={{
                ...primaryBtn,
                background: tokens["color.surface.secondary"],
                color: tokens["color.text.primary"],
              }}
            >
              {locale === "bn" ? "আরেকটি বুকিং করুন" : "Book Another"}
            </button>
          </div>
        </div>
      </main>
    );
  }

  const selectedDevice = devices.find((d) => d.id === deviceId);
  const selectedBranch = branches.find((b) => b.id === branchId);

  return (
    <main style={{ padding: 32, maxWidth: 760 }}>
      <SectionHead title={t.bookingTitle} note={t.bookingSubtitle} />

      {/* Stepper Pills */}
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        {[1, 2, 3].map((n) => (
          <span
            key={n}
            style={{
              padding: "4px 12px",
              borderRadius: tokens["dimension.border.radius-pill"],
              fontSize: tokens["typography.size.100"],
              background: n === step
                ? tokens["color.primary.base"]
                : tokens["color.surface.secondary"],
              color: n === step
                ? tokens["color.text.inverse"]
                : tokens["color.text.secondary"],
              fontWeight: 600,
            }}
          >
            {t.bookingStep(n)}
          </span>
        ))}
      </div>

      {/* STEP 1: SELECT DEVICE */}
      {step === 1 && (
        <div style={stepStyle}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 8 }}>
            <strong style={{ fontSize: tokens["typography.size.300"], display: "block" }}>
              {t.bookingStep1Title}
            </strong>
            <a
              href="/devices"
              style={{
                color: tokens["color.primary.base"],
                fontSize: tokens["typography.size.100"],
                textDecoration: "none",
                fontWeight: 500,
              }}
            >
              {t.bookingQuickRegisterDevice}
            </a>
          </div>

          {devices.length === 0 ? (
            <div style={{ marginTop: 12 }}>
              <p style={{ color: tokens["color.text.secondary"], margin: "0 0 12px" }}>
                {t.bookingNoDevices}
                <a href="/devices" style={{ color: tokens["color.primary.base"] }}>
                  {t.bookingViewDevices}
                </a>
              </p>
              {!user && (
                <button
                  type="button"
                  onClick={openLoginModal}
                  style={{
                    padding: "6px 14px",
                    background: tokens["color.primary.base"],
                    color: tokens["color.text.inverse"],
                    border: "none",
                    borderRadius: tokens["dimension.border.radius-sm"],
                    fontSize: tokens["typography.size.200"],
                    cursor: "pointer",
                  }}
                >
                  {t.signIn}
                </button>
              )}
            </div>
          ) : (
            <div style={{ display: "grid", gap: 8, marginTop: 12 }}>
              {devices.map((d) => (
                <button
                  key={d.id}
                  onClick={() => { setDeviceId(d.id); setStep(2); }}
                  style={{
                    textAlign: "left",
                    padding: 14,
                    cursor: "pointer",
                    background: deviceId === d.id ? tokens["color.surface.secondary"] : tokens["color.surface.canvas"],
                    color: tokens["color.text.primary"],
                    border: `2px solid ${deviceId === d.id ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
                    borderRadius: tokens["dimension.border.radius-sm"],
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                >
                  <div>
                    <strong style={{ fontSize: tokens["typography.size.200"] }}>{d.brand} {d.model}</strong>
                    <div style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.100"], marginTop: 2 }}>
                      {d.identifier}
                    </div>
                  </div>
                  <span style={{ fontSize: tokens["typography.size.200"], color: tokens["color.primary.base"] }}>
                    {deviceId === d.id ? "✓" : "→"}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* STEP 2: FAULT DETAILS & APPOINTMENT SLOTS */}
      {step === 2 && (
        <div style={stepStyle}>
          <strong style={{ fontSize: tokens["typography.size.300"], display: "block" }}>
            {t.bookingStep2Title}
          </strong>

          {/* Service Delivery Mode */}
          <div style={{ marginTop: 16 }}>
            <label
              htmlFor={serviceTypeSelectId}
              style={{ display: "block", color: tokens["color.text.primary"], fontSize: tokens["typography.size.200"], fontWeight: 500 }}
            >
              {t.bookingServiceTypeLabel}
            </label>
            <select
              id={serviceTypeSelectId}
              value={serviceType}
              onChange={(e) => setServiceType(e.target.value as "walk_in" | "collection" | "onsite")}
              style={inputStyle}
            >
              <option value="walk_in">{t.bookingModeWalkIn}</option>
              <option value="collection">{t.bookingModeCollection}</option>
              <option value="onsite">{t.bookingModeOnsite}</option>
            </select>
          </div>

          {/* Nearest Branch */}
          <div style={{ marginTop: 14 }}>
            <label
              htmlFor={branchSelectId}
              style={{ display: "block", color: tokens["color.text.primary"], fontSize: tokens["typography.size.200"], fontWeight: 500 }}
            >
              {t.bookingBranchLabel}
            </label>
            <select
              id={branchSelectId}
              value={branchId ?? ""}
              onChange={(e) => setBranchId(Number(e.target.value))}
              style={inputStyle}
            >
              <option value="">{locale === "bn" ? "শাখা নির্বাচন করুন…" : "Select branch…"}</option>
              {branches.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>

          {/* Appointment Date & Slot Selector */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 14 }}>
            <div>
              <label
                htmlFor={dateInputId}
                style={{ display: "block", color: tokens["color.text.primary"], fontSize: tokens["typography.size.200"], fontWeight: 500 }}
              >
                {t.bookingDateLabel}
              </label>
              <input
                id={dateInputId}
                type="date"
                required
                value={slotDate}
                onChange={(e) => setSlotDate(e.target.value)}
                style={inputStyle}
              />
            </div>

            <div>
              <label
                style={{ display: "block", color: tokens["color.text.primary"], fontSize: tokens["typography.size.200"], fontWeight: 500 }}
              >
                {t.bookingSlotLabel}
              </label>
              <div style={{ display: "flex", gap: 6, marginTop: 6 }}>
                {[
                  { id: "morning", label: t.bookingSlotMorning.split("(")[0].trim() },
                  { id: "afternoon", label: t.bookingSlotAfternoon.split("(")[0].trim() },
                  { id: "evening", label: t.bookingSlotEvening.split("(")[0].trim() },
                ].map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => setSlot(s.id as "morning" | "afternoon" | "evening")}
                    style={{
                      flex: 1,
                      padding: "8px 4px",
                      background: slot === s.id ? tokens["color.primary.base"] : tokens["color.surface.canvas"],
                      color: slot === s.id ? tokens["color.text.inverse"] : tokens["color.text.primary"],
                      border: `1px solid ${slot === s.id ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
                      borderRadius: tokens["dimension.border.radius-sm"],
                      fontSize: tokens["typography.size.100"],
                      cursor: "pointer",
                      fontWeight: slot === s.id ? 600 : 400,
                    }}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Category */}
          <div style={{ marginTop: 14 }}>
            <label
              htmlFor={categorySelectId}
              style={{ display: "block", color: tokens["color.text.primary"], fontSize: tokens["typography.size.200"], fontWeight: 500 }}
            >
              {t.bookingCategoryLabel}
            </label>
            <select
              id={categorySelectId}
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              style={inputStyle}
            >
              {categories.map(([v, label]) => (
                <option key={v} value={v}>{label}</option>
              ))}
            </select>
          </div>

          {/* Fault Description */}
          <div style={{ marginTop: 14 }}>
            <label
              htmlFor={faultTextareaId}
              style={{ display: "block", color: tokens["color.text.primary"], fontSize: tokens["typography.size.200"], fontWeight: 500 }}
            >
              {t.bookingFaultLabel} *
            </label>
            <textarea
              id={faultTextareaId}
              value={fault}
              onChange={(e) => setFault(e.target.value)}
              rows={3}
              style={inputStyle}
              placeholder={t.bookingFaultPlaceholder}
            />
          </div>

          <div style={{ display: "flex", gap: 8, marginTop: 20 }}>
            <button
              onClick={() => setStep(1)}
              style={{ ...primaryBtn, background: tokens["color.surface.secondary"], color: tokens["color.text.primary"] }}
            >
              {t.bookingBack}
            </button>
            <button
              disabled={!fault.trim()}
              onClick={() => setStep(3)}
              style={{ ...primaryBtn, opacity: fault.trim() ? 1 : 0.5 }}
            >
              {t.bookingNext}
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: REVIEW & CONFIRM */}
      {step === 3 && (
        <div style={stepStyle}>
          <strong style={{ fontSize: tokens["typography.size.300"], display: "block" }}>
            {t.bookingStep3Title}
          </strong>

          <div
            style={{
              marginTop: 16,
              padding: 16,
              background: tokens["color.surface.secondary"],
              borderRadius: tokens["dimension.border.radius-sm"],
              display: "grid",
              gridTemplateColumns: "180px 1fr",
              gap: 10,
              fontSize: tokens["typography.size.200"],
            }}
          >
            <span style={{ color: tokens["color.text.secondary"] }}>{t.bookingConfirmDevice}</span>
            <strong>{selectedDevice ? `${selectedDevice.brand} ${selectedDevice.model}` : "—"}</strong>

            <span style={{ color: tokens["color.text.secondary"] }}>{t.bookingServiceTypeLabel}</span>
            <strong>{serviceType === "walk_in" ? t.bookingModeWalkIn : serviceType === "collection" ? t.bookingModeCollection : t.bookingModeOnsite}</strong>

            <span style={{ color: tokens["color.text.secondary"] }}>{t.bookingBranchLabel}</span>
            <span>{selectedBranch?.name || "—"}</span>

            <span style={{ color: tokens["color.text.secondary"] }}>{t.bookingDateLabel}</span>
            <span>{slotDate} ({slot === "morning" ? t.bookingSlotMorning : slot === "afternoon" ? t.bookingSlotAfternoon : t.bookingSlotEvening})</span>

            <span style={{ color: tokens["color.text.secondary"] }}>{t.bookingConfirmCategory}</span>
            <span>{categories.find(([v]) => v === category)?.[1]}</span>

            <span style={{ color: tokens["color.text.secondary"] }}>{t.bookingConfirmDescription}</span>
            <span style={{ wordBreak: "break-word" }}>{fault}</span>
          </div>

          <div style={{ display: "flex", gap: 8, marginTop: 20 }}>
            <button
              onClick={() => setStep(2)}
              style={{ ...primaryBtn, background: tokens["color.surface.secondary"], color: tokens["color.text.primary"] }}
            >
              {t.bookingBack}
            </button>
            <button
              disabled={busy}
              onClick={submit}
              style={{ ...primaryBtn, opacity: busy ? 0.7 : 1 }}
            >
              {busy ? t.bookingSubmitting : t.bookingConfirmBtn}
            </button>
          </div>
        </div>
      )}

      {error && (
        <p
          role="alert"
          style={{
            marginTop: 16,
            padding: "10px 14px",
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.status.error-bg"],
            color: tokens["color.status.error"],
            fontSize: tokens["typography.size.200"],
          }}
        >
          {error}
        </p>
      )}
    </main>
  );
}

export default function BookingPage() {
  return (
    <RequireAuth>
      <BookingPageContent />
    </RequireAuth>
  );
}
