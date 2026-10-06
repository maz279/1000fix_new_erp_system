"use client";

/* P01 devices — the customer's registered devices, the M17 history
 * timeline, and ownership transfer (T05: "portal P01 exposes this in
 * Phase 5"). All rows from /customer/devices (P-11). */
import { useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Loading, LoadError } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

interface HistoryEntry { event: string; description: string; date: string }
interface Device {
  id: number;
  brand: string;
  model: string;
  identifier: string;
  warranty_status: string;
  state: string;
  history: HistoryEntry[];
}

const card: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 20,
};
const transferBtn: React.CSSProperties = {
  padding: "6px 14px",
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.secondary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
  fontSize: tokens["typography.size.200"],
};

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [transferFor, setTransferFor] = useState<Device | null>(null);

  async function reload() {
    const d = await callOdoo<{ devices: Device[] }>("/customer/devices");
    setDevices(d.devices || []);
  }

  useEffect(() => {
    reload()
      .then(() => setLoading(false))
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, []);

  async function doTransfer(toPartnerId: number) {
    if (!transferFor) return;
    const d = await callOdoo<{ transferred?: boolean; error?: { message: string } }>(
      "/customer/ownership/transfer", {
        device_id: transferFor.id,
        to_partner_id: toPartnerId,
      });
    setNotice(d.error ? d.error.message : "মালিকানা হস্তান্তর সম্পন্ন");
    setTransferFor(null);
    if (!d.error) reload();
  }

  if (loading) return <Loading label="লোড হচ্ছে…" />;
  if (error) return <LoadError what="ডিভাইস" message={error} />;

  return (
    <main style={{ padding: 32 }}>
      <SectionHead title="আমার ডিভাইস" note={`${devices.length}টি নিবন্ধিত ডিভাইস — M17 রেজিস্ট্রি থেকে`} />
      {notice && (
        <p role="status" style={{
          padding: "10px 14px", marginBottom: 16,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.status.info-bg"],
          color: tokens["color.status.info"],
          fontSize: tokens["typography.size.200"],
        }}>{notice}</p>
      )}
      <div style={{ display: "grid", gap: 16 }}>
        {devices.map((d) => (
          <section key={d.id} style={card}>
            <header style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <strong style={{ fontSize: tokens["typography.size.300"], flex: 1 }}>
                {d.brand} {d.model}
              </strong>
              <Pill state={d.warranty_status} />
              <button style={transferBtn} onClick={() => setTransferFor(d)}>
                মালিকানা হস্তান্তর
              </button>
            </header>
            <p style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
              আইডেন্টিফায়ার: {d.identifier}
            </p>
            <details style={{ marginTop: 8 }}>
              <summary style={{ cursor: "pointer", color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
                সার্ভিস ইতিহাস ({d.history.length})
              </summary>
              <ul style={{ margin: "8px 0 0", paddingLeft: 20, color: tokens["color.text.primary"], fontSize: tokens["typography.size.200"] }}>
                {d.history.map((h, i) => (
                  <li key={i} style={{ marginBottom: 4 }}>
                    <span style={{ color: tokens["color.text.secondary"] }}>{h.date}</span> — {h.description || h.event}
                  </li>
                ))}
                {d.history.length === 0 && <li>কোনো ইতিহাস নেই</li>}
              </ul>
            </details>
          </section>
        ))}
        {devices.length === 0 && (
          <p style={{ color: tokens["color.text.secondary"] }}>কোনো ডিভাইস নিবন্ধিত নেই।</p>
        )}
      </div>

      {transferFor && (
        <div role="dialog" aria-label="মালিকানা হস্তান্তর" style={{
          position: "fixed", inset: 0, display: "grid", placeItems: "center",
          background: "rgba(0,0,0,0.4)",
        }}>
          <div style={{ ...card, maxWidth: 420, margin: 16 }}>
            <strong>মালিকানা হস্তান্তর — {transferFor.brand} {transferFor.model}</strong>
            <p style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
              নতুন মালিকের পার্টনার আইডি দিন (হস্তান্তর রেকর্ড স্থায়ীভাবে সংরক্ষিত হয়)।
            </p>
            <form onSubmit={(e) => {
              e.preventDefault();
              const data = new FormData(e.currentTarget);
              doTransfer(Number(data.get("to")));
            }}>
              <input name="to" type="number" required placeholder="নতুন মালিকের আইডি" style={{
                width: "100%", padding: 10,
                background: tokens["color.surface.canvas"],
                color: tokens["color.text.primary"],
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-sm"],
              }} />
              <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
                <button type="button" style={transferBtn} onClick={() => setTransferFor(null)}>বাতিল</button>
                <button type="submit" style={{
                  ...transferBtn,
                  background: tokens["color.primary.base"],
                  color: tokens["color.text.inverse"],
                  border: "none",
                }}>হস্তান্তর নিশ্চিত করুন</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}
