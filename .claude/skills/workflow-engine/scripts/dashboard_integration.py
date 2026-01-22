#!/usr/bin/env python3
"""
Dashboard Integration - Integrates workflows with Marketing Dashboard
Developed by Team 10x.in
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import websockets
    import asyncio
    HAS_WEBSOCKETS = True
except ImportError:
    HAS_WEBSOCKETS = False

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent


class DashboardIntegration:
    """Integrates workflow engine with Marketing Dashboard."""

    def __init__(self):
        self.dashboard_url = os.getenv("DASHBOARD_URL", "http://localhost:3000")
        self.api_url = f"{self.dashboard_url}/api"
        self.websocket_url = os.getenv("CANVAS_WEBSOCKET_URL", "ws://localhost:3002/ws")
        self.workflows_dir = ROOT_DIR / "output" / "workflows"

    def push_workflow_to_dashboard(self, workflow_path: str) -> dict:
        """Push workflow data to Marketing Dashboard."""
        if not HAS_REQUESTS:
            print("requests not installed. Install with: pip install requests")
            return {"success": False, "error": "requests not installed"}

        try:
            with open(workflow_path, "r") as f:
                workflow = json.load(f)

            # Format workflow for dashboard
            dashboard_data = {
                "type": "workflow",
                "workflow_id": workflow["workflow_id"],
                "name": workflow["name"],
                "description": workflow["description"],
                "status": workflow["status"],
                "created_at": workflow["created_at"],
                "steps": workflow["steps"],
                "user_inputs": workflow.get("user_inputs", {}),
                "execution": workflow.get("execution", {}),
                "metadata": {
                    "source": "workflow-engine",
                    "developed_by": "Team 10x.in"
                }
            }

            # POST to dashboard API
            response = requests.post(
                f"{self.api_url}/workflows",
                json=dashboard_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.ok:
                print(f"Workflow pushed to dashboard: {workflow['workflow_id']}")
                return {"success": True, "data": response.json()}
            else:
                print(f"Failed to push workflow: {response.status_code}")
                return {"success": False, "error": response.text}

        except requests.exceptions.ConnectionError:
            print("Dashboard not available. Is it running on port 3000?")
            return {"success": False, "error": "Dashboard not available"}
        except Exception as e:
            print(f"Error pushing workflow: {e}")
            return {"success": False, "error": str(e)}

    def get_workflow_from_dashboard(self, workflow_id: str) -> dict:
        """Get workflow data from Marketing Dashboard."""
        if not HAS_REQUESTS:
            return {"success": False, "error": "requests not installed"}

        try:
            response = requests.get(
                f"{self.api_url}/workflows/{workflow_id}",
                timeout=10
            )

            if response.ok:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}

        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Dashboard not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def list_workflows_from_dashboard(self) -> dict:
        """List all workflows from Marketing Dashboard."""
        if not HAS_REQUESTS:
            return {"success": False, "error": "requests not installed"}

        try:
            response = requests.get(
                f"{self.api_url}/workflows",
                timeout=10
            )

            if response.ok:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}

        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Dashboard not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_workflow_status(self, workflow_id: str, status: str, progress: dict = None) -> dict:
        """Update workflow status in Marketing Dashboard."""
        if not HAS_REQUESTS:
            return {"success": False, "error": "requests not installed"}

        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }

            if progress:
                update_data["progress"] = progress

            response = requests.patch(
                f"{self.api_url}/workflows/{workflow_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.ok:
                print(f"Workflow status updated: {workflow_id} -> {status}")
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}

        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Dashboard not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def stream_workflow_updates(self, workflow_id: str, callback=None):
        """Stream workflow updates via WebSocket."""
        if not HAS_WEBSOCKETS:
            print("websockets not installed. Install with: pip install websockets")
            return

        try:
            async with websockets.connect(self.websocket_url) as ws:
                # Subscribe to workflow updates
                await ws.send(json.dumps({
                    "type": "subscribe-workflow",
                    "workflow_id": workflow_id
                }))

                print(f"Subscribed to workflow updates: {workflow_id}")

                while True:
                    message = await ws.recv()
                    data = json.loads(message)

                    if data.get("type") == "workflow-update":
                        print(f"Workflow update: {data}")
                        if callback:
                            callback(data)

                        # Check if workflow is complete
                        if data.get("status") in ["completed", "failed", "cancelled"]:
                            break

        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
        except Exception as e:
            print(f"WebSocket error: {e}")

    def send_notification(self, title: str, message: str, type: str = "info") -> dict:
        """Send notification to Marketing Dashboard."""
        if not HAS_REQUESTS:
            return {"success": False, "error": "requests not installed"}

        try:
            notification_data = {
                "title": title,
                "message": message,
                "type": type,
                "timestamp": datetime.now().isoformat(),
                "source": "workflow-engine"
            }

            response = requests.post(
                f"{self.api_url}/notifications",
                json=notification_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )

            if response.ok:
                return {"success": True}
            else:
                return {"success": False, "error": response.text}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def sync_workflow_outputs(self, workflow_id: str) -> dict:
        """Sync workflow outputs with Marketing Dashboard assets."""
        workflow_dir = self.workflows_dir / workflow_id

        if not workflow_dir.exists():
            return {"success": False, "error": f"Workflow directory not found: {workflow_id}"}

        try:
            synced_assets = []

            # Find all output files
            output_files = list(workflow_dir.glob("*"))

            for output_file in output_files:
                if output_file.is_file():
                    # Determine asset type
                    ext = output_file.suffix.lower()
                    asset_type = self._get_asset_type(ext)

                    if asset_type:
                        # Create asset entry
                        asset_data = {
                            "type": asset_type,
                            "name": output_file.name,
                            "path": str(output_file),
                            "workflow_id": workflow_id,
                            "created_at": datetime.now().isoformat(),
                            "metadata": {
                                "size": output_file.stat().st_size,
                                "extension": ext
                            }
                        }

                        # Push to dashboard
                        if HAS_REQUESTS:
                            try:
                                response = requests.post(
                                    f"{self.api_url}/assets",
                                    json=asset_data,
                                    headers={"Content-Type": "application/json"},
                                    timeout=10
                                )
                                if response.ok:
                                    synced_assets.append(asset_data["name"])
                            except:
                                pass

            print(f"Synced {len(synced_assets)} assets to dashboard")
            return {"success": True, "synced": synced_assets}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _get_asset_type(self, extension: str) -> str:
        """Determine asset type from file extension."""
        type_map = {
            ".json": "data",
            ".md": "document",
            ".pdf": "document",
            ".pptx": "presentation",
            ".ppt": "presentation",
            ".png": "image",
            ".svg": "image",
            ".jpg": "image",
            ".jpeg": "image",
            ".html": "web",
            ".css": "style",
            ".js": "code",
            ".txt": "text"
        }
        return type_map.get(extension, None)


def main():
    if len(sys.argv) < 2:
        print("Usage: python dashboard_integration.py <action> [options]")
        print("Actions:")
        print("  push <workflow_path>       Push workflow to dashboard")
        print("  get <workflow_id>          Get workflow from dashboard")
        print("  list                       List all workflows")
        print("  status <workflow_id> <status>  Update workflow status")
        print("  sync <workflow_id>         Sync workflow outputs to assets")
        print("  notify <title> <message>   Send notification")
        sys.exit(1)

    action = sys.argv[1]
    integration = DashboardIntegration()

    if action == "push" and len(sys.argv) >= 3:
        result = integration.push_workflow_to_dashboard(sys.argv[2])
    elif action == "get" and len(sys.argv) >= 3:
        result = integration.get_workflow_from_dashboard(sys.argv[2])
    elif action == "list":
        result = integration.list_workflows_from_dashboard()
    elif action == "status" and len(sys.argv) >= 4:
        result = integration.update_workflow_status(sys.argv[2], sys.argv[3])
    elif action == "sync" and len(sys.argv) >= 3:
        result = integration.sync_workflow_outputs(sys.argv[2])
    elif action == "notify" and len(sys.argv) >= 4:
        result = integration.send_notification(sys.argv[2], sys.argv[3])
    else:
        print("Invalid action or missing arguments")
        sys.exit(1)

    print("\n--- RESULT ---")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
