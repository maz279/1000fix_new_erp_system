"use client";

/**
 * Theme Provider (PP3-M03) — dark mode + density toggles.
 *
 * Switches the `data-theme` and `data-density` attributes on <html>;
 * the generated token CSS custom properties cascade from there (the
 * dark set is `color.dark.*` in the DTCG source; the densities map to
 * `dimension.density.row-*`). No hand-authored colours — the token
 * source is the only truth (CFM-01).
 */
import { createContext, useContext, useEffect, useState } from "react";
import { tokens } from "../lib/imports";

type Theme = "light" | "dark";
type Density = "compact" | "cozy" | "relaxed";

interface ThemeContextValue {
  theme: Theme;
  density: Density;
  toggleTheme: () => void;
  setDensity: (d: Density) => void;
}

const ThemeContext = createContext<ThemeContextValue>({
  theme: "light",
  density: "cozy",
  toggleTheme: () => {},
  setDensity: () => {},
});

export function useTheme() {
  return useContext(ThemeContext);
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setTheme] = useState<Theme>("light");
  const [density, setDensityState] = useState<Density>("cozy");

  // Persist to localStorage; restore on mount
  useEffect(() => {
    const savedTheme = localStorage.getItem("fix_theme") as Theme;
    const savedDensity = localStorage.getItem("fix_density") as Density;
    if (savedTheme) setTheme(savedTheme);
    if (savedDensity) setDensityState(savedDensity);
  }, []);

  // Apply the attributes + persist
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    document.documentElement.setAttribute("data-density", density);
    localStorage.setItem("fix_theme", theme);
    localStorage.setItem("fix_density", density);
  }, [theme, density]);

  const toggleTheme = () => setTheme(theme === "light" ? "dark" : "light");
  const setDensity = (d: Density) => setDensityState(d);

  return (
    <ThemeContext.Provider value={{ theme, density, toggleTheme, setDensity }}>
      {children}
    </ThemeContext.Provider>
  );
}

/** The toggle buttons — token-driven, no hand-authored colours. */
export function ThemeToggles() {
  const { theme, density, toggleTheme, setDensity } = useTheme();
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
      <button
        onClick={toggleTheme}
        aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
        style={{
          padding: "4px 8px",
          background: tokens["color.surface.primary"],
          color: tokens["color.text.secondary"],
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-sm"],
          cursor: "pointer",
          fontSize: tokens["typography.size.200"],
        }}
      >
        {theme === "light" ? "🌙" : "☀️"}
      </button>
      <select
        value={density}
        onChange={(e) => setDensity(e.target.value as Density)}
        aria-label="Row density"
        style={{
          padding: "4px 8px",
          background: tokens["color.surface.primary"],
          color: tokens["color.text.secondary"],
          border: `1px solid ${tokens["color.border.default"]}`,
          borderRadius: tokens["dimension.border.radius-sm"],
          fontSize: tokens["typography.size.200"],
        }}
      >
        <option value="compact">Compact</option>
        <option value="cozy">Cozy</option>
        <option value="relaxed">Relaxed</option>
      </select>
    </div>
  );
}
