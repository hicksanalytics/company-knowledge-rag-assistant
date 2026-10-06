import unittest
from decimal import Decimal

from src.policy_tools import get_invoice_approvers


class InvoiceApprovalTests(unittest.TestCase):
    def test_manager_threshold(self):
        result = get_invoice_approvers(Decimal("5000"))
        self.assertEqual(
            result["approvers"],
            ["department manager"],
        )

    def test_director_threshold(self):
        result = get_invoice_approvers(Decimal("12000"))
        self.assertEqual(
            result["approvers"],
            ["department manager", "director"],
        )

    def test_vice_president_threshold(self):
        result = get_invoice_approvers(Decimal("30000"))
        self.assertEqual(
            result["approvers"],
            [
                "department manager",
                "director",
                "vice president",
            ],
        )


if __name__ == "__main__":
    unittest.main()