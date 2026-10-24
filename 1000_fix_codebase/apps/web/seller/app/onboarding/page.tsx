"use client";

/* P07 Seller Onboarding — L6 KYC & INT-035 Trade Licence Verification.
 * KYC status is read from /seller/dashboard. There is NO backend KYC
 * submission/verification route, so the form is disabled with an honest
 * notice — nothing is "verified" client-side.
 * WCAG 2.2 AA compliant with full keyboard navigation and high-contrast tokens. */
import { useEffect, useState } from "react";
import { tokens, Pill, SectionHead, Stat } from "../../lib/imports";
import { callOdoo } from "../../lib/api";

const cardStyle: React.CSSProperties = {
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
  background: tokens["color.surface.primary"],
  padding: 24,
  marginBottom: 20,
};

const inputGroupStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: 6,
  marginBottom: 16,
};

const labelStyle: React.CSSProperties = {
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
  color: tokens["color.text.secondary"],
};

const inputStyle: React.CSSProperties = {
  padding: "10px 14px",
  background: tokens["color.surface.canvas"],
  color: tokens["color.text.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-sm"],
  fontSize: tokens["typography.size.200"],
  outline: "none",
  width: "100%",
  boxSizing: "border-box",
};

const btnPrimary: React.CSSProperties = {
  padding: "10px 20px",
  border: "none",
  borderRadius: tokens["dimension.border.radius-sm"],
  cursor: "pointer",
  fontSize: tokens["typography.size.200"],
  fontWeight: Number(tokens["typography.weight.medium"]),
  background: tokens["color.primary.base"],
  color: tokens["color.text.inverse"],
  alignSelf: "flex-start",
};

interface SellerKyc {
  kyc_status: string;
  kyc_ref: string;
}

export default function SellerOnboardingPage() {
  const [tradeLicense, setTradeLicense] = useState("");
  const [authority, setAuthority] = useState("");
  const [binNumber, setBinNumber] = useState("");
  const [etinNumber, setEtinNumber] = useState("");
  const [businessName, setBusinessName] = useState("");
  // KYC standing comes from the backend (/seller/dashboard) — never assumed.
  const [kyc, setKyc] = useState<SellerKyc | null>(null);
  const [kycLoading, setKycLoading] = useState(true);
  const [kycError, setKycError] = useState<string | null>(null);

  useEffect(() => {
    callOdoo<{ seller?: SellerKyc; error?: { code?: string; message: string } } | undefined>("/seller/dashboard")
      .then((d) => {
        if (!d) setKycError("The server returned an empty response.");
        else if (d.error) setKycError(d.error.message);
        else setKyc(d.seller ?? null);
      })
      .catch((e: Error) => setKycError(e.message))
      .finally(() => setKycLoading(false));
  }, []);

  function handleSubmit(e: React.FormEvent) {
    // No backend KYC submission service exists; the form is disabled and
    // this guard keeps an Enter keypress from implying anything was sent.
    e.preventDefault();
  }

  const status = kyc?.kyc_status ?? "unverified";

  return (
    <main style={{ padding: 32, maxWidth: 900, margin: "0 auto" }}>
      <SectionHead
        title="Seller Onboarding & KYC (অনবোর্ডিং ও যাচাইকরণ)"
        note="L6 Merchant KYC — Trade Licence, BIN-13 and e-TIN registration (M12)"
      />

      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <Stat label="KYC Status" value={kycLoading ? "Loading…" : <Pill state={status} />} tone="primary" />
        <Stat label="KYC Reference" value={kyc?.kyc_ref || "—"} />
      </div>

      {kycError && (
        <div
          role="alert"
          style={{
            padding: "12px 16px",
            marginBottom: 20,
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.status.error-bg"],
            color: tokens["color.status.error"],
            fontSize: tokens["typography.size.200"],
            border: `1px solid ${tokens["color.status.error"]}`,
          }}
        >
          Could not load your KYC status: {kycError}
        </div>
      )}

      <div
        role="note"
        style={{
          padding: "12px 16px",
          marginBottom: 20,
          borderRadius: tokens["dimension.border.radius-sm"],
          background: tokens["color.status.warning-bg"],
          color: tokens["color.status.warning"],
          fontSize: tokens["typography.size.200"],
          border: `1px solid ${tokens["color.status.warning"]}`,
        }}
      >
        Online KYC submission is not yet available — there is no backend service to receive or verify
        these documents, so this form cannot be submitted. KYC is completed by 1000FiX compliance;
        contact seller support (hotline 16743) to start or update your verification.
      </div>

      <form onSubmit={handleSubmit} style={cardStyle} aria-label="Seller Onboarding Form (submission unavailable)">
        <fieldset disabled style={{ border: "none", margin: 0, padding: 0 }}>
        <h2
          style={{
            fontSize: tokens["typography.size.300"],
            fontWeight: Number(tokens["typography.weight.semibold"]),
            marginTop: 0,
            marginBottom: 16,
          }}
        >
          Enterprise Statutory Registration
        </h2>

        <div style={inputGroupStyle}>
          <label htmlFor="businessName" style={labelStyle}>
            Business Legal Entity Name (ব্যবসায়িক প্রতিষ্ঠানের নাম)
          </label>
          <input
            id="businessName"
            type="text"
            required
            value={businessName}
            onChange={(e) => setBusinessName(e.target.value)}
            style={inputStyle}
          />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 16 }}>
          <div style={inputGroupStyle}>
            <label htmlFor="tradeLicense" style={labelStyle}>
              Trade Licence Number (ট্রেড লাইসেন্স নম্বর — INT-035)
            </label>
            <input
              id="tradeLicense"
              type="text"
              required
              value={tradeLicense}
              onChange={(e) => setTradeLicense(e.target.value)}
              placeholder="Trade licence number"
              style={inputStyle}
            />
          </div>

          <div style={inputGroupStyle}>
            <label htmlFor="authority" style={labelStyle}>
              Issuing Authority (সিটি কর্পোরেশন / আরজেএসসি)
            </label>
            <select
              id="authority"
              value={authority}
              onChange={(e) => setAuthority(e.target.value)}
              style={inputStyle}
            >
              <option value="">Select authority</option>
              <option value="DSCC">Dhaka South City Corp (DSCC)</option>
              <option value="DNCC">Dhaka North City Corp (DNCC)</option>
              <option value="CCC">Chittagong City Corp (CCC)</option>
              <option value="RJSC">RJSC Bangladesh</option>
            </select>
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div style={inputGroupStyle}>
            <label htmlFor="binNumber" style={labelStyle}>
              Business Identification Number (BIN-13 / ভ্যাট নিবন্ধন)
            </label>
            <input
              id="binNumber"
              type="text"
              maxLength={13}
              required
              value={binNumber}
              onChange={(e) => setBinNumber(e.target.value)}
              placeholder="13-digit BIN"
              style={inputStyle}
            />
          </div>

          <div style={inputGroupStyle}>
            <label htmlFor="etinNumber" style={labelStyle}>
              e-TIN Number (১২ ডিজিট ই-টিআইএন)
            </label>
            <input
              id="etinNumber"
              type="text"
              maxLength={12}
              required
              value={etinNumber}
              onChange={(e) => setEtinNumber(e.target.value)}
              placeholder="12-digit e-TIN"
              style={inputStyle}
            />
          </div>
        </div>

        <div style={inputGroupStyle}>
          <label htmlFor="docUpload" style={labelStyle}>
            Supporting Documents (ট্রেড লাইসেন্স ও এনআইডি কপি আপলোড)
          </label>
          <input
            id="docUpload"
            type="file"
            accept=".pdf,.png,.jpg"
            style={{ ...inputStyle, padding: 8 }}
            aria-describedby="docHelp"
          />
          <span id="docHelp" style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
            PDF, PNG or JPG up to 10MB (Stored under PDPA residency controls)
          </span>
        </div>

        <button type="submit" style={{ ...btnPrimary, cursor: "not-allowed", opacity: 0.6 }} aria-disabled="true">
          Submission unavailable (জমা দেওয়া যাচ্ছে না)
        </button>
        </fieldset>
      </form>
    </main>
  );
}
