/** Server-side Odoo reachability probe; exposes no ERP data. */
import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

const UPSTREAM_TIMEOUT_MS = 4_000;

function odooBase(): string | null {
  const raw = (process.env.ODOO_INTERNAL_URL || "http://127.0.0.1:8069").trim();
  try {
    const url = new URL(raw);
    if (url.protocol !== "http:" && url.protocol !== "https:") return null;
    if (url.username || url.password || url.search || url.hash) return null;
    return url.origin;
  } catch {
    return null;
  }
}

export async function GET(): Promise<NextResponse> {
  const base = odooBase();
  if (!base) {
    return NextResponse.json({ ok: false, reason: "misconfigured" }, { status: 503 });
  }
  try {
    const res = await fetch(`${base}/web/login`, {
      method: "GET",
      redirect: "manual",
      cache: "no-store",
      signal: AbortSignal.timeout(UPSTREAM_TIMEOUT_MS),
    });
    return NextResponse.json(
      { ok: res.status < 500 },
      { status: 200, headers: { "cache-control": "no-store" } }
    );
  } catch {
    return NextResponse.json(
      { ok: false, reason: "unreachable" },
      { status: 200, headers: { "cache-control": "no-store" } }
    );
  }
}
