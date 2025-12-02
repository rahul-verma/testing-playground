# Casanova_demo.py
# Streamlit UI for Casanova - an order bot using gpt-4o-mini + tool calling

import os
import json
import random
from datetime import datetime, timedelta

import streamlit as st
from openai import OpenAI

# -------------------------------------------------------------------
# OpenAI client (expects OPENAI_API_KEY in env or set via sidebar)
# -------------------------------------------------------------------

if "OPENAI_API_KEY" not in os.environ:
    st.sidebar.warning("Set OPENAI_API_KEY in environment or below.")
    api_key_input = st.sidebar.text_input("OpenAI API Key", type="password")
    if api_key_input:
        os.environ["OPENAI_API_KEY"] = api_key_input

client = OpenAI()

# -------------------------------------------------------------------
# System / Casanova context
# -------------------------------------------------------------------

Casanova_CONTEXT = """
You are an AI customer service agent built on Casanova for a regulated
insurance/finance e-commerce company operating across multiple countries
(e.g., Germany, EU, US).

The company uses Casanova to build agents for:
- Order tracking (“Where is my package?”)
- Returns & refunds
- FAQs (opening hours, policies, coverage, prices)

Agents run over phone (voice) and web chat. The environment is regulated,
so security, privacy, and auditability really matter.

You are currently focused on ORDER TRACKING-style requests only.

You MUST use the appropriate tools:

INTENTS → TOOLS
- TRACK_STATUS:
  - User asks “where is my order/parcel/package/shipment”,
    “current status”, “last scan”, “with courier?”, “left warehouse?” etc.
  - Use tool: track_order_status

- ASK_ETA:
  - User asks “when will it arrive”, “expected delivery date/time”,
    “still scheduled for today?”, “close to being delivered?” etc.
  - Use tool: get_order_eta

- REPORT_ISSUE:
  - User reports delays, missing package, “I haven’t received it yet”,
    “tracking not updating”, “is it lost?” etc.
  - Use tool: report_delivery_issue (in addition to other tools if needed).

If the user mentions order, package, shipment, parcel, or delivery,
try to collect an order_id (if missing) in a short clarification question
before calling tools.

You must never invent actual customer data. Tool outputs simulate a backend.
"""

system_message = {"role": "system", "content": Casanova_CONTEXT}

# -------------------------------------------------------------------
# Tool definitions (intents → 3 tools)
# -------------------------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "track_order_status",
            "description": (
                "TRACK_STATUS intent. "
                "Get detailed tracking status and current location of a customer's order."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The customer's order ID as provided in the conversation.",
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_eta",
            "description": (
                "ASK_ETA intent. "
                "Get the estimated delivery date/time of the customer's order."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The customer's order ID as provided in the conversation.",
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "report_delivery_issue",
            "description": (
                "REPORT_ISSUE intent. "
                "Create or update an issue ticket when the customer reports a delay, "
                "non-receipt, tracking problems, or a possibly lost parcel."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The customer's order ID if known.",
                    },
                    "issue_type": {
                        "type": "string",
                        "description": "High-level category of the issue.",
                        "enum": [
                            "DELAYED",
                            "NOT_RECEIVED",
                            "TRACKING_NOT_UPDATING",
                            "POSSIBLY_LOST",
                            "OTHER",
                        ],
                    },
                    "customer_description": {
                        "type": "string",
                        "description": "Free-text description of the problem in customer's own words.",
                    },
                },
                "required": ["issue_type", "customer_description"],
                "additionalProperties": False,
            },
        },
    },
]

# -------------------------------------------------------------------
# Backend stub implementations (replace with real Casanova/backends)
# -------------------------------------------------------------------

def track_order_status(order_id: str) -> dict:
    sample_statuses = [
        ("In transit", "Regional hub", -2),
        ("With courier", "Local delivery depot", -1),
        ("Out for delivery", "On delivery vehicle", 0),
        ("Delivered", "Customer's address", -1),
    ]
    status, location, days_offset = random.choice(sample_statuses)
    last_scan = (datetime.utcnow() + timedelta(days=days_offset)).isoformat() + "Z"
    return {
        "order_id": order_id,
        "status": status,
        "current_location": location,
        "last_scan_timestamp_utc": last_scan,
        "carrier": "DemoCarrier Express",
    }


def get_order_eta(order_id: str) -> dict:
    today = datetime.utcnow().date()
    eta_date = today + timedelta(days=random.randint(0, 4))
    return {
        "order_id": order_id,
        "eta_date": eta_date.isoformat(),
        "eta_window_local": "09:00–12:00",
        "still_on_schedule": random.choice([True, True, False]),
    }


def report_delivery_issue(
    order_id: str | None = None,
    issue_type: str = "OTHER",
    customer_description: str = "",
) -> dict:
    ticket_id = f"TICKET-{random.randint(100000, 999999)}"
    return {
        "ticket_id": ticket_id,
        "order_id": order_id,
        "issue_type": issue_type,
        "customer_description": customer_description,
        "status": "OPEN",
        "created_at_utc": datetime.utcnow().isoformat() + "Z",
        "next_step": "Our support team will review this case and contact the customer if needed.",
    }


tool_name_to_python_fn = {
    "track_order_status": track_order_status,
    "get_order_eta": get_order_eta,
    "report_delivery_issue": report_delivery_issue,
}

# -------------------------------------------------------------------
# Chat + tool-calling orchestration (one turn)
# -------------------------------------------------------------------

def run_turn(user_input: str, chat_history: list[dict]) -> str:
    """
    chat_history: list of {"role": "user"|"assistant", "content": "..."}
    Returns assistant's final text reply after any tool calls.
    """
    # Compose messages for the model
    messages = [system_message] + chat_history + [
        {"role": "user", "content": user_input}
    ]

    # First call – model decides whether to call tools
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    assistant_message = response.choices[0].message

    # If tools are requested
    if assistant_message.tool_calls:
        messages.append(
            {
                "role": "assistant",
                "tool_calls": assistant_message.tool_calls,
            }
        )

        tool_results_messages = []

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments or "{}")
            python_fn = tool_name_to_python_fn.get(tool_name)

            if python_fn is None:
                tool_output = {"error": f"Unknown tool: {tool_name}"}
            else:
                tool_output = python_fn(**tool_args)

            tool_results_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": json.dumps(tool_output),
                }
            )

        messages.extend(tool_results_messages)

        # Second call – model uses tool outputs to answer user
        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        final_message = final_response.choices[0].message
        return final_message.content

    # No tools needed
    else:
        return assistant_message.content

# -------------------------------------------------------------------
# Streamlit UI
# -------------------------------------------------------------------

st.set_page_config(page_title="Casanova Order Bot Demo", page_icon="📦", layout="centered")

st.title("📦 Casanova")
st.caption("Multi-turn conversation • gpt-4o-mini • 3 intents → 3 tools")

with st.sidebar:
    st.markdown("### Demo Info")
    st.markdown(
        "- **Intents**: TRACK_STATUS, ASK_ETA, REPORT_ISSUE\n"
        "- **Tools**: `track_order_status`, `get_order_eta`, `report_delivery_issue`\n"
        "- Tools are stubbed; in production they would call Casanova flows / backends."
    )

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    # Optional: seed with a system-intro message
    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": "Hi! I’m your Casanova. Your AI-powered order assistant. How can I help with your package today?",
        }
    )

# Display chat history
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# User input box (multi-turn)
prompt = st.chat_input("Ask about your order, delivery, or tracking…")

if prompt:
    # Show user message immediately
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Run model + tools, then show assistant reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = run_turn(prompt, st.session_state.chat_history[:-1])
            st.markdown(reply)
    st.session_state.chat_history.append(
        {"role": "assistant", "content": reply}
    )
