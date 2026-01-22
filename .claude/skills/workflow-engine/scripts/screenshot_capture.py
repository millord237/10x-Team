#!/usr/bin/env python3
"""
Screenshot Capture - Captures screenshots via browser extension or Chrome DevTools
Developed by Team 10x.in
"""

import asyncio
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import websockets
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent


class ScreenshotCapture:
    """Captures screenshots using browser extension WebSocket or Selenium."""

    def __init__(self, output_dir: str = None):
        self.output_dir = Path(output_dir) if output_dir else ROOT_DIR / "output" / "screenshots"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.websocket_url = os.getenv("WEBSOCKET_URL", "ws://localhost:3002/ws")

    async def capture_via_websocket(self, url: str = None, full_page: bool = False, filename: str = None) -> str:
        """Capture screenshot via browser extension WebSocket."""
        if not HAS_WEBSOCKETS:
            print("websockets not installed. Install with: pip install websockets")
            return None

        try:
            async with websockets.connect(self.websocket_url) as ws:
                # Identify as workflow engine
                await ws.send(json.dumps({
                    "type": "workflow-engine-connected",
                    "capabilities": ["screenshot-request"]
                }))

                # Wait for acknowledgment
                response = await asyncio.wait_for(ws.recv(), timeout=5)
                print(f"Connected: {response}")

                # If URL provided, navigate first
                if url:
                    await ws.send(json.dumps({
                        "type": "browser-command",
                        "payload": {
                            "action": "NAVIGATE",
                            "url": url
                        }
                    }))
                    # Wait for navigation
                    await asyncio.sleep(2)

                # Request screenshot
                request_type = "full-page-screenshot-request" if full_page else "screenshot-request"
                request_id = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                await ws.send(json.dumps({
                    "type": request_type,
                    "requestId": request_id,
                    "payload": {
                        "format": "png",
                        "quality": 100
                    }
                }))

                # Wait for response
                response = await asyncio.wait_for(ws.recv(), timeout=30)
                data = json.loads(response)

                if data.get("success"):
                    # Save screenshot
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    default_filename = f"screenshot_{timestamp}.png"
                    final_filename = filename or default_filename
                    output_path = self.output_dir / final_filename

                    # Decode base64 and save
                    if data.get("dataUrl"):
                        # Remove data URL prefix
                        base64_data = data["dataUrl"].split(",")[1] if "," in data["dataUrl"] else data["dataUrl"]
                        image_data = base64.b64decode(base64_data)

                        with open(output_path, "wb") as f:
                            f.write(image_data)

                        print(f"Screenshot saved: {output_path}")
                        return str(output_path)
                    elif data.get("screenshots"):
                        # Multiple screenshots for full page
                        paths = []
                        for i, screenshot in enumerate(data["screenshots"]):
                            part_filename = f"screenshot_{timestamp}_part{i+1}.png"
                            part_path = self.output_dir / part_filename

                            base64_data = screenshot["dataUrl"].split(",")[1] if "," in screenshot["dataUrl"] else screenshot["dataUrl"]
                            image_data = base64.b64decode(base64_data)

                            with open(part_path, "wb") as f:
                                f.write(image_data)

                            paths.append(str(part_path))

                        print(f"Full page screenshots saved: {len(paths)} parts")
                        return paths
                else:
                    print(f"Screenshot capture failed: {data.get('error')}")
                    return None

        except asyncio.TimeoutError:
            print("Screenshot capture timed out")
            return None
        except Exception as e:
            print(f"Screenshot capture error: {e}")
            return None

    def capture_via_selenium(self, url: str, full_page: bool = False, filename: str = None) -> str:
        """Capture screenshot using Selenium (fallback method)."""
        if not HAS_SELENIUM:
            print("selenium not installed. Install with: pip install selenium")
            return None

        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")

            driver = webdriver.Chrome(options=chrome_options)

            try:
                driver.get(url)
                # Wait for page to load
                driver.implicitly_wait(5)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                default_filename = f"screenshot_{timestamp}.png"
                final_filename = filename or default_filename
                output_path = self.output_dir / final_filename

                if full_page:
                    # Get full page dimensions
                    total_height = driver.execute_script("return document.body.scrollHeight")
                    total_width = driver.execute_script("return document.body.scrollWidth")

                    # Set window size to full page
                    driver.set_window_size(total_width, total_height)
                    driver.save_screenshot(str(output_path))
                else:
                    driver.save_screenshot(str(output_path))

                print(f"Screenshot saved: {output_path}")
                return str(output_path)

            finally:
                driver.quit()

        except Exception as e:
            print(f"Selenium screenshot error: {e}")
            return None

    def capture_dashboard(self, filename: str = None) -> str:
        """Capture Marketing Dashboard screenshot."""
        dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:3000")
        return self.capture_via_selenium(dashboard_url, full_page=True, filename=filename)

    def capture_canvas(self, filename: str = None) -> str:
        """Capture TLDraw Canvas screenshot."""
        canvas_url = os.getenv("CANVAS_URL", "http://localhost:3001")
        return self.capture_via_selenium(canvas_url, full_page=False, filename=filename)


async def main():
    if len(sys.argv) < 2:
        print("Usage: python screenshot_capture.py <url|dashboard|canvas> [options]")
        print("Options:")
        print("  --full-page    Capture full page screenshot")
        print("  --filename     Output filename")
        print("  --websocket    Use WebSocket method (requires browser extension)")
        print("  --selenium     Use Selenium method (headless browser)")
        print("")
        print("Examples:")
        print("  python screenshot_capture.py https://example.com")
        print("  python screenshot_capture.py dashboard --full-page")
        print("  python screenshot_capture.py canvas --filename workflow_diagram.png")
        sys.exit(1)

    target = sys.argv[1]
    full_page = "--full-page" in sys.argv
    use_websocket = "--websocket" in sys.argv
    use_selenium = "--selenium" in sys.argv

    filename = None
    if "--filename" in sys.argv:
        idx = sys.argv.index("--filename")
        if idx + 1 < len(sys.argv):
            filename = sys.argv[idx + 1]

    capture = ScreenshotCapture()

    if target == "dashboard":
        result = capture.capture_dashboard(filename)
    elif target == "canvas":
        result = capture.capture_canvas(filename)
    elif use_websocket:
        result = await capture.capture_via_websocket(target, full_page, filename)
    else:
        result = capture.capture_via_selenium(target, full_page, filename)

    if result:
        print(f"\n--- SCREENSHOT RESULT ---")
        print(json.dumps({"success": True, "path": result}, indent=2))
    else:
        print("\n--- SCREENSHOT FAILED ---")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
