#!/usr/bin/env python3
"""
load_master_data.py - Wrapper in migrations/ delegating to tooling/scripts/load-master-data.py
"""

import runpy
from pathlib import Path

# Add project root and invoke main
script_path = Path(__file__).resolve().parent.parent / "tooling" / "scripts" / "load-master-data.py"
runpy.run_path(str(script_path), run_name="__main__")
