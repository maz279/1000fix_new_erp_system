// Unit tests for lib/offline-sync.ts — run: `npm test` (node --test; Node >= 22.18
// strips the TypeScript types of the imported module natively).
import assert from "node:assert/strict";
import { test } from "node:test";

import {
  SYNC_PERIOD_S,
  advanceCountdown,
  createSyncTicker,
  removeAcknowledged,
  singleFlight,
} from "./offline-sync.ts";

const flush = () => new Promise((resolve) => setImmediate(resolve));

/**
 * Models React's development StrictMode for a state setter: an updater
 * FUNCTION is invoked twice (React does this to surface impure updaters);
 * a plain value is just stored.
 */
function strictModeSetter(initial) {
  const box = { value: initial, updaterCalls: 0 };
  box.set = (next) => {
    if (typeof next === "function") {
      box.updaterCalls += 1;
      next(box.value); // the extra, discarded invocation
      box.value = next(box.value);
    } else {
      box.value = next;
    }
  };
  return box;
}

test("advanceCountdown is due exactly once per period and wraps to the period", () => {
  let countdown = SYNC_PERIOD_S;
  let due = 0;
  for (let i = 0; i < SYNC_PERIOD_S; i += 1) {
    const step = advanceCountdown(countdown);
    countdown = step.next;
    if (step.due) due += 1;
  }
  assert.equal(due, 1);
  assert.equal(countdown, SYNC_PERIOD_S);
});

test("singleFlight runs one task at a time and drops overlapping triggers", async () => {
  let runs = 0;
  let release;
  const flight = singleFlight(async () => {
    runs += 1;
    await new Promise((resolve) => {
      release = resolve;
    });
  });
  const first = flight.trigger();
  const second = flight.trigger(); // same tick: must be dropped, guard is synchronous
  assert.equal(runs, 1);
  assert.equal(flight.isRunning(), true);
  assert.equal(await second, false);
  release();
  assert.equal(await first, true);
  assert.equal(flight.isRunning(), false);
  const third = flight.trigger(); // free again once settled
  assert.equal(runs, 2);
  release();
  assert.equal(await third, true);
});

test("singleFlight releases the guard when the task throws", async () => {
  const flight = singleFlight(async () => {
    throw new Error("network down");
  });
  await assert.rejects(flight.trigger(), /network down/);
  assert.equal(flight.isRunning(), false);
});

test("ticker under StrictMode: exactly one sync per due tick", async () => {
  const countdown = strictModeSetter(SYNC_PERIOD_S);
  let syncs = 0;
  const tick = createSyncTicker({
    onCountdown: countdown.set,
    shouldSync: () => true,
    flight: singleFlight(async () => {
      syncs += 1;
    }),
  });
  for (let second = 1; second <= 3 * SYNC_PERIOD_S; second += 1) {
    tick();
    await flush();
  }
  assert.equal(syncs, 3, "90 s = 3 due ticks = 3 syncs, never 6");
  assert.equal(countdown.updaterCalls, 0, "the ticker must write values, never updaters");
  assert.equal(countdown.value, SYNC_PERIOD_S);
});

test("control: the old side-effect-in-updater ticker syncs twice under StrictMode", () => {
  // The pre-fix page: setSyncCountdown(prev => { if (prev <= 1) { triggerSync(); return 30 } ... })
  const countdown = strictModeSetter(SYNC_PERIOD_S);
  let syncs = 0;
  const legacyTick = () =>
    countdown.set((prev) => {
      if (prev <= 1) {
        syncs += 1; // triggerSync()
        return SYNC_PERIOD_S;
      }
      return prev - 1;
    });
  for (let second = 1; second <= SYNC_PERIOD_S; second += 1) legacyTick();
  assert.equal(syncs, 2, "the harness reproduces the duplicate upload");
});

test("a sync slower than the period is never re-entered by later ticks", async () => {
  let syncs = 0;
  let release;
  const flight = singleFlight(async () => {
    syncs += 1;
    await new Promise((resolve) => {
      release = resolve;
    });
  });
  const tick = createSyncTicker({ onCountdown: () => {}, shouldSync: () => true, flight });
  for (let second = 1; second <= 3 * SYNC_PERIOD_S; second += 1) {
    tick();
    await flush();
  }
  assert.equal(syncs, 1, "still the first upload in flight after 90 s");
  release();
  await flush();
  for (let second = 1; second <= SYNC_PERIOD_S; second += 1) {
    tick();
    await flush();
  }
  assert.equal(syncs, 2, "the next due tick after completion starts one new sync");
  release();
});

test("no sync when shouldSync() is false (offline simulation, auth block, empty journal)", async () => {
  let syncs = 0;
  const tick = createSyncTicker({
    onCountdown: () => {},
    shouldSync: () => false,
    flight: singleFlight(async () => {
      syncs += 1;
    }),
  });
  for (let second = 1; second <= 2 * SYNC_PERIOD_S; second += 1) {
    tick();
    await flush();
  }
  assert.equal(syncs, 0);
});

test("removeAcknowledged drops only acknowledged ids and keeps commands queued meanwhile", () => {
  const sent = [{ command_id: "a" }, { command_id: "b" }, { command_id: "c" }];
  const current = [...sent, { command_id: "d" }]; // "d" was queued during the sync
  const acknowledged = { a: { clock_in: true }, c: { consumed: {} } }; // "b" was rejected
  assert.deepEqual(
    removeAcknowledged(current, acknowledged).map((cmd) => cmd.command_id),
    ["b", "d"],
  );
  assert.deepEqual(
    removeAcknowledged(current, {}).map((cmd) => cmd.command_id),
    ["a", "b", "c", "d"],
    "nothing acknowledged (checksum/auth refusal) -> nothing removed",
  );
  assert.deepEqual(
    removeAcknowledged([{ command_id: "toString" }], {}).map((cmd) => cmd.command_id),
    ["toString"],
    "inherited object keys are not acknowledgements",
  );
});
