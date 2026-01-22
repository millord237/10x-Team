#!/usr/bin/env python3
"""
Canvas Sync - Syncs workflows with TLDraw canvas via WebSocket
Developed by Team 10x.in
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime

try:
    import websockets
except ImportError:
    print("Installing websockets...")
    os.system(f"{sys.executable} -m pip install websockets")
    import websockets

# Configuration
WEBSOCKET_URL = os.getenv("CANVAS_WEBSOCKET_URL", "ws://localhost:3002/ws")
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "output" / "workflows"


class CanvasSync:
    """Handles WebSocket communication with TLDraw canvas."""

    def __init__(self, websocket_url: str = WEBSOCKET_URL):
        self.websocket_url = websocket_url
        self.websocket = None
        self.connected = False

    async def connect(self):
        """Connect to WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.websocket_url)
            self.connected = True
            print(f"Connected to canvas at {self.websocket_url}")
            return True
        except Exception as e:
            print(f"Failed to connect to canvas: {e}")
            print("Make sure the canvas server is running: npm run canvas")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            print("Disconnected from canvas")

    async def send_workflow(self, workflow: dict) -> bool:
        """Send workflow to canvas for visualization."""
        if not self.connected:
            if not await self.connect():
                return False

        message = {
            "type": "workflow:create",
            "workflow_id": workflow["workflow_id"],
            "timestamp": datetime.now().isoformat(),
            "data": {
                "name": workflow["name"],
                "description": workflow["description"],
                "steps": workflow["steps"],
                "skills_used": workflow.get("skills_used", []),
                "metadata": workflow.get("metadata", {})
            }
        }

        try:
            await self.websocket.send(json.dumps(message))
            print(f"Workflow sent to canvas: {workflow['workflow_id']}")

            # Wait for acknowledgment
            response = await asyncio.wait_for(self.websocket.recv(), timeout=10)
            response_data = json.loads(response)

            if response_data.get("type") == "workflow:created":
                print(f"Canvas acknowledged workflow creation")
                return True
            else:
                print(f"Unexpected response: {response_data}")
                return False

        except asyncio.TimeoutError:
            print("Timeout waiting for canvas response")
            return False
        except Exception as e:
            print(f"Error sending workflow: {e}")
            return False

    async def wait_for_export(self, workflow_id: str, timeout: int = 300) -> dict:
        """Wait for workflow export from canvas."""
        if not self.connected:
            if not await self.connect():
                return None

        print(f"Waiting for workflow export from canvas...")
        print(f"Please review the workflow in canvas at http://localhost:3001")
        print(f"Click 'Export' when ready to execute")

        try:
            while True:
                message = await asyncio.wait_for(self.websocket.recv(), timeout=timeout)
                data = json.loads(message)

                if data.get("type") == "workflow:export" and data.get("workflow_id") == workflow_id:
                    print(f"Received workflow export from canvas")
                    return data.get("data")

                elif data.get("type") == "workflow:cancel":
                    print(f"Workflow cancelled by user")
                    return None

        except asyncio.TimeoutError:
            print(f"Timeout waiting for export (waited {timeout}s)")
            return None
        except Exception as e:
            print(f"Error waiting for export: {e}")
            return None

    async def update_progress(self, workflow_id: str, step_id: int, status: str, progress: int):
        """Send progress update to canvas."""
        if not self.connected:
            return

        message = {
            "type": "workflow:progress",
            "workflow_id": workflow_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "current_step": step_id,
                "status": status,
                "progress_percent": progress
            }
        }

        try:
            await self.websocket.send(json.dumps(message))
        except Exception as e:
            print(f"Error sending progress update: {e}")

    async def send_completion(self, workflow_id: str, outputs: dict):
        """Send completion notification to canvas."""
        if not self.connected:
            return

        message = {
            "type": "workflow:complete",
            "workflow_id": workflow_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "status": "completed",
                "outputs": outputs
            }
        }

        try:
            await self.websocket.send(json.dumps(message))
            print(f"Completion notification sent to canvas")
        except Exception as e:
            print(f"Error sending completion: {e}")


async def sync_workflow_to_canvas(workflow_path: str):
    """Load workflow and sync to canvas."""
    # Load workflow
    with open(workflow_path, "r") as f:
        workflow = json.load(f)

    sync = CanvasSync()

    try:
        # Send to canvas
        success = await sync.send_workflow(workflow)
        if not success:
            return None

        # Wait for export
        exported = await sync.wait_for_export(workflow["workflow_id"])

        if exported:
            # Update workflow with export
            workflow["canvas"]["visualized"] = True
            workflow["canvas"]["exported_at"] = datetime.now().isoformat()
            workflow["status"] = "approved"

            # Merge any canvas modifications
            if "steps" in exported:
                workflow["steps"] = exported["steps"]

            # Save updated workflow
            with open(workflow_path, "w") as f:
                json.dump(workflow, f, indent=2)

            print(f"Workflow approved and ready for execution")
            return workflow

        return None

    finally:
        await sync.disconnect()


def main():
    if len(sys.argv) < 2:
        print("Usage: python canvas_sync.py <workflow_path>")
        print("Example: python canvas_sync.py output/workflows/wf_123456/workflow.json")
        sys.exit(1)

    workflow_path = sys.argv[1]

    if not os.path.exists(workflow_path):
        print(f"Workflow not found: {workflow_path}")
        sys.exit(1)

    # Run async sync
    result = asyncio.run(sync_workflow_to_canvas(workflow_path))

    if result:
        print("\n--- APPROVED WORKFLOW ---")
        print(json.dumps(result, indent=2))
    else:
        print("\nWorkflow not approved or sync failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
