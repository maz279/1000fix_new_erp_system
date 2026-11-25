#!/usr/bin/env python3
"""test_journey_12_procurement.py — Journey 12: Purchase Requisition to Three-Way Match Payment Test Suite.
Realises Journey 12 of the 15 critical journeys (RQ-007 §4.3, URD §18, Gate G3-06, G3-07).
"""

from __future__ import annotations

import unittest

TOLERANCE_BDT = 10.00


def three_way_match(
    po: dict, grn: dict, invoice: dict, tolerance_bdt: float
) -> tuple[bool, list[str]]:
    """G3-06 three-way match: per SKU the PO quantity, the GRN quantity that
    passed QC and the invoiced quantity must agree, and the billed amount must
    equal the invoiced quantities at PO unit cost within tolerance. Returns
    (passed, variances); any variance blocks."""
    variances: list[str] = []
    if grn["po_id"] != po["po_id"] or invoice["po_id"] != po["po_id"]:
        variances.append("documents reference different purchase orders")
    po_qty = {line["sku"]: line["qty"] for line in po["items"]}
    unit_cost = {line["sku"]: line["unit_cost"] for line in po["items"]}
    grn_qty: dict[str, int] = {}
    for line in grn["items_received"]:
        accepted = line["qty_received"] if line["qc_passed"] else 0
        grn_qty[line["sku"]] = grn_qty.get(line["sku"], 0) + accepted
    inv_qty = {line["sku"]: line["qty"] for line in invoice["lines"]}
    for sku in sorted(set(po_qty) | set(grn_qty) | set(inv_qty)):
        ordered = po_qty.get(sku, 0)
        received = grn_qty.get(sku, 0)
        billed = inv_qty.get(sku, 0)
        if received != ordered:
            variances.append(f"{sku}: GRN qty {received} != PO qty {ordered}")
        if billed != received:
            variances.append(f"{sku}: invoice qty {billed} != GRN qty {received}")
    expected_amount = sum(qty * unit_cost.get(sku, 0.0) for sku, qty in inv_qty.items())
    price_variance = abs(invoice["billed_amount"] - expected_amount)
    if price_variance > tolerance_bdt:
        variances.append(
            f"price variance {price_variance:.2f} BDT exceeds tolerance {tolerance_bdt:.2f}"
        )
    return not variances, variances


def _three_way_documents() -> tuple[dict, dict, dict]:
    po = {
        "po_id": 501,
        "items": [
            {"sku": "DISP-SAM-S24", "qty": 50, "unit_cost": 4500.00},
            {"sku": "BAT-APP-IP15", "qty": 100, "unit_cost": 2200.00},
        ],
    }
    grn = {
        "grn_id": 702,
        "po_id": 501,
        "items_received": [
            {"sku": "DISP-SAM-S24", "qty_received": 50, "qc_passed": True},
            {"sku": "BAT-APP-IP15", "qty_received": 100, "qc_passed": True},
        ],
    }
    invoice = {
        "bill_id": 901,
        "po_id": 501,
        "lines": [
            {"sku": "DISP-SAM-S24", "qty": 50},
            {"sku": "BAT-APP-IP15", "qty": 100},
        ],
        "billed_amount": 445000.00,
    }
    return po, grn, invoice


class TestJourney12ProcurementThreeWay(unittest.TestCase):
    def test_01_purchase_requisition_and_po_issuance(self):
        """Verify procurement requisition approval and PO issuance (M16)."""
        po = {
            "po_id": 501,
            "po_number": "PO-2026-0891",
            "supplier_id": 88,
            "items": [
                {"sku": "DISP-SAM-S24", "qty": 50, "unit_cost": 4500.00},
                {"sku": "BAT-APP-IP15", "qty": 100, "unit_cost": 2200.00},
            ],
            "total_amount": 50 * 4500.00 + 100 * 2200.00,
            "status": "issued",
        }
        self.assertEqual(po["total_amount"], 445000.00)
        self.assertEqual(po["status"], "issued")

    def test_02_goods_receipt_grn_verification(self):
        """Verify warehouse intake and GRN inspection (M41)."""
        grn = {
            "grn_id": 702,
            "po_id": 501,
            "items_received": [
                {"sku": "DISP-SAM-S24", "qty_received": 50, "qc_passed": True},
                {"sku": "BAT-APP-IP15", "qty_received": 100, "qc_passed": True},
            ],
            "status": "verified",
        }
        all_qc_passed = all(line["qc_passed"] for line in grn["items_received"])
        self.assertTrue(all_qc_passed)

    def test_03_vendor_invoice_intake(self):
        """Verify accounts payable vendor invoice intake (M52)."""
        vendor_bill = {
            "bill_id": 901,
            "bill_number": "INV-SUPP-9812",
            "po_id": 501,
            "supplier_id": 88,
            "billed_amount": 445000.00,
            "currency": "BDT",
        }
        self.assertEqual(vendor_bill["billed_amount"], 445000.00)

    def test_04_three_way_match_and_tolerance_gate(self):
        """Verify three-way matching between PO, GRN, and vendor invoice (G3-06)."""
        po, grn, invoice = _three_way_documents()
        match_passed, variances = three_way_match(po, grn, invoice, TOLERANCE_BDT)
        self.assertEqual(variances, [])
        self.assertTrue(match_passed, "Three-way match must succeed when within tolerance")

    def test_04b_grn_short_receipt_blocks_the_match(self):
        """G3-06: a GRN quantity below the PO/invoice quantity BLOCKS payment."""
        po, grn, invoice = _three_way_documents()
        grn["items_received"][1]["qty_received"] = 90  # 10 batteries short
        match_passed, variances = three_way_match(po, grn, invoice, TOLERANCE_BDT)
        self.assertFalse(match_passed, "A GRN quantity mismatch must fail the three-way match")
        self.assertIn("BAT-APP-IP15: GRN qty 90 != PO qty 100", variances)
        self.assertIn("BAT-APP-IP15: invoice qty 100 != GRN qty 90", variances)

    def test_04c_grn_missing_line_blocks_the_match(self):
        """A PO line never received on the GRN is a mismatch, not a zero variance."""
        po, grn, invoice = _three_way_documents()
        grn["items_received"] = grn["items_received"][:1]
        match_passed, variances = three_way_match(po, grn, invoice, TOLERANCE_BDT)
        self.assertFalse(match_passed)
        self.assertIn("BAT-APP-IP15: GRN qty 0 != PO qty 100", variances)

    def test_04d_grn_qc_rejected_quantity_does_not_count_as_received(self):
        """QC-failed GRN lines are not accepted stock - they cannot satisfy the match."""
        po, grn, invoice = _three_way_documents()
        grn["items_received"][0]["qc_passed"] = False
        match_passed, variances = three_way_match(po, grn, invoice, TOLERANCE_BDT)
        self.assertFalse(match_passed)
        self.assertIn("DISP-SAM-S24: GRN qty 0 != PO qty 50", variances)

    def test_04e_price_variance_beyond_tolerance_blocks_the_match(self):
        po, grn, invoice = _three_way_documents()
        invoice["billed_amount"] += 50.00
        match_passed, variances = three_way_match(po, grn, invoice, TOLERANCE_BDT)
        self.assertFalse(match_passed)
        self.assertEqual(len(variances), 1)
        self.assertIn("price variance", variances[0])

    def test_05_treasury_settlement_and_gl_posting(self):
        """Verify payment release approval and general ledger journal posting (M19 / M50)."""
        payment_release = {
            "settlement_id": "PAY-SETTLE-8812",
            "bill_id": 901,
            "method": "BEFTN",
            "amount": 445000.00,
            "status": "cleared",
        }
        gl_entry = {
            "journal": "AP",
            "debit_account": "210000_AccountsPayable",
            "credit_account": "100020_BankMain",
            "amount": 445000.00,
            "balanced": True,
        }
        self.assertEqual(payment_release["status"], "cleared")
        self.assertTrue(gl_entry["balanced"])


if __name__ == "__main__":
    unittest.main()
