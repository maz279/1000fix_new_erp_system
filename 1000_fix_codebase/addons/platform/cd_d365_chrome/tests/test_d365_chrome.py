"""cd_d365_chrome tests — same CFM guarantees as cd_design_tokens' own suite.

The module ships no models; what it must guarantee is that the skin is
wired into the backend bundle, is token-pure (CFM-01: no raw colour/size
literals) and references only tokens the generator actually declares — so a
rename or removal in tokens.json fails here, not in the browser.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]
REPO = MODULE.parents[2]
TOKENS_SOURCE = REPO / "libs/ts/ui/src/tokens/tokens.json"
SKIN = MODULE / "static/src"


def declared_tokens() -> set[str]:
    def walk(node: dict, prefix: str = "") -> set[str]:
        out: set[str] = set()
        for key in sorted(node):
            if key.startswith("$"):
                continue
            child = node[key]
            path = f"{prefix}.{key}" if prefix else key
            if isinstance(child, dict) and "$value" in child:
                out.add(f"${path.replace('.', '-').lower()}")
            elif isinstance(child, dict):
                out.update(walk(child, path))
        return out

    with open(TOKENS_SOURCE, encoding="utf-8") as handle:
        return walk(json.load(handle))


class TestManifestWiring(unittest.TestCase):
    def test_skin_is_in_the_backend_bundle(self):
        text = (MODULE / "__manifest__.py").read_text(encoding="utf-8")
        self.assertIn("cd_d365_chrome/static/src/chrome.scss", text)
        self.assertIn("cd_d365_chrome/static/src/discuss.scss", text)
        self.assertIn("web.assets_backend", text)
        self.assertIn("cd_design_tokens", text)  # token dependency is mandatory


class TestTokenPurity(unittest.TestCase):
    RAW_COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\brgb[a]?\(")
    RAW_SIZE = re.compile(r"\b\d+(\.\d+)?(px|rem|em|pt)\b")

    def test_skin_contains_no_raw_literals(self):
        for partial in sorted(SKIN.glob("*.scss")):
            for line_no, line in enumerate(partial.read_text(encoding="utf-8").splitlines(), 1):
                code = line.split("//")[0]
                self.assertIsNone(self.RAW_COLOR.search(code), f"{partial.name}:{line_no}")
                self.assertIsNone(self.RAW_SIZE.search(code), f"{partial.name}:{line_no} {code}")

    def test_skin_references_only_declared_tokens(self):
        declared = declared_tokens()
        self.assertTrue(declared, "tokens.json unreadable — token-purity test cannot run")
        for partial in sorted(SKIN.glob("*.scss")):
            for ref in re.findall(r"\$[a-z0-9-]+", partial.read_text(encoding="utf-8")):
                self.assertIn(ref, declared, f"{partial.name}: unknown token {ref}")


if __name__ == "__main__":
    unittest.main()
