# M58-F4 (A09 ERP audit 2026-11-23): the candidate's government identifiers
# (NID, birth registration, passport) live in the Bangladesh-resident store,
# as the employees' do since M21-A6. The row keeps only the keyed hash (the
# duplicate check), a pointer and the last four digits.
#
# The store stands in memory (cd_hr_core/tests/residency_memory): the real
# local store answers synthetic values only, so a test that needs the value
# back installs the double.
import pytest
from odoo.addons.cd_hr_core.tests.residency_memory import install
from odoo.addons.cd_talent.tests.test_a09_talent_controls import (
    _accept,
    _candidate,
    _ready_to_hire,
    _requisition,
    make_x,
)
from odoo.exceptions import AccessError, ValidationError

NID = "1995123456789"  # 13 digits
BRN = "20001234567890123"  # 17 digits
PASSPORT = "BX1234567"
SEQ = [0]


@pytest.fixture
def x(odoo_env):
    return make_x(odoo_env)


def _column(env, cand, name):
    """What the candidate's row actually holds in `name` (bypasses the ORM)."""
    env.cr.execute("SELECT %s FROM fix_candidate WHERE id = %%s" % name, (cand.id,))
    return env.cr.fetchone()[0]


def test_the_candidate_nid_never_lands_in_the_regional_database(x, monkeypatch):
    """A09 M58-F4: the verifier could read `nid_number` in clear. The row now
    keeps a pointer, a keyed hash and the last four digits; the value is in the
    store, and every read of it is logged."""
    store = install(monkeypatch)
    cand = _candidate(x, _requisition(x), nid_number=NID)
    ref = cand.sudo().nid_ref
    assert ref
    # nothing clear in the row, and no column holds the value either
    assert not _column(x.env, cand, "nid_number")
    assert NID not in (cand.sudo().nid_hash or "")
    assert store.data == {"candidate nid:%s" % ref: NID}
    # last four digits for display; the rest is never shown
    assert cand.sudo().identity_last4 == {"nid_number": "6789"}
    assert cand.nid_number_masked == "***6789"
    # a role that may read the candidate but not the value
    with pytest.raises(AccessError):
        cand.with_user(x.approver).read(["nid_number"])
    assert cand.with_user(x.approver).nid_number_masked == "***6789"
    # a reader reads it back through the store - and the read is logged
    x.env.invalidate_all()
    assert cand.with_user(x.verifier).nid_number == NID
    assert any(op == "get" and key.endswith(ref) for op, key in store.calls)
    log = (
        x.env["fix.hr.identity.access.log"]
        .sudo()
        .search([("record_model", "=", "fix.candidate"), ("record_id", "=", cand.id)])
    )
    assert log and set(log.mapped("field_name")) == {"nid_number"}
    assert NID not in " ".join(log.mapped("purpose") or [])


def test_the_same_nid_is_still_caught_by_its_hash(x, monkeypatch):
    """The duplicate check reads no value at all: the keyed hash is enough, and
    it is the same hash M21 stores on an employee."""
    install(monkeypatch)
    req = _requisition(x)
    first = _candidate(x, req, nid_number=NID)
    with pytest.raises(ValidationError, match="same email, phone or NID"):
        _candidate(x, req, nid_number=NID)
    # a different requisition is not a duplicate application
    other = _candidate(x, _requisition(x), nid_number=NID)
    assert other.sudo().nid_hash == first.sudo().nid_hash
    # the plain birth registration and passport are held the same way
    brn = _candidate(x, req, birth_reg_number=BRN)
    assert brn.sudo().birth_reg_ref and not _column(x.env, brn, "birth_reg_number")
    with pytest.raises(ValidationError, match="17 digits"):
        _candidate(x, req, birth_reg_number="12345")


def test_the_hire_copies_the_identifiers_and_releases_the_candidate(x, monkeypatch):
    """M58-F4 at the hire: each identifier the store serves back intact is
    written to the employee master (into M21's store) and the candidate's copy
    is erased; the keyed hash stays so the same person is never hired twice."""
    store = install(monkeypatch)
    req = _requisition(x)
    cand, offer = _ready_to_hire(
        x, req, nid_number=NID, birth_reg_number=BRN, passport_number=PASSPORT
    )
    nid_hash = cand.sudo().nid_hash
    _accept(x, offer)
    assert cand.state == "hired"
    emp = cand.employee_id.sudo()
    # the employee master holds them, in M21's store, under its own pointers
    assert emp.nid_number == NID and emp.birth_reg_number == BRN
    assert emp.passport_number == PASSPORT
    assert emp.nid_hash == nid_hash  # the same keyed hash: one person, one NID
    assert not [key for key in store.data if key.startswith("candidate ")]
    assert NID in store.data.values() and BRN in store.data.values()
    # the candidate keeps only the hash: a second application is still caught
    assert not cand.sudo().nid_ref and not _column(x.env, cand, "nid_number")
    assert cand.sudo().nid_hash == nid_hash
    with pytest.raises(ValidationError, match="same email, phone or NID"):
        _candidate(x, req, nid_number=NID)


def test_the_erasure_cron_removes_the_value_from_the_store(x, monkeypatch):
    """M58-F3/F4: anonymising a candidate now reaches the store, not just the
    row. A store that is down leaves the value for the next run and does not
    stop the record from being anonymised."""
    store = install(monkeypatch)
    req = _requisition(x)
    cand = _candidate(x, req, nid_number=NID)
    assert store.data
    cand.with_user(x.recruiter).action_reject(reason="Not selected")
    cand.sudo()._guarded().write({"retention_until": x.today.replace(year=x.today.year - 1)})
    # the store is down: the record is still anonymised, the value stays
    store.down = True
    assert x.env["fix.candidate"].cron_erase_expired_candidates() == 1
    assert cand.sudo().erased and store.data
    # the next run reaches the store once it is back
    store.down = False
    cand.sudo()._guarded().write({"erased": False, "retention_until": x.today.replace(year=2020)})
    x.env["fix.candidate"].cron_erase_expired_candidates()
    assert not store.data
    assert not cand.sudo().nid_ref and not cand.sudo().nid_hash


def test_the_upgrade_moves_a_value_left_in_the_clear_column(x, monkeypatch):
    """The post-migrate moves the rows written before this change. Idempotent;
    a row it cannot move keeps its value for the next run."""
    store = install(monkeypatch)
    cand = _candidate(x, _requisition(x))
    # a pre-residency row: the value in the clear column, no pointer, no hash
    x.env.cr.execute(
        "UPDATE fix_candidate SET nid_number = %s, nid_ref = NULL, nid_hash = NULL, "
        "identity_last4 = NULL WHERE id = %s",
        (NID, cand.id),
    )
    cand.invalidate_recordset()
    result = x.env["fix.candidate"].sudo()._fix_identity_move_clear_values()
    assert result["moved"] == 1 and result["left"] == 0
    cand.invalidate_recordset()
    assert not _column(x.env, cand, "nid_number")
    assert cand.sudo().nid_ref and cand.sudo().nid_hash
    assert store.data == {"candidate nid:%s" % cand.sudo().nid_ref: NID}
    assert cand.sudo().identity_last4 == {"nid_number": "6789"}
    # running it again changes nothing
    again = x.env["fix.candidate"].sudo()._fix_identity_move_clear_values()
    assert again == {"moved": 0, "dropped_on_hired": 0, "left": 0}


def test_the_daily_cron_moves_a_row_the_upgrade_could_not(x, monkeypatch):
    """A store that is down during the upgrade leaves the value in the clear
    column - never lost, and the daily cron moves it when the store is back."""
    store = install(monkeypatch)
    cron = x.env.ref("cd_talent.cron_talent_identity_move")
    assert cron.active and cron.model_id.model == "fix.candidate"
    assert cron.code.strip() == "model.cron_identity_move_clear_values()"
    cand = _candidate(x, _requisition(x))
    x.env.cr.execute(
        "UPDATE fix_candidate SET nid_number = %s, nid_ref = NULL, nid_hash = NULL, "
        "identity_last4 = NULL WHERE id = %s",
        (NID, cand.id),
    )
    cand.invalidate_recordset()
    store.down = True
    assert x.env["fix.candidate"].sudo()._fix_identity_move_clear_values()["left"] == 1
    cand.invalidate_recordset()
    assert _column(x.env, cand, "nid_number") == NID  # the value is still there
    store.down = False
    moved = x.env["fix.candidate"].sudo().cron_identity_move_clear_values()
    assert moved["moved"] == 1, moved
    cand.invalidate_recordset()
    assert not _column(x.env, cand, "nid_number")
    assert cand.sudo().nid_ref and store.data == {"candidate nid:%s" % cand.sudo().nid_ref: NID}
