// Unit tests for lib/clock-in.ts — run: `npm test`.
import assert from "node:assert/strict";
import { test } from "node:test";

import {
  CLOCK_IN_GEO_OPTIONS,
  GeoFixError,
  acquireFreshFix,
  clockInParams,
  describeClockIn,
  geoFixErrorText,
  pendingClockInsFromSync,
  toGpsFix,
} from "./clock-in.ts";
import { batchChecksum, canonicalJson } from "./technician.ts";

const position = (latitude, longitude, accuracy, timestamp = 1_700_000_000_000) => ({
  coords: { latitude, longitude, accuracy },
  timestamp,
});

/** A geolocation double that records the options it was asked with. */
function geolocationDouble(outcome) {
  const calls = [];
  return {
    calls,
    getCurrentPosition(success, failure, options) {
      calls.push(options);
      if (outcome.position) success(outcome.position);
      else failure({ code: outcome.errorCode });
    },
  };
}

// --- payload ---------------------------------------------------------------

test("a fresh high-accuracy fix is requested, never a cached one", async () => {
  const geo = geolocationDouble({ position: position(23.81031, 90.41249, 12.5) });
  await acquireFreshFix(geo);
  assert.equal(geo.calls.length, 1);
  assert.equal(geo.calls[0].enableHighAccuracy, true);
  assert.equal(geo.calls[0].maximumAge, 0);
  assert.ok(geo.calls[0].timeout > 0 && geo.calls[0].timeout <= 30_000);
  assert.deepEqual(geo.calls[0], CLOCK_IN_GEO_OPTIONS);
});

test("clock-in params carry geo_lat/geo_long/accuracy_m unrounded (§6.5)", async () => {
  const fix = await acquireFreshFix(geolocationDouble({ position: position(23.810312345, 90.412498765, 8.25) }));
  assert.deepEqual(clockInParams(fix, "P02-WEB-PWA"), {
    geo_lat: 23.810312345,
    geo_long: 90.412498765,
    accuracy_m: 8.25,
    device_ref: "P02-WEB-PWA",
  });
});

test("the offline clock_in payload is the same shape and survives the SP-03 digest", async () => {
  const fix = toGpsFix(position(23.8, 90.4, 140));
  const payload = clockInParams(fix, "P02-OFFLINE-SIM");
  assert.deepEqual(Object.keys(payload).sort(), ["accuracy_m", "device_ref", "geo_lat", "geo_long"]);
  assert.equal(payload.accuracy_m, 140, "a poor accuracy is still reported (the server flags it)");
  const commands = [{ command_id: "c-1", operation: "clock_in", payload }];
  assert.equal(
    canonicalJson(commands),
    '[{"command_id":"c-1","operation":"clock_in","payload":{"accuracy_m":140,"device_ref":"P02-OFFLINE-SIM","geo_lat":23.8,"geo_long":90.4}}]',
  );
  assert.match(await batchChecksum(commands), /^[0-9a-f]{64}$/);
});

test("an unusable device accuracy is omitted (never invented)", () => {
  for (const accuracy of [Number.NaN, -1, Number.POSITIVE_INFINITY]) {
    const params = clockInParams(toGpsFix(position(23.8, 90.4, accuracy)), "P02-WEB-PWA");
    assert.equal("accuracy_m" in params, false);
    assert.equal(params.geo_lat, 23.8);
  }
});

test("geolocation failures map to explicit codes - no fallback position", async () => {
  for (const [errorCode, expected] of [
    [1, "permission_denied"],
    [2, "unavailable"],
    [3, "timeout"],
  ]) {
    await assert.rejects(acquireFreshFix(geolocationDouble({ errorCode })), (err) => {
      assert.ok(err instanceof GeoFixError);
      assert.equal(err.code, expected);
      return true;
    });
  }
  await assert.rejects(acquireFreshFix(undefined), (err) => err.code === "unsupported");
  assert.match(geoFixErrorText("permission_denied", "en"), /permission denied/i);
  assert.match(geoFixErrorText("timeout", "bn"), /জিপিএস/);
});

// --- pending rendering -------------------------------------------------------

const PENDING_OUTSIDE = {
  clock_in: true,
  attendance_id: 41,
  check_in: "2026-10-22 03:00:00",
  in_geofence: false,
  distance_m: 1520.3,
  geofence_result: "outside",
  approval_state: "pending",
  message:
    "Clock-in recorded - pending supervisor approval: position outside the geofence of zone DHK-N (1520.3 m away)",
};

test("a pending clock-in renders as a warning with the server reason (en)", () => {
  const outcome = describeClockIn(PENDING_OUTSIDE, "en");
  assert.equal(outcome.tone, "warning");
  assert.equal(outcome.pending, true);
  assert.equal(outcome.text, PENDING_OUTSIDE.message, "the backend string is shown verbatim");
  assert.equal(outcome.reason, "position outside the geofence of zone DHK-N (1520.3 m away)");
  assert.equal(outcome.geofenceResult, "outside");
});

test("a pending clock-in renders as a warning in Bengali, keeping the server reason", () => {
  const outcome = describeClockIn(PENDING_OUTSIDE, "bn");
  assert.equal(outcome.tone, "warning");
  assert.match(outcome.text, /^ক্লক-ইন রেকর্ড হয়েছে — সুপারভাইজারের অনুমোদনের অপেক্ষায়: /);
  assert.match(outcome.text, /আপনার জোনের জিওফেন্সের বাইরে/);
  assert.ok(outcome.text.includes("(position outside the geofence of zone DHK-N (1520.3 m away))"));
});

test("low accuracy and a missing accuracy are pending, not success", () => {
  const low = describeClockIn(
    {
      clock_in: true,
      geofence_result: "low_accuracy",
      approval_state: "pending",
      message: "Clock-in recorded - pending supervisor approval: GPS accuracy not reported, the limit is 100 m",
    },
    "en",
  );
  assert.equal(low.tone, "warning");
  assert.equal(low.reason, "GPS accuracy not reported, the limit is 100 m");
  // no message from the server: still a pending warning, composed from the result
  const bare = describeClockIn({ clock_in: true, geofence_result: "no_zone", approval_state: "pending" }, "en");
  assert.equal(bare.tone, "warning");
  assert.equal(bare.text, "Clock-in recorded - pending supervisor approval: your branch has no dispatch zone");
});

test("an accepted clock-in is a success", () => {
  const res = {
    clock_in: true,
    geofence_result: "inside",
    approval_state: "not_required",
    distance_m: 120.4,
    message: "Clock-in successful (within geofence)",
  };
  assert.deepEqual(describeClockIn(res, "en"), {
    tone: "success",
    pending: false,
    text: "Clock-in successful (within geofence)",
    reason: null,
    geofenceResult: "inside",
  });
  assert.equal(describeClockIn(res, "bn").tone, "success");
});

test("already clocked in on a pending record keeps the warning", () => {
  const outcome = describeClockIn(
    { clock_in: true, already_clocked_in: true, approval_state: "pending", message: "Already clocked in" },
    "en",
  );
  assert.equal(outcome.tone, "warning");
  assert.equal(outcome.text, "Already clocked in - that clock-in is still pending supervisor approval");
});

test("pending offline clock-ins are surfaced from a sync acknowledgement", () => {
  const commands = [
    { command_id: "a", operation: "clock_in" },
    { command_id: "b", operation: "job_status" },
    { command_id: "c", operation: "clock_in" },
    { command_id: "d", operation: "clock_in" }, // rejected -> not acknowledged
  ];
  const acknowledged = {
    a: { ...PENDING_OUTSIDE, status: "already_applied" },
    b: { approval_state: "pending" }, // not a clock-in
    c: { clock_in: true, geofence_result: "inside", approval_state: "not_required" },
  };
  const pending = pendingClockInsFromSync(commands, acknowledged, "en");
  assert.deepEqual(
    pending.map((p) => p.commandId),
    ["a"],
  );
  assert.equal(pending[0].outcome.tone, "warning");
});
