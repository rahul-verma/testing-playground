# tests/test_caller_exception_mapping.py
import pytest

from order_tracking.contract import (
    ContextValidationException,
    CustomerAction,
    CustomerContext,
    InvalidCustomerIdException,
    TrackingStrategyException,
    UpstreamOrderPlatformUnavailableException,
)
from order_tracking.consumer import CallerOutcome, OrderTrackingCaller


# -----------------------------
# Minimal stub provider to force expensive/rare errors
# (matches the updated provider interface)
# -----------------------------
class StubProvider:
    def __init__(self, decide_side_effect=None, decide_return=("AI_SIMPLE", None)):
        self._decide_side_effect = decide_side_effect
        self._decide_return = decide_return

    def decide_strategy(self, ctx):
        if self._decide_side_effect:
            raise self._decide_side_effect
        strategy, side_effects = self._decide_return
        return strategy, (side_effects or [])


def _minimal_valid_ctx():
    # Not strictly needed for exception mapping tests when the stub ignores ctx,
    # but provides a realistic compatible value for black-box style.
    return CustomerContext(
        action=CustomerAction.TRACK_ORDER,
        customer_id="CUST-123456",
        country="US",
        is_vip=False,
        authenticated=True,
        channel=None,          # stub does not inspect; keep minimal
        orders=[],             # stub does not inspect; keep minimal
        recent_failed_ai_attempts=0,
        ai_confidence=0.9,
    )


def test_caller_maps_upstream_unavailable_to_specific_outcome():
    caller = OrderTrackingCaller(service=StubProvider(
        decide_side_effect=UpstreamOrderPlatformUnavailableException("down")
    ))
    resp = caller.decide(_minimal_valid_ctx())
    assert resp.outcome == CallerOutcome.UPSTREAM_UNAVAILABLE
    assert resp.error_code == "UPSTREAM_UNAVAILABLE"
    assert resp.strategy is None
    assert "down" in (resp.error_message or "")


def test_caller_maps_validation_exception_to_bad_request():
    caller = OrderTrackingCaller(service=StubProvider(
        decide_side_effect=InvalidCustomerIdException("bad id")
    ))
    resp = caller.decide(_minimal_valid_ctx())
    assert resp.outcome == CallerOutcome.BAD_REQUEST
    assert resp.error_code == "InvalidCustomerIdException"
    assert resp.strategy is None
    assert "bad id" in (resp.error_message or "")


def test_caller_maps_unknown_domain_exception_to_internal_error():
    class SomeDomainError(TrackingStrategyException):
        pass

    caller = OrderTrackingCaller(service=StubProvider(decide_side_effect=SomeDomainError("boom")))
    resp = caller.decide(_minimal_valid_ctx())
    assert resp.outcome == CallerOutcome.INTERNAL_ERROR
    assert resp.error_code == "TRACKING_STRATEGY_ERROR"
    assert resp.strategy is None
    assert "boom" in (resp.error_message or "")


def test_caller_passes_through_strategy_mapping_when_no_exception():
    caller = OrderTrackingCaller(service=StubProvider(decide_return=("AI_DETAILED", [])))
    resp = caller.decide(_minimal_valid_ctx())
    assert resp.outcome == CallerOutcome.AI_DETAILED
    assert resp.strategy == "AI_DETAILED"
    assert resp.error_code is None
