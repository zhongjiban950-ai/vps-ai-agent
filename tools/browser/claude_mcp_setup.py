#!/usr/bin/env python3
"""Claude.ai MCP connector automation - connect all available integrations."""

import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from browser_agent import BrowserAgent


CLAUDE_SETTINGS_URL = "https://claude.ai/settings/integrations"
CLAUDE_MCP_URL = "https://claude.ai/settings/mcp"


async def check_claude_login(agent: BrowserAgent) -> bool:
    """Check if logged into Claude."""
    await agent.goto("https://claude.ai", wait="networkidle")
    url = await agent.get_url()
    path = await agent.screenshot("claude_check")

    if "login" in url or "oauth" in url:
        print(f"Not logged into Claude. Screenshot: {path}")
        return False
    print(f"Logged into Claude. URL: {url}")
    return True


async def list_mcp_connectors(agent: BrowserAgent):
    """List all available MCP connectors on Claude."""
    await agent.goto(CLAUDE_SETTINGS_URL, wait="networkidle")
    await agent.page.wait_for_timeout(2000)
    path = await agent.screenshot("integrations_page")
    print(f"Integrations page screenshot: {path}")

    text = await agent.get_all_text()
    links = await agent.get_links()
    buttons = await agent.get_buttons()

    print("\n=== Page Text (truncated) ===")
    print(text[:2000])
    print("\n=== Links ===")
    for l in links:
        if any(kw in l['text'].lower() for kw in ['connect', 'integrat', 'mcp', 'enable', 'add']):
            print(f"  [{l['text'][:60]}] -> {l['href']}")
    print("\n=== Buttons ===")
    for b in buttons:
        print(f"  [{b['text'][:60]}] id={b['id']}")

    return text, links, buttons


async def connect_all_mcps(agent: BrowserAgent):
    """Try to connect all available MCP integrations."""
    await agent.goto(CLAUDE_SETTINGS_URL, wait="networkidle")
    await agent.page.wait_for_timeout(3000)
    path = await agent.screenshot("before_connect")
    print(f"Starting MCP connection. Screenshot: {path}")

    # Find all "Connect" buttons
    connect_buttons = await agent.page.query_selector_all('button:has-text("Connect")')
    print(f"Found {len(connect_buttons)} Connect buttons")

    for i, btn in enumerate(connect_buttons):
        try:
            label = await btn.inner_text()
            # Get parent context for the connector name
            parent = await btn.evaluate_handle("el => el.closest('[class]') || el.parentElement")
            parent_text = await parent.evaluate("el => el.innerText")
            connector_name = parent_text.split('\n')[0][:60]

            print(f"\n--- Connecting [{i+1}]: {connector_name} ---")
            await btn.click()
            await agent.page.wait_for_timeout(3000)
            await agent.screenshot(f"connect_{i+1}")

            # Handle OAuth popups
            pages = agent.page.context.pages
            if len(pages) > 1:
                popup = pages[-1]
                print(f"  OAuth popup: {popup.url}")
                await popup.screenshot(path=str(f"/tmp/browser_screenshots/oauth_{i+1}.png"))
                # Try to authorize
                auth_btns = await popup.query_selector_all('button:has-text("Allow"), button:has-text("Authorize"), button:has-text("Accept"), button:has-text("Grant")')
                for ab in auth_btns:
                    try:
                        await ab.click()
                        await popup.wait_for_timeout(2000)
                    except:
                        pass

            print(f"  Done connecting {connector_name}")
        except Exception as e:
            print(f"  Error: {e}")
            await agent.screenshot(f"error_{i+1}")

    await agent.screenshot("after_all_connects")
    print("\nAll connectors processed.")


async def main():
    agent = BrowserAgent(headless=True)
    await agent.start()

    # Load saved cookies
    if await agent.load_cookies("claude"):
        print("Loaded Claude cookies")

    if not await check_claude_login(agent):
        print("\nNeed to login to Claude first.")
        print("Options:")
        print("1. Run with 'login' argument and provide session cookie")
        print("2. Use browser_agent.py interactively to login")
        await agent.stop()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "list":
        await list_mcp_connectors(agent)
    elif len(sys.argv) > 1 and sys.argv[1] == "connect":
        await connect_all_mcps(agent)
    else:
        await list_mcp_connectors(agent)
        print("\n\nRun with 'connect' to auto-connect all MCPs")

    await agent.save_cookies("claude")
    await agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
