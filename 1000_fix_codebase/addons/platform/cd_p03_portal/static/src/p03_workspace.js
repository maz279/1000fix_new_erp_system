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
import { Component, onWillStart, useState, markup } from "@odoo/owl";
import { P03_AREAS, P03_MODULES, P03_ROLES, generateGridData } from "./p03_modules_meta";

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
            this.showToast("Please select an active order to assign.");
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
            this.showToast("Dispatch assignment failed — see server log.");
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
            this.showToast("Notification failed — see server log.");
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
            this.showToast("QC advance failed — see server log.");
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
            this.showToast("QC rework update failed — see server log.");
        }
    }


    /* Template-safe formatting helpers (null → em dash, never a crash). */
    fmtBDT(v) { return fmtBDT(v); }
    fmtNum(v) { return fmtNum(v); }
    stateLabel(s) { return STATE_LABELS[s] || s || "—"; }
    serviceTypeLabel(s) { return SERVICE_TYPE_LABELS[s] || s || "—"; }
    get jobCardDate() {
        return new Date().toLocaleDateString("en-GB",
            { day: "2-digit", month: "short", year: "numeric" }).toUpperCase();
    }

    /* Module KPI labels (values land with each module's wiring phase). */
    get kpiLabels() {
        return (this.state.activeModule.kpis || []).map(k => k.l);
    }

    /* Resolve a cross-navigation term to a real module/screen — no dead
       hardcoded targets. */
    openCross(term) {
        const code = String(term).split(" ")[0];
        if (/^M\d{2}$/.test(code) && P03_MODULES[code]) return this.openModule(code);
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
        this.ensureTab(`mod-${mid}`, `${mid} · ${mod.en}`, mod.icon, "workspace", { mid });
        this.state.megaMenuOpen = false;
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
            forms: mod.captures
                ? mod.captures.filter(c => c.freg.includes(sub[0])).map(c => c.en)
                : mod.forms.slice(0, 3),
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
                    STATE_LABELS[o.state] || o.state || "—",
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
            captureLabel: ((hit.m.captures || []).find(c => c.screens.includes(hit.sc.id)) || {}).en || null,
            gridData: grid
        };
        this.state.filteredGridRows = [...grid.rows];
        this.state.viewMode = hit.sc.t === "f" ? "form" : hit.sc.t === "d" || hit.sc.t === "c" ? "console" : "screen";
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
            this.showToast("Failed to load the order from the backend.");
        }
    }

    /* --- Data capture routing (module-aware) ---------------------------
       A module that declares a `captures` map (P03_MODULES[mid].captures)
       opens the REAL Odoo form each label captures into. A module without
       one keeps the service-order intake modal until its phase maps it. */
    findCapture(label, mid) {
        const mod = P03_MODULES[mid || this.state.activeModuleId];
        return ((mod && mod.captures) || []).find(c => c.en === label) || null;
    }

    get headerCaptureLabel() {
        const caps = this.state.activeModule && this.state.activeModule.captures;
        return caps && caps.length ? `+ New ${caps[0].en}` : "+ New Service Order";
    }

    get fregCaptureLabel() {
        const f = this.state.activeFreg;
        return f && f.module.captures && f.forms.length ? `+ New ${f.forms[0]}` : "+ New Entry";
    }

    get screenCaptureLabel() {
        const sc = this.state.activeScreen;
        return sc && sc.captureLabel ? `+ New ${sc.captureLabel}` : "+ New Record";
    }

    async openCapture(label, mid) {
        const cap = this.findCapture(label, mid);
        if (!cap) {
            this.openNewForm();
            return;
        }
        try {
            await this.actionService.doAction({
                type: "ir.actions.act_window",
                name: cap.en,
                res_model: cap.model,
                views: [[false, "form"]],
                target: "new",
            });
        } catch (e) {
            console.error(`Capture '${cap.en}' failed to open`, e);
            this.showToast(`'${cap.en}' could not open — is its module installed?`);
        }
    }

    openHeaderCapture() {
        const caps = this.state.activeModule && this.state.activeModule.captures;
        if (caps && caps.length) return this.openCapture(caps[0].en);
        this.openNewForm();
    }

    openFregCapture() {
        const f = this.state.activeFreg;
        if (f && f.module.captures && f.forms.length) return this.openCapture(f.forms[0], f.mid);
        this.openNewForm();
    }

    openScreenCapture() {
        const sc = this.state.activeScreen;
        if (sc && sc.captureLabel) return this.openCapture(sc.captureLabel, sc.mid);
        this.openNewForm();
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
            this.showToast("Stage transition failed — see server log.");
        }
    }

    holdStage() {
        if (!this.state.activeRecord) return;
        this.showToast("Hold requires a reason dialog — lands with the SLA-hold phase (state stays unchanged).");
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
            this.showToast("Customer name, phone, serial and fault description are required.");
            this.state.modalStep = 1;
            return;
        }
        this.showToast("Submitting Service Order to backend…");
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
            this.showToast("Submission failed — the order was NOT created.");
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
        this.state.lang = this.state.lang === "en" ? "bn" : "en";
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
            this.showToast("Open a service order first — the Job Card prints the live record.");
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
            this.showToast("Open a service order first.");
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
            this.showToast("Enter the technician to assign (matched against HR records).");
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
            this.showToast("Dispatch failed — see server log.");
        }
    }

    // --- Inventory Reservation Modal ---
    openInventoryModal() {
        if (!this.state.activeRecord) {
            this.showToast("Open a service order first.");
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
            this.showToast("Enter the part SKU (matched against the product catalogue).");
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
            this.showToast("Reservation failed — see server log.");
        }
    }

    // --- Dynamics-365 Tell Me Command Palette ---
    openTellMe() {
        this.state.tellMeOpen = true;
    }

    closeTellMe() {
        this.state.tellMeOpen = false;
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
                    if (s.en.toLowerCase().includes(q) || s.id.toLowerCase().includes(q)) {
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
            this.showToast("No rows in the active grid — nothing to export.");
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
