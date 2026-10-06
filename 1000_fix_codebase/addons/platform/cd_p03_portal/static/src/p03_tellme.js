/** @odoo-module **/

/* Tell-ME Global Search (archetype A13) — PP2-M05.
 *
 * The prototype's dual-language command palette: opens with Ctrl+K or
 * Alt+Q, searches the frozen registry (modules, screens, reports, forms)
 * in EN and বাংলা via /p03/tellme, and navigates with ↑/↓/Enter.
 * Keyboard-first per the prototype's defect-#10 lesson.
 */
import { registry } from "@core/registry";
import { useService } from "@core/utils";
import { Component, onMounted, onWillUnmount, useState } from "@odoo/owl";

export class TellMeSearch extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.action = useService("action");
        this.state = useState({
            query: "",
            results: [],
            activeIndex: 0,
            isOpen: false,
        });
        this._boundKeydown = this._onKeydown.bind(this);
        onMounted(() => document.addEventListener("keydown", this._boundKeydown));
        onWillUnmount(() => document.removeEventListener("keydown", this._boundKeydown));
    }

    _onKeydown(ev) {
        // Ctrl+K or Alt+Q opens the palette
        if ((ev.ctrlKey && ev.key === "k") || (ev.altKey && ev.key === "q")) {
            ev.preventDefault();
            this.state.isOpen = !this.state.isOpen;
            this.state.query = "";
            this.state.results = [];
            this.state.activeIndex = 0;
        }
        if (!this.state.isOpen) return;
        if (ev.key === "Escape") {
            ev.preventDefault();
            this.state.isOpen = false;
        } else if (ev.key === "ArrowDown") {
            ev.preventDefault();
            this.state.activeIndex = Math.min(
                this.state.activeIndex + 1, this.state.results.length - 1);
        } else if (ev.key === "ArrowUp") {
            ev.preventDefault();
            this.state.activeIndex = Math.max(this.state.activeIndex - 1, 0);
        } else if (ev.key === "Enter" && this.state.results.length > 0) {
            ev.preventDefault();
            this._open(this.state.results[this.state.activeIndex]);
        }
    }

    async onInput(ev) {
        this.state.query = ev.target.value;
        this.state.activeIndex = 0;
        if (this.state.query.length < 2) {
            this.state.results = [];
            return;
        }
        const data = await this.rpc("/p03/tellme", {
            query: this.state.query, limit: 20,
        });
        this.state.results = data.results || [];
    }

    _open(result) {
        this.state.isOpen = false;
        if (result.kind === "module") {
            // Open the workspace scoped to this module
            this.action.doAction({
                type: "ir.actions.client",
                tag: "p03_workspace",
                params: { module_id: result.id },
            });
        }
        // screens and reports navigate to their module's workspace;
        // dedicated actions land per-phase and dispatch here.
    }

    get kindLabels() {
        return { module: "Module", screen: "Screen", report: "Report", form: "Form" };
    }
}

TellMeSearch.template = "cd_p03_portal.TellMeSearch";

// Register as a systray item so the palette is always available
registry.category("systray").add("p03_tellme", {
    Component: TellMeSearch,
}, { sequence: 5, force: true });
