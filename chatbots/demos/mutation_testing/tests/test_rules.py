import sys, os
mydir = os.path.dirname(__file__)
print(mydir)
sys.path.append(mydir + "/../src")  # Adjust path for imports if necessary

import unittest
from datetime import date
from refunds.rules import is_refund_eligible, Decision


class Dummy:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class RefundRulesTests(unittest.TestCase):

    def test_approved_basic_case(self):
        order = Dummy(
            purchase_date=date(2025, 1, 1),
            amount=100,
            product_type="Physical",
        )
        customer = Dummy(region="DE", is_fraud_flagged=False)
        policy = Dummy(max_refund_days=30, allows_digital_refunds=False)

        decision = is_refund_eligible(order, customer, policy, date(2025, 1, 15))
        self.assertEqual(Decision("APPROVED", "Eligible for refund"), decision)
        
    def test_approved_outside_refund_window_boundary_1(self):
        order = Dummy(
            purchase_date=date(2025, 1, 1),
            amount=100,
            product_type="Physical",
        )
        customer = Dummy(region="DE", is_fraud_flagged=False)
        policy = Dummy(max_refund_days=30, allows_digital_refunds=False)

        decision = is_refund_eligible(order, customer, policy, date(2025, 1, 31))
        self.assertEqual(Decision("APPROVED", "Eligible for refund"), decision)

    def test_denied_outside_refund_window_boundary_2(self):
        order = Dummy(
            purchase_date=date(2025, 1, 1),
            amount=100,
            product_type="Physical",
        )
        customer = Dummy(region="DE", is_fraud_flagged=False)
        policy = Dummy(max_refund_days=30, allows_digital_refunds=False)

        decision = is_refund_eligible(order, customer, policy, date(2025, 2, 1))
        self.assertEqual(Decision("DENIED", "Outside refund window"), decision)


if __name__ == "__main__":
    unittest.main()
