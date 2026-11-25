/**
 * P02 geofenced clock-in (M55 AUT-WFM-02 / T-06) — pure helpers (no React),
 * unit-tested by lib/clock-in.test.mjs (`npm test`).
 *
 * Contract (docs/guides/offline-sync-protocol.md §6.5, technician_api.py
 * parse_clock_in_position / evaluate_clock_in_position): the online
 * /technician/attendance/clock_in call and the offline `clock_in` command carry
 * the SAME params — geo_lat, geo_long (required) and accuracy_m (the fix's
 * accuracy radius in metres). Odoo always RECORDS the clock-in and flags it
 * `approval_state: "pending"` (with a reason) unless it is inside the
 * technician's own-zone geofence with accuracy within its limit (default
 * 100 m). An unreported accuracy is flagged — so it is always sent when known.
 */

export type ClockInLocale = "bn" | "en";

/** A position fix exactly as the device reported it (no rounding, no fallback). */
export interface GpsFix {
  lat: number;
  lng: number;
  /** Accuracy radius in metres; null when the device did not report a usable one. */
  accuracyM: number | null;
  /** Epoch ms of the fix. */
  at: number;
}

/** The subset of GeolocationPosition used here (a real one is assignable). */
export interface PositionLike {
  coords: { latitude: number; longitude: number; accuracy: number };
  timestamp: number;
}

/** The subset of navigator.geolocation used here (the real object is assignable). */
export interface GeolocationLike {
  getCurrentPosition(
    success: (position: PositionLike) => void,
    error?: (failure: { code: number }) => void,
    options?: PositionOptions,
  ): void;
}

export const CLOCK_IN_FIX_TIMEOUT_MS = 20_000;

/** A FRESH high-accuracy fix: never a cached position (maximumAge 0). */
export const CLOCK_IN_GEO_OPTIONS: PositionOptions = {
  enableHighAccuracy: true,
  timeout: CLOCK_IN_FIX_TIMEOUT_MS,
  maximumAge: 0,
};

export type GeoFixErrorCode = "permission_denied" | "unavailable" | "timeout" | "unsupported";

export class GeoFixError extends Error {
  readonly code: GeoFixErrorCode;

  constructor(code: GeoFixErrorCode) {
    super(`geolocation: ${code}`);
    this.name = "GeoFixError";
    this.code = code;
  }
}

export function toGpsFix(position: PositionLike): GpsFix {
  const { latitude, longitude, accuracy } = position.coords;
  return {
    lat: latitude,
    lng: longitude,
    accuracyM: Number.isFinite(accuracy) && accuracy >= 0 ? accuracy : null,
    at: position.timestamp,
  };
}

/** Request a fresh fix; rejects with GeoFixError (GeolocationPositionError codes 1/2/3). */
export function acquireFreshFix(geolocation: GeolocationLike | null | undefined): Promise<GpsFix> {
  return new Promise((resolve, reject) => {
    if (!geolocation) {
      reject(new GeoFixError("unsupported"));
      return;
    }
    geolocation.getCurrentPosition(
      (position) => resolve(toGpsFix(position)),
      (failure) =>
        reject(
          new GeoFixError(
            failure.code === 1 ? "permission_denied" : failure.code === 3 ? "timeout" : "unavailable",
          ),
        ),
      { ...CLOCK_IN_GEO_OPTIONS },
    );
  });
}

/** Params of the online clock-in AND of the offline `clock_in` command payload (§6.5). */
export function clockInParams(fix: GpsFix, deviceRef: string): Record<string, unknown> {
  return {
    geo_lat: fix.lat,
    geo_long: fix.lng,
    ...(fix.accuracyM !== null ? { accuracy_m: fix.accuracyM } : {}),
    device_ref: deviceRef,
  };
}

/** /technician/attendance/clock_in result (also the acknowledged value of an offline clock_in). */
export interface ClockInResponse {
  clock_in?: boolean;
  already_clocked_in?: boolean;
  attendance_id?: number;
  check_in?: string;
  in_geofence?: boolean;
  distance_m?: number | null;
  geofence_result?: string;
  approval_state?: string;
  message?: string;
}

const GEOFENCE_RESULT_COPY: Record<string, { bn: string; en: string }> = {
  inside: { bn: "আপনার জোনের জিওফেন্সের ভেতরে", en: "inside your zone geofence" },
  outside: { bn: "আপনার জোনের জিওফেন্সের বাইরে", en: "outside your zone geofence" },
  no_zone: { bn: "আপনার শাখার কোনো ডিসপ্যাচ জোন নেই", en: "your branch has no dispatch zone" },
  no_geofence: { bn: "আপনার জোনে কোনো সক্রিয় জিওফেন্স নেই", en: "your zone has no active geofence" },
  low_accuracy: { bn: "জিপিএস নির্ভুলতা যথেষ্ট নয়", en: "GPS accuracy too low" },
};

export function geofenceResultText(result: string | undefined, locale: ClockInLocale): string | null {
  if (!result) return null;
  const copy = GEOFENCE_RESULT_COPY[result];
  return copy ? copy[locale] : result;
}

const PENDING_COPY = {
  en: "Clock-in recorded - pending supervisor approval",
  bn: "ক্লক-ইন রেকর্ড হয়েছে — সুপারভাইজারের অনুমোদনের অপেক্ষায়",
} as const;

/** The server's own message prefix for a flagged clock-in (technician_api.py). */
const SERVER_PENDING_PREFIX = /^Clock-in recorded - pending supervisor approval:\s*/;

export interface ClockInOutcome {
  /** "warning" for anything awaiting approval — never rendered as a plain success. */
  tone: "success" | "warning";
  pending: boolean;
  text: string;
  /** The server's reason (English, verbatim) when the clock-in is pending. */
  reason: string | null;
  geofenceResult: string | null;
}

/** What to show for a clock-in response: a pending clock-in is a warning, with its reason. */
export function describeClockIn(res: ClockInResponse, locale: ClockInLocale): ClockInOutcome {
  const pending = res.approval_state === "pending";
  const geofenceResult = res.geofence_result ?? null;

  if (res.already_clocked_in) {
    const base = locale === "bn" ? "আপনি ইতিমধ্যে ক্লক-ইন করেছেন" : res.message || "Already clocked in";
    const tail = !pending
      ? ""
      : locale === "bn"
        ? " — সেই ক্লক-ইন এখনও সুপারভাইজারের অনুমোদনের অপেক্ষায়"
        : " - that clock-in is still pending supervisor approval";
    return { tone: pending ? "warning" : "success", pending, text: base + tail, reason: null, geofenceResult };
  }

  if (pending) {
    const serverReason = res.message ? res.message.replace(SERVER_PENDING_PREFIX, "").trim() : "";
    const reason = serverReason || null;
    const label = geofenceResultText(res.geofence_result, locale);
    let text: string;
    if (locale === "en") {
      text = res.message || `${PENDING_COPY.en}: ${label ?? "no reason given"}`;
    } else {
      const detail = [label, reason ? `(${reason})` : null].filter(Boolean).join(" ");
      text = `${PENDING_COPY.bn}: ${detail || "কারণ জানানো হয়নি"}`;
    }
    return { tone: "warning", pending, text, reason, geofenceResult };
  }

  const text =
    locale === "bn"
      ? `ক্লক-ইন সফল — ${geofenceResultText(res.geofence_result ?? "inside", "bn")}`
      : res.message || "Clock-in successful (within geofence)";
  return { tone: "success", pending, text, reason: null, geofenceResult };
}

/**
 * Pending clock-ins among the commands a /technician/sync acknowledged (an
 * offline clock-in is evaluated on replay exactly like an online one).
 */
export function pendingClockInsFromSync(
  commands: readonly { command_id: string; operation: string }[],
  acknowledged: Readonly<Record<string, unknown>>,
  locale: ClockInLocale,
): { commandId: string; outcome: ClockInOutcome }[] {
  const pending: { commandId: string; outcome: ClockInOutcome }[] = [];
  for (const cmd of commands) {
    if (cmd.operation !== "clock_in" || !Object.prototype.hasOwnProperty.call(acknowledged, cmd.command_id)) {
      continue;
    }
    const value = acknowledged[cmd.command_id];
    if (typeof value !== "object" || value === null) continue;
    const outcome = describeClockIn(value as ClockInResponse, locale);
    if (outcome.pending) pending.push({ commandId: cmd.command_id, outcome });
  }
  return pending;
}

const GEO_ERROR_COPY: Record<GeoFixErrorCode, { bn: string; en: string }> = {
  permission_denied: {
    bn: "লোকেশন অনুমতি দেওয়া হয়নি — ক্লক-ইন করতে এই সাইটকে লোকেশন অ্যাক্সেস দিন।",
    en: "Location permission denied — allow location access for this site to clock in.",
  },
  unavailable: {
    bn: "আপনার অবস্থান পাওয়া যাচ্ছে না — খোলা জায়গায় যান বা জিপিএস চালু করে আবার চেষ্টা করুন।",
    en: "Your position is unavailable — move to open sky or turn on GPS, then retry.",
  },
  timeout: {
    bn: "২০ সেকেন্ডের মধ্যে জিপিএস ফিক্স পাওয়া যায়নি — আবার চেষ্টা করুন।",
    en: "No GPS fix within 20 seconds — please retry.",
  },
  unsupported: {
    bn: "এই ডিভাইস/ব্রাউজার অবস্থান দিতে পারে না (নিরাপদ HTTPS সংযোগ প্রয়োজন)।",
    en: "This device or browser cannot provide a location (a secure HTTPS connection is required).",
  },
};

export function geoFixErrorText(code: GeoFixErrorCode, locale: ClockInLocale): string {
  return GEO_ERROR_COPY[code][locale];
}
