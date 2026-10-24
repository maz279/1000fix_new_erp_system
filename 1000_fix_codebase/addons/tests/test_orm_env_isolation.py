"""Self-test of the live-ORM `odoo_env` environment (addons/conftest.py).

The fixture is the foundation of every ORM-level test, so its two promises
are verified directly: a test sees its own writes, and nothing it writes
survives the test (rollback isolation).
"""

MARKER = "odoo-env-fixture-isolation-probe"


def test_writes_are_visible_inside_the_test(odoo_env):
    partner = odoo_env["res.partner"].create({"name": MARKER})
    assert partner.id
    assert odoo_env["res.partner"].search_count([("name", "=", MARKER)]) == 1


def test_writes_do_not_survive_the_test(odoo_env):
    # Runs after the test above (file order): its partner must be gone.
    assert odoo_env["res.partner"].search_count([("name", "=", MARKER)]) == 0


def test_commit_is_neutralised(odoo_env):
    odoo_env["res.partner"].create({"name": MARKER + "-commit"})
    odoo_env.cr.commit()  # must NOT persist
    odoo_env.cr.rollback()
    assert odoo_env["res.partner"].search_count([("name", "=", MARKER + "-commit")]) == 0


def test_teardown_rolls_back_despite_an_unflushable_pending_write(odoo_registry):
    """Regression (R01 re-audit 2026-10-22): a test that left an invalid
    pending write made the teardown's flushing invalidate_all() raise before
    cr.rollback(), leaking an open transaction whose row locks stalled every
    other run on fix_test. The fixture's teardown must survive it."""
    import sys
    from pathlib import Path

    import pytest
    from odoo import SUPERUSER_ID, api

    conftest_file = str(Path(__file__).resolve().parents[1] / "conftest.py")
    conftest = next(  # --import-mode=importlib: not importable by name
        m for m in list(sys.modules.values()) if getattr(m, "__file__", None) == conftest_file
    )

    def broken_env():
        cr = odoo_registry.cursor()
        env = api.Environment(cr, SUPERUSER_ID, {})
        env.ref("base.BDT").name = None  # NOT NULL column, plain stored field: fails at flush
        return env

    # The scenario is real: flushing that pending write fails.
    env = broken_env()
    with pytest.raises(Exception):  # noqa: B017 - psycopg2 NotNullViolation via the ORM
        env.invalidate_all()
    env.cr.rollback()
    env.cr.close()

    # The fixture's teardown discards it and still rolls back and closes.
    env = broken_env()
    conftest._discard_env(env)
    assert env.cr.closed
