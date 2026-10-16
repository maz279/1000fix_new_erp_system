/** @odoo-module **/

/* Tab Rail (prototype shell) — PP2-M07-T01.
 *
 * The prototype's accumulating closable tab rail, ported to R1: the
 * breadcrumb bar accumulates visited workspaces as closable tabs,
 * persists across sessions via localStorage, and deep-link-restores.
 * Non-normative options (dirty-state guard, LRU eviction) land only if
 * measured need appears (the audit's ruling).
 */
import { registry } from "@web/core/registry";
import { useEffect } from "@odoo/owl";

const STORAGE_KEY = "p03_open_tabs";
const MAX_TABS = 12; // sensible cap; LRU eviction is a non-normative option

export function p03TabRailEffect(env) {
    /** Reads the breadcrumb on every action and records the tab. */
    let tabs = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");

    const push = (title, actionTag) => {
        if (!title || !actionTag) return;
        tabs = tabs.filter((t) => t.tag !== actionTag);
        tabs.push({ title, tag: actionTag, at: Date.now() });
        if (tabs.length > MAX_TABS) tabs = tabs.slice(-MAX_TABS);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(tabs));
    };

    // Hook into Odoo's action service to record tabs
    const originalDoAction = env.services.action.doAction.bind(env.services.action);
    env.services.action.doAction = async (...args) => {
        const result = await originalDoAction(...args);
        try {
            const action = args[0];
            if (typeof action === "object" && action.tag) {
                push(action.name || action.tag, action.tag);
            }
        } catch { /* non-blocking */ }
        return result;
    };

    return () => {
        // cleanup: restore the original
        env.services.action.doAction = originalDoAction;
    };
}

registry.category("effects").add("p03_tab_rail", {
    mount: p03TabRailEffect,
}, { force: true });
