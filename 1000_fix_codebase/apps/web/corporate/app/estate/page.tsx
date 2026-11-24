"use client";

/**
 * Fleet estate — the corporate client's registered devices by site.
 *
 * Live, partner-fenced data from /corporate/estate. Adds site and asset-tag
 * visibility, warranty filtering, CSV export and a bulk path into the service
 * request flow. Money is never computed here; the backend sends every value.
 */
import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { callOdoo } from "../../lib/api";
import { useLanguage } from "../../components/language";
import { RequireAuth } from "../../components/require-auth";
import {
  PageHeader,
  Panel,
  StatePill,
  StatCard,
  downloadCsv,
  linkButtonStyle,
  pageStyle,
  tdStyle,
  thStyle,
} from "../../components/ui";

interface Device {
  id: number;
  brand: string;
  model: string;
  identifier: string;
  serial_number: string;
  imei: string;
  asset_tag: string;
  site: string;
  state: string;
  custody_state: string;
  warranty_status: string;
  warranty_end: string | null;
}

interface SiteRow {
  site: string;
  count: number;
}

function EstateContent() {
  const { locale } = useLanguage();
  const { t } = useLanguage();
  const bn = locale === "bn";
  const router = useRouter();
  const [devices, setDevices] = useState<Device[]>([]);
  const [sites, setSites] = useState<SiteRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState("");
  const [warranty, setWarranty] = useState("all");
  const [siteFilter, setSiteFilter] = useState("all");
  const [selected, setSelected] = useState<number[]>([]);

  useEffect(() => {
    let active = true;
    callOdoo<{ devices: Device[]; sites: SiteRow[] }>("/corporate/estate")
      .then((d) => {
        if (!active) return;
        setDevices(d.devices || []);
        setSites(d.sites || []);
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

  const filtered = useMemo(
    () =>
      devices.filter((d) => {
        const q = query.trim().toLowerCase();
        const matchesQuery =
          !q ||
          d.brand.toLowerCase().includes(q) ||
          d.model.toLowerCase().includes(q) ||
          d.serial_number.toLowerCase().includes(q) ||
          d.asset_tag.toLowerCase().includes(q) ||
          d.imei.toLowerCase().includes(q);
        const matchesWarranty = warranty === "all" || d.warranty_status === warranty;
        const matchesSite = siteFilter === "all" || d.site === siteFilter;
        return matchesQuery && matchesWarranty && matchesSite;
      }),
    [devices, query, warranty, siteFilter]
  );

  const toggle = (id: number) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  };

  const exportCsv = () => {
    downloadCsv(
      `1000fix-fleet-${new Date().toISOString().slice(0, 10)}.csv`,
      ["Brand", "Model", "Serial", "IMEI", "Asset tag", "Site", "Warranty status", "Warranty end", "State"],
      devices.map((d) => [
        d.brand,
        d.model,
        d.serial_number,
        d.imei,
        d.asset_tag,
        d.site,
        d.warranty_status,
        d.warranty_end || "",
        d.state,
      ])
    );
  };

  if (loading) return <Loading label={bn ? "ডিভাইস বহর লোড হচ্ছে…" : "Loading the fleet estate…"} />;
  if (error) return <LoadError what={bn ? "ডিভাইস বহর" : "Fleet estate"} message={error} />;

  const inWarranty = devices.filter((d) => ["in_warranty", "extended"].includes(d.warranty_status)).length;
  const unassigned = devices.filter((d) => !d.site).length;
  const outWarranty = devices.filter((d) => d.warranty_status === "out_of_warranty").length;

  return (
    <main style={pageStyle}>
      <PageHeader
        title={bn ? "ডিভাইস বহর" : "Fleet estate"}
        subtitle={
          bn
            ? `${devices.length}টি নিবন্ধিত ডিভাইস — সাইট, সিরিয়াল, অ্যাসেট ট্যাগ ও ওয়ারেন্টি অবস্থা।`
            : `${devices.length} registered devices — site, serial, asset tag and warranty state.`
        }
        actions={
          <>
            <button type="button" onClick={exportCsv} style={{ ...linkButtonStyle, cursor: "pointer" }}>
              ⬇ {bn ? "CSV এক্সপোর্ট" : "Export CSV"}
            </button>
            <Link
              href={
                selected.length
                  ? `/service-requests?devices=${selected.join(",")}`
                  : "/service-requests"
              }
              style={{ ...linkButtonStyle, textDecoration: "none" }}
            >
              {bn
                ? selected.length
                  ? `${selected.length} ডিভাইসের জন্য অনুরোধ`
                  : "সার্ভিস অনুরোধ"
                : selected.length
                  ? `Request service for ${selected.length}`
                  : "Raise a service request"}
            </Link>
          </>
        }
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 16 }}>
        <StatCard label={bn ? "মোট ডিভাইস" : "Total assets"} value={devices.length} tone="primary" />
        <StatCard label={bn ? "ওয়ারেন্টিতে" : "In warranty"} value={inWarranty} tone="success" />
        <StatCard label={bn ? "ওয়ারেন্টির বাইরে" : "Out of warranty"} value={outWarranty} tone={outWarranty ? "warning" : "neutral"} />
        <StatCard label={bn ? "সাইট ছাড়া" : "Unassigned site"} value={unassigned} tone={unassigned ? "error" : "neutral"} />
      </section>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", marginBottom: 12 }}>
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={bn ? "ব্র্যান্ড, মডেল, সিরিয়াল বা অ্যাসেট ট্যাগ…" : "Brand, model, serial or asset tag…"}
          style={{
            flex: "1 1 260px",
            maxWidth: 420,
            padding: "8px 12px",
            border: `1px solid ${tokens["color.border.default"]}`,
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.surface.primary"],
            color: tokens["color.text.primary"],
            fontSize: tokens["typography.size.200"],
          }}
        />
        <select
          value={siteFilter}
          onChange={(e) => setSiteFilter(e.target.value)}
          aria-label={bn ? "সাইট" : "Site"}
          style={{
            padding: "8px 10px",
            border: `1px solid ${tokens["color.border.default"]}`,
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.surface.primary"],
            color: tokens["color.text.primary"],
            fontSize: tokens["typography.size.200"],
          }}
        >
          <option value="all">{bn ? `সব সাইট (${sites.length})` : `All sites (${sites.length})`}</option>
          {sites.map((s) => (
            <option key={s.site} value={s.site}>{s.site} ({s.count})</option>
          ))}
        </select>
        {[
          { key: "all", en: "All", bn: "সব" },
          { key: "in_warranty", en: "In warranty", bn: "ওয়ারেন্টিতে" },
          { key: "extended", en: "Extended", bn: "এক্সটেন্ডেড" },
          { key: "out_of_warranty", en: "Out", bn: "বাইরে" },
        ].map((f) => (
          <button
            key={f.key}
            type="button"
            aria-pressed={warranty === f.key}
            onClick={() => setWarranty(f.key)}
            style={{
              padding: "6px 12px",
              fontSize: tokens["typography.size.200"],
              borderRadius: tokens["dimension.border.radius-sm"],
              border: `1px solid ${warranty === f.key ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
              background: warranty === f.key ? tokens["color.primary.base"] : tokens["color.surface.primary"],
              color: warranty === f.key ? tokens["color.text.inverse"] : tokens["color.text.secondary"],
              cursor: "pointer",
            }}
          >
            {bn ? f.bn : f.en}
          </button>
        ))}
      </div>

      <Panel>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={{ ...thStyle, width: 34 }} aria-label={t.estateTitle}> </th>
                <th style={thStyle}>{bn ? "ডিভাইস" : "Device"}</th>
                <th style={thStyle}>{bn ? "সিরিয়াল" : "Serial"}</th>
                <th style={thStyle}>{bn ? "অ্যাসেট ট্যাগ" : "Asset tag"}</th>
                <th style={thStyle}>{bn ? "সাইট" : "Site"}</th>
                <th style={thStyle}>{bn ? "ওয়ারেন্টি" : "Warranty"}</th>
                <th style={thStyle}>{bn ? "অবস্থা" : "State"}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((d) => (
                <tr key={d.id}>
                  <td style={tdStyle}>
                    <input
                      type="checkbox"
                      checked={selected.includes(d.id)}
                      onChange={() => toggle(d.id)}
                      aria-label={`${bn ? "নির্বাচন" : "Select"} ${d.brand} ${d.model}`}
                    />
                  </td>
                  <td style={tdStyle}>
                    <div style={{ fontWeight: 600 }}>{d.brand} {d.model}</div>
                    <div style={{ fontSize: 11, color: tokens["color.text.secondary"] }}>{d.identifier || "—"}</div>
                  </td>
                  <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11.5 }}>{d.serial_number || d.imei || "—"}</td>
                  <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11.5 }}>{d.asset_tag || "—"}</td>
                  <td style={tdStyle}>{d.site || <span style={{ color: tokens["color.status.warning"] }}>{bn ? "নির্ধারিত নয়" : "Unassigned"}</span>}</td>
                  <td style={tdStyle}>
                    <StatePill state={d.warranty_status} />
                    {d.warranty_end && (
                      <div style={{ fontSize: 10.5, color: tokens["color.text.secondary"], marginTop: 2 }}>→ {d.warranty_end}</div>
                    )}
                  </td>
                  <td style={tdStyle}>{d.state}</td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ ...tdStyle, textAlign: "center", color: tokens["color.text.secondary"], padding: 28 }}>
                    {bn ? "এই ফিল্টারে কোনো ডিভাইস নেই।" : "No devices in this filter."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      {selected.length > 0 && (
        <div
          role="status"
          style={{
            marginTop: 12,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 12,
            flexWrap: "wrap",
            padding: "10px 14px",
            background: tokens["color.surface.primary"],
            border: `1px solid ${tokens["color.primary.base"]}`,
            borderRadius: tokens["dimension.border.radius-md"],
            fontSize: 12.5,
          }}
        >
          <span>
            {bn
              ? `${selected.length}টি ডিভাইস নির্বাচিত — এক অনুরোধে সার্ভিস তৈরি করুন।`
              : `${selected.length} device${selected.length === 1 ? "" : "s"} selected — raise one bulk request.`}
          </span>
          <div style={{ display: "flex", gap: 8 }}>
            <button type="button" onClick={() => setSelected([])} style={{ ...linkButtonStyle, cursor: "pointer" }}>
              {bn ? "নির্বাচন বাতিল" : "Clear"}
            </button>
            <button
              type="button"
              onClick={() => router.push(`/service-requests?devices=${selected.join(",")}`)}
              style={{
                ...linkButtonStyle,
                background: tokens["color.primary.base"],
                color: tokens["color.text.inverse"],
                border: "none",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              {bn ? "বাল্ক অনুরোধ" : "Continue to request"}
            </button>
          </div>
        </div>
      )}
    </main>
  );
}

export default function EstatePage() {
  return (
    <RequireAuth>
      <EstateContent />
    </RequireAuth>
  );
}
