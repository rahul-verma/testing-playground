import datetime
import unittest
from unittest.mock import Mock


# ==========================
# Actual SUT Code
# ==========================

class OrderNotFound(Exception):
    pass


class Order:
    def __init__(self, order_id: str, status: str, expected_delivery: datetime.date):
        self.order_id = order_id
        self.status = status
        self.expected_delivery = expected_delivery


class OrderService:
    """
    In the real system this would call an external order backend.
    For tests, we don't want that → we'll use a stub.
    """
    def get_order(self, order_id: str) -> Order:
        raise NotImplementedError


class EscalationClient:
    """
    In the real system this might push a task to a human agent queue.
    For tests, we want to verify how it's used → we'll use a mock.
    """
    def escalate(self, order_id: str, reason: str) -> None:
        raise NotImplementedError


class OrderStatusHandler:
    """
    Small domain object that coordinates:
      - retrieving the order
      - deciding what to tell the user
      - deciding when to escalate to a human
    """

    DELAY_THRESHOLD_DAYS = 3

    def __init__(self, order_service: OrderService, escalation_client: EscalationClient):
        self.order_service = order_service
        self.escalation_client = escalation_client

    def handle_where_is_my_order(self, order_id: str, today: datetime.date) -> str:
        try:
            order = self.order_service.get_order(order_id)
        except OrderNotFound:
            # Business rule: unknown order → escalate.
            self.escalation_client.escalate(order_id, reason="ORDER_NOT_FOUND")
            return (
                "I couldn't immediately find your order. "
                "I've escalated this to a human agent who will investigate."
            )

        # Known order:
        if order.status == "SHIPPED":
            return f"Your order {order.order_id} has been shipped and is on its way."

        # Check for delay
        if order.expected_delivery < today - datetime.timedelta(days=self.DELAY_THRESHOLD_DAYS):
            # delayed beyond threshold → escalate
            self.escalation_client.escalate(order.order_id, reason="DELIVERY_DELAY")
            return (
                f"Your order {order.order_id} seems delayed. "
                "I've escalated this to a human agent to check with the carrier."
            )

        # Not shipped, but not delayed beyond threshold
        return f"Your order {order.order_id} is being prepared and should arrive soon."


# ==========================
# Test doubles for the exercise
# ==========================

class StubOrderService(OrderService):
    """
    Simple stub:
      - does NO real external calls
      - returns pre-configured orders from an in-memory dict
      - raises OrderNotFound if order_id is unknown
    """

    def __init__(self, orders_by_id):
        self._orders_by_id = dict(orders_by_id)

    def get_order(self, order_id: str) -> Order:
        try:
            return self._orders_by_id[order_id]
        except KeyError:
            raise OrderNotFound(order_id)


# ==========================
# Tests (exercise)
# ==========================

class TestOrderStatusHandler(unittest.TestCase):

    def setUp(self):
        # Common "today" date for deterministic tests
        self.today = datetime.date(2025, 5, 1)

    # --- PART 1: Using a STUB for OrderService ---

    def test_shipped_order_uses_stubbed_data_and_does_not_escalate(self):
        """
        Goal:
          - Use StubOrderService to control the order data.
          - Assert that the response message is correct.
          - Assert that no escalation happens.

        This shows a STUB:
          - We pre-configure what get_order() returns.
          - We do NOT assert on how the stub was called.
        """

        # configure a stub with an order that is SHIPPED
        shipped_order = Order(
            order_id="ORDER-123",
            status="SHIPPED",
            expected_delivery=self.today  # doesn't really matter for shipped
        )
        order_service_stub = StubOrderService({
            "ORDER-123": shipped_order
        })

        # create a mock for the escalation client (we still care about its interactions)
        escalation_mock = Mock(spec=EscalationClient)

        handler = OrderStatusHandler(order_service_stub, escalation_mock)

        # call handle_where_is_my_order and capture the response
        response = handler.handle_where_is_my_order("ORDER-123", today=self.today)

        # assert that the response mentions the order has been shipped
        self.assertIn("has been shipped", response)
        self.assertIn("ORDER-123", response)

        # assert that escalation_client.escalate was NOT called
        escalation_mock.escalate.assert_not_called()

    # --- PART 2: Using a MOCK for EscalationClient ---

    def test_delayed_order_triggers_escalation_mock(self):
        """
        Goal:
          - Use a stubbed order that is delayed beyond the threshold.
          - Use a mock for EscalationClient to verify:
              * It was called
              * It was called with the correct order_id and reason.

        This shows a MOCK:
          - We care about the interaction contract: which method, which args.
        """

        delayed_delivery_date = self.today - datetime.timedelta(days=10)
        delayed_order = Order(
            order_id="ORDER-999",
            status="PROCESSING",
            expected_delivery=delayed_delivery_date
        )

        order_service_stub = StubOrderService({
            "ORDER-999": delayed_order
        })

        # HERE the mock is central: we verify how it's used.
        escalation_mock = Mock(spec=EscalationClient)

        handler = OrderStatusHandler(order_service_stub, escalation_mock)

        response = handler.handle_where_is_my_order("ORDER-999", today=self.today)

        # First, assert the user-facing response mentions escalation
        self.assertIn("seems delayed", response)
        self.assertIn("escalated", response)

        # Now use MOCK-style verification: interaction is part of the behavior
        escalation_mock.escalate.assert_called_once_with("ORDER-999", reason="DELIVERY_DELAY")

    def test_unknown_order_triggers_escalation_mock_with_order_not_found_reason(self):
        """
        Second mock-based test:
          - No order in the stub for ORDER-404 → OrderNotFound.
          - Handler should escalate with reason ORDER_NOT_FOUND.
        """

        order_service_stub = StubOrderService({})  # empty

        escalation_mock = Mock(spec=EscalationClient)
        handler = OrderStatusHandler(order_service_stub, escalation_mock)

        response = handler.handle_where_is_my_order("ORDER-404", today=self.today)

        self.assertIn("couldn't immediately find your order", response)
        escalation_mock.escalate.assert_called_once_with("ORDER-4014", reason="ORDER_NOT_FOUND")


if __name__ == "__main__":
    unittest.main()
