#!/usr/bin/env python3
"""MCP connector status checker and manager."""

# Known MCP connectors available on Claude.ai
KNOWN_CONNECTORS = {
    "Ahrefs": {"type": "api", "status": "available", "description": "SEO analytics"},
    "Canva": {"type": "oauth", "status": "available", "description": "Design tool"},
    "Context7": {"type": "api", "status": "available", "description": "Library docs"},
    "Gmail": {"type": "oauth", "status": "available", "description": "Email"},
    "Google Calendar": {"type": "oauth", "status": "available", "description": "Calendar"},
    "Learning Commons Knowledge Graph": {"type": "api", "status": "available", "description": "Education standards"},
    "Play Sheet Music": {"type": "api", "status": "available", "description": "Music notation"},
    "Slack": {"type": "oauth", "status": "available", "description": "Team messaging"},
}


def list_connectors():
    print(f"{'Connector':<40} {'Type':<8} {'Status':<12} {'Description'}")
    print("-" * 90)
    for name, info in KNOWN_CONNECTORS.items():
        print(f"{name:<40} {info['type']:<8} {info['status']:<12} {info['description']}")


def check_connected():
    """Check which connectors are currently connected (from tool availability)."""
    connected = []
    not_connected = []
    for name in KNOWN_CONNECTORS:
        # This would be checked against actual MCP tool availability
        connected.append(name)  # Placeholder
    return connected, not_connected


if __name__ == "__main__":
    print("=== Known Claude.ai MCP Connectors ===\n")
    list_connectors()
    print(f"\nTotal: {len(KNOWN_CONNECTORS)} connectors")
    print("\nTo connect: use claude_mcp_setup.py or connect manually at https://claude.ai/settings/integrations")
