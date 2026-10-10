"use client";

/**
 * LandingShell — the shared marketing shell every portal's public face
 * uses (PP5: "the landing/login experience ports to the shared
 * marketing shell"). Renders the 12 production-wired portal cards +
 * 10 journey strips from the GENERATED landing artefact (navigation,
 * not data — extracted from the frozen registry with deep links).
 * Fully bilingual: Bengali-first with an EN toggle (DE-17).
 * Tokens only (CFM-01) — strictly zero hand-authored hex colors.
 * WCAG 2.2 AA compliant keyboard navigation and ARIA controls.
 */
import { useState } from "react";
import { tokens } from "./tokens/tokens.generated";
import raw from "../../i18n/src/landing.generated.json";

interface PortalShortcut {
  label_en: string;
  label_bn: string;
  url: string;
}

interface PortalItem {
  id: string;
  en: string;
  bn: string;
  users: string;
  users_bn: string;
  volume: string;
  volume_bn: string;
  url: string;
  port: number;
  is_live: boolean;
  is_mobile: boolean;
  tech: string;
  capabilities: string[];
  capabilities_bn: string[];
  shortcuts: PortalShortcut[];
}

interface JourneyStep {
  actor: string;
  actor_bn: string;
  desc: string;
  desc_bn: string;
}

interface JourneyItem {
  id: string;
  en: string;
  bn: string;
  steps: JourneyStep[];
}

interface LandingArtefact {
  $description: string;
  portals: PortalItem[];
  journeys: JourneyItem[];
  counts: { portals: number; journeys: number };
}

const data = raw as unknown as LandingArtefact;

export function LandingShell({
  portalId,
  locale: controlledLocale,
  onToggleLocale,
}: {
  portalId?: string;
  locale?: "bn" | "en";
  onToggleLocale?: () => void;
}) {
  const [internalLocale, setInternalLocale] = useState<"bn" | "en">("bn");
  const [openJourney, setOpenJourney] = useState<string | null>(null);

  const currentLocale = controlledLocale ?? internalLocale;
  const handleToggle = () => {
    if (onToggleLocale) {
      onToggleLocale();
    } else {
      setInternalLocale(currentLocale === "bn" ? "en" : "bn");
    }
  };

  const bn = (en: string, bnText?: string) =>
    currentLocale === "bn" && bnText ? bnText : en;

  return (
    <main
      style={{
        background: tokens["color.surface.canvas"],
        color: tokens["color.text.primary"],
        minHeight: "100vh",
        fontFamily: `${tokens["typography.font.bengali.family"]}, ${tokens["typography.font.latin.family"]}, ${tokens["typography.font.latin.fallback"]}`,
      }}
    >
      {/* Hero Banner with Integrated Language Synchronization */}
      <header
        style={{
          padding: "36px 32px 28px",
          borderBottom: `${tokens["dimension.border.width"]} solid ${tokens["color.border.default"]}`,
          background: tokens["color.surface.primary"],
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
          <div style={{ flex: 1, minWidth: 280 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <span
                style={{
                  fontSize: tokens["typography.size.100"],
                  background: tokens["color.status.info-bg"],
                  color: tokens["color.primary.base"],
                  border: `${tokens["dimension.border.width"]} solid ${tokens["color.status.info-border"]}`,
                  padding: "3px 10px",
                  borderRadius: tokens["dimension.border.radius-pill"],
                  fontWeight: Number(tokens["typography.weight.semibold"]),
                }}
              >
                {bn("ISO 9001:2015 Certified", "আইএসও ৯০০১:২০১৫ সার্টিফাইড")}
              </span>
              <span
                style={{
                  fontSize: tokens["typography.size.100"],
                  background: tokens["color.surface.secondary"],
                  color: tokens["color.text.secondary"],
                  padding: "3px 10px",
                  borderRadius: tokens["dimension.border.radius-pill"],
                }}
              >
                {bn("Hotline: 16743", "হটলাইন: ১৬৭৪৩")}
              </span>
            </div>
            <h1
              style={{
                margin: 0,
                fontSize: tokens["typography.size.500"],
                fontWeight: Number(tokens["typography.weight.bold"]),
                lineHeight: tokens["typography.lineHeight.step-500"],
                color: tokens["color.text.primary"],
              }}
            >
              {bn(
                "1000FiX — every device, every service, one platform",
                "১০০০FiX — প্রতিটি ডিভাইস, প্রতিটি সার্ভিস, এক প্ল্যাটফর্ম"
              )}
            </h1>
            <p
              style={{
                margin: "8px 0 0",
                color: tokens["color.text.secondary"],
                fontSize: tokens["typography.size.200"],
                lineHeight: tokens["typography.lineHeight.step-200"],
              }}
            >
              {bn(
                "12 production portals · 10 customer journeys — fully integrated smart service architecture",
                "১২টি সমন্বিত পোর্টাল · ১০টি গ্রাহক যাত্রাপথ — সম্পূর্ণ আধুনিক ডিজিটাল আফটার-সেলস সিস্টেম"
              )}
            </p>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <button
              onClick={handleToggle}
              aria-label={bn("Switch language to English", "ভাষা পরিবর্তন করে বাংলায় দেখুন")}
              style={{
                padding: "8px 18px",
                cursor: "pointer",
                background: tokens["color.surface.primary"],
                color: tokens["color.primary.base"],
                border: `${tokens["dimension.border.width"]} solid ${tokens["color.primary.base"]}`,
                borderRadius: tokens["dimension.border.radius-sm"],
                fontSize: tokens["typography.size.200"],
                fontWeight: Number(tokens["typography.weight.semibold"]),
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <span>🌐</span>
              <span>{currentLocale === "bn" ? "English" : "বাংলা"}</span>
            </button>
          </div>
        </div>
      </header>

      {/* 12 Interactive Production Portal Cards */}
      <section
        aria-labelledby="portals-section-heading"
        style={{ padding: "32px 32px 16px" }}
      >
        <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 16 }}>
          <h2
            id="portals-section-heading"
            style={{
              margin: 0,
              fontSize: tokens["typography.size.400"],
              fontWeight: Number(tokens["typography.weight.bold"]),
            }}
          >
            {bn("Integrated Portals (P01–P12)", "সমন্বিত ১২টি পোর্টাল নির্দেশিকা (P01–P12)")}
          </h2>
          <span
            style={{
              color: tokens["color.text.secondary"],
              fontSize: tokens["typography.size.200"],
            }}
          >
            {bn("Click any portal below to launch", "সরাসরি প্রবেশ করতে নিচে যেকোনো পোর্টাল নির্বাচন করুন")}
          </span>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(310px, 1fr))",
            gap: 16,
          }}
        >
          {data.portals.map((p) => {
            const isCurrent = portalId === p.id;
            const cardCapabilities =
              currentLocale === "bn" && p.capabilities_bn && p.capabilities_bn.length > 0
                ? p.capabilities_bn
                : p.capabilities;

            return (
              <article
                key={p.id}
                style={{
                  padding: 20,
                  display: "flex",
                  flexDirection: "column",
                  border: `${tokens["dimension.border.width"]} solid ${
                    isCurrent ? tokens["color.primary.base"] : tokens["color.border.default"]
                  }`,
                  borderRadius: tokens["dimension.border.radius-md"],
                  background: isCurrent
                    ? tokens["color.primary.wash"]
                    : tokens["color.surface.primary"],
                  boxShadow: isCurrent
                    ? `0 0 0 1px ${tokens["color.primary.base"]}`
                    : "none",
                }}
              >
                {/* Card Header & Status Badges */}
                <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
                  <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
                    <span
                      style={{
                        padding: "2px 8px",
                        background: isCurrent
                          ? tokens["color.primary.base"]
                          : tokens["color.surface.secondary"],
                        color: isCurrent
                          ? tokens["color.text.inverse"]
                          : tokens["color.primary.base"],
                        borderRadius: tokens["dimension.border.radius-sm"],
                        fontWeight: Number(tokens["typography.weight.bold"]),
                        fontSize: tokens["typography.size.200"],
                      }}
                    >
                      {p.id}
                    </span>
                    <h3
                      style={{
                        margin: 0,
                        fontSize: tokens["typography.size.200"],
                        fontWeight: Number(tokens["typography.weight.bold"]),
                        color: tokens["color.text.primary"],
                        lineHeight: tokens["typography.lineHeight.step-200"],
                      }}
                    >
                      {bn(p.en, p.bn)}
                    </h3>
                  </div>

                  {isCurrent && (
                    <span
                      style={{
                        fontSize: tokens["typography.size.100"],
                        color: tokens["color.primary.base"],
                        fontWeight: Number(tokens["typography.weight.semibold"]),
                        background: tokens["color.primary.tint"],
                        padding: "2px 6px",
                        borderRadius: tokens["dimension.border.radius-sm"],
                        whiteSpace: "nowrap",
                      }}
                    >
                      {bn("Current", "বর্তমান")}
                    </span>
                  )}
                </div>

                {/* Audience & Metric Volume */}
                <div
                  style={{
                    marginTop: 10,
                    color: tokens["color.text.secondary"],
                    fontSize: tokens["typography.size.100"],
                    display: "flex",
                    alignItems: "center",
                    gap: 6,
                    flexWrap: "wrap",
                  }}
                >
                  <span>{bn(p.users, p.users_bn)}</span>
                  <span>·</span>
                  <span style={{ fontWeight: Number(tokens["typography.weight.semibold"]) }}>
                    {bn(p.volume, p.volume_bn)}
                  </span>
                </div>

                {/* Capabilities list */}
                <ul
                  style={{
                    margin: "12px 0",
                    paddingLeft: 18,
                    color: tokens["color.text.secondary"],
                    fontSize: tokens["typography.size.100"],
                    flex: 1,
                    lineHeight: "1.6",
                  }}
                >
                  {cardCapabilities.map((c, i) => (
                    <li key={i}>{c}</li>
                  ))}
                </ul>

                {/* Status / Technology Indicator */}
                <div
                  style={{
                    marginBottom: 14,
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    fontSize: tokens["typography.size.100"],
                  }}
                >
                  <span
                    style={{
                      display: "inline-block",
                      width: 8,
                      height: 8,
                      borderRadius: tokens["dimension.border.radius-pill"],
                      background: p.is_live
                        ? tokens["color.status.success"]
                        : tokens["color.border.accessible"],
                    }}
                  />
                  <span style={{ color: tokens["color.text.secondary"] }}>
                    {p.is_live
                      ? bn(`Port ${p.port} · Live Active`, `পোর্ট ${p.port} · সক্রিয় সংযোগ`)
                      : bn(`Port ${p.port} · Standby`, `পোর্ট ${p.port} · স্ট্যান্ডার্ড সংযোগ`)}
                  </span>
                  <span style={{ color: tokens["color.border.strong"] }}>|</span>
                  <span style={{ color: tokens["color.text.secondary"] }}>{p.tech}</span>
                </div>

                {/* Primary Action Button */}
                <div style={{ marginTop: "auto" }}>
                  <a
                    href={p.url}
                    target={p.url.startsWith("http") ? "_blank" : undefined}
                    rel="noreferrer"
                    aria-label={bn(`Launch portal ${p.id}: ${p.en}`, `${p.id} পোর্টাল খুলুন: ${p.bn}`)}
                    style={{
                      display: "block",
                      textAlign: "center",
                      padding: "8px 14px",
                      textDecoration: "none",
                      borderRadius: tokens["dimension.border.radius-sm"],
                      fontSize: tokens["typography.size.200"],
                      fontWeight: Number(tokens["typography.weight.semibold"]),
                      background: isCurrent
                        ? tokens["color.primary.base"]
                        : tokens["color.surface.primary"],
                      color: isCurrent
                        ? tokens["color.text.inverse"]
                        : tokens["color.primary.base"],
                      border: `${tokens["dimension.border.width"]} solid ${tokens["color.primary.base"]}`,
                    }}
                  >
                    {isCurrent
                      ? bn("Enter Customer Home →", "হোমে প্রবেশ করুন →")
                      : p.id === "P03"
                      ? bn("Launch Odoo Operations ↗", "ওডু অপারেশনস পোর্টাল ↗")
                      : p.is_mobile
                      ? bn("View Dispatch Hub ↗", "সেন্ট্রাল হাব দেখুন ↗")
                      : bn("Launch Portal ↗", "পোর্টাল খুলুন ↗")}
                  </a>

                  {/* Deep-link shortcuts (for P01 or configured portals) */}
                  {p.shortcuts && p.shortcuts.length > 0 && (
                    <div
                      style={{
                        marginTop: 10,
                        paddingTop: 8,
                        borderTop: `${tokens["dimension.border.width"]} dashed ${tokens["color.border.default"]}`,
                        display: "flex",
                        gap: 6,
                        flexWrap: "wrap",
                      }}
                    >
                      {p.shortcuts.map((sc, sci) => (
                        <a
                          key={sci}
                          href={sc.url}
                          target={sc.url.startsWith("http") ? "_blank" : undefined}
                          rel="noreferrer"
                          style={{
                            fontSize: tokens["typography.size.100"],
                            color: tokens["color.text.secondary"],
                            textDecoration: "none",
                            background: tokens["color.surface.secondary"],
                            padding: "3px 8px",
                            borderRadius: tokens["dimension.border.radius-sm"],
                          }}
                        >
                          {bn(sc.label_en, sc.label_bn)}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </section>

      {/* 10 Production Journey Strips with Accessible Accordions */}
      <section
        aria-labelledby="journeys-section-heading"
        style={{ padding: "16px 32px 48px" }}
      >
        <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 16 }}>
          <h2
            id="journeys-section-heading"
            style={{
              margin: 0,
              fontSize: tokens["typography.size.400"],
              fontWeight: Number(tokens["typography.weight.bold"]),
            }}
          >
            {bn("End-to-End Journeys (J01–J10)", "সম্পূর্ণ সেবা প্রক্রিয়াসমূহ (J01–J10)")}
          </h2>
          <span
            style={{
              color: tokens["color.text.secondary"],
              fontSize: tokens["typography.size.200"],
            }}
          >
            {bn("Click any journey to inspect step-by-step trace", "ধাপভিত্তিক বিস্তারিত দেখতে ক্লিক করুন")}
          </span>
        </div>

        <div style={{ display: "grid", gap: 10 }}>
          {data.journeys.map((j) => {
            const isOpen = openJourney === j.id;
            const headerId = `journey-header-${j.id}`;
            const panelId = `journey-panel-${j.id}`;

            return (
              <div
                key={j.id}
                style={{
                  border: `${tokens["dimension.border.width"]} solid ${
                    isOpen ? tokens["color.primary.base"] : tokens["color.border.default"]
                  }`,
                  borderRadius: tokens["dimension.border.radius-md"],
                  background: tokens["color.surface.primary"],
                  overflow: "hidden",
                }}
              >
                <button
                  id={headerId}
                  onClick={() => setOpenJourney(isOpen ? null : j.id)}
                  aria-expanded={isOpen}
                  aria-controls={panelId}
                  aria-label={bn(
                    `Toggle journey ${j.id}: ${j.en}`,
                    `যাত্রাপথ ${j.id} বিস্তারিত দেখুন বা লুকান: ${j.bn}`
                  )}
                  style={{
                    width: "100%",
                    textAlign: "left",
                    cursor: "pointer",
                    padding: "14px 18px",
                    background: "transparent",
                    border: "none",
                    color: tokens["color.text.primary"],
                    fontSize: tokens["typography.size.200"],
                    fontWeight: Number(tokens["typography.weight.medium"]),
                    display: "flex",
                    gap: 14,
                    alignItems: "center",
                  }}
                >
                  <span
                    style={{
                      color: tokens["color.primary.base"],
                      fontWeight: Number(tokens["typography.weight.bold"]),
                    }}
                  >
                    {j.id}
                  </span>
                  <span style={{ flex: 1, fontWeight: Number(tokens["typography.weight.semibold"]) }}>
                    {bn(j.en, j.bn)}
                  </span>
                  <span
                    style={{
                      color: tokens["color.text.secondary"],
                      fontSize: tokens["typography.size.100"],
                      background: tokens["color.surface.secondary"],
                      padding: "2px 8px",
                      borderRadius: tokens["dimension.border.radius-sm"],
                    }}
                  >
                    {isOpen ? "▲" : "▼"} {j.steps.length} {bn("steps", "ধাপ")}
                  </span>
                </button>

                {isOpen && (
                  <div
                    id={panelId}
                    role="region"
                    aria-labelledby={headerId}
                    style={{
                      borderTop: `${tokens["dimension.border.width"]} solid ${tokens["color.border.default"]}`,
                      background: tokens["color.surface.wash"],
                      padding: "14px 18px 16px 36px",
                    }}
                  >
                    <ol
                      style={{
                        margin: 0,
                        padding: 0,
                        color: tokens["color.text.secondary"],
                        fontSize: tokens["typography.size.200"],
                        lineHeight: "1.7",
                      }}
                    >
                      {j.steps.map((s, i) => (
                        <li key={i} style={{ marginBottom: 8 }}>
                          <strong style={{ color: tokens["color.text.primary"], marginRight: 6 }}>
                            {bn(s.actor, s.actor_bn)}
                          </strong>
                          {" — "}
                          <span>{bn(s.desc, s.desc_bn)}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </section>
    </main>
  );
}
