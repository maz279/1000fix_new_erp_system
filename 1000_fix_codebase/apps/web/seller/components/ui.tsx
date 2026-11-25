"use client";

/**
 * Shared presentation atoms for the seller portal. Tokens only (CFM-01);
 * money arrives as backend BN-007 strings and is never recomputed here.
 */
import type { CSSProperties, ReactNode } from "react";
import { tokens } from "../lib/imports";

export const pageStyle: CSSProperties = {
  padding: "28px 32px 48px",
  maxWidth: 1440,
  margin: "0 auto",
};

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <header
      style={{
        display: "flex",
        flexWrap: "wrap",
        alignItems: "flex-start",
        justifyContent: "space-between",
        gap: 16,
        marginBottom: 22,
        paddingBottom: 18,
        borderBottom: `1px solid ${tokens["color.border.default"]}`,
      }}
    >
      <div style={{ minWidth: 0 }}>
        <h1
          style={{
            margin: "0 0 6px",
            fontSize: tokens["typography.size.500"],
            lineHeight: 1.2,
            color: tokens["color.text.primary"],
          }}
        >
          {title}
        </h1>
        {subtitle && (
          <p
            style={{
              margin: 0,
              maxWidth: "95ch",
              color: tokens["color.text.secondary"],
              fontSize: tokens["typography.size.200"],
              lineHeight: 1.55,
            }}
          >
            {subtitle}
          </p>
        )}
      </div>
      {actions && <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>{actions}</div>}
    </header>
  );
}

export function StatCard({
  label,
  value,
  note,
  tone = "neutral",
}: {
  label: string;
  value: string | number;
  note?: string;
  tone?: "neutral" | "primary" | "success" | "warning" | "error";
}) {
  const color =
    tone === "primary"
      ? tokens["color.primary.base"]
      : tone === "success"
        ? tokens["color.status.success"]
        : tone === "warning"
          ? tokens["color.status.warning"]
          : tone === "error"
            ? tokens["color.status.error"]
            : tokens["color.text.primary"];
  return (
    <article
      style={{
        padding: 16,
        background: tokens["color.surface.primary"],
        border: `1px solid ${tokens["color.border.default"]}`,
        borderRadius: tokens["dimension.border.radius-md"],
        minWidth: 0,
      }}
    >
      <div style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.200"], marginBottom: 6 }}>
        {label}
      </div>
      <div
        style={{
          fontSize: tokens["typography.size.500"],
          fontWeight: Number(tokens["typography.weight.bold"]),
          color,
          fontVariantNumeric: "tabular-nums",
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
        title={String(value)}
      >
        {value}
      </div>
      {note && (
        <div style={{ color: tokens["color.text.secondary"], fontSize: tokens["typography.size.100"], marginTop: 4 }}>
          {note}
        </div>
      )}
    </article>
  );
}

export function Panel({
  title,
  actions,
  children,
  padding = 0,
}: {
  title?: string;
  actions?: ReactNode;
  children: ReactNode;
  padding?: number;
}) {
  return (
    <section
      style={{
        background: tokens["color.surface.primary"],
        border: `1px solid ${tokens["color.border.default"]}`,
        borderRadius: tokens["dimension.border.radius-md"],
        overflow: "hidden",
      }}
    >
      {(title || actions) && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 12,
            padding: "12px 16px",
            borderBottom: `1px solid ${tokens["color.border.default"]}`,
          }}
        >
          {title && (
            <h2 style={{ margin: 0, fontSize: tokens["typography.size.300"], color: tokens["color.text.primary"] }}>
              {title}
            </h2>
          )}
          {actions}
        </div>
      )}
      <div style={{ padding }}>{children}</div>
    </section>
  );
}

const STATE_TONE: Record<string, { bg: string; fg: string }> = {
  success: { bg: tokens["color.status.success-bg"], fg: tokens["color.status.success"] },
  warning: { bg: tokens["color.status.warning-bg"], fg: tokens["color.status.warning"] },
  error: { bg: tokens["color.status.error-bg"], fg: tokens["color.status.error"] },
  info: { bg: tokens["color.status.info-bg"], fg: tokens["color.status.info"] },
  neutral: { bg: tokens["color.surface.secondary"], fg: tokens["color.text.secondary"] },
};

const STATE_MAP: Record<string, keyof typeof STATE_TONE> = {
  verified: "success",
  selected: "success",
  paid: "success",
  earned: "success",
  active: "success",
  resolved: "success",
  completed: "success",
  submitted: "info",
  open: "info",
  quoted: "info",
  in_progress: "info",
  investigating: "info",
  accrued: "warning",
  in_review: "warning",
  pending: "warning",
  raised: "warning",
  arbitration: "warning",
  paused: "warning",
  draft: "neutral",
  unverified: "neutral",
  not_selected: "neutral",
  void: "neutral",
  rejected: "error",
  forfeited: "error",
  escalated: "error",
  cancelled: "error",
};

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: keyof typeof STATE_TONE }) {
  const t = STATE_TONE[tone] ?? STATE_TONE.neutral;
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 9px",
        borderRadius: tokens["dimension.border.radius-pill"],
        fontSize: tokens["typography.size.100"],
        fontWeight: 600,
        background: t.bg,
        color: t.fg,
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </span>
  );
}

export function StateBadge({ state, label }: { state: string; label?: string }) {
  const tone = STATE_MAP[state.toLowerCase()] ?? "neutral";
  return <Badge tone={tone}>{label ?? state.replace(/_/g, " ")}</Badge>;
}

/** Client-side CSV of already-rendered backend values (no math here). */
export function downloadCsv(filename: string, header: string[], rows: string[][]): void {
  const escape = (v: string) => `"${(v ?? "").replace(/"/g, '""')}"`;
  const csv = [header, ...rows].map((r) => r.map(escape).join(",")).join("\r\n");
  const blob = new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export const thStyle: CSSProperties = {
  textAlign: "left",
  padding: "9px 14px",
  fontSize: tokens["typography.size.100"],
  color: tokens["color.text.secondary"],
  textTransform: "uppercase",
  letterSpacing: "0.04em",
  whiteSpace: "nowrap",
};

export const tdStyle: CSSProperties = {
  padding: "9px 14px",
  fontSize: tokens["typography.size.200"],
  color: tokens["color.text.primary"],
  borderTop: `1px solid ${tokens["color.border.default"]}`,
  verticalAlign: "middle",
};

export const linkButtonStyle: CSSProperties = {
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  padding: "8px 14px",
  borderRadius: tokens["dimension.border.radius-sm"],
  border: `1px solid ${tokens["color.border.default"]}`,
  background: tokens["color.surface.primary"],
  color: tokens["color.text.primary"],
  fontSize: tokens["typography.size.200"],
  fontWeight: 500,
  textDecoration: "none",
  cursor: "pointer",
};

export const primaryLinkStyle: CSSProperties = {
  ...linkButtonStyle,
  border: "none",
  background: tokens["color.primary.base"],
  color: tokens["color.text.inverse"],
  fontWeight: 600,
};

export const selectStyle: CSSProperties = {
  padding: "8px 10px",
  borderRadius: tokens["dimension.border.radius-sm"],
  border: `1px solid ${tokens["color.border.default"]}`,
  background: tokens["color.surface.primary"],
  color: tokens["color.text.primary"],
  fontSize: tokens["typography.size.200"],
};
