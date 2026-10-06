import type { Metadata } from "next";
import { tokens } from "../../../../libs/ts/ui/src/tokens/tokens.generated";

export const metadata: Metadata = {
  title: "1000FiX — Corporate B2B Portal",
  description: "Estate, consolidated invoicing and service requests for corporate clients (P04).",
};

/**
 * The shell styles itself from the GENERATED R2 token emission only — no
 * hand-authored colours (CFM-01 discipline extends to app shells). Dark theme
 * arrives with the PP3 theme toggle; it will swap the token set, not values.
 */
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
