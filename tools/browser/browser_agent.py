#!/usr/bin/env python3
"""Browser automation agent using Playwright.
Supports both headless and headed mode for Google/Claude configuration."""

import asyncio
import json
import os
import sys
from pathlib import Path
from playwright.async_api import async_playwright, Page, Browser

SCREENSHOT_DIR = Path("/tmp/browser_screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

COOKIES_DIR = Path(os.path.expanduser("~/.config/omnimind/cookies"))
COOKIES_DIR.mkdir(parents=True, exist_ok=True)


class BrowserAgent:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser: Browser = None
        self.page: Page = None
        self.playwright = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await self.browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        self.page = await context.new_page()
        return self

    async def stop(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def screenshot(self, name="screen"):
        path = SCREENSHOT_DIR / f"{name}.png"
        await self.page.screenshot(path=str(path), full_page=False)
        return str(path)

    async def goto(self, url, wait="load"):
        await self.page.goto(url, wait_until=wait, timeout=30000)
        return await self.screenshot("goto")

    async def click(self, selector):
        await self.page.click(selector, timeout=10000)
        await self.page.wait_for_timeout(1000)
        return await self.screenshot("click")

    async def fill(self, selector, text):
        await self.page.fill(selector, text, timeout=10000)

    async def type_text(self, selector, text, delay=50):
        await self.page.type(selector, text, delay=delay)

    async def press(self, key):
        await self.page.keyboard.press(key)

    async def wait_for(self, selector, timeout=15000):
        await self.page.wait_for_selector(selector, timeout=timeout)

    async def get_text(self, selector):
        el = await self.page.query_selector(selector)
        return await el.inner_text() if el else None

    async def get_all_text(self):
        return await self.page.inner_text("body")

    async def get_url(self):
        return self.page.url

    async def save_cookies(self, name):
        cookies = await self.page.context.cookies()
        path = COOKIES_DIR / f"{name}.json"
        path.write_text(json.dumps(cookies, indent=2))
        return str(path)

    async def load_cookies(self, name):
        path = COOKIES_DIR / f"{name}.json"
        if path.exists():
            cookies = json.loads(path.read_text())
            await self.page.context.add_cookies(cookies)
            return True
        return False

    async def eval_js(self, script):
        return await self.page.evaluate(script)

    async def get_links(self):
        return await self.page.eval_on_selector_all(
            "a[href]",
            "els => els.map(e => ({text: e.innerText.trim(), href: e.href})).filter(e => e.text)"
        )

    async def get_buttons(self):
        return await self.page.eval_on_selector_all(
            "button, [role='button'], input[type='submit']",
            "els => els.map(e => ({text: e.innerText.trim() || e.value || '', id: e.id, class: e.className}))"
        )


async def interactive_session():
    """Run an interactive browser session for manual-like automation."""
    agent = BrowserAgent(headless=True)
    await agent.start()
    print("Browser agent started. Commands: goto <url> | click <sel> | fill <sel> <text> | screenshot | text | links | buttons | quit")

    while True:
        try:
            cmd = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not cmd:
            continue

        parts = cmd.split(maxsplit=1)
        action = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        try:
            if action == "quit":
                break
            elif action == "goto":
                path = await agent.goto(arg)
                print(f"Navigated. Screenshot: {path}")
            elif action == "click":
                path = await agent.click(arg)
                print(f"Clicked. Screenshot: {path}")
            elif action == "fill":
                sel, text = arg.split(maxsplit=1)
                await agent.fill(sel, text)
                print("Filled.")
            elif action == "screenshot":
                path = await agent.screenshot(arg or "manual")
                print(f"Screenshot: {path}")
            elif action == "text":
                print(await agent.get_all_text())
            elif action == "links":
                for link in await agent.get_links():
                    print(f"  [{link['text'][:50]}] -> {link['href']}")
            elif action == "buttons":
                for btn in await agent.get_buttons():
                    print(f"  [{btn['text'][:50]}] id={btn['id']}")
            elif action == "url":
                print(await agent.get_url())
            elif action == "js":
                print(await agent.eval_js(arg))
            elif action == "cookies_save":
                print(await agent.save_cookies(arg or "default"))
            elif action == "cookies_load":
                print(await agent.load_cookies(arg or "default"))
            else:
                print(f"Unknown command: {action}")
        except Exception as e:
            print(f"Error: {e}")

    await agent.stop()
    print("Browser closed.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_session())
    else:
        print("Usage: python browser_agent.py interactive")
        print("  Or import BrowserAgent in your scripts")
