"use client";

/**
 * Brand scope for the signed-in partner user.
 *
 * The server resolves the brands from the authenticated user
 * (/brand/portal/session); the portal never asks for a raw brand id. A user
 * linked to several brands gets a selector; every API call sends the chosen
 * id, which Odoo still validates against the user's own brands.
 */
import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";
import { callOdoo } from "../lib/api";
import { useAuth } from "./auth-gate";
import { selectStyle } from "./ui";

export interface BrandRef {
  id: number;
  name: string;
  code: string;
}

interface BrandContextValue {
  ready: boolean;
  error: string | null;
  brands: BrandRef[];
  brandId: number | null;
  brand: BrandRef | null;
  selectBrand: (id: number) => void;
  reload: () => Promise<void>;
}

const BrandContext = createContext<BrandContextValue>({
  ready: false,
  error: null,
  brands: [],
  brandId: null,
  brand: null,
  selectBrand: () => {},
  reload: async () => {},
});

export function useBrand() {
  return useContext(BrandContext);
}

const STORAGE_KEY = "fix_brand_id";

export function BrandProvider({ children }: { children: ReactNode }) {
  const { status } = useAuth();
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [brands, setBrands] = useState<BrandRef[]>([]);
  const [brandId, setBrandId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setReady(false);
    setError(null);
    try {
      const d = await callOdoo<{
        brands?: BrandRef[];
        selected?: number;
        error?: { message: string };
      }>("/brand/portal/session");
      if (d.error) {
        setError(d.error.message);
        setBrands([]);
        setBrandId(null);
      } else {
        const list = d.brands ?? [];
        setBrands(list);
        const saved =
          typeof window !== "undefined" ? Number(window.sessionStorage.getItem(STORAGE_KEY)) : 0;
        const chosen = list.some((b) => b.id === saved) ? saved : (d.selected ?? list[0]?.id ?? null);
        setBrandId(chosen ?? null);
        if (chosen) window.sessionStorage.setItem(STORAGE_KEY, String(chosen));
      }
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setReady(true);
    }
  }, []);

  useEffect(() => {
    if (status === "signed-in") void load();
    else if (status === "signed-out") {
      setReady(false);
      setBrands([]);
      setBrandId(null);
      setError(null);
    }
  }, [status, load]);

  const selectBrand = useCallback((id: number) => {
    setBrandId(id);
    if (typeof window !== "undefined") window.sessionStorage.setItem(STORAGE_KEY, String(id));
  }, []);

  return (
    <BrandContext.Provider
      value={{
        ready,
        error,
        brands,
        brandId,
        brand: brands.find((b) => b.id === brandId) ?? null,
        selectBrand,
        reload: load,
      }}
    >
      {children}
    </BrandContext.Provider>
  );
}

/** Brand switcher for the nav; renders nothing until a brand is resolved. */
export function BrandSelect() {
  const { ready, brands, brandId, selectBrand } = useBrand();
  if (!ready || brands.length === 0) return null;
  if (brands.length === 1) {
    return (
      <span
        title={brands[0].code}
        style={{
          fontSize: 11.5,
          fontWeight: 600,
          color: "var(--fix-ink-2)",
          background: "var(--fix-surface-2)",
          padding: "3px 10px",
          borderRadius: 999,
          whiteSpace: "nowrap",
        }}
      >
        {brands[0].name}
      </span>
    );
  }
  return (
    <select
      value={brandId ?? ""}
      onChange={(e) => selectBrand(Number(e.target.value))}
      aria-label="Acting brand"
      style={{ ...selectStyle, maxWidth: 190 }}
    >
      {brands.map((b) => (
        <option key={b.id} value={b.id}>
          {b.name} {b.code ? `(${b.code})` : ""}
        </option>
      ))}
    </select>
  );
}
