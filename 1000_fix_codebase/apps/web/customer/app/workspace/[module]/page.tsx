"use client";

/**
 * Embedded ERP workspace pane (P03 Operations Workspace in-page).
 *
 * Registry modules without a native customer-portal page render HERE —
 * inside the portal main area — instead of navigating away to :8069:
 *   - the pane iframes the P03 client action on the SAME hostname the user
 *     browses (Odoo's session cookie is host-only + port-agnostic, so the
 *     iframe shares the portal's Odoo login — no login wall);
 *   - it then drives the workspace to the requested module via a
 *     postMessage handshake: `p03:open {m, s}` is retried until the
 *     workspace OWL controller acks `p03:opened` (it mounts seconds after
 *     the iframe load event, so a single fire would be racy);
 *   - odoo-side listener: cd_p03_portal/static/src/p03_workspace.js;
 *     framing is allowed by the cd_portal_embed module's frame-ancestors
 *     policy.
 */
import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { navAreas, tokens } from "../../../lib/imports";
import type { NavModule } from "../../../lib/imports";
import { useLanguage } from "../../../components/language";

const P03_DEEPLINK_PATH = "/odoo/action-cd_p03_portal.action_p03_workspace";

function opsUrlForHost(hostname: string | null): string {
  return `http://${hostname ?? "127.0.0.1"}:8069${P03_DEEPLINK_PATH}`;
}

const ALL_MODULES: Record<string, NavModule> = {};
for (const area of navAreas) {
  for (const m of area.modules) ALL_MODULES[m.id] = m;
}

function WorkspacePane() {
  const params = useParams<{ module: string }>();
  const searchParams = useSearchParams();
  const moduleId = params?.module ?? "p03";
  const screenId = searchParams.get("screen");

  const { locale } = useLanguage();

  // Root pane (/workspace/p03) shows the workspace home — no handshake.
  const isRoot = moduleId === "p03" || !ALL_MODULES[moduleId];
  const mod = ALL_MODULES[moduleId] ?? null;

  // Browsing hostname (mount-resolved) keeps the Odoo cookie jar continuous
  // with the portal session — same pattern as the rest of the shell.
  const [hostName, setHostName] = useState<string | null>(null);
  useEffect(() => {
    setHostName(window.location.hostname);
  }, []);
  const src = opsUrlForHost(hostName);
  // MessageEvent.origin is scheme://host:port — compare against the URL's
  // origin, not the full deep-link URL.
  const opsOrigin = useMemo(() => new URL(src).origin, [src]);

  const [loaded, setLoaded] = useState(false);
  // Ack is tracked per module id: switching modules while the page stays
  // mounted re-arms the handshake without reloading the iframe (src is
  // constant — the workspace itself navigates).
  const [ackedFor, setAckedFor] = useState<string | null>(isRoot ? moduleId : null);
  const opened = ackedFor === moduleId;

  const frameRef = useRef<HTMLIFrameElement>(null);

  // Retry `p03:open` until the workspace acks — the listener inside Odoo
  // only exists once the OWL action has mounted, which happens well after
  // the iframe's load event.
  useEffect(() => {
    if (isRoot || opened || !hostName) return;
    const target = mod?.id ?? moduleId;
    const id = window.setInterval(() => {
      frameRef.current?.contentWindow?.postMessage(
        { type: "p03:open", m: target, s: screenId },
        src
      );
    }, 600);
    return () => window.clearInterval(id);
  }, [isRoot, opened, hostName, moduleId, screenId, src, mod]);

  // Handshake ack from the embedded workspace (origin must be the Odoo host).
  useEffect(() => {
    const onMessage = (ev: MessageEvent) => {
      if (ev.origin !== opsOrigin) return;
      const d = ev.data as { type?: string; m?: string } | null;
      if (d?.type === "p03:opened" && d.m === moduleId) {
      frameRef.current?.contentWindow?.postMessage(
        { type: "p03:set-locale", locale },
        src
      );
        setAckedFor(moduleId);
      }
    };
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [opsOrigin, moduleId]);

  const title = mod
    ? `${mod.icon} ${locale === "bn" ? mod.bn : mod.en}`
    : locale === "bn"
      ? "🧭 অপারেশনস ওয়ার্কস্পেস"
      : "🧭 Operations Workspace";

  const statusLine = useMemo(() => {
    if (locale === "bn") {
      if (!loaded) return "P03 ওয়ার্কস্পেস লোড হচ্ছে…";
      if (!opened && !isRoot) return `${moduleId} খোলা হচ্ছে…`;
      return `P03 ওয়ার্কস্পেস · Odoo ব্যাকএন্ড (${hostName ?? "…"}:8069) থেকে এমবেড করা`;
    }
    if (!loaded) return "Loading the P03 workspace…";
    if (!opened && !isRoot) return `Opening ${moduleId}…`;
    return `P03 workspace · embedded from the Odoo backend (${hostName ?? "…"}:8069)`;
  }, [locale, loaded, opened, isRoot, moduleId, hostName]);

  useEffect(() => {
    frameRef.current?.contentWindow?.postMessage(
      { type: "p03:set-locale", locale },
      src
    );
  }, [locale, src]);

  const onFrameLoad = useCallback(() => setLoaded(true), []);

  return (
    <section
      aria-label={locale === "bn" ? "এমবেডেড ERP ওয়ার্কস্পেস" : "Embedded ERP workspace"}
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 10,
        height: "calc(100dvh - 176px)",
        minHeight: 460,
      }}
      data-testid="workspace-pane"
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          flexWrap: "wrap",
          padding: "12px 16px",
          background: tokens["color.surface.primary"],
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-sm"],
        }}
      >
        <div style={{ minWidth: 0 }}>
          <h1
            style={{
              margin: 0,
              fontSize: tokens["typography.size.300"],
              color: tokens["color.primary.base"],
              whiteSpace: "nowrap",
              overflow: "hidden",
              textOverflow: "ellipsis",
            }}
          >
            {title}
            {mod && (
              <span
                className="mono faint"
                style={{ marginLeft: 8, fontSize: tokens["typography.size.100"] }}
              >
                {mod.id}
              </span>
            )}
          </h1>
          <p style={{ margin: "4px 0 0", fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
            {statusLine}
          </p>
        </div>
        <a
          href={src}
          target="_blank"
          rel="noopener"
          style={{
            fontSize: tokens["typography.size.100"],
            fontWeight: 600,
            color: tokens["color.primary.base"],
            textDecoration: "none",
            whiteSpace: "nowrap",
          }}
        >
          {locale === "bn" ? "পূর্ণ স্ক্রিনে খুলুন ↗" : "Open full view ↗"}
        </a>
      </div>

      <div
        style={{
          position: "relative",
          flex: "1 1 auto",
          minHeight: 0,
          background: tokens["color.surface.primary"],
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-sm"],
          overflow: "hidden",
        }}
      >
        {!loaded && (
          <div
            role="status"
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: tokens["color.text.secondary"],
              fontSize: tokens["typography.size.200"],
            }}
          >
            {statusLine}
          </div>
        )}
        <iframe
          ref={frameRef}
          src={src}
          title={locale === "bn" ? "P03 অপারেশনস ওয়ার্কস্পেস" : "P03 Operations Workspace"}
          onLoad={onFrameLoad}
          data-testid="workspace-frame"
          style={{ width: "100%", height: "100%", border: 0, display: "block", background: "#fff" }}
        />
      </div>
    </section>
  );
}

export default function WorkspacePage() {
  return (
    <Suspense fallback={null}>
      <WorkspacePane />
    </Suspense>
  );
}
