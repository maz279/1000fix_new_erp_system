# brand_submission_engine.py — Configuration-driven Brand Warranty Submission Workflows (R05-M01-T03)
#
# Transforms claims into brand-specific format via configuration (not release code).
# Enforces the BLOCKING completeness check — incomplete packs are blocked before dispatch.
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class CompletenessViolationError(Exception):
    """Raised when a claim fails the blocking completeness check."""

    def __init__(self, claim_no: str, brand_name: str, missing_items: list[str]):
        self.claim_no = claim_no
        self.brand_name = brand_name
        self.missing_items = missing_items
        super().__init__(
            f"Claim {claim_no} blocked for {brand_name}: missing mandatory evidence: "
            f"{', '.join(missing_items)} (incomplete pack rejected at gateway)"
        )


class BrandTemplateRegistry:
    """Loads and caches the 18 brand templates."""

    def __init__(self, config_path: Path | None = None):
        if config_path is None:
            config_path = Path(__file__).resolve().parent / "brand_templates.json"
        self.config_path = config_path
        self._templates: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self):
        data = json.loads(self.config_path.read_text(encoding="utf-8"))
        for tmpl in data.get("templates", []):
            self._templates[tmpl["brand_code"]] = tmpl
            # also index by brand_name lower
            self._templates[tmpl["brand_name"].lower()] = tmpl

    def get_template(self, brand_key: str) -> dict[str, Any] | None:
        return self._templates.get(brand_key) or self._templates.get(brand_key.lower())

    def list_all_templates(self) -> list[dict[str, Any]]:
        # return unique by brand_code
        seen = set()
        result = []
        for v in self._templates.values():
            if v["brand_code"] not in seen:
                seen.add(v["brand_code"])
                result.append(v)
        return sorted(result, key=lambda x: x["brand_code"])


class BrandSubmissionWorkflow:
    """Executes a single brand's submission workflow per its template."""

    def __init__(self, template: dict[str, Any]):
        self.template = template
        self.brand_code = template["brand_code"]
        self.brand_name = template["brand_name"]
        self.channel = template["channel"]
        self.endpoint = template["endpoint"]
        self.mandatory_evidence = set(template.get("mandatory_evidence", []))
        self.mapping = template.get("payload_mapping", {})

    def check_completeness(self, claim_data: dict[str, Any]) -> bool:
        """T03 / T05: BLOCKING completeness check.
        Raises CompletenessViolationError if any mandatory evidence is missing."""
        present_evidence = set(claim_data.get("evidence_keys", []))
        missing = [item for item in self.mandatory_evidence if item not in present_evidence]
        if missing:
            raise CompletenessViolationError(
                claim_no=claim_data.get("claim_no", "UNKNOWN"),
                brand_name=self.brand_name,
                missing_items=missing,
            )
        return True

    def transform_payload(self, claim_data: dict[str, Any]) -> dict[str, Any]:
        """Transforms generic claim fields into brand-specific payload based on mapping."""
        brand_payload = {
            "header": {
                "brand_code": self.brand_code,
                "brand_name": self.brand_name,
                "submission_channel": self.channel,
                "target_endpoint": self.endpoint,
            },
            "data": {},
        }
        for brand_field, source_field in self.mapping.items():
            brand_payload["data"][brand_field] = claim_data.get(source_field)

        return brand_payload

    def execute_submission(self, claim_data: dict[str, Any]) -> dict[str, Any]:
        """Full pipeline: Validate -> Transform -> Submit (mock transport)."""
        # 1. Blocking completeness check
        self.check_completeness(claim_data)

        # 2. Transform per brand template
        transformed = self.transform_payload(claim_data)

        # 3. Dispatch to destination channel
        ack = {
            "status": "submitted",
            "claim_no": claim_data.get("claim_no"),
            "brand_code": self.brand_code,
            "channel": self.channel,
            "endpoint": self.endpoint,
            "payload": transformed,
            "acknowledgement_ref": f"ACK/{self.brand_code}/{claim_data.get('claim_no')}",
        }
        return ack
