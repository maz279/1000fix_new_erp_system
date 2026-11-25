"""GV-009: verify_archive_integrity.py hashes and opens the archives it can actually reach;
an unmounted store, encrypted archives, the DCM-25 human read and the DCM-18 retention
trigger are UNMEASURED (so no class and no verdict is ever PASS on its word), and a
missing / corrupt / mismatched archive is FAIL. Only temp files are touched."""

from __future__ import annotations

import gzip
import hashlib
import importlib.util
import io
import json
import os
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "tooling" / "scripts" / "verify_archive_integrity.py"


def _load():
    spec = importlib.util.spec_from_file_location("verify_archive_integrity_ut", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mod = _load()
CLASSES = {c["class_id"]: c for c in mod.ARCHIVE_CLASSES}


def _store_path(root: Path, class_id: str) -> Path:
    path = root / mod.store_relative(CLASSES[class_id]["archive_path"])
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _write_fixity(path: Path, digest: str | None = None) -> None:
    digest = digest or hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_name(path.name + ".sha256").write_bytes(f"{digest}  {path.name}\n".encode())


def _zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in members.items():
            zf.writestr(name, data)


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        self._env = os.environ.pop(mod.ARCHIVE_ROOT_ENV, None)
        self.addCleanup(self._restore_env)

    def _restore_env(self):
        if self._env is not None:
            os.environ[mod.ARCHIVE_ROOT_ENV] = self._env

    @staticmethod
    def cls(ev, class_id):
        return next(c for c in ev["archive_classes"] if c["archive_class_id"] == class_id)


class TestArchiveIntegrity(Base):
    def test_unmounted_store_is_unmeasured_never_pass(self):
        ev = mod.build_evidence(None)
        self.assertFalse(ev["archive_store_mounted"])
        self.assertEqual(ev["total_archive_classes"], 8)
        self.assertEqual(ev["total_archive_classes_tested"], 0)
        self.assertIsNone(ev["restorability_success_rate"])
        self.assertIsNone(ev["total_measured_archive_bytes"])
        for c in ev["archive_classes"]:
            self.assertEqual(c["checks"]["archive_present"]["status"], "UNMEASURED")
            self.assertEqual(c["verification_status"], "INCOMPLETE")
            self.assertIsNone(c["sha256_checksum"])
            self.assertIsNone(c["retention_governance"]["statutory_disposal_date"])
        self.assertEqual(ev["verdict"], "INCOMPLETE")
        self.assertEqual(mod.exit_code_for(ev["verdict"]), 2)

    def test_readable_zip_with_fixity_still_not_pass_without_human_read(self):
        path = _store_path(self.root, "ARCH-CL-02")
        _zip(path, {"sheets/dhanmondi_2024_service_log.xlsx": b"x" * 100, "b.csv": b"1,2\n"})
        _write_fixity(path)
        ev = mod.build_evidence(self.root)
        c = self.cls(ev, "ARCH-CL-02")
        for name in ("archive_present", "checksum", "machine_restore_drill"):
            self.assertEqual(c["checks"][name]["status"], "PASS", c["checks"][name])
        self.assertEqual(c["checks"]["human_sample_read"]["status"], "UNMEASURED")
        self.assertEqual(c["verification_status"], "INCOMPLETE")
        self.assertEqual(c["sha256_checksum"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(c["measured_size_bytes"], path.stat().st_size)
        self.assertEqual(c["restorability_drill"]["records_read_and_verified"], 2)
        # every other class is missing from the mounted store -> FAIL
        self.assertEqual(self.cls(ev, "ARCH-CL-08")["checks"]["archive_present"]["status"], "FAIL")
        self.assertEqual(ev["verdict"], "FAIL")
        self.assertEqual(mod.exit_code_for(ev["verdict"]), 1)

    def test_checksum_mismatch_fails(self):
        path = _store_path(self.root, "ARCH-CL-02")
        _zip(path, {"dhanmondi_2024_service_log.xlsx": b"data"})
        _write_fixity(path, "0" * 64)
        c = self.cls(mod.build_evidence(self.root), "ARCH-CL-02")
        self.assertEqual(c["checks"]["checksum"]["status"], "FAIL")
        self.assertEqual(c["verification_status"], "FAIL")

    def test_no_fixity_record_is_unmeasured(self):
        path = _store_path(self.root, "ARCH-CL-02")
        _zip(path, {"dhanmondi_2024_service_log.xlsx": b"data"})
        c = self.cls(mod.build_evidence(self.root), "ARCH-CL-02")
        self.assertEqual(c["checks"]["checksum"]["status"], "UNMEASURED")
        self.assertIsNotNone(c["sha256_checksum"])

    def test_corrupt_zip_and_missing_sample_fail(self):
        path = _store_path(self.root, "ARCH-CL-08")
        path.write_bytes(b"not a zip at all")
        c = self.cls(mod.build_evidence(self.root), "ARCH-CL-08")
        self.assertEqual(c["checks"]["machine_restore_drill"]["status"], "FAIL")
        _zip(path, {"other.pdf": b"%PDF"})
        c = self.cls(mod.build_evidence(self.root), "ARCH-CL-08")
        self.assertEqual(c["checks"]["machine_restore_drill"]["status"], "FAIL")
        self.assertIn("MISSING", c["checks"]["machine_restore_drill"]["detail"])

    def test_gzip_drill_and_encrypted_archive(self):
        gz = _store_path(self.root, "ARCH-CL-06")
        with gzip.open(gz, "wb") as fh:
            fh.write(b"sku,name\nA,1\nB,2\n")
        enc = _store_path(self.root, "ARCH-CL-01")
        enc.write_bytes(os.urandom(64))
        ev = mod.build_evidence(self.root)
        self.assertEqual(
            self.cls(ev, "ARCH-CL-06")["checks"]["machine_restore_drill"]["status"], "PASS"
        )
        self.assertEqual(
            self.cls(ev, "ARCH-CL-06")["restorability_drill"]["records_read_and_verified"], 3
        )
        enc_drill = self.cls(ev, "ARCH-CL-01")["checks"]["machine_restore_drill"]
        self.assertEqual(enc_drill["status"], "UNMEASURED")
        self.assertIn("encrypted", enc_drill["detail"])
        self.assertEqual(ev["total_archive_classes_tested"], 1)
        self.assertEqual(ev["restorability_success_rate"], "100.0%")

    def test_tar_drill_reads_members(self):
        path = self.root / "bundle.tar.gz"
        with tarfile.open(path, "w:gz") as tf:
            data = b"hello"
            info = tarfile.TarInfo("dir/sample.txt")
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
        ac = {
            "archive_format": "tar.gz",
            "archive_path": "x/bundle.tar.gz",
            "sample_table": "sample.txt",
        }
        check, count = mod.restore_drill(path, ac)
        self.assertEqual(check["status"], "PASS")
        self.assertEqual(count, 1)

    def test_configured_but_unmounted_root_is_unmeasured(self):
        ev = mod.build_evidence(self.root / "does-not-exist")
        self.assertFalse(ev["archive_store_mounted"])
        self.assertEqual(ev["verdict"], "INCOMPLETE")


class TestOutputs(Base):
    def test_main_writes_only_temp_outputs(self):
        out = self.root / "out"
        originals = (mod.EVIDENCE_DIR, mod.DOCS_DIR)
        mod.EVIDENCE_DIR, mod.DOCS_DIR = out / "evidence", out / "docs"
        try:
            code = mod.main([])
        finally:
            mod.EVIDENCE_DIR, mod.DOCS_DIR = originals
        self.assertEqual(code, 2)
        ev = json.loads((out / "evidence" / mod.EVIDENCE_NAME).read_text(encoding="utf-8"))
        self.assertEqual(ev["overall_status"], "INCOMPLETE")
        md = (out / "docs" / mod.MD_NAME).read_text(encoding="utf-8")
        self.assertNotIn("8 / 8 PASS", md)
        self.assertIn("UNMEASURED", md)


if __name__ == "__main__":
    unittest.main()
