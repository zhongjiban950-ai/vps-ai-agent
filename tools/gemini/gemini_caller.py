#!/usr/bin/env python3
"""Unified Gemini API caller - supports API Key and Service Account auth."""

import json
import sys
import os
import urllib.request
import urllib.error

# Service account support
SA_KEY_PATH = "/root/harmonyols-workspace-3016ac085cd8.json"

# API Keys
API_KEYS = [
    os.environ.get("GOOGLE_API_KEY", ""),
    os.environ.get("GEMINI_API_KEY", ""),
]

MODELS = {
    "flash": "gemini-2.5-flash",
    "pro": "gemini-2.5-pro",
    "3.1": "gemini-3.1-pro-preview",
    "3.1-tools": "gemini-3.1-pro-preview-customtools",
    "3-pro": "gemini-3-pro-preview",
    "3-flash": "gemini-3-flash-preview",
}


def get_sa_token():
    """Get OAuth2 token from service account."""
    try:
        from google.oauth2 import service_account
        import google.auth.transport.requests
        creds = service_account.Credentials.from_service_account_file(
            SA_KEY_PATH,
            scopes=["https://www.googleapis.com/auth/generative-language",
                     "https://www.googleapis.com/auth/cloud-platform"]
        )
        creds.refresh(google.auth.transport.requests.Request())
        return creds.token
    except Exception as e:
        print(f"SA token error: {e}", file=sys.stderr)
        return None


def call_gemini(prompt, model="gemini-2.5-pro", use_sa=False, temperature=0.7, max_tokens=4096):
    """Call Gemini API."""
    url_base = "https://generativelanguage.googleapis.com/v1beta/models"

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
            "topP": 0.9,
        }
    }
    data = json.dumps(body).encode()

    if use_sa:
        token = get_sa_token()
        if not token:
            raise RuntimeError("Failed to get SA token")
        url = f"{url_base}/{model}:generateContent"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    else:
        api_key = next((k for k in API_KEYS if k), None)
        if not api_key:
            raise RuntimeError("No API key found")
        url = f"{url_base}/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}

    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=60)
        result = json.loads(resp.read())
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        err = e.read().decode()[:500]
        raise RuntimeError(f"API error {e.code}: {err}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Gemini API Caller")
    parser.add_argument("prompt", nargs="?", help="Prompt text")
    parser.add_argument("-m", "--model", default="pro", choices=list(MODELS.keys()) + list(MODELS.values()),
                       help="Model shortname or full name")
    parser.add_argument("--sa", action="store_true", help="Use service account instead of API key")
    parser.add_argument("-t", "--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=4096)
    parser.add_argument("--list-models", action="store_true")
    args = parser.parse_args()

    if args.list_models:
        for k, v in MODELS.items():
            print(f"  {k:12s} -> {v}")
        return

    if not args.prompt:
        parser.print_help()
        return

    model = MODELS.get(args.model, args.model)
    print(f"[Model: {model} | SA: {args.sa}]", file=sys.stderr)

    result = call_gemini(args.prompt, model=model, use_sa=args.sa,
                         temperature=args.temperature, max_tokens=args.max_tokens)
    print(result)


if __name__ == "__main__":
    main()
