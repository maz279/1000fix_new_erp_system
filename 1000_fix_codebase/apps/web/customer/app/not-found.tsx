import Link from "next/link";

export default function NotFound() {
  return (
    <main className="fx-page" style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "60vh", gap: 10 }}>
      <div style={{ fontSize: 40 }} aria-hidden>🔍</div>
      {/* `locale` was referenced but never bound, and this is a server
          component with no language context; the rest of the page is
          already bilingual, so the heading is too. */}
      <h1>পৃষ্ঠা পাওয়া যায়নি / Page not found</h1>
      <p className="muted">এই ঠিকানাটি P01 কাস্টমার পোর্টালে নেই। / This address does not exist in the P01 customer portal.</p>
      <Link className="btn btn-primary" href="/">হোমে ফিরুন / Back to home</Link>
    </main>
  );
}
