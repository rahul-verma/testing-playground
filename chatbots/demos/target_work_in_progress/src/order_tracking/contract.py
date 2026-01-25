from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Protocol

# ============================================================
# Custom exceptions
# ============================================================

class TrackingStrategyException(Exception):
    """Base class for all strategy/validation/external exceptions."""


class ContextValidationException(TrackingStrategyException):
    """Base class for context validation failures."""


class InvalidCustomerActionException(ContextValidationException):
    pass


class InvalidCustomerIdException(ContextValidationException):
    pass


class InvalidCountryFormatException(ContextValidationException):
    pass


class UnsupportedCountryException(ContextValidationException):
    pass


class InvalidRecentFailedAIAttemptsException(ContextValidationException):
    pass


class InvalidAIConfidenceException(ContextValidationException):
    pass


class InvalidOrderIdException(ContextValidationException):
    pass


class InvalidOrderAmountException(ContextValidationException):
    pass


class InvalidOrderItemCountException(ContextValidationException):
    pass


class UpstreamOrderPlatformUnavailableException(TrackingStrategyException):
    """
    Dynamic, costly-to-reproduce exception.
    Represents an upstream platform outage/maintenance/rate-limit event.
    """
    pass


# -----------------------------
# Discrete values (Enums)
# -----------------------------

class Channel(Enum):
    VOICE = auto()
    WEBCHAT = auto()


class CustomerAction(Enum):
    """
    Customer-initiated intent. Drives strategy decisions and any implicit state progression.
    """
    TRACK_ORDER = auto()
    REQUEST_REFUND = auto()
    CANCEL_ORDER = auto()
    OPEN_DISPUTE = auto()


class OrderStatus(Enum):
    SHIPPED = auto()
    DELIVERED = auto()
    CANCELLED = auto()
    UNKNOWN = auto()


class Strategy(Enum):
    AI_SIMPLE = auto()
    AI_DETAILED = auto()
    AI_WITH_HUMAN_FALLBACK = auto()
    MANDATORY_HUMAN = auto()
    NO_ORDERS_FOUND = auto()
    AUTH_REQUIRED = auto()


class SideEffectType(Enum):
    """
    Optional: implied downstream actions (not explicit state-transition triggers).
    """
    CREATE_REFUND_CASE = auto()
    CREATE_DISPUTE_CASE = auto()
    ESCALATE_TO_AGENT_QUEUE = auto()
    REQUIRE_AUTH_STEP_UP = auto()


# -----------------------------
# Data models + config
# -----------------------------

@dataclass(frozen=True)
class PolicyConfig:
    min_failed_ai_attempts: int = 0
    max_failed_ai_attempts: int = 5
    many_recent_ai_failures_threshold: int = 2

    high_value_amount_threshold: float = 1000.00
    min_ai_confidence: float = 0.50

    min_customer_id_len: int = 6
    max_customer_id_len: int = 36
    min_order_id_len: int = 8
    max_order_id_len: int = 32
    country_code_len: int = 2

    regulated_countries: frozenset[str] = frozenset({"DE", "FR"})
    strict_auth_countries: frozenset[str] = frozenset({"US", "DE"})
    supported_countries: frozenset[str] = frozenset({"DE", "US", "FR", "GB", "IN"})


@dataclass
class Order:
    order_id: str
    total_amount: float
    item_count: int
    status: OrderStatus
    is_flagged_fraud_risk: bool
    has_open_dispute: bool


@dataclass
class CustomerContext:
    """
    Request context for decisioning. Action is included to support implicit progression.
    """
    action: CustomerAction
    customer_id: str
    country: str
    is_vip: bool
    authenticated: bool
    channel: Channel
    orders: List[Order]
    recent_failed_ai_attempts: int
    ai_confidence: float  # 0.0..1.0


@dataclass(frozen=True)
class SideEffect:
    """
    Optional output describing an implied downstream action.
    """
    effect_type: SideEffectType
    order_id: str | None = None


# ============================================================
# Protocols (seams)
# ============================================================

class Validator(Protocol):
    def validate_or_raise(self, ctx: CustomerContext) -> None: ...


class RiskScorer(Protocol):
    def score(self, order: Order, cfg: PolicyConfig) -> int: ...


class OrderSelector(Protocol):
    def select(self, orders: List[Order], scorer: RiskScorer, cfg: PolicyConfig) -> Order: ...


class RulesEngine(Protocol):
    def evaluate(self, ctx: CustomerContext, highest_risk_order: Order, cfg: PolicyConfig) -> tuple[Strategy, List[SideEffect]]: ...


class UpstreamHealthChecker(Protocol):
    def ensure_available(self) -> None: ...
