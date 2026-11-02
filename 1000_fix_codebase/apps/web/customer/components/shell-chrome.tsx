"use client";

/**
 * Service-Teal Fluent SHELL — the Dynamics-365 portal chrome (asset 6 port).
 *
 * Faithful port of the frozen prototype shell (Front_end/js/shell.js +
 * css/app.css) to Next.js App Router, driven by the generated nav payload
 * (libs nav.generated.ts ← contracts/nav/registry.json):
 *   - 48px command bar: hamburger, brand, Tell-ME search (Ctrl+K / Alt+Q),
 *     app-supplied controls slot (language / theme / density / auth)
 *   - 248px collapsible sitemap rail: portal sections + 12 ERP area
 *     accordions (67 modules), collapse to 48px icon rail
 *   - per-area mega menu flyout (module chips + group columns + screens)
 *   - MDI tab strip (session-persisted, closable, LRU-capped)
 *   - 28px status bar: env badge, company, backend health, hotline
 *
 * ERP entries render INSIDE this portal: modules with a realized native
 * customer page navigate in-app; every other registry module opens
 * /workspace/<moduleId> — the embedded P03 Operations Workspace pane
 * (app/workspace/[module]/page.tsx).
 *
 * Lives in the app (not libs/ts/ui) because it imports next/link +
 * next/navigation, which do not resolve from the lib directory — the lib
 * keeps only the framework-free nav payload.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { navAreas, navCounts, pingHealth } from "../lib/imports";
import type { NavArea, NavModule } from "../lib/imports";
import type { ShellLocale, ShellSection, ShellCopy } from "../lib/imports";

export type { ShellLocale, ShellSection, ShellCopy };

/**
 * ERP module destinations. The registry carries no routing fields, so the
 * native-customer-surface map is maintained here; modules without a native
 * page open the embedded P03 workspace pane instead — no navigation away
 * from the portal.
 */
const NATIVE_MODULE_ROUTES: Record<string, string> = {
  M01: "/", // Service Requests & Orders → My Service Bookings
  M02: "/technician", // Field Service & Dispatch → P02 job queue
  M03: "/tracking", // Service Logistics (Pick & Drop) → live tracking
  M17: "/devices", // Device & Asset Registry → My Registered Devices
};

const NATIVE_SCREEN_ROUTES: Record<string, string> = {
  "M01-estimates": "/estimates",
};

function moduleHref(m: NavModule): string {
  return NATIVE_MODULE_ROUTES[m.id] ?? `/workspace/${m.id}`;
}

function screenHref(m: NavModule, screenId: string): string {
  return NATIVE_SCREEN_ROUTES[screenId] ?? `/workspace/${m.id}`;
}

/** All registry modules by id — tab/breadcrumb labels for /workspace routes. */
const ALL_MODULES: Record<string, NavModule> = {};
for (const area of navAreas) {
  for (const m of area.modules) ALL_MODULES[m.id] = m;
}

interface Tab {
  href: string;
  label: string;
}

const pick = (locale: ShellLocale, en: string, bn: string) => (locale === "bn" ? bn : en);

/* ---------------------------------------------------------------------------
 * Tell-ME — the D365 global search palette (results dropdown under the input)
 * ------------------------------------------------------------------------- */
function TellMe({
  locale,
  sections,
  copy,
}: {
  locale: ShellLocale;
  sections: ShellSection[];
  copy: ShellCopy;
}) {
  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [index, setIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const boxRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey && e.key.toLowerCase() === "k") || (e.altKey && e.key.toLowerCase() === "q")) {
        e.preventDefault();
        inputRef.current?.focus();
        setOpen(true);
      }
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (boxRef.current && !boxRef.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  interface Hit {
    kind: "page" | "module" | "screen";
    label: string;
    meta: string;
    href: string;
  }

  const hits = useMemo<Hit[]>(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    const out: Hit[] = [];
    for (const s of sections) {
      if (s.en.toLowerCase().includes(q) || s.bn.includes(query.trim())) {
        out.push({ kind: "page", label: pick(locale, s.en, s.bn), meta: "P01", href: s.href });
      }
    }
    for (const area of navAreas) {
      for (const m of area.modules) {
        if (out.length > 40) break;
        if (m.en.toLowerCase().includes(q) || m.bn.includes(query.trim()) || m.id.toLowerCase() === q) {
          out.push({ kind: "module", label: `${m.icon} ${pick(locale, m.en, m.bn)}`, meta: m.id, href: moduleHref(m) });
        }
        for (const g of m.groups) {
          for (const sc of g.screens) {
            if (
              sc.en.toLowerCase().includes(q) ||
              sc.bn.includes(query.trim()) ||
              sc.id.toLowerCase() === q
            ) {
              out.push({
                kind: "screen",
                label: pick(locale, sc.en, sc.bn),
                meta: `${sc.id} · ${m.id}`,
                href: screenHref(m, sc.id),
              });
            }
            if (out.length > 40) break;
          }
          if (out.length > 40) break;
        }
      }
    }
    return out.slice(0, 24);
  }, [query, sections, locale]);

  const grouped = useMemo(() => {
    const g: Record<Hit["kind"], Hit[]> = { page: [], module: [], screen: [] };
    for (const h of hits) if (g[h.kind].length < 8) g[h.kind].push(h);
    return g;
  }, [hits]);

  const go = useCallback(
    (hit: Hit) => {
      setOpen(false);
      setQuery("");
      router.push(hit.href);
    },
    [router]
  );

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setIndex((i) => Math.min(i + 1, hits.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setIndex((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter" && hits[index]) {
      e.preventDefault();
      go(hits[index]);
    }
  };

  return (
    <div className="fx-tellme" ref={boxRef}>
      <input
        ref={inputRef}
        type="search"
        role="searchbox"
        aria-label={copy.searchPlaceholder}
        placeholder={copy.searchPlaceholder}
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setOpen(true);
          setIndex(0);
        }}
        onFocus={() => setOpen(true)}
        onKeyDown={onKeyDown}
        data-testid="tellme-input"
      />
      <span className="tm-ico" aria-hidden>⌕</span>
      <span className="tm-kbd kbd kbd-sm" aria-hidden>Alt+Q</span>
      <div className={`tm-results${open && query.trim() ? " open" : ""}`} role="listbox">
        {hits.length === 0 && (
          <div className="tm-item" style={{ color: "var(--fix-ink-muted)" }}>{copy.tellmeEmpty}</div>
        )}
        {grouped.page.length > 0 && (
          <div className="tm-group">
            <h5>{copy.tellmePages}</h5>
            {grouped.page.map((h, i) => (
              <a key={`p${i}`} className={`tm-item${index === hits.indexOf(h) ? " active" : ""}`} href={h.href} onClick={(e) => { e.preventDefault(); go(h); }}>
                <span>{h.label}</span>
                <span className="tm-meta">{h.meta}</span>
              </a>
            ))}
          </div>
        )}
        {grouped.module.length > 0 && (
          <div className="tm-group">
            <h5>{copy.tellmeModules} · P03</h5>
            {grouped.module.map((h) => (
              <a key={h.meta} className={`tm-item${index === hits.indexOf(h) ? " active" : ""}`} href={h.href} onClick={(e) => { e.preventDefault(); go(h); }}>
                <span>{h.label}</span>
                <span className="tm-meta">{h.meta}</span>
              </a>
            ))}
          </div>
        )}
        {grouped.screen.length > 0 && (
          <div className="tm-group">
            <h5>{copy.tellmeScreens} · P03</h5>
            {grouped.screen.map((h) => (
              <a key={h.meta + h.label} className={`tm-item${index === hits.indexOf(h) ? " active" : ""}`} href={h.href} onClick={(e) => { e.preventDefault(); go(h); }}>
                <span>{h.label}</span>
                <span className="tm-meta mono">{h.meta}</span>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------------
 * Mega menu — per-area flyout (module chips + group columns + screens)
 * ------------------------------------------------------------------------- */
function MegaMenu({
  area,
  locale,
  onClose,
}: {
  area: NavArea | null;
  locale: ShellLocale;
  onClose: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const onDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) onClose();
    };
    const onEsc = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onEsc);
    return () => {
      document.removeEventListener("mousedown", onDown);
      document.removeEventListener("keydown", onEsc);
    };
  }, [onClose]);

  if (!area) return null;
  const groups = area.modules.reduce((n, m) => n + m.groups.length, 0);
  const screens = area.modules.reduce(
    (n, m) => n + m.groups.reduce((k, g) => k + g.screens.length, 0),
    0
  );

  return (
    <div className="fx-mega open" ref={ref} role="dialog" aria-label={pick(locale, area.en, area.bn)} data-testid="mega-menu">
      <div className="mega-head">
        <div className="mega-title">
          {pick(locale, area.en, area.bn)} <span className="mono faint" style={{ fontSize: 10 }}>{area.id}</span>
        </div>
        <div className="mega-actions">
          {area.modules.map((m) => (
            <Link key={m.id} className="mega-chip" href={moduleHref(m)} title={m.id} onClick={onClose}>
              {m.icon} {pick(locale, m.en, m.bn)}
            </Link>
          ))}
        </div>
      </div>
      <div className="mega-cols">
        {area.modules.slice(0, 3).map((m: NavModule) =>
          m.groups.map((g) => (
            <div className="mega-col" key={`${m.id}-${g.en}`}>
              <h6>
                <i>{m.id}</i> {g.en}
              </h6>
              {g.screens.map((s) => (
                <Link key={s.id} href={screenHref(m, s.id)} onClick={onClose}>
                  {pick(locale, s.en, s.bn)}
                  <span className="sc-type">{s.t}</span>
                </Link>
              ))}
            </div>
          ))
        )}
      </div>
      <div className="mega-foot">
        {area.modules.length} {locale === "bn" ? "মডিউল" : "modules"} · {groups}{" "}
        {locale === "bn" ? "গ্রুপ" : "groups"} · {screens}{" "}
        {locale === "bn" ? "স্ক্রিন — পোর্টালের ভিতরে খোলে" : "screens — open inside the portal"}
      </div>
    </div>
  );
}

/* ---------------------------------------------------------------------------
 * The shell
 * ------------------------------------------------------------------------- */
export function Shell({
  brandHref = "/",
  brandWord,
  brandSub,
  locale,
  sections,
  copy,
  rightSlot,
  healthUrl = "/api/odoo/web/login",
  bareRoutes = ["/login"],
  storageKey = "fix-shell-tabs",
  children,
}: {
  brandHref?: string;
  brandWord: string;
  brandSub: string;
  locale: ShellLocale;
  sections: ShellSection[];
  copy: ShellCopy;
  rightSlot?: React.ReactNode;
  healthUrl?: string;
  /** Routes that render bare (no chrome) — e.g. the split-screen /login. */
  bareRoutes?: string[];
  storageKey?: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  const [navOpen, setNavOpen] = useState(false);
  const [openArea, setOpenArea] = useState<string | null>(null);
  const [megaArea, setMegaArea] = useState<NavArea | null>(null);
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [online, setOnline] = useState<boolean | null>(null);

  // restore persisted chrome state
  useEffect(() => {
    setCollapsed(localStorage.getItem(`${storageKey}-collapsed`) === "1");
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw) setTabs(JSON.parse(raw));
    } catch {
      /* ignore corrupt state */
    }
  }, [storageKey]);

  const labelFor = useCallback(
    (href: string): string => {
      const s = sections.find((x) => x.href === href);
      if (s) return `${s.icon} ${pick(locale, s.en, s.bn)}`;
      const ws = href.match(/^\/workspace\/([^/]+)$/);
      if (ws) {
        const m = ALL_MODULES[ws[1]];
        return m ? `${m.icon} ${pick(locale, m.en, m.bn)}` : "🧭 Operations Workspace";
      }
      return href;
    },
    [sections, locale]
  );

  // tab bookkeeping on navigation
  useEffect(() => {
    if (!pathname || bareRoutes.includes(pathname)) return;
    setTabs((prev) => {
      const exists = prev.some((t) => t.href === pathname);
      const next = exists
        ? prev
        : [...prev, { href: pathname, label: labelFor(pathname) }].slice(-8);
      localStorage.setItem(storageKey, JSON.stringify(next));
      return next;
    });
  }, [pathname, labelFor, storageKey, bareRoutes]);

  // backend health poll (light GET through the same-origin rewrite)
  useEffect(() => {
    let cancelled = false;
    const ping = async () => {
      // P-11: every fetch() lives in libs/ts/api-client (FF-39). pingHealth
      // never throws — an unreachable endpoint is simply offline.
      const ok = await pingHealth(healthUrl);
      if (!cancelled) setOnline(ok);
    };
    ping();
    const id = setInterval(ping, 30000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [healthUrl]);

  const closeTab = (href: string) => {
    setTabs((prev) => {
      const idx = prev.findIndex((t) => t.href === href);
      const next = prev.filter((t) => t.href !== href);
      localStorage.setItem(storageKey, JSON.stringify(next));
      if (pathname === href) {
        const fallback = next[Math.min(idx, next.length - 1)];
        router.push(fallback ? fallback.href : "/");
      }
      return next;
    });
  };

  if (pathname && bareRoutes.includes(pathname)) {
    return <>{children}</>;
  }

  const activeSection = sections.find(
    (s) => s.href === pathname || (s.href !== "/" && pathname.startsWith(s.href))
  );

  // Workspace-pane crumb: /workspace/M31 → "M31 · Workshop & Depot Repair"
  const wsMatch = pathname ? pathname.match(/^\/workspace\/([^/]+)$/) : null;
  const wsCrumb = wsMatch
    ? ALL_MODULES[wsMatch[1]]
      ? `${wsMatch[1]} · ${pick(locale, ALL_MODULES[wsMatch[1]].en, ALL_MODULES[wsMatch[1]].bn)}`
      : "Operations Workspace"
    : null;

  const toggleCollapsed = () => {
    setCollapsed((c) => {
      localStorage.setItem(`${storageKey}-collapsed`, c ? "0" : "1");
      return !c;
    });
  };

  return (
    <div className={`fx-shell${collapsed ? " nav-collapsed" : ""}${navOpen ? " nav-open" : ""}`}>
      <header className="fx-topbar" data-testid="command-bar">
        <button
          className="tb-icon-btn"
          aria-label={locale === "bn" ? "নেভিগেশন" : "Navigation"}
          aria-expanded={navOpen || !collapsed}
          onClick={() => {
            if (window.innerWidth <= 1024) setNavOpen((v) => !v);
            else toggleCollapsed();
          }}
        >
          ☰
        </button>
        <Link className="tb-brand" href={brandHref}>
          <span className="tb-logo" aria-hidden>F</span>
          <span className="tb-word">
            {brandWord}
            <small>{brandSub}</small>
          </span>
        </Link>
        <TellMe locale={locale} sections={sections} copy={copy} />
        <div className="tb-right">{rightSlot}</div>
      </header>

      <nav className="fx-nav" aria-label={locale === "bn" ? "প্রধান নেভিগেশন" : "Primary"}>
        {!collapsed && (
          <div className="nav-head">
            <div className="nv-search">
              <input
                type="search"
                placeholder={locale === "bn" ? "নেভিগেশন ফিল্টার…" : "Filter navigation…"}
                onChange={(e) => {
                  const q = e.target.value.trim().toUpperCase();
                  if (!q) return setOpenArea(null);
                  const hit = navAreas.find(
                    (a) =>
                      a.en.toUpperCase().includes(q) ||
                      a.bn.includes(e.target.value.trim()) ||
                      a.id === q
                  );
                  if (hit) setOpenArea(hit.id);
                }}
                aria-label={locale === "bn" ? "নেভিগেশন ফিল্টার" : "Filter navigation"}
              />
              <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden>
                <circle cx="7" cy="7" r="4.5" stroke="currentColor" />
                <line x1="10.5" y1="10.5" x2="14" y2="14" stroke="currentColor" />
              </svg>
            </div>
          </div>
        )}
        <div className="nav-scroll">
          <Link
            className={`nav-item${pathname === "/" ? " active" : ""}`}
            href="/"
            onClick={() => setNavOpen(false)}
          >
            <span aria-hidden>🏠</span>
            <span className="nav-label">{copy.home}</span>
          </Link>

          <div className="nav-zone-title">{copy.portalZone}</div>
          {sections
            .filter((s) => s.href !== "/")
            .map((s) => (
              <Link
                key={s.href}
                className={`nav-item${pathname === s.href ? " active" : ""}`}
                href={s.href}
                onClick={() => setNavOpen(false)}
              >
                <span aria-hidden>{s.icon}</span>
                <span className="nav-label">{pick(locale, s.en, s.bn)}</span>
              </Link>
            ))}

          <div className="nav-zone-title">{copy.erpZone}</div>
          {navAreas.map((area) => {
            const expanded = openArea === area.id;
            return (
              <div key={area.id}>
                <div style={{ display: "flex", alignItems: "center" }}>
                  <button
                    className={`nav-item nav-area${expanded ? " expanded" : ""}`}
                    style={{ flex: 1 }}
                    aria-expanded={expanded}
                    onClick={() => setOpenArea(expanded ? null : area.id)}
                  >
                    <span className="chev" aria-hidden>›</span>
                    <span className="nav-label">{pick(locale, area.en, area.bn)}</span>
                    <span className="nav-count">{area.modules.length}</span>
                  </button>
                  {!collapsed && (
                    <button
                      className="tb-icon-btn"
                      style={{ minWidth: 26, height: 26 }}
                      aria-label={`${pick(locale, area.en, area.bn)} — mega menu`}
                      onClick={(e) => {
                        e.stopPropagation();
                        setMegaArea(area);
                      }}
                    >
                      ▤
                    </button>
                  )}
                </div>
                {expanded && !collapsed && (
                  <div className="nav-sub open">
                    {area.modules.map((m) => (
                      <Link key={m.id} className="nav-mod" href={moduleHref(m)} onClick={() => setNavOpen(false)}>
                        <span aria-hidden>{m.icon}</span>
                        <span className="nav-label">{pick(locale, m.en, m.bn)}</span>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            );
          })}

          <div className="nav-zone-title">{copy.systemZone}</div>
          <Link className="nav-item" href="/workspace/p03" onClick={() => setNavOpen(false)}>
            <span aria-hidden>🧭</span>
            <span className="nav-label">{copy.opsLabel}</span>
          </Link>
          <Link className="nav-item" href="/welcome">
            <span aria-hidden>✦</span>
            <span className="nav-label">{copy.portalsLabel}</span>
          </Link>
        </div>
      </nav>

      <MegaMenu area={megaArea} locale={locale} onClose={() => setMegaArea(null)} />

      <div className="fx-main">
        {tabs.length > 0 && (
          <div className="fx-tabstrip" data-testid="tab-strip">
            {tabs.map((t) => (
              <span key={t.href} className={`tab${pathname === t.href ? " active" : ""}`}>
                <Link href={t.href}>{t.label}</Link>
                <button
                  className="x"
                  aria-label={`${copy.closeTab}: ${t.label}`}
                  onClick={() => closeTab(t.href)}
                >
                  ✕
                </button>
              </span>
            ))}
          </div>
        )}
        <main className="fx-page" data-testid="workspace">
          <div className="crumbs" data-testid="breadcrumbs">
            <Link href="/">{brandWord}</Link>
            {activeSection && activeSection.href !== "/" && (
              <>
                <span className="sep">›</span>
                <span>{pick(locale, activeSection.en, activeSection.bn)}</span>
              </>
            )}
            {wsCrumb && (
              <>
                <span className="sep">›</span>
                <span>{wsCrumb}</span>
              </>
            )}
          </div>
          {children}
        </main>
      </div>

      <footer className="fx-statusbar" data-testid="status-bar">
        <span className="sb-env">DEMO</span>
        <span>{copy.company}</span>
        <span className="sb-spacer" />
        <span title={online === null ? "…" : online ? copy.online : copy.offline}>
          <span className={`sb-dot ${online === false ? "err" : "ok"}`} aria-hidden />
          {online === null ? "…" : online ? copy.online : copy.offline}
        </span>
        <span className="mono faint">
          {navCounts.modules} M · {navCounts.screens} S
        </span>
        <span>Service-Teal Fluent · WCAG 2.2 AA</span>
      </footer>
    </div>
  );
}
