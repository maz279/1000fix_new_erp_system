#!/usr/bin/env python3
"""
load_master_data.py - Wrapper in migrations/ delegating to tooling/scripts/load-master-data.py
"""
import sys
from pathlib import Path

# Add project root and invoke main
script_path = Path(__file__).resolve().parent.parent / "tooling" / "scripts" / "load-master-data.py"
exec(script_path.read_text(encoding="utf-8"))
