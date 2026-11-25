"use client";

/**
 * Shared UI atoms for the R2 portals (PP5) — Pill, Stat, DataTable,
 * SectionHead. Styled ONLY from the generated token emission (CFM-01:
 * no hand-authored colours); every portal imports these through its
 * lib/imports barrel so the atoms exist once (no per-app duplication).
 *
 * Theme bridge (2026-10-23): role colours resolve to the R6 CSS custom
 * properties (tokens.css) with the literal token value as fallback —
 * portals that ship tokens.css get working [data-theme=dark]; portals
 * that don't render exactly as before.
 */
import { tokens } from "./tokens/tokens.generated";

/** var(--fix-<path>, <literal token value>) — see generate-design-tokens.py R6. */
const v = (path: string): string =>
  `var(--fix-${path.replace(/\./g, "-")}, ${tokens[path as keyof typeof tokens]})`;

// Semantic aliases (light literal fallback / dark override in tokens.css)
const C = {
  surface: v("color.surface.primary"),
  surface2: v("color.surface.secondary"),
  ink: v("color.text.primary"),
  inkMuted: v("color.text.secondary"),
  stroke: v("color.border.default"),
  primary: v("color.primary.base"),
  okBg: v("color.status.success-bg"),
  ok: tokens["color.status.success"],
  warnBg: v("color.status.warning-bg"),
  warn: tokens["color.status.warning"],
  errBg: v("color.status.error-bg"),
  err: tokens["color.status.error"],
  infoBg: v("color.status.info-bg"),
  info: tokens["color.status.info"],
  neutralBg: v("color.status.neutral-bg"),
  neutral: tokens["color.status.neutral"],
};

const PILL_COLORS: Record<string, { bg: string; fg: string }> = {
  // success family
  active: { bg: C.okBg, fg: C.ok },
  granted: { bg: C.okBg, fg: C.ok },
  approved: { bg: C.okBg, fg: C.ok },
  matched: { bg: C.okBg, fg: C.ok },
  verified: { bg: C.okBg, fg: C.ok },
  received: { bg: C.okBg, fg: C.ok },
  remitted: { bg: C.okBg, fg: C.ok },
  resolved_agent: { bg: C.okBg, fg: C.ok },
  commissioned: { bg: C.okBg, fg: C.ok },
  converted: { bg: C.okBg, fg: C.ok },
  paid: { bg: C.okBg, fg: C.ok },
  done: { bg: C.okBg, fg: C.ok },
  // warning family
  pending: { bg: C.warnBg, fg: C.warn },
  sent: { bg: C.warnBg, fg: C.warn },
  submitted: { bg: C.warnBg, fg: C.warn },
  partially_received: { bg: C.warnBg, fg: C.warn },
  with_ai: { bg: C.warnBg, fg: C.warn },
  quoted: { bg: C.warnBg, fg: C.warn },
  open: { bg: C.warnBg, fg: C.warn },
  acknowledged: { bg: C.warnBg, fg: C.warn },
  // error family
  expired: { bg: C.errBg, fg: C.err },
  rejected: { bg: C.errBg, fg: C.err },
  blocked: { bg: C.errBg, fg: C.err },
  withdrawn: { bg: C.errBg, fg: C.err },
  voided: { bg: C.errBg, fg: C.err },
  mismatch: { bg: C.errBg, fg: C.err },
  cancelled: { bg: C.errBg, fg: C.err },
  // info family (agent lane)
  with_agent: { bg: C.infoBg, fg: C.info },
  selected: { bg: C.infoBg, fg: C.info },
  in_progress: { bg: C.infoBg, fg: C.info },
  new: { bg: C.infoBg, fg: C.info },
  confirmed: { bg: C.infoBg, fg: C.info },
};

export function Pill({ state, label }: { state: string; label?: string }) {
  const pair = PILL_COLORS[state] || { bg: C.neutralBg, fg: C.neutral };
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
      border: `1px solid ${C.stroke}`,
      borderRadius: tokens["dimension.border.radius-md"],
      background: C.surface,
      padding: "16px 20px",
      minWidth: 140,
    }}>
      <div style={{
        fontSize: tokens["typography.size.100"],
        color: C.inkMuted,
        textTransform: "uppercase",
        letterSpacing: "0.06em",
        marginBottom: 6,
      }}>{label}</div>
      <div style={{
        fontSize: tokens["typography.size.400"],
        fontWeight: Number(tokens["typography.weight.semibold"]),
        color: tone === "primary" ? C.primary : C.ink,
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
        color: C.ink,
      }}>{title}</h1>
      {note ? (
        <p style={{
          margin: "8px 0 0",
          color: C.inkMuted,
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
      border: `1px solid ${C.stroke}`,
      borderRadius: tokens["dimension.border.radius-md"],
      overflow: "hidden",
    }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ background: C.surface2 }}>
            {columns.map((c) => (
              <th key={c.header} style={{
                textAlign: "left",
                padding: "8px 16px",
                fontSize: tokens["typography.size.200"],
                fontWeight: Number(tokens["typography.weight.medium"]),
                color: C.inkMuted,
                borderBottom: `1px solid ${C.stroke}`,
              }}>{c.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={keyOf ? keyOf(row) : ((row as { id?: string | number }).id ?? i)} style={{
              borderBottom: `1px solid ${C.stroke}`,
            }}>
              {columns.map((c) => (
                <td key={c.header} style={{
                  padding: "8px 16px",
                  fontSize: tokens["typography.size.200"],
                  color: C.ink,
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
    <main style={{ padding: 48, color: C.inkMuted }}>
      {label}
    </main>
  );
}

export function LoadError({ what, message }: { what: string; message: string }) {
  return (
    <main className="load-error" style={{ margin: "0 auto", maxWidth: 640 }}>
      <h4>⚠️ Failed to load {what}</h4>
      <p style={{ fontSize: 12 }}>{message}</p>
    </main>
  );
}
