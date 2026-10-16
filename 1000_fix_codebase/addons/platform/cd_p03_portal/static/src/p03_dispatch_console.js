/** @odoo-module **/

/* Process Console: Dispatch Board (archetype A7) — PP2-M03.
 *
 * The dispatch console: live status pills, a zone-column board of open
 * work orders, and action rails. Values come from read_group on the
 * fix.work.order model — never literals (data strategy §2). The stepper
 * × checklist × gauge pattern lands with the console actions that mutate
 * real records.
 */
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class P03DispatchConsole extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            counts: null,   // per-state work-order counts
            zones: [],      // zone columns with recent orders
        });
        onWillStart(async () => {
            await this._load();
        });
    }

    async _load() {
        // read_group on the REAL model — the console is a view, not a data
        // source (AS-09). If fix.work.order has no rows, we render empty.
        try {
            const groups = await this.orm.silent.readGroup(
                "fix.work.order",
                [["state", "!=", "cancelled"]],
                ["state"], 0, "state asc", 50,
            );
            this.state.counts = {};
            for (const g of groups) {
                this.state.counts[g.state] = g.state_count;
            }
        } catch {
            this.state.counts = {};  // model not seeded — honest empty
        }
        try {
            const orders = await this.orm.silent.searchRead(
                "fix.work.order",
                [["state", "in", ["pending", "assigned", "in_progress"]]],
                ["name", "state", "order_id"], 10, "write_date desc",
            );
            this.state.zones = orders;
        } catch {
            this.state.zones = [];
        }
    }

    get totalCount() {
        return Object.values(this.state.counts || {}).reduce((a, b) => a + b, 0);
    }

    get stateLabels() {
        return {
            draft: "Draft", pending: "Pending", assigned: "Assigned",
            in_progress: "In Progress", completed: "Completed", failed: "Failed",
        };
    }

    refresh() {
        this._load();
    }
}

P03DispatchConsole.template = "cd_p03_portal.P03DispatchConsole";

registry.category("actions").add("p03_dispatch_console", P03DispatchConsole, { force: true });
