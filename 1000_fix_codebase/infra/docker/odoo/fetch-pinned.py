#!/usr/bin/env python3
"""Build-time only: download an artefact pinned in tooling/versions.lock.

The URL and the SHA256 are both read from versions.lock (by key), so the image
shares one pin with the rest of the programme. The bytes are verified BEFORE
they are written; a mismatch fails the image build (never "re-download and
hope" - re-pin through a reviewed change).

  fetch-pinned.py <versions.lock> <URL_KEY> <SHA256_KEY> <dest-file>

Used for the wkhtmltopdf .deb (WORKSTATION_WKHTMLTOPDF_CONTAINER_BOOKWORM_*).
"""

from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path


def lock_values(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            out[key.strip()] = value.split("#", 1)[0].strip().strip('"')
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__, file=sys.stderr)
        return 2
    lock_file, url_key, sha_key, dest = argv
    lock = lock_values(Path(lock_file))
    url, want = lock[url_key], lock[sha_key].lower()
    if not url.startswith("https://"):
        print(f"fetch-pinned: refusing non-https URL {url}", file=sys.stderr)
        return 1
    with urllib.request.urlopen(url, timeout=180) as resp:  # noqa: S310 - https, hash-verified below
        blob = resp.read()
    got = hashlib.sha256(blob).hexdigest()
    if got != want:
        print(f"fetch-pinned: SHA256 mismatch for {url}: {got} != {want}", file=sys.stderr)
        return 1
    Path(dest).parent.mkdir(parents=True, exist_ok=True)
    Path(dest).write_bytes(blob)
    print(f"fetch-pinned: {url} (sha256 {got[:12]}..., {len(blob)} bytes) -> {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
