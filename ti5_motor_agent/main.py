#!/usr/bin/env python3
"""TI5 Motor Agent — Interactive CLI entry point.

Usage:
    python -m ti5_motor_agent              # Interactive mode
    python -m ti5_motor_agent "query"      # Single query mode

Environment:
    ANTHROPIC_API_KEY    — Required for Claude API access
    TI5_PROJECT_ROOT     — Path to test-ti5-kkw project (default: ~/test-ti5-kkw)
"""

import sys
import os

def main():
    # Check API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable is required.")
        print("  export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    from .agent import create_agent, run_agent_loop

    client, tools, system_prompt = create_agent()
    conversation_history = []

    # Single query mode
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        response, _ = run_agent_loop(query, client, conversation_history)
        print(response)
        return

    # Interactive mode
    print("=" * 50)
    print("  TI5 Motor Agent v0.1.0")
    print("  Type 'quit' or 'exit' to end session")
    print("=" * 50)
    print()

    while True:
        try:
            user_input = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        try:
            response, conversation_history = run_agent_loop(
                user_input, client, conversation_history
            )
            print(f"\nAgent> {response}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
