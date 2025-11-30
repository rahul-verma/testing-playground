from datetime import date


class Decision:
    def __init__(self, status: str, reason: str):
        self.status = status
        self.reason = reason

    def __eq__(self, other):
        return (
            isinstance(other, Decision)
            and self.status == other.status
            and self.reason == other.reason
        )


def is_refund_eligible(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")

__all__ = ["is_refund_eligible", "Decision"]
