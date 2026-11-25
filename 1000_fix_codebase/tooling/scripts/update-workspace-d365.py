#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(
    "c:/software_project/software_project_14/1000 fix/1000fix_new_erp_system/1000_fix_codebase"
)
JS_PATH = ROOT / "addons" / "platform" / "cd_p03_portal" / "static" / "src" / "p03_workspace.js"
XML_PATH = ROOT / "addons" / "platform" / "cd_p03_portal" / "static" / "src" / "p03_workspace.xml"

js_text = JS_PATH.read_text(encoding="utf-8")

old_ml_rows = """    get mlRows() {
        const gl = this.state.gl;
        if (!gl || !gl.data || gl.data.error) return [];
        return gl.data.rows || [];
    }"""

new_ml_methods = """    get mlRows() {
        const gl = this.state.gl;
        if (!gl || !gl.data || gl.data.error) return [];
        let rows = gl.data.rows || [];

        // 1. D365 Quick-Find Search Filter across all visible columns
        if (gl.mlSearch && gl.mlSearch.trim()) {
            const q = gl.mlSearch.toLowerCase().trim();
            rows = rows.filter((r) => {
                const cols = gl.modelCfg.cols || Object.keys(r);
                return cols.some((col) => {
                    const val = r[col];
                    if (val == null) return false;
                    if (typeof val === "object") {
                        const s = val.label || val.name || "";
                        return String(s).toLowerCase().includes(q);
                    }
                    return String(val).toLowerCase().includes(q);
                });
            });
        }

        // 2. D365 Column Header Sorting
        if (gl.mlSortCol) {
            const col = gl.mlSortCol;
            const asc = gl.mlSortAsc !== false ? 1 : -1;
            rows = [...rows].sort((a, b) => {
                let va = a[col], vb = b[col];
                if (va && typeof va === "object") va = va.label || va.name || "";
                if (vb && typeof vb === "object") vb = vb.label || vb.name || "";
                if (va == null && vb == null) return 0;
                if (va == null) return 1;
                if (vb == null) return -1;
                if (typeof va === "number" && typeof vb === "number") return (va - vb) * asc;
                return String(va).localeCompare(String(vb)) * asc;
            });
        }

        return rows;
    }

    mlToggleSort(col) {
        const gl = this.state.gl;
        if (gl.mlSortCol === col) {
            gl.mlSortAsc = !gl.mlSortAsc;
        } else {
            gl.mlSortCol = col;
            gl.mlSortAsc = true;
        }
    }

    mlOnSearchInput(ev) {
        this.state.gl.mlSearch = ev.target.value;
    }

    mlClearSearch() {
        this.state.gl.mlSearch = "";
    }

    mlExportCsv() {
        const gl = this.state.gl;
        if (!gl || !gl.data || !gl.modelCfg) return;
        const cols = gl.modelCfg.cols || [];
        const labels = gl.data.labels || {};
        const rows = this.mlRows;

        const headerRow = cols.map(c => `"${(labels[c] || c).replace(/"/g, '""')}"`).join(",");
        const dataRows = rows.map(r => {
            return cols.map(c => {
                const cellText = this.mlCell(r, c);
                return `"${String(cellText).replace(/"/g, '""')}"`;
            }).join(",");
        });

        const csvContent = "\\uFEFF" + [headerRow, ...dataRows].join("\\r\\n");
        const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        const filename = `${gl.modelCfg.model || "records"}_export_${new Date().toISOString().slice(0, 10)}.csv`;
        link.setAttribute("href", url);
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        this.showToast(this.t(`Exported ${rows.length} records to CSV`));
    }"""

# Normalize line endings for replacement
if old_ml_rows in js_text:
    js_text = js_text.replace(old_ml_rows, new_ml_methods)
    JS_PATH.write_text(js_text, encoding="utf-8")
    print("p03_workspace.js successfully updated with D365 mlRows, sort, search, and export!")
else:
    # Try with CRLF
    old_crlf = old_ml_rows.replace("\n", "\r\n")
    if old_crlf in js_text:
        js_text = js_text.replace(old_crlf, new_ml_methods.replace("\n", "\r\n"))
        JS_PATH.write_text(js_text, encoding="utf-8")
        print("p03_workspace.js successfully updated with CRLF!")
    else:
        print("Could not find old_ml_rows in p03_workspace.js!")
