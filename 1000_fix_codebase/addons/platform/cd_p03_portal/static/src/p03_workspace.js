/** @odoo-module **/

/* =====================================================================
 * P03 Operations Workspace — Dynamics-365 Canonical Shell & 13 Archetypes
 * Port of Prototype UX (FIX-UXD-2026-001) for 1000 FiX Services Ltd.
 *
 * DATA POLICY (03-DATA-STRATEGY): every number rendered in this shell is
 * read from the live backend (rpc → /p03/* controllers over real Odoo
 * models). Where a surface has no backend phase yet, the workspace renders
 * an empty state — never an invented value.
 * ===================================================================== */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { user } from "@web/core/user";
import { Component, onWillStart, onWillUnmount, onMounted, useState, markup } from "@odoo/owl";
import { P03_AREAS, P03_MODULES, P03_ROLES, generateGridData, P03_LIVE_SCREENS, P03_MODULE_CREATE, P03_FORM_MODELS, P03_FORM_CHIPS, P03_DATA_SCREENS } from "./p03_modules_meta";
import { P03_BN, P03_STATES } from "./p03_i18n";
import { P03_REPORT_ROUTES } from "./p03_modules_meta";

// Register rpc & user services in Odoo services registry to guarantee useService resolves cleanly
export const rpcService = {
    start() {
        return rpc;
    },
};
if (!registry.category("services").contains("rpc")) {
    registry.category("services").add("rpc", rpcService);
}

export const userService = {
    start() {
        return user;
    },
};
if (!registry.category("services").contains("user")) {
    registry.category("services").add("user", userService);
}

function esc(s) {
    return String(s == null ? "" : s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function path(pts) {
    return pts
        .map((p, i) => (i ? "L" : "M") + p[0].toFixed(1) + " " + p[1].toFixed(1))
        .join(" ");
}

/* Money display only — BN-007 South-Asian grouping; null-safe. */
function fmtBDT(v) {
    return v == null ? "—" : `৳ ${Number(v).toLocaleString("en-IN")}`;
}

function fmtNum(v) {
    return v == null ? "—" : Number(v).toLocaleString("en-IN");
}

/* Chart palette resolves through the conformance token aliases (CFM-01). */
const CHART_VARS = [
    "var(--chart-1)", "var(--chart-2)", "var(--chart-3)", "var(--chart-4)",
    "var(--chart-5)", "var(--chart-6)", "var(--chart-7)", "var(--chart-8)",
];

function fxSparkSvg(data, colorVar) {
    if (!data || data.length < 2) return "";
    const w = 52, h = 18;
    const mn = Math.min(...data);
    let mx = Math.max(...data);
    if (mx === mn) mx = mn + 1;
    const pts = data.map((v, i) => [
        2 + (i * (w - 4)) / (data.length - 1),
        h - 2 - ((v - mn) / (mx - mn)) * (h - 4),
    ]);
    return `<svg class="spark" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" aria-hidden="true">` +
        `<path d="${path(pts)}" fill="none" stroke="${colorVar}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>` +
        `<circle cx="${pts[pts.length - 1][0].toFixed(1)}" cy="${pts[pts.length - 1][1].toFixed(1)}" r="2" fill="${colorVar}"/>` +
        `</svg>`;
}

function fxLineSvg(labels, values) {
    if (!values || values.every((v) => !v)) return "";
    const W = 480, H = 180, padL = 40, padB = 24, padT = 12;
    const mx = Math.max(...values, 1) * 1.08;
    const mn = 0;
    const X = (i) => padL + (i * (W - padL - 8)) / (labels.length - 1);
    const Y = (v) => H - padB - ((v - mn) / (mx - mn)) * (H - padB - padT);
    const col = CHART_VARS[0];

    let g = `<svg width="${W}" height="${H}" role="img" aria-label="Service orders — 12-month trend chart" class="chart">`;
    for (let k = 0; k <= 4; k++) {
        const yy = padT + (k * (H - padB - padT)) / 4;
        const val = mx - (k * (mx - mn)) / 4;
        g += `<line x1="${padL}" x2="${W - 6}" y1="${yy}" y2="${yy}" stroke="var(--stroke)" stroke-width="1"/>` +
            `<text x="${padL - 6}" y="${yy + 3}" text-anchor="end" font-size="9" fill="var(--ink-500)">${Math.round(val)}</text>`;
    }
    labels.forEach((l, i) => {
        g += `<text x="${X(i)}" y="${H - 6}" text-anchor="middle" font-size="9" fill="var(--ink-500)">${esc(l)}</text>`;
    });
    const pts = values.map((v, i) => [X(i), Y(v)]);
    g += `<path d="${path(pts)}" fill="none" stroke="${col}" stroke-width="2.2" stroke-linecap="round"/>`;
    pts.forEach(([x, y]) => {
        g += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="3" fill="${col}"/>`;
    });
    g += `<rect x="${padL + 180}" y="4" width="8" height="8" fill="${col}"/>` +
        `<text x="${padL + 192}" y="12" font-size="9" fill="var(--ink-900)">Service orders / month</text>`;
    return g + "</svg>";
}

function fxDonutSvg(data, centre, centreSub) {
    if (!data || !data.length) return "";
    const S = 180, R = S / 2 - 14, r = R - 24, cx = S / 2, cy = S / 2;
    const total = data.reduce((a, b) => a + b.v, 0);
    if (!total) return "";
    let a0 = -Math.PI / 2;
    let paths = "";
    data.forEach((d, i) => {
        const span = (d.v / total) * 2 * Math.PI;
        const a1 = a0 + span;
        const large = span > Math.PI ? 1 : 0;
        const dStr =
            `M ${cx + R * Math.cos(a0)} ${cy + R * Math.sin(a0)} ` +
            `A ${R} ${R} 0 ${large} 1 ${cx + R * Math.cos(a1)} ${cy + R * Math.sin(a1)} ` +
            `L ${cx + r * Math.cos(a1)} ${cy + r * Math.sin(a1)} ` +
            `A ${r} ${r} 0 ${large} 0 ${cx + r * Math.cos(a0)} ${cy + r * Math.sin(a0)} Z`;
        paths += `<path d="${dStr}" fill="${CHART_VARS[i % CHART_VARS.length]}" stroke="var(--surface)" stroke-width="1.5"/>`;
        a0 = a1;
    });
    return `<svg width="${S}" height="${S}" viewBox="0 0 ${S} ${S}" role="img" aria-label="Intake channel mix donut chart" class="chart">` +
        paths +
        `<circle cx="${cx}" cy="${cy}" r="${r - 1}" fill="var(--surface)"/>` +
        `<text x="${cx}" y="${cy - 2}" text-anchor="middle" font-size="13" font-weight="700" fill="var(--ink-900)">${esc(centre || "")}</text>` +
        `<text x="${cx}" y="${cy + 12}" text-anchor="middle" font-size="8" fill="var(--ink-500)">${esc(centreSub || "")}</text>` +
        `</svg>`;
}

/* BPF stage ids ↔ model states (AS-06 vocabulary). */
const STAGE_OF_STATE = {
    draft: 1, intake: 1, diagnostic: 2, estimate_pending: 3,
    estimate_sent: 3, awaiting_approval: 3, approved: 4, in_repair: 5,
    qc_pending: 6, qc_failed: 5, ready: 7, delivered: 8, closed: 8,
    cancelled: 8,
};
const STATE_OF_STAGE = {
    1: "intake", 2: "diagnostic", 3: "estimate_pending", 4: "approved",
    5: "in_repair", 6: "qc_pending", 7: "ready", 8: "delivered",
};

const SERVICE_TYPE_LABELS = {
    // mirrors fix.service.order.service_type (16 channels) — D10 fix, M01
    // audit 2026-11-06: legends/tables must never fall back to raw keys.
    walk_in: "Walk-in Counter", collection: "Collection/Delivery",
    onsite: "On-site", mail_in: "Mail-in", corporate: "Corporate/Bulk",
    web_portal: "Web Portal (P01)", mobile_app: "Customer Mobile App (P04)",
    whatsapp: "WhatsApp (M27)", ai_assistant: "AI Assistant (M32)",
    hotline: "Hotline 16743", email: "Email Intake",
    b2b_bulk: "B2B Portal Bulk Upload", marketplace: "Marketplace (M12)",
    partner_referral: "Partner Referral (M40)", msp_alert: "MSP Alert (M05)",
    pm_schedule: "Contract Preventive Schedule (M08)",
};

const STATE_LABELS = {
    draft: "Draft", intake: "Received", diagnostic: "Diagnosing",
    estimate_pending: "Estimate", estimate_sent: "Estimate Sent",
    awaiting_approval: "Awaiting Approval", approved: "Approved",
    in_repair: "In Progress", qc_pending: "QC Check", qc_failed: "QC Rework",
    ready: "Ready", delivered: "Delivered", closed: "Closed",
    cancelled: "Cancelled",
    pending: "Pending", assigned: "Assigned", in_progress: "In Progress",
    completed: "Completed", failed: "Failed",
};

const ATTACH_ICONS = { pdf: "📋", jpg: "📷", jpeg: "📷", png: "🔬", webp: "📷" };

export class P03Workspace extends Component {
    static template = "cd_p03_portal.P03Workspace";

    setup() {
        this.areas = P03_AREAS;
        this.modules = P03_MODULES;
        this.roles = P03_ROLES;
        this.rpc = rpc;
        try {
            this.rpcService = useService("rpc");
        } catch (_) {
            this.rpcService = rpc;
        }
        this.actionService = useService("action");
        this.userService = user;
        try {
            this.userService = useService("user") || user;
        } catch (_) {
            this.userService = user;
        }

        // ---- language (DE-17): exactly ONE language at a time. Priority:
        // portal embed hint → per-browser memory → the Odoo user's lang.
        // The toggle persists; embedded portals push p03:set-locale.
        this._onEmbedLocale = (ev) => {
            const data = ev.data || {};
            if (data.type === "p03:set-locale" && (data.locale === "bn" || data.locale === "en")) {
                this.setLang(data.locale, { persist: true });
            }
        };

        this.state = useState({
            viewMode: "home", // 'home' | 'workspace' | 'freg' | 'screen' | 'record' | 'console' | 'form' | 'dispatch_console' | 'branch_console' | 'workshop_console'
            activeTab: "home",
            openTabs: [
                { id: "home", title: "Role Center", icon: "⊞", mode: "home" }
            ],

            // 15 Role Workspaces State (RP-004 §4.2)
            activeRoleId: "service_intake",
            dispatchMapData: null,
            consoleData: null,
            selectedBranchId: null,
            mapSelectedPin: null,
            mapZoom: "dhaka", // 'national' | 'dhaka'
            quickDispatchModalOpen: false,
            quickDispatchOrder: null,

            activeModuleId: "M01",
            activeModule: P03_MODULES.M01,

            // Sub-Module Capability State (freg)
            activeFreg: null,

            // Operational Screen State (screen / grid)
            activeScreen: null,
            gridFilter: {
                branch: "All branches",
                status: "All",
                search: "",
                viewPill: "all"
            },
            filteredGridRows: [],

            // Master-Detail Record State — populated ONLY from the backend
            activeRecord: null,
            recordActiveTab: "overview",
            recordLines: [],
            recordAttachments: [],
            recordAuditTrail: [],

            // M19 GL in-workspace screens (the D365 pilot): one state object
            // carrying the active screen kind, its live data from /p03/gl/*,
            // the CoA FactBox selection, the JE editor and the close console.
            gl: null,

            // 5-Tab Enterprise Data-Entry Form Modal State — blank inputs
            formModalOpen: false,
            modalStep: 1,
            formData: this.blankForm(),

            // Navigation and Shell State
            navExpanded: true,
            moduleSearchQuery: "",
            megaMenuOpen: false,
            tellMeOpen: false,
            tellMeQuery: "",
            tellMeLiveRecords: [],
            jobCardModalOpen: false,
            dispatchModalOpen: false,
            inventoryModalOpen: false,
            theme: "light",
            density: "compact",
            lang: "en",
            personaId: "super_admin",
            toastMessage: "",
            toastVisible: false,

            // Modal forms — blank; validated server-side (AS-09)
            dispatchForm: { technician: "", vanRoute: "", etaWindow: "", notes: "" },
            inventoryForm: { partSku: "", partName: "", qty: 1, bin: "" },

            // Live backend caches
            stats: null,
            recentOrders: [],

            // Universal RECORD TAB pane (user directive 2026-10-29: a record
            // opens in its OWN tab, never inline below the grid). Holds
            // { tabId, kind, id, title, subtitle, loading, data, error, ... }.
            recView: null,
        });

        // Per-tab record payload cache: switching between record tabs is
        // instant and in-progress data is not refetched (ServiceNow/xmatix
        // session-tab guidance — state preservation on return).
        this._recCache = {};
        this._REC_TAB_CAP = 16;

        this.bpfStages = [
            { id: 1, name: "Received", state: "intake" },
            { id: 2, name: "Diagnosing", state: "diagnostic" },
            { id: 3, name: "Estimate", state: "estimate_pending" },
            { id: 4, name: "Approved", state: "approved" },
            { id: 5, name: "In Progress", state: "in_repair" },
            { id: 6, name: "QC Check", state: "qc_pending" },
            { id: 7, name: "Ready for Delivery", state: "ready" },
            { id: 8, name: "Delivered", state: "delivered" }
        ];

        // Branch filter list — real fix.branch values, loaded with stats.
        this.branchOptions = [];

        // Global Alt+Q / Ctrl+K Tell-ME shortcut
        if (typeof window !== "undefined") {
            window.addEventListener("keydown", (ev) => {
                if ((ev.altKey && (ev.key === "q" || ev.key === "Q")) || ((ev.ctrlKey || ev.metaKey) && ev.key === "k")) {
                    ev.preventDefault();
                    this.state.tellMeOpen = !this.state.tellMeOpen;
                } else if (ev.key === "Escape" && this.state.tellMeOpen) {
                    this.state.tellMeOpen = false;
                }
            });
        }

        // --- P01 portal embed channel --------------------------------------
        // The Next.js customer portal embeds this workspace in a cross-origin
        // iframe (:3000 framing :8069 — allowed by cd_portal_embed's frame
        // policy) and drives it to a module/screen via postMessage. The
        // parent retries `p03:open` until the ack below, so mounting order
        // is irrelevant.
        this._onPortalMessage = (ev) => {
            const data = ev && ev.data;
            if (!data || data.type !== "p03:open") {
                return;
            }
            const mid = P03_MODULES[data.m] ? data.m : null;
            if (!mid) {
                return;
            }
            // Set the module BEFORE the screen: openScreen alone leaves the
            // breadcrumb and the module rail on whatever was last open, so a
            // deep-linked screen showed another module's context entirely
            // (A04 audit, 2026-10-31 — the P01 portal embed uses this path).
            this.openModule(mid);
            if (data.s && typeof data.s === "string" && data.s.length <= 64) {
                this.openScreen(data.s);
            }
            if (ev.source && ev.source.postMessage) {
                ev.source.postMessage(
                    { type: "p03:opened", m: mid, s: data.s || null },
                    ev.origin
                );
            }
        };
        window.addEventListener("message", this._onPortalMessage);
        this._initLang();
        window.addEventListener("message", this._onEmbedLocale);
        onMounted(() => {
            // A11y: suppress keyboard trap on hidden Odoo stock navbar
            const nav = document.querySelector(".o_navbar");
            if (nav) {
                nav.setAttribute("aria-hidden", "true");
                nav.setAttribute("inert", "");
            }
        });

        onWillUnmount(() => {
            const nav = document.querySelector(".o_navbar");
            if (nav) {
                nav.removeAttribute("aria-hidden");
                nav.removeAttribute("inert");
            }
            window.removeEventListener("message", this._onPortalMessage);
            if (this._onEmbedLocale) window.removeEventListener("message", this._onEmbedLocale);
        });

        onWillStart(async () => {
            await Promise.all([
                this.loadStats(),
                this.loadRecentOrders(),
                this.loadDispatchMap(),
                this.loadConsoleData(),
            ]);
            // client-action params (mega menu / deep links): the action may
            // carry {module_id, screen_id} — land directly on that screen.
            const params =
                (this.props && (this.props.actionParams || (this.props.action && this.props.action.params))) || {};
            const mid = params.module_id || params.moduleId;
            const sid = params.screen_id || params.screenId;
            if (mid && P03_MODULES[mid]) {
                this.openModule(mid);
                if (sid && typeof sid === "string" && sid.length <= 64) {
                    this.openScreen(sid);
                }
            }
        });
    }

    blankForm() {
        return {
            customer_name: "",
            customer_phone: "",
            branch_name: "",
            service_type: "walk_in",
            entitlement: "standard",
            corporate_client: "",
            priority: "normal",
            brand: "",
            model: "",
            serial: "",
            fault_description: "",
            fault_description_bn: "",
            pre_existing_damage: false,
            power_adapter_received: false,
            lines: [{ desc: "", type: "Part", qty: 1, price: 0 }]
        };
    }

    async loadStats() {
        try {
            const res = await this.rpc("/p03/stats", {});
            if (res) {
                this.state.stats = res;
                this.branchOptions = res.branches || [];
                this.technicianOptions = res.technicians || [];
            }
        } catch (e) {
            console.warn("Could not fetch /p03/stats:", e);
        }
    }

    async loadDispatchMap() {
        try {
            const res = await this.rpc("/p03/dispatch/map_data", {});
            if (res && res.success) {
                this.state.dispatchMapData = res;
            }
        } catch (e) {
            console.warn("Could not fetch /p03/dispatch/map_data:", e);
        }
    }

    async loadConsoleData(branchId) {
        try {
            const params = branchId ? { branch_id: branchId } : {};
            const res = await this.rpc("/p03/consoles/data", params);
            if (res && res.success) {
                this.state.consoleData = res;
            }
        } catch (e) {
            console.warn("Could not fetch /p03/consoles/data:", e);
        }
    }

    // --- 15 Role Workspaces Getters & Actions ---
    get activeRole() {
        if (Array.isArray(this.roles)) {
            return this.roles.find(r => r.id === this.state.activeRoleId) || this.roles[0] || {};
        }
        return (this.roles && this.roles[this.state.activeRoleId]) || {};
    }

    get rolesList() {
        return Array.isArray(this.roles) ? this.roles : Object.values(this.roles || {});
    }

    /* Registry totals computed from the loaded meta so rendered copy (mega
     * menu header, rail annotations) can never drift from the data. */
    get areaCount() {
        return this.areas.length;
    }

    get moduleCount() {
        return Object.keys(this.modules).length;
    }

    switchRole(roleId) {
        const r = this.rolesList.find(role => role.id === roleId);
        if (r) {
            this.state.activeRoleId = roleId;
            this.showToast(`Switched workspace: ${r.en} (${r.code})`);
        }
    }

    // --- Dispatch Console & Interactive Live Map Methods ---
    setMapZoom(zoom) {
        this.state.mapZoom = zoom;
    }

    projectCoord(lat, lng, width = 640, height = 480) {
        if (!lat || !lng) return { x: Math.round(width / 2), y: Math.round(height / 2) };
        if (this.state.mapZoom === "dhaka") {
            const minLat = 23.68, maxLat = 23.92;
            const minLng = 90.32, maxLng = 90.48;
            const x = ((lng - minLng) / (maxLng - minLng)) * (width - 80) + 40;
            const y = height - (((lat - minLat) / (maxLat - minLat)) * (height - 80) + 40);
            return {
                x: Math.max(25, Math.min(width - 25, Math.round(x))),
                y: Math.max(25, Math.min(height - 25, Math.round(y)))
            };
        } else {
            const minLat = 20.6, maxLat = 26.6;
            const minLng = 88.0, maxLng = 92.8;
            const x = ((lng - minLng) / (maxLng - minLng)) * (width - 80) + 40;
            const y = height - (((lat - minLat) / (maxLat - minLat)) * (height - 80) + 40);
            return {
                x: Math.max(25, Math.min(width - 25, Math.round(x))),
                y: Math.max(25, Math.min(height - 25, Math.round(y)))
            };
        }
    }

    get branchPins() {
        const branches = this.state.dispatchMapData?.branches || [];
        return branches.map(b => {
            const pt = this.projectCoord(b.lat, b.lng);
            return { ...b, x: pt.x, y: pt.y };
        });
    }

    get techPins() {
        const techs = this.state.dispatchMapData?.technicians || [];
        return techs.map(t => {
            const pt = this.projectCoord(t.lat, t.lng);
            return { ...t, x: pt.x, y: pt.y };
        });
    }

    get orderPins() {
        const orders = this.state.dispatchMapData?.orders || [];
        return orders.map(o => {
            const pt = this.projectCoord(o.lat, o.lng);
            return { ...o, x: pt.x, y: pt.y };
        });
    }

    get dhakaGeofenceCircle() {
        const pt = this.projectCoord(23.8000, 90.4000);
        const r = this.state.mapZoom === "dhaka" ? 140 : 26;
        return { cx: pt.x, cy: pt.y, r };
    }

    selectMapPin(item, pinType) {
        this.state.mapSelectedPin = { ...item, pinType };
    }

    clearMapPin() {
        this.state.mapSelectedPin = null;
    }

    openQuickDispatch(order) {
        this.state.quickDispatchOrder = order;
        this.state.quickDispatchModalOpen = true;
    }

    closeQuickDispatch() {
        this.state.quickDispatchModalOpen = false;
        this.state.quickDispatchOrder = null;
    }

    async assignTechFromMap(techName) {
        const orderId = this.state.quickDispatchOrder?.id ||
                        (this.state.mapSelectedPin?.pinType === "order" ? this.state.mapSelectedPin.id : null);
        if (!orderId) {
            this.showToast(t('Please select an active order to assign.'));
            return;
        }
        try {
            const res = await this.rpc("/p03/dispatch/assign", {
                order_id: orderId,
                technician: techName,
            });
            if (res && res.success) {
                this.showToast(`Technician ${res.technician} assigned to order #${orderId} ✓`);
                this.closeQuickDispatch();
                this.clearMapPin();
                await Promise.all([
                    this.loadDispatchMap(),
                    this.loadRecentOrders(),
                ]);
            } else {
                this.showToast(res?.error || "Dispatch assignment refused.");
            }
        } catch (err) {
            this.showToast(t('Dispatch assignment failed — see server log.'));
        }
    }

    // --- Consoles Navigation & Instant Operations ---
    openDispatchConsole() {
        this.state.viewMode = "dispatch_console";
        this.ensureTab("console-dispatch", "🗺 Dispatch Console & Map", "🗺", "dispatch_console");
        this.loadDispatchMap();
    }

    openBranchConsole() {
        this.state.viewMode = "branch_console";
        this.ensureTab("console-branch", "🏢 Branch Operations Console", "🏢", "branch_console");
        this.loadConsoleData(this.state.selectedBranchId);
    }

    openWorkshopConsole() {
        this.state.viewMode = "workshop_console";
        this.ensureTab("console-workshop", "🔧 Workshop & Bench Console", "🔧", "workshop_console");
        this.loadConsoleData(this.state.selectedBranchId);
    }

    async filterBranchConsole(branchId) {
        this.state.selectedBranchId = branchId ? parseInt(branchId) : null;
        await this.loadConsoleData(this.state.selectedBranchId);
        this.showToast(branchId ? `Branch filter updated: #${branchId}` : "Showing all branches");
    }

    async quickNotifyCustomer(customerName, orderId) {
        // REAL action: logs a collection notification on the order's
        // chatter (mail.thread) — the SMS channel dispatch itself lands
        // with the M27 notification phase; no fabricated "queued" claims.
        try {
            const res = await this.rpc("/p03/notify/collection", {
                order_id: orderId,
            });
            if (res && res.success) {
                this.showToast(`Collection notification logged to ${res.order} chatter ✓`);
            } else {
                this.showToast(res?.error || "Notification failed — see server log.");
            }
        } catch (e) {
            this.showToast(t('Notification failed — see server log.'));
        }
    }

    async quickPassQC(orderId) {
        try {
            const res = await this.rpc("/p03/service_order/advance", {
                order_id: orderId,
                target_state: "ready",
            });
            if (res && res.success) {
                this.showToast(`Order #${orderId} passed QC inspection and marked Ready for Collection ✓`);
                await Promise.all([
                    this.loadConsoleData(this.state.selectedBranchId),
                    this.loadRecentOrders(),
                ]);
            } else {
                this.showToast(res?.error || "Failed to advance order.");
            }
        } catch (e) {
            this.showToast(t('QC advance failed — see server log.'));
        }
    }

    async quickReworkQC(orderId) {
        try {
            const res = await this.rpc("/p03/service_order/advance", {
                order_id: orderId,
                target_state: "in_repair",
            });
            if (res && res.success) {
                this.showToast(`Order #${orderId} failed QC — returned to bench for rework ⚠`);
                await Promise.all([
                    this.loadConsoleData(this.state.selectedBranchId),
                    this.loadRecentOrders(),
                ]);
            } else {
                this.showToast(res?.error || "Failed to flag order for rework.");
            }
        } catch (e) {
            this.showToast(t('QC rework update failed — see server log.'));
        }
    }


    /* Template-safe formatting helpers (null → em dash, never a crash). */
    fmtBDT(v) { return fmtBDT(v); }
    fmtNum(v) { return fmtNum(v); }
    stateLabel(s) { return this.tState(s) !== s ? this.tState(s) : (STATE_LABELS[s] || s || "—"); }
    serviceTypeLabel(s) { return SERVICE_TYPE_LABELS[s] || s || "—"; }
    get jobCardDate() {
        return new Date().toLocaleDateString("en-GB",
            { day: "2-digit", month: "short", year: "numeric" }).toUpperCase();
    }

    /* Module KPI labels (values land with each module's wiring phase). */
    get kpiLabels() {
        return (this.state.activeModule.kpis || []).map(k => k.l);
    }

    /* KPI objects for the module view; `m` is the metric key served by
     * /p03/finance/kpis (real Odoo reads) when the module has live KPIs. */
    get moduleKpis() {
        return this.state.activeModule.kpis || [];
    }

    kpiValue(kpi) {
        if (kpi.m && this.state.financeKpis && this.state.financeKpis[kpi.m] != null) {
            const v = this.state.financeKpis[kpi.m];
            // BN-007 South-Asian grouping, same as the grids (lakh/crore) —
            // a KPI and its report must not disagree on digit grouping
            const num = typeof v === "number"
                ? v.toLocaleString("en-IN", { maximumFractionDigits: 2 })
                : String(v);
            // `suffix` declares the unit on the fragment's KPI (%, ৳, h…) —
            // a bare number on a rate tile reads as a count (audit D2);
            // `prefix` does the same for money (৳ 65,700).
            return (kpi.prefix || "") + num + (kpi.suffix || "");
        }
        return "—";
    }

    kpiLive(kpi) {
        return !!(kpi.m && this.state.financeKpis && this.state.financeKpis[kpi.m] != null);
    }

    /* Is this registry screen backed by a real Odoo model (A08 live map) or
     * an in-workspace data screen (M19 GL pilot)? */
    screenLive(screenId) {
        return !!(P03_LIVE_SCREENS[screenId] || P03_DATA_SCREENS[screenId]);
    }

    /* The module's "+ New" label — finance modules create their OWN record
     * type (P03_MODULE_CREATE), everything else stays the service order. */
    get newButtonLabel() {
        const create = P03_MODULE_CREATE[this.state.activeModuleId];
        return create ? `+ ${this.t(create.label)}` : this.t("+ New Service Order");
    }

    onModuleNew() {
        const mid = this.state.activeModuleId;
        const create = P03_MODULE_CREATE[mid];
        if (create) {
            // M19's manual entry is the in-workspace D365 editor (draft →
            // SoD review), not the stock Odoo form.
            if (mid === "M19") {
                this.openGlJeEditor();
                return;
            }
            // M20's manual-exception invoice is the in-workspace editor too
            if (mid === "M20") {
                this.openScreen("M20-invoice");
                return;
            }
            if (create.screen && P03_DATA_SCREENS[create.screen]) {
                const cfg = P03_DATA_SCREENS[create.screen];
                this.openFormScreen(
                    create.screen,
                    { sc: { en: cfg.title || create.label, t: "f" }, m: { title: (this.state.activeModule && this.state.activeModule.title) || "" } },
                    cfg
                );
                return;
            }
            if (this.openModuleFormForModel(create.model)) {
                return;
            }
            this.openModelForm(create.model, create.label);
            return;
        }
        this.openNewForm();
    }

    /* Open a REAL Odoo form view for a model — LAST-RESORT fallback only.
     * D365 screen convention (user directive 2026-10-27): data-entry chips
     * open the module's in-workspace D365 form screen (P03_FORM_CHIPS →
     * P03_DATA_SCREENS model_form). A dialog is used only when the module
     * declares no form screen for the target model. */
    openModelForm(resModel, label) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: label || "New Record",
            res_model: resModel,
            views: [[false, "form"]],
            target: "new",
        });
    }

    /* Open the in-workspace D365 form for a model when the active module
     * declares one. Screen-specific overrides win (e.g. the Leads grid
     * creates a lead, the Opportunities grid an opportunity), then the
     * model map. Returns true when it opened. */
    openModuleFormForModel(model, recordId) {
        const mid = this.state.activeModuleId;
        const chips = P03_FORM_CHIPS || {};
        const byScreen = chips[`${mid}:__by_screen__`] || {};
        const byModel = chips[`${mid}:__by_model__`] || {};
        const gl = this.state.gl;
        const screenId = gl && gl.screenId;
        const formScreen = (screenId && byScreen[screenId]) || byModel[model];
        if (formScreen && P03_DATA_SCREENS[formScreen]) {
            const cfg = { ...P03_DATA_SCREENS[formScreen], recordId: recordId || null };
            this.openFormScreen(formScreen, this.state.activeScreen ? { sc: this.state.activeScreen, m: { title: (this.state.activeModule && this.state.activeModule.title) || "" } } : null, cfg);
            return true;
        }
        return false;
    }

    /* Data-entry form chips: A08 modules open their real model form; other
     * modules keep the generic intake flow. Never the wrong-module form. */
    openFormChip(formLabel) {
        const mid = this.state.activeModuleId;
        if (mid === "M19" && /journal entry/i.test(formLabel)) {
            this.openGlJeEditor();
            return;
        }
        if (mid === "M20") {
            if (/invoice request/i.test(formLabel)) {
                this.openScreen("M20-invoice");
                return;
            }
            // Receipt / Credit Note / Refund / Payment Link / VDS now have
            // their own D365 form screens (P03_FORM_CHIPS) — the old
            // list-routing shortcuts are gone (D17: a form chip must never
            // land on a list).
        }
        // D365 form screen wins FIRST: a chip with an in-workspace form
        // routes even when the module declares no FORM_MODELS entry (M01's
        // Estimate/QC chips hit this — the check used to sit inside the
        // `mapped` branch and never ran; audit D-M01-3).
        const chipScreen = (P03_FORM_CHIPS && P03_FORM_CHIPS[`${mid}:${formLabel}`]) || null;
        if (chipScreen && P03_DATA_SCREENS[chipScreen]) {
            const cfg = P03_DATA_SCREENS[chipScreen];
            this.openFormScreen(
                chipScreen,
                { sc: { en: cfg.title || formLabel, t: "f" }, m: { title: (this.state.activeModule && this.state.activeModule.title) || "" } },
                cfg
            );
            return;
        }
        const mapped = P03_FORM_MODELS[`${mid}:${formLabel}`];
        if (mapped) {
            this.openModelForm(mapped, formLabel);
            return;
        }
        if (mid === "M19" && /intercompany/i.test(formLabel)) {
            this.showToast(t('Intercompany charges land with the multi-entity phase (FR-FIN-026..031)'));
            return;
        }
        const create = P03_MODULE_CREATE[mid];
        if (create) {
            // Module has a live create surface — use it rather than nothing.
            if (create.screen && P03_DATA_SCREENS[create.screen]) {
                const cfg = P03_DATA_SCREENS[create.screen];
                this.openFormScreen(
                    create.screen,
                    { sc: { en: cfg.title || create.label, t: "f" }, m: { title: (this.state.activeModule && this.state.activeModule.title) || "" } },
                    cfg
                );
                return;
            }
            if (this.openModuleFormForModel(create.model)) {
                return;
            }
            this.openModelForm(create.model, create.label);
            return;
        }
        this.openNewForm();
    }

    /* Report exports: the download hits the SAME pack function the screen
     * renders — the export cannot drift from what the user sees. xlsx is
     * the presentation artefact (brand header, meta, totals); csv is raw.
     */
    exportReport(format) {
        const gl = this.state.gl;
        const cfg = gl && gl.reportCfg;
        if (!cfg) return;
        const params = new URLSearchParams({ module: cfg.module, report: cfg.report, format });
        if (cfg.period !== false) {
            params.set("date_from", gl.stmtFrom);
            params.set("date_to", gl.stmtTo);
        }
        Object.entries(cfg.params || {}).forEach(([k, v]) => params.set(k, v));
        Object.entries(gl.reportFilters || {}).forEach(([k, v]) => {
            if (v && v !== "All") params.set(k, v);
        });
        window.open(`/p03/model/report/export?${params.toString()}`, "_blank");
    }

    /* Print-ready PDF document: a self-contained page (brand header,
     * report meta, repeating table head, totals, notes, footer) — the
     * browser's Save-as-PDF produces the professional artefact; the app
     * chrome never leaks into the document. */
    printReportPdf() {
        const html = this._reportPrintHtml();
        if (!html) { this.showToast(this.t("Print preparation failed")); return; }
        this._reportPrintFrame(html);
    }

    /* Write the print document into a hidden iframe and print THAT — no
     * popup blocker can stop it, and it works inside the portal embed. */
    _reportPrintFrame(docHtml) {
        const frame = document.createElement("iframe");
        frame.setAttribute("aria-hidden", "true");
        frame.style.cssText = "position:fixed;right:0;bottom:0;width:0;height:0;border:0;visibility:hidden;";
        document.body.appendChild(frame);
        frame.contentDocument.open();
        frame.contentDocument.write(docHtml);
        frame.contentDocument.close();
        frame.contentWindow.addEventListener("afterprint", () => setTimeout(() => frame.remove(), 60000));
        setTimeout(() => {
            frame.contentWindow.focus();
            frame.contentWindow.print();
        }, 150);
    }

    _reportPrintHtml() {
        const gl = this.state.gl;
        const cfg = gl && gl.reportCfg;
        const data = gl && gl.data;
        if (!cfg || !data || data.error) return null;
        const labels = data.labels || {};
        const esc = (s) => String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        const fmt = (v) => (typeof v === "number" ? v.toLocaleString() : esc(v));
        const filtersMeta = Object.entries(gl.reportFilters || {})
            .filter(([, v]) => v && v !== "All")
            .map(([k, v]) => `${esc(k)}: ${esc(v)}`)
            .join(" · ");
        const period = cfg.period !== false ? `${esc(gl.stmtFrom || "…")} → ${esc(gl.stmtTo || "…")}` : "";
        const cols = data.cols || [];
        const totals = data.totals || {};
        const landscape = cols.length > 6 ? "@page { size: A4 landscape; margin: 14mm 12mm; }" : "@page { size: A4; margin: 16mm 14mm; }";
        return `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${esc(data.title || "Report")}</title>
<style>
${landscape}
body { font-family: Inter, "Segoe UI", "Noto Sans Bengali", sans-serif; color: #242424; margin: 0; }
.doc-head { display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 3px solid #0E7A6E; padding-bottom: 8px; margin-bottom: 12px; }
.brand { font-size: 18px; font-weight: 700; color: #0E7A6E; }
.brand small { display: block; font-size: 10px; font-weight: 400; color: #616161; }
h1 { font-size: 15px; margin: 0 0 2px; }
.meta { font-size: 10px; color: #616161; margin-bottom: 10px; }
table { width: 100%; border-collapse: collapse; font-size: 11px; }
thead { display: table-header-group; }
th { background: #0E7A6E; color: #fff; text-align: left; padding: 5px 8px; font-weight: 600; }
td { padding: 4px 8px; border-bottom: 1px solid #E0E0E0; }
tbody tr:nth-child(even) td { background: #F5F5F5; }
tr { break-inside: avoid; }
td.num, th.num { text-align: right; }
tfoot td, tr.totals td { font-weight: 700; border-top: 2px solid #0E7A6E; border-bottom: none; }
.notes { font-size: 9px; color: #616161; margin-top: 10px; }
.foot { margin-top: 14px; padding-top: 6px; border-top: 1px solid #E0E0E0; font-size: 9px; color: #616161; display: flex; justify-content: space-between; }
</style></head><body>
<div class="doc-head">
  <div class="brand">1000 FiX ERP<small>1000 FiX Services Ltd. — ISO 9001:2015 · Hotline 16743</small></div>
  <div style="text-align:right; font-size:10px; color:#616161;">${new Date().toLocaleString()}</div>
</div>
<h1>${esc(data.title || "")}</h1>
<div class="meta">${period ? "Period: " + period : ""}${filtersMeta ? (period ? " · " : "") + filtersMeta : ""} · Generated by ${esc(this.userService.name || "")}</div>
<table><thead><tr>${cols.map((c) => `<th>${esc(labels[c] || c)}</th>`).join("")}</tr></thead>
<tbody>${(data.rows || []).map((r) => `<tr>${cols.map((c) => `<td class="${typeof r[c] === "number" ? "num" : ""}">${fmt(r[c])}</td>`).join("")}</tr>`).join("")}</tbody>
${Object.keys(totals).length ? `<tfoot><tr>${cols.map((c) => `<td class="${typeof totals[c] === "number" ? "num" : ""}">${fmt(totals[c])}</td>`).join("")}</tr></tfoot>` : ""}
</table>
${(data.notes || []).length ? `<div class="notes">${data.notes.map((n) => "• " + esc(n)).join("<br/>")}</div>` : ""}
<div class="foot"><span>1000 FiX Services Ltd. — confidential internal report</span><span>${(data.rows || []).length} rows</span></div>
</body></html>`;
    }

    /* M32 assistant playground — runs the REAL classifier (/p03/assistant/
     * classify), not a canned demo. */
    assistantSet(text) {
        if (this.state.gl) this.state.gl.assistantText = text;
    }

    async assistantAsk() {
        const gl = this.state.gl;
        if (!gl || gl.assistantBusy) return;
        gl.assistantBusy = true;
        try {
            const res = await this.rpc("/p03/assistant/classify", { text: gl.assistantText || "" });
            gl.assistantResult = res && !res.error ? res : { error: (res && res.error) || "The assistant did not answer." };
        } catch (e) {
            gl.assistantResult = { error: this.t("Connection lost — press ↻ Refresh to reload this screen.") };
        }
        gl.assistantBusy = false;
        this.render(true);
    }

    /* ================================================================
     * M19 GL IN-WORKSPACE SCREENS — the Dynamics-365 pilot. Every screen
     * of the Financial Accounting & GL module renders INSIDE this shell
     * from live /p03/gl/* data; nothing leaves to a stock Odoo view.
     * ================================================================ */

    _glFyWindow() {
        // BD fiscal year July-June. Dates are formatted from LOCAL parts —
        // toISOString() is UTC and shifts both edges back a day east of UTC.
        const now = new Date();
        const y = now.getFullYear();
        const start = now.getMonth() >= 6 ? new Date(y, 6, 1) : new Date(y - 1, 6, 1); // July = month 6
        const end = new Date(start.getFullYear() + 1, 5, 30);
        const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
        return [iso(start), iso(end)];
    }

    openGlScreen(screenId, hit, config) {
        const [fyFrom, fyTo] = this._glFyWindow();
        this.state.gl = {
            screenId,
            hitSc: hit ? hit.sc : null,
            hitM: hit ? hit.m : null,
            modelCfg: config.model ? config : null,
            reportCfg: config.kind === "table_report" ? config : null,
            reportFilters: {},
            cfg: config,
            kind: config.kind,
            report: config.report || null,
            title: hit ? hit.sc.en : "GL",
            moduleTitle: hit ? hit.m.title : "M19 · Financial Accounting & GL",
            data: null,
            loading: true,
            error: null,
            // CoA
            selected: null,
            coaType: "all",
            coaSearch: "",
            // journals
            journalPill: "all",
            drillCode: null,
            jeDetail: null,
            // statement
            stmtFrom: fyFrom,
            stmtTo: fyTo,
            // close console
            selectedCloseId: null,
            evidenceStep: null,
            evidenceText: "",
            // JE editor
            editor: null,
            // ---- M20 AR screens ----
            arState: "all",          // invoice state filter
            arDetail: null,          // invoice record view
            arEditor: null,          // manual invoice editor
            arNoteForm: null,        // credit-note quick create (per invoice)
            receiptForm: null,       // receipt quick create
            allocPick: { receipt_id: null, invoice_id: null, amount: null }, // manual allocation
            matchProposals: null,    // auto-match console
            customers: [],           // picker for statements/editor
            stmtCustomer: null,      // statement customer
            arFrom: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().slice(0, 10),
            arTo: new Date().toISOString().slice(0, 10),
            asOfDate: new Date().toISOString().slice(0, 10),
            snapDetail: null,        // captured snapshot rows
            assistantText: "",
            assistantResult: null,
            assistantBusy: false,
            prompt: null,            // generic reason prompt {title,label,action,id,value}
            mlState: "__all",        // model_list state filter
            mlSelected: null,        // model_list selected row
            // ---- M01 service-order screens ----
            soCfg: config.scope || config.kind === "so_board" || config.kind === "so_intake" ? config : null,
            soScope: config.scope || null,   // all|wip|holds|rework|rwty
            soSearch: "",
            soState: "all",          // state filter pill on so_list
            boardCol: null,          // selected pipeline column (so_board)
            soBusy: null,            // order id with an action in flight
            // ---- M02 field-service screens ----
            fsSuggest: null,         // suggestions for the dispatch modal {order, rows}
            fsSuggestPicked: null,   // employee id picked in the modal
            fsBusy: null,            // field order id with an action in flight
        };
        this.state.viewMode = "gl";
        this.ensureTab(`gl-${screenId}`, this.state.gl.title, hit && hit.sc.t === "f" ? "▤" : "⛁", "gl", { screenId });
        this.loadGlData();
    }

    /* Bilingual GL screen titles — re-resolve on every language switch. */
    get glTitle() {
        const gl = this.state.gl;
        if (!gl) return "";
        return (gl.hitSc && this.tBilingual(gl.hitSc)) || gl.title || "";
    }

    /* Heading icon: the owning module's, not a fixed finance glyph — this
     * view now renders every area's in-workspace screens, not just M19's. */
    get glModuleIcon() {
        const gl = this.state.gl;
        return (gl && gl.hitM && gl.hitM.icon) || "⛁";
    }

    get glModuleTitle() {
        const gl = this.state.gl;
        if (!gl) return "";
        return (gl.hitM && this.tBilingual(gl.hitM)) || gl.moduleTitle || "";
    }

    refreshGlScreen() {
        if (this.state.viewMode === "gl" && this.state.gl) this.loadGlData();
    }

    async loadGlData() {
        const gl = this.state.gl;
        if (!gl) return;
        gl.loading = true;
        gl.error = null;
        try {
            if (gl.kind === "coa") {
                gl.data = await this.rpc("/p03/gl/coa", {});
            } else if (gl.kind === "journals") {
                gl.jeDetail = null;
                gl.data = await this.rpc("/p03/gl/journals", {
                    state: gl.journalPill === "all" ? null : gl.journalPill,
                    account_code: gl.drillCode,
                });
            } else if (gl.kind === "je_editor") {
                const [accounts, templates] = await Promise.all([
                    this.rpc("/p03/gl/accounts", {}),
                    this.rpc("/p03/gl/templates", {}),
                ]);
                gl.data = {
                    accounts: accounts.rows,
                    branches: accounts.branches || [],
                    templates: templates.rows,
                };
                if (!gl.editor) this._glNewEditor();
            } else if (gl.kind === "statement") {
                gl.data = await this.rpc("/p03/gl/statements", {
                    report: gl.report,
                    date_from: gl.stmtFrom,
                    date_to: gl.stmtTo,
                });
                if (!gl.data || gl.data.success === false) {
                    gl.error = (gl.data && gl.data.error) || "Statement unavailable";
                    gl.data = null;
                }
            } else if (gl.kind === "close") {
                gl.data = await this.rpc("/p03/gl/close", {});
                if (!gl.selectedCloseId && gl.data.closes.length) {
                    gl.selectedCloseId = gl.data.closes[0].id;
                }
            } else if (gl.kind === "periods") {
                gl.data = await this.rpc("/p03/gl/periods", {});
            } else if (gl.kind === "dimensions") {
                gl.data = await this.rpc("/p03/gl/dimensions", {});
            } else if (gl.kind === "suspense") {
                gl.data = await this.rpc("/p03/gl/suspense", {});
            } else if (gl.kind === "recon") {
                gl.data = await this.rpc("/p03/gl/recon", {});
            } else if (gl.kind === "audit") {
                gl.data = await this.rpc("/p03/gl/audit", {});
            } else if (gl.kind === "ar_invoices" || gl.kind === "ar_brand") {
                gl.arDetail = null;
                gl.data = await this.rpc("/p03/ar/invoices", {
                    state: gl.arState === "all" ? null : gl.arState,
                });
            } else if (gl.kind === "ar_editor") {
                const [customers, invoices] = await Promise.all([
                    this.rpc("/p03/ar/customers", {}),
                    this.rpc("/p03/ar/invoices", { state: "draft" }),
                ]);
                gl.customers = customers.rows;
                gl.data = { drafts: invoices.rows };
                if (!gl.arEditor) this._arNewEditor();
            } else if (gl.kind === "ar_events") {
                gl.data = await this.rpc("/p03/ar/events", {});
            } else if (gl.kind === "ar_consolidated") {
                gl.data = await this.rpc("/p03/ar/consolidated", {});
            } else if (gl.kind === "ar_receipts") {
                gl.data = await this.rpc("/p03/ar/receipts", {});
                if (!gl.customers.length) {
                    const res = await this.rpc("/p03/ar/customers", {});
                    gl.customers = res.rows;
                }
            } else if (gl.kind === "ar_links") {
                gl.data = await this.rpc("/p03/ar/payment-links", {});
            } else if (gl.kind === "ar_allocation") {
                const [match, openItems, receipts] = await Promise.all([
                    this.rpc("/p03/ar/match", {}),
                    this.rpc("/p03/ar/open-items", {}),
                    this.rpc("/p03/ar/receipts", { state: "confirmed" }),
                ]);
                gl.matchProposals = match.proposals;
                gl.data = {
                    exceptions: match.exceptions,
                    open_invoices: openItems.rows,
                    unapplied: receipts.rows.filter((r) => r.unapplied > 0.005),
                };
            } else if (gl.kind === "ar_credit") {
                gl.data = await this.rpc("/p03/ar/credit-profiles", {});
                if (!gl.customers.length) {
                    const res = await this.rpc("/p03/ar/customers", {});
                    gl.customers = res.rows;
                }
            } else if (gl.kind === "ar_dunning" || gl.kind === "ar_disputes") {
                gl.data = await this.rpc("/p03/ar/dunning", {});
            } else if (gl.kind === "ar_refunds") {
                gl.data = await this.rpc("/p03/ar/credit-notes", {});
            } else if (gl.kind === "ar_aging") {
                gl.data = await this.rpc("/p03/ar/aging", {});
                gl.snapDetail = null;
            } else if (gl.kind === "ar_leakage") {
                gl.data = await this.rpc("/p03/ar/leakage", {});
            } else if (gl.kind === "ar_statements") {
                const res = await this.rpc("/p03/ar/customers", {});
                gl.customers = res.rows;
                if (!gl.data) gl.data = { statement: null };
            } else if (gl.kind === "table_report") {
                const cfg = gl.reportCfg;
                const params = Object.assign({}, cfg.params || {});
                if (cfg.period !== false) {
                    params.date_from = gl.stmtFrom;
                    params.date_to = gl.stmtTo;
                }
                // pack-declared filters (channel, group-by, …) ride the same
                // params — exports and screen stay one query
                Object.entries(gl.reportFilters || {}).forEach(([k, v]) => {
                    if (v && v !== "All") params[k] = v;
                });
                const res = await this.rpc("/p03/model/report", {
                    module: cfg.module, report: cfg.report, params,
                });
                gl.data = res.error ? { error: res.error } : res;
            } else if (gl.kind === "model_list") {
                // one silent retry — a restart in flight must not leave the
                // screen parked on an error banner (audit D8: five of the
                // user's PDFs captured exactly that state)
                const fetchRows = () => this.rpc("/p03/model/records", {
                    model: gl.modelCfg.model,
                    cols: gl.modelCfg.cols,
                    domain: gl.modelCfg.domain || [],
                    state_field: gl.modelCfg.stateField || null,
                    state_filter: gl.mlState || "__all",
                    // bilingual headers: field labels follow the UI language
                    lang: this.state.lang === "bn" ? "bn_BD" : "en_US",
                });
                let res;
                try {
                    res = await fetchRows();
                } catch (e1) {
                    await new Promise((r) => setTimeout(r, 1200));
                    res = await fetchRows();
                }
                gl.data = res.error ? { error: res.error } : res;
            } else if (gl.kind === "so_list") {
                const res = await this.rpc("/p03/orders/list", {
                    limit: 200,
                    scope: gl.soScope === "all" ? null : gl.soScope,
                    search: gl.soSearch || null,
                });
                gl.data = res.error ? { error: res.error } : res;
            } else if (gl.kind === "so_board") {
                const [stats, orders] = await Promise.all([
                    this.rpc("/p03/stats", {}),
                    this.rpc("/p03/orders/list", { limit: 100, scope: "wip" }),
                ]);
                gl.data = { stats, orders: orders.orders || [], scope: orders.scope };
            } else if (gl.kind === "so_intake") {
                const [stats, walkins] = await Promise.all([
                    this.rpc("/p03/stats", {}),
                    this.rpc("/p03/model/records", {
                        model: "fix.walkin.intake",
                        cols: ["customer_id", "device_serial_input", "fault_description", "state", "create_date"],
                        state_field: "state",
                        state_filter: "__all",
                    }),
                ]);
                gl.data = { stats, walkins: walkins.error ? [] : (walkins.rows || []).slice(0, 8) };
            } else if (gl.kind === "fs_board") {
                const [kpis, unassigned, active] = await Promise.all([
                    this.rpc("/p03/field/kpis", {}),
                    this.rpc("/p03/model/records", {
                        model: "fix.field.order",
                        cols: ["name", "order_id", "zone_id", "priority", "scheduled_start", "sla_deadline", "state", "technician_id"],
                        domain: [["state", "in", ["draft", "pending_dispatch", "declined"]]],
                    }),
                    this.rpc("/p03/model/records", {
                        model: "fix.field.order",
                        cols: ["name", "order_id", "zone_id", "priority", "scheduled_start", "sla_deadline", "state", "technician_id"],
                        domain: [["state", "in", ["dispatched", "accepted", "en_route", "arrived", "in_progress"]]],
                    }),
                ]);
                gl.data = {
                    kpis: kpis.M02 || kpis,
                    unassigned: unassigned.rows || [],
                    active: active.rows || [],
                };
            } else if (gl.kind === "bi_role") {
                // M25 role dashboards: one measured payload per role from
                // /p03/bi/role. Money tiles are pre-formatted here so the
                // template never calls Number/String (QWeb has no globals).
                const role = (gl.cfg && gl.cfg.role) || "ceo";
                const res = await this.rpc("/p03/bi/role", { role });
                if (!res || res.error) {
                    gl.data = { error: (res && res.error) || "Dashboard unavailable", groups: [], notes: [] };
                } else {
                    gl.data = {
                        title: res.title || "",
                        as_of: res.as_of || "",
                        notes: res.notes || [],
                        groups: (res.groups || []).map((g) => ({
                            title: g.title,
                            kpis: (g.kpis || []).map((k) => ({
                                l: k.l,
                                v: k.money
                                    ? this.fmtBDT(k.v)
                                    : k.v === null || k.v === undefined ? "—" : String(k.v),
                            })),
                        })),
                    };
                }
            } else if (gl.kind === "bi_exec") {
                // M25 executive C-Suite KPI dashboard: one live payload from
                // /p03/bi/exec (real order/estimate/invoice aggregates). The
                // branch precomputes display-ready rows so the template only
                // loops — no Math or globals in template expressions.
                const res = await this.rpc("/p03/bi/exec", {});
                if (!res || res.error) {
                    gl.data = { error: (res && res.error) || "Dashboard unavailable", kpis: {}, trend: [], channels: [], branches: [] };
                } else {
                    const trend = res.trend || [];
                    let trendMax = 1;
                    for (const pt of trend) { if (pt.orders > trendMax) trendMax = pt.orders; }
                    const channels = res.channels || [];
                    let chanMax = 1;
                    for (const ch of channels) { if (ch.count > chanMax) chanMax = ch.count; }
                    gl.data = {
                        kpis: res.kpis || {},
                        trend: trend.map(pt => ({ label: pt.month, orders: pt.orders, pct: Math.max(4, Math.round((pt.orders * 100) / trendMax)) })),
                        channels: channels.map(ch => ({ label: ch.key, count: ch.count, pct: Math.max(4, Math.round((ch.count * 100) / chanMax)) })),
                        branches: res.branches || [],
                    };
                }
            } else if (gl.kind === "fs_map") {
                gl.data = await this.rpc("/p03/dispatch/map_data", {});
                if (!gl.data || gl.data.error) {
                    gl.data = { branches: [], technicians: [], orders: [] };
                }
            } else if (gl.kind === "fs_crews") {
                // crews: co-dispatched technicians — measured as the field
                // orders whose service order carries >1 work-order technician
                gl.data = await this.rpc("/p03/model/records", {
                    model: "fix.work.order",
                    cols: ["name", "order_id", "technician_id", "state"],
                    domain: [["technician_id", "!=", false]],
                });
            }
        } catch (e) {
            gl.error = "Connection lost — press ↻ Refresh to reload this screen.";
            console.warn("GL screen load failed:", e);
        }
        gl.loading = false;
    }


    /* ---------------- M01 service-order screens (so_*) ----------------
     * The so_list/so_board/so_intake kinds: rows come from /p03/orders/list
     * (real orders with estimate-backed amounts), the board adds /p03/stats.
     * Actions run the SAME whitelisted model methods the Odoo forms use
     * (/p03/model/action, savepointed) or the backend-driven stepper. */

    get soRows() {
        const gl = this.state.gl;
        if (!gl || !gl.data || gl.data.error) return [];
        const orders = gl.data.orders || [];
        if (!gl.soState || gl.soState === "all") return orders;
        return orders.filter((o) => o.state === gl.soState);
    }

    get soStateOptions() {
        const gl = this.state.gl;
        if (!gl || !gl.data || gl.data.error) return [];
        const seen = new Map();
        for (const o of gl.data.orders || []) {
            if (o.state && !seen.has(o.state)) seen.set(o.state, this.stateLabel(o.state));
        }
        return [...seen.entries()].map(([key, label]) => ({ key, label }));
    }

    /* Channel mix as [{key, count}] — Owl expressions cannot carry object
     * literals ({} breaks its expression parser), so this stays in JS.
     * D10 (M01 audit 2026-11-06): the intake table shows the channel LABEL. */
    get soChannelMix() {
        const gl = this.state.gl;
        const mix = (gl && gl.data && gl.data.stats && gl.data.stats.channel_mix) || {};
        return Object.entries(mix).map(([key, count]) => ({
            key: SERVICE_TYPE_LABELS[key] || key, count,
        }));
    }

    get soScopeTitle() {
        const gl = this.state.gl;
        const scope = gl && gl.soScope;
        const titles = {
            all: this.t("All Service Orders"),
            wip: this.t("WIP — orders in active work"),
            holds: this.t("Holds — deferred repairs"),
            rework: this.t("Rework-flagged open orders"),
            rwty: this.t("Delivered & closed — repair warranty"),
        };
        return titles[scope] || this.t("Service Orders");
    }

    soAgeClass(days) {
        if (days === null || days === undefined) return "";
        if (days < 1) return "chip ok";
        if (days < 2) return "chip warn";
        return "chip bad";
    }

    soM2o(value) {
        // many2one search_read values arrive as [id, name]
        return Array.isArray(value) ? (value[1] || "—") : (value || "—");
    }

    /* Date rendering for Owl templates: expressions there expose NO JS
     * globals (String/parseInt are unavailable — measured the hard way), so
     * slicing stays in component code. Falsy (null/""/false) renders —. */
    ymd(value) {
        if (!value) return "—";
        return String(value).slice(0, 10);
    }

    /** The AS-06 forward path (mirrors VALID_TRANSITIONS' happy path; the
     * backend remains the authority — a refused transition comes back as an
     * error toast, never a client-side state change). */
    soNextState(state) {
        const forward = {
            draft: "intake", intake: "diagnostic", diagnostic: "estimate_pending",
            estimate_pending: "estimate_sent", estimate_sent: "awaiting_approval",
            awaiting_approval: "approved", approved: "in_repair", in_repair: "qc_pending",
            qc_pending: "ready", qc_failed: "in_repair", ready: "delivered",
            delivered: "closed",
        };
        return forward[state] || null;
    }

    async soAdvance(order) {
        const next = this.soNextState(order.state);
        if (!next) {
            this.showToast(this.t("This order has no forward transition left."));
            return;
        }
        if (!window.confirm(this.t("Advance order") + " " + order.name + ": " + this.stateLabel(order.state) + " → " + this.stateLabel(next) + "?")) return;
        this.state.gl.soBusy = order.id;
        try {
            const res = await this.rpc("/p03/order/advance_stage", {
                order_id: order.id,
                next_state: next,
            });
            if (res && res.success) {
                this.showToast(order.name + ": " + this.stateLabel(res.state));
                await this.loadGlData();
            } else {
                this.showToast((res && res.error) || this.t("Transition refused by the backend."));
            }
        } finally {
            this.state.gl.soBusy = null;
        }
    }

    async soAction(order, method, labelEn) {
        if (!window.confirm(order.name + " — " + this.t(labelEn) + "?")) return;
        this.state.gl.soBusy = order.id;
        try {
            const res = await this.rpc("/p03/model/action", {
                model: "fix.service.order",
                ids: [order.id],
                method,
            });
            if (res && res.success) {
                this.showToast(order.name + " — " + this.t(labelEn) + " ✓");
                await this.loadGlData();
            } else {
                this.showToast((res && res.error) || this.t("Action refused by the backend."));
            }
        } finally {
            this.state.gl.soBusy = null;
        }
    }

    /* A02 audit M01-P2: the order actions of the screen (m01.js SO_ACTIONS)
     * that apply to this row's state. The server remains the authority. */
    soActionsFor(row) {
        const cfg = this.state.gl && this.state.gl.soCfg;
        const list = (cfg && cfg.actions) || [];
        return list.filter((a) => !a.states || a.states.includes(row.state));
    }

    soPickAction(row, ev) {
        const key = ev.target.value;
        ev.target.value = "";
        if (key) this.soRunAction(row, key);
    }

    /** Run one order action: prompt for each server argument (`asks`), add
     * the fixed ones (`kw`), and report the backend's answer. */
    async soRunAction(row, key) {
        const cfg = this.soActionsFor(row).find((a) => a.id === key);
        if (!cfg) return;
        const kwargs = Object.assign({}, cfg.kw || {});
        const asks = cfg.asks || [];
        for (const ask of asks) {
            const value = window.prompt(row.name + " — " + this.t(ask.label));
            if (value === null) return;
            kwargs[ask.kwarg] = ask.number ? Number(value) : value;
        }
        if (!asks.length && !window.confirm(row.name + " — " + this.t(cfg.l) + "?")) return;
        this.state.gl.soBusy = row.id;
        try {
            const res = await this.rpc("/p03/model/action", {
                model: "fix.service.order",
                ids: [row.id],
                method: cfg.m,
                kwargs,
            });
            const result = (res && res.result) || {};
            if (res && res.success && result.verified !== false) {
                this.showToast(row.name + " — " + this.t(cfg.l) + " ✓");
                await this.loadGlData();
            } else {
                this.showToast((res && res.error) || result.error || this.t("Action refused by the backend."));
            }
        } finally {
            this.state.gl.soBusy = null;
        }
    }

    /* Board pipeline: the 14 AS-06 states folded into board columns with
     * live counts from /p03/stats.by_state. */
    get boardColumns() {
        const gl = this.state.gl;
        if (!gl || !gl.data || gl.data.error || !gl.data.stats) return [];
        const byState = gl.data.stats.by_state || {};
        const cols = [
            { key: "intake", label: this.t("Intake"), states: ["draft", "intake"] },
            { key: "diagnostic", label: this.t("Diagnosis"), states: ["diagnostic"] },
            { key: "estimate", label: this.t("Estimate & Approval"), states: ["estimate_pending", "estimate_sent", "awaiting_approval"] },
            { key: "repair", label: this.t("Repair"), states: ["approved", "in_repair"] },
            { key: "qc", label: this.t("QC"), states: ["qc_pending", "qc_failed"] },
            { key: "ready", label: this.t("Ready"), states: ["ready"] },
            { key: "delivered", label: this.t("Delivered"), states: ["delivered"] },
            { key: "closed", label: this.t("Closed"), states: ["closed"] },
            { key: "cancelled", label: this.t("Cancelled"), states: ["cancelled"] },
        ];
        for (const col of cols) {
            col.count = col.states.reduce((sum, s) => sum + (byState[s] || 0), 0);
            col.orders = (gl.data.orders || []).filter((o) => col.states.includes(o.state)).slice(0, 6);
        }
        return cols;
    }

    get boardRowsForColumn() {
        const gl = this.state.gl;
        if (!gl || !gl.boardCol) return [];
        const col = this.boardColumns.find((c) => c.key === gl.boardCol);
        if (!gl.data || gl.data.error) return [];
        const states = col ? col.states : null;
        const orders = gl.data.orders || [];
        return states ? orders.filter((o) => states.includes(o.state)) : orders;
    }

    get soBoardSelectedLabel() {
        const gl = this.state.gl;
        if (!gl || !gl.boardCol) return "";
        const col = this.boardColumns.find((c) => c.key === gl.boardCol);
        return col ? col.label : "";
    }

    /* ---------------- M02 field-service screens (fs_*) ---------------- */

    get fsKpis() {
        const gl = this.state.gl;
        return (gl && gl.data && gl.data.kpis) || {};
    }

    get fsUnassigned() {
        const gl = this.state.gl;
        return (gl && gl.data && gl.data.unassigned) || [];
    }

    get fsActive() {
        const gl = this.state.gl;
        return (gl && gl.data && gl.data.active) || [];
    }

    get fsCrewPairs() {
        const gl = this.state.gl;
        const rows = (gl && gl.data && gl.data.rows) || [];
        const byOrder = {};
        for (const wo of rows) {
            const key = wo.order_id && wo.order_id.id;
            if (!key) continue;
            byOrder[key] = byOrder[key] || { order: wo.order_id.name || key, techs: new Map() };
            if (wo.technician_id && wo.technician_id.name) {
                byOrder[key].techs.set(wo.technician_id.id, wo.technician_id.name);
            }
        }
        return Object.values(byOrder)
            .filter((c) => c.techs.size > 1)
            .map((c) => ({ order: c.order, techs: [...c.techs.values()].join(" + ") }));
    }

    /** Dispatch modal: pull the ranked suggestions for one field order. */
    async fsOpenSuggest(row) {
        const gl = this.state.gl;
        gl.fsSuggest = { order: row, rows: null };
        gl.fsSuggestPicked = null;
        try {
            const res = await this.rpc("/p03/field/suggest", { field_order_id: row.id });
            if (gl.fsSuggest && gl.fsSuggest.order.id === row.id) {
                gl.fsSuggest.rows = (res && res.suggestions) || [];
            }
        } catch (e) {
            gl.fsSuggest.rows = [];
        }
    }

    fsCloseSuggest() {
        this.state.gl.fsSuggest = null;
        this.state.gl.fsSuggestPicked = null;
    }

    /** Dispatch with the picked (or top-ranked) technician. */
    async fsConfirmDispatch() {
        const gl = this.state.gl;
        if (!gl.fsSuggest || !gl.fsSuggest.rows) return;
        const pickId = gl.fsSuggestPicked || (gl.fsSuggest.rows[0] && gl.fsSuggest.rows[0].employee_id);
        if (!pickId) {
            this.showToast(this.t("No technician available to dispatch."));
            return;
        }
        const order = gl.fsSuggest.order;
        gl.fsBusy = order.id;
        try {
            const res = await this.rpc("/p03/model/action", {
                model: "fix.field.order",
                ids: [order.id],
                method: "action_dispatch",
                kwargs: { technician_id: pickId },
            });
            if (res && res.success) {
                const picked = gl.fsSuggest.rows.find((r) => r.employee_id === pickId);
                this.showToast(order.name + " → " + (picked ? picked.name : this.t("technician")) + " ✓");
                this.fsCloseSuggest();
                await this.loadGlData();
            } else {
                this.showToast((res && res.error) || this.t("Dispatch refused by the backend."));
            }
        } finally {
            gl.fsBusy = null;
        }
    }

    /** Field-order lifecycle button (accept / travel / arrive / work / complete). */
    async fsAction(row, method, labelEn) {
        if (!window.confirm(row.name + " — " + this.t(labelEn) + "?")) return;
        this.state.gl.fsBusy = row.id;
        try {
            const res = await this.rpc("/p03/model/action", {
                model: "fix.field.order",
                ids: [row.id],
                method,
            });
            if (res && res.success) {
                this.showToast(row.name + " — " + this.t(labelEn) + " ✓");
                await this.loadGlData();
            } else {
                this.showToast((res && res.error) || this.t("Action refused by the backend."));
            }
        } finally {
            this.state.gl.fsBusy = null;
        }
    }

    fsNextAction(row) {
        // the forward path of the field-order state machine (authority: the
        // backend VALID transitions; this only picks the next button)
        const forward = {
            draft: ["action_request_dispatch", "Submit for Dispatch"],
            pending_dispatch: ["action_dispatch", "Dispatch"],
            declined: ["action_dispatch", "Dispatch"],
            dispatched: ["action_accept", "Accept"],
            accepted: ["action_start_travel", "Start Travel"],
            en_route: ["action_arrive", "Mark Arrival"],
            arrived: ["action_start_work", "Start Work"],
            in_progress: ["action_complete", "Complete"],
        };
        return forward[row.state] || null;
    }

    /* ---------------- generic model_list screens ---------------- */

    get mlRows() {
        const gl = this.state.gl;
        if (!gl || !gl.data || gl.data.error) return [];
        let rows = gl.data.rows || [];

        // 1. D365 Quick-Find Search Filter across all visible columns
        if (gl.mlSearch && gl.mlSearch.trim()) {
            const q = gl.mlSearch.toLowerCase().trim();
            rows = rows.filter((r) => {
                const cols = gl.modelCfg.cols || Object.keys(r);
                return cols.some((col) => {
                    const val = r[col];
                    if (val == null) return false;
                    if (typeof val === "object") {
                        const s = val.label || val.name || "";
                        return String(s).toLowerCase().includes(q);
                    }
                    return String(val).toLowerCase().includes(q);
                });
            });
        }

        // 2. D365 Column Header Sorting
        if (gl.mlSortCol) {
            const col = gl.mlSortCol;
            const asc = gl.mlSortAsc !== false ? 1 : -1;
            rows = [...rows].sort((a, b) => {
                let va = a[col], vb = b[col];
                if (va && typeof va === "object") va = va.label || va.name || "";
                if (vb && typeof vb === "object") vb = vb.label || vb.name || "";
                if (va == null && vb == null) return 0;
                if (va == null) return 1;
                if (vb == null) return -1;
                if (typeof va === "number" && typeof vb === "number") return (va - vb) * asc;
                return String(va).localeCompare(String(vb)) * asc;
            });
        }

        return rows;
    }

    mlToggleSort(col) {
        const gl = this.state.gl;
        if (gl.mlSortCol === col) {
            gl.mlSortAsc = !gl.mlSortAsc;
        } else {
            gl.mlSortCol = col;
            gl.mlSortAsc = true;
        }
    }

    mlOnSearchInput(ev) {
        this.state.gl.mlSearch = ev.target.value;
    }

    mlClearSearch() {
        this.state.gl.mlSearch = "";
    }

    /* Branded server-side export (user directive 2026-11-07): the workbook /
     * PDF is rendered by the server from EXACTLY the rows this screen serves,
     * with the official 1000 FiX letterhead (logo + address + ISO badge). */
    mlExportServer(fmt) {
        const gl = this.state.gl;
        if (!gl || !gl.modelCfg || !gl.modelCfg.model) return;
        const q = new URLSearchParams({
            model: gl.modelCfg.model,
            format: fmt,
            cols: (gl.modelCfg.cols || []).join(","),
            lang: this.state.lang === "bn" ? "bn_BD" : "en_US",
        });
        window.open(`/p03/model/list/export?${q.toString()}`, "_blank");
    }

    /* Register-screen export (R1): the statutory CoA screen exports the
     * coa_register pack — hierarchy, flags and live ledger balances — through
     * the same branded engine as every pack. */
    coaExport(fmt) {
        const q = new URLSearchParams({ module: "M19", report: "coa_register", format: fmt });
        window.open(`/p03/model/report/export?${q.toString()}`, "_blank");
    }

    mlEmailOpen() {
        const gl = this.state.gl;
        if (!gl) return;
        const today = new Date().toISOString().slice(0, 10);
        // pack mode (register screens) vs list mode (model_list grids)
        if (gl.kind === "coa") {
            gl.mlEmail = {
                open: true, mode: "pack", module: "M19", report: "coa_register",
                title: "Chart of Accounts Register",
                to: "",
                subject: `1000 FiX — Chart of Accounts Register ${today}`,
                body: "", format: "xlsx", sending: false, result: null,
            };
            return;
        }
        if (!gl.modelCfg || !gl.modelCfg.model) return;
        gl.mlEmail = {
            open: true, mode: "list",
            title: (gl.modelCfg.model || "").split(".").pop().replace(/_/g, " "),
            to: "",
            subject: `1000 FiX — ${gl.modelCfg.model.split(".").pop()} list export ${today}`,
            body: "", format: "xlsx", sending: false, result: null,
        };
    }

    mlEmailClose() {
        if (this.state.gl) this.state.gl.mlEmail = null;
    }

    async mlEmailSend() {
        const gl = this.state.gl;
        const dlg = gl && gl.mlEmail;
        if (!dlg || dlg.sending) return;
        dlg.sending = true;
        dlg.result = null;
        const base = {
            to: dlg.to,
            subject: dlg.subject,
            body: dlg.body,
            format: dlg.format,
            lang: this.state.lang === "bn" ? "bn_BD" : "en_US",
        };
        const payload = dlg.mode === "pack"
            ? Object.assign(base, { module: dlg.module, report: dlg.report })
            : Object.assign(base, {
                model: gl.modelCfg.model,
                cols: (gl.modelCfg.cols || []).join(","),
            });
        try {
            const res = await this.rpc("/p03/model/list/email", payload);
            dlg.result = res;
            if (res && res.ok) this.showToast(this.t(`Emailed ${res.attachment} to ${res.recipients.length} recipient(s)`));
        } catch (e) {
            dlg.result = { error: (e && e.message) || "Send failed" };
        } finally {
            dlg.sending = false;
        }
    }

    mlExportCsv() {
        const gl = this.state.gl;
        if (!gl || !gl.data || !gl.modelCfg) return;
        const cols = gl.modelCfg.cols || [];
        const labels = gl.data.labels || {};
        const rows = this.mlRows;
        
        const headerRow = cols.map(c => `"${(labels[c] || c).replace(/"/g, '""')}"`).join(",");
        const dataRows = rows.map(r => {
            return cols.map(c => {
                const cellText = this.mlCell(r, c);
                return `"${String(cellText).replace(/"/g, '""')}"`;
            }).join(",");
        });
        
        const csvContent = "\uFEFF" + [headerRow, ...dataRows].join("\r\n");
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        const filename = `${gl.modelCfg.model || "records"}_export_${new Date().toISOString().slice(0, 10)}.csv`;
        link.setAttribute("href", url);
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        this.showToast(this.t(`Exported ${rows.length} records to CSV`));
    }

    get mlStates() {
        const gl = this.state.gl;
        if (!gl || !gl.modelCfg || !gl.modelCfg.stateField) return [];
        const seen = new Map();
        for (const r of this.mlRows) {
            const v = r[gl.modelCfg.stateField];
            // selection → its label; boolean → Yes/No (a raw "false" pill
            // leaked into the Identity filter strip — audit D4b)
            if (v && v.key != null && !seen.has(v.key)) seen.set(v.key, v.label);
            else if (typeof v === "boolean" && !seen.has(String(v))) {
                seen.set(String(v), v ? this.t("Yes") : this.t("No"));
            }
        }
        return [...seen.entries()].map(([key, label]) => ({ key, label }));
    }

    mlSetState(key) {
        this.state.gl.mlState = key;
        this.loadGlData();
    }

    mlCell(row, field) {
        const v = row[field];
        if (v == null || v === "") return "—";
        if (typeof v === "object") {
            if (v.label != null) return v.label;          // selection
            if (v.name != null) return v.name;            // many2one
            return String(v);
        }
        // booleans show their verdict — a bare False must never leak the
        // literal "false" into a cell (audit D4, from the user's PDF)
        if (typeof v === "boolean") return v ? "✓" : "✗";
        // format by the field's own type: money always carries ৳ (even below
        // 1,000), integer counts never do; the magnitude heuristic remains
        // only for payloads that predate the `kinds` metadata.
        const kind = this.state.gl && this.state.gl.data && this.state.gl.data.kinds
            ? this.state.gl.data.kinds[field] : null;
        if (kind === "monetary") return fmtBDT(v);
        if (kind === "integer") return fmtNum(v);
        if (typeof v === "number" && Math.abs(v) >= 1000) return fmtNum(v);
        return String(v);
    }

    mlIsState(row, field) {
        const v = row[field];
        return !!(v && typeof v === "object" && v.key != null);
    }

    mlSelect(row) {
        const gl = this.state.gl;
        if (!row) return;
        // The row's actions (mlAction) read gl.mlSelected — keep it pointing
        // at this row so the same workflow methods serve the record pane.
        gl.mlSelected = row;
        const label = row.name || row.reference || row.reference_no || `#${row.id}`;
        this.openRecordTab({
            kind: "model_record",
            id: row.id,
            icon: (this.state.activeModule && this.state.activeModule.icon) || "▤",
            title: String(label),
            subtitle: (gl && gl.modelCfg && gl.modelCfg.model) || "",
            screenId: gl ? gl.screenId : null,
            moduleId: this.state.activeModuleId,
            row,
        });
    }

    /* The record's D365 in-workspace form when the module declares one,
     * else the model's Odoo form in a dialog (last resort). The list
     * reloads on close. */
    mlOpenForm(resId) {
        const gl = this.state.gl;
        if (this.openModuleFormForModel(gl.modelCfg.model, resId || null)) return;
        // No declared D365 form for this model: keep the record IN the
        // workspace as a record tab (never an Odoo dialog — the estate rule
        // is that every record surface renders inside the shell).
        const row = resId ? ((gl.data && gl.data.rows) || []).find((r) => r.id === resId) : null;
        if (resId) {
            this.openRecordTab({
                kind: "model_record",
                id: resId,
                icon: (this.state.activeModule && this.state.activeModule.icon) || "▤",
                title: String((row && (row.name || row.reference || row.reference_no)) || `#${resId}`),
                subtitle: (gl.modelCfg && gl.modelCfg.model) || "",
                screenId: gl.screenId,
                moduleId: this.state.activeModuleId,
                row,
            });
            return;
        }
        this.showToast(this.t("This model has no in-workspace form yet — the record opens read-only in its tab."));
    }

    mlRefresh() {
        this.loadGlData();
    }

    mlNew() {
        this.mlOpenForm(false);
    }

    /* ================================================================
     * D365 IN-WORKSPACE FORM SCREENS (user directive 2026-10-27).
     *
     * Schema-driven record forms rendered INSIDE the workspace shell in the
     * Dynamics-365 layout — command bar, record header with a status pill,
     * section cards, labelled field grid. NEVER an Odoo dialog: the user
     * must not see Odoo chrome, Odoo field styling or chatter tables.
     * Schema comes from the module fragment (FORM_SCREENS); field metadata
     * and choices from /p03/model/form; saving posts /p03/model/write
     * (savepoint + the caller's own ACL).
     * ================================================================ */
    get formTabs() {
        const gl = this.state.gl;
        return (gl && gl.formCfg && gl.formCfg.tabs) || [];
    }

    get formActiveTab() {
        const gl = this.state.gl;
        if (!gl || !gl.form) return "";
        if (gl.form.activeTab) return gl.form.activeTab;
        const tabs = this.formTabs;
        return (tabs.length && tabs[0].id) || "";
    }

    formSetTab(tabId) {
        const gl = this.state.gl;
        if (!gl || !gl.form) return;
        gl.form.activeTab = tabId;
        this.render(true);
    }

    get formSections() {
        const gl = this.state.gl;
        const all = (gl && gl.formCfg && gl.formCfg.sections) || [];
        const tabs = this.formTabs;
        if (!tabs || !tabs.length) {
            return all;
        }
        const active = this.formActiveTab;
        return all.filter((s) => !s.tab || s.tab === active);
    }

    get formStatusText() {
        const gl = this.state.gl;
        if (!gl || gl.kind !== "model_form" || !gl.formCfg) return "";
        const status = gl.formCfg.status;
        if (!status) return "";
        const typed = gl.form.values ? gl.form.values[status.field] : undefined;
        // a workflow state is rarely an input on the form: it is served apart
        const raw = typed !== undefined ? typed : gl.form.statusValue;
        if (raw === undefined || raw === null) return "";
        if (status.labels) {
            const key = raw === true ? "true" : raw === false ? "false" : String(raw ?? "");
            if (status.labels[key] !== undefined) return this.t(status.labels[key]);
        }
        return raw === true ? this.t("Yes") : raw === false ? this.t("No") : String(raw ?? "");
    }

    formFieldValue(name) {
        const gl = this.state.gl;
        const v = gl && gl.form ? gl.form.values[name] : undefined;
        return v === undefined || v === null ? "" : v;
    }

    /* name -> field metadata (from /p03/model/form) for the template. */
    get formFieldsMeta() {
        const gl = this.state.gl;
        const map = {};
        ((gl && gl.data && gl.data.fields) || []).forEach((f) => {
            map[f.name] = f;
        });
        return map;
    }

    /* The raw key/id for <select> binding (never an object). */
    formSelectValue(name) {
        const raw = this.formFieldValue(name);
        if (raw && typeof raw === "object") return raw.id;
        return raw;
    }

    /* Display text for read-only D365 fields. */
    formDisplay(name) {
        const meta = this.formFieldsMeta[name];
        const raw = this.formFieldValue(name);
        if (name === "name" && !raw) return "[Auto-Generated on Save]";
        if (name === "state" && !raw) return "Draft (New)";
        if (!meta) return raw === "" || raw === null || raw === undefined ? "—" : String(raw);
        if (meta.type === "many2one") return raw && raw.label ? raw.label : "—";
        if (meta.type === "many2many") {
            const labels = (Array.isArray(raw) ? raw : []).map((v) => {
                if (v && typeof v === "object") return v.label;
                const hit = (meta.choices || []).find((c) => c.id === v);
                return hit ? hit.label : String(v);
            });
            return labels.length ? labels.join(", ") : "—";
        }
        if (meta.type === "selection") {
            const hit = (meta.choices || []).find((c) => c.key === raw);
            return hit ? this.t(hit.label) : raw === "" || raw === null || raw === undefined ? "—" : String(raw);
        }
        if (meta.type === "boolean") return raw ? this.t("Yes") : this.t("No");
        if (meta.type === "monetary") return raw === "" || raw === null || raw === undefined ? "—" : String(raw);
        return raw === "" || raw === null || raw === undefined ? "—" : String(raw);
    }

    /* Helper for rendering binary / base64 image data */
    formImageSrc(name) {
        const v = this.formFieldValue(name);
        if (!v) return "";
        if (typeof v === "string" && (v.startsWith("data:") || v.startsWith("http"))) return v;
        if (typeof v === "string" && v.startsWith("PD94bWw")) return `data:image/svg+xml;base64,${v}`;
        return `data:image/png;base64,${v}`;
    }

    /* Handler for binary photo / file upload in D365 forms */
    formHandleImageUpload(name, ev) {
        const file = ev.target.files && ev.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            const dataUrl = e.target.result;
            const base64 = dataUrl.includes(",") ? dataUrl.split(",")[1] : dataUrl;
            this.formSet(name, base64);
            this.render(true);
        };
        reader.readAsDataURL(file);
    }

    /* Helper for physical document download URL (data: URI) */
    formFileDownloadHref(name) {
        const v = this.formFieldValue(name);
        if (!v) return "#";
        if (typeof v === "string" && (v.startsWith("data:") || v.startsWith("http"))) return v;
        if (typeof v === "string" && v.startsWith("JVBERi")) return `data:application/pdf;base64,${v}`;
        if (typeof v === "string" && v.startsWith("iVBORw0KGgo")) return `data:image/png;base64,${v}`;
        if (typeof v === "string" && v.startsWith("/9j/")) return `data:image/jpeg;base64,${v}`;
        return `data:application/octet-stream;base64,${v}`;
    }

    /* Helper for displaying physical document filename */
    formFileName(name) {
        const directFn = this.formFieldValue(name + "_filename") ||
                         this.formFieldValue(name.replace(/_file$/, "") + "_filename") ||
                         this.formFieldValue(name.replace(/_file$/, "") + "_name") ||
                         this.formFieldValue("file_name");
        if (directFn) return directFn;
        const v = this.formFieldValue(name);
        if (!v) return "";
        if (typeof v === "string" && v.startsWith("JVBERi")) return `${name}.pdf`;
        if (typeof v === "string" && v.startsWith("iVBORw0KGgo")) return `${name}.png`;
        if (typeof v === "string" && v.startsWith("/9j/")) return `${name}.jpg`;
        return `${name}.bin`;
    }

    /* Handler for physical document upload (PDF, PNG, JPG, DOCX) */
    formHandleFileUpload(name, ev) {
        const file = ev.target.files && ev.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (e) => {
            const dataUrl = e.target.result;
            const base64 = dataUrl.includes(",") ? dataUrl.split(",")[1] : dataUrl;
            this.formSet(name, base64);
            const fnCandidates = [
                name + "_filename",
                name.replace(/_file$/, "") + "_filename",
                name.replace(/_file$/, "") + "_name",
                "file_name"
            ];
            for (const fnField of fnCandidates) {
                if (this.formFieldsMeta[fnField]) {
                    this.formSet(fnField, file.name);
                    break;
                }
            }
            if (this.formFieldsMeta["file_size"]) {
                this.formSet("file_size", file.size);
            }
            if (this.formFieldsMeta["file_mimetype"]) {
                this.formSet("file_mimetype", file.type || "application/octet-stream");
            }
            this.render(true);
        };
        reader.readAsDataURL(file);
    }

    /* Handler for clearing uploaded document and its metadata */
    formClearFile(name) {
        this.formSet(name, false);
        const fnCandidates = [
            name + "_filename",
            name.replace(/_file$/, "") + "_filename",
            name.replace(/_file$/, "") + "_name",
            "file_name"
        ];
        for (const fnField of fnCandidates) {
            if (this.formFieldsMeta[fnField]) {
                this.formSet(fnField, "");
                break;
            }
        }
        if (this.formFieldsMeta["file_size"]) {
            this.formSet("file_size", 0);
        }
        if (this.formFieldsMeta["file_mimetype"]) {
            this.formSet("file_mimetype", "");
        }
        this.render(true);
    }

    openFormScreen(screenId, hit, cfg) {
        const recordId = cfg.recordId || null;
        const activeTab = (cfg.tabs && cfg.tabs.length && cfg.tabs[0].id) || "";
        this.state.gl = {
            screenId,
            hitSc: hit ? hit.sc : null,
            hitM: hit ? hit.m : null,
            kind: "model_form",
            formCfg: cfg,
            title: (hit && hit.sc && hit.sc.en) || cfg.title || "Record",
            moduleTitle: hit ? hit.m.title : "",
            data: null,
            loading: true,
            error: null,
            mlSelected: null,
            mlState: "__all",
            form: { recordId, values: {}, busy: false, error: null,
                    activeTab, lineMeta: [], lineValues: [], lineRemoved: [] },
        };
        this.state.viewMode = "gl";
        // Record tabs, not screen tabs: editing record B must never overwrite
        // record A's tab. A NEW record keeps the screen-scoped tab (one draft
        // tab per form), an EXISTING record gets its own closable tab.
        const tabId = recordId ? `form-${screenId}-${recordId}` : `gl-${screenId}`;
        const payload = recordId ? { screenId, recordId } : { screenId };
        this._formCache = this._formCache || {};
        this._formCache[tabId] = { screenId, hit, cfg };
        this.ensureTab(
            tabId,
            `${this.state.gl.title}${recordId ? ` #${recordId}` : ""}`,
            hit && hit.sc.t === "f" ? "▤" : "⛁",
            "gl",
            payload
        );
        this.loadFormData();
    }

    async loadFormData() {
        const gl = this.state.gl;
        if (!gl || gl.kind !== "model_form") return;
        gl.loading = true;
        gl.form.error = null;
        gl.form.unavailable = false;
        try {
            const res = await this.rpc("/p03/model/form", {
                model: gl.formCfg.model,
                fields: gl.formCfg.sections.flatMap((s) => s.fields),
                record_id: gl.form.recordId || false,
                // bilingual labels: field/selection text follows the UI language
                lang: this.state.lang === "bn" ? "bn_BD" : "en_US",
                lines: gl.formCfg.lines || false,
                status_field: (gl.formCfg.status && gl.formCfg.status.field) || false,
            });
            gl.data = res;
            gl.form.statusValue = res.status_value;
            gl.form.lineMeta = (res.lines && res.lines.fields) || [];
            gl.form.lineValues = ((res.lines && res.lines.rows) || []).map((r) => ({ ...r }));
            gl.form.lineRemoved = [];
            if (res.error) {
                // the form could not be LOADED at all (model not served by
                // the workspace registry, or ACL-denied). Distinct from a
                // failed save, which must keep the command bar.
                gl.form.error = res.error;
                gl.form.unavailable = true;
            } else if (res.record) {
                gl.form.values = { ...res.record };
            } else {
                gl.form.values = {};
                for (const section of gl.formCfg.sections) {
                    for (const field of section.fields) {
                        if (field.value !== undefined) gl.form.values[field.name] = field.value;
                    }
                }
                // a brand-new record with a required child grid starts with
                // one blank target so the form is usable without hunting
                // (fixedRows: the server fills the rows, nothing is keyed in)
                if (gl.formCfg.lines && !gl.formCfg.lines.fixedRows && !gl.form.lineValues.length) this.formAddLine();
            }
        } catch (e) {
            gl.data = null;
            gl.form.error = this.t("Could not load the form — try again");
            gl.form.unavailable = true;
        }
        gl.loading = false;
        this.render(true);
    }

    /* A many2one whose list exceeds the server's choice limit searches on the
     * server as the user types. `line` marks a field of the child grid. */
    formChoiceSearch(meta, query, line) {
        const gl = this.state.gl;
        if (!gl || gl.kind !== "model_form") return;
        clearTimeout(this._choiceTimer);
        this._choiceTimer = setTimeout(async () => {
            const params = { field: meta.name, q: query, domain: meta.choice_domain || [] };
            if (line) {
                params.model = (gl.data.lines && gl.data.lines.model) || false;
                params.parent_model = gl.formCfg.model;
                params.parent_field = gl.formCfg.lines.field;
            } else {
                params.model = gl.formCfg.model;
            }
            const res = await this.rpc("/p03/model/choices", params);
            if (!res || res.error) return;
            const found = new Set(res.choices.map((c) => c.id));
            const inUse = (meta.choices || []).filter((c) => !found.has(c.id) && this._choiceInUse(meta, c.id, line));
            meta.choices = [...inUse, ...res.choices];
            this.render(true);
        }, 250);
    }

    _choiceInUse(meta, id, line) {
        const gl = this.state.gl;
        const same = (v) => (v && typeof v === "object" ? v.id : v) === id;
        if (line) return (gl.form.lineValues || []).some((row) => same(row[meta.name]));
        return same(gl.form.values[meta.name]);
    }

    /* A many2many input is a multi-select: the save posts every selected id. */
    formSetMany(name, ev) {
        const ids = [...ev.target.selectedOptions].map((o) => Number(o.value));
        this.formSet(name, ids);
    }

    formManySelected(name, id) {
        const raw = this.formFieldValue(name);
        return Array.isArray(raw) && raw.some((v) => (v && typeof v === "object" ? v.id : v) === id);
    }

    formSet(name, value) {
        const gl = this.state.gl;
        if (!gl || gl.kind !== "model_form") return;
        // QWeb handlers pass strings: coerce to the model type here (JS
        // scope), never in the template (String/Number are not template
        // globals — the 2026-10-27 "ctx.String is not a function" lesson).
        const meta = this.formFieldsMeta[name] || {};
        if (meta.type === "many2one") {
            value = value === "" || value === false || value === null ? false : Number(value);
        } else if (meta.type === "boolean") {
            value = !!value;
        } else if (meta.type === "monetary" || meta.type === "float" || meta.type === "integer") {
            value = value === "" || value === false ? false : Number(value);
        }
        gl.form.values[name] = value;
        if (gl.formCfg.status && gl.formCfg.status.field === name) this.render(true);
    }

    /* ---- declared one2many child grid (allocation targets, JE template
     * lines): the header alone is refused by the models' own constraints
     * ("rule has no targets", "template is not balanced"), so the D365 form
     * edits header + lines in ONE save. ---- */
    get formLineCfg() {
        const gl = this.state.gl;
        return (gl && gl.formCfg && gl.formCfg.lines) || null;
    }

    get formLineFields() {
        const gl = this.state.gl;
        return (gl && gl.form && gl.form.lineMeta) || [];
    }

    get formLineRows() {
        const gl = this.state.gl;
        return (gl && gl.form && gl.form.lineValues) || [];
    }

    formLineMeta(name) {
        return this.formLineFields.find((f) => f.name === name) || {};
    }

    formLineValue(rowIndex, name) {
        const row = this.formLineRows[rowIndex] || {};
        const v = row[name];
        return v === undefined || v === null ? "" : v;
    }

    /* Text of a read-only grid cell: a many2one arrives as {id, label}. */
    formLineDisplay(rowIndex, name) {
        const raw = this.formLineValue(rowIndex, name);
        const meta = this.formLineMeta(name);
        if (raw && typeof raw === "object") return raw.label || "";
        if (meta.type === "selection") {
            const hit = (meta.choices || []).find((c) => c.key === raw);
            return hit ? this.t(hit.label) : raw;
        }
        return raw;
    }

    formLineSelectValue(rowIndex, name) {
        const raw = this.formLineValue(rowIndex, name);
        if (raw && typeof raw === "object") return raw.id;
        return raw;
    }

    formLineSet(rowIndex, name, value) {
        const gl = this.state.gl;
        if (!gl || gl.kind !== "model_form") return;
        const rows = gl.form.lineValues;
        if (!rows[rowIndex]) return;
        const meta = this.formLineMeta(name);
        if (meta.type === "many2one") {
            value = value === "" || value === false || value === null ? false : Number(value);
        } else if (meta.type === "boolean") {
            value = !!value;
        } else if (meta.type === "monetary" || meta.type === "float" || meta.type === "integer") {
            value = value === "" || value === false ? false : Number(value);
        }
        rows[rowIndex][name] = value;
        if (this.formLineCfg && this.formLineCfg.total) this.render(true);
    }

    formAddLine() {
        const gl = this.state.gl;
        if (!gl || gl.kind !== "model_form" || !this.formLineCfg) return;
        const row = {};
        if (this.formLineCfg.defaults) Object.assign(row, this.formLineCfg.defaults);
        gl.form.lineValues.push(row);
        this.render(true);
    }

    formRemoveLine(rowIndex) {
        const gl = this.state.gl;
        if (!gl || gl.kind !== "model_form") return;
        const row = gl.form.lineValues[rowIndex];
        if (row && row.id) gl.form.lineRemoved.push(row.id);
        gl.form.lineValues.splice(rowIndex, 1);
        this.render(true);
    }

    /* Running total for the cfg.lines.total chip (e.g. shares must hit 100%). */
    get formLineTotal() {
        const cfg = this.formLineCfg;
        const gl = this.state.gl;
        if (!cfg || !cfg.total || !gl || !gl.form) return null;
        const sum = (gl.form.lineValues || []).reduce(
            (acc, row) => acc + (Number(row[cfg.total.field]) || 0),
            0
        );
        return Math.round(sum * 100) / 100;
    }

    /* Debit-minus-credit for a balanced line grid (recurring JE templates). */
    get formLineBalance() {
        const cfg = this.formLineCfg;
        const gl = this.state.gl;
        if (!cfg || !cfg.balance || !gl || !gl.form) return null;
        const [dr, cr] = cfg.balance.fields;
        const sum = (gl.form.lineValues || []).reduce(
            (acc, row) => acc + (Number(row[dr]) || 0) - (Number(row[cr]) || 0),
            0
        );
        return Math.round(sum * 100) / 100;
    }

    async formSave(close) {
        const gl = this.state.gl;
        if (!gl || gl.kind !== "model_form" || gl.form.busy) return;
        gl.form.busy = true;
        gl.form.error = null;
        const values = {};
        for (const section of gl.formCfg.sections) {
            for (const field of section.fields) {
                const v = gl.form.values[field.name];
                if (v !== undefined && v !== null && v !== "") values[field.name] = v;
            }
        }
        let lines = null;
        const lineCfg = this.formLineCfg;
        if (lineCfg && !lineCfg.readonlyGrid) {
            const rows = [];
            for (const row of gl.form.lineValues || []) {
                const vals = {};
                for (const field of lineCfg.fields || []) {
                    const v = row[field.name];
                    if (v !== undefined && v !== null && v !== "") vals[field.name] = v;
                }
                if (Object.keys(vals).length) rows.push({ id: row.id || null, values: vals });
            }
            lines = { field: lineCfg.field, rows, removed: gl.form.lineRemoved || [] };
        }
        try {
            const res = await this.rpc("/p03/model/write", {
                model: gl.formCfg.model,
                record_id: gl.form.recordId || false,
                values,
                lines,
            });
            if (res.error) {
                gl.form.error = res.error;
                gl.form.busy = false;
                this.render(true);
                return;
            }
            this.showToast(this.t("Saved ✓"));
            gl.form.busy = false;
            if (close) {
                this.formBackToList();
            } else {
                gl.form.recordId = res.id;
                this.loadFormData();
            }
        } catch (e) {
            gl.form.error = this.t("The save failed — server-side rules are enforced");
            gl.form.busy = false;
            this.render(true);
        }
    }

    formBackToList() {
        const gl = this.state.gl;
        const back = gl && gl.formCfg && gl.formCfg.back;
        if (back && P03_DATA_SCREENS[back]) {
            this.openScreen(back);
        } else if (back) {
            this.openScreen(back);
        } else {
            this.showToast(this.t("Saved — returning"));
            this.state.viewMode = "workspace";
            this.render(true);
        }
    }

    async mlAction(method, label) {
        const gl = this.state.gl;
        const row = gl.mlSelected;
        if (!row) { this.showToast("Select a row first"); return; }
        const cfg = (gl.modelCfg.actions || []).find((a) => a.m === method) || {};
        if (cfg.ask) {
            // needs a typed value (e.g. the customer's POD OTP at hand-over,
            // or an MSP resolution note) — the generic prompt modal collects
            // it, then the action runs with kwargs. `kwarg` names the value's
            // parameter on the server method (default: otp).
            gl.prompt = { title: label, label: cfg.ask, value: "", _ml: { row, method, label, kwarg: cfg.kwarg || "otp" } };
            return;
        }
        if (cfg.asks && cfg.asks.length) {
            // several typed values (e.g. closing a legal matter needs an
            // outcome AND a note) — chain native prompts exactly like the
            // service-order runner; cancelling any prompt aborts the action.
            const kwargs = Object.assign({}, cfg.kw || {});
            for (const ask of cfg.asks) {
                const value = window.prompt(row.name + " — " + this.t(ask.label));
                if (value === null) return;
                kwargs[ask.kwarg] = ask.number ? Number(value) : value;
            }
            const res = await this._arCall("/p03/model/action", {
                model: gl.modelCfg.model, ids: [row.id], method, kwargs,
            }, label + " ✓");
            if (res.success) {
                this._mlActionResult(res);
                this.loadGlData();
                this.state.gl.mlSelected = null;
                if (this.state.viewMode === "record_view") this.refreshRecordTab();
            }
            return;
        }
        const res = await this._arCall("/p03/model/action", {
            model: gl.modelCfg.model, ids: [row.id], method,
            kwargs: cfg.kw || undefined,
        }, label ? label + " ✓" : "Done ✓");
        if (res.success) {
            this._mlActionResult(res);
            this.loadGlData();
            this.state.gl.mlSelected = null;
        }
    }

    /** An action may answer with a result the user must see — e.g. the
     * whistleblowing reveal returns the reporter's identity (or the note
     * that the report was anonymous). Surface it; never let it vanish
     * into the RPC log. */
    _mlActionResult(res) {
        const r = (res && res.result) || {};
        if (r.reporter) this.showToast(this.t("Reporter") + ": " + r.reporter);
        else if (r.note) this.showToast(r.note);
    }

    /* ---------------- CoA ---------------- */

    get glCoaFiltered() {
        const gl = this.state.gl;
        if (!gl || !gl.data) return [];
        return gl.data.rows.filter((r) => {
            if (gl.coaType !== "all" && r.type !== gl.coaType) return false;
            if (gl.coaSearch) {
                const q = gl.coaSearch.toLowerCase();
                if (!(r.code.toLowerCase().includes(q) || (r.name || "").toLowerCase().includes(q))) return false;
            }
            return true;
        });
    }

    glSelectAccount(row) {
        this.state.gl.selected = row;
    }

    /* ---------------- Journals ---------------- */

    glSetJournalPill(pill) {
        this.state.gl.journalPill = pill;
        this.loadGlData();
    }

    async glOpenJe(moveId) {
        const gl = this.state.gl;
        const row = ((gl && gl.data && (gl.data.rows || gl.data.moves)) || []).find((r) => r.id === moveId || r.move_id === moveId) || {};
        this.openRecordTab({
            kind: "journal_entry",
            id: moveId,
            icon: "📘",
            title: row.name || this.t("Journal entry"),
            subtitle: row.journal || "",
            screenId: gl ? gl.screenId : null,
            moduleId: this.state.activeModuleId,
        });
    }

    glBackToJournals() {
        this.state.gl.jeDetail = null;
    }

    async glApproveJe(moveId) {
        try {
            const res = await this.rpc("/p03/gl/je/approve", { move_id: moveId });
            this.showToast(res.message || res.error);
            if (res.success) {
                this.glOpenJe(moveId);
                this.loadGlData();
            }
        } catch (e) {
            this.showToast(t('Approval failed — the SoD rules are enforced server-side'));
        }
    }

    /* ---------------- JE editor (draft → SoD review) ---------------- */

    _glNewEditor() {
        this.state.gl.editor = {
            ref: "",
            date: new Date().toISOString().slice(0, 10),
            lines: [
                { account_id: "", label: "", debit: "", credit: "", branch_id: "", cost_centre: "", business_line: "" },
                { account_id: "", label: "", debit: "", credit: "", branch_id: "", cost_centre: "", business_line: "" },
            ],
            templateName: "",
            schedule: "monthly",
            autoReverse: false,
        };
    }

    glEditorSet(line, field, value) {
        line[field] = value;
    }

    glEditorAddLine() {
        this.state.gl.editor.lines.push({ account_id: "", label: "", debit: "", credit: "", branch_id: "", cost_centre: "", business_line: "" });
    }

    glEditorRemoveLine(idx) {
        if (this.state.gl.editor.lines.length > 2) this.state.gl.editor.lines.splice(idx, 1);
    }

    get glEditorTotals() {
        const lines = (this.state.gl && this.state.gl.editor && this.state.gl.editor.lines) || [];
        const num = (v) => parseFloat(v) || 0.0;
        const debit = lines.reduce((s, l) => s + num(l.debit), 0);
        const credit = lines.reduce((s, l) => s + num(l.credit), 0);
        return { debit, credit, balanced: Math.round((debit - credit) * 100) / 100 === 0 };
    }

    _glEditorPayload() {
        const editor = this.state.gl.editor;
        return {
            ref: editor.ref,
            date: editor.date,
            lines: editor.lines
                .filter((l) => l.account_id && (parseFloat(l.debit) || parseFloat(l.credit)))
                .map((l) => ({
                    account_id: parseInt(l.account_id, 10),
                    label: l.label,
                    debit: parseFloat(l.debit) || 0.0,
                    credit: parseFloat(l.credit) || 0.0,
                    branch_id: l.branch_id ? parseInt(l.branch_id, 10) : false,
                    cost_centre: l.cost_centre,
                    business_line: l.business_line,
                })),
        };
    }

    async glSaveDraft() {
        const totals = this.glEditorTotals;
        if (!totals.balanced) {
            this.showToast(`Entry not balanced: debit ${totals.debit.toFixed(2)} vs credit ${totals.credit.toFixed(2)}`);
            return;
        }
        try {
            const res = await this.rpc("/p03/gl/je/create", this._glEditorPayload());
            this.showToast(res.message || res.error);
            if (res.success) this._glNewEditor();
        } catch (e) {
            this.showToast(t('Could not save the draft entry'));
        }
    }

    async glSaveTemplate() {
        const editor = this.state.gl.editor;
        const payload = this._glEditorPayload();
        if (payload.lines.length < 2) {
            this.showToast(t('A template needs at least two filled lines'));
            return;
        }
        try {
            const res = await this.rpc("/p03/gl/templates/create", {
                name: editor.templateName || editor.ref || "Workspace accrual template",
                schedule: editor.schedule,
                auto_reverse: editor.autoReverse,
                next_run_date: editor.date,
                ref: editor.ref,
                lines: payload.lines,
            });
            this.showToast(res.message || res.error);
            if (res.success) this.loadGlData(); // refresh the templates panel
        } catch (e) {
            this.showToast(t('Could not save the template'));
        }
    }

    /* ---------------- Statements ---------------- */

    glStmtInput(field, value) {
        this.state.gl[field] = value;
    }

    glRunStatement() {
        this.loadGlData();
    }

    glDrillAccount(code) {
        // Statement drill-down: the Journals screen filtered to one account
        this.state.gl.drillCode = code;
        this.openGlScreen("M19-journals", null, { kind: "journals" });
        this.state.gl.title = `Journals — account ${code}`;
    }

    /* ---------------- Close console ---------------- */

    get glSelectedClose() {
        const gl = this.state.gl;
        if (!gl || !gl.data) return null;
        return gl.data.closes.find((c) => c.id === gl.selectedCloseId) || null;
    }

    glSelectClose(id) {
        this.state.gl.selectedCloseId = id;
    }

    async glCloseAction(action, step) {
        const gl = this.state.gl;
        try {
            const res = await this.rpc("/p03/gl/close/action", {
                close_id: gl.selectedCloseId,
                action,
                step_id: step ? step.id : null,
                evidence: action === "mark_done" ? (gl.evidenceText || "").trim() : null,
                state: action === "set_state" ? "in_progress" : null,
            });
            this.showToast(res.message || res.error);
            gl.evidenceStep = null;
            gl.evidenceText = "";
            if (res.success) this.loadGlData();
        } catch (e) {
            this.showToast(t('Close action failed'));
        }
    }

    glEvidencePrompt(step) {
        this.state.gl.evidenceStep = step;
        this.state.gl.evidenceText = "";
    }

    /* ---------------- Periods / templates ---------------- */

    async glLockPeriod(closeId) {
        try {
            const res = await this.rpc("/p03/gl/periods/lock", { close_id: closeId });
            this.showToast(res.message || res.error);
            if (res.success) this.loadGlData();
        } catch (e) {
            this.showToast(t('Lock failed'));
        }
    }

    async glGenerateTemplate(templateId) {
        try {
            const res = await this.rpc("/p03/gl/templates/generate", { template_id: templateId });
            this.showToast(res.message || res.error);
            if (res.success) this.loadGlData();
        } catch (e) {
            this.showToast(t('Template run failed'));
        }
    }

    /* Open the in-workspace JE editor (the "+ New Journal Entry" path —
       previously called but never defined, a latent M19 defect). */
    openGlJeEditor() {
        this.openScreen("M19-je");
    }

    /* ================================================================
     * M20 AR IN-WORKSPACE SCREENS — the CD-M20-02 extension of the GL
     * pilot. All 15 screens of AR, Invoicing & Collections render inside
     * this shell from live /p03/ar/* data; write actions call the same
     * model methods the Odoo forms use (NID rule, FR-ARB-025, authority
     * ladders all enforced server-side).
     * ================================================================ */

    async _arCall(url, payload, okMessage) {
        try {
            const res = await this.rpc(url, payload);
            this.showToast(res.success ? (okMessage || "Done ✓") : (res.error || "Refused"));
            return res;
        } catch (e) {
            this.showToast(t('The action failed — server-side rules are enforced'));
            return { success: false };
        }
    }

    /* ---------------- invoices ---------------- */

    arSetStateFilter(value) {
        this.state.gl.arState = value;
        this.loadGlData();
    }

    async arOpenInvoice(invoiceId) {
        const gl = this.state.gl;
        const row = ((gl && gl.data && gl.data.rows) || []).find((r) => r.id === invoiceId) || {};
        this.openRecordTab({
            kind: "ar_invoice",
            id: invoiceId,
            icon: "🧾",
            title: row.name || this.t("Invoice"),
            subtitle: row.customer || "",
            screenId: gl ? gl.screenId : null,
            moduleId: this.state.activeModuleId,
        });
    }

    arBackToInvoices() {
        this.state.gl.arDetail = null;
    }

    /* ---------------- manual invoice editor (FR-ARB-010) ---------------- */

    _arNewEditor() {
        this.state.gl.arEditor = {
            customer_id: null,
            date: new Date().toISOString().slice(0, 10),
            reason: "",
            lines: [{ description: "", taxable: 0, vat: 0 }],
        };
    }

    arEditorSet(field, value) {
        this.state.gl.arEditor[field] = value;
    }

    arEditorAddLine() {
        this.state.gl.arEditor.lines.push({ description: "", taxable: 0, vat: 0 });
    }

    arEditorRemoveLine(index) {
        this.state.gl.arEditor.lines.splice(index, 1);
        if (this.state.gl.arEditor.lines.length < 1) this.arEditorAddLine();
    }

    get arEditorTotals() {
        const editor = this.state.gl && this.state.gl.arEditor;
        if (!editor) return { taxable: 0, vat: 0, total: 0 };
        const taxable = editor.lines.reduce((s, l) => s + (parseFloat(l.taxable) || 0), 0);
        const vat = editor.lines.reduce((s, l) => s + (parseFloat(l.vat) || 0), 0);
        return { taxable, vat, total: taxable + vat };
    }

    /* Owl templates expose no JS globals — line totals are computed here,
       never with parseFloat inside the template. */
    arLineTotal(line) {
        return (parseFloat(line.taxable) || 0) + (parseFloat(line.vat) || 0);
    }

    async arSaveDraftInvoice() {
        const editor = this.state.gl.arEditor;
        if (!editor.customer_id) {
            this.showToast(t('Pick a customer first'));
            return;
        }
        if (!editor.reason.trim()) {
            this.showToast(t('A reason code is mandatory for manual invoices (FR-ARB-010)'));
            return;
        }
        const res = await this._arCall("/p03/ar/invoice/create", {
            customer_id: editor.customer_id,
            invoice_date: editor.date,
            reason: editor.reason,
            lines: editor.lines.filter((l) => (parseFloat(l.taxable) || 0) > 0),
        }, "Draft saved — review, then Issue");
        if (res.success) {
            this._arNewEditor();
            this.loadGlData();
        }
    }

    async arIssueDraft(invoiceId) {
        const res = await this._arCall("/p03/ar/invoice/issue", { invoice_id: invoiceId }, "Issued — Mushak + number + GL");
        if (res.success) this.loadGlData();
    }

    async arRegisterPaid(invoiceId) {
        // close-out only on settlement evidence: the model refuses while a
        // residual remains (receipts, credit notes, VDS certificates)
        const res = await this._arCall("/p03/model/action", {
            model: "fix.ar.invoice", ids: [invoiceId], method: "action_register_paid",
        }, "Closed as paid");
        if (res.success) this.loadGlData();
    }

    /* ---------------- generic reason prompt ---------------- */

    glPrompt(title, label, action, id) {
        this.state.gl.prompt = { title, label, action, id, value: "" };
    }

    glPromptCancel() {
        this.state.gl.prompt = null;
    }

    async glPromptOk() {
        const p = this.state.gl.prompt;
        if (!p) return;
        this.state.gl.prompt = null;
        const endpoints = {
            cancel_invoice: ["/p03/ar/invoice/cancel", { invoice_id: p.id, reason: p.value }, "Cancelled — mirror posted"],
            writeoff_invoice: ["/p03/ar/invoice/writeoff", { invoice_id: p.id, reason: p.value }, "Written off"],
            reverse_receipt: ["/p03/ar/receipt/reverse", { receipt_id: p.id, reason: p.value }, "Receipt reversed"],
            suppress_dunning: ["/p03/ar/dunning/suppress", { dunning_id: p.id, reason: p.value }, "Dunning suppressed"],
            resolve_dispute: ["/p03/ar/dispute/resolve", { dispute_id: p.id, note: p.value }, "Dispute resolved"],
            lift_dunning: ["/p03/ar/dunning/lift", { dunning_id: p.id, note: p.value }, "Suppression lifted"],
            route_je: ["/p03/gl/je/route", { move_id: p.id, reason: p.value }, "Routed for approval"],
            discard_je: ["/p03/gl/je/discard", { move_id: p.id, reason: p.value }, "Draft discarded"],
            set_cutover: ["/p03/gl/close/action", { close_id: p.id, action: "set_cutover", entry: p.value }, "Cutover entry set"],
        };
        // model_list "ask" actions (e.g. the customer's POD OTP at hand-over,
        // or an MSP resolution note) — the kwarg names the server parameter
        if (p._ml) {
            const { row, method, label, kwarg } = p._ml;
            const res = await this._arCall(
                "/p03/model/action",
                { model: this.state.gl.modelCfg.model, ids: [row.id], method, kwargs: { [kwarg || "otp"]: p.value } },
                label + " ✓"
            );
            if (res.success) {
                this._mlActionResult(res);
                this.loadGlData();
                this.state.gl.mlSelected = null;
                if (this.state.viewMode === "record_view") this.refreshRecordTab();
            }
            return;
        }
        const call = endpoints[p.action];
        if (!call) return;
        const res = await this._arCall(call[0], call[1], call[2]);
        if (res.success) {
            this.loadGlData();
            if (this.state.viewMode === "record_view") this.refreshRecordTab();
        }
    }

    /* ---------------- billable events ---------------- */

    async arEventGenerate(eventId) {
        const res = await this._arCall("/p03/ar/event/generate", { event_id: eventId }, "Processed");
        if (res.success) this.loadGlData();
    }

    async arEventProcessAll() {
        const res = await this._arCall("/p03/ar/event/process-all", {}, "Batch processed");
        if (res.success) this.loadGlData();
    }

    /* ---------------- receipts ---------------- */

    arOpenReceiptForm() {
        this.state.gl.receiptForm = {
            customer_id: null,
            amount: null,
            method: "cash",
            reference: "",
            branch_id: null,
            nid: "",
        };
    }

    arReceiptFormSet(field, value) {
        this.state.gl.receiptForm[field] = value;
    }

    async arReceiptCreate() {
        const form = this.state.gl.receiptForm;
        if (!form.customer_id || !form.amount) {
            this.showToast(t('Customer and amount are required'));
            return;
        }
        const res = await this._arCall("/p03/ar/receipt/create", { ...form }, "Receipt captured (draft)");
        if (res.success) {
            this.state.gl.receiptForm = null;
            this.loadGlData();
        }
    }

    async arReceiptConfirm(receiptId) {
        const res = await this._arCall("/p03/ar/receipt/confirm", { receipt_id: receiptId }, "Confirmed — GL posted");
        if (res.success) this.loadGlData();
    }

    /* ---------------- matching & allocation ---------------- */

    async arAutoMatch() {
        try {
            const res = await this.rpc("/p03/ar/match", {});
            this.state.gl.matchProposals = res.proposals;
            this.state.gl.data.exceptions = res.exceptions;
            this.showToast(`${res.proposals.length} proposal(s) scored · ${res.exceptions.length} exception(s)`);
        } catch (e) {
            this.showToast(t('Auto-match failed'));
        }
    }

    async arApplyProposal(p) {
        const res = await this._arCall("/p03/ar/allocation/create", {
            receipt_id: p.receipt_id,
            invoice_id: p.invoice_id,
            amount: p.amount,
        }, `Allocated ৳${p.amount.toFixed(2)} (score ${p.score})`);
        if (res.success) this.loadGlData();
    }

    arAllocSet(field, value) {
        // ids arrive as strings — parsed here, never with parseInt in the template
        this.state.gl.allocPick[field] =
            field === "amount" ? value : value ? parseInt(value, 10) : null;
    }

    async arAllocManual() {
        const pick = this.state.gl.allocPick;
        if (!pick.receipt_id || !pick.invoice_id || !pick.amount) {
            this.showToast(t('Pick a receipt, an invoice and an amount'));
            return;
        }
        const res = await this._arCall("/p03/ar/allocation/create", { ...pick }, "Allocated");
        if (res.success) {
            this.state.gl.allocPick = { receipt_id: null, invoice_id: null, amount: null };
            this.loadGlData();
        }
    }

    /* ---------------- credit control ---------------- */

    arProfileNew() {
        // reads the picker's value through state, never via document globals
        const sel = document.getElementById("ar-credit-customer");
        const customerId = sel ? parseInt(sel.value, 10) : null;
        if (!customerId) {
            this.showToast(t('Pick a customer first'));
            return;
        }
        return this.arProfileSave(
            { customer_id: customerId, limit: 0, terms: 30, hold: false },
            "limit",
            0
        );
    }

    arStmtCustomerSet(value) {
        this.state.gl.stmtCustomer = value ? parseInt(value, 10) : null;
    }

    async arProfileSave(row, field, value) {
        const res = await this._arCall("/p03/ar/credit-profile/save", {
            customer_id: row.customer_id,
            credit_limit: field === "limit" ? value : row.limit,
            terms_days: field === "terms" ? value : row.terms,
            hold: field === "hold" ? value : row.hold,
            hold_reason: row.hold_reason || "",
        }, "Credit profile saved");
        if (res.success) this.loadGlData();
    }

    /* ---------------- dunning & disputes ---------------- */

    async arRunDunning() {
        const res = await this._arCall("/p03/ar/dunning/run", {}, "Dunning ladder run");
        if (res.success) this.loadGlData();
    }

    async arDisputeCreate(invoiceId, amount, reason) {
        if (!invoiceId || !amount) {
            this.showToast(t('Disputed amount is required'));
            return;
        }
        const res = await this._arCall("/p03/ar/dispute/create", {
            invoice_id: invoiceId, amount, reason: reason || "",
        }, "Dispute opened — dunning suspends on the disputed amount");
        if (res.success) this.loadGlData();
    }

    /* ---------------- ageing ---------------- */

    async arCaptureSnapshot() {
        const res = await this._arCall("/p03/ar/aging/capture", {
            as_of: this.state.gl.asOfDate,
        }, "Snapshot captured — immutable from now");
        if (res.success) this.loadGlData();
    }

    async arAgingSelectSnapshot(snapshotId) {
        const gl = this.state.gl;
        gl.snapDetail = { loading: true };
        try {
            const res = await this.rpc("/p03/ar/aging/snapshot", { snapshot_id: snapshotId });
            gl.snapDetail = res;
        } catch (e) {
            gl.snapDetail = { snapshot: null, rows: [] };
        }
    }

    /* ---------------- credit notes ---------------- */

    arOpenNoteForm(invoiceId) {
        this.state.gl.arNoteForm = { invoice_id: invoiceId, amount: null, reason: "goodwill" };
    }

    arNoteFormSet(field, value) {
        this.state.gl.arNoteForm[field] = value;
    }

    async arCreateNote() {
        const form = this.state.gl.arNoteForm;
        if (!form.amount) {
            this.showToast(t('Credit amount is required'));
            return;
        }
        const res = await this._arCall("/p03/ar/credit-note/create", { ...form }, "Credit note created");
        if (res.success) {
            this.state.gl.arNoteForm = null;
            this.loadGlData();
        }
    }

    async arIssueNote(noteId) {
        const res = await this._arCall("/p03/ar/credit-note/issue", { note_id: noteId }, "Issued & applied");
        if (res.success) this.loadGlData();
    }

    /* ---------------- payment links ---------------- */

    async arCreateLink(invoiceId) {
        const res = await this._arCall("/p03/ar/payment-link/create", { invoice_id: invoiceId }, "Single-use link generated (gateway = porting phase)");
        if (res.success) this.loadGlData();
    }

    /* ---------------- consolidated bills ---------------- */

    async arConsolidatedGenerate(customerId) {
        const today = new Date();
        const start = new Date(today.getFullYear(), today.getMonth(), 1).toISOString().slice(0, 10);
        const res = await this._arCall("/p03/ar/consolidated/generate", {
            customer_id: customerId,
            period_start: start,
            period_end: today.toISOString().slice(0, 10),
        }, "Consolidated bill generated");
        if (res.success) this.loadGlData();
    }

    async arConsolidatedSend(billId) {
        const res = await this._arCall("/p03/ar/consolidated/send", { bill_id: billId }, "Marked sent");
        if (res.success) this.loadGlData();
    }

    /* ---------------- statements ---------------- */

    async arRunStatement() {
        const gl = this.state.gl;
        if (!gl.stmtCustomer) {
            this.showToast(t('Pick a customer'));
            return;
        }
        try {
            const res = await this.rpc("/p03/ar/statement", {
                customer_id: gl.stmtCustomer,
                date_from: gl.arFrom,
                date_to: gl.arTo,
            });
            gl.data = { statement: res.statement };
        } catch (e) {
            this.showToast(t('Statement run failed'));
        }
    }

    arStatementCsv() {
        const stmt = this.state.gl.data && this.state.gl.data.statement;
        if (!stmt) return;
        const rows = [["Date", "Type", "Reference", "Detail", "Amount (BDT)"]]
            .concat(stmt.rows.map((r) => [r.date, r.kind, r.ref, r.detail, r.charge.toFixed(2)]));
        const csv = rows.map((r) => r.map((c) => `"${String(c).replace(/"/g, '""')}"`).join(",")).join("\n");
        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = `1000FiX_Statement_${stmt.customer_id}_${stmt.date_to}.csv`;
        a.click();
        URL.revokeObjectURL(a.href);
        this.showToast(`Statement exported (${stmt.rows.length} lines) ✓`);
    }

    /* Resolve a cross-navigation term to a real module/screen — no dead
       hardcoded targets. */
    openCross(term) {
        const q = String(term).toLowerCase();
        const mod = Object.values(P03_MODULES).find(m =>
            m.title.toLowerCase().includes(q) || m.en.toLowerCase().includes(q) ||
            m.area.toLowerCase() === q);
        if (mod) return this.openModule(mod.code);
        let hit = null;
        for (const m of Object.values(P03_MODULES)) {
            for (const g of m.groups) {
                for (const sc of g.screens) {
                    if (sc.en.toLowerCase().includes(q) || g.en.toLowerCase().includes(q)) {
                        hit = sc.id;
                        break;
                    }
                }
                if (hit) break;
            }
            if (hit) break;
        }
        if (hit) return this.openScreen(hit);
        this.showToast(`No module matches '${term}' yet — it lands with its porting phase.`);
    }

    /* Open the P03 Report Center (A10/A11) for the report library. */
    /* A built-in report chip: opens the in-workspace screen that already
     * renders this report's data (M19/M20 routed); honest toast otherwise —
     * NEVER a doAction that leaves the workspace shell. */
    openReport(reportName, mid = this.state.activeModuleId) {
        const route = P03_REPORT_ROUTES[`${mid}:${reportName}`];
        if (route && (P03_DATA_SCREENS[route] || P03_LIVE_SCREENS[route])) {
            this.openScreen(route);
            return;
        }
        this.showToast(this.tf("Report '{name}' arrives with the workspace phase of its module", { name: reportName }));
    }

    openFregReport(reportName) {
        this.openReport(reportName, this.state.activeFreg ? this.state.activeFreg.mid : this.state.activeModuleId);
    }

    /* The header "▤ Reports" chip: scroll to the Built-in Reports card. */
    scrollToBuiltinReports() {
        const el = document.getElementById("builtin-reports");
        if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    /* Receipts screen: live tender mix (Payment Method Mix report data). */
    get glReceiptMethodMix() {
        const gl = this.state.gl;
        if (!gl || gl.kind !== "ar_receipts" || !gl.data) return [];
        const mix = {};
        for (const r of gl.data.rows) {
            if (r.state === "reversed") continue;
            const key = r.method || "—";
            const slot = mix[key] || (mix[key] = { method: key, count: 0, amount: 0 });
            slot.count += 1;
            slot.amount += r.amount || 0;
        }
        return Object.values(mix).sort((a, b) => b.amount - a.amount);
    }

    openReportCenter() {
        this.actionService.doAction("cd_p03_portal.action_p03_report_center");
    }

    async loadRecentOrders() {
        try {
            const res = await this.rpc("/p03/orders/list", { limit: 25 });
            if (res && res.orders) this.state.recentOrders = res.orders;
        } catch (e) {
            console.warn("Could not fetch /p03/orders/list:", e);
        }
    }

    /* --- Real chart getters (from /p03/stats) --- */
    get sparkSvg1() {
        return markup(fxSparkSvg(this.state.stats?.trend?.values, CHART_VARS[0]));
    }
    get sparkSvg2() { return ""; }
    get sparkSvg3() { return ""; }
    get sparkSvg4() { return ""; }
    get sparkSvg5() { return ""; }
    get sparkSvg6() { return ""; }

    get revenueLineSvg() {
        const t = this.state.stats?.trend;
        if (!t) return markup('<div class="chart-empty">Loading live data…</div>');
        if (!t.values.some((v) => v)) {
            return markup('<div class="chart-empty">No service orders recorded yet — the 12-month trend appears once intake data exists.</div>');
        }
        return markup(fxLineSvg(t.labels, t.values));
    }

    get channelLegend() {
        const mix = this.state.stats?.channel_mix || {};
        return Object.entries(mix).map(([k, v], i) => ({
            label: SERVICE_TYPE_LABELS[k] || k,
            value: v,
            color: `var(--chart-${(i % 8) + 1})`,
        }));
    }

    get channelDonutSvg() {
        const mix = this.state.stats?.channel_mix;
        if (!mix) return markup('<div class="chart-empty">Loading live data…</div>');
        const data = Object.entries(mix).map(([k, v]) => ({ v }));
        const total = Object.values(mix).reduce((a, b) => a + b, 0);
        if (!total) {
            return markup('<div class="chart-empty">No intake in the last 30 days — the channel mix appears with the first order.</div>');
        }
        return markup(fxDonutSvg(data, String(total), "orders · 30 days"));
    }

    /* --- Financial preview of the intake form (display only; the
           persisted money is backend-computed on fix.estimate) --- */
    get lineSubtotal() {
        return this.state.formData.lines.reduce((sum, ln) => sum + (Number(ln.price) || 0) * (Number(ln.qty) || 0), 0);
    }
    get lineVat() {
        return Math.round(this.lineSubtotal * 0.15);
    }
    get lineGrandTotal() {
        return this.lineSubtotal + this.lineVat;
    }

    /* --- Navigation & Tabstrip Management --- */
    openHome() {
        this.state.viewMode = "home";
        this.state.activeTab = "home";
    }

    /* Team chat: the native Odoo Discuss app, addressed by action xmlid so
     * the link survives any path Odoo's mail module re-asserts on upgrade.
     * Opened in a new tab — never a doAction, which would swap the D365
     * shell away. */
    openChat() {
        window.open("/odoo/action-mail.action_discuss", "_blank", "noopener");
        this.showToast(this.t("Team Chat opened in a new tab (Discuss)"));
    }

    openModule(mid) {
        const mod = P03_MODULES[mid] || P03_MODULES.M01;
        this.state.activeModuleId = mid;
        this.state.activeModule = mod;
        this.state.viewMode = "workspace";
        this.state.financeKpis = null;
        this.ensureTab(`mod-${mid}`, `${mid} · ${mod.en}`, mod.icon, "workspace", { mid });
        this.state.megaMenuOpen = false;
        // A08 modules fetch REAL KPI aggregates (metric keys on the kpis);
        // A02 modules have their own service KPI endpoint (same shape);
        // A11 · M25/M26 serve their own KPI payloads.
        if ((mod.kpis || []).some(k => k.m)) {
            const kpiRoute = mid === "M02" ? "/p03/field/kpis"
                : (mid === "M31" ? "/p03/workshop/kpis"
                : (mid === "M03" ? "/p03/logistics/kpis"
                : (mid === "M04" ? "/p03/branch/kpis"
                : (mid === "M05" ? "/p03/msp/kpis"
                : (mid === "M06" ? "/p03/data/kpis"
                : (mid === "M29" ? "/p03/security/kpis"
                : (mid === "M28" ? "/p03/platform/kpis"
                : (mid === "M62" ? "/p03/dataops/kpis"
                : (mid === "M63" ? "/p03/workflow/kpis"
                : (mid === "M25" ? "/p03/bi/kpis"
                : (mid === "M26" ? "/p03/ml/kpis"
                : (mod.area === "A12" ? "/p03/platform/kpis"
                : (mod.area === "A10" ? "/p03/grc/kpis"
                : (mod.area === "A05" ? "/p03/circular/kpis"
                : (mod.area === "A09" ? "/p03/people/kpis"
                : (mod.area === "A07" ? "/p03/asset/kpis"
                : (mod.area === "A06" ? "/p03/supply/kpis"
                : (mod.area === "A02" ? "/p03/service/kpis" : "/p03/finance/kpis"))))))))))))))))));
            this.rpc(kpiRoute, { module: mid })
                .then((res) => {
                    if (this.state.activeModuleId === mid && res && res[mid]) {
                        this.state.financeKpis = res[mid];
                    }
                })
                .catch(() => { /* KPIs stay placeholder "—" on failure */ });
        }
    }

    openFreg(mid, fnIndex) {
        const mod = P03_MODULES[mid] || P03_MODULES.M01;
        const sub = (mod.freg && mod.freg.sub[fnIndex]) || ["1", "General Capability", 8];
        // A sub-module may declare what actually implements it:
        //   ['6', 'Kits & Bundles', 4, { model, screens, reports, forms }]
        // Without that 4th element this panel used to borrow the MODULE's
        // first six screens — identical for every sub-module, so sub-module 6
        // listed Brand and Typed Taxonomy and nothing about kits.
        const map = sub[3] || null;

        const all = [];
        mod.groups.forEach(g => {
            g.screens.forEach(s => all.push({ ...s, groupEn: g.en }));
        });
        // Report screens are declared in SCREENS and reached through the
        // module's report chips, not its nav groups - resolve them there too,
        // or a mapped report silently drops out of the panel.
        const resolve = (id) => {
            const nav = all.find(s => s.id === id);
            if (nav) return nav;
            const cfg = P03_DATA_SCREENS[id];
            return cfg ? { id, en: cfg.title || id, bn: cfg.title_bn || cfg.bn, t: "r", groupEn: "Reports" } : null;
        };
        const screens = map && map.screens ? map.screens.map(resolve).filter(Boolean) : [];

        this.state.activeFreg = {
            mid,
            fnIndex,
            subModuleNo: sub[0],
            subModuleTitle: sub[1],
            functionCount: sub[2],
            module: mod,
            model: (map && map.model) || null,
            mapped: !!map,
            screens,
            reports: (map && map.reports) || [],
            forms: (map && map.forms) || [],
            loading: !!(map && map.model),
            gridData: { cols: [], rows: [] }
        };
        this.state.viewMode = "freg";
        this.ensureTab(`freg-${mid}-${fnIndex}`, `⌘ ${sub[1]}`, "⌘", "freg", { mid, fnIndex });
        if (map && map.model) this.loadFregRecords(map);
    }

    /* The sub-module's OWN live records, from the same whitelisted endpoint
     * every other live screen uses. The table this replaces was built by
     * generateGridData(), whose every return path ended `rows: []` — it chose
     * column headers by keyword and never carried data, in any module. */
    async loadFregRecords(map) {
        const fr = this.state.activeFreg;
        try {
            const res = await this.rpc("/p03/model/records", {
                model: map.model,
                cols: map.cols || [],
                // a sub-module is often a SLICE of a shared model (holds,
                // rework, escalations) - the same safe domain list screens use
                domain: map.domain || [],
                lang: this.state.lang === "bn" ? "bn_BD" : "en_US",
            });
            if (!this.state.activeFreg || this.state.activeFreg !== fr) return;
            if (!res || res.error) {
                fr.gridData = { cols: [], rows: [], error: (res && res.error) || "unavailable" };
            } else {
                const labels = res.labels || {};
                const cols = (res.rows && res.rows.length)
                    ? Object.keys(res.rows[0]).filter(k => k !== "id")
                    : (map.cols || []);
                fr.gridData = {
                    cols: cols.map(c => labels[c] || c),
                    rows: (res.rows || []).map(r => {
                        const row = cols.map(c => {
                            const v = r[c];
                            if (v === null || v === undefined || v === false) return "—";
                            if (typeof v === "object") return v.label || v.name || v.key || "—";
                            return v;
                        });
                        // the record id rides as a non-enumerated property so
                        // the grid still renders only cells, exactly as the
                        // order grids carry `row.orderId`
                        Object.defineProperty(row, "recId", { value: r.id, enumerable: false });
                        return row;
                    }),
                    total: res.total || (res.rows || []).length,
                };
            }
        } catch (e) {
            fr.gridData = { cols: [], rows: [], error: this.t("Could not load records") };
        }
        fr.loading = false;
        this.render(true);
    }

    openScreen(screenId, customGroupEn) {
        let hit = null;
        for (const mid in P03_MODULES) {
            const m = P03_MODULES[mid];
            for (const g of m.groups) {
                for (const sc of g.screens) {
                    if (sc.id === screenId) {
                        hit = { mid, m, g, sc };
                        break;
                    }
                }
                if (hit) break;
            }
            if (hit) break;
        }

        if (!hit) {
            const mod = this.state.activeModule;
            // Non-registry screens (report/form routes like M33-rpt-growth)
            // must NOT inherit the module's FIRST screen's title — that made
            // every built-in report render as "Party Directory" (user PDF,
            // audit D14). Synthesize the hit from the data-screen config.
            const ds = P03_DATA_SCREENS[screenId];
            const fallbackSc = ds
                ? { id: screenId, en: ds.title || ds.report || screenId, bn: ds.title_bn || ds.title || ds.report || screenId, t: ds.kind === "model_form" ? "f" : "r" }
                : mod.groups[0].screens[0];
            hit = { mid: this.state.activeModuleId, m: mod, g: mod.groups[0], sc: fallbackSc };
        }

        // In-workspace D365 screens (M19 GL pilot): render INSIDE the shell
        // from live /p03/gl/* data — checked BEFORE the live-model dispatch
        // so these screens never leave the workspace for a stock Odoo view.
        const dataScreen = P03_DATA_SCREENS[screenId];
        if (dataScreen) {
            // D365 in-workspace record forms (user directive 2026-10-27):
            // schema-driven form screens render inside the shell, never as
            // an Odoo dialog.
            if (dataScreen.kind === "model_form") {
                this.openFormScreen(screenId, hit, dataScreen);
                return;
            }
            this.openGlScreen(screenId, hit, dataScreen);
            return;
        }

        // Live surfaces (A08 finance): screens backed by real Odoo models
        // open the actual list (or form, for type-f screens) view instead of
        // the empty placeholder grid.
        const liveModel = P03_LIVE_SCREENS[screenId];
        if (liveModel) {
            const isForm = hit.sc.t === "f";
            this.actionService.doAction({
                type: "ir.actions.act_window",
                name: hit.sc.en,
                res_model: liveModel,
                views: isForm ? [[false, "form"]] : [[false, "list"], [false, "form"]],
                target: "current",
            });
            return;
        }

        // A08 finance screens are ONLY ever live data screens: one without a
        // data screen shows an honest "not built" state, never the generic
        // service-order grid (repair filters, order rows) other areas use.
        // The same honesty applies to ANY unregistered dashboard (t:'d') or
        // calculator (t:'c') screen: code reached here only when no live or
        // data surface is registered, so the old behavior — silently falling
        // through to console mode and rendering the M02 dispatch console —
        // showed the WRONG module's content. Render "not built" instead.
        if (hit.m.area === "A08" || hit.sc.t === "d" || hit.sc.t === "c") {
            this.state.activeScreen = {
                id: hit.sc.id, en: hit.sc.en, bn: hit.sc.bn, t: hit.sc.t, mid: hit.mid,
                moduleTitle: hit.m.title, groupTitle: customGroupEn || hit.g.en,
                notBuilt: true, gridData: { cols: [], rows: [] },
            };
            this.state.filteredGridRows = [];
            this.state.viewMode = "screen";
            this.ensureTab(`screen-${hit.sc.id}`, `◌ ${hit.sc.en}`, "◌", "screen", { screenId: hit.sc.id });
            return;
        }

        const glyph = hit.sc.t === "g" ? "⛁" : hit.sc.t === "f" ? "▤" : hit.sc.t === "d" ? "▦" : hit.sc.t === "c" ? "⌘" : "◈";
        const grid = generateGridData(hit.sc.id, hit.g.en, hit.m.en);

        // Order-like screens surface the REAL recent orders (amounts from
        // the order's latest estimate; null until one exists). The order id
        // rides as a non-enumerated property — the grid renders only cells.
        if (/order|all|intake|wip/i.test(hit.sc.id) && this.state.recentOrders.length > 0) {
            grid.rows = this.state.recentOrders.map(o => {
                const row = [
                    o.name,
                    o.customer_id ? o.customer_id[1] : "—",
                    o.device_id ? o.device_id[1] : "—",
                    o.branch_id ? o.branch_id[1] : "—",
                    o.technician_id ? o.technician_id[1] : "Unassigned",
                    this.stateLabel(o.state),
                    o.sla_resolution_deadline ? o.sla_resolution_deadline.slice(0, 10) : "—",
                    fmtBDT(o.grand_total),
                    fmtBDT(o.vat_amount)
                ];
                row.orderId = o.id;
                return row;
            });
        }

        this.state.activeScreen = {
            id: hit.sc.id,
            en: hit.sc.en,
            bn: hit.sc.bn,
            t: hit.sc.t,
            mid: hit.mid,
            moduleTitle: hit.m.title,
            groupTitle: customGroupEn || hit.g.en,
            gridData: grid
        };
        this.state.filteredGridRows = [...grid.rows];
        // Type-f screens render as the grid view (no separate form template
        // exists in the workspace canvas) — live ones opened a real Odoo
        // form above; the rest show the honest empty state.
        this.state.viewMode = hit.sc.t === "d" || hit.sc.t === "c" ? "console" : "screen";
        this.ensureTab(`screen-${hit.sc.id}`, `${glyph} ${hit.sc.en}`, glyph, this.state.viewMode, { screenId: hit.sc.id });
    }

    /* Open a record from the SUB-MODULE records grid.
     *
     * Not `openRecord` - that one is hard-wired to service orders
     * (`/p03/order/get`), so clicking a kit, a rate card or a referral there
     * sent its NAME as an order id and raised "Oops! Something went wrong"
     * (reported 2026-11-01 with a screenshot of M37 / Kits & Bundles).
     *
     * Routes through the module's declared form for the sub-module's model,
     * which is the same path a normal list row takes. */
    openFregRecord(row) {
        const fr = this.state.activeFreg;
        if (!fr || !fr.model) return;
        const recId = (row && row.recId) || null;
        // open the sub-module's own screen first so the form has its context
        const target = (fr.screens && fr.screens[0] && fr.screens[0].id) || null;
        if (target) this.openScreen(target);
        if (!recId) return;
        if (this.openModuleFormForModel(fr.model, recId)) return;
        this.openRecordTab({
            kind: "model_record",
            id: recId,
            icon: (this.state.activeModule && this.state.activeModule.icon) || "▤",
            title: String((row && row[0]) || ("#" + recId)),
            subtitle: fr.model,
            moduleId: this.state.activeModuleId,
        });
    }

    /* --- Master-detail record: REAL backend fetch --- */
    async openRecord(orderRow) {
        const orderId = orderRow && orderRow.id ? orderRow.id : orderRow;
        const tabId = `rec-${orderId}`;
        this.ensureTab(tabId, "▤ …", "▤", "record", { orderId });
        const tab = this.state.openTabs.find(t => t.id === tabId);
        this.state.viewMode = "record";
        this.state.activeRecord = null; // loading state
        try {
            const res = await this.rpc("/p03/order/get", { order_id: orderId });
            if (!res || !res.success) {
                this.showToast(res?.error || "Order not found");
                return;
            }
            const o = res.order;
            this.state.activeRecord = {
                id: o.name,
                order_id: o.id,
                name: o.name,
                customer_name: o.customer_name,
                customer_phone: o.customer_phone,
                device_name: o.device_name,
                serial_number: o.serial_number,
                branch_name: o.branch_name,
                technician: o.technician || "Unassigned",
                priority: (o.priority || "normal").toUpperCase(),
                current_stage: STAGE_OF_STATE[o.state] || 1,
                state: o.state,
                service_type: o.service_type,
                fault_description: o.fault_description,
                total_amount: o.grand_total,
                vat_amount: o.vat_amount,
                taxable_amount: o.grand_total != null && o.vat_amount != null
                    ? o.grand_total - o.vat_amount : null,
                sla_clock: o.sla_resolution_deadline || "",
                company: res.company
            };
            this.state.recordLines = (res.estimate_lines || []).map((l, i) => ({
                id: i,
                desc: l.description,
                type: l.line_type === "labour" ? "Labor" : l.line_type === "part" ? "Part" : "Diagnostic",
                qty: l.quantity,
                price: l.unit_price,
                total: l.line_total,
                status: `Estimate: ${o.estimate_state || "draft"}`
            }));
            this.state.recordAttachments = (res.attachments || []).map((a, i) => ({
                id: i,
                title: a.title,
                type: a.type || "FILE",
                size: a.size_kb ? `${a.size_kb} KB` : "—",
                date: (a.date || "").slice(0, 16).replace("T", " "),
                tag: "Record",
                icon: ATTACH_ICONS[(a.type || "").toLowerCase()] || "📎"
            }));
            this.state.recordAuditTrail = (res.audit_trail || []).map(m => ({
                time: (m.time || "").slice(0, 19).replace("T", " "),
                actor: m.actor,
                event: (m.body || "").replace(/<[^>]+>/g, "").slice(0, 140) || "—",
                state: "",
                ip: ""
            }));
            tab.title = `▤ ${o.name}`;
        } catch (e) {
            console.error("Failed to load order", e);
            this.showToast(t('Failed to load the order from the backend.'));
        }
    }

    openNewForm() {
        const mid = this.state.activeModuleId || "M01";
        const create = P03_MODULE_CREATE[mid];
        if (create && create.screen && P03_DATA_SCREENS[create.screen]) {
            const cfg = P03_DATA_SCREENS[create.screen];
            this.openFormScreen(
                create.screen,
                { sc: { en: cfg.title || create.label, t: "f" }, m: { title: (this.state.activeModule && this.state.activeModule.title) || "" } },
                cfg
            );
            return;
        }
        if (create && create.model) {
            if (this.openModuleFormForModel(create.model)) {
                return;
            }
        }
        if (P03_DATA_SCREENS["M01-form-order"]) {
            const cfg = P03_DATA_SCREENS["M01-form-order"];
            this.openFormScreen(
                "M01-form-order",
                { sc: { en: cfg.title || "New Service Order", t: "f" }, m: { title: "M01 · Service Requests & Orders" } },
                cfg
            );
            return;
        }
        this.state.formData = this.blankForm();
        this.state.formModalOpen = true;
        this.state.modalStep = 1;
    }

    closeModal() {
        this.state.formModalOpen = false;
    }

    setModalStep(step) {
        this.state.modalStep = step;
    }

    /* =================================================================
     * UNIVERSAL RECORD TABS (user directive 2026-10-29).
     *
     * Every record surface — M20 invoices, M19 journal entries, every
     * module's model_list rows — opens the record in its OWN closable tab
     * in the workspace tabstrip instead of expanding a panel below the
     * grid. One engine serves M01–M67:
     *   - smart reuse: reopening a record focuses its existing tab;
     *   - per-tab payload cache: switching back is instant, no refetch;
     *   - cap + eviction: >16 tabs evicts the oldest record tab
     *     (session-tab guidance: a tab bar must stay a map, not a pile).
     * ================================================================= */
    async openRecordTab(desc) {
        const tabId = `rec-${desc.kind}-${desc.id}`;
        const icon = desc.icon || "▤";
        // the tabstrip renders tab.icon in its own slot — the title carries
        // only the record name
        this.ensureTab(tabId, desc.title || String(desc.id), icon, "record_view", desc);
        this.state.viewMode = "record_view";
        const cached = this._recCache[tabId];
        if (cached) {
            this.state.recView = cached;
            return;
        }
        this.state.recView = { ...desc, tabId, loading: true, data: null, error: null };
        try {
            const data = await this._fetchRecordData(desc);
            const error = (data && data.error) || null;
            const view = { ...desc, tabId, loading: false, data: error ? null : data, error };
            this.state.recView = view;
            if (!error) this._recCache[tabId] = view;
        } catch (e) {
            this.state.recView = { ...desc, tabId, loading: false, data: null, error: this.t("Could not load the record") };
        }
    }

    async _fetchRecordData(desc) {
        if (desc.kind === "ar_invoice") {
            return await this.rpc("/p03/ar/invoice", { invoice_id: desc.id });
        }
        if (desc.kind === "journal_entry") {
            return await this.rpc("/p03/gl/je", { move_id: desc.id });
        }
        if (desc.kind === "model_record") {
            // the row is already the server payload; the pane renders its
            // declared columns and the same workflow actions as the grid
            return { row: desc.row || {} };
        }
        return null;
    }

    /* Re-render a record tab after an action (issue, post, approve…) —
     * drops the cache entry and refetches. */
    async refreshRecordTab() {
        const rv = this.state.recView;
        if (!rv || !rv.tabId) return;
        delete this._recCache[rv.tabId];
        const desc = { kind: rv.kind, id: rv.id, title: rv.title, subtitle: rv.subtitle, icon: rv.icon, row: rv.row, screenId: rv.screenId, moduleId: rv.moduleId };
        this.state.recView = { ...desc, tabId: rv.tabId, loading: true };
        const data = await this._fetchRecordData(desc);
        const error = (data && data.error) || null;
        const view = { ...desc, tabId: rv.tabId, loading: false, data: error ? null : data, error };
        this.state.recView = view;
        if (!error) this._recCache[rv.tabId] = view;
        // the source grid must show the new state next time it is opened
        if (this.state.gl && this.state.gl.kind !== "model_form") {
            const stale = Object.keys(this._recCache).filter((k) => k !== rv.tabId);
            stale.forEach((k) => delete this._recCache[k]);
        }
    }

    /* Run a record action, then refresh both the pane and the source grid. */
    async recAction(fn) {
        try {
            await fn();
        } finally {
            await this.refreshRecordTab();
            if (this.state.gl && typeof this.loadGlData === "function" && this.state.gl.screenId) {
                this.loadGlData();
            }
        }
    }

    closeRecordTab() {
        const rv = this.state.recView;
        if (!rv) return;
        this.closeTab(rv.tabId);
    }

    /* Back-link from the record pane to the grid it came from. */
    goBackToScreen() {
        const rv = this.state.recView;
        if (rv && rv.screenId) this.openScreen(rv.screenId);
    }

    /* The declared workflow actions for a model_list row, filtered to the
     * row's current state exactly as the grid action bar does. */
    recActionsFor(row) {
        const gl = this.state.gl;
        const cfg = (gl && gl.modelCfg && gl.modelCfg.actions) || [];
        if (!row) return [];
        return cfg.filter((a) => !a.states || a.states.includes(row.state));
    }

    /* [label, value] pairs for the record pane, from the screen's declared
     * columns and the row payload (server labels win). */
    recFieldPairs(row) {
        const gl = this.state.gl;
        if (!row) return [];
        const cfg = gl && gl.modelCfg;
        const cols = (cfg && cfg.cols) || Object.keys(row).filter((k) => k !== "id").slice(0, 24);
        const labels = (gl && gl.data && gl.data.labels) || {};
        return cols.map((c) => [labels[c] || c, this.mlCell(row, c)]);
    }

    ensureTab(tabId, title, icon, mode, payload = {}) {
        // The strip renders `icon` in its own span, so a title that also
        // starts with it would show the glyph twice ("⛁ ⛁ Dedup Rule").
        if (icon && typeof title === "string" && title.startsWith(`${icon} `)) {
            title = title.slice(icon.length + 1);
        }
        const existing = this.state.openTabs.find(t => t.id === tabId);
        if (!existing) {
            this.state.openTabs.push({ id: tabId, title, icon, mode, payload });
            // Cap: evict the OLDEST record tab once past the limit — the
            // tabstrip must stay navigable (home and screens are kept).
            const cap = this._REC_TAB_CAP || 16;
            if (this.state.openTabs.length > cap) {
                const victim = this.state.openTabs.find(
                    (t) => t.mode === "record_view" && t.id !== tabId && t.id !== this.state.activeTab
                );
                if (victim) {
                    this.state.openTabs = this.state.openTabs.filter((t) => t.id !== victim.id);
                    delete this._recCache[victim.id];
                }
            }
        }
        this.state.activeTab = tabId;
    }

    switchTab(tab) {
        this.state.activeTab = tab.id;
        this.state.viewMode = tab.mode;
        if (tab.mode === "workspace" && tab.payload?.mid) {
            this.state.activeModuleId = tab.payload.mid;
            this.state.activeModule = P03_MODULES[tab.payload.mid] || P03_MODULES.M01;
        } else if (tab.mode === "freg" && tab.payload?.mid) {
            this.openFreg(tab.payload.mid, tab.payload.fnIndex);
        } else if (tab.mode === "screen" && tab.payload?.screenId) {
            this.openScreen(tab.payload.screenId);
        } else if (tab.mode === "gl" && tab.payload?.screenId) {
            // record forms restore with their OWN recordId — a per-record tab
            // must never reload into the wrong record
            if (tab.payload.recordId) {
                const dataScreen = P03_DATA_SCREENS[tab.payload.screenId];
                if (dataScreen) {
                    const cached = this._formCache && this._formCache[tab.id];
                    const hit = (cached && cached.hit) || {
                        sc: { en: dataScreen.title || tab.payload.screenId, t: "f" },
                        m: { title: (this.state.activeModule && this.state.activeModule.title) || "" },
                    };
                    this.openFormScreen(tab.payload.screenId, hit, { ...dataScreen, recordId: tab.payload.recordId });
                    return;
                }
            }
            this.openScreen(tab.payload.screenId);
        } else if (tab.mode === "record_view") {
            // restore the cached record payload; refetch only when evicted
            const cached = this._recCache[tab.id];
            if (cached) {
                this.state.viewMode = "record_view";
                this.state.recView = cached;
            } else {
                this.openRecordTab(tab.payload || {});
            }
        } else if (tab.mode === "record" && tab.payload?.orderId) {
            this.openRecord(tab.payload.orderId);
        } else if (tab.mode === "dispatch_console") {
            this.state.viewMode = "dispatch_console";
            this.loadDispatchMap();
        } else if (tab.mode === "branch_console") {
            this.state.viewMode = "branch_console";
            this.loadConsoleData(this.state.selectedBranchId);
        } else if (tab.mode === "workshop_console") {
            this.state.viewMode = "workshop_console";
            this.loadConsoleData(this.state.selectedBranchId);
        }
    }

    closeTab(tabId, ev) {
        if (ev) ev.stopPropagation();
        if (tabId === "home") return; // Keep home tab permanent
        if (this._recCache) delete this._recCache[tabId];
        this.state.openTabs = this.state.openTabs.filter(t => t.id !== tabId);
        if (this.state.activeTab === tabId) {
            const last = this.state.openTabs[this.state.openTabs.length - 1];
            this.switchTab(last);
        }
    }

    // --- Grid Filtering ---
    applyGridFilter(field, val) {
        this.state.gridFilter[field] = val;
        if (!this.state.activeScreen || !this.state.activeScreen.gridData) return;

        let rows = this.state.activeScreen.gridData.rows;
        const branch = this.state.gridFilter.branch;
        const status = this.state.gridFilter.status;
        const q = this.state.gridFilter.search.toLowerCase();

        if (branch && branch !== "All branches") {
            rows = rows.filter(r => r.some(c => String(c).toLowerCase().includes(branch.toLowerCase())));
        }
        if (status && status !== "All" && status !== "Any") {
            rows = rows.filter(r => String(r[5] || "").toLowerCase() === status.toLowerCase());
        }
        if (q) {
            rows = rows.filter(r => r.some(c => String(c).toLowerCase().includes(q)));
        }
        this.state.filteredGridRows = rows;
    }

    setFilterViewPill(pill) {
        this.state.gridFilter.viewPill = pill;
        if (pill === "all") {
            this.state.gridFilter.status = "All";
        } else if (pill === "risk") {
            this.state.gridFilter.status = "diagnostic";
        }
        this.applyGridFilter("viewPill", pill);
    }

    // --- BPF stepper: strictly backend-driven (AS-06) ---
    async advanceStage() {
        if (!this.state.activeRecord) return;
        const nextStageId = Math.min(8, (STAGE_OF_STATE[this.state.activeRecord.state] || 1) + 1);
        const targetState = STATE_OF_STAGE[nextStageId];
        try {
            const res = await this.rpc("/p03/order/advance_stage", {
                order_id: this.state.activeRecord.order_id,
                next_state: targetState
            });
            if (res && res.success) {
                this.state.activeRecord.state = res.state;
                this.state.activeRecord.current_stage = STAGE_OF_STATE[res.state] || 1;
                this.showToast(`Workflow stage advanced to: ${res.state}`);
                await this.openRecord(this.state.activeRecord.order_id);
            } else {
                this.showToast(res?.error || "Transition refused by the backend.");
            }
        } catch (e) {
            this.showToast(this.t('Stage transition failed — see server log.'));
        }
    }

    holdStage() {
        if (!this.state.activeRecord) return;
        this.showToast(t('Hold requires a reason dialog — lands with the SLA-hold phase (state stays unchanged).'));
    }

    // --- Intake form line items ---
    addLineItem() {
        this.state.formData.lines.push({ desc: "", type: "Part", qty: 1, price: 0 });
    }

    removeLineItem(idx) {
        if (this.state.formData.lines.length > 1) {
            this.state.formData.lines.splice(idx, 1);
        }
    }

    // --- Two-way backend form submission ---
    async submitServiceOrder() {
        const fd = this.state.formData;
        if (!fd.customer_name || !fd.customer_phone || !fd.fault_description || !fd.serial) {
            this.showToast(t('Customer name, phone, serial and fault description are required.'));
            this.state.modalStep = 1;
            return;
        }
        this.showToast(t('Submitting Service Order to backend…'));
        try {
            const res = await this.rpc("/p03/order/create", {
                customer_name: fd.customer_name,
                customer_phone: fd.customer_phone,
                branch_name: fd.branch_name,
                brand: fd.brand,
                model: fd.model,
                serial: fd.serial,
                fault_description: fd.fault_description,
                priority: fd.priority,
                service_type: fd.service_type,
                entitlement: fd.entitlement,
                idempotency_key: (typeof crypto !== "undefined" && crypto.randomUUID)
                    ? crypto.randomUUID() : String(Date.now())
            });

            if (res && res.success) {
                this.closeModal();
                this.showToast(`Order created: ${res.order_name}${res.idempotent_replay ? " (idempotent replay)" : ""}`);
                await this.loadRecentOrders();
                await this.openRecord(res.order_id);
            } else {
                this.showToast(`Backend rejected: ${res?.error || "unknown error"}`);
            }
        } catch (err) {
            console.error("Submission failed:", err);
            this.showToast(t('Submission failed — the order was NOT created.'));
        }
    }

    // --- Search & Shell Controls ---
    toggleNavRail() {
        this.state.navExpanded = !this.state.navExpanded;
    }

    toggleMegaMenu() {
        this.state.megaMenuOpen = !this.state.megaMenuOpen;
    }

    toggleTheme() {
        this.state.theme = this.state.theme === "light" ? "dark" : "light";
    }

    toggleDensity() {
        this.state.density = this.state.density === "compact" ? "normal" : "compact";
    }

    toggleLang() {
        this.setLang(this.state.lang === "en" ? "bn" : "en", { persist: true });
    }

    /* ---- i18n helpers (DE-17): ONE language at a time, English fallback ---- */

    _initLang() {
        let lang = null;
        try {
            lang = window.localStorage.getItem("p03_lang");
        } catch (_) { /* private mode */ }
        if (lang !== "bn" && lang !== "en") {
            const userLang = (this.userService && this.userService.lang) || "";
            lang = userLang.startsWith("bn") ? "bn" : "en";
        }
        this.state.lang = lang;
    }

    setLang(lang, { persist = false } = {}) {
        this.state.lang = lang;
        if (persist) {
            try {
                window.localStorage.setItem("p03_lang", lang);
            } catch (_) { /* private mode */ }
        }
    }

    /* t(s): the Bangla rendering in bn mode, the English key otherwise.
     * Unknown keys fall back to the English — never an invented value. */
    t(s) {
        if (this.state.lang === "bn" && s && Object.prototype.hasOwnProperty.call(P03_BN, s)) {
            return P03_BN[s];
        }
        return s;
    }

    /* tf(s, params): t() plus {token} substitution for interpolated strings. */
    tf(s, params = {}) {
        return this.t(s).replace(/\{(\w+)\}/g, (m, k) =>
            Object.prototype.hasOwnProperty.call(params, k) ? String(params[k]) : m);
    }

    /* tState(raw): model state keys → the active language's label. */
    tState(raw) {
        const row = raw != null ? P03_STATES[String(raw)] : null;
        if (!row) return raw;
        return this.state.lang === "bn" ? row.bn : row.en;
    }

    /* The active language's value for meta entities that carry both. */
    tBilingual(entity) {
        if (!entity) return "";
        return this.state.lang === "bn" ? entity.bn || entity.en : entity.en;
    }

    onModuleSearch(ev) {
        this.state.moduleSearchQuery = ev.target.value.toLowerCase();
    }

    get filteredNavAreas() {
        const q = this.state.moduleSearchQuery;
        if (!q) return this.areas;
        return this.areas.map(a => {
            const matchedMods = a.mods.filter(mKey => {
                const m = P03_MODULES[mKey];
                return m && (m.code.toLowerCase().includes(q) || m.en.toLowerCase().includes(q) || m.bn.includes(q));
            });
            return { ...a, mods: matchedMods };
        }).filter(a => a.mods.length > 0);
    }

    // --- Job Card & Tax Invoice Modal ---
    openJobCardModal() {
        if (!this.state.activeRecord) {
            this.showToast(t('Open a service order first — the Job Card prints the live record.'));
            return;
        }
        this.state.jobCardModalOpen = true;
    }

    closeJobCardModal() {
        this.state.jobCardModalOpen = false;
    }

    printJobCardWindow() {
        if (typeof window !== "undefined") {
            window.print();
        }
    }

    // --- Field Dispatch Modal ---
    openDispatchModal() {
        if (!this.state.activeRecord) {
            this.showToast(t('Open a service order first.'));
            return;
        }
        this.state.dispatchModalOpen = true;
    }

    closeDispatchModal() {
        this.state.dispatchModalOpen = false;
    }

    async confirmDispatch() {
        const df = this.state.dispatchForm;
        if (!df.technician) {
            this.showToast(t('Enter the technician to assign (matched against HR records).'));
            return;
        }
        try {
            const res = await this.rpc("/p03/dispatch/assign", {
                order_id: this.state.activeRecord.order_id,
                technician: df.technician,
                van_route: df.vanRoute,
                eta_window: df.etaWindow,
                notes: df.notes
            });
            if (res && res.success) {
                this.showToast(`Dispatched: ${res.technician} on ${res.work_order}`);
                this.closeDispatchModal();
                await this.openRecord(this.state.activeRecord.order_id);
            } else {
                this.showToast(res?.error || "Dispatch refused by the backend.");
            }
        } catch (e) {
            this.showToast(t('Dispatch failed — see server log.'));
        }
    }

    // --- Inventory Reservation Modal ---
    openInventoryModal() {
        if (!this.state.activeRecord) {
            this.showToast(t('Open a service order first.'));
            return;
        }
        this.state.inventoryModalOpen = true;
    }

    closeInventoryModal() {
        this.state.inventoryModalOpen = false;
    }

    async confirmInventoryReserve() {
        const inv = this.state.inventoryForm;
        if (!inv.partSku) {
            this.showToast(t('Enter the part SKU (matched against the product catalogue).'));
            return;
        }
        try {
            const res = await this.rpc("/p03/inventory/reserve", {
                order_id: this.state.activeRecord.order_id,
                part_sku: inv.partSku,
                qty: inv.qty,
                warehouse_bin: inv.bin
            });
            if (res && res.success) {
                this.showToast(`Reserved ${res.qty}× ${res.part} on ${res.work_order} (৳ ${res.unit_cost.toLocaleString("en-IN")}/unit)`);
                this.closeInventoryModal();
                await this.openRecord(this.state.activeRecord.order_id);
            } else {
                this.showToast(res?.error || "Reservation refused by the backend.");
            }
        } catch (e) {
            this.showToast(t('Reservation failed — see server log.'));
        }
    }

    // --- Dynamics-365 Tell Me Command Palette ---
    openTellMe() {
        this.state.tellMeOpen = true;
        this.state.tellMeQuery = "";
        this.state.tellMeLiveRecords = [];
    }

    closeTellMe() {
        this.state.tellMeOpen = false;
        this.state.tellMeQuery = "";
        this.state.tellMeLiveRecords = [];
    }

    async onTellMeInput(ev) {
        this.state.tellMeQuery = ev.target.value;
        const q = (ev.target.value || "").trim();
        if (q.length >= 2) {
            try {
                const res = await this.rpc("/p03/tellme", { query: q, limit: 12 });
                if (res && res.results) {
                    this.state.tellMeLiveRecords = res.results.filter(r => r.kind === "record");
                }
            } catch (err) {
                console.warn("TellMe RPC query error:", err);
            }
        } else {
            this.state.tellMeLiveRecords = [];
        }
    }

    get tellMeResults() {
        const q = (this.state.tellMeQuery || "").trim().toLowerCase();
        const baseActions = [
            { id: "act-new", title: "+ Create New Service Order", icon: "▤", group: "Actions", fn: () => { this.closeTellMe(); this.openNewForm(); } },
            { id: "act-disp", title: "⚡ Open Dispatch Console & Map", icon: "🗺", group: "Actions", fn: () => { this.closeTellMe(); this.openDispatchConsole(); } },
            { id: "act-branch", title: "🏢 Open Branch Operations Console", icon: "🏢", group: "Actions", fn: () => { this.closeTellMe(); this.openBranchConsole(); } },
            { id: "act-workshop", title: "🔧 Open Workshop Bench Console", icon: "🔧", group: "Actions", fn: () => { this.closeTellMe(); this.openWorkshopConsole(); } },
            { id: "act-tech", title: "⚡ Assign Field Technician", icon: "⚡", group: "Actions", fn: () => { this.closeTellMe(); this.openDispatchModal(); } },
            { id: "act-print", title: "🖨 Print Job Card & Mushak 6.3", icon: "🖨", group: "Actions", fn: () => { this.closeTellMe(); this.openJobCardModal(); } },
            { id: "act-inv", title: "📦 Reserve Parts from Inventory (M15)", icon: "📦", group: "Actions", fn: () => { this.closeTellMe(); this.openInventoryModal(); } },
            { id: "act-exp", title: "⤓ Export Active Data Grid to CSV", icon: "⤓", group: "Actions", fn: () => { this.closeTellMe(); this.exportGridCsv(); } }
        ];

        const liveRecords = (this.state.tellMeLiveRecords || []).map(r => ({
            id: `rec-${r.res_id || r.id}`,
            title: r.title,
            sub: r.sub || r.res_model,
            icon: r.icon || "📄",
            group: "Live Database Records (≤4 Clicks)",
            fn: () => {
                this.closeTellMe();
                if (r.res_model === "fix.service.order" && r.res_id) {
                    this.openRecord(r.res_id);
                } else if (r.res_id) {
                    this.actionService.doAction({
                        type: "ir.actions.act_window",
                        res_model: r.res_model || "fix.service.order",
                        res_id: r.res_id,
                        views: [[false, "form"]],
                    });
                }
            }
        }));

        if (!q) {
            return {
                actions: baseActions,
                records: [],
                modules: Object.values(P03_MODULES).slice(0, 6),
                screens: [
                    { id: "M01-all", title: "All Service Orders", icon: "⛁", group: "Service Operations", fn: () => { this.closeTellMe(); this.openScreen("M01-all"); } },
                    { id: "M02-dispatch", title: "Live Dispatch Board", icon: "🚐", group: "Field Service", fn: () => { this.closeTellMe(); this.openScreen("M02-dispatch"); } },
                    { id: "M03-cons", title: "Consignments & Custody Chain", icon: "📦", group: "Logistics", fn: () => { this.closeTellMe(); this.openScreen("M03-cons"); } },
                    { id: "M15-stock", title: "Parts Stock & Inventory", icon: "📦", group: "Supply Chain", fn: () => { this.closeTellMe(); this.openScreen("M15-stock"); } }
                ]
            };
        }

        const mods = Object.values(P03_MODULES).filter(m =>
            m.code.toLowerCase().includes(q) || m.en.toLowerCase().includes(q) || m.bn.includes(q)
        ).slice(0, 8);

        const scrs = [];
        Object.values(P03_MODULES).forEach(m => {
            m.groups.forEach(g => {
                g.screens.forEach(s => {
                    if (s.en.toLowerCase().includes(q) || s.id.toLowerCase().includes(q) || g.en.toLowerCase().includes(q) || m.en.toLowerCase().includes(q) || m.code.toLowerCase().includes(q)) {
                        scrs.push({
                            id: s.id,
                            title: `${s.en} (${m.code})`,
                            icon: "⛁",
                            group: m.title,
                            fn: () => { this.closeTellMe(); this.openScreen(s.id); }
                        });
                    }
                });
            });
        });

        const acts = baseActions.filter(a => a.title.toLowerCase().includes(q));

        return {
            actions: acts,
            records: liveRecords,
            modules: mods,
            screens: scrs.slice(0, 8)
        };
    }

    exportGridCsv() {
        const rows = this.state.filteredGridRows || [];
        if (!rows.length) {
            this.showToast(t('No rows in the active grid — nothing to export.'));
            return;
        }
        const cols = (this.state.activeScreen && this.state.activeScreen.gridData)
            ? this.state.activeScreen.gridData.cols
            : ["Row"];
        let csv = cols.join(",") + "\n";
        rows.forEach(r => {
            csv += r.map(c => `"${String(c).replace(/"/g, '""')}"`).join(",") + "\n";
        });
        if (typeof window !== "undefined") {
            const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `1000FiX_Export_${Date.now()}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
        this.showToast(`Exported ${rows.length} live records to CSV ✓`);
    }

    /* Console pipeline: REAL orders grouped into the 8 BPF stages. */
    get pipelineByStage() {
        const groups = {};
        this.bpfStages.forEach(st => { groups[st.id] = []; });
        this.state.recentOrders.forEach(o => {
            const stage = STAGE_OF_STATE[o.state] || 1;
            if (groups[stage]) {
                groups[stage].push(o);
            }
        });
        return groups;
    }

    /* Open the approval inbox item's source record via a real window action. */
    openActivity(act) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: act.res_model,
            res_id: act.res_id,
            views: [[false, "form"]],
        });
    }

    showToast(msg) {
        this.state.toastMessage = msg;
        this.state.toastVisible = true;
        clearTimeout(this._toastTimer);
        this._toastTimer = setTimeout(() => {
            this.state.toastVisible = false;
        }, 3200);
    }
}

// Register P03Workspace for all relevant action paths
registry.category("actions").add("p03_workspace", P03Workspace, { force: true });
registry.category("actions").add("cd_p03_portal.workspace", P03Workspace, { force: true });
