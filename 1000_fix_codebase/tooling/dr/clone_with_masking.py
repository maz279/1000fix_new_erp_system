#!/usr/bin/env python3
"""clone_with_masking.py — In-Stream Sovereign PII Masking Pipeline for Staging Clones (NFR-086c).

Statutory Invariant:
Under Bangladesh Personal Data Protection Act (PDPA) §4.5.4, NFR-086c, and Rule SC-002:
"Non-production NEVER holds unmasked residency-classified data in any region.
Masking runs INSIDE the clone job — an unmasked clone cannot exist even briefly on disk."

This script streams database dump/table data through an in-memory transformer,
substituting all sovereign PII with cryptographically pseudorandom yet structurally
valid synthetic counterparts before any byte is written to the destination.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import hmac
import re
import sys
from collections.abc import Iterable

MASKING_SALT = b"1000fix_sovereign_z4_nfr086c_masking_salt_2026"

# Regex patterns for Bangladesh Sovereign PII
NID_PATTERN = re.compile(r"\b(?:\d{10}|\d{13}|\d{17})\b")
PHONE_BD_PATTERN = re.compile(r"(?:\+?8801|01)[3-9]\d{8}\b")
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
BANK_ACC_PATTERN = re.compile(r"\b(?:1\d{12}|2\d{12}|[0-9]{13,16})\b")
MFS_WALLET_PATTERN = re.compile(r"\b(?:bkash|nagad|rocket)[-_:]?(?:01[3-9]\d{8})\b", re.IGNORECASE)
MASKED_EMAIL_DOMAIN = "@masked.1000fix.internal"


def mask_nid(raw_nid: str) -> str:
    digest = hmac.new(MASKING_SALT, raw_nid.encode("utf-8"), hashlib.sha256).hexdigest()[:8]
    return f"BD-NID-MASKED-{digest.upper()}"


def mask_phone(raw_phone: str) -> str:
    digest = hmac.new(MASKING_SALT, raw_phone.encode("utf-8"), hashlib.sha256).hexdigest()[:4]
    return f"+880170000{digest[:4]}"


def mask_email(raw_email: str) -> str:
    digest = hmac.new(MASKING_SALT, raw_email.encode("utf-8"), hashlib.sha256).hexdigest()[:8]
    return f"anon-{digest}{MASKED_EMAIL_DOMAIN}"


def mask_mfs(raw_mfs: str) -> str:
    digest = hmac.new(MASKING_SALT, raw_mfs.encode("utf-8"), hashlib.sha256).hexdigest()[:6]
    return f"MFS-WALLET-{digest.upper()}"


def mask_bank_acc(raw_acc: str) -> str:
    digest = hmac.new(MASKING_SALT, raw_acc.encode("utf-8"), hashlib.sha256).hexdigest()[:6]
    return f"BANK-ACC-{digest.upper()}"


def mask_stream_chunk(text: str) -> str:
    """In-stream transformation applying regex masking without saving intermediate files."""
    # 1. Mask MFS wallets
    text = MFS_WALLET_PATTERN.sub(lambda m: mask_mfs(m.group(0)), text)
    # 2. Mask Phone numbers
    text = PHONE_BD_PATTERN.sub(lambda m: mask_phone(m.group(0)), text)
    # 3. Mask Emails
    text = EMAIL_PATTERN.sub(lambda m: mask_email(m.group(0)), text)
    # 4. Mask NID numbers (10/13/17 digits)
    text = NID_PATTERN.sub(lambda m: mask_nid(m.group(0)), text)
    # 5. Mask bank account numbers (the 14-16 digit runs NID masking leaves)
    text = BANK_ACC_PATTERN.sub(lambda m: mask_bank_acc(m.group(0)), text)
    return text


def residual_pii(text: str) -> list[str]:
    """PII kinds whose raw pattern still matches `text` (masked placeholders excluded)."""
    kinds = [
        kind
        for kind, pattern in (
            ("MFS_WALLET", MFS_WALLET_PATTERN),
            ("MOBILE_BD", PHONE_BD_PATTERN),
            ("NID", NID_PATTERN),
            ("BANK_ACC", BANK_ACC_PATTERN),
        )
        if pattern.search(text)
    ]
    if any(not m.group(0).endswith(MASKED_EMAIL_DOMAIN) for m in EMAIL_PATTERN.finditer(text)):
        kinds.append("EMAIL")
    return kinds


def process_stream(input_stream: Iterable[str], output_stream) -> dict:
    lines_processed = 0
    bytes_processed = 0
    masks_applied = 0
    residual_lines = 0

    for line in input_stream:
        masked_line = mask_stream_chunk(line)
        output_stream.write(masked_line)
        lines_processed += 1
        bytes_processed += len(masked_line.encode("utf-8"))
        if masked_line != line:
            masks_applied += 1
        if residual_pii(masked_line):
            residual_lines += 1

    return {
        "status": "SUCCESS",
        "lines_processed": lines_processed,
        "bytes_processed": bytes_processed,
        "lines_masked": masks_applied,
        "residual_pii_lines": residual_lines,
        "nfr_086c_enforced": residual_lines == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="In-stream database clone masking tool (NFR-086c)")
    parser.add_argument("--input", help="Source dump file path (if omitted, reads stdin)")
    parser.add_argument("--output", help="Target masked file path (if omitted, writes stdout)")
    args = parser.parse_args()

    # ExitStack closes only the files opened here - never stdin/stdout.
    with contextlib.ExitStack() as stack:
        in_f = stack.enter_context(open(args.input, encoding="utf-8")) if args.input else sys.stdin
        out_f = (
            stack.enter_context(open(args.output, "w", encoding="utf-8"))
            if args.output
            else sys.stdout
        )
        stats = process_stream(in_f, out_f)
        if args.output:
            print(
                f"[NFR-086c] Masking complete: {stats['lines_processed']} lines, {stats['lines_masked']} masked lines.",
                file=sys.stderr,
            )
    if not stats["nfr_086c_enforced"]:
        print(
            f"[NFR-086c] {stats['residual_pii_lines']} output line(s) still match a raw PII pattern.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
