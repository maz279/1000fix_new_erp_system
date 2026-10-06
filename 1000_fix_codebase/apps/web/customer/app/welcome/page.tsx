"use client";

/* P01 public landing — the shared marketing shell (PP5): 12 portal
 * cards + 10 journey strips from the generated landing artefact,
 * bilingual with a Bengali default (DE-17). This is the portal's
 * public face before login; / is the signed-in home. */
import { LandingShell } from "../../lib/imports";

export default function LandingPage() {
  return <LandingShell portalId="P01" />;
}
