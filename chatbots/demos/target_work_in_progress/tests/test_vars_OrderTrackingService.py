# tests/test_recent_failed_ai_attempts_bva.py
import pytest

from order_tracking.contract import (
    Channel,
    CustomerAction,
    CustomerContext,
    InvalidRecentFailedAIAttemptsException,
    Order,
    OrderStatus,
    PolicyConfig,
)
from order_tracking.provider import OrderTrackingStrategyService


CFG = PolicyConfig()


# Avoid flaky dynamic outage by injecting a health checker that never fails.
class NeverFailHealthCheck:
    def ensure_available(self) -> None:
        return


def _valid_ctx_with_attempts(attempts):
    return CustomerContext(
        action=CustomerAction.TRACK_ORDER,
        customer_id="CUST-123456",
        country="US",
        is_vip=False,
        authenticated=True,
        channel=Channel.WEBCHAT,
        orders=[
            Order(
                order_id="ORD-12345678",
                total_amount=999.99,
                item_count=1,
                status=OrderStatus.SHIPPED,
                is_flagged_fraud_risk=False,
                has_open_dispute=False,
            )
        ],
        recent_failed_ai_attempts=attempts,  # variable under test
        ai_confidence=0.90,
    )


@pytest.mark.parametrize(
    # Header line (columns)
    "case_id,recent_failed_ai_attempts,expect_exception,expected_exception_type",
    [
        # -----------------------
        # Valid partitions + BVA
        # -----------------------
        ("BVA_min", CFG.min_failed_ai_attempts, False, None),  # 0
        ("BVA_min_plus_1", CFG.min_failed_ai_attempts + 1, False, None),  # 1
        ("BVA_threshold_minus_1", CFG.many_recent_ai_failures_threshold - 1, False, None),  # 1
        ("BVA_threshold", CFG.many_recent_ai_failures_threshold, False, None),  # 2
        ("BVA_threshold_plus_1", CFG.many_recent_ai_failures_threshold + 1, False, None),  # 3
        ("BVA_max_minus_1", CFG.max_failed_ai_attempts - 1, False, None),  # 4
        ("BVA_max", CFG.max_failed_ai_attempts, False, None),  # 5

        # -----------------------
        # Invalid partitions (ECP)
        # -----------------------
        ("ECP_negative", -1, True, InvalidRecentFailedAIAttemptsException),
        ("ECP_above_max", CFG.max_failed_ai_attempts + 1, True, InvalidRecentFailedAIAttemptsException),

        # Non-integer / non-numeric partitions (type robustness)
        # Current validator compares ints directly, so wrong types raise TypeError.
        ("ECP_none", None, True, TypeError),
        ("ECP_float", 1.0, True, TypeError),
        ("ECP_float_fraction", 1.5, True, TypeError),
        ("ECP_numeric_string", "2", True, TypeError),
        ("ECP_alpha_string", "two", True, TypeError),
        ("ECP_empty_string", "", True, TypeError),
    ],
)
def test_recent_failed_ai_attempts_bva_ecp(case_id, recent_failed_ai_attempts, expect_exception, expected_exception_type):
    service = OrderTrackingStrategyService(cfg=CFG, health=NeverFailHealthCheck())
    ctx = _valid_ctx_with_attempts(recent_failed_ai_attempts)

    if expect_exception:
        with pytest.raises(expected_exception_type):
            service.decide_strategy(ctx)
    else:
        # Purpose: prove valid boundary values do not throw.
        strategy_name, side_effects = service.decide_strategy(ctx)
        assert isinstance(strategy_name, str)
        assert isinstance(side_effects, list)
