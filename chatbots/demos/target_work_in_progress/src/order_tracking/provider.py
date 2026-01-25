from __future__ import annotations

from math import isfinite
from time import time
from typing import Callable, List, Optional, Tuple

from .contract import (
    # models / enums
    Channel,
    CustomerAction,
    CustomerContext,
    Order,
    OrderStatus,
    PolicyConfig,
    SideEffect,
    SideEffectType,
    Strategy,
    # exceptions
    ContextValidationException,
    InvalidAIConfidenceException,
    InvalidCountryFormatException,
    InvalidCustomerActionException,
    InvalidCustomerIdException,
    InvalidOrderAmountException,
    InvalidOrderIdException,
    InvalidOrderItemCountException,
    InvalidRecentFailedAIAttemptsException,
    UnsupportedCountryException,
    UpstreamOrderPlatformUnavailableException,
    # protocols
    OrderSelector,
    RiskScorer,
    RulesEngine,
    UpstreamHealthChecker,
    Validator,
)

# ============================================================
# Default implementations
# ============================================================

class DefaultValidator:
    def __init__(self, cfg: PolicyConfig):
        self.cfg = cfg

    @staticmethod
    def _is_blank(s: Optional[str]) -> bool:
        return s is None or s.strip() == ""

    def _valid_id(self, s: str, min_len: int, max_len: int) -> bool:
        if self._is_blank(s):
            return False
        if not (min_len <= len(s) <= max_len):
            return False
        allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        return all(ch in allowed for ch in s)

    def _valid_country_format(self, code: str) -> bool:
        if self._is_blank(code):
            return False
        if len(code) != self.cfg.country_code_len:
            return False
        if not code.isalpha() or not code.isupper():
            return False
        return True

    @staticmethod
    def _valid_int_range(x: int, lo: int, hi: int) -> bool:
        return lo <= x <= hi

    @staticmethod
    def _valid_float_range(x: float, lo: float, hi: float) -> bool:
        return isfinite(x) and lo <= x <= hi

    @staticmethod
    def _valid_action(action: CustomerAction) -> bool:
        # Keeping this explicit makes it easy to extend and easy to test.
        return action in {
            CustomerAction.TRACK_ORDER,
            CustomerAction.REQUEST_REFUND,
            CustomerAction.CANCEL_ORDER,
            CustomerAction.OPEN_DISPUTE,
        }

    def validate_or_raise(self, ctx: CustomerContext) -> None:
        cfg = self.cfg

        # Action validation
        if not self._valid_action(ctx.action):
            raise InvalidCustomerActionException(f"Unsupported/invalid action: {ctx.action!r}")

        # Customer validation
        if not self._valid_id(ctx.customer_id, cfg.min_customer_id_len, cfg.max_customer_id_len):
            raise InvalidCustomerIdException(
                f"Invalid customer_id={ctx.customer_id!r}. Expected length "
                f"{cfg.min_customer_id_len}..{cfg.max_customer_id_len} and chars [A-Za-z0-9-_]."
            )

        if not self._valid_country_format(ctx.country):
            raise InvalidCountryFormatException(
                f"Invalid country={ctx.country!r}. Expected ISO alpha-2 uppercase (e.g., 'US', 'DE')."
            )
        if ctx.country not in cfg.supported_countries:
            raise UnsupportedCountryException(
                f"Unsupported country={ctx.country!r}. Supported countries: {sorted(cfg.supported_countries)}."
            )

        # NOTE: This expects int-like values; passing non-int will likely raise TypeError
        # during comparison, which is acceptable for robustness tests.
        if not self._valid_int_range(ctx.recent_failed_ai_attempts, cfg.min_failed_ai_attempts, cfg.max_failed_ai_attempts):
            raise InvalidRecentFailedAIAttemptsException(
                f"Invalid recent_failed_ai_attempts={ctx.recent_failed_ai_attempts}. "
                f"Expected {cfg.min_failed_ai_attempts}..{cfg.max_failed_ai_attempts}."
            )

        if not self._valid_float_range(ctx.ai_confidence, 0.0, 1.0):
            raise InvalidAIConfidenceException(
                f"Invalid ai_confidence={ctx.ai_confidence!r}. Expected finite float within 0.0..1.0."
            )

        # Orders list
        if ctx.orders is None:
            raise ContextValidationException("orders must be a list (not None).")

        # Per-order validation
        for idx, o in enumerate(ctx.orders):
            if not self._valid_id(o.order_id, cfg.min_order_id_len, cfg.max_order_id_len):
                raise InvalidOrderIdException(
                    f"Invalid order_id at index {idx}: {o.order_id!r}. Expected length "
                    f"{cfg.min_order_id_len}..{cfg.max_order_id_len} and chars [A-Za-z0-9-_]."
                )
            if not self._valid_float_range(o.total_amount, 0.0, 1_000_000.0):
                raise InvalidOrderAmountException(
                    f"Invalid total_amount at index {idx}: {o.total_amount!r}. Expected finite float within 0.0..1_000_000.0."
                )
            if not self._valid_int_range(o.item_count, 0, 999):
                raise InvalidOrderItemCountException(
                    f"Invalid item_count at index {idx}: {o.item_count}. Expected 0..999."
                )


class DefaultRiskScorer:
    def score(self, order: Order, cfg: PolicyConfig) -> int:
        score = 0
        if order.total_amount >= cfg.high_value_amount_threshold:
            score += 2
        if order.is_flagged_fraud_risk:
            score += 5
        if order.has_open_dispute:
            score += 3
        return score


class DefaultOrderSelector:
    def select(self, orders: List[Order], scorer: RiskScorer, cfg: PolicyConfig) -> Order:
        best: Optional[Order] = None
        best_score = -1
        for o in orders:
            s = scorer.score(o, cfg)
            if best is None or s > best_score:
                best, best_score = o, s
        return best  # caller ensures non-empty


class DefaultRulesEngine:
    """
    Rules are defined as ordered predicates for clarity and for decision-table teaching.
    Produces (Strategy, side_effects) where side_effects represent implied downstream actions.
    """

    def __init__(self) -> None:
        self._rules: List[Tuple[Callable[[CustomerContext, Order, PolicyConfig], bool], Callable[[CustomerContext, Order, PolicyConfig], Tuple[Strategy, List[SideEffect]]]]] = [
            # 1) Authentication gate
            (
                lambda ctx, o, cfg: (not ctx.authenticated)
                and (ctx.channel == Channel.VOICE or ctx.country in cfg.strict_auth_countries),
                lambda ctx, o, cfg: (Strategy.AUTH_REQUIRED, [SideEffect(SideEffectType.REQUIRE_AUTH_STEP_UP, order_id=o.order_id)]),
            ),

            # 2) Mandatory human (risk / failures / low confidence)
            (
                lambda ctx, o, cfg: (
                    ((ctx.country in cfg.regulated_countries) and self._high_risk_order(o, cfg))
                    or (ctx.recent_failed_ai_attempts >= cfg.many_recent_ai_failures_threshold)
                    or (ctx.ai_confidence < cfg.min_ai_confidence)
                ),
                lambda ctx, o, cfg: (Strategy.MANDATORY_HUMAN, [SideEffect(SideEffectType.ESCALATE_TO_AGENT_QUEUE, order_id=o.order_id)]),
            ),

            # 3) Action-specific implied effects (examples)
            (
                lambda ctx, o, cfg: ctx.action == CustomerAction.OPEN_DISPUTE,
                lambda ctx, o, cfg: (Strategy.AI_WITH_HUMAN_FALLBACK, [SideEffect(SideEffectType.CREATE_DISPUTE_CASE, order_id=o.order_id)]),
            ),
            (
                lambda ctx, o, cfg: ctx.action == CustomerAction.REQUEST_REFUND,
                lambda ctx, o, cfg: (Strategy.AI_WITH_HUMAN_FALLBACK, [SideEffect(SideEffectType.CREATE_REFUND_CASE, order_id=o.order_id)]),
            ),
            (
                lambda ctx, o, cfg: ctx.action == CustomerAction.CANCEL_ORDER,
                lambda ctx, o, cfg: (Strategy.AI_WITH_HUMAN_FALLBACK, []),
            ),

            # 4) Default: TRACK_ORDER routing (status + VIP + channel + country)
            (
                lambda ctx, o, cfg: ctx.action == CustomerAction.TRACK_ORDER and o.status == OrderStatus.DELIVERED and ctx.is_vip and ctx.channel == Channel.VOICE,
                lambda ctx, o, cfg: (Strategy.AI_WITH_HUMAN_FALLBACK, []),
            ),
            (
                lambda ctx, o, cfg: ctx.action == CustomerAction.TRACK_ORDER and o.status == OrderStatus.DELIVERED and ctx.is_vip and ctx.channel == Channel.WEBCHAT,
                lambda ctx, o, cfg: (Strategy.AI_DETAILED, []),
            ),
            (
                lambda ctx, o, cfg: ctx.action == CustomerAction.TRACK_ORDER and o.status == OrderStatus.DELIVERED and (not ctx.is_vip),
                lambda ctx, o, cfg: (Strategy.AI_SIMPLE, []),
            ),
            (
                lambda ctx, o, cfg: ctx.action == CustomerAction.TRACK_ORDER and (o.status in (OrderStatus.SHIPPED, OrderStatus.UNKNOWN)) and ctx.channel == Channel.WEBCHAT,
                lambda ctx, o, cfg: (Strategy.AI_DETAILED, []),
            ),
            (
                lambda ctx, o, cfg: ctx.action == CustomerAction.TRACK_ORDER and (o.status in (OrderStatus.SHIPPED, OrderStatus.UNKNOWN)) and ctx.channel == Channel.VOICE,
                lambda ctx, o, cfg: (Strategy.AI_SIMPLE, []),
            ),
            (
                lambda ctx, o, cfg: ctx.action == CustomerAction.TRACK_ORDER and o.status == OrderStatus.CANCELLED and ctx.country == "US" and ctx.channel == Channel.VOICE,
                lambda ctx, o, cfg: (Strategy.AI_WITH_HUMAN_FALLBACK, []),
            ),

            # 5) Final fallback rule
            (
                lambda ctx, o, cfg: True,
                lambda ctx, o, cfg: (Strategy.AI_SIMPLE, []),
            ),
        ]

    @staticmethod
    def _high_risk_order(o: Order, cfg: PolicyConfig) -> bool:
        return bool(
            (o.total_amount >= cfg.high_value_amount_threshold)
            or o.is_flagged_fraud_risk
            or o.has_open_dispute
        )

    def evaluate(self, ctx: CustomerContext, highest_risk_order: Order, cfg: PolicyConfig) -> Tuple[Strategy, List[SideEffect]]:
        for cond, outcome_fn in self._rules:
            if cond(ctx, highest_risk_order, cfg):
                return outcome_fn(ctx, highest_risk_order, cfg)
        return (Strategy.AI_SIMPLE, [])


class DefaultUpstreamHealthChecker:
    """
    Dynamic, input-independent failure.
    First N seconds of every minute are treated as outage.
    """

    def __init__(self, *, fail_window_seconds: int = 3, cycle_seconds: int = 60):
        self.fail_window_seconds = fail_window_seconds
        self.cycle_seconds = cycle_seconds

    def ensure_available(self) -> None:
        now = int(time()) % self.cycle_seconds
        if now < self.fail_window_seconds:
            raise UpstreamOrderPlatformUnavailableException(
                "Upstream order platform unavailable (simulated intermittent outage)."
            )


# ============================================================
# Facade/service
# ============================================================

class OrderTrackingStrategyService:
    """
    Provider-facing service:
    - Validates input
    - Selects highest-risk order
    - Applies ordered rules to return (Strategy, side_effects)
    """

    def __init__(
        self,
        cfg: PolicyConfig,
        validator: Optional[Validator] = None,
        scorer: Optional[RiskScorer] = None,
        selector: Optional[OrderSelector] = None,
        rules: Optional[RulesEngine] = None,
        health: Optional[UpstreamHealthChecker] = None,
    ):
        self.cfg = cfg
        self.validator = validator or DefaultValidator(cfg)
        self.scorer = scorer or DefaultRiskScorer()
        self.selector = selector or DefaultOrderSelector()
        self.rules = rules or DefaultRulesEngine()
        self.health = health or DefaultUpstreamHealthChecker()

    def decide_strategy(self, ctx: CustomerContext) -> Tuple[str, List[SideEffect]]:
        """
        Returns:
            - (strategy_name, side_effects)

        Raises:
            - validation exceptions for invalid partitions
            - UpstreamOrderPlatformUnavailableException for dynamic upstream failures
        """
        self.health.ensure_available()
        self.validator.validate_or_raise(ctx)

        if not ctx.orders:
            return (Strategy.NO_ORDERS_FOUND.name, [])

        highest = self.selector.select(ctx.orders, self.scorer, self.cfg)
        strategy, side_effects = self.rules.evaluate(ctx, highest, self.cfg)
        return (strategy.name, side_effects)
