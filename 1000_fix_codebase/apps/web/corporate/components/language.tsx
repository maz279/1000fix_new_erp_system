"use client";

/**
 * Corporate B2B Language Provider & Bilingual Dictionary.
 * English-first default for corporate B2B clients in Bangladesh with instant Bangla toggle.
 * Persists selected locale in localStorage (fix_corporate_locale).
 * Tokens only (CFM-01) — no hand-authored colors.
 */
import { createContext, useContext, useEffect, useState } from "react";
import { tokens } from "../lib/imports";

export type Locale = "en" | "bn";

export interface CorporateTranslations {
  // Navigation & Shell
  portalTitle: string;
  isoBadge: string;
  navOverview: string;
  navEstate: string;
  navInvoices: string;
  navRequests: string;
  navCustomerPortal: string;
  navOdooErp: string;
  navHotline: string;
  signIn: string;
  signOut: string;
  guestUser: string;
  loggedInAs: string;
  toggleLangLabel: string;

  // Overview / Dashboard
  overviewTitle: string;
  overviewSubtitle: string;
  enterpriseBadge: string;
  slaBadge: string;
  kpiFleetTotal: string;
  kpiActiveWarranty: string;
  kpiOpenOrders: string;
  kpiInvoicesTotal: string;
  quickActionsTitle: string;
  actionNewRequest: string;
  actionNewRequestDesc: string;
  actionViewEstate: string;
  actionViewEstateDesc: string;
  actionViewInvoices: string;
  actionViewInvoicesDesc: string;
  actionSupport: string;
  actionSupportDesc: string;
  recentOrdersTitle: string;
  recentInvoicesTitle: string;
  viewAll: string;

  // Estate Screen
  estateTitle: string;
  estateSubtitle: (count: number) => string;
  estateSearchPlaceholder: string;
  estateFilterAll: string;
  estateFilterActive: string;
  estateFilterExpired: string;
  estateFilterPending: string;
  estateFilterVoided: string;
  colBrand: string;
  colModel: string;
  colIdentifier: string;
  colWarranty: string;
  colEndDate: string;
  estateEmpty: string;

  // Invoices Screen
  invoicesTitle: string;
  invoicesSubtitle: (count: number) => string;
  invoicesFinancialNote: string;
  invoicesFilterAll: string;
  invoicesFilterIssued: string;
  invoicesFilterPaid: string;
  invoicesFilterDraft: string;
  invoicesFilterCredited: string;
  colInvoiceNo: string;
  colCustomer: string;
  colDate: string;
  colState: string;
  colGross: string;
  colVat: string;
  colNet: string;
  invoicesEmpty: string;

  // Service Requests Screen
  requestsTitle: string;
  requestsSubtitle: (count: number) => string;
  newRequestButton: string;
  cancelButton: string;
  formCategory: string;
  formDevice: string;
  formDeviceSelectPlaceholder: string;
  formDescription: string;
  formDescriptionPlaceholder: string;
  formSubmit: string;
  submitting: string;
  catStandard: string;
  catWarranty: string;
  catAmc: string;
  colOrderRef: string;
  colDevice: string;
  colOpenedDate: string;
  requestsEmpty: string;

  // Status & Generic
  loading: string;
  errorPrefix: string;
  unauthenticatedNotice: string;
  unauthenticatedSignInBtn: string;
  statusActive: string;
  statusExpired: string;
  statusPending: string;
  statusVoided: string;
  statusIssued: string;
  statusPaid: string;
  statusDraft: string;
  statusCredited: string;

  // Auth Modal
  authModalTitle: string;
  authModalSubtitle: string;
  personaAdmin: string;
  personaAdminRole: string;
  personaPortal: string;
  personaPortalRole: string;
  personaDemo: string;
  personaDemoRole: string;
  usernameLabel: string;
  passwordLabel: string;
  loginButton: string;
  loggingIn: string;
  closeButton: string;
}

const enTranslations: CorporateTranslations = {
  portalTitle: "Corporate B2B Portal",
  isoBadge: "ISO 9001:2015 CERTIFIED",
  navOverview: "Overview",
  navEstate: "Fleet Estate",
  navInvoices: "Invoices",
  navRequests: "Service Requests",
  navCustomerPortal: "Customer Portal (:3010) ↗",
  navOdooErp: "Odoo ERP (:8069) ↗",
  navHotline: "Enterprise Hotline: 16743",
  signIn: "Sign In",
  signOut: "Sign Out",
  guestUser: "Corporate Guest",
  loggedInAs: "Corporate Account",
  toggleLangLabel: "Switch language to বাংলা",

  overviewTitle: "Enterprise Fleet & Service Operations",
  overviewSubtitle: "Centralized device asset management, consolidated B2B billing, and SLA service order tracking across Bangladesh.",
  enterpriseBadge: "B2B Enterprise Portal",
  slaBadge: "24/7 SLA Supported",
  kpiFleetTotal: "Total Fleet Assets",
  kpiActiveWarranty: "Active Warranties",
  kpiOpenOrders: "Active Service Requests",
  kpiInvoicesTotal: "Consolidated Invoices",
  quickActionsTitle: "Enterprise Actions",
  actionNewRequest: "Submit Service Request",
  actionNewRequestDesc: "Create immediate repair or maintenance order for registered fleet devices.",
  actionViewEstate: "Manage Asset Fleet",
  actionViewEstateDesc: "Inspect serial numbers, warranty terms, and device locations.",
  actionViewInvoices: "Consolidated Invoices",
  actionViewInvoicesDesc: "Review multi-job corporate tax invoices with South Asian grouping.",
  actionSupport: "Dedicated Enterprise Desk",
  actionSupportDesc: "Direct enterprise priority support via hotline 16743 & certified engineers.",
  recentOrdersTitle: "Recent Fleet Service Requests",
  recentInvoicesTitle: "Recent Consolidated Invoices",
  viewAll: "View All →",

  estateTitle: "Corporate Fleet Estate",
  estateSubtitle: (count) => `${count} registered corporate devices across enterprise locations`,
  estateSearchPlaceholder: "Search by brand, model, or serial/IMEI...",
  estateFilterAll: "All Devices",
  estateFilterActive: "Active Warranty",
  estateFilterExpired: "Expired",
  estateFilterPending: "Pending Verification",
  estateFilterVoided: "Voided",
  colBrand: "Brand",
  colModel: "Model",
  colIdentifier: "Serial / IMEI",
  colWarranty: "Warranty Status",
  colEndDate: "Coverage Expiry",
  estateEmpty: "No corporate devices found matching filter.",

  invoicesTitle: "Consolidated B2B Invoices",
  invoicesSubtitle: (count) => `${count} corporate multi-job invoices for enterprise account`,
  invoicesFinancialNote: "All monetary values are backend-computed strings (AS-10 / BN-007 standard; portal performs zero client arithmetic).",
  invoicesFilterAll: "All Invoices",
  invoicesFilterIssued: "Issued",
  invoicesFilterPaid: "Paid",
  invoicesFilterDraft: "Draft",
  invoicesFilterCredited: "Credited",
  colInvoiceNo: "Invoice #",
  colCustomer: "Corporate Entity",
  colDate: "Billing Date",
  colState: "Payment Status",
  colGross: "Gross Amount (৳)",
  colVat: "VAT 15% (৳)",
  colNet: "Net Payable (৳)",
  invoicesEmpty: "No consolidated invoices recorded.",

  requestsTitle: "Service Requests at Scale",
  requestsSubtitle: (count) => `${count} service and maintenance work orders in enterprise pipeline`,
  newRequestButton: "+ New Service Request",
  cancelButton: "Cancel",
  formCategory: "Service Tier / Category",
  formDevice: "Target Fleet Device",
  formDeviceSelectPlaceholder: "-- Select a registered fleet device --",
  formDescription: "Fault Description & Issue Details",
  formDescriptionPlaceholder: "Detail the hardware or operational failure observed on this asset...",
  formSubmit: "Submit Work Order",
  submitting: "Submitting to Odoo...",
  catStandard: "Standard Repair Service",
  catWarranty: "OEM Warranty Claim",
  catAmc: "Annual Maintenance Contract (AMC)",
  colOrderRef: "Order Ref",
  colDevice: "Asset / Device",
  colOpenedDate: "Date Logged",
  requestsEmpty: "No service orders found.",

  loading: "Loading live data from Odoo ERP via Kong...",
  errorPrefix: "Connection or validation error:",
  unauthenticatedNotice: "Please authenticate to view live corporate records from Odoo ERP.",
  unauthenticatedSignInBtn: "Sign In as Corporate Client",
  statusActive: "Active",
  statusExpired: "Expired",
  statusPending: "Pending",
  statusVoided: "Voided",
  statusIssued: "Issued",
  statusPaid: "Paid",
  statusDraft: "Draft",
  statusCredited: "Credited",

  authModalTitle: "Corporate B2B Authentication",
  authModalSubtitle: "Authenticate against Odoo ERP session through Kong Gateway (port 8000).",
  personaAdmin: "Enterprise Administrator",
  personaAdminRole: "Full access to all fleet devices, work orders, and consolidated invoices",
  personaPortal: "Corporate Client User",
  personaPortalRole: "Standard enterprise partner portal access",
  personaDemo: "Operations Demo Account",
  personaDemoRole: "Evaluator persona with access to all sample corporate assets",
  usernameLabel: "Corporate Login ID / Username",
  passwordLabel: "Password",
  loginButton: "Sign In to Corporate Portal",
  loggingIn: "Authenticating session...",
  closeButton: "Close Dialog",
};

const bnTranslations: CorporateTranslations = {
  portalTitle: "কর্পোরেট বি২বি পোর্টাল",
  isoBadge: "আইএসও ৯০০১:২০১৫ সার্টিফাইড",
  navOverview: "সারসংক্ষেপ",
  navEstate: "ডিভাইস বহর (এস্টেট)",
  navInvoices: "কনসোলিডেটেড ইনভয়েস",
  navRequests: "সার্ভিস রিকোয়েস্ট",
  navCustomerPortal: "কাস্টমার পোর্টাল (:৩০১০) ↗",
  navOdooErp: "ওডু ইআরপি (:৮০৬৯) ↗",
  navHotline: "এন্টারপ্রাইজ হটলাইন: ১৬৭৪৩",
  signIn: "সাইন ইন",
  signOut: "সাইন আউট",
  guestUser: "কর্পোরেট অতিথি",
  loggedInAs: "কর্পোরেট অ্যাকাউন্ট",
  toggleLangLabel: "ইংরেজি ভাষায় পরিবর্তন করুন",

  overviewTitle: "এন্টারপ্রাইজ ডিভাইস বহর ও সার্ভিস পরিচালনা",
  overviewSubtitle: "দেশজুড়ে করপোরেট ক্লায়েন্টদের কেন্দ্রীয় অ্যাসেট পর্যবেক্ষণ, সমন্বিত ইনভয়েস এবং দ্রুততম এসএলএ সার্ভিস ট্র্যাকিং।",
  enterpriseBadge: "বি২বি এন্টারপ্রাইজ পোর্টাল",
  slaBadge: "২৪/৭ সার্বক্ষণিক এসএলএ",
  kpiFleetTotal: "মোট নিবন্ধিত ডিভাইস",
  kpiActiveWarranty: "সক্রিয় ওয়ারেন্টি",
  kpiOpenOrders: "চলমান সার্ভিস অর্ডার",
  kpiInvoicesTotal: "কনসোলিডেটেড ইনভয়েস",
  quickActionsTitle: "কর্পোরেট অ্যাকশন",
  actionNewRequest: "নতুন সার্ভিস রিকোয়েস্ট দিন",
  actionNewRequestDesc: "নিবন্ধিত ডিভাইসের জন্য দ্রুত মেরামত বা রক্ষণাবেক্ষণ অর্ডার দাখিল করুন।",
  actionViewEstate: "ডিভাইস বহর পরিদর্শন",
  actionViewEstateDesc: "সিরিয়াল নম্বর, আইএমইআই এবং ওয়ারেন্টি মেয়াদের তালিকা দেখুন।",
  actionViewInvoices: "কনসোলিডেটেড ইনভয়েস",
  actionViewInvoicesDesc: "সাউথ এশিয়ান নিউমেরিক ফরম্যাটে মোট ভ্যাট ও বকেয়া হিসাব দেখুন।",
  actionSupport: "ডেডিকেটেড এন্টারপ্রাইজ সাপোর্ট",
  actionSupportDesc: "হটলাইন ১৬৭৪৩ ও প্রত্যয়িত প্রকৌশলীদের মাধ্যমে অগ্রাধিকারভিত্তিক সেবা।",
  recentOrdersTitle: "সাম্প্রতিক সার্ভিস অর্ডারসমূহ",
  recentInvoicesTitle: "সাম্প্রতিক কনসোলিডেটেড ইনভয়েসসমূহ",
  viewAll: "সবগুলো দেখুন →",

  estateTitle: "কর্পোরেট ডিভাইস বহর (এস্টেট)",
  estateSubtitle: (count) => `বিভিন্ন শাখায় মোট ${count} টি কর্পোরেট ডিভাইস নিবন্ধিত আছে`,
  estateSearchPlaceholder: "ব্র্যান্ড, মডেল বা সিরিয়াল/আইএমইআই খুঁজুন...",
  estateFilterAll: "সকল ডিভাইস",
  estateFilterActive: "সক্রিয় ওয়ারেন্টি",
  estateFilterExpired: "মেয়াদোত্তীর্ণ",
  estateFilterPending: "যাচাই অপেক্ষমান",
  estateFilterVoided: "বাতিলকৃত",
  colBrand: "ব্র্যান্ড",
  colModel: "মডেল",
  colIdentifier: "সিরিয়াল / আইএমইআই",
  colWarranty: "ওয়ারেন্টি স্ট্যাটাস",
  colEndDate: "মেয়াদ শেষ",
  estateEmpty: "ফিল্টারের সাথে মিল রেখে কোনো ডিভাইস পাওয়া যায়নি।",

  invoicesTitle: "কনসোলিডেটেড বি২বি ইনভয়েস",
  invoicesSubtitle: (count) => `কর্পোরেট অ্যাকাউন্টের মোট ${count} টি সমন্বিত ইনভয়েস`,
  invoicesFinancialNote: "সমস্ত আর্থিক মান ওডু ব্যাকএন্ড কর্তৃক গণনাকৃত স্ট্রিং (AS-10 / BN-007 মানদণ্ড; পোর্টালে কোনো ক্লায়েন্ট ক্যালকুলেশন নেই)।",
  invoicesFilterAll: "সকল ইনভয়েস",
  invoicesFilterIssued: "ইস্যুকৃত",
  invoicesFilterPaid: "পরিশোধিত",
  invoicesFilterDraft: "খসড়া",
  invoicesFilterCredited: "ক্রেডিটেড",
  colInvoiceNo: "ইনভয়েস নং",
  colCustomer: "কর্পোরেট প্রতিষ্ঠান",
  colDate: "বিলিং তারিখ",
  colState: "পেমেন্ট অবস্থা",
  colGross: "মোট মূল্য (৳)",
  colVat: "মূসক ১৫% (৳)",
  colNet: "পরিশোধযোগ্য নেট (৳)",
  invoicesEmpty: "কোনো সমন্বিত ইনভয়েস পাওয়া যায়নি।",

  requestsTitle: "কর্পোরেট সার্ভিস রিকোয়েস্ট",
  requestsSubtitle: (count) => `সার্ভিস পাইপলাইনে মোট ${count} টি কাজ চলমান`,
  newRequestButton: "+ নতুন সার্ভিস রিকোয়েস্ট",
  cancelButton: "বাতিল",
  formCategory: "সার্ভিসের ধরন",
  formDevice: "টার্গেট কর্পোরেট ডিভাইস",
  formDeviceSelectPlaceholder: "-- নিবন্ধিত ডিভাইস নির্বাচন করুন --",
  formDescription: "ত্রুটির বিবরণ ও লক্ষণ",
  formDescriptionPlaceholder: "ডিভাইসে পরিলক্ষিত হার্ডওয়্যার বা সফটওয়্যার সমস্যা বিস্তারিত লিখুন...",
  formSubmit: "রিকোয়েস্ট জমা দিন",
  submitting: "ওডুতে জমা হচ্ছে...",
  catStandard: "সাধারণ মেরামত সার্ভিস",
  catWarranty: "ওয়ারেন্টি ক্লেইম",
  catAmc: "বার্ষিক রক্ষণাবেক্ষণ চুক্তি (এএমসি)",
  colOrderRef: "অর্ডার রেফারেন্স",
  colDevice: "ডিভাইস",
  colOpenedDate: "দাখিলের তারিখ",
  requestsEmpty: "কোনো সার্ভিস অর্ডার পাওয়া যায়নি।",

  loading: "ওডু ইআরপি থেকে কঙ গেটওয়ের মাধ্যমে লাইভ ডেটা লোড হচ্ছে...",
  errorPrefix: "সংযোগ বা যাচাইকরণ ত্রুটি:",
  unauthenticatedNotice: "ওডু ইআরপি থেকে লাইভ কর্পোরেট তথ্য দেখতে অনুগ্রহ করে সাইন ইন করুন।",
  unauthenticatedSignInBtn: "কর্পোরেট ক্লায়েন্ট হিসেবে সাইন ইন করুন",
  statusActive: "সক্রিয়",
  statusExpired: "মেয়াদোত্তীর্ণ",
  statusPending: "অপেক্ষমান",
  statusVoided: "বাতিল",
  statusIssued: "ইস্যুকৃত",
  statusPaid: "পরিশোধিত",
  statusDraft: "খসড়া",
  statusCredited: "ক্রেডিটেড",

  authModalTitle: "কর্পোরেট বি২বি লগইন",
  authModalSubtitle: "কঙ গেটওয়ের মাধ্যমে ওডু ইআরপি সেশনে সরাসরি প্রবেশ করুন।",
  personaAdmin: "এন্টারপ্রাইজ অ্যাডমিনিস্ট্রেটর",
  personaAdminRole: "সমস্ত বহর, সার্ভিস অর্ডার এবং ইনভয়েসে সম্পূর্ণ এক্সেস",
  personaPortal: "কর্পোরেট ক্লায়েন্ট ইউজার",
  personaPortalRole: "স্ট্যান্ডার্ড এন্টারপ্রাইজ পার্টনার পোর্টাল এক্সেস",
  personaDemo: "অপারেশনস ডেমো অ্যাকাউন্ট",
  personaDemoRole: "কর্পোরেট সম্পদ মূল্যায়নের জন্য পরীক্ষামূলক এক্সেস",
  usernameLabel: "লগইন ইউজারনেম",
  passwordLabel: "পাসওয়ার্ড",
  loginButton: "কর্পোরেট পোর্টালে প্রবেশ করুন",
  loggingIn: "যাচাই করা হচ্ছে...",
  closeButton: "ডায়ালগ বন্ধ করুন",
};

interface LanguageContextValue {
  locale: Locale;
  t: CorporateTranslations;
  setLocale: (l: Locale) => void;
  toggleLocale: () => void;
}

const LanguageContext = createContext<LanguageContextValue>({
  locale: "en",
  t: enTranslations,
  setLocale: () => {},
  toggleLocale: () => {},
});

export function useLanguage() {
  return useContext(LanguageContext);
}

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  useEffect(() => {
    const saved = localStorage.getItem("fix_corporate_locale") as Locale;
    if (saved === "en" || saved === "bn") {
      setLocaleState(saved);
    }
  }, []);

  const setLocale = (l: Locale) => {
    setLocaleState(l);
    localStorage.setItem("fix_corporate_locale", l);
    document.documentElement.lang = l;
  };

  const toggleLocale = () => {
    const next = locale === "en" ? "bn" : "en";
    setLocale(next);
  };

  return (
    <LanguageContext.Provider
      value={{
        locale,
        t: locale === "bn" ? bnTranslations : enTranslations,
        setLocale,
        toggleLocale,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function LanguageToggle() {
  const { locale, toggleLocale, t } = useLanguage();
  return (
    <button
      onClick={toggleLocale}
      aria-label={t.toggleLangLabel}
      style={{
        padding: "4px 10px",
        background: tokens["color.surface.primary"],
        color: tokens["color.primary.base"],
        border: `1px solid ${tokens["color.primary.base"]}`,
        borderRadius: tokens["dimension.border.radius-sm"],
        cursor: "pointer",
        fontSize: tokens["typography.size.200"],
        fontWeight: Number(tokens["typography.weight.semibold"]),
        display: "inline-flex",
        alignItems: "center",
        gap: 4,
      }}
    >
      🌐 {locale === "en" ? "বাংলা" : "English"}
    </button>
  );
}
