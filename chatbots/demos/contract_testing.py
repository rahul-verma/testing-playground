"""
contract_testing_demo.py

Run with:
    python -m unittest contract_testing_demo.py
"""

import unittest
import uuid
from datetime import datetime, timezone

from jsonschema import validate, ValidationError


# =========================
# Shared Contract (Schemas)
# =========================

SKILL_REQUEST_SCHEMA = {
    "$id": "https://example.com/schemas/skill-request.json",
    "type": "object",
    "required": ["request_id", "timestamp", "skill", "channel", "parameters"],
    "properties": {
        "request_id": {"type": "string"},  # keep simple for demo
        "timestamp": {"type": "string"},
        "skill": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
            },
        },
        "channel": {
            "type": "object",
            "required": ["type"],
            "properties": {
                "type": {"type": "string"},
                "locale": {"type": "string"},
                "session_id": {"type": "string"},
                "conversation_id": {"type": "string"},
            },
            "additionalProperties": True,
        },
        "user_context": {"type": "object"},
        "dialog_context": {"type": "object"},
        "parameters": {
            "type": "object",
            "required": ["order_id"],
            "properties": {
                "order_id": {"type": "string"},
            },
            "additionalProperties": True,
        },
        "security": {"type": "object"},
        "compliance": {"type": "object"},
        "trace": {"type": "object"},
    },
    "additionalProperties": True,
}

SKILL_RESPONSE_SCHEMA = {
    "$id": "https://example.com/schemas/skill-response.json",
    "type": "object",
    "required": ["request_id", "skill", "status"],
    "properties": {
        "request_id": {"type": "string"},
        "skill": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"},
            },
        },
        "status": {
            "type": "object",
            "required": ["code"],
            "properties": {
                "code": {
                    "type": "string",
                    "enum": ["SUCCESS", "NEEDS_MORE_INFO", "BUSINESS_ERROR", "TECH_ERROR"],
                },
                "subcode": {"type": ["string", "null"]},
                "message": {"type": ["string", "null"]},
            },
        },
        "prompts": {"type": "array"},
        "data": {"type": "object"},
        "next_actions": {"type": "array"},
        "questions": {"type": "array"},
        "errors": {"type": "array"},
        "telemetry": {"type": "object"},
        "audit": {"type": "object"},
    },
    "additionalProperties": True,
}


# =========================
# Consumer-side Code
# (Conversation Orchestrator)
# =========================

def build_order_tracking_request(order_id: str) -> dict:
    """
    Orchestrator builds a skill request for the 'order_tracking' skill.
    This function embodies the *consumer* expectations.
    """
    now = datetime.now(timezone.utc).isoformat()
    return {
        "request_id": str(uuid.uuid4()),
        "timestamp": now,
        "skill": {
            "name": "order_tracking",
            "version": "v1",
        },
        "channel": {
            "type": "web",
            "locale": "en-GB",
            "session_id": "sess-123",
            "conversation_id": "conv-456",
        },
        "user_context": {
            "user_id": "cust-42",
            "authenticated": True,
            "roles": ["customer"],
            "jurisdiction": "EU",
        },
        "dialog_context": {
            "turn_index": 3,
            "intent": "TRACK_ORDER",
            "confidence": 0.93,
            "entities": {
                "order_id": order_id,
            },
        },
        "parameters": {
            "order_id": order_id,
        },
        "security": {
            "pii_allowed": True,
            "max_pii_level": "LOW",
            "auth_level": "STRONG",
        },
        "compliance": {
            "region": "EU",
            "sector": "insurance",
            "consents": {
                "call_recording": True,
                "data_enrichment": False,
            },
        },
        "trace": {
            "correlation_id": "trace-abc",
            "parent_span_id": "span-xyz",
        },
    }


# =========================
# Provider-side Code
# (Skill Implementation)
# =========================

def handle_order_tracking_request(request: dict) -> dict:
    """
    Provider implementation for the 'order_tracking' skill.
    This simulates reading a request dict and returning a response dict.
    In a real system this would be an HTTP handler.
    """

    # In a real implementation you'd validate request against SKILL_REQUEST_SCHEMA
    # at the boundary too, and return a TECH_ERROR on failure.

    order_id = request.get("parameters", {}).get("order_id")

    # Dumb fake logic just for demo:
    if not order_id:
        status = {
            "code": "NEEDS_MORE_INFO",
            "subcode": "MISSING_ORDER_ID",
            "message": "Order ID is required.",
        }
        prompts = [
            {
                "role": "assistant",
                "channel_hint": request["channel"]["type"],
                "text": "Could you please provide your order number?",
                "tone": "neutral",
                "sensitive": False,
            }
        ]
        questions = [
            {
                "id": "need_order_id",
                "text": "Please ask the user for their order number.",
                "required_parameters": ["order_id"],
            }
        ]
        data = {}
    else:
        status = {
            "code": "SUCCESS",
            "subcode": None,
            "message": None,
        }
        prompts = [
            {
                "role": "assistant",
                "channel_hint": request["channel"]["type"],
                "text": f"Your order {order_id} is on its way and should arrive tomorrow.",
                "tone": "neutral",
                "sensitive": False,
            }
        ]
        questions = []
        data = {
            "order_id": order_id,
            "status": "IN_TRANSIT",
            "carrier": "DHL",
            "eta": "2025-12-01",
            "tracking_url": f"https://tracking.example.com/{order_id}",
        }

    response = {
        "request_id": request["request_id"],
        "skill": {
            "name": "order_tracking",
            "version": "v1",
        },
        "status": status,
        "prompts": prompts,
        "data": data,
        "next_actions": [],
        "questions": questions,
        "errors": [],
        "telemetry": {
            "latency_ms": 42,
            "backend_calls": [
                {
                    "system": "OMS",
                    "operation": "GET_ORDER_STATUS",
                    "latency_ms": 30,
                    "success": True,
                }
            ],
        },
        "audit": {
            "pii_touched": ["name", "address"],
            "decisions": [
                {
                    "rule_id": "GDPR_MASK_ADDRESS",
                    "outcome": "MASKED",
                }
            ],
        },
    }
    return response


# =========================
# Contract Tests
# =========================

class ConsumerContractTests(unittest.TestCase):
    """
    Tests that the *consumer* (orchestrator) is building requests
    that conform to the agreed contract (SKILL_REQUEST_SCHEMA).
    """

    def test_build_order_tracking_request_matches_schema(self):
        req = build_order_tracking_request(order_id="ORD-123456")

        # Validate against shared contract
        validate(instance=req, schema=SKILL_REQUEST_SCHEMA)

        # A couple of semantic expectations from the consumer side
        self.assertEqual(req["skill"]["name"], "order_tracking")
        self.assertIn("order_id", req["parameters"])
        self.assertEqual(req["parameters"]["order_id"], "ORD-123456")


class ProviderContractTests(unittest.TestCase):
    """
    Tests that the *provider* (skill implementation) produces responses
    that conform to the agreed contract (SKILL_RESPONSE_SCHEMA),
    given a valid request.
    """

    def test_handle_order_tracking_request_success_matches_schema(self):
        # Arrange: consumer builds a valid request
        request = build_order_tracking_request(order_id="ORD-999999")
        validate(instance=request, schema=SKILL_REQUEST_SCHEMA)

        # Act: provider handles the request
        response = handle_order_tracking_request(request)

        # Assert: response conforms to the response contract
        validate(instance=response, schema=SKILL_RESPONSE_SCHEMA)
        self.assertEqual(response["status"]["code"], "SUCCESS")
        self.assertEqual(response["data"]["order_id"], "ORD-999999")

    def test_handle_order_tracking_request_missing_order_id_contract(self):
        # Arrange: simulate a slightly broken consumer (no order_id)
        bad_request = build_order_tracking_request(order_id=None)
        bad_request["parameters"].pop("order_id", None)

        # Notice: the request NO LONGER validates against the schema
        with self.assertRaises(ValidationError):
            validate(instance=bad_request, schema=SKILL_REQUEST_SCHEMA)

        # But let's say provider code still gets this (e.g. missing validation at gateway)
        response = handle_order_tracking_request(bad_request)

        # Provider must still respect *response* contract:
        validate(instance=response, schema=SKILL_RESPONSE_SCHEMA)

        # And signal the correct status to the orchestrator
        self.assertEqual(response["status"]["code"], "NEEDS_MORE_INFO")
        self.assertEqual(response["status"]["subcode"], "MISSING_ORDER_ID")
        self.assertTrue(response["questions"])


class ProviderBackwardCompatibilityTests(unittest.TestCase):
    """
    Example showing how to catch *breaking changes* in provider behavior.
    Imagine a dev accidentally removes the 'status' field from the response;
    these tests would fail.
    """

    def test_response_must_always_include_status(self):
        request = build_order_tracking_request(order_id="ORD-111111")
        response = handle_order_tracking_request(request)

        # Explicit assertion about critical fields
        self.assertIn("status", response)
        self.assertIn("code", response["status"])

        # And still validate against the full schema
        validate(instance=response, schema=SKILL_RESPONSE_SCHEMA)


if __name__ == "__main__":
    unittest.main()
