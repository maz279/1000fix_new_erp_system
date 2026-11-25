"use client";

/* P01 live tracking — 5-stage milestone stepper, deep-linking, technician ETA & SLA clocks (Dual Language).
 * Polling fallback (15 s); rides the live Odoo 5-stage milestone payload.
 * Tokens only (CFM-01) — no hand-authored colors. */
import { Suspense, useCallback, useEffect, useState, useId } from "react";
import { useSearchParams } from "next/navigation";
import { tokens, SectionHead, Pill, Stat, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage, Translations } from "../../components/language";
import { useAuth } from "../../components/auth-modal";

interface Booking { id: number; ref: string; legacy_reference?: string | null; state: string; device: string }

interface StageItem {
  id: string;
  label_en: string;
  label_bn: string;
  completed: boolean;
}

interface Tracking {
  id: number;
  ref: string;
  legacy_reference?: string | null;
  state: string;
  current_stage: number;
  stages: StageItem[];
  device: string;
  branch: string;
  service_type: string;
  technician: string;
  eta_resolution: string;
  sla_paused: boolean;
  created_at: string;
}

function getStateLabel(state: string, t: Translations): string {
  switch (state) {
    case "draft": return t.stateDraft;
    case "sent": return t.stateSent;
    case "confirmed": return t.stateConfirmed;
    case "in_progress": return t.stateInProgress;
    case "done": return t.stateDone;
    case "delivered": return t.stateDelivered;
    case "cancelled": return t.stateCancelled;
    case "closed": return t.stateClosed;
    default: return state;
  }
}

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

function TrackingContent() {
  const { t, locale } = useLanguage();
  const { user } = useAuth();
  const searchParams = useSearchParams();
  const queryOrderId = searchParams.get("order_id");
  const queryRef = searchParams.get("ref");
  const queryToken = searchParams.get("token");

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [orderId, setOrderId] = useState<number | null>(queryOrderId ? Number(queryOrderId) : null);
  const [activeRef, setActiveRef] = useState<string | null>(queryRef || null);
  const [manualRef, setManualRef] = useState<string>("");
  const [tracking, setTracking] = useState<Tracking | null>(null);
  const [error, setError] = useState<string | null>(null);

  const selectId = useId();

  const refresh = useCallback(async (id?: number | null, refStr?: string | null) => {
    try {
      if (refStr) {
        const d = await callOdoo<{ tracking?: Tracking; error?: { message: string } }>(
          "/customer/tracking", { ref: refStr, token: queryToken || undefined });
        if (d.error) setError(d.error.message);
        else setTracking(d.tracking || null);
      } else if (id != null) {
        const d = await callOdoo<{ tracking?: Tracking; error?: { message: string } }>(
          "/customer/tracking", { order_id: id });
        if (d.error) setError(d.error.message);
        else setTracking(d.tracking || null);
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }, [queryToken]);

  // Load customer service bookings if user is logged in
  useEffect(() => {
    if (queryRef) {
      setActiveRef(queryRef);
      refresh(null, queryRef);
    }

    // Only attempt to fetch user bookings if authenticated
    if (user) {
      callOdoo<{ bookings: Booking[] }>("/customer/bookings")
        .then((d) => {
          const list = d.bookings || [];
          setBookings(list);
          if (!orderId && !queryRef && list.length > 0) {
            setOrderId(list[0].id);
          }
        })
        .catch(() => {
          // Unauthenticated or guest visitor: non-blocking, manual lookup form remains available
        });
    }
  }, [user, queryRef, refresh, orderId]);

  // Deep-link query parameter synchronization
  useEffect(() => {
    if (queryOrderId) {
      setOrderId(Number(queryOrderId));
      setActiveRef(null);
    } else if (queryRef) {
      setActiveRef(queryRef);
    }
  }, [queryOrderId, queryRef]);

  // Poll every 15 s when order or ref is selected
  useEffect(() => {
    if (activeRef) {
      refresh(null, activeRef);
      const interval = setInterval(() => refresh(null, activeRef), 15000);
      return () => clearInterval(interval);
    }
    if (orderId == null) return;
    refresh(orderId, null);
    const interval = setInterval(() => refresh(orderId, null), 15000);
    return () => clearInterval(interval);
  }, [orderId, activeRef, refresh]);

  if (error && activeRef && !tracking) {
    // Show error banner instead of full page takeover
  }

  const defaultStages: StageItem[] = [
    { id: "intake", label_en: "Intake Received", label_bn: "ইন্ট্যাক গ্রহণ", completed: true },
    { id: "diagnostic", label_en: "Diagnostic", label_bn: "রোগ নির্ণয় ও পরীক্ষা", completed: false },
    { id: "in_repair", label_en: "Bench Repair", label_bn: "বেঞ্চ মেরামত", completed: false },
    { id: "qc", label_en: "Quality Control", label_bn: "কোয়ালিটি কন্ট্রোল (QC)", completed: false },
    { id: "ready", label_en: "Ready / Delivered", label_bn: "ডেলিভারি প্রস্তুত / সম্পন্ন", completed: false },
  ];

  const stagesToRender = tracking?.stages || defaultStages;
  const currentStageIndex = tracking?.current_stage ?? 0;

  return (
    <main style={{ padding: 32, maxWidth: 840 }}>
      <SectionHead title={t.trackingTitle} note={t.trackingSubtitle} />

      {/* Reference Direct Lookup including MIG-03 / FR-SRM-088 Legacy References */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (manualRef.trim()) {
            setError(null);
            setActiveRef(manualRef.trim());
            setOrderId(null);
            refresh(null, manualRef.trim());
          }
        }}
        style={{
          marginTop: 16,
          padding: 16,
          background: tokens["color.surface.primary"],
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-sm"],
        }}
      >
        <label
          htmlFor="legacy-ref-input"
          style={{
            display: "block",
            marginBottom: 6,
            color: tokens["color.text.secondary"],
            fontSize: tokens["typography.size.200"],
            fontWeight: 500,
          }}
        >
          {locale === "bn"
            ? "অর্ডার বা পূর্ববর্তী রেফারেন্স নম্বর অনুসন্ধান (FR-SRM-088)"
            : "Search by Order or Legacy Reference (FR-SRM-088 / MIG-03)"}
        </label>
        <div style={{ display: "flex", gap: 10 }}>
          <input
            id="legacy-ref-input"
            type="text"
            value={manualRef}
            onChange={(e) => setManualRef(e.target.value)}
            placeholder={locale === "bn" ? "যেমন: SO-2026-001 বা STN-2024-88412" : "e.g. SO-2026-001 or STN-2024-88412"}
            style={inputStyle}
            aria-label="Order or legacy reference lookup"
          />
          <button
            type="submit"
            id="legacy-search-submit-btn"
            style={{
              padding: "10px 20px",
              background: tokens["color.primary.base"],
              color: tokens["color.text.inverse"],
              border: "none",
              borderRadius: tokens["dimension.border.radius-sm"],
              fontWeight: 600,
              cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            {locale === "bn" ? "অনুসন্ধান" : "Search"}
          </button>
        </div>
        {error && (
          <div
            id="tracking-lookup-error"
            role="alert"
            style={{
              marginTop: 12,
              padding: "10px 14px",
              background: tokens["color.status.error-bg"],
              color: tokens["color.status.error"],
              border: `1px solid ${tokens["color.status.error-border"]}`,
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: tokens["typography.size.200"],
            }}
          >
            {error}
          </div>
        )}
      </form>

      {/* Order Selector */}
      <div style={{ marginTop: 16 }}>
        <label
          htmlFor={selectId}
          style={{
            display: "block",
            marginBottom: 6,
            color: tokens["color.text.secondary"],
            fontSize: tokens["typography.size.200"],
            fontWeight: 500,
          }}
        >
          {locale === "bn" ? "অথবা আপনার বর্তমান অর্ডার থেকে নির্বাচন করুন" : "Or Select From Your Active Orders"}
        </label>
        <select
          id={selectId}
          value={orderId ?? ""}
          onChange={(e) => {
            setOrderId(e.target.value ? Number(e.target.value) : null);
            setActiveRef(null);
          }}
          style={inputStyle}
          aria-label={locale === "bn" ? "অর্ডার নির্বাচন" : "Order selection"}
        >
          <option value="">{t.trackingSelectPlaceholder}</option>
          {bookings.map((b) => (
            <option key={b.id} value={b.id}>
              {b.ref} {b.legacy_reference ? `[Legacy: ${b.legacy_reference}]` : ""} — {b.device} ({b.state})
            </option>
          ))}
        </select>
      </div>

      {orderId != null && !tracking && !error && (
        <div style={{ marginTop: 20 }}>
          <Loading label={t.trackingLoading} />
        </div>
      )}

      {/* 5-STAGE MILESTONE STEPPER */}
      {tracking && (
        <div style={{ marginTop: 24 }}>
          <div
            style={{
              padding: 24,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20, flexWrap: "wrap", gap: 10 }}>
              <h3 style={{ margin: 0, fontSize: tokens["typography.size.300"], color: tokens["color.primary.base"] }}>
                {t.trackingMilestonesTitle}
              </h3>
              <Pill state={tracking.state} label={getStateLabel(tracking.state, t)} />
            </div>

            {/* Stepper visual bar */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(5, 1fr)",
                position: "relative",
                gap: 8,
                marginTop: 10,
              }}
            >
              {stagesToRender.map((stage, idx) => {
                const isCompleted = idx <= currentStageIndex;
                const isCurrent = idx === currentStageIndex;
                const stageLabel = locale === "bn" ? stage.label_bn : stage.label_en;

                return (
                  <div key={stage.id} style={{ textAlign: "center", position: "relative" }}>
                    {/* Circle badge */}
                    <div
                      style={{
                        width: 36,
                        height: 36,
                        margin: "0 auto",
                        borderRadius: "50%",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        fontSize: tokens["typography.size.200"],
                        fontWeight: 700,
                        background: isCurrent
                          ? tokens["color.primary.base"]
                          : isCompleted
                          ? tokens["color.status.success-bg"]
                          : tokens["color.surface.secondary"],
                        color: isCurrent
                          ? tokens["color.text.inverse"]
                          : isCompleted
                          ? tokens["color.status.success"]
                          : tokens["color.text.secondary"],
                        border: isCurrent
                          ? `2px solid ${tokens["color.primary.base"]}`
                          : isCompleted
                          ? `2px solid ${tokens["color.status.success"]}`
                          : `1px solid ${tokens["color.border.default"]}`,
                        boxShadow: isCurrent ? "0 0 0 4px rgba(10, 126, 122, 0.2)" : "none",
                        transition: "all 0.3s ease",
                      }}
                    >
                      {idx < currentStageIndex ? "✓" : idx + 1}
                    </div>

                    {/* Stage Label */}
                    <div
                      style={{
                        marginTop: 8,
                        fontSize: tokens["typography.size.100"],
                        fontWeight: isCurrent ? 700 : isCompleted ? 600 : 400,
                        color: isCurrent
                          ? tokens["color.primary.base"]
                          : isCompleted
                          ? tokens["color.text.primary"]
                          : tokens["color.text.secondary"],
                        lineHeight: 1.25,
                      }}
                    >
                      {stageLabel}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Progress Track Line */}
            <div
              style={{
                height: 4,
                background: tokens["color.surface.secondary"],
                borderRadius: tokens["dimension.border.radius-pill"],
                marginTop: 16,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  height: "100%",
                  width: `${Math.min(100, ((currentStageIndex + 1) / 5) * 100)}%`,
                  background: tokens["color.primary.base"],
                  transition: "width 0.5s ease",
                }}
              />
            </div>
          </div>

          {/* ORDER & TECHNICIAN STATS CARD */}
          <div
            style={{
              marginTop: 16,
              padding: 20,
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
            }}
          >
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16 }}>
              <Stat label={t.trackingStatRef} value={tracking.ref} />
              {tracking.legacy_reference && (
                <Stat
                  label={locale === "bn" ? "পূর্ববর্তী রেফারেন্স (MIG-03)" : "Legacy Reference (MIG-03)"}
                  value={tracking.legacy_reference}
                />
              )}
              <Stat label={t.trackingDeviceDetails} value={tracking.device || "—"} />
              <Stat label={t.bookingBranchLabel} value={tracking.branch || "—"} />
              <Stat label={t.trackingServiceMode} value={tracking.service_type === "walk_in" ? t.bookingModeWalkIn : tracking.service_type === "collection" ? t.bookingModeCollection : t.bookingModeOnsite} />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginTop: 16, paddingTop: 16, borderTop: `1px solid ${tokens["color.border.default"]}` }}>
              <Stat
                label={t.trackingStatTech}
                value={tracking.technician || t.trackingStatTechUnassigned}
              />
              <Stat
                label={t.trackingEtaDeadline}
                value={tracking.eta_resolution || (locale === "bn" ? "প্রক্রিয়াধীন" : "In Progress")}
              />
              <Stat
                label={t.trackingStatSla}
                value={tracking.sla_paused ? t.trackingSlaPaused : t.trackingSlaRunning}
              />
            </div>
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

export default function TrackingPage() {
  return (
    <Suspense fallback={<main style={{ padding: 32 }}><Loading label="Loading live tracking…" /></main>}>
      <TrackingContent />
    </Suspense>
  );
}
