"""TI5 Motor Agent — main agent configuration using Anthropic SDK."""

import anthropic
import json
import os
from pathlib import Path

from .system_prompt import SYSTEM_PROMPT

# Tool definitions for the agent
TOOLS = [
    # CAN Control Tools
    {
        "name": "can_open",
        "description": "Open CAN bus device. channel: 0=left arm (IDs 16-22), 1=right arm (IDs 23-29)",
        "input_schema": {
            "type": "object",
            "properties": {
                "channel": {
                    "type": "integer",
                    "description": "CAN channel index (0=left arm, 1=right arm)",
                    "enum": [0, 1]
                }
            },
            "required": ["channel"]
        }
    },
    {
        "name": "can_close",
        "description": "Close CAN bus device. Always call after operations.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "can_send_command",
        "description": "Send a CAN command to a motor. Use cmd codes: 1=enable, 2=disable, 10=status, 11=clear_fault, 28=current, 29=speed, 30=position, 31=trapezoid, 36/37=vel_limit, 82=estop",
        "input_schema": {
            "type": "object",
            "properties": {
                "motor_id": {"type": "integer", "description": "Motor CAN ID (16-29)"},
                "cmd_code": {"type": "integer", "description": "Command code"},
                "param": {"type": "integer", "description": "Optional int32 parameter for write commands"}
            },
            "required": ["motor_id", "cmd_code"]
        }
    },
    {
        "name": "can_read_register",
        "description": "Read a register from a motor. Returns int32 value or null if no response.",
        "input_schema": {
            "type": "object",
            "properties": {
                "motor_id": {"type": "integer", "description": "Motor CAN ID (16-29)"},
                "cmd_code": {"type": "integer", "description": "Read command code (e.g. 8=position, 10=status, 20=voltage, 49=temp, 100=model)"},
                "wait_ms": {"type": "integer", "description": "Timeout in ms (default 100)", "default": 100}
            },
            "required": ["motor_id", "cmd_code"]
        }
    },
    # Test Tools
    {
        "name": "run_sil_test",
        "description": "Run SIL (Software-in-the-Loop) tests. No hardware needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "test_file": {
                    "type": "string",
                    "description": "Test file path relative to scripts/, e.g. 'CAN_Test/tests/test_L0_phase0_can.py'"
                },
                "test_class": {"type": "string", "description": "Optional: specific test class to run"},
                "verbose": {"type": "boolean", "default": True}
            },
            "required": ["test_file"]
        }
    },
    {
        "name": "run_hil_test",
        "description": "Run HIL (Hardware-in-the-Loop) tests. Requires USB-CAN + motor power. CONFIRM with user before running.",
        "input_schema": {
            "type": "object",
            "properties": {
                "test_file": {"type": "string", "description": "Test file path relative to scripts/"},
                "motor_id": {"type": "integer", "description": "Target motor ID for the test"},
                "test_class": {"type": "string", "description": "Optional: specific test class"}
            },
            "required": ["test_file"]
        }
    },
    # Documentation Search Tools
    {
        "name": "search_docs",
        "description": "Search project documentation for a keyword or topic.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (keyword or topic)"},
                "path": {"type": "string", "description": "Directory to search in (default: docs/)", "default": "docs/"}
            },
            "required": ["query"]
        }
    },
    # Web Search Tools
    {
        "name": "search_github",
        "description": "Search ti5robot GitHub repositories for code, issues, or documentation.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "repo": {"type": "string", "description": "Specific repo name (e.g. 'multiMotorInterfaceCPP'). Leave empty for org-wide search."}
            },
            "required": ["query"]
        }
    },
    {
        "name": "search_web",
        "description": "Search the web for TI5 motor, CAN protocol, or CRA motor information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"]
        }
    },
    # Unit Conversion Tool
    {
        "name": "convert_units",
        "description": "Convert between motor control units (degrees, counts, speed, current).",
        "input_schema": {
            "type": "object",
            "properties": {
                "value": {"type": "number", "description": "Input value"},
                "from_unit": {
                    "type": "string",
                    "enum": ["degrees", "radians", "position_counts", "out_position_counts", "deg_per_sec", "speed_cmd", "rpm"],
                    "description": "Source unit"
                },
                "to_unit": {
                    "type": "string",
                    "enum": ["degrees", "radians", "position_counts", "out_position_counts", "deg_per_sec", "speed_cmd", "rpm"],
                    "description": "Target unit"
                },
                "gear_ratio": {"type": "number", "description": "Gear ratio (101 or 121)", "default": 101}
            },
            "required": ["value", "from_unit", "to_unit"]
        }
    }
]


def create_agent():
    """Create and return the TI5 Motor Agent client and tools."""
    client = anthropic.Anthropic()
    return client, TOOLS, SYSTEM_PROMPT


def run_agent_loop(user_message: str, client=None, conversation_history=None):
    """Run one turn of the agent loop.

    Args:
        user_message: The user's input message
        client: Anthropic client (created if None)
        conversation_history: List of messages (created if None)

    Returns:
        tuple: (response_text, conversation_history)
    """
    if client is None:
        client = anthropic.Anthropic()

    if conversation_history is None:
        conversation_history = []

    conversation_history.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=TOOLS,
        messages=conversation_history,
    )

    # Process tool calls in a loop
    while response.stop_reason == "tool_use":
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = _execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        conversation_history.append({"role": "assistant", "content": response.content})
        conversation_history.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversation_history,
        )

    # Extract text response
    response_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            response_text += block.text

    conversation_history.append({"role": "assistant", "content": response.content})

    return response_text, conversation_history


def _execute_tool(tool_name: str, tool_input: dict) -> dict:
    """Execute a tool and return the result."""
    from .tools import can_control, test_runner, doc_search, web_search

    handlers = {
        "can_open": can_control.can_open,
        "can_close": can_control.can_close,
        "can_send_command": can_control.can_send_command,
        "can_read_register": can_control.can_read_register,
        "run_sil_test": test_runner.run_sil_test,
        "run_hil_test": test_runner.run_hil_test,
        "search_docs": doc_search.search_docs,
        "search_github": web_search.search_github,
        "search_web": web_search.search_web,
        "convert_units": can_control.convert_units,
    }

    handler = handlers.get(tool_name)
    if handler is None:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        return handler(**tool_input)
    except Exception as e:
        return {"error": f"{tool_name} failed: {str(e)}"}
