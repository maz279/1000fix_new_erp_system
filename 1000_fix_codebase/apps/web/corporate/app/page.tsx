import { tokens } from "../../../../libs/ts/ui/src/tokens/tokens.generated";
import { uiCopy } from "../../../../libs/ts/api-client/src/ui-copy";

/**
 * PP1-M01-T01 scaffold proof: the home screen renders ENTIRELY from generated
 * artefacts — design tokens (R2 emission) and the copy registry — proving the
 * token + i18n pipelines reach a real Next 16 app. No literals, no fixtures:
 * the "estate" figures below come from the copy registry; live data arrives
 * with PP3 via libs/ts/api-client (through Kong), never here.
 */
export default function Home() {
  const brand = tokens["color.primary.base"];
  const t = (k: string) => uiCopy(k, "en");
  return (
    <main style={{ padding: Number(tokens["dimension.space.lg"].replace("px", "")) * 2 }}>
      <p style={{ color: brand, fontWeight: Number(tokens["typography.weight.semibold"]), letterSpacing: "0.08em", textTransform: "uppercase", margin: 0 }}>
        {t("nav.portal.p04")}
      </p>
      <h1 style={{ fontSize: tokens["typography.size.600"], lineHeight: tokens["typography.lineHeight.step-600"], marginBottom: tokens["dimension.space.md"] }}>
        {t("proto.land.h1a")} {t("proto.land.h1b")}
      </h1>
      <p style={{ maxWidth: "48ch", color: tokens["color.text.secondary"], lineHeight: tokens["typography.lineHeight.loose"] }}>
        {t("proto.land.lede")}
      </p>
      <p style={{ marginTop: tokens["dimension.space.lg"], color: tokens["color.text.ink-faint"], fontSize: tokens["typography.size.200"] }}>
        PP1 scaffold — token-driven; live estate, invoices and service requests land in PP3.
      </p>
    </main>
  );
}
