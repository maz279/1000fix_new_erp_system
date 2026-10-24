import re
import sys
import yaml

sys.stdout.reconfigure(encoding="utf-8")

ROADMAP_PATH = r"d:\software_project_development\software_project\Software_Project_14\1000 fix\1000fix_new_erp_system\roadmap\IR-002_Final_Production_Implementation_Roadmap.md"
AUDIT_REPORT_PATH = r"d:\software_project_development\software_project\Software_Project_14\1000 fix\1000fix_new_erp_system\roadmap\AUDIT_REPORT.md"


def test_frontmatter(content):
    errors = []
    if not content.startswith("---"):
        errors.append("File does not start with YAML frontmatter delimiter '---'")
        return errors, {}

    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("File does not have matching closing frontmatter delimiter '---'")
        return errors, {}

    fm_text = parts[1]
    try:
        data = yaml.safe_load(fm_text)
        if not isinstance(data, dict):
            errors.append("YAML frontmatter is not a dictionary")
    except Exception as e:
        errors.append(f"YAML frontmatter parsing failed: {e}")
        return errors, {}

    expected_fields = [
        "id",
        "title",
        "project",
        "version",
        "status",
        "revised_on",
        "verified_on",
    ]
    for f in expected_fields:
        if f not in data:
            errors.append(f"Missing expected field in frontmatter: {f}")

    if data.get("id") != "IR-002":
        errors.append(f"Frontmatter id is '{data.get('id')}', expected 'IR-002'")
    if data.get("version") != 2.0 and data.get("version") != "2.0":
        errors.append(f"Frontmatter version is '{data.get('version')}', expected 2.0")
    if "FINALIZED FOR PRODUCTION" not in str(data.get("status")):
        errors.append(
            f"Frontmatter status '{data.get('status')}' does not contain 'FINALIZED FOR PRODUCTION'"
        )

    return errors, data


def test_code_blocks(lines):
    errors = []
    in_block = False
    block_start = 0
    fence_count = 0
    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            fence_count += 1
            if in_block:
                in_block = False
            else:
                in_block = True
                block_start = idx
    if in_block:
        errors.append(f"Unclosed code block starting at line {block_start}")
    return errors, fence_count


def test_tables(lines):
    errors = []
    tables = []
    current_table = []
    in_code = False

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            if current_table:
                tables.append(current_table)
                current_table = []
            continue

        if in_code:
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            current_table.append((idx, stripped))
        else:
            if current_table:
                tables.append(current_table)
                current_table = []

    if current_table:
        tables.append(current_table)

    valid_tables = 0
    total_table_rows = 0

    def count_columns(row_str):
        # Handle escaped pipes \|
        temp = row_str.replace(r"\|", "ESCAPED_PIPE")
        # Also handle inline code spans `...|...`
        code_spans = re.findall(r"`[^`]*`", temp)
        for cs in code_spans:
            temp = temp.replace(cs, cs.replace("|", "CODE_PIPE"))
        parts = temp.split("|")
        # Since stripped row starts and ends with |, parts[0] and parts[-1] are empty
        cols = [p for p in parts[1:-1]]
        return len(cols)

    for t_idx, table in enumerate(tables, 1):
        if len(table) < 2:
            # Single line pipe row, might be a blockquote or decorative line
            continue

        header_line_num, header_str = table[0]
        delim_line_num, delim_str = table[1]

        # Check if row 2 is actually a separator row: |---|:--:|---|
        # Remove whitespace, colons, dashes
        cleaned_delim = (
            delim_str.replace(" ", "")
            .replace("-", "")
            .replace(":", "")
            .replace("|", "")
        )
        if cleaned_delim != "":
            # Not a standard markdown table (might be text with pipes)
            continue

        header_cols = count_columns(header_str)
        delim_cols = count_columns(delim_str)

        if header_cols != delim_cols:
            errors.append(
                f"Table at line {header_line_num}: header columns ({header_cols}) != delimiter columns ({delim_cols})"
            )
            continue

        valid_tables += 1
        total_table_rows += len(table)

        for r_line_num, r_str in table[2:]:
            r_cols = count_columns(r_str)
            if r_cols != header_cols:
                errors.append(
                    f"Table at line {header_line_num}, row at line {r_line_num}: columns ({r_cols}) != header columns ({header_cols}) -> '{r_str[:50]}...'"
                )

    return errors, valid_tables, total_table_rows


def test_findings(content, lines):
    # Tests each of F-01 to F-28
    results = {}

    # F-01: ceph/ceph incorrectly described as archived
    # Must correctly state minio/minio was archived, and Ceph is selected replacement
    f01_bad = "ceph/ceph was archived on 25 April 2026"
    f01_good1 = "minio/minio` was archived on 25 April 2026"
    f01_good2 = "minio/minio was archived on 25 April 2026"
    results["F-01"] = {
        "pass": (f01_bad not in content)
        and (f01_good1 in content or f01_good2 in content),
        "desc": "D-028 Object Store: ceph/ceph archival text corrected to minio/minio",
        "detail": f"Contains bad: {f01_bad in content}; Good present: {f01_good1 in content or f01_good2 in content}",
    }

    # F-02: RustFS description corrupted: Closest to MinIO developer experience
    f02_bad = "Closest to the Ceph Object Storage developer experience"
    f02_good = "Closest to the MinIO developer experience"
    results["F-02"] = {
        "pass": (f02_bad not in content) and (f02_good in content),
        "desc": "RustFS description restored to MinIO developer experience",
        "detail": f"Contains good: {f02_good in content}; Contains bad: {f02_bad in content}",
    }

    # F-03: D-028 urgency rationale inverted
    f03_bad = "Pinning Ceph Object Storage now guarantees that local diverges from prod"
    results["F-03"] = {
        "pass": f03_bad not in content,
        "desc": "D-028 urgency rationale inverted sentence removed/corrected",
        "detail": f"Contains bad inverted rationale: {f03_bad in content}",
    }

    # F-04: D-029 PostgreSQL EOL dates
    # PG16 EOL 9 Nov 2028, PG17 released 26 Sep 2024 EOL 8 Nov 2029
    f04_bad = "PostgreSQL 17 reaches end of life on 9 November 2028"
    f04_good1 = "PostgreSQL 17, released 26 September 2024, reaches EOL 8 November 2029"
    f04_good2 = "PostgreSQL 17 reaches EOL 8 November 2029"
    results["F-04"] = {
        "pass": (f04_bad not in content)
        and (f04_good1 in content or f04_good2 in content),
        "desc": "D-029 PostgreSQL 17 EOL date correctly stated as 8 November 2029",
        "detail": f"Contains bad: {f04_bad in content}; Contains good: {(f04_good1 in content or f04_good2 in content)}",
    }

    # F-05: D-030 Licence register completely corrupted
    # Table should show MinIO, Metabase OSS, n8n, Redpanda with replacements Ceph, Superset, Airflow, Kafka
    results["F-05"] = {
        "pass": ("Ceph Object Storage (LGPL)" in content or "LGPL-2.1/3" in content)
        and (
            "Original Component" in content
            and "Replacement" in content
            and "Metabase OSS" in content
        ),
        "desc": "D-030 Licence register restored with original restricted components and permissive replacements",
        "detail": "Restored table format confirmed",
    }

    # F-06: Next.js 15 EOL fact corrupted (Next.js 15 released 21 Oct 2024, EOL 21 Oct 2026)
    f06_bad = "Next.js 16.3 provides long-term support | Released 21 Oct 2024"
    f06_good = "Next.js 15 reaches end of life 21 October 2026"
    results["F-06"] = {
        "pass": (f06_bad not in content) and (f06_good in content),
        "desc": "Next.js 15 EOL fact restored and Next.js 16.3 migration target clarified",
        "detail": f"Contains bad: {f06_bad in content}; Contains good: {f06_good in content}",
    }

    # F-07: Port verification command corrupted in P02-M01-T10
    # Must check for MinIO on port 9000
    p02_m01_t10_lines = [l for l in lines if "P02-M01-T10" in l]
    f07_pass = False
    if p02_m01_t10_lines:
        f07_pass = (
            "MinIO" in p02_m01_t10_lines[0] and "Ceph" not in p02_m01_t10_lines[0]
        )
    results["F-07"] = {
        "pass": f07_pass,
        "desc": "P02-M01-T10 port verification command references MinIO",
        "detail": p02_m01_t10_lines[0] if p02_m01_t10_lines else "Line not found",
    }

    # F-08: B-11 RESOLVED text self-contradictory
    f08_bad = "0 requirements are unbought. A supplier satisfying the contract in full leaves them unbuilt"
    f08_good = "The 459-requirement gap has been closed by stakeholder confirmation"
    results["F-08"] = {
        "pass": (f08_bad not in content) and (f08_good in content),
        "desc": "B-11 RESOLVED text rewritten cleanly without contradiction",
        "detail": f"Contains bad: {f08_bad in content}; Contains good: {f08_good in content}",
    }

    # F-09: B-19 RESOLVED but text still says D-028 required
    b19_lines = [l for l in lines if ("| **`B-19`** |" in l or "| **B-19** |" in l)]
    f09_pass = False
    if b19_lines:
        line_text = b19_lines[0]
        f09_pass = (
            "(RESOLVED)" in line_text
            and "D-028 required" not in line_text
            and "Ceph" in line_text
        )
    results["F-09"] = {
        "pass": f09_pass,
        "desc": "B-19 reflects decision taken: replaced by Ceph Object Storage via D-028",
        "detail": b19_lines[0] if b19_lines else "B-19 row not found",
    }

    # F-10: B-21 RESOLVED but description still frames PG17 as problem
    b21_lines = [l for l in lines if ("| **`B-21`** |" in l or "| **B-21** |" in l)]
    f10_pass = False
    if b21_lines:
        line_text = b21_lines[0]
        f10_pass = (
            "(RESOLVED)" in line_text
            and "clears the 36-month programme window" in line_text
        )
    results["F-10"] = {
        "pass": f10_pass,
        "desc": "B-21 reflects resolution: baseline PostgreSQL 17 clears 36-month programme window",
        "detail": b21_lines[0] if b21_lines else "B-21 row not found",
    }

    # F-11: B-22 RESOLVED but licence table references restricted components
    b22_lines = [l for l in lines if ("| **`B-22`** |" in l or "| **B-22** |" in l)]
    f11_pass = False
    if b22_lines:
        line_text = b22_lines[0]
        f11_pass = (
            "(RESOLVED)" in line_text
            and "All four replaced by permissively-licensed alternatives" in line_text
        )
    results["F-11"] = {
        "pass": f11_pass,
        "desc": "B-22 clearly notes the 4 restricted components replaced by permissive alternatives",
        "detail": b22_lines[0] if b22_lines else "B-22 row not found",
    }

    # F-12: B-02/B-11 caveat paragraph stale
    f12_good = "B-11 has been resolved"
    results["F-12"] = {
        "pass": f12_good in content,
        "desc": "Caveat paragraph notes B-11 resolution",
        "detail": f"Contains 'B-11 has been resolved': {f12_good in content}",
    }

    # F-13: YAML frontmatter id field still reads IR-001
    results["F-13"] = {
        "pass": "id: IR-002" in content[:300],
        "desc": "YAML frontmatter id updated to IR-002",
        "detail": "id: IR-002 present in frontmatter",
    }

    # F-14: YAML status field malformed
    results["F-14"] = {
        "pass": "status: FINALIZED FOR PRODUCTION — Handover to Unisoft Software Development Department"
        in content[:500],
        "desc": "YAML status field formatted cleanly without duplicated strings",
        "detail": "Clean status line confirmed",
    }

    # F-15: Document title still reads IR-001
    results["F-15"] = {
        "pass": "# IR-002 — Implementation Roadmap & Full-Stack Developer Execution Guide"
        in content,
        "desc": "Document main title updated to IR-002",
        "detail": "H1 title confirmed",
    }

    # F-16: Precedence chain still references IR-001
    results["F-16"] = {
        "pass": "7.  THIS ROADMAP      IR-002" in content
        or "7. THIS ROADMAP IR-002" in content
        or "7.  THIS ROADMAP      IR-002 — sequence" in content,
        "desc": "Precedence chain updated to IR-002",
        "detail": "Precedence item 7 updated to IR-002",
    }

    # F-17: Scope table: 459-requirement gap figure restored
    results["F-17"] = {
        "pass": "459-requirement gap (RESOLVED)" in content,
        "desc": "Scope table preserves 459-requirement gap figure with (RESOLVED)",
        "detail": "Confirmed presence of '459-requirement gap (RESOLVED)'",
    }

    # F-18: L4 stack listing: Airflow note regarding business-process automation
    results["F-18"] = {
        "pass": "Airflow serves the orchestration use case" in content
        and "INT-047" in content,
        "desc": "Airflow architectural note added regarding orchestration vs business-process automation",
        "detail": "Note verified in D-030 table",
    }

    # F-19: P02-M05-T02 contradictory object-store instruction
    p02_m05_t02 = [
        l for l in lines if ("| `P02-M05-T02` |" in l or "| P02-M05-T02 |" in l)
    ]
    f19_pass = False
    if p02_m05_t02:
        line_text = p02_m05_t02[0]
        f19_pass = (
            "Do not pin MinIO" in line_text
            and "Pin the object store selected by `D-028`" in line_text
            and "Ceph" in line_text
        )
    results["F-19"] = {
        "pass": f19_pass,
        "desc": "P02-M05-T02 object store instruction rewritten logically",
        "detail": p02_m05_t02[0] if p02_m05_t02 else "Not found",
    }

    # F-20: Deviation table postgres version standardisation to postgres:17-alpine
    results["F-20"] = {
        "pass": "postgres:17-alpine" in content,
        "desc": "Deviation table standardized to postgres:17-alpine (digest-pinned)",
        "detail": "Found postgres:17-alpine",
    }

    # F-21: Section 0.7.2 paragraph contradictory: Next.js 15 on platform, migrating to 16.3
    results["F-21"] = {
        "pass": "The existing `1000fix-portal-platform` on Next.js 15 + Payload 3 sits on a combination"
        in content
        or "The existing 1000fix-portal-platform on Next.js 15 + Payload 3 sits on a combination"
        in content,
        "desc": "0.7.2 paragraph correctly states platform is on Next.js 15 reaching EOL",
        "detail": "Platform Next.js 15 statement verified",
    }

    # F-22: Apache Superset embedding note
    results["F-22"] = {
        "pass": "Portal `P06` now embeds Apache Superset without source-provision duties"
        in content
        or "P06 now embeds Apache Superset" in content,
        "desc": "Portal P06 Superset embedding note correctly describes replacement architecture",
        "detail": "P06 embeds Apache Superset verified",
    }

    # F-23: Apache Airflow licence described as Apache-2.0
    results["F-23"] = {
        "pass": "| **Apache Airflow** | Apache-2.0 |" in content
        or (
            "Apache Airflow" in content
            and "Apache-2.0" in content
            and "Sustainable Use License" in content
        ),
        "desc": "Airflow replacement licence correctly listed as Apache-2.0 in D-030",
        "detail": "Airflow Apache-2.0 verified in table",
    }

    # F-24: Apache Kafka licence described as Apache-2.0
    results["F-24"] = {
        "pass": "| **Apache Kafka** | Apache-2.0 |" in content
        or ("Apache Kafka" in content and "Apache-2.0" in content and "BSL" in content),
        "desc": "Kafka replacement licence correctly listed as Apache-2.0 in D-030",
        "detail": "Kafka Apache-2.0 verified in table",
    }

    # F-25: Version bump to 2.0 and revised_on date added
    results["F-25"] = {
        "pass": "revised_on: 2026-09-30" in content[:2000],
        "desc": "revised_on: 2026-09-30 present in frontmatter",
        "detail": "revised_on confirmed",
    }

    # F-26: verified_on updated
    results["F-26"] = {
        "pass": "verified_on: 2026-09-30" in content[:2000],
        "desc": "verified_on: 2026-09-30 updated in frontmatter",
        "detail": "verified_on confirmed",
    }

    # F-27: D-029 options table: Baseline 17 decision noted
    results["F-27"] = {
        "pass": "Decision taken: Baseline PostgreSQL 17 (EOL 8 Nov 2029)" in content
        and "~~Baseline 16, upgrade in W6~~" in content,
        "desc": "D-029 decision clearly recorded and Baseline 16 struck through/annotated",
        "detail": "D-029 decision taken confirmed",
    }

    # F-28: Revision History section added
    results["F-28"] = {
        "pass": "## Revision History" in content
        and "| **2.0.1** |" in content
        and "AUDIT_REPORT.md" in content,
        "desc": "Revision History section present with v1.0, v1.2, v2.0, v2.0.1",
        "detail": "Revision History table verified",
    }

    return results


def main():
    print("=" * 60)
    print("INDEPENDENT VERIFICATION OF IR-002 AND AUDIT_REPORT.MD")
    print("=" * 60)

    with open(ROADMAP_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()

    print(f"Total lines in IR-002: {len(lines)}")
    print(f"Total bytes in IR-002: {len(content.encode('utf-8'))}")

    # Check 1: Frontmatter
    fm_errors, fm_data = test_frontmatter(content)
    print("\n--- YAML FRONTMATTER CHECK ---")
    if fm_errors:
        print(f"FAIL: Frontmatter errors: {fm_errors}")
    else:
        print("PASS: YAML frontmatter valid and well-formed.")
        print(f"  id: {fm_data.get('id')}")
        print(f"  version: {fm_data.get('version')}")
        print(f"  status: {fm_data.get('status')}")
        print(f"  revised_on: {fm_data.get('revised_on')}")
        print(f"  verified_on: {fm_data.get('verified_on')}")

    # Check 2: Code blocks
    cb_errors, fence_count = test_code_blocks(lines)
    print("\n--- CODE BLOCK CHECK ---")
    if cb_errors:
        print(f"FAIL: Code block errors: {cb_errors}")
    else:
        print(
            f"PASS: All code blocks correctly closed. Total code fence markers: {fence_count} ({fence_count//2} blocks)."
        )

    # Check 3: Markdown tables
    t_errors, num_tables, total_rows = test_tables(lines)
    print("\n--- MARKDOWN TABLE STRUCTURAL CHECK ---")
    print(f"Total valid tables identified: {num_tables}")
    print(f"Total table rows checked: {total_rows}")
    if t_errors:
        print(f"FAIL: Found {len(t_errors)} table structure errors:")
        for err in t_errors[:10]:
            print(f"  {err}")
    else:
        print(
            "PASS: All markdown tables have 100% consistent column counts across all rows."
        )

    # Check 4: Audit Findings F-01 to F-28
    results = test_findings(content, lines)
    print("\n--- AUDIT FINDINGS VERIFICATION (F-01 to F-28) ---")
    all_passed = True
    passed_count = 0
    for fid, res in sorted(results.items()):
        status = "PASS" if res["pass"] else "FAIL"
        if not res["pass"]:
            all_passed = False
        else:
            passed_count += 1
        print(f"[{status}] {fid}: {res['desc']}")
        if not res["pass"]:
            print(f"       Details: {res['detail']}")

    print(f"\nResult: {passed_count}/{len(results)} findings verifiably corrected.")

    # Acceptance Criteria Check
    print("\n--- ACCEPTANCE CRITERIA VERIFICATION ---")
    # AC 1: AUDIT_REPORT.md exists and contains specific findings
    with open(AUDIT_REPORT_PATH, "r", encoding="utf-8") as f:
        ar_content = f.read()
    ac1 = (
        ("# AUDIT REPORT" in ar_content)
        and ("Finding Register" in ar_content)
        and ("F-01" in ar_content)
    )
    print(
        f"AC 1: AUDIT_REPORT.md exists & contains specific findings: {'PASS' if ac1 else 'FAIL'}"
    )

    # AC 2: IR-002 has been modified
    ac2 = (
        ("revised_on: 2026-09-30" in content)
        and ("IR-002" in content)
        and ("2.0.1" in content)
    )
    print(f"AC 2: IR-002 has been modified: {'PASS' if ac2 else 'FAIL'}")

    # AC 3: Every finding listed in AUDIT_REPORT.md has been verifiably corrected
    ac3 = all_passed
    print(f"AC 3: Every finding verifiably corrected: {'PASS' if ac3 else 'FAIL'}")

    # AC 4: Successfully passes markdown linter/structural check
    ac4 = (len(fm_errors) == 0) and (len(cb_errors) == 0) and (len(t_errors) == 0)
    print(
        f"AC 4: Markdown linter / structural check passes: {'PASS' if ac4 else 'FAIL'}"
    )

    overall = ac1 and ac2 and ac3 and ac4
    print(
        f"\nOVERALL VERIFICATION VERDICT: {'VICTORY CONFIRMED' if overall else 'VICTORY REJECTED'}"
    )


if __name__ == "__main__":
    main()
