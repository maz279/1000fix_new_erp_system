import type { Metadata } from "next";
import { tokens } from "../../../../libs/ts/ui/src/tokens/tokens.generated";

export const metadata: Metadata = {
  title: "1000FiX — Brand",
  description: "brand portal (R2) — PP1 scaffold",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body
        style={{
          margin: 0,
          background: tokens["color.surface.canvas"],
          color: tokens["color.text.primary"],
          fontFamily: `${tokens["typography.font.latin.family"]}, ${tokens["typography.font.latin.fallback"]}`,
        }}
      >
        {children}
      </body>
    </html>
  );
}
