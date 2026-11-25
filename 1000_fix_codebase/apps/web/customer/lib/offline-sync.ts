/**
 * P02 offline-journal sync scheduling — pure helpers (no React, no I/O),
 * unit-tested by lib/offline-sync.test.mjs (`node --test`).
 *
 * Why this exists: the 30 s ticker used to call the sync from INSIDE a
 * setState updater. React may invoke an updater more than once (StrictMode in
 * development, and concurrent rendering may replay it in production), so one
 * tick could upload the same journal twice. Odoo's legacy /technician/sync
 * keeps no per-command idempotency ledger (unlike /api/v1/offline/sync), so a
 * duplicate upload re-executes commands: a second check-in attempt, a second
 * stock movement. The rules enforced here:
 * - the tick is a plain timer callback; the countdown is written as a VALUE,
 *   never as an updater with a side effect;
 * - at most one sync is in flight (single-flight), from the timer or a click;
 * - a command leaves the journal only once the server acknowledged it, and
 *   commands queued while a sync was in flight are kept.
 */

export const SYNC_PERIOD_S = 30;

/** One countdown step: the next value and whether a sync is due on this tick. */
export function advanceCountdown(
  prev: number,
  period: number = SYNC_PERIOD_S,
): { next: number; due: boolean } {
  return prev <= 1 ? { next: period, due: true } : { next: prev - 1, due: false };
}

export interface SingleFlight {
  /** Runs the task unless one is already running; resolves true when this call ran it. */
  trigger: () => Promise<boolean>;
  isRunning: () => boolean;
}

/**
 * At most one execution of `task` at a time; overlapping triggers are dropped
 * (not queued — the next tick picks up whatever is still in the journal).
 * The guard is taken synchronously, before the first await.
 */
export function singleFlight(task: () => Promise<void>): SingleFlight {
  let running = false;
  return {
    trigger: async () => {
      if (running) return false;
      running = true;
      try {
        await task();
        return true;
      } finally {
        running = false;
      }
    },
    isRunning: () => running,
  };
}

export interface SyncTickerOptions {
  /** Receives the new countdown VALUE (safe to pass straight to a state setter). */
  onCountdown: (seconds: number) => void;
  /** Checked only when a sync is due (offline simulation, auth block, empty journal). */
  shouldSync: () => boolean;
  flight: SingleFlight;
  period?: number;
}

/** The 1 s timer callback: advance the countdown and, when due, trigger ONE sync. */
export function createSyncTicker({
  onCountdown,
  shouldSync,
  flight,
  period = SYNC_PERIOD_S,
}: SyncTickerOptions): () => void {
  let countdown = period;
  return () => {
    const step = advanceCountdown(countdown, period);
    countdown = step.next;
    onCountdown(step.next);
    if (step.due && shouldSync()) void flight.trigger();
  };
}

/**
 * The journal after a sync response: drop exactly the acknowledged command ids
 * from the CURRENT journal (which may hold commands queued during the sync).
 */
export function removeAcknowledged<C extends { command_id: string }>(
  current: readonly C[],
  acknowledged: Readonly<Record<string, unknown>>,
): C[] {
  return current.filter((cmd) => !Object.prototype.hasOwnProperty.call(acknowledged, cmd.command_id));
}
