"use client";

/**
 * Language Provider & Bilingual Dictionary (DE-17: Bengali-first with full English toggle).
 * Provides responsive dual-language switching across all customer portal routes.
 * Persists selected locale in localStorage (fix_locale).
 * Tokens only (CFM-01) — no hand-authored colors.
 */
import { createContext, useContext, useEffect, useState } from "react";
import { tokens } from "../lib/imports";

export type Locale = "bn" | "en";

export interface Translations {
  // Navigation & Shell
  portalTitle: string;
  isoBadge: string;
  navHome: string;
  navBooking: string;
  navTracking: string;
  navEstimates: string;
  navDevices: string;
  navConsent: string;
  navTechnician: string;
  navWelcome: string;
  navCorporate: string;
  navOperations: string;
  navHotline: string;
  signIn: string;
  signOut: string;
  guestUser: string;
  loggedInAs: string;
  toggleLangLabel: string;

  // Home / Bookings
  homeTitle: string;
  homeSubtitle: (count: number) => string;
  homeColRef: string;
  homeColDevice: string;
  homeColFault: string;
  homeColCategory: string;
  homeColTechnician: string;
  homeColStatus: string;
  homeEmpty: string;
  homeFooterNote: string;
  homeFooterLink: string;
  homeFooterEnd: string;
  homeSignInPrompt: string;
  homeSignInButton: string;

  // States
  stateDraft: string;
  stateSent: string;
  stateConfirmed: string;
  stateInProgress: string;
  stateDone: string;
  stateDelivered: string;
  stateCancelled: string;
  stateClosed: string;

  // Booking Wizard
  bookingTitle: string;
  bookingSubtitle: string;
  bookingStep: (n: number) => string;
  bookingStep1Title: string;
  bookingNoDevices: string;
  bookingViewDevices: string;
  bookingStep2Title: string;
  bookingCategoryLabel: string;
  bookingCatStandard: string;
  bookingCatWarranty: string;
  bookingCatAmc: string;
  bookingFaultLabel: string;
  bookingFaultPlaceholder: string;
  bookingBack: string;
  bookingNext: string;
  bookingStep3Title: string;
  bookingConfirmDevice: string;
  bookingConfirmCategory: string;
  bookingConfirmDescription: string;
  bookingSubmitting: string;
  bookingConfirmBtn: string;
  bookingSuccessTitle: string;
  bookingSuccessRef: (ref: string) => string;
  bookingSuccessNote: string;
  bookingSuccessTrackingLink: string;

  // Live Tracking
  trackingTitle: string;
  trackingSubtitle: string;
  trackingSelectPlaceholder: string;
  trackingLoading: string;
  trackingStatRef: string;
  trackingStatStatus: string;
  trackingStatTech: string;
  trackingStatTechUnassigned: string;
  trackingStatEta: string;
  trackingStatSla: string;
  trackingSlaPaused: string;
  trackingSlaRunning: string;

  // Estimates
  estimatesTitle: string;
  estimatesSubtitle: string;
  estimatesColOrder: string;
  estimatesColVersion: string;
  estimatesColTotal: string;
  estimatesColExpiry: string;
  estimatesColAction: string;
  estimatesApprove: string;
  estimatesReject: string;
  estimatesEmpty: string;
  estimatesLegend: string;
  estimatesPromptProof: string;
  estimatesNoticeDone: string;

  // Devices & Warranty
  devicesTitle: string;
  devicesSubtitle: (count: number) => string;
  devicesBtnTransfer: string;
  devicesIdentifier: (id: string) => string;
  devicesHistorySummary: (count: number) => string;
  devicesHistoryEmpty: string;
  devicesEmpty: string;
  devicesTransferTitle: (brand: string, model: string) => string;
  devicesTransferDesc: string;
  devicesTransferPlaceholder: string;
  devicesTransferCancel: string;
  devicesTransferConfirm: string;
  devicesTransferNoticeSuccess: string;

  // PDPA Consent
  consentTitle: string;
  consentSubtitle: string;
  consentGrantedWithProof: (date: string, proof: string) => string;
  consentWithdrawn: (date: string) => string;
  consentNone: string;
  consentBtnGrant: string;
  consentBtnWithdraw: string;
  consentPromptProof: string;
  consentNoticeSaved: string;
  channelSms: string;
  channelWhatsapp: string;
  channelEmail: string;
  channelPush: string;
  channelMarketing: string;

  // Phone OTP Authentication (250K+ Customers)
  authOtpTab: string;
  authCredsTab: string;
  authPhoneLabel: string;
  authPhonePlaceholder: string;
  authSendOtpBtn: string;
  authOtpSentNotice: (masked: string) => string;
  authOtpCodeLabel: string;
  authVerifyOtpBtn: string;
  authResendOtp: string;

  // Device Registration
  devicesBtnRegister: string;
  devicesRegisterTitle: string;
  devicesRegisterDesc: string;
  devicesRegisterModelLabel: string;
  devicesRegisterSerialLabel: string;
  devicesRegisterImeiLabel: string;
  devicesRegisterChannelLabel: string;
  devicesRegisterBtnSubmit: string;
  devicesRegisterSuccess: string;

  // Booking Slots & Service Modes
  bookingServiceTypeLabel: string;
  bookingModeWalkIn: string;
  bookingModeCollection: string;
  bookingModeOnsite: string;
  bookingBranchLabel: string;
  bookingDateLabel: string;
  bookingSlotLabel: string;
  bookingSlotMorning: string;
  bookingSlotAfternoon: string;
  bookingSlotEvening: string;
  bookingQuickRegisterDevice: string;

  // Live Tracking Milestones & ETA
  trackingMilestonesTitle: string;
  trackingDeviceDetails: string;
  trackingServiceMode: string;
  trackingEtaDeadline: string;
  trackingStageActive: string;

  // Estimates Mushak 6.3 & E-Sign
  estimatesMushakTitle: string;
  estimatesPartsTotal: string;
  estimatesLabourTotal: string;
  estimatesDiscount: string;
  estimatesVatRate: string;
  estimatesGrandTotal: string;
  estimatesApproveModalTitle: string;
  estimatesApprovalRefLabel: string;
  estimatesApprovalRefPlaceholder: string;
  estimatesConfirmApprove: string;

  // PDPA Consent Modal
  consentModalTitle: string;
  consentProofLabel: string;
  consentConfirmGrant: string;

  // Common Feedback
  loading: string;
  loadErrorTitle: (what: string) => string;
  sessionExpired: string;
  sessionExpiredHint: string;
}

export const DICTIONARY: Record<Locale, Translations> = {
  bn: {
    portalTitle: "১০০০FiX কাস্টমার",
    isoBadge: "আইএসও ৯০০১:২০১৫",
    navHome: "হোম",
    navBooking: "বুকিং",
    navTracking: "ট্র্যাকিং",
    navEstimates: "অনুমান",
    navDevices: "ডিভাইস",
    navConsent: "সম্মতি",
    navTechnician: "টেকনিশিয়ান (P02)",
    navWelcome: "✦ প্ল্যাটফর্ম",
    navCorporate: "করপোরেট (:3001) ↗",
    navOperations: "অপারেশনস (:8069) ↗",
    navHotline: "📞 ১৬৭৪৩",
    signIn: "লগইন",
    signOut: "লগআউট",
    guestUser: "অতিথি",
    loggedInAs: "সংযুক্ত",
    toggleLangLabel: "English",

    homeTitle: "আমার সার্ভিস বুকিং",
    homeSubtitle: (c) => `${c}টি অর্ডার — লাইভ অবস্থা সার্ভার থেকে`,
    homeColRef: "রেফারেন্স",
    homeColDevice: "ডিভাইস",
    homeColFault: "সমস্যা",
    homeColCategory: "ক্যাটাগরি",
    homeColTechnician: "টেকনিশিয়ান",
    homeColStatus: "অবস্থা",
    homeEmpty: "কোনো সার্ভিস বুকিং পাওয়া যায়নি।",
    homeFooterNote: "নতুন সার্ভিস নিতে ",
    homeFooterLink: "বুকিং",
    homeFooterEnd: " পাতায় যান — তিন ধাপে সম্পন্ন।",
    homeSignInPrompt: "আপনার সার্ভিস অর্ডার ও ডিভাইস দেখতে লগইন করুন।",
    homeSignInButton: "কাস্টমার লগইন করুন",

    stateDraft: "খসড়া",
    stateSent: "পাঠানো",
    stateConfirmed: "নিশ্চিত",
    stateInProgress: "চলমান",
    stateDone: "সম্পন্ন",
    stateDelivered: "ডেলিভারি",
    stateCancelled: "বাতিল",
    stateClosed: "বন্ধ",

    bookingTitle: "নতুন সার্ভিস বুকিং",
    bookingSubtitle: "তিন ধাপে সম্পন্ন — ডিভাইস, সমস্যা, নিশ্চিতকরণ",
    bookingStep: (n) => `ধাপ ${n}`,
    bookingStep1Title: "১ — ডিভাইস নির্বাচন করুন",
    bookingNoDevices: "কোনো নিবন্ধিত ডিভাইস নেই — ",
    bookingViewDevices: "ডিভাইস পাতা দেখুন।",
    bookingStep2Title: "২ — সমস্যার বিবরণ",
    bookingCategoryLabel: "ক্যাটাগরি",
    bookingCatStandard: "স্ট্যান্ডার্ড সার্ভিস",
    bookingCatWarranty: "ওয়ারেন্টি সার্ভিস",
    bookingCatAmc: "AMC চুক্তি",
    bookingFaultLabel: "কী সমস্যা হয়েছে?",
    bookingFaultPlaceholder: "যেমন: ফোন চার্জ হচ্ছে না, স্ক্রিনে দাগ ইত্যাদি…",
    bookingBack: "ফিরে যান",
    bookingNext: "পরবর্তী",
    bookingStep3Title: "৩ — নিশ্চিত করুন",
    bookingConfirmDevice: "ডিভাইস",
    bookingConfirmCategory: "ক্যাটাগরি",
    bookingConfirmDescription: "বিবরণ",
    bookingSubmitting: "পাঠানো হচ্ছে…",
    bookingConfirmBtn: "বুকিং নিশ্চিত করুন",
    bookingSuccessTitle: "বুকিং সম্পন্ন ✅",
    bookingSuccessRef: (ref) => `রেফারেন্স: ${ref}`,
    bookingSuccessNote: "অগ্রগতি দেখতে ",
    bookingSuccessTrackingLink: "ট্র্যাকিং পাতায় যান।",

    trackingTitle: "লাইভ ট্র্যাকিং",
    trackingSubtitle: "অবস্থা প্রতি ১৫ সেকেন্ডে সদ্য হয় (পোলিং)",
    trackingSelectPlaceholder: "— অর্ডার নির্বাচন করুন —",
    trackingLoading: "ট্র্যাক আনা হচ্ছে…",
    trackingStatRef: "রেফারেন্স",
    trackingStatStatus: "অবস্থা",
    trackingStatTech: "টেকনিশিয়ান",
    trackingStatTechUnassigned: "নির্ধারিত নয়",
    trackingStatEta: "সমাধানের সম্ভাব্য সময়",
    trackingStatSla: "SLA ঘড়ি",
    trackingSlaPaused: "বিরত",
    trackingSlaRunning: "চলমান",

    estimatesTitle: "অনুমান অনুমোদন",
    estimatesSubtitle: "৫,০০০ ৳ এর বেশি হলে লিখিত অনুমোদন আবশ্যক; ২৫,০০০ ৳ এর বেশি হলে ব্রাঞ্চ ম্যানেজারেরও অনুমোদন লাগবে (BRU-SRM-07/08)",
    estimatesColOrder: "অর্ডার",
    estimatesColVersion: "ভার্সন",
    estimatesColTotal: "মোট (৳)",
    estimatesColExpiry: "মেয়াদ",
    estimatesColAction: "পদক্ষেপ",
    estimatesApprove: "অনুমোদন",
    estimatesReject: "বাতিল",
    estimatesEmpty: "এই মুহূর্তে অপেক্ষমান কোনো অনুমান নেই।",
    estimatesLegend: "= আপনার অনুমোদনের অপেক্ষায়",
    estimatesPromptProof: "অনুমোদনের প্রমাণ দিন (OTP আইডি / ই-সাইন রেফারেন্স)",
    estimatesNoticeDone: "সম্পন্ন হয়েছে",

    devicesTitle: "আমার ডিভাইস",
    devicesSubtitle: (c) => `${c}টি নিবন্ধিত ডিভাইস — M17 রেজিস্ট্রি থেকে`,
    devicesBtnTransfer: "মালিকানা হস্তান্তর",
    devicesIdentifier: (id) => `আইডেন্টিফায়ার: ${id}`,
    devicesHistorySummary: (c) => `সার্ভিস ইতিহাস (${c})`,
    devicesHistoryEmpty: "কোনো ইতিহাস নেই",
    devicesEmpty: "কোনো ডিভাইস নিবন্ধিত নেই।",
    devicesTransferTitle: (brand, model) => `মালিকানা হস্তান্তর — ${brand} ${model}`,
    devicesTransferDesc: "নতুন মালিকের পার্টনার আইডি দিন (হস্তান্তর রেকর্ড স্থায়ীভাবে সংরক্ষিত হয়)।",
    devicesTransferPlaceholder: "নতুন মালিকের আইডি",
    devicesTransferCancel: "বাতিল",
    devicesTransferConfirm: "হস্তান্তর নিশ্চিত করুন",
    devicesTransferNoticeSuccess: "মালিকানা হস্তান্তর সম্পন্ন",

    consentTitle: "সম্মতি ড্যাশবোর্ড",
    consentSubtitle: "প্রতি চ্যানেলে সম্মতি দিন বা প্রত্যাহার করুন — প্রত্যাহারের রেকর্ড স্থায়ীভাবে থাকে (BTRC/DND)",
    consentGrantedWithProof: (date, proof) => `দেওয়া হয়েছে — ${date} (প্রমাণ: ${proof})`,
    consentWithdrawn: (date) => `প্রত্যাহার — ${date}`,
    consentNone: "কোনো সম্মতি নেই",
    consentBtnGrant: "সম্মতি দিন",
    consentBtnWithdraw: "প্রত্যাহার",
    consentPromptProof: "সম্মতির প্রমাণ দিন (OTP আইডি / ই-সাইন রেফারেন্স / স্বাক্ষরিত ফর্ম আইডি)",
    consentNoticeSaved: "সম্মতি সংরক্ষিত হয়েছে",
    channelSms: "এসএমএস",
    channelWhatsapp: "হোয়াটসঅ্যাপ",
    channelEmail: "ইমেইল",
    channelPush: "পুশ নোটিফিকেশন",
    channelMarketing: "মার্কেটিং (সব চ্যানেল)",

    authOtpTab: "মোবাইল ওটিপি (২৫০K+ গ্রাহক)",
    authCredsTab: "পাসওয়ার্ড ও ডেমো পারসোনা",
    authPhoneLabel: "১১-সংখ্যার মোবাইল নম্বর",
    authPhonePlaceholder: "০১৭১১২২৩৩৪৪ বা 017XXXXXXXX",
    authSendOtpBtn: "ওটিপি কোড পাঠান",
    authOtpSentNotice: (masked) => `৬-সংখ্যার যাচাইকরণ কোড পাঠানো হয়েছে ${masked} নম্বরে`,
    authOtpCodeLabel: "৬-সংখ্যার ওটিপি যাচাইকরণ কোড",
    authVerifyOtpBtn: "যাচাই করুন ও পোর্টাল প্রবেশ করুন",
    authResendOtp: "কোড পাননি? পুনরায় পাঠান",

    devicesBtnRegister: "+ নতুন ডিভাইস যোগ করুন",
    devicesRegisterTitle: "নতুন ডিভাইস প্রোফাইলে যোগ করুন",
    devicesRegisterDesc: "১০০০ফিক্স অফিসিয়াল ডিভাইস ট্র্যাকিং ও ওয়ারেন্টি ম্যানেজমেন্ট (M17)",
    devicesRegisterModelLabel: "ডিভাইস মডেল নির্বাচন করুন",
    devicesRegisterSerialLabel: "সিরিয়াল নম্বর (Serial Number)",
    devicesRegisterImeiLabel: "আইএমইআই নম্বর (IMEI 1 - ১৫ সংখ্যা)",
    devicesRegisterChannelLabel: "ক্রয় চ্যানেল (Purchase Channel)",
    devicesRegisterBtnSubmit: "ডিভাইস নিবন্ধন সম্পন্ন করুন",
    devicesRegisterSuccess: "ডিভাইসটি সফলভাবে নিবন্ধিত হয়েছে!",

    bookingServiceTypeLabel: "সার্ভিস গ্রহণের মাধ্যম",
    bookingModeWalkIn: "ওয়াক-ইন ড্রপ-অফ (শাখা সার্ভিস সেন্টার)",
    bookingModeCollection: "ডোরস্টেপ পিকআপ (হোম কালেকশন)",
    bookingModeOnsite: "অন-সাইট পরিদর্শন (বাসা/অফিস)",
    bookingBranchLabel: "নিকটস্থ সার্ভিস সেন্টার শাখা",
    bookingDateLabel: "অ্যাপয়েন্টমেন্টের তারিখ",
    bookingSlotLabel: "পছন্দের সময় স্লট",
    bookingSlotMorning: "সকাল (১০:০০ - ০১:০০)",
    bookingSlotAfternoon: "দুপুর (০২:০০ - ০৫:০০)",
    bookingSlotEvening: "সন্ধ্যা (০৫:০০ - ০৮:০০)",
    bookingQuickRegisterDevice: "+ ডিভাইস নেই? নতুন ডিভাইস যোগ করুন",

    trackingMilestonesTitle: "৫-ধাপের লাইভ সার্ভিস অগ্রগতি ও ট্র্যাকিং",
    trackingDeviceDetails: "ডিভাইস ও সার্ভিস শাখা",
    trackingServiceMode: "সার্ভিস মাধ্যম",
    trackingEtaDeadline: "রেজোলিউশন এসএলএ সময়সীমা",
    trackingStageActive: "বর্তমান অবস্থা",

    estimatesMushakTitle: "মূসক-৬.৩ সার্ভিস এস্টিমেট ও ট্যাক্স ইনভয়েস প্রিভিউ",
    estimatesPartsTotal: "যন্ত্রাংশের মূল্য (Parts Total)",
    estimatesLabourTotal: "মেরামত পারিশ্রমিক (Labour Service)",
    estimatesDiscount: "বিশেষ ছাড় (Discount)",
    estimatesVatRate: "ভ্যাট (১৫% মূসক)",
    estimatesGrandTotal: "সর্বমোট প্রদেয় (Grand Total BDT)",
    estimatesApproveModalTitle: "এস্টিমেট অনুমোদন ও ই-স্বাক্ষর (BRU-SRM-07)",
    estimatesApprovalRefLabel: "ওটিপি আইডি বা ডিজিটাল স্বাক্ষর রেফারেন্স",
    estimatesApprovalRefPlaceholder: "উদাঃ OTP-994821 অথবা E-SIGN-TXN",
    estimatesConfirmApprove: "অনুমোদন ও ই-স্বাক্ষর নিশ্চিত করুন",

    consentModalTitle: "পিডিপিএ ডেটা সম্মতি প্রদান (PDPA Compliance)",
    consentProofLabel: "যাচাইযোগ্য সম্মতি প্রমাণ (OTP আইডি / ডিজিটাল ফরম আইডি)",
    consentConfirmGrant: "সম্মতি প্রদান নিশ্চিত করুন",

    loading: "লোড হচ্ছে…",
    loadErrorTitle: (what) => what,
    sessionExpired: "সেশন মেয়াদোত্তীর্ণ বা সাইন ইন করা নেই",
    sessionExpiredHint: "অনুগ্রহ করে কাস্টমার হিসেবে সাইন ইন করুন।",
  },

  en: {
    portalTitle: "1000FiX Customer",
    isoBadge: "ISO 9001:2015",
    navHome: "Home",
    navBooking: "Booking",
    navTracking: "Tracking",
    navEstimates: "Estimates",
    navDevices: "Devices",
    navConsent: "Consent",
    navTechnician: "Technician (P02)",
    navWelcome: "✦ Platform",
    navCorporate: "Corporate (:3001) ↗",
    navOperations: "Operations (:8069) ↗",
    navHotline: "📞 16743",
    signIn: "Sign In",
    signOut: "Sign Out",
    guestUser: "Guest",
    loggedInAs: "Connected",
    toggleLangLabel: "বাংলা",

    homeTitle: "My Service Bookings",
    homeSubtitle: (c) => `${c} orders — live status from server`,
    homeColRef: "Reference",
    homeColDevice: "Device",
    homeColFault: "Fault Description",
    homeColCategory: "Category",
    homeColTechnician: "Technician",
    homeColStatus: "Status",
    homeEmpty: "No service bookings found.",
    homeFooterNote: "To request a new service, visit the ",
    homeFooterLink: "Booking",
    homeFooterEnd: " page — completed in 3 quick steps.",
    homeSignInPrompt: "Please sign in to view your service orders and registered devices.",
    homeSignInButton: "Customer Sign In",

    stateDraft: "Draft",
    stateSent: "Sent",
    stateConfirmed: "Confirmed",
    stateInProgress: "In Progress",
    stateDone: "Completed",
    stateDelivered: "Delivered",
    stateCancelled: "Cancelled",
    stateClosed: "Closed",

    bookingTitle: "New Service Booking",
    bookingSubtitle: "Completed in 3 steps — Device, Fault Description, Confirmation",
    bookingStep: (n) => `Step ${n}`,
    bookingStep1Title: "1 — Select Registered Device",
    bookingNoDevices: "No registered devices found — ",
    bookingViewDevices: "View Devices page.",
    bookingStep2Title: "2 — Fault Details",
    bookingCategoryLabel: "Order Category",
    bookingCatStandard: "Standard Service",
    bookingCatWarranty: "Warranty Service",
    bookingCatAmc: "AMC Contract",
    bookingFaultLabel: "What problem occurred?",
    bookingFaultPlaceholder: "E.g., phone does not charge, display flickering, liquid damage…",
    bookingBack: "Back",
    bookingNext: "Next",
    bookingStep3Title: "3 — Review & Confirm",
    bookingConfirmDevice: "Device",
    bookingConfirmCategory: "Category",
    bookingConfirmDescription: "Fault Description",
    bookingSubmitting: "Submitting…",
    bookingConfirmBtn: "Confirm Booking",
    bookingSuccessTitle: "Booking Confirmed ✅",
    bookingSuccessRef: (ref) => `Reference: ${ref}`,
    bookingSuccessNote: "To monitor real-time repair progress, visit the ",
    bookingSuccessTrackingLink: "Tracking page.",

    trackingTitle: "Live Service Tracking",
    trackingSubtitle: "Status refreshes automatically every 15 seconds (live polling)",
    trackingSelectPlaceholder: "— Select Service Order —",
    trackingLoading: "Fetching tracking updates…",
    trackingStatRef: "Reference",
    trackingStatStatus: "Current Status",
    trackingStatTech: "Technician",
    trackingStatTechUnassigned: "Not Assigned Yet",
    trackingStatEta: "Estimated Resolution Time",
    trackingStatSla: "SLA Clock",
    trackingSlaPaused: "Paused",
    trackingSlaRunning: "Running",

    estimatesTitle: "Estimate Approval",
    estimatesSubtitle: "Written approval is required for > ৳5,000; Branch Manager sign-off is required for > ৳25,000 (BRU-SRM-07/08)",
    estimatesColOrder: "Order",
    estimatesColVersion: "Version",
    estimatesColTotal: "Total (৳)",
    estimatesColExpiry: "Expiry Date",
    estimatesColAction: "Action",
    estimatesApprove: "Approve",
    estimatesReject: "Reject",
    estimatesEmpty: "There are currently no pending estimates awaiting approval.",
    estimatesLegend: "= Awaiting Your Approval",
    estimatesPromptProof: "Provide documented approval reference (OTP ID / e-Sign Reference)",
    estimatesNoticeDone: "Action completed successfully",

    devicesTitle: "My Registered Devices",
    devicesSubtitle: (c) => `${c} registered devices — from M17 Device Registry`,
    devicesBtnTransfer: "Transfer Ownership",
    devicesIdentifier: (id) => `Identifier: ${id}`,
    devicesHistorySummary: (c) => `Service History (${c})`,
    devicesHistoryEmpty: "No past service history recorded",
    devicesEmpty: "No devices currently registered under this account.",
    devicesTransferTitle: (brand, model) => `Transfer Ownership — ${brand} ${model}`,
    devicesTransferDesc: "Enter the recipient partner ID (ownership audit log is permanently preserved).",
    devicesTransferPlaceholder: "New Owner Partner ID",
    devicesTransferCancel: "Cancel",
    devicesTransferConfirm: "Confirm Transfer",
    devicesTransferNoticeSuccess: "Ownership transfer completed successfully",

    consentTitle: "PDPA Consent Dashboard",
    consentSubtitle: "Grant or withdraw consent per communication channel — revocation audit log is permanently preserved (BTRC/DND)",
    consentGrantedWithProof: (date, proof) => `Granted — ${date} (Proof: ${proof})`,
    consentWithdrawn: (date) => `Withdrawn — ${date}`,
    consentNone: "No consent on record",
    consentBtnGrant: "Grant Consent",
    consentBtnWithdraw: "Withdraw",
    consentPromptProof: "Provide verifiable proof (OTP ID / e-Sign Ref / Signed Form ID)",
    consentNoticeSaved: "Consent preference saved successfully",
    channelSms: "SMS",
    channelWhatsapp: "WhatsApp",
    channelEmail: "Email",
    channelPush: "Push Notifications",
    channelMarketing: "Marketing (All Channels)",

    authOtpTab: "Mobile OTP (250K+ Customers)",
    authCredsTab: "Credentials & Demo Persona",
    authPhoneLabel: "11-Digit Mobile Number",
    authPhonePlaceholder: "017XXXXXXXX or 018XXXXXXXX",
    authSendOtpBtn: "Send OTP Code",
    authOtpSentNotice: (masked) => `6-digit verification code sent to ${masked}`,
    authOtpCodeLabel: "6-Digit Verification OTP Code",
    authVerifyOtpBtn: "Verify OTP & Sign In",
    authResendOtp: "Didn't receive code? Resend OTP",

    devicesBtnRegister: "+ Register New Device",
    devicesRegisterTitle: "Register New Device to Profile",
    devicesRegisterDesc: "Official 1000FiX Device Registry & Warranty Tracking (M17)",
    devicesRegisterModelLabel: "Select Device Model",
    devicesRegisterSerialLabel: "Serial Number (Optional if IMEI provided)",
    devicesRegisterImeiLabel: "IMEI 1 (15 Digits)",
    devicesRegisterChannelLabel: "Purchase Channel",
    devicesRegisterBtnSubmit: "Complete Device Registration",
    devicesRegisterSuccess: "Device successfully registered to your account!",

    bookingServiceTypeLabel: "Service Delivery Mode",
    bookingModeWalkIn: "Walk-in Drop-off (Branch Center)",
    bookingModeCollection: "Doorstep Pickup (Home Collection)",
    bookingModeOnsite: "On-site Field Inspection",
    bookingBranchLabel: "Select Nearest Branch",
    bookingDateLabel: "Preferred Appointment Date",
    bookingSlotLabel: "Available Time Slot",
    bookingSlotMorning: "Morning (10:00 AM - 01:00 PM)",
    bookingSlotAfternoon: "Afternoon (02:00 PM - 05:00 PM)",
    bookingSlotEvening: "Evening (05:00 PM - 08:00 PM)",
    bookingQuickRegisterDevice: "+ Device not listed? Register New Device",

    trackingMilestonesTitle: "5-Stage Real-Time Service Milestones",
    trackingDeviceDetails: "Device & Allocated Branch",
    trackingServiceMode: "Service Mode",
    trackingEtaDeadline: "Resolution SLA Target Deadline",
    trackingStageActive: "Current Milestone",

    estimatesMushakTitle: "Mushak 6.3 Service Estimate & Tax Breakdown Preview",
    estimatesPartsTotal: "Parts Total",
    estimatesLabourTotal: "Labour Service Fee",
    estimatesDiscount: "Special Discount",
    estimatesVatRate: "VAT (15% Mushak)",
    estimatesGrandTotal: "Grand Total Payable (BDT)",
    estimatesApproveModalTitle: "Estimate Approval & E-Signature (BRU-SRM-07)",
    estimatesApprovalRefLabel: "OTP Verification ID or Digital Signature Ref",
    estimatesApprovalRefPlaceholder: "e.g. OTP-994821 or E-SIGN-TXN",
    estimatesConfirmApprove: "Confirm Approval & Digital Signature",

    consentModalTitle: "PDPA Consent Verification & Grant",
    consentProofLabel: "Verifiable Consent Proof (OTP / Form ID)",
    consentConfirmGrant: "Confirm Consent Grant",

    loading: "Loading…",
    loadErrorTitle: (what) => what,
    sessionExpired: "Session expired or not signed in",
    sessionExpiredHint: "Please sign in to access your customer records.",
  },
};

interface LanguageContextValue {
  locale: Locale;
  setLocale: (l: Locale) => void;
  toggleLocale: () => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextValue>({
  locale: "bn",
  setLocale: () => {},
  toggleLocale: () => {},
  t: DICTIONARY.bn,
});

export function useLanguage() {
  return useContext(LanguageContext);
}

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("bn");

  useEffect(() => {
    const saved = localStorage.getItem("fix_locale") as Locale;
    if (saved === "en" || saved === "bn") {
      setLocaleState(saved);
      document.documentElement.lang = saved;
    } else {
      document.documentElement.lang = "bn";
    }
  }, []);

  const setLocale = (l: Locale) => {
    setLocaleState(l);
    localStorage.setItem("fix_locale", l);
    document.documentElement.lang = l;
  };

  const toggleLocale = () => {
    setLocale(locale === "bn" ? "en" : "bn");
  };

  return (
    <LanguageContext.Provider value={{ locale, setLocale, toggleLocale, t: DICTIONARY[locale] }}>
      {children}
    </LanguageContext.Provider>
  );
}

/** Language toggle button styled with Service-Teal Fluent tokens */
export function LanguageToggle() {
  const { locale, toggleLocale, t } = useLanguage();
  return (
    <button
      onClick={toggleLocale}
      aria-label={`Switch to ${locale === "bn" ? "English" : "Bangla"}`}
      style={{
        padding: "4px 10px",
        background: tokens["color.surface.primary"],
        color: tokens["color.primary.base"],
        border: `1px solid ${tokens["color.primary.base"]}`,
        borderRadius: tokens["dimension.border.radius-sm"],
        cursor: "pointer",
        fontSize: tokens["typography.size.200"],
        fontWeight: Number(tokens["typography.weight.semibold"]),
      }}
    >
      {t.toggleLangLabel}
    </button>
  );
}
