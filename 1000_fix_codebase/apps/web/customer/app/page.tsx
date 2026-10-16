"use client";

/* P01 home — the customer's bookings at a glance (Dual Language: Bengali-first + English).
 * Every row comes from /customer/bookings through the api wrapper (P-11);
 * zero local data (FF-39); money never computed here (AS-09/AS-10).
 * Tokens only (CFM-01) — no hand-authored colors. */
import { useEffect, useState } from "react";
import { tokens, Pill, SectionHead, DataTable, Loading, LoadError } from "../lib/imports";
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
  const { user, openLoginModal, loginWithCredentials } = useAuth();
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

  // Friendly authenticated guidance if unauthenticated or session expired
  if (error && (error.toLowerCase().includes("session expired") || !user)) {
    return (
      <main style={{ padding: 32, maxWidth: 680 }}>
        <SectionHead title={t.homeTitle} note={t.sessionExpired} />
        <div
          style={{
            marginTop: 20,
            padding: 24,
            background: tokens["color.surface.primary"],
            border: `1px solid ${tokens["color.border.default"]}`,
            borderRadius: tokens["dimension.border.radius-md"],
          }}
        >
          <p style={{ margin: "0 0 16px", color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"] }}>
            {t.homeSignInPrompt}
          </p>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
            <button
              onClick={openLoginModal}
              style={{
                padding: "10px 20px",
                background: tokens["color.primary.base"],
                color: tokens["color.text.inverse"],
                border: "none",
                borderRadius: tokens["dimension.border.radius-sm"],
                cursor: "pointer",
                fontSize: tokens["typography.size.200"],
                fontWeight: Number(tokens["typography.weight.semibold"]),
              }}
            >
              {t.homeSignInButton}
            </button>
            <button
              onClick={() => loginWithCredentials("admin", "admin")}
              style={{
                padding: "8px 14px",
                background: tokens["color.surface.secondary"],
                color: tokens["color.text.primary"],
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-sm"],
                cursor: "pointer",
                fontSize: tokens["typography.size.100"],
              }}
            >
              {locale === "bn" ? "⚡ এক-ক্লিক ডেমো লগইন" : "⚡ One-Click Demo Sign In"}
            </button>
          </div>
        </div>
      </main>
    );
  }

  if (error) return <LoadError what={t.loadErrorTitle(locale === "bn" ? "বুকিং" : "Bookings")} message={error} />;

  const columns: Column<Booking>[] = [
    { header: t.homeColRef, cell: (b) => b.ref },
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
    <main style={{ padding: 32 }}>
      <SectionHead
        title={t.homeTitle}
        note={t.homeSubtitle(bookings.length)}
      />
      {bookings.length === 0 ? (
        <p style={{ color: tokens["color.text.secondary"], marginTop: 16 }}>{t.homeEmpty}</p>
      ) : (
        <DataTable rows={bookings} columns={columns} />
      )}
      <p style={{
        marginTop: 24,
        color: tokens["color.text.secondary"],
        fontSize: tokens["typography.size.200"],
      }}>
        {t.homeFooterNote}
        <a href="/booking" style={{ color: tokens["color.primary.base"] }}>
          {t.homeFooterLink}
        </a>
        {t.homeFooterEnd}
      </p>
    </main>
  );
}
