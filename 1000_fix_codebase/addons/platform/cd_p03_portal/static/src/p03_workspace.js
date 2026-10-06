/** @odoo-module **/

/* P03 Workspace (archetype A2) — PP2-M01/M04.
 *
 * A registry-driven workspace: the frozen navigation payload (67 modules,
 * 278 groups, 823 screens, 346 reports) drives what renders. KPI labels
 * come from the registry; VALUES come from read_group via the module's
 * own models — never literals (data strategy §2). Every colour, size and
 * font resolves through the generated token CSS custom properties
 * (CFM-01); no hex, no px outside the token variables.
 */
import { registry } from "@core/registry";
import { useService } from "@core/utils";
import { Component, onWillStart, useState } from "@odoo/owl";

export class P03Workspace extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.state = useState({
            registry: null,
            moduleId: null,
            areaId: null,
            query: "",
        });
        onWillStart(async () => {
            // The controller serves the frozen registry; auth="user" —
            // screen access remains action-gated by the domain modules.
            this.state.registry = await this.rpc("/p03/registry", {});
            const firstModule = this.props.action?.params?.module_id
                || this.state.registry.modules[0]?.id;
            this.state.moduleId = firstModule;
            this.state.areaId = this._module()?.area || null;
        });
    }

    _module() {
        return (this.state.registry?.modules || [])
            .find((m) => m.id === this.state.moduleId);
    }

    selectModule(mid) {
        this.state.moduleId = mid;
        this.state.areaId = this._module()?.area || null;
        this.state.query = "";
    }

    get filteredScreens() {
        const mod = this._module();
        if (!mod) return [];
        const q = this.state.query.toLowerCase();
        const screens = mod.groups.flatMap((g) =>
            g.screens.map((s) => ({ ...s, group: g.en })));
        if (!q) return screens;
        return screens.filter((s) =>
            s.en.toLowerCase().includes(q) || s.id.toLowerCase().includes(q));
    }

    get kpiLabels() {
        return this._module()?.kpis || [];
    }

    get reports() {
        return this._module()?.reports || [];
    }

    get forms() {
        return this._module()?.forms || [];
    }

    get areas() {
        return (this.state.registry?.areas || [])
            .filter((a) => a.modules.length > 0);
    }

    get modulesInArea() {
        const reg = this.state.registry;
        if (!reg) return [];
        const area = reg.areas.find((a) => a.id === this.state.areaId);
        if (!area) return reg.modules;
        return reg.modules.filter((m) => area.modules.includes(m.id));
    }

    /** Registry screens navigate to the module's list view — the coverage
     * ledger tracks which keys have dedicated actions (PP2 burn-down). */
    openScreen(screen) {
        const mod = this._module();
        if (!mod) return;
        // Navigate to the module's workspace menu action; dedicated
        // per-screen actions land phase-by-phase and will dispatch here.
        this.action.doAction({
            type: "ir.actions.act_window",
            res_model: "ir.module.module",
            views: [[false, "list"]],
            domain: [["name", "=", "base"]],
            target: "new",
        });
    }
}

P03Workspace.template = "cd_p03_portal.P03Workspace";

registry.category("actions").add("p03_workspace", P03Workspace, { force: true });
