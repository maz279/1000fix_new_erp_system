"use client";

/* P01 home — the customer's bookings at a glance (Dual Language: Bengali-first + English).
 * Every row comes from /customer/bookings through the api wrapper (P-11);
 * zero local data (FF-39); money never computed here (AS-09/AS-10).
 * Backend-offline is distinguished from signed-out (the old page masked
 * both behind the same "session expired" card). */
import { useEffect, useState } from "react";
import Link from "next/link";
import { Pill, SectionHead, DataTable, Loading, LoadError } from "../lib/imports";
import type { Column } from "../lib/imports";
import { callOdoo } from "../lib/api";
import { useLanguage, Translations } from "../components/language";
import { useAuth } from "../components/auth-modal";

interface Booking {
  id: number;
  ref: string;
  state: string;
  category: string;
  device: string;
  fault: string;
  technician: string;
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

export default function CustomerHome() {
  const { t, locale } = useLanguage();
  const { user, openLoginModal, loginWithCredentials, backendReachable } = useAuth();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    callOdoo<{ bookings: Booking[] }>("/customer/bookings")
      .then((d) => {
        if (!active) return;
        setBookings(d.bookings || []);
        setError(null);
        setLoading(false);
      })
      .catch((e: Error) => {
        if (!active) return;
        setError(e.message);
        setLoading(false);
      });
    return () => { active = false; };
  }, [user]);

  if (loading) return <Loading label={t.loading} />;

  const offline = backendReachable === false;

  if (error && offline) {
    return (
      <LoadError
        what={locale === "bn" ? "ব্যাকএন্ড সংযোগ" : "Backend connection"}
        message={
          locale === "bn"
            ? "Odoo ব্যাকএন্ডে পৌঁছানো যাচ্ছে না (127.0.0.1:8069)। স্ট্যাক চালু আছে কিনা দেখুন।"
            : "Cannot reach the Odoo backend (127.0.0.1:8069). Check that the stack is running."
        }
      />
    );
  }

  // Friendly authenticated guidance if unauthenticated or session expired
  if (error && !user) {
    return (
      <main>
        <SectionHead title={t.homeTitle} note={t.sessionExpired} />
        <div className="fx-card" style={{ marginTop: 20 }}>
          <p className="muted" style={{ margin: "0 0 16px" }}>
            {t.homeSignInPrompt}
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
            <button className="btn btn-primary" onClick={openLoginModal}>
              {t.homeSignInButton}
            </button>
            <button className="btn" onClick={() => loginWithCredentials("admin", "admin")}>
              {locale === "bn" ? "⚡ এক-ক্লিক ডেমো লগইন" : "⚡ One-Click Demo Sign In"}
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (error) return <LoadError what={t.loadErrorTitle(locale === "bn" ? "বুকিং" : "Bookings")} message={error} />;

  const columns: Column<Booking>[] = [
    { header: t.homeColRef, cell: (b) => <span className="id-chip">{b.ref}</span> },
    { header: t.homeColDevice, cell: (b) => b.device },
    { header: t.homeColFault, cell: (b) => b.fault },
    { header: t.homeColCategory, cell: (b) => b.category },
    { header: t.homeColTechnician, cell: (b) => b.technician || "—" },
    {
      header: t.homeColStatus,
      cell: (b) => <Pill state={b.state} label={getStateLabel(b.state, t)} />,
    },
  ];

  return (
    <main>
      <SectionHead
        title={t.homeTitle}
        note={t.homeSubtitle(bookings.length)}
      />
      {bookings.length === 0 ? (
        <p className="muted" style={{ marginTop: 16 }}>{t.homeEmpty}</p>
      ) : (
        <div className="fx-card" style={{ padding: 0, overflow: "hidden" }}>
          <DataTable rows={bookings} columns={columns} />
        </div>
      )}
      <p className="footer-note">
        {t.homeFooterNote}
        <Link href="/booking">{t.homeFooterLink}</Link>
        {t.homeFooterEnd}
      </p>
    </main>
  );
}
