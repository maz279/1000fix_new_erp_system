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
import { Component, onWillStart, onWillUnmount, useState, markup } from "@odoo/owl";
import { P03_AREAS, P03_MODULES, P03_ROLES, generateGridData, P03_LIVE_SCREENS, P03_MODULE_CREATE, P03_FORM_MODELS, P03_DATA_SCREENS } from "./p03_modules_meta";
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
    walk_in: "Walk-in Counter", collection: "Collection / Drop-off",
    onsite: "On-site Visit", mail_in: "Mail-in", corporate: "Corporate B2B",
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
            recentOrders: []
        });

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
            if (data.s && typeof data.s === "string" && data.s.length <= 64) {
                this.openScreen(data.s);
            } else {
                this.openModule(mid);
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
        onWillUnmount(() => {
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
            return typeof v === "number" && !Number.isInteger(v) ? v.toLocaleString("en-BD", { maximumFractionDigits: 0 }) : String(v);
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
            this.openModelForm(create.model, create.label);
            return;
        }
        this.openNewForm();
    }

    /* Open a REAL Odoo form view for a model (finance data-entry forms). */
    openModelForm(resModel, label) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: label || "New Record",
            res_model: resModel,
            views: [[false, "form"]],
            target: "current",
        });
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
            if (/receipt/i.test(formLabel)) {
                this.openScreen("M20-receipts");
                return;
            }
            if (/payment link/i.test(formLabel)) {
                this.openScreen("M20-links");
                return;
            }
            if (/credit note|refund/i.test(formLabel)) {
                this.openScreen("M20-refunds");
                return;
            }
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
            this.openModelForm(create.model, create.label);
            return;
        }
        this.openNewForm();
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
            prompt: null,            // generic reason prompt {title,label,action,id,value}
            mlState: "__all",        // model_list state filter
            mlSelected: null,        // model_list selected row
        };
        this.state.viewMode = "gl";
        this.ensureTab(`gl-${screenId}`, `${hit && hit.sc.t === "f" ? "▤" : "⛁"} ${this.state.gl.title}`, "⛁", "gl", { screenId });
        this.loadGlData();
    }

    /* Bilingual GL screen titles — re-resolve on every language switch. */
    get glTitle() {
        const gl = this.state.gl;
        if (!gl) return "";
        return (gl.hitSc && this.tBilingual(gl.hitSc)) || gl.title || "";
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
                const res = await this.rpc("/p03/model/report", {
                    module: cfg.module, report: cfg.report, params,
                });
                gl.data = res.error ? { error: res.error } : res;
            } else if (gl.kind === "model_list") {
                const res = await this.rpc("/p03/model/records", {
                    model: gl.modelCfg.model,
                    cols: gl.modelCfg.cols,
                    domain: gl.modelCfg.domain || [],
                    state_field: gl.modelCfg.stateField || null,
                    state_filter: gl.mlState || "__all",
                });
                gl.data = res.error ? { error: res.error } : res;
            }
        } catch (e) {
            gl.error = "Could not reach the GL endpoint — try Refresh.";
            console.warn("GL screen load failed:", e);
        }
        gl.loading = false;
    }


    /* ---------------- generic model_list screens ---------------- */

    get mlRows() {
        const gl = this.state.gl;
        if (!gl || !gl.data || gl.data.error) return [];
        return gl.data.rows || [];
    }

    get mlStates() {
        const gl = this.state.gl;
        if (!gl || !gl.modelCfg || !gl.modelCfg.stateField) return [];
        const seen = new Map();
        for (const r of this.mlRows) {
            const v = r[gl.modelCfg.stateField];
            if (v && v.key != null && !seen.has(v.key)) seen.set(v.key, v.label);
        }
        return [...seen.entries()].map(([key, label]) => ({ key, label }));
    }

    mlSetState(key) {
        this.state.gl.mlState = key;
        this.loadGlData();
    }

    mlCell(row, field) {
        const v = row[field];
        if (v == null) return "—";
        if (typeof v === "object") {
            if (v.label != null) return v.label;          // selection
            if (v.name != null) return v.name;            // many2one
            return String(v);
        }
        if (typeof v === "boolean") return v ? "✓" : "—";
        if (typeof v === "number" && Math.abs(v) >= 1000) return fmtBDT(v);
        return String(v);
    }

    mlIsState(row, field) {
        const v = row[field];
        return !!(v && typeof v === "object" && v.key != null);
    }

    mlSelect(row) {
        this.state.gl.mlSelected = this.state.gl.mlSelected === row ? null : row;
    }

    /* The model's own Odoo form, in a dialog over the workspace: every field
     * rule, constraint and ACL of the backend applies; the list reloads on
     * close. */
    mlOpenForm(resId) {
        const gl = this.state.gl;
        this.actionService.doAction(
            {
                type: "ir.actions.act_window",
                name: (this.state.activeScreen && this.state.activeScreen.en) || "",
                res_model: gl.modelCfg.model,
                res_id: resId || false,
                views: [[false, "form"]],
                target: "new",
                context: gl.modelCfg.context || {},
            },
            { onClose: () => this.loadGlData() }
        );
    }

    mlNew() {
        this.mlOpenForm(false);
    }

    async mlAction(method, label) {
        const gl = this.state.gl;
        const row = gl.mlSelected;
        if (!row) { this.showToast("Select a row first"); return; }
        const res = await this._arCall("/p03/model/action", {
            model: gl.modelCfg.model, ids: [row.id], method,
        }, label ? label + " ✓" : "Done ✓");
        if (res.success) { this.loadGlData(); this.state.gl.mlSelected = null; }
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
        gl.jeDetail = { loading: true };
        try {
            const res = await this.rpc("/p03/gl/je", { move_id: moveId });
            gl.jeDetail = res.success ? res : { error: res.error };
        } catch (e) {
            gl.jeDetail = { error: "Could not load the entry" };
        }
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
        gl.arDetail = { loading: true };
        try {
            const res = await this.rpc("/p03/ar/invoice", { invoice_id: invoiceId });
            gl.arDetail = res.invoice ? res : { error: "Not found" };
        } catch (e) {
            gl.arDetail = { error: "Could not load the invoice" };
        }
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
        };
        const call = endpoints[p.action];
        if (!call) return;
        const res = await this._arCall(call[0], call[1], call[2]);
        if (res.success) {
            this.loadGlData();
            if (this.state.gl.arDetail) this.arOpenInvoice(this.state.gl.arDetail.invoice.id);
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

    openModule(mid) {
        const mod = P03_MODULES[mid] || P03_MODULES.M01;
        this.state.activeModuleId = mid;
        this.state.activeModule = mod;
        this.state.viewMode = "workspace";
        this.state.financeKpis = null;
        this.ensureTab(`mod-${mid}`, `${mid} · ${mod.en}`, mod.icon, "workspace", { mid });
        this.state.megaMenuOpen = false;
        // A08 modules fetch REAL KPI aggregates (metric keys on the kpis).
        if ((mod.kpis || []).some(k => k.m)) {
            this.rpc("/p03/finance/kpis", { module: mid })
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
        const grid = generateGridData(`FREG-${mid}-${fnIndex}`, sub[1], mod.en);

        const mappedScreens = [];
        mod.groups.forEach(g => {
            g.screens.forEach(s => mappedScreens.push({ ...s, groupEn: g.en }));
        });

        this.state.activeFreg = {
            mid,
            fnIndex,
            subModuleNo: sub[0],
            subModuleTitle: sub[1],
            functionCount: sub[2],
            module: mod,
            screens: mappedScreens.slice(0, 6),
            reports: mod.reports.slice(0, 4),
            forms: mod.forms.slice(0, 3),
            gridData: grid
        };
        this.state.viewMode = "freg";
        this.ensureTab(`freg-${mid}-${fnIndex}`, `⌘ ${sub[1]}`, "⌘", "freg", { mid, fnIndex });
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
            hit = { mid: this.state.activeModuleId, m: mod, g: mod.groups[0], sc: mod.groups[0].screens[0] };
        }

        // In-workspace D365 screens (M19 GL pilot): render INSIDE the shell
        // from live /p03/gl/* data — checked BEFORE the live-model dispatch
        // so these screens never leave the workspace for a stock Odoo view.
        const dataScreen = P03_DATA_SCREENS[screenId];
        if (dataScreen) {
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
        if (hit.m.area === "A08") {
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

    ensureTab(tabId, title, icon, mode, payload = {}) {
        const existing = this.state.openTabs.find(t => t.id === tabId);
        if (!existing) {
            this.state.openTabs.push({ id: tabId, title, icon, mode, payload });
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
            this.openScreen(tab.payload.screenId);
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
            this.showToast(t('Stage transition failed — see server log.'));
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
                    { id: "M03-counter", title: "Walk-in Counter Queue", icon: "🏢", group: "Branch Operations", fn: () => { this.closeTellMe(); this.openScreen("M03-counter"); } },
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
