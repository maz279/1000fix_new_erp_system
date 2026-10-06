"use client";

/* P01 live tracking — pick an order, watch state/technician/SLA.
 * Polling fallback today (15 s); the websocket upgrade rides the same
 * payload shape (backend note in /customer/tracking). */
import { useCallback, useEffect, useState } from "react";
import { tokens, SectionHead, Pill, Stat, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface Booking { id: number; ref: string; state: string; device: string }
interface Tracking {
  id: number; ref: string; state: string; technician: string;
  eta_resolution: string; sla_paused: boolean;
}

const inputStyle: React.CSSProperties = {
  padding: 10,
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
};

export default function TrackingPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [orderId, setOrderId] = useState<number | null>(null);
  const [tracking, setTracking] = useState<Tracking | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ bookings: Booking[] }>("/customer/bookings")
      .then((d) => setBookings(d.bookings || []))
      .catch((e: Error) => setError(e.message));
  }, []);

  const refresh = useCallback(async (id: number) => {
    try {
      const d = await callOdoo<{ tracking?: Tracking; error?: { message: string } }>(
        "/customer/tracking", { order_id: id });
      if (d.error) setError(d.error.message);
      else setTracking(d.tracking || null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  // polling fallback: every 15 s while an order is selected
  useEffect(() => {
    if (orderId == null) return;
    refresh(orderId);
    const t = setInterval(() => refresh(orderId), 15000);
    return () => clearInterval(t);
  }, [orderId, refresh]);

  if (error && bookings.length === 0) return <LoadError what="ট্র্যাকিং" message={error} />;

  return (
    <main style={{ padding: 32, maxWidth: 720 }}>
      <SectionHead title="লাইভ ট্র্যাকিং" note="অবস্থা প্রতি ১৫ সেকেন্ডে সদ্য হয় (পোলিং)" />
      <select value={orderId ?? ""} onChange={(e) => setOrderId(Number(e.target.value))}
        style={inputStyle} aria-label="অর্ডার নির্বাচন">
        <option value="">— অর্ডার নির্বাচন করুন —</option>
        {bookings.map((b) => (
          <option key={b.id} value={b.id}>{b.ref} — {b.device}</option>
        ))}
      </select>

      {orderId != null && !tracking && !error && <Loading label="ট্র্যাক আনা হচ্ছে…" />}

      {tracking && (
        <div style={{ marginTop: 24 }}>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <Stat label="রেফারেন্স" value={tracking.ref} />
            <Stat label="অবস্থা" value={<Pill state={tracking.state} />} />
          </div>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginTop: 12 }}>
            <Stat label="টেকনিশিয়ান" value={tracking.technician || "নির্ধারিত নয়"} />
            <Stat label="সমাধানের সম্ভাব্য সময়" value={tracking.eta_resolution || "—"} />
            <Stat label="SLA ঘড়ি" value={tracking.sla_paused ? "বিরত" : "চলমান"} />
          </div>
        </div>
      )}

      {error && (
        <p role="alert" style={{
          marginTop: 16, padding: "10px 14px",
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.status.error-bg"],
          color: tokens["color.status.error"],
          fontSize: tokens["typography.size.200"],
        }}>{error}</p>
      )}
    </main>
  );
}
