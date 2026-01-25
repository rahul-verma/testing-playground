from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from .contract import (
    ContextValidationException,
    CustomerContext,
    SideEffect,
    Strategy,
    TrackingStrategyException,
    UpstreamOrderPlatformUnavailableException,
)
from .provider import OrderTrackingStrategyService


class CallerOutcome(Enum):
    AI_SIMPLE = auto()
    AI_DETAILED = auto()
    AI_WITH_HUMAN_FALLBACK = auto()
    MANDATORY_HUMAN = auto()
    NO_ORDERS_FOUND = auto()
    AUTH_REQUIRED = auto()

    BAD_REQUEST = auto()
    UPSTREAM_UNAVAILABLE = auto()
    INTERNAL_ERROR = auto()


@dataclass
class DecisionResponse:
    outcome: CallerOutcome
    strategy: Optional[str] = None
    selected_order_id: Optional[str] = None
    reasons: Optional[List[str]] = None
    side_effects: Optional[List[Dict[str, Any]]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


_STRATEGY_TO_OUTCOME = {
    Strategy.AI_SIMPLE.name: CallerOutcome.AI_SIMPLE,
    Strategy.AI_DETAILED.name: CallerOutcome.AI_DETAILED,
    Strategy.AI_WITH_HUMAN_FALLBACK.name: CallerOutcome.AI_WITH_HUMAN_FALLBACK,
    Strategy.MANDATORY_HUMAN.name: CallerOutcome.MANDATORY_HUMAN,
    Strategy.NO_ORDERS_FOUND.name: CallerOutcome.NO_ORDERS_FOUND,
    Strategy.AUTH_REQUIRED.name: CallerOutcome.AUTH_REQUIRED,
}


def _serialize_side_effect(se: SideEffect) -> Dict[str, Any]:
    return {
        "effect_type": se.effect_type.name,
        "order_id": se.order_id,
    }


class OrderTrackingCaller:
    """
    Consumer-facing wrapper around the provider (callee).
    Converts provider return values and domain exceptions into caller outcomes.
    """

    def __init__(self, service: OrderTrackingStrategyService):
        self.service = service

    def decide(self, ctx: CustomerContext) -> DecisionResponse:
        try:
            # Provider now returns (strategy_name, side_effects)
            strategy_name, side_effects = self.service.decide_strategy(ctx)

            return DecisionResponse(
                outcome=_STRATEGY_TO_OUTCOME.get(strategy_name, CallerOutcome.INTERNAL_ERROR),
                strategy=strategy_name,
                # selected_order_id is not currently returned by provider; can be added later.
                selected_order_id=None,
                reasons=None,
                side_effects=[_serialize_side_effect(se) for se in side_effects],
            )

        except UpstreamOrderPlatformUnavailableException as ex:
            return DecisionResponse(
                outcome=CallerOutcome.UPSTREAM_UNAVAILABLE,
                error_code="UPSTREAM_UNAVAILABLE",
                error_message=str(ex),
            )

        except ContextValidationException as ex:
            return DecisionResponse(
                outcome=CallerOutcome.BAD_REQUEST,
                error_code=ex.__class__.__name__,
                error_message=str(ex),
            )

        except TrackingStrategyException as ex:
            return DecisionResponse(
                outcome=CallerOutcome.INTERNAL_ERROR,
                error_code="TRACKING_STRATEGY_ERROR",
                error_message=str(ex),
            )

        except Exception as ex:
            return DecisionResponse(
                outcome=CallerOutcome.INTERNAL_ERROR,
                error_code="UNEXPECTED_ERROR",
                error_message=str(ex),
            )
