# Tests for cd_device_registry (P04-M01) — device, warranty, ownership, history.
import pytest


class TestFixDevice:
    def test_model_exists(self):
        from addons.domain.a_service_delivery.cd_device_registry.models.fix_device import FixDevice
        assert FixDevice is not None

    def test_serial_unique_constraint(self):
        from addons.domain.a_service_delivery.cd_device_registry.models.fix_device import FixDevice
        assert hasattr(FixDevice, "_serial_unique")  # Odoo 19 models.Constraint attr

    def test_imei1_unique_constraint(self):
        from addons.domain.a_service_delivery.cd_device_registry.models.fix_device import FixDevice
        assert hasattr(FixDevice, "_imei1_unique")  # Odoo 19 models.Constraint attr

    def test_imei_format_constraint(self):
        from addons.domain.a_service_delivery.cd_device_registry.models.fix_device import FixDevice
        assert '_check_identity_format' in dir(FixDevice)

    def test_ownership_transfer_api(self):
        from addons.domain.a_service_delivery.cd_device_registry.models.fix_device import FixDevice
        assert 'action_transfer_ownership' in dir(FixDevice)

    def test_warranty_status_computed(self):
        from addons.domain.a_service_delivery.cd_device_registry.models.fix_device import FixDevice
        assert '_compute_warranty_status' in dir(FixDevice)

    def test_device_history_api(self):
        from addons.domain.a_service_delivery.cd_device_registry.models.fix_device import FixDevice
        assert 'add_history' in dir(FixDevice)

    def test_state_selection_present(self):
        from addons.domain.a_service_delivery.cd_device_registry.models.fix_device import FixDevice
        assert 'state' in dir(FixDevice)


class TestFixWarranty:
    def test_model_exists(self):
        from addons.domain.a_service_delivery.cd_device_registry.models.fix_warranty import FixWarranty
        assert FixWarranty is not None


class TestFixDeviceHistory:
    def test_model_exists(self):
        from addons.domain.a_service_delivery.cd_device_registry.models.fix_device_history import FixDeviceHistory
        assert FixDeviceHistory is not None
