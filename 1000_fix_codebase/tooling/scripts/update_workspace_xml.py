import os

workspace_xml = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "addons",
    "platform",
    "cd_p03_portal",
    "static",
    "src",
    "p03_workspace.xml",
)
workspace_xml = os.path.abspath(workspace_xml)

with open(workspace_xml, encoding="utf-8") as f:
    content = f.read()

target = """                        <!-- ============ GENERIC MODEL LIST (A08 completion) ============ -->
                        <div t-if="!state.gl.loading &amp;&amp; state.gl.kind === 'model_list' &amp;&amp; state.gl.data" class="gl-layout">
                            <div class="gl-main fx-card">
                                <div t-if="state.gl.data.error" style="padding: 40px; text-align: center; color: var(--ink-300);"><t t-esc="state.gl.data.error"/></div>
                                <div t-if="!state.gl.data.error">
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; gap: 10px; flex-wrap: wrap;">
                                        <h3><t t-if="state.gl.data.total &amp;&amp; state.gl.data.total > state.gl.data.count"><t t-esc="state.gl.data.count"/> <t t-esc='t("of")'/> <t t-esc="state.gl.data.total"/> </t><t t-esc='t(state.gl.data.count === 1 ? "record · live from Odoo" : "records · live from Odoo")'/></h3>
                                        <div style="display: flex; gap: 6px; flex-wrap: wrap;" t-if="mlStates.length">
                                            <button class="btn btn-sm" t-att-class="{'btn-primary': state.gl.mlState === '__all'}" t-on-click="() => this.mlSetState('__all')"><t t-esc='t("All")'/></button>
                                            <t t-foreach="mlStates" t-as="st" t-key="st.key">
                                                <button class="btn btn-sm" t-att-class="{'btn-primary': state.gl.mlState === st.key}" t-on-click="() => this.mlSetState(st.key)"><t t-esc="st.label"/></button>
                                            </t>
                                        </div>
                                    </div>
                                    <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px;">
                                        <button t-if="state.gl.modelCfg.create !== false" class="btn btn-sm" t-on-click="() => this.mlNew()"><t t-esc='t("+ New")'/></button>
                                        <t t-foreach="state.gl.modelCfg.actions || []" t-as="act" t-key="act.m">
                                            <button class="btn btn-primary btn-sm" t-on-click="() => this.mlAction(act.m, act.l)"><t t-esc="t(act.l)"/></button>
                                        </t>
                                    </div>
                                    <div class="tbl-wrap">
                                        <table class="fx-table">
                                            <thead>
                                                <tr>
                                                    <t t-foreach="state.gl.modelCfg.cols" t-as="col" t-key="col">
                                                        <th><t t-esc="state.gl.data.labels[col] || col"/></th>
                                                    </t>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr t-foreach="mlRows" t-as="row" t-key="row.id" style="cursor: pointer;"
                                                    t-on-click="() => this.mlSelect(row)"
                                                    t-att-class="{'alt': row_index % 2, 'gl-row-selected': state.gl.mlSelected === row}">
                                                    <t t-foreach="state.gl.modelCfg.cols" t-as="col" t-key="col">
                                                        <td>
                                                            <span t-if="mlIsState(row, col)" class="chip"><t t-esc="mlCell(row, col)"/></span>
                                                            <span t-else=""><t t-esc="mlCell(row, col)"/></span>
                                                        </td>
                                                    </t>
                                                </tr>
                                                <tr t-if="!mlRows.length"><td t-att-colspan="state.gl.modelCfg.cols.length" style="text-align: center; color: var(--ink-300);"><t t-esc='state.gl.modelCfg.create !== false ? t("No records yet — use + New to create the first one.") : t("No records yet.")'/></td></tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                            <aside class="gl-factbox">
                                <h4><t t-esc='t("How this screen works")'/></h4>
                                <div class="fb-sec"><p style="font-size: 12px;"><t t-esc='t("Rows are live records straight from the Odoo model. Action buttons call the same server-side workflow methods the back-office forms use — rules and states are enforced there, not here.")'/></p></div>
                            </aside>
                        </div>"""

replacement = """                        <!-- ============ GENERIC MODEL LIST (D365 Grid Standard) ============ -->
                        <div t-if="!state.gl.loading &amp;&amp; state.gl.kind === 'model_list' &amp;&amp; state.gl.data" class="gl-layout">
                            <div class="gl-main fx-card">
                                <div t-if="state.gl.data.error" style="padding: 40px; text-align: center; color: var(--ink-300);"><t t-esc="state.gl.data.error"/></div>
                                <div t-if="!state.gl.data.error">
                                    <!-- Dynamics 365 Command Bar -->
                                    <div class="d365-cmdbar" style="display: flex; gap: 8px; align-items: center; padding: 6px 10px; background: var(--surface-100, #f8fafc); border-radius: 6px; margin-bottom: 12px; border: 1px solid var(--border-color, #e2e8f0); flex-wrap: wrap;">
                                        <button t-if="state.gl.modelCfg.create !== false" class="btn btn-primary btn-sm" t-on-click="() => this.mlNew()" title="Create new record">
                                            <span style="margin-right: 4px; font-weight: 700;">+</span> <t t-esc='t("New")'/>
                                        </button>
                                        <t t-foreach="state.gl.modelCfg.actions || []" t-as="act" t-key="act.m">
                                            <button class="btn btn-sm" t-on-click="() => this.mlAction(act.m, act.l)"><t t-esc="t(act.l)"/></button>
                                        </t>
                                        <button class="btn btn-sm" t-on-click="() => this.mlExportCsv()" title="Export current rows to CSV">
                                            <span style="margin-right: 4px;">⤓</span> <t t-esc='t("Export CSV")'/>
                                        </button>
                                        <button class="btn btn-sm" t-on-click="() => this.mlRefresh()" title="Refresh records from Odoo">
                                            <span style="margin-right: 4px;">↻</span> <t t-esc='t("Refresh")'/>
                                        </button>

                                        <!-- D365 Real-Time Quick Find Search Box -->
                                        <div style="margin-left: auto; display: flex; align-items: center; gap: 6px; background: #fff; border: 1px solid var(--border-color, #cbd5e1); border-radius: 4px; padding: 2px 8px;">
                                            <span style="color: var(--ink-400); font-size: 13px;">🔍</span>
                                            <input type="text"
                                                   style="border: none; outline: none; background: transparent; font-size: 12px; padding: 3px 0; min-width: 170px; color: var(--ink-900);"
                                                   placeholder="Quick find..."
                                                   t-att-value="state.gl.mlSearch"
                                                   t-on-input="(ev) => this.mlOnSearchInput(ev)"/>
                                            <button t-if="state.gl.mlSearch"
                                                    style="border: none; background: transparent; padding: 0 2px; color: var(--ink-400); cursor: pointer; font-size: 11px;"
                                                    t-on-click="() => this.mlClearSearch()"
                                                    title="Clear search">✕</button>
                                        </div>
                                    </div>

                                    <!-- Status / Filter Pills & Record Counter -->
                                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; gap: 10px; flex-wrap: wrap;">
                                        <div style="font-size: 13px; font-weight: 500; color: var(--ink-700);">
                                            <span t-esc="mlRows.length"/> <t t-esc='t(mlRows.length === 1 ? "record" : "records")'/>
                                            <t t-if="state.gl.data.total &amp;&amp; state.gl.data.total > mlRows.length">
                                                (of <span t-esc="state.gl.data.total"/> total)
                                            </t>
                                            <span style="color: var(--ink-400); font-size: 12px; margin-left: 4px;">· live from Odoo</span>
                                            <span t-if="state.gl.mlSearch" class="chip" style="margin-left: 6px; font-size: 11px; padding: 2px 6px;">Filtered</span>
                                        </div>
                                        <div style="display: flex; gap: 6px; flex-wrap: wrap;" t-if="mlStates.length">
                                            <button class="btn btn-sm" t-att-class="{'btn-primary': state.gl.mlState === '__all'}" t-on-click="() => this.mlSetState('__all')"><t t-esc='t("All")'/></button>
                                            <t t-foreach="mlStates" t-as="st" t-key="st.key">
                                                <button class="btn btn-sm" t-att-class="{'btn-primary': state.gl.mlState === st.key}" t-on-click="() => this.mlSetState(st.key)"><t t-esc="st.label"/></button>
                                            </t>
                                        </div>
                                    </div>

                                    <!-- D365 Interactive Table with Clickable Sort Headers -->
                                    <div class="tbl-wrap">
                                        <table class="fx-table">
                                            <thead>
                                                <tr>
                                                    <t t-foreach="state.gl.modelCfg.cols" t-as="col" t-key="col">
                                                        <th style="cursor: pointer; user-select: none;"
                                                            t-on-click="() => this.mlToggleSort(col)"
                                                            t-att-title="'Sort by ' + (state.gl.data.labels[col] || col)">
                                                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 6px;">
                                                                <span><t t-esc="state.gl.data.labels[col] || col"/></span>
                                                                <span style="font-size: 10px; color: var(--ink-400);">
                                                                    <t t-if="state.gl.mlSortCol === col">
                                                                        <t t-if="state.gl.mlSortAsc">▲</t>
                                                                        <t t-else="">▼</t>
                                                                    </t>
                                                                    <t t-else="">⇅</t>
                                                                </span>
                                                            </div>
                                                        </th>
                                                    </t>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr t-foreach="mlRows" t-as="row" t-key="row.id" style="cursor: pointer;"
                                                    t-on-click="() => this.mlSelect(row)"
                                                    t-att-class="{'alt': row_index % 2, 'gl-row-selected': state.gl.mlSelected === row}">
                                                    <t t-foreach="state.gl.modelCfg.cols" t-as="col" t-key="col">
                                                        <td>
                                                            <span t-if="mlIsState(row, col)" class="chip"><t t-esc="mlCell(row, col)"/></span>
                                                            <span t-else=""><t t-esc="mlCell(row, col)"/></span>
                                                        </td>
                                                    </t>
                                                </tr>
                                                <tr t-if="!mlRows.length"><td t-att-colspan="state.gl.modelCfg.cols.length" style="text-align: center; color: var(--ink-300); padding: 24px;"><t t-esc='state.gl.mlSearch ? t("No matching records found for search.") : (state.gl.modelCfg.create !== false ? t("No records yet — use + New to create the first one.") : t("No records yet."))'/></td></tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                            <!-- D365 FactBox Aside -->
                            <aside class="gl-factbox">
                                <t t-if="state.gl.mlSelected">
                                    <h4><t t-esc='t("Record Summary")'/></h4>
                                    <div class="fb-sec">
                                        <div style="font-size: 14px; font-weight: 600; color: var(--ink-900); margin-bottom: 4px;">
                                            <t t-esc="state.gl.mlSelected.name || state.gl.mlSelected.reference || state.gl.mlSelected.reference_no || ('#' + state.gl.mlSelected.id)"/>
                                        </div>
                                        <div style="font-size: 11px; color: var(--ink-500); margin-bottom: 8px;">
                                            ID #<t t-esc="state.gl.mlSelected.id"/> · <t t-esc="state.gl.modelCfg.model"/>
                                        </div>
                                        <div t-if="state.gl.mlSelected.state" style="margin-bottom: 10px;">
                                            <span class="chip"><t t-esc="state.gl.mlSelected.state"/></span>
                                        </div>
                                        <button class="btn btn-sm btn-primary" style="width: 100%; margin-top: 8px;" t-on-click="() => this.mlOpenForm(state.gl.mlSelected.id)">
                                            <t t-esc='t("Open Full Form")'/>
                                        </button>
                                    </div>
                                    <div class="fb-sec" t-if="state.gl.modelCfg.actions &amp;&amp; state.gl.modelCfg.actions.length">
                                        <h5><t t-esc='t("Actions")'/></h5>
                                        <div style="display: flex; flex-direction: column; gap: 4px; margin-top: 6px;">
                                            <t t-foreach="state.gl.modelCfg.actions" t-as="act" t-key="act.m">
                                                <button class="btn btn-sm" t-on-click="() => this.mlAction(act.m, act.l)"><t t-esc="t(act.l)"/></button>
                                            </t>
                                        </div>
                                    </div>
                                </t>
                                <t t-else="">
                                    <h4><t t-esc='t("Screen Overview")'/></h4>
                                    <div class="fb-sec"><p style="font-size: 12px;"><t t-esc='t("Live records from Odoo. Click any column header to sort ascending or descending. Use Quick Find for real-time search, or filter by state pills.")'/></p></div>
                                    <div class="fb-sec"><p style="font-size: 11px; color: var(--ink-500);"><t t-esc='t("Click any row to open the D365 in-workspace form or inspect FactBox details.")'/></p></div>
                                </t>
                            </aside>
                        </div>"""

norm_content = content.replace("\r\n", "\n")
norm_target = target.replace("\r\n", "\n")
norm_replacement = replacement.replace("\r\n", "\n")

if norm_target in norm_content:
    norm_content = norm_content.replace(norm_target, norm_replacement, 1)
    with open(workspace_xml, "w", encoding="utf-8") as f:
        f.write(norm_content)
    print("p03_workspace.xml updated successfully with D365 Grid standard!")
else:
    print("Target not found in XML")
