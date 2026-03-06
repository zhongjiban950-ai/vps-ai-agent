#!/usr/bin/env python3
"""Credential manager - centralized credential access."""

import json
import os
from pathlib import Path

CRED_DIR = Path(os.path.expanduser("~/.config/omnimind"))
SA_KEY = Path("/root/harmonyols-workspace-3016ac085cd8.json")
UNIFIED_PWD = Path(os.path.expanduser("~/.claude/unified_password.txt"))


def get_sa_info():
    """Get service account info."""
    if SA_KEY.exists():
        data = json.loads(SA_KEY.read_text())
        return {
            "project_id": data["project_id"],
            "client_email": data["client_email"],
            "key_file": str(SA_KEY),
        }
    return None


def get_api_keys():
    """Get all configured API keys."""
    keys = {}
    for var in ["GOOGLE_API_KEY", "GEMINI_API_KEY"]:
        val = os.environ.get(var)
        if val:
            keys[var] = f"{val[:12]}...{val[-4:]}"
    return keys


def get_unified_password():
    """Get unified password."""
    if UNIFIED_PWD.exists():
        return UNIFIED_PWD.read_text().strip()
    return None


if __name__ == "__main__":
    print("=== Service Account ===")
    sa = get_sa_info()
    if sa:
        for k, v in sa.items():
            print(f"  {k}: {v}")

    print("\n=== API Keys ===")
    for k, v in get_api_keys().items():
        print(f"  {k}: {v}")

    print("\n=== Unified Password ===")
    pwd = get_unified_password()
    print(f"  {'Set' if pwd else 'Not set'}")
