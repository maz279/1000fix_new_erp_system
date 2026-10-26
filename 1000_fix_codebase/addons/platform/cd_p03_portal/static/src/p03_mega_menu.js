/** @odoo-module **/

/* Dynamics-365 Multi-Column Mega Menu (PP2-M06)
 *
 * Injected into Odoo's systray navigation bar. Provides direct multi-column
 * access to all 11 business areas (A02–A12), 67 modules, 278 groups, and 823
 * screens without dead ends.
 */
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { Component, onWillStart, useState } from "@odoo/owl";

export class P03MegaMenu extends Component {
    setup() {
        this.rpc = rpc;
        this.action = useService("action");
        this.state = useState({
            isOpen: false,
            activeArea: "A01",
            registry: null,
        });

        onWillStart(async () => {
            try {
                this.state.registry = await this.rpc("/p03/registry", {});
                const firstArea = this.areas[0]?.id || "A01";
                this.state.activeArea = firstArea;
            } catch (e) {
                console.warn("Failed to load /p03/registry for mega menu", e);
            }
        });
    }

    toggle() {
        this.state.isOpen = !this.state.isOpen;
    }

    close() {
        this.state.isOpen = false;
    }

    selectArea(areaId) {
        this.state.activeArea = areaId;
    }

    get areas() {
        return (this.state.registry?.areas || []).filter(
            (a) => a.modules && a.modules.length > 0
        );
    }

    get activeAreaObj() {
        return this.areas.find((a) => a.id === this.state.activeArea) || this.areas[0];
    }

    get modulesInActiveArea() {
        const reg = this.state.registry;
        if (!reg) return [];
        const area = this.activeAreaObj;
        if (!area) return [];
        return (reg.modules || []).filter((m) => (area.modules || []).includes(m.id));
    }

    /* Counts are computed from the served registry so the rendered copy can
     * never drift from the data (module/screen totals are exactly what
     * /p03/registry carries). */
    get moduleCount() {
        return (this.state.registry?.modules || []).length;
    }

    get screenCount() {
        return (this.state.registry?.modules || []).reduce(
            (n, m) => n + (m.groups || []).reduce((k, g) => k + (g.screens || []).length, 0),
            0
        );
    }

    openWorkspace(modId) {
        this.close();
        this.action.doAction({
            type: "ir.actions.client",
            tag: "p03_workspace",
            params: { module_id: modId },
        });
    }

    /** Open a specific workspace screen (in-shell data screen) — the deep
     * link lands on module_id + screen_id after the workspace mounts. */
    _openWorkspaceScreen(screenId, modId) {
        this.close();
        this.action.doAction({
            type: "ir.actions.client",
            tag: "p03_workspace",
            params: { module_id: modId, screen_id: screenId },
        });
    }

    openScreen(screen, mod) {
        this.close();
        const sId = (screen?.id || "").toLowerCase();
        const mId = (mod?.id || "").toUpperCase();

        // M03 logistics: registry ids deep-link into the workspace screens.
        if (mId === "M03") {
            const screenMap = {
                "m03-cons": "M03-cons",
                "m03-record": "M03-record",
                "m03-journeys": "M03-journeys",
                "m03-manifest": "M03-manifest",
                "m03-custody": "M03-custody",
                "m03-pod": "M03-pod",
                "m03-seals": "M03-seals",
                "m03-riders": "M03-riders",
                "m03-routes": "M03-routes",
                "m03-app": "M03-app",
                "m03-couriers": "M03-couriers",
                "m03-bookings": "M03-bookings",
                "m03-recon": "M03-recon",
                "m03-exc": "M03-exc",
                "m03-charges": "M03-charges",
                "m03-cod": "M03-cod",
            };
            this._openWorkspaceScreen(screenMap[sId] || "M03-cons", mId);
            return;
        }

        // M31 workshop: registry ids deep-link into the workspace screens.
        // Without this the "orders" substring rule hijacked m31-orders to
        // the M01 service-order backend list — wrong module, left the shell.
        if (mId === "M31") {
            const screenMap = {
                "m31-orders": "M31-orders",
                "m31-record": "M31-record",
                "m31-transfer": "M31-transfer",
                "m31-benches": "M31-benches",
                "m31-benchmaster": "M31-benchmaster",
                "m31-levels": "M31-levels",
                "m31-diag": "M31-diag",
                "m31-parts": "M31-parts",
                "m31-testing": "M31-testing",
                "m31-costing": "M31-costing",
                "m31-throughput": "M31-throughput",
                "m31-methods": "M31-methods",
            };
            this._openWorkspaceScreen(screenMap[sId] || "M31-orders", mId);
            return;
        }

        if (mId === "M01" || sId.includes("order") || sId.includes("ticket")) {
            const isNew = sId.includes("create") || sId.includes("intake") || sId.includes("new");
            this.action.doAction("cd_service_order.action_fix_service_order", {
                clearBreadcrumbs: true,
                viewType: isNew ? "form" : "list",
            });
            return;
        }

        // M02 field service: every screen opens INSIDE the workspace (the
        // dispatch board carries the suggestion engine); the old fallback
        // opened the Device Registry — wrong area, wrong module.
        if (mId === "M02") {
            const dispatchScreens = {
                "m02-dispatch": "M02-dispatch",
                "m02-map": "M02-map",
                "m02-unassigned": "M02-unassigned",
                "m02-sla-risk": "M02-sla-risk",
                "m02-wo": "M02-wo",
                "m02-record": "M02-record",
                "m02-exceptions": "M02-exceptions",
                "m02-crews": "M02-crews",
                "m02-zones": "M02-zones",
                "m02-routes": "M02-routes",
                "m02-territory": "M02-territory",
                // registry-only technician-app / safety screens land on the board
            };
            this._openWorkspaceScreen(dispatchScreens[sId] || "M02-dispatch", mId);
            return;
        }

        if (sId.includes("device") || sId.includes("asset")) {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: screen.en || "Device Registry",
                res_model: "fix.device",
                views: [[false, "list"], [false, "form"]],
                target: "current",
            });
            return;
        }

        if (mId === "M04" || sId.includes("branch") || sId.includes("desk")) {
            this.action.doAction({
                type: "ir.actions.act_window",
                name: screen.en || "Branches & Service Centers",
                res_model: "fix.branch",
                views: [[false, "list"], [false, "form"]],
                target: "current",
            });
            return;
        }

        // Open module workspace by default
        this.openWorkspace(mod.id);
    }

    getGlyph(type) {
        switch (type) {
            case "W": return "▦";
            case "F": return "⛁";
            case "G": return "▤";
            case "B": return "⌘";
            case "D": return "◫";
            case "R": return "◈";
            default: return "•";
        }
    }
}

P03MegaMenu.template = "cd_p03_portal.P03MegaMenu";

registry.category("systray").add("p03_mega_menu", {
    Component: P03MegaMenu,
}, { sequence: 1, force: true });
