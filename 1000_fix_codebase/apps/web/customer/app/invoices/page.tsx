"use client";

/**
 * P01 invoices & payments — the customer's own issued invoices.
 *
 * Scope: /customer/invoices is partner-scoped in Odoo (EA-05) and returns
 * only issued/paid/credited documents; internal drafts never reach the
 * portal. Every amount is a backend-
 * formatted BN-007 string (AS-09/AS-10) — this page renders, never calculates.
 */
import { useEffect, useMemo, useState } from "react";
import { SectionHead, Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { useAuth } from "../../components/auth-modal";
import { RequireAuth } from "../../components/require-auth";

interface Invoice {
  id: number;
  invoice_no: string;
  invoice_date: string;
  state: string;
  total_bdt: string;
  paid_bdt: string;
  balance_bdt: string;
}

function stateLabel(state: string, bn: boolean): string {
  switch (state) {
    case "issued":
      return bn ? "ইস্যু করা" : "Issued";
    case "paid":
      return bn ? "পরিশোধিত" : "Paid";
    case "credited":
      return bn ? "ক্রেডিট" : "Credited";
    default:
      return state;
  }
}

function stateClass(state: string): string {
  switch (state) {
    case "paid":
      return "st ok";
    case "issued":
      return "st warn";
    case "credited":
      return "st info";
    default:
      return "st neutral";
  }
}

function InvoicesContent() {
  const { locale } = useLanguage();
  const { user, backendReachable } = useAuth();
  const bn = locale === "bn";
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    callOdoo<{ invoices: Invoice[] }>("/customer/invoices")
      .then((d) => {
        if (!active) return;
        setInvoices(d.invoices || []);
        setError(null);
        setLoading(false);
      })
      .catch((e: Error) => {
        if (!active) return;
        setError(e.message);
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [user]);

  const totals = useMemo(() => {
    // The backend sends formatted strings; the page must not re-compute money.
    // Sum the numeric "paid" indicator from the row state instead.
    const paidCount = invoices.filter((i) => i.state === "paid").length;
    return { count: invoices.length, paidCount };
  }, [invoices]);

  if (loading) return <Loading label={bn ? "ইনভয়েস লোড হচ্ছে…" : "Loading invoices…"} />;
  if (error && backendReachable === false) {
    return (
      <LoadError
        what={bn ? "ব্যাকএন্ড সংযোগ" : "Backend connection"}
        message={bn ? "সার্ভিস ব্যাকএন্ডে পৌঁছানো যাচ্ছে না।" : "The service backend is unreachable."}
      />
    );
  }
  if (error) return <LoadError what={bn ? "ইনভয়েস" : "Invoices"} message={error} />;

  return (
    <main>
      <SectionHead
        title={bn ? "ইনভয়েস ও পেমেন্ট" : "Invoices & payments"}
        note={
          bn
            ? `${totals.count}টি ইনভয়েস · ${totals.paidCount}টি পরিশোধিত`
            : `${totals.count} invoice${totals.count === 1 ? "" : "s"} · ${totals.paidCount} paid`
        }
      />

      {invoices.length === 0 ? (
        <div className="fx-card" style={{ marginTop: 18 }}>
          <p className="muted" style={{ margin: 0 }}>
            {bn
              ? "এখনও কোনো ইস্যু করা ইনভয়েস নেই। মেরামত সম্পন্ন হলে ইনভয়েস এখানে দেখা যাবে।"
              : "No issued invoices yet. Once a job is billed, its invoice appears here."}
          </p>
        </div>
      ) : (
        <div className="fx-card" style={{ padding: 0, overflow: "auto", marginTop: 18 }}>
          <table className="fx-table">
            <thead>
              <tr>
                <th>{bn ? "ইনভয়েস নং" : "Invoice no."}</th>
                <th>{bn ? "তারিখ" : "Date"}</th>
                <th style={{ textAlign: "right" }}>{bn ? "মোট" : "Total"}</th>
                <th style={{ textAlign: "right" }}>{bn ? "পরিশোধিত" : "Paid"}</th>
                <th style={{ textAlign: "right" }}>{bn ? "বাকি" : "Balance"}</th>
                <th>{bn ? "অবস্থা" : "Status"}</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((inv) => (
                <tr key={inv.id}>
                  <td><span className="id-chip">{inv.invoice_no}</span></td>
                  <td>{inv.invoice_date}</td>
                  <td style={{ textAlign: "right" }} className="mono">৳ {inv.total_bdt}</td>
                  <td style={{ textAlign: "right" }} className="mono">৳ {inv.paid_bdt}</td>
                  <td style={{ textAlign: "right", fontWeight: 600 }} className="mono">৳ {inv.balance_bdt}</td>
                  <td><span className={stateClass(inv.state)}>{stateLabel(inv.state, bn)}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="fx-card" style={{ marginTop: 16 }}>
        <h3>{bn ? "পেমেন্ট কীভাবে করবেন" : "How to pay"}</h3>
        <p className="muted" style={{ margin: "6px 0 0", fontSize: tokens["typography.size.200"] }}>
          {bn
            ? "যেকোনো 1000 FiX সার্ভিস সেন্টারে নগদ, কার্ড বা মোবাইল ব্যাংকিং (bKash/Nagad) দিয়ে ইনভয়েস পরিশোধ করুন। অনলাইন পেমেন্ট চালু হলে এখানেই দেখা যাবে।"
            : "Pay at any 1000 FiX service centre by cash, card or mobile banking (bKash/Nagad). Online payment will appear here when it is enabled."}
        </p>
        <p className="muted" style={{ margin: "8px 0 0", fontSize: tokens["typography.size.100"] }}>
          {bn ? "প্রশ্ন? হটলাইন ১৬৭৪৩।" : "Questions? Hotline 16743."}
        </p>
      </div>
    </main>
  );
}

export default function InvoicesPage() {
  return (
    <RequireAuth>
      <InvoicesContent />
    </RequireAuth>
  );
}
