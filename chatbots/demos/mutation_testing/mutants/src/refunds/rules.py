from datetime import date
from inspect import signature as _mutmut_signature
from typing import Annotated
from typing import Callable
from typing import ClassVar


MutantDict = Annotated[dict[str, Callable], "Mutant"]


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None):
    """Forward call to original or mutated function, depending on the environment"""
    import os
    mutant_under_test = os.environ['MUTANT_UNDER_TEST']
    if mutant_under_test == 'fail':
        from mutmut.__main__ import MutmutProgrammaticFailException
        raise MutmutProgrammaticFailException('Failed programmatically')      
    elif mutant_under_test == 'stats':
        from mutmut.__main__ import record_trampoline_hit
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__)
        result = orig(*call_args, **call_kwargs)
        return result
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_'
    if not mutant_under_test.startswith(prefix):
        result = orig(*call_args, **call_kwargs)
        return result
    mutant_name = mutant_under_test.rpartition('.')[-1]
    if self_arg is not None:
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs)
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs)
    return result


class Decision:
    def xǁDecisionǁ__init____mutmut_orig(self, status: str, reason: str):
        self.status = status
        self.reason = reason
    def xǁDecisionǁ__init____mutmut_1(self, status: str, reason: str):
        self.status = None
        self.reason = reason
    def xǁDecisionǁ__init____mutmut_2(self, status: str, reason: str):
        self.status = status
        self.reason = None
    
    xǁDecisionǁ__init____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDecisionǁ__init____mutmut_1': xǁDecisionǁ__init____mutmut_1, 
        'xǁDecisionǁ__init____mutmut_2': xǁDecisionǁ__init____mutmut_2
    }
    
    def __init__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDecisionǁ__init____mutmut_orig"), object.__getattribute__(self, "xǁDecisionǁ__init____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __init__.__signature__ = _mutmut_signature(xǁDecisionǁ__init____mutmut_orig)
    xǁDecisionǁ__init____mutmut_orig.__name__ = 'xǁDecisionǁ__init__'

    def xǁDecisionǁ__eq____mutmut_orig(self, other):
        return (
            isinstance(other, Decision)
            and self.status == other.status
            and self.reason == other.reason
        )

    def xǁDecisionǁ__eq____mutmut_1(self, other):
        return (
            isinstance(other, Decision)
            and self.status == other.status or self.reason == other.reason
        )

    def xǁDecisionǁ__eq____mutmut_2(self, other):
        return (
            isinstance(other, Decision) or self.status == other.status
            and self.reason == other.reason
        )

    def xǁDecisionǁ__eq____mutmut_3(self, other):
        return (
            isinstance(other, Decision)
            and self.status != other.status
            and self.reason == other.reason
        )

    def xǁDecisionǁ__eq____mutmut_4(self, other):
        return (
            isinstance(other, Decision)
            and self.status == other.status
            and self.reason != other.reason
        )
    
    xǁDecisionǁ__eq____mutmut_mutants : ClassVar[MutantDict] = {
    'xǁDecisionǁ__eq____mutmut_1': xǁDecisionǁ__eq____mutmut_1, 
        'xǁDecisionǁ__eq____mutmut_2': xǁDecisionǁ__eq____mutmut_2, 
        'xǁDecisionǁ__eq____mutmut_3': xǁDecisionǁ__eq____mutmut_3, 
        'xǁDecisionǁ__eq____mutmut_4': xǁDecisionǁ__eq____mutmut_4
    }
    
    def __eq__(self, *args, **kwargs):
        result = _mutmut_trampoline(object.__getattribute__(self, "xǁDecisionǁ__eq____mutmut_orig"), object.__getattribute__(self, "xǁDecisionǁ__eq____mutmut_mutants"), args, kwargs, self)
        return result 
    
    __eq__.__signature__ = _mutmut_signature(xǁDecisionǁ__eq____mutmut_orig)
    xǁDecisionǁ__eq____mutmut_orig.__name__ = 'xǁDecisionǁ__eq__'


def x_is_refund_eligible__mutmut_orig(order, customer, policy, request_date: date) -> Decision:
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


def x_is_refund_eligible__mutmut_1(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date + order.purchase_date).days > policy.max_refund_days:
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


def x_is_refund_eligible__mutmut_2(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days >= policy.max_refund_days:
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


def x_is_refund_eligible__mutmut_3(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision(None, "Outside refund window")

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


def x_is_refund_eligible__mutmut_4(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", None)

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


def x_is_refund_eligible__mutmut_5(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("Outside refund window")

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


def x_is_refund_eligible__mutmut_6(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", )

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


def x_is_refund_eligible__mutmut_7(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("XXDENIEDXX", "Outside refund window")

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


def x_is_refund_eligible__mutmut_8(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("denied", "Outside refund window")

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


def x_is_refund_eligible__mutmut_9(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "XXOutside refund windowXX")

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


def x_is_refund_eligible__mutmut_10(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "outside refund window")

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


def x_is_refund_eligible__mutmut_11(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "OUTSIDE REFUND WINDOW")

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


def x_is_refund_eligible__mutmut_12(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" or order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_13(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region != "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_14(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "XXUSXX" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_15(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "us" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_16(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount >= 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_17(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 501:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_18(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision(None, "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_19(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", None)

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_20(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_21(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", )

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_22(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("XXMANUAL_REVIEWXX", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_23(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("manual_review", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_24(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "XXHigh-value refund in USXX")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_25(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "high-value refund in us")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_26(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "HIGH-VALUE REFUND IN US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_27(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision(None, "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_28(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", None)

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_29(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_30(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", )

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_31(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("XXDENIEDXX", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_32(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("denied", "Account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_33(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "XXAccount restrictedXX")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_34(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "account restricted")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_35(order, customer, policy, request_date: date) -> Decision:
    # R1: Time-based rule
    if (request_date - order.purchase_date).days > policy.max_refund_days:
        return Decision("DENIED", "Outside refund window")

    # R2: Region-specific rule
    if customer.region == "US" and order.amount > 500:
        return Decision("MANUAL_REVIEW", "High-value refund in US")

    # R3: Fraud / risk flag
    if customer.is_fraud_flagged:
        return Decision("DENIED", "ACCOUNT RESTRICTED")

    # R4: Product & coverage type
    if order.product_type == "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_36(order, customer, policy, request_date: date) -> Decision:
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
    if order.product_type == "Digital" or not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_37(order, customer, policy, request_date: date) -> Decision:
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
    if order.product_type != "Digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_38(order, customer, policy, request_date: date) -> Decision:
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
    if order.product_type == "XXDigitalXX" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_39(order, customer, policy, request_date: date) -> Decision:
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
    if order.product_type == "digital" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_40(order, customer, policy, request_date: date) -> Decision:
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
    if order.product_type == "DIGITAL" and not policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_41(order, customer, policy, request_date: date) -> Decision:
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
    if order.product_type == "Digital" and policy.allows_digital_refunds:
        return Decision("DENIED", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_42(order, customer, policy, request_date: date) -> Decision:
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
        return Decision(None, "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_43(order, customer, policy, request_date: date) -> Decision:
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
        return Decision("DENIED", None)

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_44(order, customer, policy, request_date: date) -> Decision:
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
        return Decision("Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_45(order, customer, policy, request_date: date) -> Decision:
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
        return Decision("DENIED", )

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_46(order, customer, policy, request_date: date) -> Decision:
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
        return Decision("XXDENIEDXX", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_47(order, customer, policy, request_date: date) -> Decision:
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
        return Decision("denied", "Digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_48(order, customer, policy, request_date: date) -> Decision:
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
        return Decision("DENIED", "XXDigital items non-refundableXX")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_49(order, customer, policy, request_date: date) -> Decision:
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
        return Decision("DENIED", "digital items non-refundable")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_50(order, customer, policy, request_date: date) -> Decision:
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
        return Decision("DENIED", "DIGITAL ITEMS NON-REFUNDABLE")

    # R5: Default allow
    return Decision("APPROVED", "Eligible for refund")


def x_is_refund_eligible__mutmut_51(order, customer, policy, request_date: date) -> Decision:
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
    return Decision(None, "Eligible for refund")


def x_is_refund_eligible__mutmut_52(order, customer, policy, request_date: date) -> Decision:
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
    return Decision("APPROVED", None)


def x_is_refund_eligible__mutmut_53(order, customer, policy, request_date: date) -> Decision:
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
    return Decision("Eligible for refund")


def x_is_refund_eligible__mutmut_54(order, customer, policy, request_date: date) -> Decision:
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
    return Decision("APPROVED", )


def x_is_refund_eligible__mutmut_55(order, customer, policy, request_date: date) -> Decision:
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
    return Decision("XXAPPROVEDXX", "Eligible for refund")


def x_is_refund_eligible__mutmut_56(order, customer, policy, request_date: date) -> Decision:
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
    return Decision("approved", "Eligible for refund")


def x_is_refund_eligible__mutmut_57(order, customer, policy, request_date: date) -> Decision:
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
    return Decision("APPROVED", "XXEligible for refundXX")


def x_is_refund_eligible__mutmut_58(order, customer, policy, request_date: date) -> Decision:
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
    return Decision("APPROVED", "eligible for refund")


def x_is_refund_eligible__mutmut_59(order, customer, policy, request_date: date) -> Decision:
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
    return Decision("APPROVED", "ELIGIBLE FOR REFUND")

x_is_refund_eligible__mutmut_mutants : ClassVar[MutantDict] = {
'x_is_refund_eligible__mutmut_1': x_is_refund_eligible__mutmut_1, 
    'x_is_refund_eligible__mutmut_2': x_is_refund_eligible__mutmut_2, 
    'x_is_refund_eligible__mutmut_3': x_is_refund_eligible__mutmut_3, 
    'x_is_refund_eligible__mutmut_4': x_is_refund_eligible__mutmut_4, 
    'x_is_refund_eligible__mutmut_5': x_is_refund_eligible__mutmut_5, 
    'x_is_refund_eligible__mutmut_6': x_is_refund_eligible__mutmut_6, 
    'x_is_refund_eligible__mutmut_7': x_is_refund_eligible__mutmut_7, 
    'x_is_refund_eligible__mutmut_8': x_is_refund_eligible__mutmut_8, 
    'x_is_refund_eligible__mutmut_9': x_is_refund_eligible__mutmut_9, 
    'x_is_refund_eligible__mutmut_10': x_is_refund_eligible__mutmut_10, 
    'x_is_refund_eligible__mutmut_11': x_is_refund_eligible__mutmut_11, 
    'x_is_refund_eligible__mutmut_12': x_is_refund_eligible__mutmut_12, 
    'x_is_refund_eligible__mutmut_13': x_is_refund_eligible__mutmut_13, 
    'x_is_refund_eligible__mutmut_14': x_is_refund_eligible__mutmut_14, 
    'x_is_refund_eligible__mutmut_15': x_is_refund_eligible__mutmut_15, 
    'x_is_refund_eligible__mutmut_16': x_is_refund_eligible__mutmut_16, 
    'x_is_refund_eligible__mutmut_17': x_is_refund_eligible__mutmut_17, 
    'x_is_refund_eligible__mutmut_18': x_is_refund_eligible__mutmut_18, 
    'x_is_refund_eligible__mutmut_19': x_is_refund_eligible__mutmut_19, 
    'x_is_refund_eligible__mutmut_20': x_is_refund_eligible__mutmut_20, 
    'x_is_refund_eligible__mutmut_21': x_is_refund_eligible__mutmut_21, 
    'x_is_refund_eligible__mutmut_22': x_is_refund_eligible__mutmut_22, 
    'x_is_refund_eligible__mutmut_23': x_is_refund_eligible__mutmut_23, 
    'x_is_refund_eligible__mutmut_24': x_is_refund_eligible__mutmut_24, 
    'x_is_refund_eligible__mutmut_25': x_is_refund_eligible__mutmut_25, 
    'x_is_refund_eligible__mutmut_26': x_is_refund_eligible__mutmut_26, 
    'x_is_refund_eligible__mutmut_27': x_is_refund_eligible__mutmut_27, 
    'x_is_refund_eligible__mutmut_28': x_is_refund_eligible__mutmut_28, 
    'x_is_refund_eligible__mutmut_29': x_is_refund_eligible__mutmut_29, 
    'x_is_refund_eligible__mutmut_30': x_is_refund_eligible__mutmut_30, 
    'x_is_refund_eligible__mutmut_31': x_is_refund_eligible__mutmut_31, 
    'x_is_refund_eligible__mutmut_32': x_is_refund_eligible__mutmut_32, 
    'x_is_refund_eligible__mutmut_33': x_is_refund_eligible__mutmut_33, 
    'x_is_refund_eligible__mutmut_34': x_is_refund_eligible__mutmut_34, 
    'x_is_refund_eligible__mutmut_35': x_is_refund_eligible__mutmut_35, 
    'x_is_refund_eligible__mutmut_36': x_is_refund_eligible__mutmut_36, 
    'x_is_refund_eligible__mutmut_37': x_is_refund_eligible__mutmut_37, 
    'x_is_refund_eligible__mutmut_38': x_is_refund_eligible__mutmut_38, 
    'x_is_refund_eligible__mutmut_39': x_is_refund_eligible__mutmut_39, 
    'x_is_refund_eligible__mutmut_40': x_is_refund_eligible__mutmut_40, 
    'x_is_refund_eligible__mutmut_41': x_is_refund_eligible__mutmut_41, 
    'x_is_refund_eligible__mutmut_42': x_is_refund_eligible__mutmut_42, 
    'x_is_refund_eligible__mutmut_43': x_is_refund_eligible__mutmut_43, 
    'x_is_refund_eligible__mutmut_44': x_is_refund_eligible__mutmut_44, 
    'x_is_refund_eligible__mutmut_45': x_is_refund_eligible__mutmut_45, 
    'x_is_refund_eligible__mutmut_46': x_is_refund_eligible__mutmut_46, 
    'x_is_refund_eligible__mutmut_47': x_is_refund_eligible__mutmut_47, 
    'x_is_refund_eligible__mutmut_48': x_is_refund_eligible__mutmut_48, 
    'x_is_refund_eligible__mutmut_49': x_is_refund_eligible__mutmut_49, 
    'x_is_refund_eligible__mutmut_50': x_is_refund_eligible__mutmut_50, 
    'x_is_refund_eligible__mutmut_51': x_is_refund_eligible__mutmut_51, 
    'x_is_refund_eligible__mutmut_52': x_is_refund_eligible__mutmut_52, 
    'x_is_refund_eligible__mutmut_53': x_is_refund_eligible__mutmut_53, 
    'x_is_refund_eligible__mutmut_54': x_is_refund_eligible__mutmut_54, 
    'x_is_refund_eligible__mutmut_55': x_is_refund_eligible__mutmut_55, 
    'x_is_refund_eligible__mutmut_56': x_is_refund_eligible__mutmut_56, 
    'x_is_refund_eligible__mutmut_57': x_is_refund_eligible__mutmut_57, 
    'x_is_refund_eligible__mutmut_58': x_is_refund_eligible__mutmut_58, 
    'x_is_refund_eligible__mutmut_59': x_is_refund_eligible__mutmut_59
}

def is_refund_eligible(*args, **kwargs):
    result = _mutmut_trampoline(x_is_refund_eligible__mutmut_orig, x_is_refund_eligible__mutmut_mutants, args, kwargs)
    return result 

is_refund_eligible.__signature__ = _mutmut_signature(x_is_refund_eligible__mutmut_orig)
x_is_refund_eligible__mutmut_orig.__name__ = 'x_is_refund_eligible'

__all__ = ["is_refund_eligible", "Decision"]
