"use client";

/**
 * Brand access — the brands linked to the signed-in partner user.
 * Access is provisioned by 1000 FiX; the portal never asks for or trusts a
 * raw brand id. Switching brand here scopes every other screen.
 */
import type { CSSProperties } from "react";
import { Loading, LoadError, tokens } from "../../lib/imports";
import { useBrand } from "../../components/brand-context";
import { PageHeader, Panel, linkButtonStyle, pageStyle, primaryLinkStyle, tdStyle, thStyle } from "../../components/ui";

const cardStyle: CSSProperties = {
  padding: 16,
  background: tokens["color.surface.primary"],
  border: `1px solid ${tokens["color.border.default"]}`,
  borderRadius: tokens["dimension.border.radius-md"],
};

export default function BrandAccountPage() {
  const { ready, error, brands, brandId, selectBrand, brand } = useBrand();

  if (!ready) return <Loading label="Resolving your brand access…" />;
  if (error) return <LoadError what="brand access" message={error} />;

  return (
    <main style={pageStyle}>
      <PageHeader
        title="Brand access"
        subtitle="The brands linked to your account. Every claim, decision and remittance is scoped to the selected brand by the server."
        actions={<a href="tel:16743" style={{ ...linkButtonStyle, textDecoration: "none" }}>☎ Warranty desk 16743</a>}
      />

      <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12, marginBottom: 16 }}>
        <div style={cardStyle}>
          <div style={{ fontSize: 11, color: tokens["color.text.secondary"], textTransform: "uppercase", letterSpacing: "0.04em" }}>Acting brand</div>
          <div style={{ fontSize: 18, fontWeight: 700, marginTop: 4 }}>{brand?.name ?? "—"}</div>
          <div style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>{brand?.code || "no code"}</div>
        </div>
        <div style={cardStyle}>
          <div style={{ fontSize: 11, color: tokens["color.text.secondary"], textTransform: "uppercase", letterSpacing: "0.04em" }}>Linked brands on this account</div>
          <div style={{ fontSize: 18, fontWeight: 700, marginTop: 4 }}>{brands.length}</div>
          <div style={{ fontSize: 11.5, color: tokens["color.text.secondary"] }}>provisioned by 1000 FiX</div>
        </div>
      </section>

      <Panel title="Brands on this account">
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: tokens["color.surface.secondary"] }}>
                <th style={thStyle}>Brand</th>
                <th style={thStyle}>Code</th>
                <th style={thStyle}>Brand ID</th>
                <th style={thStyle}>Action</th>
              </tr>
            </thead>
            <tbody>
              {brands.map((b) => (
                <tr key={b.id}>
                  <td style={{ ...tdStyle, fontWeight: 600 }}>{b.name}</td>
                  <td style={tdStyle}>{b.code || "—"}</td>
                  <td style={{ ...tdStyle, fontFamily: "monospace", fontSize: 11.5 }}>{b.id}</td>
                  <td style={tdStyle}>
                    {b.id === brandId ? (
                      <span style={{ fontSize: 11.5, color: tokens["color.status.success"], fontWeight: 600 }}>Acting brand</span>
                    ) : (
                      <button type="button" onClick={() => selectBrand(b.id)} style={{ ...primaryLinkStyle, border: "none", cursor: "pointer", padding: "5px 12px" }}>
                        Act as {b.name}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
              {brands.length === 0 && (
                <tr>
                  <td colSpan={4} style={{ ...tdStyle, color: tokens["color.text.secondary"], padding: 22 }}>
                    No brand is linked to this account. Contact the warranty desk on 16743.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Panel>

      <p style={{ marginTop: 12, fontSize: 11.5, lineHeight: 1.6, color: tokens["color.text.secondary"] }}>
        Access changes (adding a colleague's user or another brand) are made by 1000 FiX and recorded on
        the brand record. This portal never lets a user type a brand id to read another brand's claims.
      </p>
    </main>
  );
}
