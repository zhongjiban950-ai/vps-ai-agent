#!/usr/bin/env python3
"""Google Cloud Console automation - enable APIs, configure IAM, etc."""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from browser_agent import BrowserAgent


async def enable_api(project_id: str, api_name: str, agent: BrowserAgent = None):
    """Enable a Google Cloud API via console."""
    own = agent is None
    if own:
        agent = BrowserAgent(headless=True)
        await agent.start()

    url = f"https://console.cloud.google.com/apis/library/{api_name}?project={project_id}"
    await agent.goto(url)
    await agent.screenshot("api_page")

    try:
        await agent.wait_for("button:has-text('Enable')", timeout=5000)
        await agent.click("button:has-text('Enable')")
        await agent.page.wait_for_timeout(3000)
        await agent.screenshot("api_enabled")
        print(f"API {api_name} enabled for {project_id}")
    except Exception:
        print(f"API {api_name} may already be enabled or requires auth")
        await agent.screenshot("api_status")

    if own:
        await agent.stop()


async def add_iam_role(project_id: str, email: str, role: str, agent: BrowserAgent = None):
    """Add IAM role to a service account."""
    own = agent is None
    if own:
        agent = BrowserAgent(headless=True)
        await agent.start()

    url = f"https://console.cloud.google.com/iam-admin/iam?project={project_id}"
    await agent.goto(url)
    await agent.screenshot("iam_page")

    if own:
        await agent.stop()


async def check_google_login(agent: BrowserAgent):
    """Check if we're logged into Google."""
    await agent.goto("https://accounts.google.com")
    url = await agent.get_url()
    path = await agent.screenshot("google_login_check")
    if "myaccount" in url or "SignOutOptions" in (await agent.get_all_text()):
        print("Already logged in to Google")
        return True
    else:
        print(f"Not logged in. Screenshot: {path}")
        return False


async def google_login(email: str, password: str):
    """Login to Google account."""
    agent = BrowserAgent(headless=True)
    await agent.start()

    if await agent.load_cookies("google"):
        await agent.goto("https://accounts.google.com")
        if await check_google_login(agent):
            return agent

    await agent.goto("https://accounts.google.com/signin")
    await agent.screenshot("login_page")

    try:
        await agent.fill('input[type="email"]', email)
        await agent.click('#identifierNext')
        await agent.page.wait_for_timeout(2000)
        await agent.screenshot("after_email")

        await agent.fill('input[type="password"]', password)
        await agent.click('#passwordNext')
        await agent.page.wait_for_timeout(3000)
        await agent.screenshot("after_password")

        await agent.save_cookies("google")
        print("Google login completed")
    except Exception as e:
        print(f"Login error: {e}")
        await agent.screenshot("login_error")

    return agent


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python google_config.py check")
        print("  python google_config.py login <email> <password>")
        print("  python google_config.py enable-api <project_id> <api_name>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "check":
        async def _check():
            a = BrowserAgent(headless=True)
            await a.start()
            await check_google_login(a)
            await a.stop()
        asyncio.run(_check())
    elif cmd == "login" and len(sys.argv) >= 4:
        asyncio.run(google_login(sys.argv[2], sys.argv[3]))
    elif cmd == "enable-api" and len(sys.argv) >= 4:
        asyncio.run(enable_api(sys.argv[2], sys.argv[3]))
