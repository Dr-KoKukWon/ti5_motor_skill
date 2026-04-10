#!/bin/bash
# TI5 Motor Skill — Installation Script
#
# Installs all three agent configurations:
#   1. AGENTS.md → Claude Code native knowledge
#   2. OMC custom agent → oh-my-claudecode integration
#   3. Agent SDK app → standalone Python application
#
# Usage:
#   bash install.sh [PROJECT_ROOT]
#   PROJECT_ROOT defaults to ~/test-ti5-kkw

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="${1:-$HOME/test-ti5-kkw}"

echo "========================================"
echo "  TI5 Motor Skill Installer"
echo "  Project: $PROJECT_ROOT"
echo "========================================"
echo

# --- Method 1: AGENTS.md ---
echo "[1/3] Installing AGENTS.md..."
if [ -d "$PROJECT_ROOT" ]; then
    cp "$SCRIPT_DIR/AGENTS.md" "$PROJECT_ROOT/AGENTS.md"
    echo "  -> $PROJECT_ROOT/AGENTS.md (Claude Code native)"
else
    echo "  WARN: $PROJECT_ROOT not found, skipping AGENTS.md install"
fi

# --- Method 2: OMC Custom Agent ---
echo "[2/3] Installing OMC custom agent..."
CLAUDE_AGENTS_DIR="$PROJECT_ROOT/.claude/agents"
if [ -d "$PROJECT_ROOT" ]; then
    mkdir -p "$CLAUDE_AGENTS_DIR"
    cp "$SCRIPT_DIR/agents/ti5-motor.md" "$CLAUDE_AGENTS_DIR/ti5-motor.md"
    echo "  -> $CLAUDE_AGENTS_DIR/ti5-motor.md"
else
    echo "  WARN: $PROJECT_ROOT not found, skipping OMC agent install"
fi

# --- Method 3: Agent SDK App ---
echo "[3/3] Installing Agent SDK dependencies..."
if command -v pip3 &>/dev/null; then
    pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet 2>/dev/null || \
    pip3 install --user -r "$SCRIPT_DIR/requirements.txt" --quiet
    echo "  -> anthropic SDK installed"
else
    echo "  WARN: pip3 not found, install manually: pip3 install anthropic"
fi

# Set up environment hint
echo
echo "========================================"
echo "  Installation Complete!"
echo "========================================"
echo
echo "Usage:"
echo
echo "  Method 1 — Claude Code (automatic):"
echo "    cd $PROJECT_ROOT && claude"
echo "    # AGENTS.md is loaded automatically"
echo
echo "  Method 2 — OMC Agent (via Claude Code):"
echo "    Agent({ subagent_type: 'ti5-motor', prompt: '...' })"
echo
echo "  Method 3 — Standalone Agent:"
echo "    export ANTHROPIC_API_KEY='sk-ant-...'"
echo "    export TI5_PROJECT_ROOT='$PROJECT_ROOT'"
echo "    python3 -m ti5_motor_agent"
echo
echo "  Quick test (single query):"
echo "    python3 -m ti5_motor_agent 'Motor 16 status check'"
echo
