"use client";

/**
 * P02: Technician Mobile App (PWA & Field Workbench).
 * 
 * 100% wired live to Odoo 19 via /technician/* routes (AS-09/P-11/FF-39).
 * Zero mock fixtures, zero fake telemetry.
 * 
 * Capabilities:
 * 1. Day Queue: 200–400 day queue work order management, SLA countdown, job state transitions.
 * 2. Geofenced Clock-In: GPS distance validation against Dhaka Circle geofence, shift timer.
 * 3. Diagnostic Trees: Interactive symptom traversal, terminal fault code attachment.
 * 4. Van Stock Scan-Consume: Barcode scan/lookup, par-level inventory, work order parts consumption.
 * 5. 24h Offline Mode & 30s Sync: SP-07 command journal replay, batch checksum verification.
 * 
 * Dual Language (বাংলা ⇄ English), Design Token Purity (CFM-01), WCAG 2.2 AA.
 */

import { useState, useEffect, useCallback, useId, useRef, useTransition } from "react";
import { tokens, ApiError } from "../../lib/imports";
import { callOdooAsTechnician } from "../../lib/api";
import {
  batchChecksum,
  isTechnicianAuthError,
  withoutImpersonationParams,
  type TechnicianAuthErrorCode,
} from "../../lib/technician";
import {
  SYNC_PERIOD_S,
  createSyncTicker,
  removeAcknowledged,
  singleFlight,
} from "../../lib/offline-sync";
import {
  GeoFixError,
  acquireFreshFix,
  clockInParams,
  describeClockIn,
  geoFixErrorText,
  geofenceResultText,
  pendingClockInsFromSync,
  type ClockInResponse,
  type GeoFixErrorCode,
  type GpsFix,
} from "../../lib/clock-in";
import { useLanguage } from "../../components/language";
import { StaffOnly } from "../../components/staff-only";

// R01 re-audit 2026-10-22: every /technician/* call goes through
// callOdooAsTechnician (same-origin relay + server-side bearer key, gated on
// the caller's Odoo session since 2026-10-23). The technician is resolved by
// Odoo from the authenticated key's user only — this page never sends
// employee_id / technician_id.

/** Bilingual explanation for the refusals that mean "you cannot act as a technician here". */
const TECHNICIAN_AUTH_COPY: Record<TechnicianAuthErrorCode, { bn: string; en: string }> = {
  unauthenticated: {
    bn: "টেকনিশিয়ান হিসেবে সাইন-ইন প্রয়োজন — আপনার ওডু টেকনিশিয়ান অ্যাকাউন্ট দিয়ে লগইন করুন।",
    en: "Technician sign-in required — sign in with your Odoo technician account.",
  },
  not_internal_user: {
    bn: "এই অ্যাকাউন্টটি কর্মী (ইন্টার্নাল) অ্যাকাউন্ট নয় — টেকনিশিয়ান অ্যাক্সেসের জন্য কর্মী অ্যাকাউন্ট প্রয়োজন।",
    en: "This account is not an internal (employee) account — technician access requires one.",
  },
  session_user_mismatch: {
    bn: "এই পোর্টাল অন্য একজন টেকনিশিয়ানের জন্য কনফিগার করা — আপনার অ্যাকাউন্ট দিয়ে এখানে কাজ করা যাবে না। অ্যাডমিনের সাথে যোগাযোগ করুন।",
    en: "This portal is configured for a different technician — your account cannot act here. Contact your administrator.",
  },
  no_employee: {
    bn: "এই অ্যাকাউন্টের সাথে কোনো টেকনিশিয়ান (কর্মী) রেকর্ড যুক্ত নেই। আপনার ইউজারকে HR কর্মী প্রোফাইলের সাথে যুক্ত করতে অ্যাডমিনকে বলুন।",
    en: "This account is not linked to a technician (employee) record. Ask an administrator to link your user to your HR employee profile.",
  },
  forbidden: {
    bn: "অনুমতি নেই — অনুরোধটি অন্য একজন টেকনিশিয়ানের নামে ছিল। আপনি কেবল নিজের কাজ পরিচালনা করতে পারেন।",
    en: "Access denied — the request named a different technician. You can only act on your own jobs.",
  },
  technician_auth_not_configured: {
    bn: "এই সার্ভারে টেকনিশিয়ান অ্যাক্সেস কনফিগার করা হয়নি (API কী সেট নেই)। অ্যাডমিনের সাথে যোগাযোগ করুন।",
    en: "Technician access is not configured on this server (FIX_TECHNICIAN_API_KEY is not set). Contact your administrator.",
  },
  technician_auth_rejected: {
    bn: "সার্ভার এই পোর্টালের টেকনিশিয়ান ক্রেডেনশিয়াল প্রত্যাখ্যান করেছে (API কী অবৈধ, বাতিল বা মেয়াদোত্তীর্ণ)। অ্যাডমিনের সাথে যোগাযোগ করুন।",
    en: "The server rejected this portal's technician credentials (API key invalid, revoked or expired). Contact your administrator.",
  },
};

// --- Types ---
interface TechnicianProfile {
  id: number;
  name: string;
  user_id: number | null;
  active_shift: boolean;
  last_clock_in: string | null;
  status: "on_duty" | "off_duty";
  // The technician's OWN zone geofence (circle: lat/lng/radius_m; polygon: points)
  geofence: {
    id: number;
    name: string;
    type: string;
    geometry: { lat?: number; lng?: number; radius_m?: number; points?: [number, number][] };
  } | null;
}

interface WorkOrder {
  id: number;
  name: string;
  sequence: number;
  state: "draft" | "assigned" | "in_progress" | "completed" | "failed";
  start_time: string;
  end_time: string;
  duration_hours: number;
  diagnosed_fault_code: string;
  diagnostic_tree_id: number | null;
  diagnostic_tree_name: string;
  notes: string;
  parts_consumed: {
    id: number;
    product_id: number;
    product_name: string;
    quantity: number;
    unit_cost_bdt: string;
  }[];
  service_order: {
    id: number;
    ref: string;
    state: string;
    priority: string;
    fault_description: string;
    customer_name: string;
    customer_phone: string;
    device: string;
    branch: string;
    sla_deadline: string;
  };
}

interface DiagnosticTree {
  id: number;
  code: string;
  name: string;
  is_terminal: boolean;
  children: {
    id: number;
    code: string;
    name: string;
    is_terminal: boolean;
    fault_code: string;
    recommended_action: string;
  }[];
}

interface VanPart {
  id: number;
  default_code: string;
  barcode: string;
  name: string;
  list_price_bdt: string;
  stock_qty: number;
}

interface OfflineCommand {
  command_id: string;
  operation: "clock_in" | "clock_out" | "job_status" | "diagnose" | "consume_part";
  timestamp: string;
  payload: Record<string, unknown>;
  summary: string;
}

function TechnicianPortalContent() {
  const { locale } = useLanguage();
  const isBn = locale === "bn";

  // Tab State: 'queue' | 'attendance' | 'diagnostics' | 'vanstock' | 'offline'
  const [activeTab, setActiveTab] = useState<"queue" | "attendance" | "diagnostics" | "vanstock" | "offline">("queue");

  // Core Data
  const [technician, setTechnician] = useState<TechnicianProfile | null>(null);
  const [queue, setQueue] = useState<WorkOrder[]>([]);
  const [selectedWoId, setSelectedWoId] = useState<number | null>(null);
  const [trees, setTrees] = useState<DiagnosticTree[]>([]);
  const [vanStock, setVanStock] = useState<VanPart[]>([]);

  // UI / Status States
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  // Set when Odoo / the relay refuses the technician identity itself
  // (unauthenticated, no_employee, forbidden, key missing/rejected).
  const [authBlock, setAuthBlock] = useState<TechnicianAuthErrorCode | null>(null);
  const [isPending, startTransition] = useTransition();

  // Attendance (M55 AUT-WFM-02): the device's real fix only — no fallback
  // position. Odoo evaluates it against the technician's own zone geofence.
  const [gpsFix, setGpsFix] = useState<GpsFix | null>(null);
  const [gpsError, setGpsError] = useState<GeoFixErrorCode | null>(null);
  const [locating, setLocating] = useState<boolean>(false);
  const [lastClockIn, setLastClockIn] = useState<ClockInResponse | null>(null);
  // Recorded-but-flagged outcomes (pending supervisor approval) — never a plain success.
  const [warningMsg, setWarningMsg] = useState<string | null>(null);

  // Diagnostic Form
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [selectedChildNode, setSelectedChildNode] = useState<{
    id: number;
    code: string;
    fault_code: string;
    action: string;
  } | null>(null);
  const [diagNotes, setDiagNotes] = useState<string>("");

  // Van Stock Consumption Form
  const [scanInput, setScanInput] = useState<string>("");
  const [consumeQty, setConsumeQty] = useState<number>(1);

  // Offline Journal & 30s Sync
  const [isOfflineSimulated, setIsOfflineSimulated] = useState<boolean>(false);
  const [journal, setJournal] = useState<OfflineCommand[]>([]);
  // Source of truth for async code (sync, queueing): always the latest journal,
  // never a stale render closure. `journal` state only drives rendering.
  const journalRef = useRef<OfflineCommand[]>([]);
  const [syncCountdown, setSyncCountdown] = useState<number>(SYNC_PERIOD_S);
  const [lastSyncResult, setLastSyncResult] = useState<{
    token?: string;
    checksum?: string;
    ack_count?: number;
    rej_count?: number;
    at?: string;
  } | null>(null);

  // Load offline journal from localStorage on mount. Journals saved before the
  // R01 fix carry employee_id (the removed demo fallback) — strip it, Odoo
  // would refuse those commands with `forbidden`.
  useEffect(() => {
    try {
      const stored = localStorage.getItem("fix_tech_offline_journal");
      if (stored) {
        const parsed = JSON.parse(stored) as OfflineCommand[];
        const cleaned = parsed.map((cmd) => ({
          ...cmd,
          payload: withoutImpersonationParams(cmd.payload ?? {}),
        }));
        journalRef.current = cleaned;
        setJournal(cleaned);
      }
    } catch {
      // ignore
    }
  }, []);

  // Route a failed technician call to the right banner: identity refusals
  // block the workbench (authBlock); anything else is a normal error message.
  const reportError = useCallback((err: unknown, fallback: string) => {
    if (err instanceof ApiError && isTechnicianAuthError(err.code)) {
      setAuthBlock(err.code);
      setErrorMsg(null);
      return;
    }
    setErrorMsg((err as Error)?.message || fallback);
  }, []);

  // Save journal whenever updated (ref first: async readers see it immediately)
  const saveJournal = (commands: OfflineCommand[]) => {
    journalRef.current = commands;
    setJournal(commands);
    try {
      localStorage.setItem("fix_tech_offline_journal", JSON.stringify(commands));
    } catch {
      // ignore
    }
  };

  // Queue a command for offline replay
  const queueOfflineCommand = (
    op: OfflineCommand["operation"],
    payload: Record<string, unknown>,
    summary: string
  ) => {
    const current = journalRef.current;
    const cmd: OfflineCommand = {
      // SP-01: client-generated UUIDv4 (secure context); timestamp-based fallback
      command_id: globalThis.crypto?.randomUUID?.() ?? `CMD-${Date.now()}-${current.length + 1}`,
      operation: op,
      timestamp: new Date().toLocaleTimeString(),
      payload,
      summary,
    };
    saveJournal([...current, cmd]);
    setSuccessMsg(
      isBn
        ? `অফলাইন জার্নালে সংরক্ষিত (${cmd.command_id}) — পুনঃসংযোগে স্বয়ংক্রিয়ভাবে সিঙ্ক হবে`
        : `Queued in offline journal (${cmd.command_id}) — will sync automatically upon connection.`
    );
  };

  // Load Initial Data
  const refreshAll = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const [meRes, queueRes, treesRes, stockRes] = await Promise.all([
        callOdooAsTechnician<{ technician?: TechnicianProfile }>("/technician/auth/me"),
        callOdooAsTechnician<{ queue?: WorkOrder[] }>("/technician/queue"),
        callOdooAsTechnician<{ trees?: DiagnosticTree[] }>("/technician/diagnostics/tree"),
        callOdooAsTechnician<{ van_stock?: VanPart[] }>("/technician/van-stock"),
      ]);

      setAuthBlock(null);
      if (meRes.technician) setTechnician(meRes.technician);
      if (queueRes.queue) {
        setQueue(queueRes.queue);
        if (!selectedWoId && queueRes.queue.length > 0) {
          setSelectedWoId(queueRes.queue[0].id);
        }
      }
      if (treesRes.trees) {
        setTrees(treesRes.trees);
        if (treesRes.trees.length > 0 && !selectedCategory) {
          setSelectedCategory(treesRes.trees[0].id);
        }
      }
      if (stockRes.van_stock) setVanStock(stockRes.van_stock);
    } catch (err: unknown) {
      if (err instanceof ApiError && isTechnicianAuthError(err.code)) {
        // Never keep showing a previous identity's data after a refusal.
        setTechnician(null);
        setQueue([]);
        setVanStock([]);
      }
      reportError(err, "Failed to fetch technician data");
    } finally {
      setLoading(false);
    }
  }, [selectedWoId, selectedCategory, reportError]);

  useEffect(() => {
    refreshAll();
  }, [refreshAll]);

  // Real GPS acquisition (display only — every clock-in requests its own fresh fix)
  useEffect(() => {
    let active = true;
    acquireFreshFix(typeof navigator !== "undefined" ? navigator.geolocation : undefined)
      .then((fix) => {
        if (active) setGpsFix(fix);
      })
      .catch((err: unknown) => {
        if (active) setGpsError(err instanceof GeoFixError ? err.code : "unavailable");
      });
    return () => {
      active = false;
    };
  }, []);

  /** A fresh high-accuracy fix for a clock-in; null (with a message) when there is none. */
  const locateForClockIn = async (): Promise<GpsFix | null> => {
    setLocating(true);
    try {
      const fix = await acquireFreshFix(typeof navigator !== "undefined" ? navigator.geolocation : undefined);
      setGpsFix(fix);
      setGpsError(null);
      return fix;
    } catch (err: unknown) {
      const code = err instanceof GeoFixError ? err.code : "unavailable";
      setGpsError(code);
      setErrorMsg(geoFixErrorText(code, isBn ? "bn" : "en"));
      return null;
    } finally {
      setLocating(false);
    }
  };

  // Execute Sync Batch — only ever invoked through `syncFlight` (single-flight):
  // /technician/sync keeps no per-command idempotency ledger, so an overlapping
  // or repeated upload would execute the same commands twice.
  const runSync = async () => {
    const batch = journalRef.current;
    if (batch.length === 0) {
      setSuccessMsg(isBn ? "সিঙ্ক করার মতো কোনো অফলাইন নির্দেশ নেই (সব সিঙ্কড)" : "No offline commands to sync.");
      return;
    }
    setErrorMsg(null);
    try {
      // SP-03: the digest is computed over exactly the array that is sent;
      // Odoo rejects the whole batch (nothing executed) on a missing/mismatching one.
      const commands = batch.map((cmd) => ({ ...cmd, payload: withoutImpersonationParams(cmd.payload) }));
      const batch_checksum = await batchChecksum(commands);
      const res = await callOdooAsTechnician<{
        sync?: {
          acknowledged: Record<string, unknown>;
          rejected: Record<string, string>;
          checksum: string;
          token: string;
          ack_count: number;
          rej_count: number;
        };
      }>("/technician/sync", {
        commands,
        batch_checksum,
        last_token: lastSyncResult?.token || "",
      });

      if (res.sync) {
        setLastSyncResult({
          token: res.sync.token,
          checksum: res.sync.checksum,
          ack_count: res.sync.ack_count,
          rej_count: res.sync.rej_count,
          at: new Date().toLocaleTimeString(),
        });

        // Drop ONLY acknowledged commands, from the CURRENT journal: commands
        // queued while this sync was in flight must survive.
        saveJournal(removeAcknowledged(journalRef.current, res.sync.acknowledged));

        // Offline clock-ins are evaluated on replay like online ones: surface
        // any that were recorded pending supervisor approval.
        const pendingClockIns = pendingClockInsFromSync(commands, res.sync.acknowledged, isBn ? "bn" : "en");
        setWarningMsg(
          pendingClockIns.length > 0
            ? pendingClockIns.map(({ outcome }) => outcome.text).join(" | ")
            : null,
        );

        setSuccessMsg(
          isBn
            ? `সিঙ্ক সফল! ${res.sync.ack_count}টি নির্দেশ কার্যকর হয়েছে (চেকসাম: ${res.sync.checksum})`
            : `Sync completed: ${res.sync.ack_count} commands processed (Checksum: ${res.sync.checksum}).`
        );
        refreshAll();
      }
    } catch (err: unknown) {
      reportError(err, "Sync failed");
    }
  };

  // Latest-render closures for the long-lived timer (refreshed after every
  // render; never written during render).
  const runSyncRef = useRef(runSync);
  const autoSyncAllowedRef = useRef<() => boolean>(() => false);
  useEffect(() => {
    runSyncRef.current = runSync;
    // Not while simulating offline, nor while the technician identity is
    // refused (it would only fail again), nor with nothing to upload.
    autoSyncAllowedRef.current = () =>
      !isOfflineSimulated && !authBlock && journalRef.current.length > 0;
  });

  // One single-flight guard for the component's lifetime, shared by the timer
  // and the "Sync now" button (useState initializer: created once and kept
  // across StrictMode effect re-runs).
  const [syncFlight] = useState(() => singleFlight(() => runSyncRef.current()));

  const syncNow = async () => {
    const ran = await syncFlight.trigger();
    if (!ran) {
      setSuccessMsg(isBn ? "সিঙ্ক ইতিমধ্যে চলছে…" : "A sync is already in progress…");
    }
  };

  // 30s Auto-Sync Countdown Ticker. The side effect lives in the timer
  // callback, NOT in a setState updater: React may call an updater twice
  // (StrictMode, concurrent rendering), which used to upload the journal twice.
  useEffect(() => {
    const tick = createSyncTicker({
      onCountdown: setSyncCountdown,
      shouldSync: () => autoSyncAllowedRef.current(),
      flight: syncFlight,
    });
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, [syncFlight]);

  // --- Handlers ---

  // 1. Attendance Clock-In
  const handleClockIn = async () => {
    setErrorMsg(null);
    setSuccessMsg(null);
    setWarningMsg(null);
    // §6.5: geo_lat/geo_long/accuracy_m from a FRESH fix, online and offline alike
    // (an unreported accuracy is flagged for supervisor approval by Odoo).
    const fix = await locateForClockIn();
    if (!fix) return;

    if (isOfflineSimulated) {
      const accuracy = fix.accuracyM !== null ? ` ±${Math.round(fix.accuracyM)} m` : "";
      queueOfflineCommand(
        "clock_in",
        clockInParams(fix, "P02-OFFLINE-SIM"),
        `Clock-In @ (${fix.lat.toFixed(5)}, ${fix.lng.toFixed(5)})${accuracy}`
      );
      return;
    }

    try {
      const res = await callOdooAsTechnician<ClockInResponse>(
        "/technician/attendance/clock_in",
        clockInParams(fix, "P02-WEB-PWA"),
      );

      // Recorded either way; pending approval is a warning with its reason, not a success.
      const outcome = describeClockIn(res, isBn ? "bn" : "en");
      setLastClockIn(res);
      if (outcome.tone === "warning") setWarningMsg(outcome.text);
      else setSuccessMsg(outcome.text);
      refreshAll();
    } catch (err: unknown) {
      reportError(err, "Clock-in failed");
    }
  };

  // 2. Attendance Clock-Out
  const handleClockOut = async () => {
    setErrorMsg(null);
    setSuccessMsg(null);
    if (isOfflineSimulated) {
      queueOfflineCommand("clock_out", {}, `Clock-Out Shift End`);
      return;
    }

    try {
      const res = await callOdooAsTechnician<{ clock_out?: boolean; worked_hours?: number; message?: string }>(
        "/technician/attendance/clock_out"
      );
      setSuccessMsg(
        isBn
          ? `শিফট সমাপ্ত! মোট কার্যকাল: ${res.worked_hours || 0} ঘণ্টা`
          : `Shift ended! Total worked hours: ${res.worked_hours || 0} hrs`
      );
      refreshAll();
    } catch (err: unknown) {
      reportError(err, "Clock-out failed");
    }
  };

  // 3. Work Order State Change (Start / Complete)
  const handleJobAction = async (woId: number, action: "start" | "complete") => {
    setErrorMsg(null);
    setSuccessMsg(null);
    if (isOfflineSimulated) {
      queueOfflineCommand(
        "job_status",
        { work_order_id: woId, action },
        `Job ${action} on WO #${woId}`
      );
      return;
    }

    try {
      await callOdooAsTechnician("/technician/job/status", { work_order_id: woId, action });
      setSuccessMsg(
        isBn
          ? `কাজের অবস্থা আপডেট হয়েছে: ${action === "start" ? "চলমান" : "সম্পন্ন"}`
          : `Job status updated: ${action === "start" ? "In Progress" : "Completed"}`
      );
      refreshAll();
    } catch (err: unknown) {
      reportError(err, "Failed to update job status");
    }
  };

  // 4. Submit Diagnosis
  const handleDiagnosticSubmit = async () => {
    if (!selectedWoId) {
      setErrorMsg(isBn ? "প্রথমে একটি ওয়ার্ক অর্ডার নির্বাচন করুন" : "Please select a work order first");
      return;
    }
    if (!selectedChildNode) {
      setErrorMsg(isBn ? "একটি ত্রুটির লক্ষণ বা নোড নির্বাচন করুন" : "Please select a symptom / fault code");
      return;
    }

    setErrorMsg(null);
    setSuccessMsg(null);

    const payload = {
      work_order_id: selectedWoId,
      node_id: selectedChildNode.id,
      fault_code: selectedChildNode.fault_code,
      notes: diagNotes.trim(),
    };

    if (isOfflineSimulated) {
      queueOfflineCommand("diagnose", payload, `Diagnosis on WO #${selectedWoId}: ${selectedChildNode.fault_code}`);
      setDiagNotes("");
      setSelectedChildNode(null);
      return;
    }

    try {
      await callOdooAsTechnician("/technician/diagnostics/submit", payload);
      setSuccessMsg(
        isBn
          ? `ডায়াগনস্টিক ত্রুটি কোড (${selectedChildNode.fault_code}) সফলভাবে সংযুক্ত হয়েছে!`
          : `Diagnostic fault code (${selectedChildNode.fault_code}) attached successfully!`
      );
      setDiagNotes("");
      setSelectedChildNode(null);
      refreshAll();
    } catch (err: unknown) {
      reportError(err, "Failed to submit diagnosis");
    }
  };

  // 5. Consume Van Stock Part
  const handleConsumePart = async (partIdentifier: string) => {
    if (!selectedWoId) {
      setErrorMsg(isBn ? "ওয়ার্ক অর্ডার নির্বাচন করুন" : "Please select a work order first");
      return;
    }
    if (!partIdentifier.trim()) {
      setErrorMsg(isBn ? "পার্ট কোড বা বারকোড দিন" : "Please enter a part code or barcode");
      return;
    }

    setErrorMsg(null);
    setSuccessMsg(null);

    const payload = {
      work_order_id: selectedWoId,
      barcode_or_code: partIdentifier.trim(),
      quantity: consumeQty,
    };

    if (isOfflineSimulated) {
      queueOfflineCommand("consume_part", payload, `Consume ${consumeQty}x ${partIdentifier} for WO #${selectedWoId}`);
      setScanInput("");
      return;
    }

    try {
      const res = await callOdooAsTechnician<{ consumed?: { product_name: string; line_total_bdt: string } }>(
        "/technician/van-stock/consume",
        payload
      );
      setSuccessMsg(
        isBn
          ? `পার্ট ব্যবহার নিশ্চিত: ${res.consumed?.product_name || partIdentifier} (${consumeQty}টি) — ৳ ${res.consumed?.line_total_bdt}`
          : `Part consumed: ${res.consumed?.product_name || partIdentifier} (${consumeQty}x) — BDT ${res.consumed?.line_total_bdt}`
      );
      setScanInput("");
      refreshAll();
    } catch (err: unknown) {
      reportError(err, "Failed to consume van stock part");
    }
  };

  const selectedWo = queue.find((w) => w.id === selectedWoId) || queue[0];
  const activeTree = trees.find((t) => t.id === selectedCategory) || trees[0];

  const queueInputId = useId();
  const scanInputId = useId();
  const notesInputId = useId();

  return (
    <main
      style={{
        padding: "24px 20px",
        maxWidth: 1040,
        margin: "0 auto",
        color: tokens["color.text.primary"],
      }}
    >
      {/* --- Top Technician Header Card --- */}
      <section
        style={{
          background: tokens["color.surface.primary"],
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-md"],
          padding: "20px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 16,
          boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 28 }}>🛠️</span>
            <div>
              <h1
                style={{
                  margin: 0,
                  fontSize: tokens["typography.size.400"],
                  color: tokens["color.primary.base"],
                  fontWeight: Number(tokens["typography.weight.bold"]),
                }}
              >
                {isBn ? "টেকনিশিয়ান মোবাইল পোর্টাল (P02)" : "Technician Mobile Portal (P02)"}
              </h1>
              <p
                style={{
                  margin: "4px 0 0",
                  fontSize: tokens["typography.size.100"],
                  color: tokens["color.text.secondary"],
                }}
              >
                {isBn
                  ? "ফিল্ড ও ওয়ার্কশপ টেকনিশিয়ান ওয়ার্কবেঞ্চ — ২০০-৪০০ দৈনিক কিউ | অফলাইন ২৪ ঘণ্টা | জিওফেন্সড"
                  : "Field & Workshop Workbench — 200–400 Day Queue | 24h Offline Sync | Geofenced"}
              </p>
            </div>
          </div>
        </div>

        {/* Technician Profile & Duty Badge */}
        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
          <div
            style={{
              padding: "6px 14px",
              borderRadius: tokens["dimension.border.radius-pill"],
              background: technician?.active_shift
                ? tokens["color.status.success-bg"]
                : tokens["color.surface.secondary"],
              color: technician?.active_shift
                ? tokens["color.status.success"]
                : tokens["color.text.secondary"],
              fontWeight: 600,
              fontSize: tokens["typography.size.100"],
              display: "flex",
              alignItems: "center",
              gap: 6,
            }}
          >
            <span
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: technician?.active_shift
                  ? tokens["color.status.success"]
                  : tokens["color.text.secondary"],
              }}
            />
            {technician?.name || (isBn ? "টেকনিশিয়ান সংযুক্ত নয়" : "No technician signed in")} (
            {technician?.active_shift
              ? isBn
                ? "অন ডিউটি"
                : "ON DUTY"
              : isBn
              ? "অফ ডিউটি"
              : "OFF DUTY"}
            )
          </div>

          {/* Offline Simulation Switch */}
          <button
            type="button"
            onClick={() => setIsOfflineSimulated(!isOfflineSimulated)}
            style={{
              padding: "6px 12px",
              borderRadius: tokens["dimension.border.radius-sm"],
              border: `1px solid ${isOfflineSimulated ? tokens["color.status.warning"] : tokens["color.border.default"]}`,
              background: isOfflineSimulated
                ? tokens["color.status.warning-bg"]
                : tokens["color.surface.secondary"],
              color: isOfflineSimulated ? tokens["color.status.warning"] : tokens["color.text.primary"],
              fontSize: tokens["typography.size.100"],
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {isOfflineSimulated
              ? isBn
                ? "📶 সিমুলেটেড অফলাইন (সক্রিয়)"
                : "📶 Offline Sim (Active)"
              : isBn
              ? "🌐 অনলাইন মোড"
              : "🌐 Online Mode"}
          </button>
        </div>
      </section>

      {/* --- Feedback Banners --- */}
      {authBlock && (
        <div
          role="alert"
          aria-live="assertive"
          style={{
            marginTop: 16,
            padding: "14px 16px",
            borderRadius: tokens["dimension.border.radius-sm"],
            border: `1px solid ${tokens["color.status.error"]}`,
            background: tokens["color.status.error-bg"],
            color: tokens["color.status.error"],
            fontSize: tokens["typography.size.200"],
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 12,
            flexWrap: "wrap",
          }}
        >
          <span>
            <strong>{isBn ? "টেকনিশিয়ান অ্যাক্সেস বন্ধ" : "Technician access blocked"}</strong>
            {" — "}
            {isBn ? TECHNICIAN_AUTH_COPY[authBlock].bn : TECHNICIAN_AUTH_COPY[authBlock].en}
            <span style={{ display: "block", marginTop: 4, fontSize: tokens["typography.size.100"] }}>
              {isBn ? "কোড:" : "Code:"} {authBlock}
            </span>
          </span>
          <button
            type="button"
            onClick={() => refreshAll()}
            style={{
              padding: "6px 12px",
              borderRadius: tokens["dimension.border.radius-sm"],
              border: `1px solid ${tokens["color.status.error"]}`,
              background: "transparent",
              color: "inherit",
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            {isBn ? "আবার চেষ্টা করুন" : "Retry"}
          </button>
        </div>
      )}

      {errorMsg && (
        <div
          role="alert"
          style={{
            marginTop: 16,
            padding: "12px 16px",
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.status.error-bg"],
            color: tokens["color.status.error"],
            fontSize: tokens["typography.size.200"],
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span>⚠️ {errorMsg}</span>
          <button
            type="button"
            onClick={() => setErrorMsg(null)}
            style={{ background: "transparent", border: "none", cursor: "pointer", color: "inherit" }}
          >
            ✕
          </button>
        </div>
      )}

      {warningMsg && (
        <div
          role="status"
          aria-live="polite"
          style={{
            marginTop: 16,
            padding: "12px 16px",
            borderRadius: tokens["dimension.border.radius-sm"],
            border: `1px solid ${tokens["color.status.warning"]}`,
            background: tokens["color.status.warning-bg"],
            color: tokens["color.status.warning"],
            fontSize: tokens["typography.size.200"],
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 12,
          }}
        >
          <span>⏳ {warningMsg}</span>
          <button
            type="button"
            aria-label={isBn ? "বার্তা বন্ধ করুন" : "Dismiss message"}
            onClick={() => setWarningMsg(null)}
            style={{ background: "transparent", border: "none", cursor: "pointer", color: "inherit" }}
          >
            ✕
          </button>
        </div>
      )}

      {successMsg && (
        <div
          role="status"
          style={{
            marginTop: 16,
            padding: "12px 16px",
            borderRadius: tokens["dimension.border.radius-sm"],
            background: tokens["color.status.success-bg"],
            color: tokens["color.status.success"],
            fontSize: tokens["typography.size.200"],
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <span>✓ {successMsg}</span>
          <button
            type="button"
            onClick={() => setSuccessMsg(null)}
            style={{ background: "transparent", border: "none", cursor: "pointer", color: "inherit" }}
          >
            ✕
          </button>
        </div>
      )}

      {/* --- Mobile Tab Navigation (WCAG Tablist) --- */}
      <div
        role="tablist"
        aria-label="Technician workbench modules"
        style={{
          display: "flex",
          gap: 8,
          marginTop: 20,
          borderBottom: `2px solid ${tokens["color.border.default"]}`,
          overflowX: "auto",
          paddingBottom: 4,
        }}
      >
        {[
          { id: "queue", icon: "📋", labelBn: `দৈনিক কিউ (${queue.length})`, labelEn: `Day Queue (${queue.length})` },
          { id: "attendance", icon: "📍", labelBn: "জিওফেন্স হাজিরা", labelEn: "Geofence Clock-In" },
          { id: "diagnostics", icon: "🔬", labelBn: "ডায়াগনস্টিক ট্রিস", labelEn: "Diagnostic Trees" },
          { id: "vanstock", icon: "📦", labelBn: "ভ্যান স্টক স্ক্যান", labelEn: "Van Stock Scan" },
          {
            id: "offline",
            icon: "🔄",
            labelBn: `অফলাইন সিঙ্ক (${journal.length})`,
            labelEn: `Offline Sync (${journal.length})`,
          },
        ].map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              role="tab"
              aria-selected={isActive}
              aria-controls={`panel-${tab.id}`}
              id={`tab-${tab.id}`}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              style={{
                padding: "10px 16px",
                border: "none",
                background: isActive ? tokens["color.primary.base"] : tokens["color.surface.secondary"],
                color: isActive ? tokens["color.text.inverse"] : tokens["color.text.secondary"],
                borderRadius: `${tokens["dimension.border.radius-sm"]} ${tokens["dimension.border.radius-sm"]} 0 0`,
                fontSize: tokens["typography.size.200"],
                fontWeight: isActive ? 700 : 500,
                cursor: "pointer",
                whiteSpace: "nowrap",
                display: "flex",
                alignItems: "center",
                gap: 6,
                transition: "all 0.2s ease",
              }}
            >
              <span>{tab.icon}</span>
              <span>{isBn ? tab.labelBn : tab.labelEn}</span>
            </button>
          );
        })}
      </div>

      {/* =========================================================================
          TAB 1: DAY QUEUE (200-400 Day Queue Work Orders)
      ========================================================================= */}
      {activeTab === "queue" && (
        <section
          id="panel-queue"
          role="tabpanel"
          aria-labelledby="tab-queue"
          style={{ marginTop: 20 }}
        >
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: 16,
              flexWrap: "wrap",
              gap: 12,
            }}
          >
            <div>
              <h2 style={{ margin: 0, fontSize: tokens["typography.size.300"], color: tokens["color.primary.base"] }}>
                {isBn ? "দৈনিক কার্যতালিকা ও অর্ডার কিউ" : "Daily Assignment Queue"}
              </h2>
              <p style={{ margin: "2px 0 0", fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                {isBn
                  ? `মোট ${queue.length}টি ওয়ার্ক অর্ডার অর্পিত রয়েছে | অগ্রাধিকার ও এসএলএ অনুসরণে কাজ পরিচালনা করুন`
                  : `${queue.length} assigned work orders | Prioritized dispatch with SLA tracking`}
              </p>
            </div>
            <button
              type="button"
              onClick={refreshAll}
              style={{
                padding: "8px 14px",
                background: tokens["color.surface.secondary"],
                border: `1px solid ${tokens["color.border.default"]}`,
                borderRadius: tokens["dimension.border.radius-sm"],
                cursor: "pointer",
                fontSize: tokens["typography.size.100"],
                fontWeight: 600,
              }}
            >
              ↻ {isBn ? "রিফ্রেশ কিউ" : "Refresh Queue"}
            </button>
          </div>

          {queue.length === 0 ? (
            <div
              style={{
                padding: 40,
                textAlign: "center",
                background: tokens["color.surface.primary"],
                borderRadius: tokens["dimension.border.radius-md"],
                border: `1px solid ${tokens["color.border.default"]}`,
              }}
            >
              <p style={{ color: tokens["color.text.secondary"], margin: 0 }}>
                {isBn ? "বর্তমানে কোনো কাজের অর্ডার কিউতে নেই।" : "No work orders currently assigned."}
              </p>
            </div>
          ) : (
            <div style={{ display: "grid", gap: 14 }}>
              {queue.map((wo) => {
                const isSelected = selectedWoId === wo.id;
                const so = wo.service_order;
                return (
                  <div
                    key={wo.id}
                    style={{
                      background: tokens["color.surface.primary"],
                      border: `2px solid ${isSelected ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
                      borderRadius: tokens["dimension.border.radius-md"],
                      padding: 18,
                      boxShadow: isSelected ? "0 4px 12px rgba(10,126,122,0.12)" : "none",
                      transition: "all 0.2s ease",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "flex-start",
                        flexWrap: "wrap",
                        gap: 10,
                      }}
                    >
                      <div>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                          <span
                            style={{
                              background: tokens["color.surface.secondary"],
                              padding: "2px 8px",
                              borderRadius: 4,
                              fontWeight: 700,
                              fontSize: tokens["typography.size.100"],
                            }}
                          >
                            #{wo.sequence} {wo.name}
                          </span>
                          <strong style={{ fontSize: tokens["typography.size.200"], color: tokens["color.primary.base"] }}>
                            SO: {so.ref}
                          </strong>
                          <span
                            style={{
                              background:
                                so.priority === "urgent"
                                  ? tokens["color.status.error-bg"]
                                  : so.priority === "high"
                                  ? tokens["color.status.warning-bg"]
                                  : tokens["color.status.info-bg"],
                              color:
                                so.priority === "urgent"
                                  ? tokens["color.status.error"]
                                  : so.priority === "high"
                                  ? tokens["color.status.warning"]
                                  : tokens["color.status.info"],
                              padding: "2px 8px",
                              borderRadius: tokens["dimension.border.radius-pill"],
                              fontSize: tokens["typography.size.100"],
                              fontWeight: 700,
                              textTransform: "uppercase",
                            }}
                          >
                            {so.priority}
                          </span>
                          <span
                            style={{
                              padding: "2px 8px",
                              borderRadius: tokens["dimension.border.radius-pill"],
                              background:
                                wo.state === "in_progress"
                                  ? tokens["color.primary.base"]
                                  : wo.state === "completed"
                                  ? tokens["color.status.success-bg"]
                                  : tokens["color.surface.secondary"],
                              color:
                                wo.state === "in_progress"
                                  ? tokens["color.text.inverse"]
                                  : wo.state === "completed"
                                  ? tokens["color.status.success"]
                                  : tokens["color.text.secondary"],
                              fontSize: tokens["typography.size.100"],
                              fontWeight: 600,
                            }}
                          >
                            {wo.state}
                          </span>
                        </div>

                        <div style={{ marginTop: 8, fontSize: tokens["typography.size.200"] }}>
                          <strong>{so.device}</strong> — 👤 {so.customer_name} ({so.customer_phone || "N/A"})
                        </div>
                        <div
                          style={{
                            marginTop: 4,
                            fontSize: tokens["typography.size.100"],
                            color: tokens["color.text.secondary"],
                          }}
                        >
                          📌 {isBn ? "ত্রুটির বিবরণ:" : "Fault:"} {so.fault_description || "Standard inspection"}
                        </div>
                        {wo.diagnosed_fault_code && (
                          <div
                            style={{
                              marginTop: 4,
                              fontSize: tokens["typography.size.100"],
                              color: tokens["color.status.info"],
                              fontWeight: 600,
                            }}
                          >
                            🔬 {isBn ? "নির্ণীত ফল্ট কোড:" : "Fault Code:"} {wo.diagnosed_fault_code}
                          </div>
                        )}
                        {wo.parts_consumed.length > 0 && (
                          <div
                            style={{
                              marginTop: 4,
                              fontSize: tokens["typography.size.100"],
                              color: tokens["color.primary.base"],
                            }}
                          >
                            📦 {isBn ? "ব্যবহৃত যন্ত্রাংশ:" : "Consumed Parts:"}{" "}
                            {wo.parts_consumed.map((p) => `${p.product_name} (${p.quantity}টি)`).join(", ")}
                          </div>
                        )}
                      </div>

                      {/* Action buttons */}
                      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedWoId(wo.id);
                            setActiveTab("diagnostics");
                          }}
                          style={{
                            padding: "6px 12px",
                            background: tokens["color.surface.secondary"],
                            color: tokens["color.text.primary"],
                            border: `1px solid ${tokens["color.border.default"]}`,
                            borderRadius: tokens["dimension.border.radius-sm"],
                            fontSize: tokens["typography.size.100"],
                            cursor: "pointer",
                          }}
                        >
                          🔬 {isBn ? "ডায়াগনস্টিক" : "Diagnose"}
                        </button>

                        <button
                          type="button"
                          onClick={() => {
                            setSelectedWoId(wo.id);
                            setActiveTab("vanstock");
                          }}
                          style={{
                            padding: "6px 12px",
                            background: tokens["color.surface.secondary"],
                            color: tokens["color.text.primary"],
                            border: `1px solid ${tokens["color.border.default"]}`,
                            borderRadius: tokens["dimension.border.radius-sm"],
                            fontSize: tokens["typography.size.100"],
                            cursor: "pointer",
                          }}
                        >
                          📦 {isBn ? "পার্টস স্ক্যান" : "Parts"}
                        </button>

                        {wo.state !== "in_progress" && wo.state !== "completed" && (
                          <button
                            type="button"
                            onClick={() => handleJobAction(wo.id, "start")}
                            style={{
                              padding: "6px 14px",
                              background: tokens["color.primary.base"],
                              color: tokens["color.text.inverse"],
                              border: "none",
                              borderRadius: tokens["dimension.border.radius-sm"],
                              fontSize: tokens["typography.size.100"],
                              fontWeight: 600,
                              cursor: "pointer",
                            }}
                          >
                            ▶ {isBn ? "কাজ শুরু" : "Start Job"}
                          </button>
                        )}

                        {wo.state === "in_progress" && (
                          <button
                            type="button"
                            onClick={() => handleJobAction(wo.id, "complete")}
                            style={{
                              padding: "6px 14px",
                              background: tokens["color.status.success"],
                              color: tokens["color.text.inverse"],
                              border: "none",
                              borderRadius: tokens["dimension.border.radius-sm"],
                              fontSize: tokens["typography.size.100"],
                              fontWeight: 600,
                              cursor: "pointer",
                            }}
                          >
                            ✓ {isBn ? "কাজ সম্পন্ন" : "Complete"}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      )}

      {/* =========================================================================
          TAB 2: GEOFENCED ATTENDANCE (Clock-In / Clock-Out)
      ========================================================================= */}
      {activeTab === "attendance" && (
        <section
          id="panel-attendance"
          role="tabpanel"
          aria-labelledby="tab-attendance"
          style={{ marginTop: 20 }}
        >
          <div
            style={{
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              padding: 24,
            }}
          >
            <h2 style={{ margin: "0 0 8px", fontSize: tokens["typography.size.300"], color: tokens["color.primary.base"] }}>
              {isBn ? "জিওফেন্সড উপস্থিতি ও শিফট নিয়ন্ত্রণ" : "Geofenced Mobile Clock-In & Shift Control"}
            </h2>
            <p style={{ margin: "0 0 20px", fontSize: tokens["typography.size.200"], color: tokens["color.text.secondary"] }}>
              {isBn
                ? "প্রতিটি ক্লক-ইনে নতুন জিপিএস ফিক্স (অবস্থান ও নির্ভুলতা) পাঠানো হয়। সার্ভার আপনার জোনের জিওফেন্সের সাথে যাচাই করে উপস্থিতি রেকর্ড করে; জোনের বাইরে বা নির্ভুলতা সীমার (ডিফল্ট ১০০ মি) বেশি হলে তা সুপারভাইজারের অনুমোদনের জন্য অপেক্ষমান থাকে।"
                : "Each clock-in sends a fresh GPS fix (position and accuracy). The server records it against your own zone's geofence; outside the fence or less accurate than its limit (default 100 m), the clock-in is recorded pending supervisor approval."}
            </p>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
                gap: 16,
                marginBottom: 20,
              }}
            >
              {/* Geofence Zone Card */}
              <div
                style={{
                  padding: 16,
                  background: tokens["color.surface.secondary"],
                  borderRadius: tokens["dimension.border.radius-sm"],
                  border: `1px solid ${tokens["color.border.default"]}`,
                }}
              >
                <span style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                  {isBn ? "সক্রিয় জিওফেন্স জোন" : "Active Geofence Zone"}
                </span>
                <div style={{ marginTop: 4, fontWeight: 700, fontSize: tokens["typography.size.200"] }}>
                  📍 {technician?.geofence?.name ?? (isBn ? "আপনার জোনে কোনো জিওফেন্স নেই" : "No geofence for your zone")}
                </div>
                <div style={{ marginTop: 4, fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                  {(() => {
                    const geometry = technician?.geofence?.geometry;
                    if (geometry?.points) {
                      return isBn
                        ? `বহুভুজ সীমানা (${geometry.points.length}টি বিন্দু)`
                        : `Polygon boundary (${geometry.points.length} points)`;
                    }
                    if (geometry?.lat !== undefined && geometry.lng !== undefined) {
                      return `${isBn ? "কেন্দ্র:" : "Center:"} ${geometry.lat}° N, ${geometry.lng}° E | ${isBn ? "ব্যাসার্ধ:" : "Radius:"} ${geometry.radius_m ?? "—"} m`;
                    }
                    return isBn
                      ? "জোন বা জিওফেন্স ছাড়া প্রতিটি ক্লক-ইন অনুমোদনের অপেক্ষায় রেকর্ড হবে"
                      : "Without a zone geofence every clock-in is recorded pending approval";
                  })()}
                </div>
              </div>

              {/* Technician Device GPS Card */}
              <div
                style={{
                  padding: 16,
                  background: tokens["color.surface.secondary"],
                  borderRadius: tokens["dimension.border.radius-sm"],
                  border: `1px solid ${tokens["color.border.default"]}`,
                }}
              >
                <span style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                  {isBn ? "ডিভাইসের বর্তমান জিপিএস স্থানাঙ্ক" : "Device Current GPS Position"}
                </span>
                <div style={{ marginTop: 4, fontWeight: 700, fontSize: tokens["typography.size.200"] }}>
                  🛰️{" "}
                  {gpsFix
                    ? `${gpsFix.lat.toFixed(5)}° N, ${gpsFix.lng.toFixed(5)}° E`
                    : locating
                      ? isBn ? "অবস্থান নির্ণয় করা হচ্ছে…" : "Locating…"
                      : isBn ? "এখনও কোনো জিপিএস ফিক্স নেই" : "No GPS fix yet"}
                </div>
                <div
                  style={{
                    marginTop: 4,
                    fontSize: tokens["typography.size.100"],
                    color: gpsError ? tokens["color.status.error"] : tokens["color.text.secondary"],
                  }}
                >
                  {gpsError
                    ? geoFixErrorText(gpsError, isBn ? "bn" : "en")
                    : gpsFix
                      ? `${isBn ? "নির্ভুলতা:" : "Accuracy (m):"} ${gpsFix.accuracyM !== null ? `±${Math.round(gpsFix.accuracyM)} m` : isBn ? "জানানো হয়নি" : "n/a"} · ${new Date(gpsFix.at).toLocaleTimeString()}`
                      : isBn ? "ক্লক-ইন করার সময় নতুন ফিক্স নেওয়া হবে" : "A fresh fix is taken on clock-in"}
                </div>
              </div>
            </div>

            {/* Attendance Buttons */}
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
              {!technician?.active_shift ? (
                <button
                  type="button"
                  onClick={handleClockIn}
                  disabled={locating}
                  aria-busy={locating}
                  style={{
                    padding: "12px 24px",
                    background: tokens["color.primary.base"],
                    color: tokens["color.text.inverse"],
                    border: "none",
                    borderRadius: tokens["dimension.border.radius-sm"],
                    fontSize: tokens["typography.size.200"],
                    fontWeight: 700,
                    cursor: locating ? "wait" : "pointer",
                    opacity: locating ? 0.7 : 1,
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                  }}
                >
                  🟢{" "}
                  {locating
                    ? isBn ? "জিপিএস ফিক্স নেওয়া হচ্ছে…" : "Getting GPS fix…"
                    : isBn ? "শিফট শুরু করুন (ক্লক-ইন)" : "Clock-In Shift"}
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleClockOut}
                  style={{
                    padding: "12px 24px",
                    background: tokens["color.status.error"],
                    color: tokens["color.text.inverse"],
                    border: "none",
                    borderRadius: tokens["dimension.border.radius-sm"],
                    fontSize: tokens["typography.size.200"],
                    fontWeight: 700,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                  }}
                >
                  🔴 {isBn ? "শিফট শেষ করুন (ক্লক-আউট)" : "Clock-Out Shift"}
                </button>
              )}

              {technician?.last_clock_in && (
                <span style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                  {isBn ? "সর্বশেষ ক্লক-ইন:" : "Last Clock-In:"} {technician.last_clock_in}
                </span>
              )}
            </div>

            {/* Result of this session's clock-in (M55 AUT-WFM-02): pending approval is a warning */}
            {lastClockIn &&
              (() => {
                const outcome = describeClockIn(lastClockIn, isBn ? "bn" : "en");
                const tone = outcome.tone === "warning" ? "warning" : "success";
                return (
                  <div
                    role="status"
                    data-approval-state={lastClockIn.approval_state ?? ""}
                    style={{
                      marginTop: 16,
                      padding: "12px 16px",
                      borderRadius: tokens["dimension.border.radius-sm"],
                      border: `1px solid ${tokens[`color.status.${tone}`]}`,
                      background: tokens[`color.status.${tone}-bg`],
                      color: tokens[`color.status.${tone}`],
                      fontSize: tokens["typography.size.100"],
                    }}
                  >
                    <strong>
                      {outcome.pending
                        ? isBn ? "⏳ রেকর্ড হয়েছে — সুপারভাইজারের অনুমোদনের অপেক্ষায়" : "⏳ Recorded — pending supervisor approval"
                        : isBn ? "✓ ক্লক-ইন গৃহীত" : "✓ Clock-in accepted"}
                    </strong>
                    {outcome.geofenceResult && (
                      <span> · {geofenceResultText(outcome.geofenceResult, isBn ? "bn" : "en")}</span>
                    )}
                    {typeof lastClockIn.distance_m === "number" && lastClockIn.geofence_result === "outside" && (
                      <span>
                        {" "}· {isBn ? "দূরত্ব:" : "distance:"} {lastClockIn.distance_m} m
                      </span>
                    )}
                    {/* pending: the server's reason (the headline already says "pending") */}
                    <div style={{ marginTop: 4 }}>
                      {outcome.pending
                        ? `${isBn ? "কারণ:" : "Reason:"} ${outcome.reason ?? geofenceResultText(outcome.geofenceResult ?? undefined, isBn ? "bn" : "en") ?? "—"}`
                        : outcome.text}
                    </div>
                  </div>
                );
              })()}
          </div>
        </section>
      )}

      {/* =========================================================================
          TAB 3: DIAGNOSTIC DECISION TREES & FAULT CODING
      ========================================================================= */}
      {activeTab === "diagnostics" && (
        <section
          id="panel-diagnostics"
          role="tabpanel"
          aria-labelledby="tab-diagnostics"
          style={{ marginTop: 20 }}
        >
          <div
            style={{
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              padding: 24,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
              <div>
                <h2 style={{ margin: 0, fontSize: tokens["typography.size.300"], color: tokens["color.primary.base"] }}>
                  {isBn ? "ডায়াগনস্টিক ডিসিশন ট্রিস ও ফল্ট কোডিং" : "Diagnostic Decision Trees & Fault Coding"}
                </h2>
                <p style={{ margin: "4px 0 0", fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                  {isBn
                    ? "শাখাগত উপসর্গ বাছাই করে টার্মিনাল ত্রুটি কোড সংযুক্ত করুন"
                    : "Traverse symptom branches to attach verified terminal fault codes to work orders"}
                </p>
              </div>

              {/* Work Order Target Selector */}
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <label htmlFor={queueInputId} style={{ fontSize: tokens["typography.size.100"], fontWeight: 600 }}>
                  {isBn ? "অর্ডার লক্ষ্য:" : "Target WO:"}
                </label>
                <select
                  id={queueInputId}
                  value={selectedWoId || ""}
                  onChange={(e) => setSelectedWoId(Number(e.target.value))}
                  style={{
                    padding: "6px 12px",
                    background: tokens["color.surface.canvas"],
                    border: `1px solid ${tokens["color.border.default"]}`,
                    borderRadius: tokens["dimension.border.radius-sm"],
                    fontSize: tokens["typography.size.100"],
                    color: tokens["color.text.primary"],
                  }}
                >
                  {queue.map((w) => (
                    <option key={w.id} value={w.id}>
                      {w.name} — {w.service_order.device}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            {/* Diagnostic Categories Navigation */}
            <div
              style={{
                display: "flex",
                gap: 8,
                marginTop: 20,
                borderBottom: `1px solid ${tokens["color.border.default"]}`,
                paddingBottom: 8,
                overflowX: "auto",
              }}
            >
              {trees.map((t) => {
                const isCatActive = selectedCategory === t.id;
                return (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => {
                      setSelectedCategory(t.id);
                      setSelectedChildNode(null);
                    }}
                    style={{
                      padding: "8px 14px",
                      borderRadius: tokens["dimension.border.radius-sm"],
                      border: `1px solid ${isCatActive ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
                      background: isCatActive ? tokens["color.primary.base"] : tokens["color.surface.secondary"],
                      color: isCatActive ? tokens["color.text.inverse"] : tokens["color.text.primary"],
                      fontSize: tokens["typography.size.100"],
                      fontWeight: isCatActive ? 700 : 500,
                      cursor: "pointer",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {t.name}
                  </button>
                );
              })}
            </div>

            {/* Tree Nodes & Symptoms */}
            {activeTree && (
              <div style={{ marginTop: 20 }}>
                <h3 style={{ margin: "0 0 12px", fontSize: tokens["typography.size.200"], color: tokens["color.primary.base"] }}>
                  🔍 {activeTree.code} — {activeTree.name}
                </h3>

                <div style={{ display: "grid", gap: 10 }}>
                  {activeTree.children.map((child) => {
                    const isNodeSelected = selectedChildNode?.id === child.id;
                    return (
                      <div
                        key={child.id}
                        onClick={() =>
                          setSelectedChildNode({
                            id: child.id,
                            code: child.code,
                            fault_code: child.fault_code,
                            action: child.recommended_action,
                          })
                        }
                        style={{
                          padding: 14,
                          borderRadius: tokens["dimension.border.radius-sm"],
                          border: `2px solid ${isNodeSelected ? tokens["color.primary.base"] : tokens["color.border.default"]}`,
                          background: isNodeSelected
                            ? tokens["color.surface.secondary"]
                            : tokens["color.surface.primary"],
                          cursor: "pointer",
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          gap: 12,
                          transition: "all 0.15s ease",
                        }}
                      >
                        <div>
                          <strong style={{ fontSize: tokens["typography.size.200"], display: "block" }}>
                            {child.name}
                          </strong>
                          <span
                            style={{
                              fontSize: tokens["typography.size.100"],
                              color: tokens["color.status.info"],
                              fontWeight: 600,
                              display: "inline-block",
                              marginTop: 2,
                            }}
                          >
                            🏷️ {child.fault_code}
                          </span>
                          <p style={{ margin: "4px 0 0", fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                            ⚙️ {isBn ? "প্রস্তাবিত পদক্ষেপ:" : "Action:"} {child.recommended_action}
                          </p>
                        </div>
                        <span style={{ fontSize: 18, color: tokens["color.primary.base"] }}>
                          {isNodeSelected ? "✓" : "→"}
                        </span>
                      </div>
                    );
                  })}
                </div>

                {/* Submit Diagnostic Action */}
                {selectedChildNode && (
                  <div
                    style={{
                      marginTop: 20,
                      padding: 16,
                      background: tokens["color.surface.secondary"],
                      borderRadius: tokens["dimension.border.radius-sm"],
                      border: `1px solid ${tokens["color.primary.base"]}`,
                    }}
                  >
                    <div style={{ fontWeight: 700, fontSize: tokens["typography.size.200"], color: tokens["color.primary.base"] }}>
                      {isBn ? "নিশ্চিতকৃত ডায়াগনসিস:" : "Confirmed Diagnosis:"} {selectedChildNode.fault_code}
                    </div>
                    <div style={{ marginTop: 10 }}>
                      <label htmlFor={notesInputId} style={{ display: "block", fontSize: tokens["typography.size.100"], fontWeight: 600 }}>
                        {isBn ? "টেকনিশিয়ান নোট ও মাল্টিমিটার ফলাফল:" : "Technician Notes & Bench Readings:"}
                      </label>
                      <input
                        id={notesInputId}
                        type="text"
                        value={diagNotes}
                        onChange={(e) => setDiagNotes(e.target.value)}
                        placeholder={
                          isBn
                            ? "যেমন: ব্যাটারি টার্মিনাল ভোল্টেজ ২.৮V (মানক ৩.৭V এর নিচে)"
                            : "e.g. Battery terminal voltage 2.8V below nominal"
                        }
                        style={{
                          width: "100%",
                          boxSizing: "border-box",
                          padding: 8,
                          marginTop: 4,
                          borderRadius: tokens["dimension.border.radius-sm"],
                          border: `1px solid ${tokens["color.border.default"]}`,
                          fontSize: tokens["typography.size.100"],
                          background: tokens["color.surface.canvas"],
                          color: tokens["color.text.primary"],
                        }}
                      />
                    </div>
                    <div style={{ marginTop: 12, display: "flex", justifyContent: "flex-end" }}>
                      <button
                        type="button"
                        onClick={handleDiagnosticSubmit}
                        style={{
                          padding: "8px 18px",
                          background: tokens["color.primary.base"],
                          color: tokens["color.text.inverse"],
                          border: "none",
                          borderRadius: tokens["dimension.border.radius-sm"],
                          fontSize: tokens["typography.size.100"],
                          fontWeight: 700,
                          cursor: "pointer",
                        }}
                      >
                        ✓ {isBn ? "ওয়ার্ক অর্ডারে ফল্ট কোড যোগ করুন" : "Attach Fault Code to Work Order"}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </section>
      )}

      {/* =========================================================================
          TAB 4: VAN STOCK SCAN & CONSUME
      ========================================================================= */}
      {activeTab === "vanstock" && (
        <section
          id="panel-vanstock"
          role="tabpanel"
          aria-labelledby="tab-vanstock"
          style={{ marginTop: 20 }}
        >
          <div
            style={{
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              padding: 24,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
              <div>
                <h2 style={{ margin: 0, fontSize: tokens["typography.size.300"], color: tokens["color.primary.base"] }}>
                  {isBn ? "ভ্যান স্টক ইনভেন্টরি ও স্ক্যান-কনজিউম" : "Van Stock Inventory & Scan-to-Consume"}
                </h2>
                <p style={{ margin: "4px 0 0", fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                  {isBn
                    ? "বারকোড স্ক্যান করে সরাসরি ওয়ার্ক অর্ডারে যন্ত্রাংশ ব্যবহার রেকর্ড করুন"
                    : "Scan barcodes or select catalogue OEM parts to record consumption on active work order"}
                </p>
              </div>

              {/* Target WO Indicator */}
              <div
                style={{
                  background: tokens["color.surface.secondary"],
                  padding: "6px 14px",
                  borderRadius: tokens["dimension.border.radius-pill"],
                  fontSize: tokens["typography.size.100"],
                  fontWeight: 600,
                }}
              >
                WO: {selectedWo?.name || "N/A"} ({selectedWo?.service_order.device || "No device"})
              </div>
            </div>

            {/* Quick Barcode Scanner / Code Input */}
            <div
              style={{
                marginTop: 20,
                padding: 16,
                background: tokens["color.surface.secondary"],
                borderRadius: tokens["dimension.border.radius-sm"],
                border: `1px solid ${tokens["color.border.default"]}`,
                display: "flex",
                gap: 10,
                flexWrap: "wrap",
                alignItems: "flex-end",
              }}
            >
              <div style={{ flex: 1, minWidth: 220 }}>
                <label htmlFor={scanInputId} style={{ display: "block", fontSize: tokens["typography.size.100"], fontWeight: 600 }}>
                  📷 {isBn ? "বারকোড বা পার্ট কোড স্ক্যান:" : "Barcode or Part Code:"}
                </label>
                <input
                  id={scanInputId}
                  type="text"
                  value={scanInput}
                  onChange={(e) => setScanInput(e.target.value)}
                  placeholder="e.g. PART-BAT-S24 or scan barcode"
                  style={{
                    width: "100%",
                    boxSizing: "border-box",
                    padding: 8,
                    marginTop: 4,
                    borderRadius: tokens["dimension.border.radius-sm"],
                    border: `1px solid ${tokens["color.border.default"]}`,
                    fontSize: tokens["typography.size.200"],
                    background: tokens["color.surface.canvas"],
                    color: tokens["color.text.primary"],
                  }}
                />
              </div>

              <div>
                <label style={{ display: "block", fontSize: tokens["typography.size.100"], fontWeight: 600 }}>
                  {isBn ? "পরিমাণ:" : "Qty:"}
                </label>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={consumeQty}
                  onChange={(e) => setConsumeQty(Number(e.target.value))}
                  style={{
                    width: 70,
                    boxSizing: "border-box",
                    padding: 8,
                    marginTop: 4,
                    borderRadius: tokens["dimension.border.radius-sm"],
                    border: `1px solid ${tokens["color.border.default"]}`,
                    fontSize: tokens["typography.size.200"],
                    background: tokens["color.surface.canvas"],
                    color: tokens["color.text.primary"],
                  }}
                />
              </div>

              <button
                type="button"
                onClick={() => handleConsumePart(scanInput)}
                style={{
                  padding: "8px 18px",
                  background: tokens["color.primary.base"],
                  color: tokens["color.text.inverse"],
                  border: "none",
                  borderRadius: tokens["dimension.border.radius-sm"],
                  fontSize: tokens["typography.size.200"],
                  fontWeight: 700,
                  cursor: "pointer",
                  height: 40,
                }}
              >
                + {isBn ? "কনজিউম রেকর্ড" : "Consume"}
              </button>
            </div>

            {/* Allocated Van Stock Catalog */}
            <h3 style={{ margin: "24px 0 12px", fontSize: tokens["typography.size.200"], color: tokens["color.primary.base"] }}>
              📦 {isBn ? "ভ্যানে মজুদকৃত যন্ত্রাংশের তালিকা" : "Allocated Van Inventory"}
            </h3>

            <div style={{ display: "grid", gap: 10 }}>
              {vanStock.map((part) => (
                <div
                  key={part.id}
                  style={{
                    padding: 14,
                    borderRadius: tokens["dimension.border.radius-sm"],
                    border: `1px solid ${tokens["color.border.default"]}`,
                    background: tokens["color.surface.primary"],
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    flexWrap: "wrap",
                    gap: 10,
                  }}
                >
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <strong style={{ fontSize: tokens["typography.size.200"] }}>{part.name}</strong>
                      <span
                        style={{
                          background: tokens["color.surface.secondary"],
                          padding: "2px 6px",
                          borderRadius: 4,
                          fontSize: tokens["typography.size.100"],
                          fontWeight: 600,
                        }}
                      >
                        {part.default_code}
                      </span>
                    </div>
                    <div style={{ marginTop: 4, fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                      🏷️ {isBn ? "মূল্য:" : "Price:"} ৳ {part.list_price_bdt} | {isBn ? "ভ্যান স্টক:" : "Van Stock:"}{" "}
                      <strong style={{ color: tokens["color.status.success"] }}>{part.stock_qty} pcs</strong>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleConsumePart(part.default_code)}
                    style={{
                      padding: "6px 14px",
                      background: tokens["color.surface.secondary"],
                      color: tokens["color.primary.base"],
                      border: `1px solid ${tokens["color.primary.base"]}`,
                      borderRadius: tokens["dimension.border.radius-sm"],
                      fontSize: tokens["typography.size.100"],
                      fontWeight: 700,
                      cursor: "pointer",
                    }}
                  >
                    + {isBn ? "১টি ব্যবহার করুন" : "Consume 1"}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* =========================================================================
          TAB 5: 24H OFFLINE MODE & 30S SYNC (SP-07 Journal Replay)
      ========================================================================= */}
      {activeTab === "offline" && (
        <section
          id="panel-offline"
          role="tabpanel"
          aria-labelledby="tab-offline"
          style={{ marginTop: 20 }}
        >
          <div
            style={{
              background: tokens["color.surface.primary"],
              border: `1px solid ${tokens["color.border.default"]}`,
              borderRadius: tokens["dimension.border.radius-md"],
              padding: 24,
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
              <div>
                <h2 style={{ margin: 0, fontSize: tokens["typography.size.300"], color: tokens["color.primary.base"] }}>
                  {isBn ? "এসপি-০৭ অফলাইন জার্নাল ও ৩০ সেকেন্ড অটো-সিঙ্ক" : "SP-07 Offline Journal & 30s Auto-Sync"}
                </h2>
                <p style={{ margin: "4px 0 0", fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                  {isBn
                    ? "নেটওয়ার্ক বিচ্ছিন্ন থাকলেও ২৪ ঘণ্টা পর্যন্ত অফলাইন অপারেশন সক্ষম | প্রতি ৩০ সেকেন্ডে স্বয়ংক্রিয় সিঙ্ক"
                    : "Supports 24h disconnected field work with 30s automated background upload and SHA-256 verification"}
                </p>
              </div>

              <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                <span
                  style={{
                    background: tokens["color.surface.secondary"],
                    padding: "6px 12px",
                    borderRadius: tokens["dimension.border.radius-pill"],
                    fontSize: tokens["typography.size.100"],
                    fontWeight: 700,
                  }}
                >
                  ⏱️ {isBn ? `সিঙ্ক কাউন্টডাউন: ${syncCountdown} সে` : `Next Sync: ${syncCountdown}s`}
                </span>
                <button
                  type="button"
                  onClick={() => void syncNow()}
                  style={{
                    padding: "8px 16px",
                    background: tokens["color.primary.base"],
                    color: tokens["color.text.inverse"],
                    border: "none",
                    borderRadius: tokens["dimension.border.radius-sm"],
                    fontSize: tokens["typography.size.100"],
                    fontWeight: 700,
                    cursor: "pointer",
                  }}
                >
                  ⚡ {isBn ? "এখনই সিঙ্ক চালান" : "Force Sync Now"}
                </button>
              </div>
            </div>

            {/* Sync Audit Status Card */}
            {lastSyncResult && (
              <div
                style={{
                  marginTop: 16,
                  padding: 16,
                  borderRadius: tokens["dimension.border.radius-sm"],
                  background: tokens["color.surface.secondary"],
                  border: `1px solid ${tokens["color.border.default"]}`,
                  fontSize: tokens["typography.size.100"],
                }}
              >
                <div style={{ fontWeight: 700, color: tokens["color.primary.base"] }}>
                  ✓ {isBn ? "সর্বশেষ সিঙ্ক অডিট রসিদ:" : "Last Sync Audit Receipt:"}
                </div>
                <div style={{ marginTop: 6, display: "flex", gap: 16, flexWrap: "wrap" }}>
                  <span>
                    <strong>{isBn ? "সময়:" : "Timestamp:"}</strong> {lastSyncResult.at}
                  </span>
                  <span>
                    <strong>{isBn ? "কার্যকর:" : "Acknowledged:"}</strong> {lastSyncResult.ack_count} cmds
                  </span>
                  <span>
                    <strong>{isBn ? "চেকসাম:" : "SHA-256 Checksum:"}</strong> {lastSyncResult.checksum}
                  </span>
                  <span>
                    <strong>{isBn ? "টোকেন:" : "Delta Token:"}</strong> {lastSyncResult.token}
                  </span>
                </div>
              </div>
            )}

            {/* Pending Journal Queue */}
            <h3 style={{ margin: "24px 0 12px", fontSize: tokens["typography.size.200"], color: tokens["color.primary.base"] }}>
              ⏳ {isBn ? `অপেক্ষমান অফলাইন নির্দেশমালা (${journal.length}টি)` : `Pending Offline Queue (${journal.length} cmds)`}
            </h3>

            {journal.length === 0 ? (
              <div
                style={{
                  padding: 24,
                  textAlign: "center",
                  background: tokens["color.surface.secondary"],
                  borderRadius: tokens["dimension.border.radius-sm"],
                }}
              >
                <p style={{ margin: 0, color: tokens["color.status.success"], fontWeight: 600 }}>
                  ✓ {isBn ? "সব নির্দেশাবলী সার্ভারের সাথে সিঙ্ক সম্পন্ন!" : "All commands synchronized with ERP backend."}
                </p>
              </div>
            ) : (
              <div style={{ display: "grid", gap: 10 }}>
                {journal.map((cmd) => (
                  <div
                    key={cmd.command_id}
                    style={{
                      padding: 12,
                      borderRadius: tokens["dimension.border.radius-sm"],
                      border: `1px solid ${tokens["color.border.default"]}`,
                      background: tokens["color.surface.primary"],
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      gap: 12,
                    }}
                  >
                    <div>
                      <strong style={{ fontSize: tokens["typography.size.100"] }}>{cmd.summary}</strong>
                      <div style={{ fontSize: tokens["typography.size.100"], color: tokens["color.text.secondary"] }}>
                        ID: {cmd.command_id} | {cmd.timestamp} | Op: {cmd.operation}
                      </div>
                    </div>
                    <span
                      style={{
                        padding: "2px 8px",
                        background: tokens["color.status.warning-bg"],
                        color: tokens["color.status.warning"],
                        borderRadius: tokens["dimension.border.radius-pill"],
                        fontSize: tokens["typography.size.100"],
                        fontWeight: 700,
                      }}
                    >
                      PENDING
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      )}
    </main>
  );
}

export default function TechnicianPortalPage() {
  return (
    <StaffOnly>
      <TechnicianPortalContent />
    </StaffOnly>
  );
}
