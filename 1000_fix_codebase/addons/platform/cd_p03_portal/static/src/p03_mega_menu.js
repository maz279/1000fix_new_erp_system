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

    openWorkspace(modId) {
        this.close();
        this.action.doAction({
            type: "ir.actions.client",
            tag: "p03_workspace",
            params: { module_id: modId },
        });
    }

    openScreen(screen, mod) {
        this.close();
        const sId = (screen?.id || "").toLowerCase();
        const mId = (mod?.id || "").toUpperCase();

        if (mId === "M01" || sId.includes("order") || sId.includes("ticket")) {
            const isNew = sId.includes("create") || sId.includes("intake") || sId.includes("new");
            this.action.doAction("cd_service_order.action_fix_service_order", {
                clearBreadcrumbs: true,
                viewType: isNew ? "form" : "list",
            });
            return;
        }

        if (mId === "M02" || sId.includes("device") || sId.includes("asset")) {
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
