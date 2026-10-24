"""payroll-engine service shell - re-export contract (CD-M56-01).

services/payroll-engine/src/payroll_engine.py is the service's public
contract over the shared kernel (libs/py/payroll_engine). Its basename
collides with the kernel package when libs/py is on sys.path, so it is
loaded here from its file under a unique module name. The tests assert
that the shell re-exports the kernel's own objects (no copies, no drift),
that __all__ is complete and resolvable, and that a calculation through
the shell is the kernel's calculation.
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from types import ModuleType

import pytest

pytestmark = [pytest.mark.financial, pytest.mark.tax]

_ROOT = Path(__file__).resolve().parents[3]  # codebase root (libs.py.*)
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from libs.py import payroll_engine as kernel
from libs.py.payroll_engine import beftn as kernel_beftn

_SHELL_PATH = Path(__file__).resolve().parents[1] / "src" / "payroll_engine.py"
_SHELL_NAME = "payroll_engine_service_shell"


def _load_shell() -> ModuleType:
    if _SHELL_NAME in sys.modules:
        return sys.modules[_SHELL_NAME]
    spec = importlib.util.spec_from_file_location(_SHELL_NAME, _SHELL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[_SHELL_NAME] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def shell() -> ModuleType:
    return _load_shell()


def test_shell_is_loaded_from_the_service_source(shell: ModuleType) -> None:
    assert Path(shell.__file__).resolve() == _SHELL_PATH
    assert shell.__name__ == _SHELL_NAME
    assert "L5 service shell" in (shell.__doc__ or "")


def test_every_exported_name_is_the_kernel_object(shell: ModuleType) -> None:
    assert len(shell.__all__) == len(set(shell.__all__)), "duplicate __all__ entries"
    for name in shell.__all__:
        assert hasattr(shell, name), f"__all__ lists unresolvable name {name!r}"
        assert getattr(shell, name) is getattr(kernel, name), name


def test_all_lists_everything_the_shell_imports(shell: ModuleType) -> None:
    public = {n for n in vars(shell) if not n.startswith("_")}
    assert public == set(shell.__all__)


def test_all_covers_every_public_kernel_function_and_class(shell: ModuleType) -> None:
    kernel_modules = {kernel.__name__, kernel_beftn.__name__}
    kernel_api = {
        name
        for name, obj in vars(kernel).items()
        if not name.startswith("_")
        and (inspect.isfunction(obj) or inspect.isclass(obj))
        and obj.__module__ in kernel_modules
    }
    assert kernel_api, "kernel exposes no public API?"
    missing = kernel_api - set(shell.__all__)
    assert not missing, f"kernel API not re-exported by the service shell: {sorted(missing)}"


def test_statutory_constants_are_shared_not_copied(shell: ModuleType) -> None:
    assert shell.TAX_SLABS is kernel.TAX_SLABS
    assert shell.TAX_FREE_THRESHOLDS is kernel.TAX_FREE_THRESHOLDS
    assert shell.MINIMUM_TAX_LOCATIONS is kernel.MINIMUM_TAX_LOCATIONS
    assert shell.RESIGNATION_BANDS is kernel.RESIGNATION_BANDS
    threshold, day_hours = shell.TAX_FREE_THRESHOLD, shell.STANDARD_DAY_HOURS
    assert threshold == Decimal("375000")
    assert shell.GRATUITY_MIN_YEARS_VESTING == 5
    assert (shell.GRATUITY_DAYS_UPTO_12Y, shell.GRATUITY_DAYS_ABOVE_12Y) == (30, 45)
    assert day_hours == Decimal("8")


def test_payslip_through_the_shell_equals_the_kernel(shell: ModuleType) -> None:
    def slip_input(mod: ModuleType) -> object:
        return mod.PayslipInput(
            employee_ref="E-SHELL",
            basic_monthly=Decimal("80000"),
            ot_hours=Decimal("4"),
            incentive=Decimal("2500"),
            pf_employee_pct=Decimal("10"),
            pf_employer_pct=Decimal("10"),
            taxpayer_category="female_senior",
            disabled_dependents=1,
            tax_location="dhaka_chattogram_city",
            allowable_investment=Decimal("150000"),
        )

    via_shell = shell.compute_payslip(slip_input(shell))
    via_kernel = kernel.compute_payslip(slip_input(kernel))
    assert via_shell == via_kernel
    assert isinstance(via_shell, kernel.PayslipResult)
    # OT 4h at 2 x (80,000/30/8) = 2,666.67; gross 85,166.67
    assert via_shell.overtime == Decimal("2666.67")
    assert via_shell.gross == Decimal("85166.67")
    assert sum(amount for _, amount in via_shell.lines) == via_shell.net


def test_statutory_helpers_through_the_shell(shell: ModuleType) -> None:
    assert shell.income_tax(Decimal("1075000")) == Decimal("90000.00")
    assert shell.investment_tax_rebate(Decimal("675000"), Decimal("100000")) == Decimal("15000.00")
    assert shell.provident_fund(Decimal("30000"), Decimal("10"), Decimal("10")) == {
        "employee": Decimal("3000.00"),
        "employer": Decimal("3000.00"),
    }
    assert shell.is_pf_deposit_compliant(date(2026, 12, 31), date(2027, 1, 15)) is True
    assert shell.completed_years(date(2014, 1, 1), date(2026, 1, 1)) == 12
    assert shell.gratuity(Decimal("30000"), date(2011, 1, 1), date(2026, 1, 1)) == Decimal(
        "495000.00"
    )
    assert shell.resignation_compensation(
        Decimal("30000"), date(2019, 1, 1), date(2026, 1, 1)
    ) == Decimal("105000.00")
    assert shell.retrenchment_compensation(
        Decimal("30000"), date(2022, 1, 1), date(2026, 1, 1)
    ) == Decimal("240000.00")
    assert shell.overtime_amount(Decimal("30000"), Decimal("10")) == Decimal("2500.00")
    assert shell.q2(Decimal("0.125")) == Decimal("0.13")
    assert shell.is_working_day(date(2026, 10, 2)) is False
    assert shell.beftn_settlement_date(datetime(2026, 10, 1, 16, 0)) == date(2026, 10, 4)
    assert shell.validate_routing_number("125272345") is True


def test_beftn_file_through_the_shell_equals_the_kernel(shell: ModuleType) -> None:
    header = shell.BeftnBatchHeader(
        company_name="1000FIX SERVICES LTD",
        company_id="1000FIXPAY",
        originating_routing="020260123",
        batch_number=3,
        settlement_date=date(2026, 10, 4),
    )
    entries = [
        shell.BeftnEntry(
            "EMP00001", "FARHANA AHMED", "225262531", "1001234567890", Decimal("63852.12")
        )
    ]
    stamp = datetime(2026, 10, 1, 9, 30)
    content = shell.generate_beftn_batch_file(header, entries, created_at=stamp)
    assert content == kernel.generate_beftn_batch_file(header, entries, created_at=stamp)
    lines = content.split("\r\n")[:-1]
    assert [line[0] for line in lines] == ["1", "5", "6", "8", "9"]
    assert all(len(line) == 128 for line in lines)
    assert lines[2][29:39] == "0006385212"
