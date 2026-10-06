import { tokens } from "../../../../libs/ts/ui/src/tokens/tokens.generated";
import { uiCopy } from "../../../../libs/ts/api-client/src/ui-copy";

/** PP1 scaffold proof: renders entirely from generated tokens + copy registry. */
export default function Home() {
  return (
    <main style={{ padding: 48 }}>
      <p style={{ color: tokens["color.primary.base"], letterSpacing: "0.08em", textTransform: "uppercase", margin: 0 }}>
        {uiCopy("nav.portal.p12", "en")}
      </p>
      <h1 style={{ fontSize: tokens["typography.size.500"], margin: "16px 0 0" }}>
        {uiCopy("proto.land.mh", "en")}
      </h1>
      <p style={{ marginTop: 24, color: tokens["color.text.ink-faint"], fontSize: tokens["typography.size.200"] }}>
        PP1 scaffold — token-driven; live screens land with this portal's phase.
      </p>
    </main>
  );
}
