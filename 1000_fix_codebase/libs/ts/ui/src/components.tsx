"use client";

/**
 * Shared UI atoms for the R2 portals (PP5) — Pill, Stat, DataTable,
 * SectionHead. Styled ONLY from the generated token emission (CFM-01:
 * no hand-authored colours); every portal imports these through its
 * lib/imports barrel so the atoms exist once (no per-app duplication).
 */
import { tokens } from "./tokens/tokens.generated";

const PILL_COLORS: Record<string, { bg: string; fg: string }> = {
  // success family
  active: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  granted: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  approved: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  matched: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  verified: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  received: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  remitted: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  resolved_agent: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  commissioned: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  converted: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  paid: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  // warning family
  pending: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
  sent: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
  submitted: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
  partially_received: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
  with_ai: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
  quoted: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
  open: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
  acknowledged: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
  // error family
  expired: { bg: tokens["color.status.error-bg"], fg: tokens["color.status.error"] },
  rejected: { bg: tokens["color.status.error-bg"], fg: tokens["color.status.error"] },
  blocked: { bg: tokens["color.status.error-bg"], fg: tokens["color.status.error"] },
  withdrawn: { bg: tokens["color.status.error-bg"], fg: tokens["color.status.error"] },
  voided: { bg: tokens["color.status.error-bg"], fg: tokens["color.status.error"] },
  mismatch: { bg: tokens["color.status.error-bg"], fg: tokens["color.status.error"] },
  // info family (agent lane)
  with_agent: { bg: tokens["color.status.info-bg"], fg: tokens["color.status.info"] },
  selected: { bg: tokens["color.status.info-bg"], fg: tokens["color.status.info"] },
  in_progress: { bg: tokens["color.status.info-bg"], fg: tokens["color.status.info"] },
  new: { bg: tokens["color.status.info-bg"], fg: tokens["color.status.info"] },
};

export function Pill({ state, label }: { state: string; label?: string }) {
  const pair = PILL_COLORS[state] || {
    bg: tokens["color.status.neutral-bg"],
    fg: tokens["color.status.neutral"],
  };
  return (
    <span style={{
      display: "inline-block",
      padding: "2px 8px",
      borderRadius: tokens["dimension.border.radius-pill"],
      fontSize: tokens["typography.size.100"],
      fontWeight: Number(tokens["typography.weight.medium"]),
      textTransform: "uppercase",
      letterSpacing: "0.04em",
      background: pair.bg,
      color: pair.fg,
    }}>{label ?? state}</span>
  );
}

export function Stat({ label, value, tone }: { label: string; value: React.ReactNode; tone?: "primary" | "default" }) {
  return (
    <div style={{
      border: `1px solid ${tokens["color.border.default"]}`,
      borderRadius: tokens["dimension.border.radius-md"],
      background: tokens["color.surface.primary"],
      padding: "16px 20px",
      minWidth: 140,
    }}>
      <div style={{
        fontSize: tokens["typography.size.100"],
        color: tokens["color.text.secondary"],
        textTransform: "uppercase",
        letterSpacing: "0.06em",
        marginBottom: 6,
      }}>{label}</div>
      <div style={{
        fontSize: tokens["typography.size.400"],
        fontWeight: Number(tokens["typography.weight.semibold"]),
        color: tone === "primary"
          ? tokens["color.primary.base"]
          : tokens["color.text.primary"],
        fontVariantNumeric: "tabular-nums",
      }}>{value}</div>
    </div>
  );
}

export function SectionHead({ title, note }: { title: string; note?: string }) {
  return (
    <div style={{ margin: "0 0 16px" }}>
      <h1 style={{
        margin: 0,
        fontSize: tokens["typography.size.500"],
        color: tokens["color.text.primary"],
      }}>{title}</h1>
      {note ? (
        <p style={{
          margin: "8px 0 0",
          color: tokens["color.text.secondary"],
          fontSize: tokens["typography.size.200"],
        }}>{note}</p>
      ) : null}
    </div>
  );
}

export interface Column<T> {
  header: string;
  cell: (row: T) => React.ReactNode;
}

export function DataTable<T>({
  rows, columns, keyOf,
}: {
  rows: T[];
  columns: Column<T>[];
  /** Row key — defaults to row.id when present, else the row index. */
  keyOf?: (row: T) => string | number;
}) {
  return (
    <div style={{
      border: `1px solid ${tokens["color.border.default"]}`,
      borderRadius: tokens["dimension.border.radius-md"],
      overflow: "hidden",
    }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: tokens["color.surface.secondary"] }}>
            {columns.map((c) => (
              <th key={c.header} style={{
                textAlign: "left",
                padding: "8px 16px",
                fontSize: tokens["typography.size.200"],
                fontWeight: Number(tokens["typography.weight.medium"]),
                color: tokens["color.text.secondary"],
                borderBottom: `1px solid ${tokens["color.border.default"]}`,
              }}>{c.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={keyOf ? keyOf(row) : ((row as { id?: string | number }).id ?? i)} style={{
              borderBottom: `1px solid ${tokens["color.border.default"]}`,
            }}>
              {columns.map((c) => (
                <td key={c.header} style={{
                  padding: "8px 16px",
                  fontSize: tokens["typography.size.200"],
                  color: tokens["color.text.primary"],
                }}>{c.cell(row)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Loading({ label = "Loading…" }: { label?: string }) {
  return (
    <main style={{ padding: 48, color: tokens["color.text.secondary"] }}>
      {label}
    </main>
  );
}

export function LoadError({ what, message }: { what: string; message: string }) {
  return (
    <main style={{ padding: 48, color: tokens["color.status.error"] }}>
      Failed to load {what}: {message}
    </main>
  );
}
