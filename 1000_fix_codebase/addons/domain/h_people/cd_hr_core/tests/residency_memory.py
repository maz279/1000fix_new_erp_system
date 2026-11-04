# An in-memory stand-in for the residency client (libs/py/fix_residency), for
# tests: values round-trip, every call is recorded, and the store can be taken
# "down". The real local store answers synthetic values only (DE-12), so a test
# that needs the value back stands this in through `install(monkeypatch)`.
#
# Other packages whose tests write an employee NID may reuse it:
#     from odoo.addons.cd_hr_core.tests.residency_memory import install
#     store = install(monkeypatch)
from libs.py import fix_residency


class MemoryResidency:
    def __init__(self):
        self.data = {}
        self.calls = []
        self.down = False

    def _call(self, op, key):
        self.calls.append((op, key))
        if self.down:
            raise fix_residency.ResidencyError("residency service unreachable (test: down)")

    def put(self, key, value):
        self._call("put", key)
        self.data[key] = value
        return {"stored": True, "value_kind": "memory", "key": key}

    def get(self, key):
        self._call("get", key)
        return self.data.get(key, "")

    def erase(self, key):
        self._call("erase", key)
        self.data.pop(key, None)
        return {"erased": True, "key": key}

    def health(self):
        return {"status": "UP", "mode": "memory"}

    def ops(self, op):
        return [key for name, key in self.calls if name == op]


def install(monkeypatch):
    """Stand a fresh in-memory store in for get_client() and return it."""
    store = MemoryResidency()
    monkeypatch.setattr(fix_residency, "get_client", lambda: store)
    return store
