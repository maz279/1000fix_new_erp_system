"use client";

/* P01 home (Bengali-first) — the customer's bookings at a glance.
 * Every row comes from /customer/bookings through the api wrapper (P-11);
 * zero local data (FF-39); money never computed here (AS-09/AS-10). */
import { useEffect, useState } from "react";
import { tokens, Pill, SectionHead, DataTable, Loading, LoadError } from "../lib/imports";
import type { Column } from "../lib/imports";
import { callOdoo } from "../lib/api";

interface Booking {
  id: number;
  ref: string;
  state: string;
  category: string;
  device: string;
  fault: string;
  technician: string;
}

const STATE_BN: Record<string, string> = {
  draft: "খসড়া", sent: "পাঠানো", confirmed: "নিশ্চিত",
  in_progress: "চলমান", done: "সম্পন্ন", delivered: "ডেলিভারি",
  cancelled: "বাতিল", closed: "বন্ধ",
};

export default function CustomerHome() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ bookings: Booking[] }>("/customer/bookings")
      .then((d) => { setBookings(d.bookings || []); setLoading(false); })
      .catch((e: Error) => { setError(e.message); setLoading(false); });
  }, []);

  if (loading) return <Loading label="লোড হচ্ছে…" />;
  if (error) return <LoadError what="বুকিং" message={error} />;

  const columns: Column<Booking>[] = [
    { header: "রেফারেন্স", cell: (b) => b.ref },
    { header: "ডিভাইস", cell: (b) => b.device },
    { header: "সমস্যা", cell: (b) => b.fault },
    { header: "ক্যাটাগরি", cell: (b) => b.category },
    { header: "টেকনিশিয়ান", cell: (b) => b.technician || "—" },
    { header: "অবস্থা", cell: (b) => <Pill state={b.state} label={STATE_BN[b.state] ?? b.state} /> },
  ];

  return (
    <main style={{ padding: 32 }}>
      <SectionHead
        title="আমার সার্ভিস বুকিং"
        note={`${bookings.length}টি অর্ডার — লাইভ অবস্থা সার্ভার থেকে`}
      />
      <DataTable rows={bookings} columns={columns} />
      <p style={{
        marginTop: 24,
        color: tokens["color.text.secondary"],
        fontSize: tokens["typography.size.200"],
      }}>
        নতুন সার্ভিস নিতে <a href="/booking" style={{ color: tokens["color.primary.base"] }}>বুকিং</a> পাতায় যান —
        তিন ধাপে সম্পন্ন।
      </p>
    </main>
  );
}
