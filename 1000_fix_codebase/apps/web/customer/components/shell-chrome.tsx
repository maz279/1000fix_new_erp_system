"use client";

/**
 * Service-Teal Fluent SHELL — the Dynamics-365-style customer-portal chrome.
 *
 * CUSTOMER SCOPE (2026-11-24): the shell carries only the customer-account
 * sections passed by components/shell.tsx. It renders no ERP area tree, no
 * module/screen search and no embedded workspace: the customer portal is not
 * a window into the back office. Staff surfaces live in P02 (technician) and
 * P03 (operations).
 *
 * Chrome parts:
 *   - 48px command bar: hamburger, brand, page search (Ctrl+K / Alt+Q),
 *     app-supplied controls slot (language / theme / auth)
 *   - 248px collapsible sitemap rail of customer sections (collapse to 48px)
 *   - MDI tab strip (session-persisted, closable, LRU-capped)
 *   - 28px status bar: environment badge, company, backend health, hotline
 */
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import type { ShellLocale, ShellSection, ShellCopy } from "../lib/imports";

export type { ShellLocale, ShellSection, ShellCopy };

interface Tab {
  href: string;
  label: string;
}

const pick = (locale: ShellLocale, en: string, bn: string) => (locale === "bn" ? bn : en);

/* ---------------------------------------------------------------------------
 * Tell-ME — the D365-style page palette (customer portal pages only)
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

  const hits = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return [];
    return sections
      .filter((s) => s.en.toLowerCase().includes(q) || s.bn.includes(query.trim()))
      .slice(0, 12);
  }, [query, sections]);

  const go = useCallback(
    (href: string) => {
      setOpen(false);
      setQuery("");
      router.push(href);
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
      go(hits[index].href);
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
        {hits.length > 0 && (
          <div className="tm-group">
            <h5>{copy.tellmePages}</h5>
            {hits.map((h) => (
              <a
                key={h.href}
                className={`tm-item${hits[index]?.href === h.href ? " active" : ""}`}
                href={h.href}
                onClick={(e) => {
                  e.preventDefault();
                  go(h.href);
                }}
              >
                <span>{h.icon} {pick(locale, h.en, h.bn)}</span>
              </a>
            ))}
          </div>
        )}
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
  bareRoutes = ["/login"],
  storageKey = "fix-shell-tabs-v2",
  children,
}: {
  brandHref?: string;
  brandWord: string;
  brandSub: string;
  locale: ShellLocale;
  sections: ShellSection[];
  copy: ShellCopy;
  rightSlot?: React.ReactNode;
  /** Routes that render bare (no chrome) — e.g. the split-screen /login. */
  bareRoutes?: string[];
  storageKey?: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  const [navOpen, setNavOpen] = useState(false);
  const [navQuery, setNavQuery] = useState("");
  const [tabs, setTabs] = useState<Tab[]>([]);
  const [online, setOnline] = useState<boolean | null>(null);

  // restore persisted chrome state
  useEffect(() => {
    setCollapsed(localStorage.getItem(`${storageKey}-collapsed`) === "1");
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw) {
        // Tabs persisted by an older build may name ERP modules ("M01 ·
        // Service Orders"). Only customer-portal destinations are restored;
        // anything else is discarded, never rendered.
        const restored = (JSON.parse(raw) as Tab[]).filter(
          (t) =>
            t &&
            typeof t.href === "string" &&
            (t.href === "/" || sections.some((s) => s.href === t.href))
        );
        setTabs(restored);
        if (restored.length !== JSON.parse(raw).length) {
          localStorage.setItem(storageKey, JSON.stringify(restored));
        }
      }
    } catch {
      /* ignore corrupt state */
    }
  }, [storageKey, sections]);

  const labelFor = useCallback(
    (href: string): string => {
      if (href === "/") return `🏠 ${copy.home}`;
      if (href === "/support") {
        const support = sections.find((x) => x.href === "/support");
        return support ? `${support.icon} ${pick(locale, support.en, support.bn)}` : href;
      }
      const s = sections.find((x) => x.href === href);
      return s ? `${s.icon} ${pick(locale, s.en, s.bn)}` : href;
    },
    [sections, locale, copy]
  );

  // tab bookkeeping on navigation
  useEffect(() => {
    if (!pathname || bareRoutes.includes(pathname)) return;
    // Only customer-portal destinations become tabs. A staff/retired route
    // (e.g. /technician or a legacy /workspace link) must not leave a tab
    // behind while it redirects the visitor.
    const allowed = pathname === "/" || sections.some((s) => s.href === pathname);
    if (!allowed) return;
    setTabs((prev) => {
      const exists = prev.some((t) => t.href === pathname);
      const next = exists
        ? prev
        : [...prev, { href: pathname, label: labelFor(pathname) }].slice(-8);
      localStorage.setItem(storageKey, JSON.stringify(next));
      return next;
    });
  }, [pathname, labelFor, storageKey, bareRoutes, sections]);

  // backend reachability (server-side probe; the browser cannot call Odoo)
  useEffect(() => {
    let cancelled = false;
    const ping = async () => {
      try {
        const res = await fetch("/api/health", { cache: "no-store" });
        const body = (await res.json()) as { ok?: boolean };
        if (!cancelled) setOnline(Boolean(body.ok));
      } catch {
        if (!cancelled) setOnline(false);
      }
    };
    ping();
    const id = setInterval(ping, 30000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

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
    (s) => s.href === pathname || (s.href !== "/" && pathname.startsWith(`${s.href}/`))
  );

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
                value={navQuery}
                onChange={(e) => setNavQuery(e.target.value)}
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
          <Link className={`nav-item${pathname === "/" ? " active" : ""}`} href="/" onClick={() => setNavOpen(false)}>
            <span aria-hidden>🏠</span>
            <span className="nav-label">{copy.home}</span>
          </Link>

          <div className="nav-zone-title">{copy.portalZone}</div>
          {sections
            .filter((s) => {
              const q = navQuery.trim().toLowerCase();
              return !q || s.en.toLowerCase().includes(q) || s.bn.includes(navQuery.trim());
            })
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
        </div>
      </nav>

      <div className="fx-main">
        {tabs.length > 0 && (
          <div className="fx-tabstrip" data-testid="tab-strip">
            {tabs.map((t) => (
              <span key={t.href} className={`tab${pathname === t.href ? " active" : ""}`}>
                <Link href={t.href}>{t.label}</Link>
                <button className="x" aria-label={`${copy.closeTab}: ${t.label}`} onClick={() => closeTab(t.href)}>
                  ✕
                </button>
              </span>
            ))}
          </div>
        )}
        <main className="fx-page" data-testid="workspace">
          <div className="crumbs" data-testid="breadcrumbs">
            <Link href="/">{brandWord}</Link>
            {activeSection && (
              <>
                <span className="sep">›</span>
                <span>{pick(locale, activeSection.en, activeSection.bn)}</span>
              </>
            )}
          </div>
          {children}
        </main>
      </div>

      <footer className="fx-statusbar" data-testid="status-bar">
        <span className="sb-env">CUSTOMER</span>
        <span>{copy.company}</span>
        <span className="sb-spacer" />
        <span title={online === null ? "…" : online ? copy.online : copy.offline}>
          <span className={`sb-dot ${online === false ? "err" : "ok"}`} aria-hidden />
          {online === null ? "…" : online ? copy.online : copy.offline}
        </span>
        <span>হটলাইন 16743</span>
        <span>Service-Teal Fluent · WCAG 2.2 AA</span>
      </footer>
    </div>
  );
}
