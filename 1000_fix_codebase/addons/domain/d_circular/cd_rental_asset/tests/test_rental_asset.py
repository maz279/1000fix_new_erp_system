"""cd_rental_asset tests - P09-M03 (CD-M13-01)."""
import inspect
import unittest

from odoo.addons.cd_rental_asset.models.fix_rental_asset import (
    FixRentalDamage, FixRentalReservation)


class TestRentalAvailability(unittest.TestCase):
    def test_overlapping_reservations_refused(self):
        src = inspect.getsource(FixRentalReservation.action_reserve)
        self.assertIn("search_count", src)
        self.assertIn("already reserved", src)

    def test_events_published(self):
        src = inspect.getsource(FixRentalReservation)
        for event in ("rental.reserved", "rental.delivered", "rental.closed"):
            self.assertIn(event, src)

    def test_deposit_settlement(self):
        src = inspect.getsource(FixRentalReservation.action_close)
        self.assertIn("deposit_collected", src)
        self.assertIn("damage_total", src)
        self.assertIn("max", src)

    def test_damage_cost_validated(self):
        self.assertIn("negative",
                      inspect.getsource(FixRentalDamage._check_cost))

    def test_money_fields_are_monetary(self):
        import odoo.fields as f
        for fn in ("deposit_collected", "deposit_refunded", "daily_rate"):
            self.assertIsInstance(getattr(FixRentalReservation, fn), f.Monetary)


if __name__ == "__main__":
    unittest.main()
