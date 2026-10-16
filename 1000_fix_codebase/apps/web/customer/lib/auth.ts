/**
 * Customer Authentication & Session Management (W4 / P-11 contract).
 * Authenticates against Odoo via the Kong gateway (/web/session/authenticate).
 * In browsers, the Odoo session cookie (session_id) is automatically preserved
 * with credentials: "include", allowing all customer endpoints (/customer/*) to pass auth="user".
 */
export interface UserSession {
  uid: number;
  name: string;
  username: string;
  partnerId: number;
  isPortal: boolean;
}

const API_BASE = (process.env.NEXT_PUBLIC_FIX_API_BASE || "http://127.0.0.1:8000").replace(/\/+$/, "");

export async function login(loginName: string, password: string, db: string = "fix_dev"): Promise<UserSession> {
  const res = await fetch(`${API_BASE}/web/session/authenticate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "call",
      id: Date.now(),
      params: { db, login: loginName, password },
    }),
  });

  if (!res.ok) {
    throw new Error(`Authentication server error: ${res.status}`);
  }

  const data = await res.json();
  if (data.error) {
    const msg = data.error.data?.message || data.error.message || "Invalid login credentials";
    throw new Error(msg);
  }

  const result = data.result;
  if (!result || !result.uid) {
    throw new Error("Invalid username or password");
  }

  const session: UserSession = {
    uid: result.uid,
    name: result.name || loginName,
    username: result.username || loginName,
    partnerId: result.partner_id || result.uid,
    isPortal: Boolean(result.is_portal),
  };

  if (typeof window !== "undefined") {
    window.sessionStorage.setItem("fix_user", JSON.stringify(session));
    window.sessionStorage.setItem("fix_token", `session_${result.uid}_${Date.now()}`);
  }

  return session;
}

export async function sendOtp(phone: string): Promise<{ sent: boolean; message: string; masked_phone: string; dev_code?: string }> {
  const res = await fetch(`${API_BASE}/customer/auth/otp/send`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "call",
      id: Date.now(),
      params: { phone },
    }),
  });

  if (!res.ok) {
    throw new Error(`OTP service error: ${res.status}`);
  }

  const data = await res.json();
  if (data.error) {
    throw new Error(data.error.data?.message || data.error.message || "Failed to send OTP");
  }
  if (data.result?.error) {
    throw new Error(data.result.error.message || "Failed to send OTP");
  }
  return data.result;
}

export async function loginWithOtp(phone: string, otp: string): Promise<UserSession> {
  const res = await fetch(`${API_BASE}/customer/auth/otp/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      jsonrpc: "2.0",
      method: "call",
      id: Date.now(),
      params: { phone, otp },
    }),
  });

  if (!res.ok) {
    throw new Error(`OTP verification error: ${res.status}`);
  }

  const data = await res.json();
  if (data.error) {
    throw new Error(data.error.data?.message || data.error.message || "OTP verification failed");
  }
  if (data.result?.error) {
    throw new Error(data.result.error.message || "Invalid OTP code");
  }

  const user = data.result.user;
  const session: UserSession = {
    uid: user.uid,
    name: user.name || `Customer (${phone.slice(-4)})`,
    username: user.phone || phone,
    partnerId: user.partner_id || user.uid,
    isPortal: Boolean(user.is_portal),
  };

  if (typeof window !== "undefined") {
    window.sessionStorage.setItem("fix_user", JSON.stringify(session));
    window.sessionStorage.setItem("fix_token", `session_${user.uid}_${Date.now()}`);
  }

  return session;
}

export async function logout(): Promise<void> {
  try {
    await fetch(`${API_BASE}/web/session/destroy`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        id: Date.now(),
        params: {},
      }),
    });
  } catch {
    /* ignore network failure on logout */
  }

  if (typeof window !== "undefined") {
    window.sessionStorage.removeItem("fix_user");
    window.sessionStorage.removeItem("fix_token");
  }
}

export function getCurrentUser(): UserSession | null {
  if (typeof window === "undefined") return null;
  const raw = window.sessionStorage.getItem("fix_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as UserSession;
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  return getCurrentUser() !== null;
}
