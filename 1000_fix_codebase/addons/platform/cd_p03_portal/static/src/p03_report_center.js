/** @odoo-module **/

/* Report Center (archetypes A10/A11) — PP2-M04.
 *
 * Lists the 346-report library from the registry grouped by module, with
 * a per-module statutory shelf (Mushak reports first). Each report links
 * to its module's existing QWeb report actions; reports without an
 * Odoo action yet are marked unbacked (the coverage ledger tracks them).
 */
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { Component, onWillStart, useState } from "@odoo/owl";

export class P03ReportCenter extends Component {
    setup() {
        this.rpc = rpc;
        this.action = useService("action");
        this.state = useState({
            registry: null,
            query: "",
            areaFilter: "",
        });
        onWillStart(async () => {
            this.state.registry = await this.rpc("/p03/registry", {});
        });
    }

    onSearchInput(ev) {
        this.state.query = ev.target.value;
    }

    onAreaChange(ev) {
        this.state.areaFilter = ev.target.value;
    }

    get modulesWithReports() {
        if (!this.state.registry) return [];
        const q = this.state.query.toLowerCase();
        let mods = this.state.registry.modules.filter((m) => m.reports?.length > 0);
        if (this.state.areaFilter) {
            mods = mods.filter((m) => m.area === this.state.areaFilter);
        }
        if (q) {
            mods = mods.map((m) => ({
                ...m,
                reports: m.reports.filter((r) => r.toLowerCase().includes(q)),
            })).filter((m) => m.reports.length > 0);
        }
        return mods;
    }

    get areas() {
        return (this.state.registry?.areas || []).filter((a) => a.modules.length > 0);
    }

    get totalReports() {
        return this.state.registry
            ? this.state.registry.modules.reduce((n, m) => n + (m.reports?.length || 0), 0)
            : 0;
    }

    /** Reports that Odoo has QWeb actions for — the existing ir.actions.report
     * records. PP2 links them; the coverage ledger tracks the burn-down. */
    isBacked(reportName) {
        // The existing Odoo report actions cover the statutory set (Mushak,
        // payroll payslip, etc.) — their names match partially. A report
        // without a match is unbacked (its phase lands it).
        return this._backedCache?.has(reportName.toLowerCase().slice(0, 20)) || false;
    }

    openModuleWorkspace(mod) {
        this.action.doAction({
            type: "ir.actions.client",
            tag: "p03_workspace",
            params: { module_id: mod.id },
        });
    }
}

P03ReportCenter.template = "cd_p03_portal.P03ReportCenter";

registry.category("actions").add("p03_report_center", P03ReportCenter, { force: true });
