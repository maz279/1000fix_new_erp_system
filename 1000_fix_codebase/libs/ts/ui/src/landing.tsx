"use client";

/**
 * LandingShell — the shared marketing shell every portal's public face
 * uses (PP5: "the landing/login experience ports to the shared
 * marketing shell"). Renders the 12 portal cards + 10 journey strips
 * from the GENERATED landing artefact (navigation, not data — extracted
 * from the frozen registry; 10KB not 1MB). Bilingual: Bengali-first
 * with an EN toggle (DE-17 — the landing is customer-facing). Tokens
 * only (CFM-01).
 */
import { useState } from "react";
import { tokens } from "./tokens/tokens.generated";
import raw from "../../i18n/src/landing.generated.json";

interface LandingArtefact {
  $description: string;
  portals: { id: string; en: string; users: string; volume: string; capabilities: string[] }[];
  journeys: { id: string; en: string; bn: string; steps: { actor: string; desc: string }[] }[];
  counts: { portals: number; journeys: number };
}
const data = raw as LandingArtefact;

export function LandingShell({ portalId }: { portalId?: string }) {
  const [locale, setLocale] = useState<"bn" | "en">("bn");
  const [openJourney, setOpenJourney] = useState<string | null>(null);

  const bn = (en: string, bnText: string) => (locale === "bn" && bnText ? bnText : en);

  return (
    <main style={{
      background: tokens["color.surface.canvas"],
      color: tokens["color.text.primary"],
      minHeight: "100vh",
      fontFamily: `${tokens["typography.font.bengali.family"]}, ${tokens["typography.font.latin.family"]}, ${tokens["typography.font.latin.fallback"]}`,
    }}>
      {/* Hero + language toggle */}
      <header style={{
        padding: "48px 32px 32px",
        borderBottom: `1px solid ${tokens["color.border.default"]}`,
        background: tokens["color.surface.primary"],
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <h1 style={{
            margin: 0, flex: 1,
            fontSize: tokens["typography.size.500"],
            fontWeight: Number(tokens["typography.weight.bold"]),
          }}>
            {bn("1000FiX — every device, every service, one platform",
                "১০০০FiX — প্রতিটি ডিভাইস, প্রতিটি সার্ভিস, এক প্ল্যাটফর্ম")}
          </h1>
          <button onClick={() => setLocale(locale === "bn" ? "en" : "bn")}
            aria-label="Toggle language"
            style={{
              padding: "6px 14px", cursor: "pointer",
              background: tokens["color.surface.canvas"],
              color: tokens["color.text.secondary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-sm"],
              fontSize: tokens["typography.size.200"],
            }}>
            {locale === "bn" ? "English" : "বাংলা"}
          </button>
        </div>
        <p style={{
          marginTop: 12, color: tokens["color.text.secondary"],
          fontSize: tokens["typography.size.300"],
        }}>
          {bn("12 portals · 10 journeys — pick yours below",
              "১২টি পোর্টাল · ১০টি যাত্রা — নিচে আপনারটি বেছে নিন")}
        </p>
      </header>

      {/* 12 portal cards */}
      <section style={{ padding: "32px 32px 16px" }}>
        <h2 style={{ margin: "0 0 16px", fontSize: tokens["typography.size.300"] }}>
          {bn("Portals", "পোর্টাল")}
        </h2>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 12 }}>
          {data.portals.map((p) => (
            <div key={p.id} style={{
              padding: 16,
              border: `1px solid ${portalId === p.id ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              background: tokens["color.surface.primary"],
            }}>
              <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
                <strong style={{ color: tokens["color.primary.base"] }}>{p.id}</strong>
                <span style={{ fontSize: tokens["typography.size.200"] }}>{p.en}</span>
              </div>
              <div style={{
                marginTop: 6, color: tokens["color.text.secondary"],
                fontSize: tokens["typography.size.100"],
              }}>
                {p.users} · {p.volume}
              </div>
              <ul style={{
                margin: "8px 0 0", paddingLeft: 16,
                color: tokens["color.text.secondary"],
                fontSize: tokens["typography.size.100"],
              }}>
                {p.capabilities.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            </div>
          ))}
        </div>
      </section>

      {/* 10 journey strips */}
      <section style={{ padding: "16px 32px 48px" }}>
        <h2 style={{ margin: "0 0 16px", fontSize: tokens["typography.size.300"] }}>
          {bn("Journeys", "যাত্রাপথ")}
        </h2>
        <div style={{ display: "grid", gap: 8 }}>
          {data.journeys.map((j) => (
            <div key={j.id} style={{
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              background: tokens["color.surface.primary"],
              overflow: "hidden",
            }}>
              <button onClick={() => setOpenJourney(openJourney === j.id ? null : j.id)}
                aria-expanded={openJourney === j.id}
                style={{
                  width: "100%", textAlign: "left", cursor: "pointer",
                  padding: "12px 16px", background: "transparent",
                  border: "none", color: tokens["color.text.primary"],
                  fontSize: tokens["typography.size.200"],
                  fontWeight: Number(tokens["typography.weight.medium"]),
                  display: "flex", gap: 12, alignItems: "center",
                }}>
                <span style={{ color: tokens["color.primary.base"] }}>{j.id}</span>
                <span style={{ flex: 1 }}>{bn(j.en, j.bn)}</span>
                <span style={{ color: tokens["color.text.secondary"] }}>
                  {openJourney === j.id ? "▲" : "▼"} {j.steps.length}+
                </span>
              </button>
              {openJourney === j.id && (
                <ol style={{
                  margin: 0, padding: "0 16px 12px 36px",
                  color: tokens["color.text.secondary"],
                  fontSize: tokens["typography.size.200"],
                }}>
                  {j.steps.map((s, i) => (
                    <li key={i} style={{ marginBottom: 6 }}>
                      <strong style={{ color: tokens["color.text.primary"] }}>{s.actor}</strong>
                      {" — "}{s.desc}
                    </li>
                  ))}
                </ol>
              )}
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
