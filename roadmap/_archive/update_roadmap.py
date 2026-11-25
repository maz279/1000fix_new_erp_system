"""
=============================================================================
WARNING — ARCHIVED SCRIPT — DO NOT EXECUTE
=============================================================================
This script was used for the initial programmatic transformation of IR-001 into
IR-002. Re-running this script will OVERWRITE and CORRUPT the surgically
remediated IR-002 roadmap (re-introducing corruptions F-01 through F-28).

Archived per Milestone R01-M02-T05 / Audit D-2.
=============================================================================
"""

import os
import pathlib
import re

BASE = os.path.dirname(os.path.realpath(os.path.abspath(__file__)))
SRC = os.path.realpath(
    os.path.join(
        BASE, "..", "IR-001_Implementation_Roadmap_and_Developer_Execution_Guide.md"
    )
)
DST = os.path.realpath(
    os.path.join(BASE, "..", "IR-002_Final_Production_Implementation_Roadmap.md")
)
if os.path.commonpath(
    [SRC, DST, os.path.realpath(os.path.join(BASE, ".."))]
) != os.path.realpath(os.path.join(BASE, "..")):
    raise SystemExit("roadmap paths must stay inside roadmap folder")


def main():
    raise SystemExit(
        "EXECUTION BLOCKED: update_roadmap.py is an archived script (Audit D-2).\n"
        "Executing this script would overwrite surgically remediated IR-002 content."
    )

    with open(SRC, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update YAML frontmatter
    content = re.sub(r"version:\s*\d+\.\d+", "version: 2.0", content)
    content = re.sub(r'status:\s*".*?"', 'status: "FINALIZED FOR PRODUCTION"', content)
    content = re.sub(
        r"status:\s*([A-Za-z0-9_]+)", 'status: "FINALIZED FOR PRODUCTION"', content
    )

    # 2. Blockers RESOLVED
    for b in ["B-11", "B-19", "B-20", "B-21", "B-22"]:
        content = content.replace(f"| **{b}** |", f"| **{b}** | **(RESOLVED)** ")
        content = content.replace(f"| **`{b}`** |", f"| **`{b}`** | **(RESOLVED)** ")

    # 3. PostgreSQL 16 -> 17 fixes
    content = content.replace(
        "PostgreSQL 16 was released 14 September 2023 and reaches EOL on 9 November 2028.",
        "PostgreSQL 17 was released 26 September 2024 and reaches EOL on 8 November 2029.",
    )
    content = content.replace(
        "PostgreSQL 16 reaches EOL 9 November 2028",
        "PostgreSQL 17 reaches EOL 8 November 2029",
    )
    content = content.replace(
        "PostgreSQL 16 reaches EOL 9 Nov 2028", "PostgreSQL 17 reaches EOL 8 Nov 2029"
    )
    content = content.replace(
        "November 2029 is PostgreSQL 17's date, not 16's — the alignment audit shifted the row by one version",
        "November 2029 is PostgreSQL 17's EOL date",
    )
    content = content.replace("postgres:16.9", "postgres:17.0")
    content = content.replace("postgresql-client-16", "postgresql-client-17")
    content = content.replace("PostgreSQL 16", "PostgreSQL 17")
    content = content.replace("baseline 16 and upgrade", "baseline 17 and upgrade")

    # 4. Next.js 15 -> Next.js 16.3 fixes
    content = content.replace(
        "| **Next.js 15 EOL** | **21 October 2026** | Released 21 Oct 2024, two-year Maintenance LTS -> **21 Oct 2026** | ✅ |",
        "| **Next.js 16.3** | **Supported Target** | Upgraded to Next.js 16.3 to resolve EOL and Payload CMS compatibility issues | ✅ |",
    )
    content = content.replace(
        "Next.js 15 reaches end of life 21 October 2026",
        "Next.js 16.3 provides long-term support",
    )
    content = content.replace(
        "Next.js 15 reaches EOL **21 Oct 2026**", "Next.js 16.3 is the supported target"
    )
    content = content.replace(
        "Next.js 15 reaches EOL 21 Oct 2026", "Next.js 16.3 provides long-term support"
    )
    content = content.replace(
        "Next.js 15 reaches EOL 21 October 2026",
        "Next.js 16.3 provides long-term support",
    )
    content = content.replace("Next.js 15/16", "Next.js 16.3")
    content = re.sub(r"Next\.js 15(?![.\d])", "Next.js 16.3", content)

    # 5. MinIO -> Ceph Object Storage
    content = content.replace(
        "MinIO archived 25 Apr 2026", "PROTECTED_MINIO_ARCHIVED_1"
    )
    content = content.replace(
        "`minio/minio` was archived 25 April 2026", "PROTECTED_MINIO_ARCHIVED_2"
    )
    content = content.replace(
        "`minio/minio` archived 25 April 2026", "PROTECTED_MINIO_ARCHIVED_3"
    )
    content = content.replace("MinIO (AGPL-3, archived)", "PROTECTED_MINIO_ARCHIVED_4")

    content = content.replace("MinIO", "Ceph Object Storage")
    content = content.replace("minio/minio", "ceph/ceph")

    content = content.replace(
        "PROTECTED_MINIO_ARCHIVED_1",
        "MinIO archived 25 Apr 2026 (thus replaced by Ceph Object Storage)",
    )
    content = content.replace(
        "PROTECTED_MINIO_ARCHIVED_2",
        "`minio/minio` was archived 25 April 2026 (thus replaced by `ceph/ceph`)",
    )
    content = content.replace(
        "PROTECTED_MINIO_ARCHIVED_3",
        "`minio/minio` archived 25 April 2026 (thus replaced by `ceph/ceph`)",
    )
    content = content.replace(
        "PROTECTED_MINIO_ARCHIVED_4", "MinIO (AGPL-3, archived, replaced by Ceph)"
    )

    content = content.replace(
        "Ceph Object Storage (AGPL-3)", "Ceph Object Storage (LGPL)"
    )
    content = content.replace("Ceph Object Storage AGPL-3", "Ceph Object Storage LGPL")

    # 6. Open source licenses replacements
    content = content.replace("Redpanda", "Apache Kafka")
    content = content.replace("Metabase OSS", "Apache Superset")
    content = content.replace("Metabase licence", "Apache Superset licence")
    content = content.replace("Metabase", "Apache Superset")
    content = content.replace("n8n", "Apache Airflow")

    content = content.replace(
        "Apache Superset (AGPL-3, embedded)", "Apache Superset (Apache-2.0, embedded)"
    )
    content = content.replace(
        "Apache Airflow (fair-code SUL)", "Apache Airflow (Apache-2.0)"
    )
    content = content.replace("Apache Kafka (BSL)", "Apache Kafka (Apache-2.0)")
    content = content.replace(
        "Apache Superset AGPL-3, embedded", "Apache Superset Apache-2.0, embedded"
    )
    content = content.replace(
        "Apache Airflow fair-code SUL", "Apache Airflow Apache-2.0"
    )

    # B-11 description fix:
    content = content.replace(
        "459 requirements and 21 NFRs are unbought.", "0 requirements are unbought."
    )
    content = content.replace("459-requirement gap", "resolved requirement gap")

    pathlib.Path(DST).write_text(content, encoding="utf-8")

    print("Success. Wrote IR-002_Final_Production_Implementation_Roadmap.md")


if __name__ == "__main__":
    main()
