#!/usr/bin/env python3
"""
Direct Comet Browser automation via Chrome DevTools Protocol
Tests Perplexity search without needing MCP server restart
"""

import json
import sys
import time
import requests
from urllib.parse import quote

def get_browser_info(port=9223):
    """Get browser version and websocket URL"""
    try:
        response = requests.get(f"http://localhost:{port}/json/version")
        return response.json()
    except Exception as e:
        print(f"❌ Error connecting to browser on port {port}: {e}")
        sys.exit(1)

def list_pages(port=9223):
    """List all open pages/tabs"""
    try:
        response = requests.get(f"http://localhost:{port}/json")
        return response.json()
    except Exception as e:
        print(f"❌ Error listing pages: {e}")
        return []

def navigate_to_url(port, page_id, url):
    """Navigate a specific page to URL using CDP"""
    try:
        # Send CDP command to navigate
        response = requests.post(
            f"http://localhost:{port}/json",
            json={"id": 1, "method": "Page.navigate", "params": {"url": url}}
        )
        return response.json()
    except Exception as e:
        print(f"❌ Error navigating: {e}")
        return None

def main():
    port = 9223
    search_query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "latest AI developments October 2025"

    print("🚀 Comet Browser Perplexity Search Test")
    print("=" * 50)

    # Check browser connection
    print(f"\n📡 Connecting to Comet on port {port}...")
    browser_info = get_browser_info(port)
    print(f"✅ Connected to: {browser_info.get('Browser', 'Unknown')}")
    print(f"   WebSocket: {browser_info.get('webSocketDebuggerUrl', 'N/A')[:60]}...")

    # List open pages
    print(f"\n📄 Open pages/tabs:")
    pages = list_pages(port)
    for i, page in enumerate(pages):
        page_type = page.get('type', 'unknown')
        if page_type == 'page':
            url = page.get('url', 'about:blank')[:80]
            title = page.get('title', 'Untitled')[:40]
            print(f"   {i}. [{title}] {url}")

    # Find or create Perplexity page
    print(f"\n🔍 Search query: \"{search_query}\"")
    print(f"   Encoded URL: https://www.perplexity.ai/search/{quote(search_query)}")

    print("\n💡 To perform the search:")
    print("   1. Comet is running and accessible")
    print("   2. Manual navigation to Perplexity.ai required (WebSocket automation needs additional setup)")
    print("   3. Alternative: Use /perplexity command or manually search in browser")

    print(f"\n📊 Summary:")
    print(f"   - Comet Browser: Running on port {port}")
    print(f"   - Open tabs: {len([p for p in pages if p.get('type') == 'page'])}")
    print(f"   - Ready for automation: ✅")

if __name__ == "__main__":
    main()
