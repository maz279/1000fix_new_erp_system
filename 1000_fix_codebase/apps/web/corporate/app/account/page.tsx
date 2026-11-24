"use client";

/**
 * Account record — the corporate client's own master data: company identity,
 * billing details, account manager, contacts and portal users. Read-only by
 * design; changes are made by the account manager (auditable in the ERP).
 */
import { useEffect, useState } from "react";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { RequireAuth } from "../../components/require-auth";
import { PageHeader, Panel, linkButtonStyle, pageStyle, tdStyle, thStyle } from "../../components/ui";

interface Profile {
  company: {
    id: number;
    name: string;
    bin: string;
    company_registry: string;
    phone: string;
    email: string;
    street: string;
    city: string;
    zip: string;
    country: string;
    payment_terms: string | false;
  };
  account_manager: { name: string; email: string; phone: string } | null;
  contacts: { id: number; name: string; email: string; phone: string; function: string }[];
  users: { id: number; name: string; login: string }[];
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div
      style={{
        padding: "8px 10px",
        background: tokens["color.surface.secondary"],
        borderRadius: tokens["dimension.border.radius-sm"],
      }}
    >
      <div style={{ fontSize: 10, textTransform: "uppercase", letterSpacing: "0.04em", color: tokens["color.text.secondary"] }}>
        {label}
      </div>
      <div style={{ fontSize: 13, color: tokens["color.text.primary"] }}>{children || "—"}</div>
    </div>
  );
}

function AccountContent() {
  const { locale } = useLanguage();
  const bn = locale === "bn";
  const [data, setData] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    callOdoo<Profile>("/corporate/profile")
      .then((d) => {
        if (!active) return;
        setData(d);
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
  }, []);

  if (loading) return <Loading label={bn ? "অ্যাকাউন্ট লোড হচ্ছে…" : "Loading the account record…"} />;
  if (error || !data) return <LoadError what={bn ? "অ্যাকাউন্ট" : "Account"} message={error || "No data"} />;

  const c = data.company;

  return (
    <main style={pageStyle}>
      <PageHeader
        title={bn ? "অ্যাকাউন্ট রেকর্ড" : "Account record"}
        subtitle={
          bn
            ? "আপনার কোম্পানির মাস্টার ডেটা, বিলিং পরিচয়, অ্যাকাউন্ট ম্যানেজার ও যোগাযোগ। পরিবর্তন প্রয়োজন হলে অ্যাকাউন্ট ম্যানেজারের সাথে যোগাযোগ করুন।"
            : "Your company's master data, billing identity, account manager and contacts. Contact your account manager to change any value (changes are audited in the ERP)."
        }
        actions={
          <>
            <a href="tel:16743" style={{ ...linkButtonStyle, textDecoration: "none" }}>☎ 16743</a>
            <a href="mailto:corporate@1000fix.com" style={{ ...linkButtonStyle, textDecoration: "none" }}>
              ✉ corporate@1000fix.com
            </a>
          </>
        }
      />

      <Panel title={bn ? "কোম্পানি" : "Company"}>
        <div style={{ padding: 16, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 10 }}>
          <Field label={bn ? "নাম" : "Legal name"}>{c.name}</Field>
          <Field label="BIN / VAT">{c.bin}</Field>
          <Field label={bn ? "কোম্পানি রেজিস্ট্রি" : "Company registry"}>{c.company_registry}</Field>
          <Field label={bn ? "পেমেন্ট টার্ম" : "Payment terms"}>{c.payment_terms || ""}</Field>
          <Field label={bn ? "ফোন" : "Phone"}>{c.phone}</Field>
          <Field label={bn ? "ইমেইল" : "Email"}>{c.email}</Field>
          <Field label={bn ? "ঠিকানা" : "Address"}>{[c.street, c.city, c.zip, c.country].filter(Boolean).join(", ")}</Field>
          <Field label={bn ? "অ্যাকাউন্ট আইডি" : "Account ID"}>{c.id}</Field>
        </div>
      </Panel>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 16, marginTop: 16 }}>
        <Panel title={bn ? "অ্যাকাউন্ট ম্যানেজার" : "Account manager"}>
          <div style={{ padding: 16, fontSize: 12.5, lineHeight: 1.7 }}>
            {data.account_manager ? (
              <>
                <div style={{ fontWeight: 600, fontSize: 14 }}>{data.account_manager.name}</div>
                {data.account_manager.email && <div>{data.account_manager.email}</div>}
                {data.account_manager.phone && <div>{data.account_manager.phone}</div>}
              </>
            ) : (
              <span style={{ color: tokens["color.text.secondary"] }}>
                {bn
                  ? "এখনও নির্ধারিত হয়নি — ১৬৭৪৩-এ যোগাযোগ করুন।"
                  : "Not assigned yet — contact the enterprise desk on 16743."}
              </span>
            )}
          </div>
        </Panel>

        <Panel title={bn ? "পোর্টাল ব্যবহারকারী" : "Portal users"}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>{bn ? "নাম" : "Name"}</th>
                <th style={thStyle}>{bn ? "লগইন" : "Login"}</th>
              </tr>
            </thead>
            <tbody>
              {data.users.map((u) => (
                <tr key={u.id}>
                  <td style={tdStyle}>{u.name}</td>
                  <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11.5 }}>{u.login}</td>
                </tr>
              ))}
              {data.users.length === 0 && (
                <tr><td colSpan={2} style={{ ...tdStyle, color: tokens["color.text.secondary"] }}>—</td></tr>
              )}
            </tbody>
          </table>
        </Panel>
      </div>

      <div style={{ marginTop: 16 }}>
        <Panel title={bn ? "যোগাযোগ" : "Contacts"}>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: tokens["color.surface.secondary"] }}>
                  <th style={thStyle}>{bn ? "নাম" : "Name"}</th>
                  <th style={thStyle}>{bn ? "পদ" : "Function"}</th>
                  <th style={thStyle}>{bn ? "ইমেইল" : "Email"}</th>
                  <th style={thStyle}>{bn ? "ফোন" : "Phone"}</th>
                </tr>
              </thead>
              <tbody>
                {data.contacts.map((p) => (
                  <tr key={p.id}>
                    <td style={tdStyle}>{p.name}</td>
                    <td style={tdStyle}>{p.function || "—"}</td>
                    <td style={tdStyle}>{p.email || "—"}</td>
                    <td style={tdStyle}>{p.phone || "—"}</td>
                  </tr>
                ))}
                {data.contacts.length === 0 && (
                  <tr>
                    <td colSpan={4} style={{ ...tdStyle, color: tokens["color.text.secondary"] }}>
                      {bn ? "কোনো অতিরিক্ত যোগাযোগ নেই।" : "No additional contacts on the account."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>

      <p style={{ marginTop: 12, fontSize: 11.5, color: tokens["color.text.secondary"] }}>
        {bn
          ? "অ্যাকাউন্ট ডেটা ERP-তে অডিটেড। নাম, ঠিকানা বা যোগাযোগ পরিবর্তনের অনুরোধ আপনার অ্যাকাউন্ট ম্যানেজার বা ১৬৭৪৩-এ করুন।"
          : "Account data is audited in the ERP. Request name, address or contact changes through your account manager or 16743."}
      </p>
    </main>
  );
}

export default function AccountPage() {
  return (
    <RequireAuth>
      <AccountContent />
    </RequireAuth>
  );
}
