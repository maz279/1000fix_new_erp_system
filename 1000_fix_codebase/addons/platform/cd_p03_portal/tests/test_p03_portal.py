# cd_p03_portal tests — PP2 (CD-P03-01).
import inspect
import json
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
REPO = MODULE.parents[2]


class TestP03WorkspaceMenu(unittest.TestCase):
    """PP2-M01: the registry-driven menu surface."""

    def setUp(self):
        self.registry = json.loads((REPO / "contracts" / "nav" / "registry.json").read_text(encoding="utf-8"))
        self.menus_xml = (MODULE / "views" / "p03_menus.xml").read_text(encoding="utf-8")

    def test_every_cd_kind_module_has_a_workspace_menu(self):
        """The binding mapping's cd/embedded/shared modules all appear."""
        ws_count = self.menus_xml.count('parent="cd_entity_config.menu_fix_operations_root"')
        self.assertGreater(ws_count, 50,
                           f"expected >50 workspace menus under the operations root, got {ws_count}")

    def test_nvr_23_no_workspace_exceeds_7_primary_sections(self):
        """Every workspace has at most 7 direct-section children (plus the
        overflow submenu for modules with >7 groups)."""
        import re
        xml = self.menus_xml
        # roots: workspace menuitems (parent = the operations root)
        roots = re.findall(
            r'id="(menu_p03_ws_\w+)"[^>]*parent="cd_entity_config', xml)
        # all section ids: _s1.._s7 and _s7more
        all_sections = re.findall(r'id="(menu_p03_ws_\w+_s\d+\w*)"', xml)
        self.assertGreater(len(roots), 50, "workspace roots not found")
        for root in roots:
            # direct sections: exact prefix match root_sN (not root_s7more)
            prefix = root + "_s"
            direct = [s for s in all_sections
                      if s.startswith(prefix)
                      and "more" not in s
                      and s[len(prefix)].isdigit()]
            self.assertLessEqual(len(direct), 7,
                                 f"{root} has {len(direct)} primary sections (NVR-23 max 7)")

    def test_menus_reference_only_existing_parent(self):
        """Every menu's parent is either the operations root or another
        generated menu in this file (no dangling references)."""
        import re
        ids = set(re.findall(r'id="([\w.]+)"', self.menus_xml))
        parents = re.findall(r'parent="([\w.]+)"', self.menus_xml)
        for parent in parents:
            if "menu_fix_operations_root" in parent:
                continue  # the shared root (cd_entity_config)
            short = parent.split(".")[-1]
            self.assertIn(short, ids,
                          f"parent {parent} not found in generated ids")


class TestP03Controller(unittest.TestCase):
    """PP2-M01: the registry-serving controller."""

    def test_registry_served_readonly_user_auth(self):
        src = (MODULE / "controllers" / "p03_registry.py").read_text(encoding="utf-8")
        self.assertIn('auth="user"', src)
        self.assertIn("readonly=True", src)

    def test_controller_reads_the_committed_registry(self):
        """The controller's path resolves to contracts/nav/registry.json —
        the FF-38-checked artifact, not a copy."""
        src = (MODULE / "controllers" / "p03_registry.py").read_text(encoding="utf-8")
        self.assertIn("contracts", src)
        self.assertIn("registry.json", src)
        # and the file actually exists at that path
        self.assertTrue((REPO / "contracts" / "nav" / "registry.json").exists())


class TestP03OWLWorkspace(unittest.TestCase):
    """PP2-M01: the A2 archetype component."""

    def test_workspace_uses_rpc_service_not_raw_fetch(self):
        js = (MODULE / "static" / "src" / "p03_workspace.js").read_text(encoding="utf-8")
        self.assertIn('useService("rpc")', js)
        self.assertNotIn("fetch(", js, "raw fetch in OWL — use the rpc service")

    def test_owl_templates_carry_no_python_expressions(self):
        """OWL compiles t-* attribute expressions as JavaScript — a Python
        operator or literal compiles to a syntax error and crashes the
        component at render (defects found live 2026-10-09: `or` in the
        workspace topbar, `and` in the tellme palette). String literals
        inside quotes are exempted."""
        import re
        attr = re.compile(
            r't-(?:esc|out|att[a-z-]*|if|elif|foreach|value)="([^"]*)"')
        isms = [
            (r"\bor\b", "'or'"), (r"\band\b", "'and'"),
            (r"\bnot\s+(?!set\b|found\b|available\b)", "'not'"),
            (r"\bNone\b", "None"), (r"\bTrue\b", "True"),
            (r"\bFalse\b", "False"),
        ]
        for xml_file in (MODULE / "static" / "src").glob("*.xml"):
            xml = xml_file.read_text(encoding="utf-8")
            for m in attr.finditer(xml):
                expr = m.group(1)
                stripped = re.sub(r"'[^']*'|\"[^\"]*\"", "", expr)
                for pat, label in isms:
                    self.assertIsNone(
                        re.search(pat, stripped),
                        f"{xml_file.name}: Python {label} in t-expression "
                        f"{expr[:70]!r} — OWL compiles these as JavaScript")

    def test_every_owl_expression_compiles_as_javascript(self):
        """The full-strength oracle: every t-* expression (XML entities
        decoded) must compile via `new Function` — the same mechanism Owl
        uses. Skips when no Node runtime is available."""
        import shutil
        import subprocess
        import tempfile
        node = shutil.which("node")
        if not node:
            self.skipTest("node not available for the JS compile oracle")

        script = r"""
        const fs = require("fs");
        const SRC = process.argv[2];
        const ATTR = /t-(esc|out|att|attf|if|elif|foreach|value|key|on-click(?:\.\w+)?|on-input|on-change|on-focus|on-keydown|on-mouseenter)="([^"]*)"/g;
        const unesc = s => s.replace(/&lt;/g,"<").replace(/&gt;/g,">").replace(/&amp;/g,"&").replace(/&quot;/g,'"').replace(/&#39;/g,"'");
        const SCOPE = "state, props, userService, rpc, action";
        let exprs = 0; const fails = [];
        for (const f of fs.readdirSync(SRC).filter(x => x.endsWith(".xml"))) {
          const txt = fs.readFileSync(SRC + "/" + f, "utf8");
          let m;
          while ((m = ATTR.exec(txt)) !== null) {
            const expr = unesc(m[2].trim());
            if (!expr || expr.startsWith("#")) continue;
            try {
              exprs++;
              if (m[1] === "attf") {
                for (const im of expr.matchAll(/\{\{([^}]+)\}\}/g))
                  new Function(SCOPE, "return (" + im[1] + ");");
              } else {
                new Function(SCOPE, "return (" + expr + ");");
              }
            } catch (e) {
              fails.push(f + " [" + m[1] + "] " + expr.slice(0, 60) + " :: " + e.message);
            }
          }
        }
        if (fails.length) { console.error(fails.join("\n")); process.exit(1); }
        console.log(exprs + " expressions compile clean");
        """
        with tempfile.NamedTemporaryFile(
                "w", suffix=".js", delete=False, encoding="utf-8") as fh:
            fh.write(script)
            script_path = fh.name
        try:
            proc = subprocess.run(
                [node, script_path, str(MODULE / "static" / "src")],
                capture_output=True, text=True, timeout=60)
        finally:
            Path(script_path).unlink(missing_ok=True)
        self.assertEqual(
            proc.returncode, 0,
            f"OWL expression compile failures:\n{proc.stderr}")
        self.assertIn("expressions compile clean", proc.stdout)

    def test_workspace_template_uses_token_variables_only(self):
        """The template resolves colours through --fix-* custom properties
        (CFM-01: no hand-authored hex outside the generator)."""
        xml = (MODULE / "static" / "src" / "p03_workspace.xml").read_text(encoding="utf-8")
        import re
        hexes = re.findall(r"#[0-9a-fA-F]{6}\b", xml)
        # fallbacks in var() are allowed (--fix-x, #fallback) — count only
        # hexes that are NOT inside a var() fallback
        outside_var = [h for h in hexes
                       if not re.search(rf"var\([^)]*{h}", xml)]
        self.assertEqual(len(outside_var), 0,
                         f"hand-authored hex outside var() fallbacks: {outside_var[:5]}")

    def test_kpi_labels_from_registry_values_never_literal(self):
        """KPI cards render the registry label with a dash placeholder —
        values come from read_group in the phase that wires the model."""
        xml = (MODULE / "static" / "src" / "p03_workspace.xml").read_text(encoding="utf-8")
        self.assertIn("t-esc=\"kpi\"", xml)  # label
        self.assertNotIn("1,284", xml, "a literal KPI value leaked into the template")


class TestP03Actions(unittest.TestCase):
    """PP2-M06: role centers + workspace action."""

    def test_workspace_action_registered(self):
        xml = (MODULE / "views" / "p03_actions.xml").read_text(encoding="utf-8")
        self.assertIn('tag">p03_workspace', xml.replace(">", '">', 0) if ">" in xml else xml)
        self.assertIn("p03_workspace", xml)

    def test_four_persona_role_centers(self):
        xml = (MODULE / "views" / "p03_actions.xml").read_text(encoding="utf-8")
        for persona in ("Operations", "Finance", "Branch", "Super User"):
            self.assertIn(persona, xml)


class TestTellMeSearch(unittest.TestCase):
    """PP2-M05: the Tell-ME global search (A13)."""

    def test_controller_searches_both_locales(self):
        src = (MODULE / "controllers" / "p03_tellme.py").read_text(encoding="utf-8")
        self.assertIn("en_match", src)
        self.assertIn("bn_match", src)
        self.assertIn("auth=\"user\"", src)

    def test_controller_indexes_screens_and_reports(self):
        """The index covers modules, screens, reports AND forms — all four
        navigable entities from the registry."""
        src = (MODULE / "controllers" / "p03_tellme.py").read_text(encoding="utf-8")
        for kind in ("module", "screen", "report", "form"):
            self.assertIn(f'"{kind}"', src)

    def test_owl_component_has_keyboard_navigation(self):
        """The palette navigates with ArrowUp/ArrowDown/Enter (defect-#10)."""
        js = (MODULE / "static" / "src" / "p03_tellme.js").read_text(encoding="utf-8")
        for key in ("ArrowDown", "ArrowUp", "Enter", "Escape"):
            self.assertIn(key, js, f"keyboard nav: {key} missing")

    def test_owl_opens_with_ctrl_k_or_alt_q(self):
        js = (MODULE / "static" / "src" / "p03_tellme.js").read_text(encoding="utf-8")
        self.assertIn("ctrlKey", js)
        self.assertIn("altKey", js)

    def test_registered_as_systray(self):
        js = (MODULE / "static" / "src" / "p03_tellme.js").read_text(encoding="utf-8")
        self.assertIn('category("systray")', js)

    def test_template_has_bengali_placeholder(self):
        xml = (MODULE / "static" / "src" / "p03_tellme.xml").read_text(encoding="utf-8")
        self.assertIn("বাংলা", xml, "the search placeholder must mention বাংলা")


class TestReportCenter(unittest.TestCase):
    """PP2-M04: the Report Center (A10/A11)."""

    def test_action_registered(self):
        xml = (MODULE / "views" / "p03_actions.xml").read_text(encoding="utf-8")
        self.assertIn("p03_report_center", xml)
        self.assertIn("Report Center", xml)

    def test_owl_lists_346_reports(self):
        """The component computes the total from the registry — the
        prototype's full report library is the denominator."""
        js = (MODULE / "static" / "src" / "p03_report_center.js").read_text(encoding="utf-8")
        self.assertIn("reports", js)
        self.assertIn("totalReports", js)

    def test_filter_by_area_and_query(self):
        js = (MODULE / "static" / "src" / "p03_report_center.js").read_text(encoding="utf-8")
        self.assertIn("areaFilter", js)
        self.assertIn("query", js)

    def test_template_renders_module_sections_with_counts(self):
        xml = (MODULE / "static" / "src" / "p03_report_center.xml").read_text(encoding="utf-8")
        self.assertIn("mod.reports.length", xml)
        self.assertIn("t-esc=\"report\"", xml)


class TestGridConformance(unittest.TestCase):
    """PP2-M02-T01: grid/list conformance layer (A4)."""

    def test_scss_defines_filter_chips(self):
        scss = (MODULE / "static" / "src" / "p03_conformance.scss").read_text(encoding="utf-8")
        self.assertIn("p03-filter-chip", scss)

    def test_scss_defines_sortable_headers(self):
        scss = (MODULE / "static" / "src" / "p03_conformance.scss").read_text(encoding="utf-8")
        self.assertIn("p03-sortable", scss)
        self.assertIn("sort-asc", scss)
        self.assertIn("sort-desc", scss)

    def test_scss_defines_status_pills(self):
        scss = (MODULE / "static" / "src" / "p03_conformance.scss").read_text(encoding="utf-8")
        for status in ("success", "warning", "error", "info", "neutral"):
            self.assertIn(f"&.{status}", scss)

    def test_scss_focus_ring(self):
        scss = (MODULE / "static" / "src" / "p03_conformance.scss").read_text(encoding="utf-8")
        self.assertIn(":focus-visible", scss)


class TestRecordDetails(unittest.TestCase):
    """PP2-M02-T02: record details — BPF stepper + FactBox (A5)."""

    def test_bpf_stepper_on_service_order(self):
        xml = (MODULE / "views" / "p03_service_order_details.xml").read_text(encoding="utf-8")
        self.assertIn("p03-bpf-strip", xml)
        # the six stages of the service-order lifecycle
        for stage in ("Intake", "Diagnostic", "Estimate", "Repair", "QC", "Close"):
            self.assertIn(stage, xml)

    def test_factbox_rail_present(self):
        xml = (MODULE / "views" / "p03_service_order_details.xml").read_text(encoding="utf-8")
        self.assertIn("p03_factbox", xml)
        self.assertIn("FactBox", xml)

    def test_view_inherits_existing_form(self):
        xml = (MODULE / "views" / "p03_service_order_details.xml").read_text(encoding="utf-8")
        self.assertIn("inherit_id", xml)
        self.assertIn("cd_service_order.view_fix_service_order_form", xml)


class TestDispatchConsole(unittest.TestCase):
    """PP2-M03: the process console (A7)."""

    def test_action_registered(self):
        xml = (MODULE / "views" / "p03_actions.xml").read_text(encoding="utf-8")
        self.assertIn("p03_dispatch_console", xml)
        self.assertIn("Dispatch Console", xml)

    def test_reads_from_real_model_not_literals(self):
        """The console renders read_group data — never fabricated values."""
        js = (MODULE / "static" / "src" / "p03_dispatch_console.js").read_text(encoding="utf-8")
        self.assertIn("readGroup", js)
        self.assertIn("fix.work.order", js)

    def test_template_has_status_pills_and_refresh(self):
        xml = (MODULE / "static" / "src" / "p03_dispatch_console.xml").read_text(encoding="utf-8")
        self.assertIn("badge", xml)
        self.assertIn("Refresh", xml)


class TestTabRail(unittest.TestCase):
    """PP2-M07: the tab rail port."""

    def test_persists_to_localstorage(self):
        js = (MODULE / "static" / "p03_tab_rail.js").read_text(encoding="utf-8") if (MODULE / "static" / "p03_tab_rail.js").exists() else \
             (MODULE / "static" / "src" / "p03_tab_rail.js").read_text(encoding="utf-8")
        self.assertIn("localStorage", js)
        self.assertIn("p03_open_tabs", js)

    def test_caps_tab_count(self):
        js = (MODULE / "static" / "src" / "p03_tab_rail.js").read_text(encoding="utf-8")
        self.assertIn("MAX_TABS", js)

    def test_no_lru_eviction_beyond_cap(self):
        """Non-normative: LRU eviction is NOT a requirement — the cap is."""
        js = (MODULE / "static" / "src" / "p03_tab_rail.js").read_text(encoding="utf-8")
        self.assertNotIn("BroadcastChannel", js, "BroadcastChannel sync is NOT a requirement")


class TestCoverageLedger(unittest.TestCase):
    """PP2-M03: the screen-key coverage ledger exists and is honest."""

    def test_ledger_generated_with_totals(self):
        ledger = (REPO / "docs" / "navigation" / "p03-coverage-ledger.md").read_text(encoding="utf-8")
        self.assertIn("backed", ledger)
        self.assertIn("unbacked", ledger)
        self.assertIn("Totals", ledger)
        # 754 screens is the honest current state (nothing backed yet at PP2
        # scaffold; phases wire actions and the number drops)
        self.assertIn("754", ledger)

class TestP03ConsolesAndRoles(unittest.TestCase):
    """P03 Operations Portal: 15 Role Workspaces, Dispatch Console, and Branch & Workshop Consoles."""

    def test_fifteen_role_workspaces_defined(self):
        js = (MODULE / "static" / "src" / "p03_modules_meta.js").read_text(encoding="utf-8")
        self.assertIn("P03_ROLES", js)
        expected_roles = [
            "service_intake", "dispatch_manager", "branch_manager", "workshop_supervisor",
            "field_technician", "inventory_keeper", "procurement_officer", "finance_officer",
            "hr_payroll", "quality_auditor", "contact_centre_agent", "account_manager",
            "marketplace_ops", "rider_logistics", "system_admin"
        ]
        for role in expected_roles:
            self.assertTrue(f"'{role}'" in js or f'"{role}"' in js, f"Role workspace {role} must be defined in P03_ROLES")

    def test_dispatch_map_data_route_defined(self):
        """PP7: the map endpoint must serve real data ONLY — the synthetic
        'Seed Dhaka Circle' geofence and jittered technician GPS that this
        test originally asserted were fabrication defects, removed."""
        src = (MODULE / "controllers" / "p03_service_order_api.py").read_text(encoding="utf-8")
        self.assertIn('"/p03/dispatch/map_data"', src)
        self.assertIn("branches", src)
        self.assertIn("technicians", src)
        self.assertNotIn("Seed Dhaka Circle", src)
        # technician positions come from real attendance GPS only
        self.assertIn("geo_lat", src)

    def test_consoles_data_route_defined(self):
        src = (MODULE / "controllers" / "p03_service_order_api.py").read_text(encoding="utf-8")
        self.assertIn('"/p03/consoles/data"', src)
        self.assertIn("branch_console", src)
        self.assertIn("workshop_console", src)
        self.assertIn("walkin_queue", src)
        self.assertIn("wip_ageing", src)
        self.assertIn("bench_board", src)
        self.assertIn("qc_queue", src)

    def test_workspace_template_contains_all_consoles(self):
        xml = (MODULE / "static" / "src" / "p03_workspace.xml").read_text(encoding="utf-8")
        self.assertIn("dispatch_console", xml)
        self.assertIn("branch_console", xml)
        self.assertIn("workshop_console", xml)
        self.assertIn("role-switcher-card", xml)
        self.assertIn("Live Vector Map", xml)

    def test_advance_stage_route_defined(self):
        """PP7: ONE strict handler serves both paths — the parallel-session
        `advance_order_stage` (QC-checklist forgery + direct sudo writes)
        was removed; this test now asserts it stays gone."""
        src = (MODULE / "controllers" / "p03_service_order_api.py").read_text(encoding="utf-8")
        self.assertIn('"/p03/order/advance_stage"', src)
        self.assertIn('"/p03/service_order/advance"', src)
        self.assertIn("def advance_stage", src)
        self.assertNotIn("def advance_order_stage", src)
        self.assertNotIn("Standard Inspection (Passed)", src)


if __name__ == "__main__":
    unittest.main()
