"use client";

/* P01 <=3-step booking (Bengali-first, DE-17).
 * Step 1: device — Step 2: fault + category — Step 3: confirm → POST.
 * The model validates server-side (AS-09); rejections render inline
 * (never a silent warn). */
import { useEffect, useState } from "react";
import { tokens, SectionHead, Pill } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface Device {
  id: number;
  brand: string;
  model: string;
  identifier: string;
}

const CATEGORIES = [
  ["standard", "স্ট্যান্ডার্ড সার্ভিস"],
  ["warranty", "ওয়ারেন্টি"],
  ["amc", "AMC চুক্তি"],
] as const;

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
  padding: 10,
  marginTop: 6,
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
};

export default function BookingPage() {
  const [step, setStep] = useState(1);
  const [devices, setDevices] = useState<Device[]>([]);
  const [deviceId, setDeviceId] = useState<number | null>(null);
  const [fault, setFault] = useState("");
  const [category, setCategory] = useState("standard");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<{ ref: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ devices: Device[] }>("/customer/devices")
      .then((d) => setDevices(d.devices || []))
      .catch((e: Error) => setError(e.message));
  }, []);

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      const d = await callOdoo<{ booking?: { ref: string }; error?: { message: string } }>(
        "/customer/bookings", {
          device_id: deviceId,
          fault_description: fault,
          order_category: category,
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
      <main style={{ padding: 32 }}>
        <SectionHead title="বুকিং সম্পন্ন ✅" note={`রেফারেন্স: ${result.ref}`} />
        <p style={{ color: tokens["color.text.secondary"] }}>
          অগ্রগতি দেখতে <a href="/tracking" style={{ color: tokens["color.primary.base"] }}>ট্র্যাকিং</a> পাতায় যান।
        </p>
      </main>
    );
  }

  return (
    <main style={{ padding: 32, maxWidth: 720 }}>
      <SectionHead title="নতুন সার্ভিস বুকিং" note="তিন ধাপে সম্পন্ন — ডিভাইস, সমস্যা, নিশ্চিতকরণ" />
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        {[1, 2, 3].map((n) => (
          <span key={n} style={{
            padding: "2px 10px",
            borderRadius: tokens["dimension.border.radius-pill"],
            fontSize: tokens["typography.size.100"],
            background: n === step
              ? tokens["color.primary.base"]
              : tokens["color.surface.secondary"],
            color: n === step
              ? tokens["color.text.inverse"]
              : tokens["color.text.secondary"],
          }}>ধাপ {n}</span>
        ))}
      </div>

      {step === 1 && (
        <div style={stepStyle}>
          <strong>১ — ডিভাইস নির্বাচন করুন</strong>
          {devices.length === 0 ? (
            <p style={{ color: tokens["color.text.secondary"] }}>
              কোনো নিবন্ধিত ডিভাইস নেই — <a href="/devices" style={{ color: tokens["color.primary.base"] }}>ডিভাইস</a> পাতা দেখুন।
            </p>
          ) : (
            <div style={{ display: "grid", gap: 8, marginTop: 12 }}>
              {devices.map((d) => (
                <button key={d.id} onClick={() => { setDeviceId(d.id); setStep(2); }}
                  style={{
                    textAlign: "left", padding: 12, cursor: "pointer",
                    background: tokens["color.surface.canvas"],
                    color: tokens["color.text.primary"],
                    border: `1px solid ${deviceId === d.id ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
                    borderRadius: tokens["dimension.border.radius-sm"],
                  }}>
                  {d.brand} {d.model} <span style={{ color: tokens["color.text.secondary"] }}>({d.identifier})</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {step === 2 && (
        <div style={stepStyle}>
          <strong>২ — সমস্যার বিবরণ</strong>
          <label style={{ display: "block", marginTop: 12, color: tokens["color.text.secondary"] }}>
            ক্যাটাগরি
            <select value={category} onChange={(e) => setCategory(e.target.value)} style={inputStyle}>
              {CATEGORIES.map(([v, bn]) => <option key={v} value={v}>{bn}</option>)}
            </select>
          </label>
          <label style={{ display: "block", marginTop: 12, color: tokens["color.text.secondary"] }}>
            কী সমস্যা হয়েছে?
            <textarea value={fault} onChange={(e) => setFault(e.target.value)}
              rows={4} style={inputStyle} placeholder="যেমন: ফোন চার্জ হচ্ছে না…" />
          </label>
          <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
            <button onClick={() => setStep(1)} style={{ ...primaryBtn, background: tokens["color.surface.secondary"], color: tokens["color.text.primary"] }}>ফিরে যান</button>
            <button disabled={!fault.trim()} onClick={() => setStep(3)} style={{ ...primaryBtn, opacity: fault.trim() ? 1 : 0.5 }}>পরবর্তী</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div style={stepStyle}>
          <strong>৩ — নিশ্চিত করুন</strong>
          <dl style={{ marginTop: 12, display: "grid", gridTemplateColumns: "auto 1fr", gap: 8, color: tokens["color.text.primary"] }}>
            <dt style={{ color: tokens["color.text.secondary"] }}>ডিভাইস</dt>
            <dd style={{ margin: 0 }}>{devices.find((d) => d.id === deviceId)?.brand} {devices.find((d) => d.id === deviceId)?.model}</dd>
            <dt style={{ color: tokens["color.text.secondary"] }}>ক্যাটাগরি</dt>
            <dd style={{ margin: 0 }}>{CATEGORIES.find(([v]) => v === category)?.[1]}</dd>
            <dt style={{ color: tokens["color.text.secondary"] }}>বিবরণ</dt>
            <dd style={{ margin: 0 }}>{fault}</dd>
          </dl>
          <div style={{ display: "flex", gap: 8, marginTop: 16 }}>
            <button onClick={() => setStep(2)} style={{ ...primaryBtn, background: tokens["color.surface.secondary"], color: tokens["color.text.primary"] }}>ফিরে যান</button>
            <button disabled={busy} onClick={submit} style={primaryBtn}>{busy ? "পাঠানো হচ্ছে…" : "বুকিং নিশ্চিত করুন"}</button>
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
