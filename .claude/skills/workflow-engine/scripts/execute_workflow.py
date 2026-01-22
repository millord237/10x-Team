#!/usr/bin/env python3
"""
Workflow Executor - Executes approved workflows autonomously
Developed by Team 10x.in
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import subprocess
import traceback

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "output" / "workflows"
SKILLS_DIR = ROOT_DIR / ".claude" / "skills"
SCRIPTS_DIR = ROOT_DIR / ".claude" / "scripts"

# Logging
LOG_FORMAT = "[{timestamp}] [{level}] {message}"


class WorkflowExecutor:
    """Executes workflows autonomously."""

    def __init__(self, workflow_path: str):
        self.workflow_path = Path(workflow_path)
        self.workflow = None
        self.log_file = None
        self.canvas_sync = None

    def load_workflow(self):
        """Load workflow from file."""
        with open(self.workflow_path, "r") as f:
            self.workflow = json.load(f)

        # Setup logging
        log_path = self.workflow_path.parent / f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.log_file = open(log_path, "w")

        self.log("INFO", f"Loaded workflow: {self.workflow['workflow_id']}")
        return self.workflow

    def log(self, level: str, message: str):
        """Log message to file and console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = LOG_FORMAT.format(timestamp=timestamp, level=level, message=message)
        print(log_line)
        if self.log_file:
            self.log_file.write(log_line + "\n")
            self.log_file.flush()

    def save_workflow(self):
        """Save workflow state."""
        with open(self.workflow_path, "w") as f:
            json.dump(self.workflow, f, indent=2)

    def validate_workflow(self) -> bool:
        """Validate workflow is ready for execution."""
        if self.workflow["status"] != "approved":
            self.log("ERROR", f"Workflow not approved. Status: {self.workflow['status']}")
            return False

        if not self.workflow["user_inputs"].get("gathered"):
            self.log("ERROR", "User inputs not gathered")
            return False

        return True

    def resolve_template(self, template: str, context: dict) -> str:
        """Resolve template variables."""
        result = template

        # Replace user_inputs
        if "{{user_inputs}}" in result:
            result = result.replace("{{user_inputs}}", json.dumps(context.get("user_inputs", {})))

        # Replace workflow_id
        if "{{workflow_id}}" in result:
            result = result.replace("{{workflow_id}}", self.workflow["workflow_id"])

        # Replace step references
        import re
        step_refs = re.findall(r'\{\{steps\.(\d+)\.outputs\}\}', result)
        for step_id in step_refs:
            step = next((s for s in self.workflow["steps"] if s["step_id"] == int(step_id)), None)
            if step and step.get("outputs"):
                result = result.replace(f"{{{{steps.{step_id}.outputs}}}}", json.dumps(step["outputs"]))

        return result

    def get_skill_executor(self, skill: str) -> str:
        """Get the executor script for a skill."""
        # Check for skill-specific executor
        skill_path = SKILLS_DIR / skill.replace("/", os.sep)
        if skill_path.exists():
            executor = skill_path / "scripts" / "execute.py"
            if executor.exists():
                return str(executor)

        # Check for generic skill script
        scripts_path = SCRIPTS_DIR / f"{skill.replace('/', '_')}.py"
        if scripts_path.exists():
            return str(scripts_path)

        # Return None for built-in handling
        return None

    async def execute_step(self, step: dict, context: dict) -> dict:
        """Execute a single workflow step."""
        step_id = step["step_id"]
        skill = step["skill"]
        action = step["action"]

        self.log("STEP", f"Executing step {step_id}: {step['name']} ({skill})")

        # Update step status
        step["status"] = "running"
        step["started_at"] = datetime.now().isoformat()
        self.save_workflow()

        try:
            # Resolve inputs
            resolved_inputs = {}
            for key, value in step.get("inputs", {}).items():
                if isinstance(value, str):
                    resolved_inputs[key] = self.resolve_template(value, context)
                else:
                    resolved_inputs[key] = value

            # Get executor
            executor = self.get_skill_executor(skill)

            if executor:
                # Run external executor
                result = await self.run_external_executor(executor, action, resolved_inputs, step)
            else:
                # Built-in execution
                result = await self.run_builtin_executor(skill, action, resolved_inputs, step)

            # Update step
            step["status"] = "completed"
            step["completed_at"] = datetime.now().isoformat()
            step["outputs"] = result

            self.log("OK", f"Step {step_id} completed successfully")
            return result

        except Exception as e:
            self.log("ERROR", f"Step {step_id} failed: {str(e)}")
            traceback.print_exc()

            step["status"] = "failed"
            step["error"] = str(e)
            step["completed_at"] = datetime.now().isoformat()

            # Retry logic
            if step.get("retry_count", 0) > 0:
                step["retry_count"] -= 1
                self.log("RETRY", f"Retrying step {step_id} ({step['retry_count']} retries left)")
                return await self.execute_step(step, context)

            raise

        finally:
            self.save_workflow()

    async def run_external_executor(self, executor: str, action: str, inputs: dict, step: dict) -> dict:
        """Run external skill executor."""
        # Prepare input file
        input_file = self.workflow_path.parent / f"step{step['step_id']}_input.json"
        with open(input_file, "w") as f:
            json.dump({"action": action, "inputs": inputs}, f)

        # Run executor
        process = await asyncio.create_subprocess_exec(
            sys.executable, executor, str(input_file),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=step.get("timeout", 600)
        )

        if process.returncode != 0:
            raise Exception(f"Executor failed: {stderr.decode()}")

        # Parse output
        output_file = self.workflow_path.parent / f"step{step['step_id']}_output.json"
        if output_file.exists():
            with open(output_file, "r") as f:
                return json.load(f)

        return {"stdout": stdout.decode(), "status": "completed"}

    async def run_builtin_executor(self, skill: str, action: str, inputs: dict, step: dict) -> dict:
        """Run built-in skill executor."""
        self.log("INFO", f"Using built-in executor for {skill}/{action}")

        # Save inputs as output for now (placeholder)
        output_file = self.workflow_path.parent / f"step{step['step_id']}_output.json"
        result = {
            "skill": skill,
            "action": action,
            "inputs": inputs,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }

        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)

        return result

    async def execute(self):
        """Execute the entire workflow."""
        self.load_workflow()

        if not self.validate_workflow():
            return False

        self.log("INFO", "=" * 50)
        self.log("INFO", f"Starting workflow execution: {self.workflow['name']}")
        self.log("INFO", f"Steps: {len(self.workflow['steps'])}")
        self.log("INFO", "=" * 50)

        # Update workflow status
        self.workflow["status"] = "executing"
        self.workflow["execution"]["started_at"] = datetime.now().isoformat()
        self.save_workflow()

        # Build execution context
        context = {
            "user_inputs": self.workflow["user_inputs"].get("answers", {}),
            "workflow_id": self.workflow["workflow_id"],
            "steps": {}
        }

        # Execute steps in order
        completed_steps = set()

        for step in self.workflow["steps"]:
            step_id = step["step_id"]

            # Check dependencies
            for dep_id in step.get("depends_on", []):
                if dep_id not in completed_steps:
                    self.log("WAIT", f"Waiting for dependency: step {dep_id}")
                    # In a more complex system, we'd wait here
                    # For now, assume sequential execution

            # Execute step
            try:
                result = await self.execute_step(step, context)
                context["steps"][step_id] = {"outputs": result}
                completed_steps.add(step_id)

                # Update progress
                progress = int((len(completed_steps) / len(self.workflow["steps"])) * 100)
                self.workflow["execution"]["progress_percent"] = progress
                self.workflow["execution"]["current_step"] = step_id
                self.save_workflow()

            except Exception as e:
                self.log("ERROR", f"Workflow failed at step {step_id}")
                self.workflow["status"] = "failed"
                self.workflow["execution"]["error"] = str(e)
                self.save_workflow()
                return False

        # Complete workflow
        self.workflow["status"] = "completed"
        self.workflow["execution"]["completed_at"] = datetime.now().isoformat()
        self.workflow["execution"]["progress_percent"] = 100
        self.save_workflow()

        self.log("INFO", "=" * 50)
        self.log("INFO", "Workflow execution completed successfully!")
        self.log("INFO", f"Output directory: {self.workflow_path.parent}")
        self.log("INFO", "=" * 50)

        if self.log_file:
            self.log_file.close()

        return True


async def main():
    if len(sys.argv) < 2:
        print("Usage: python execute_workflow.py <workflow_path>")
        sys.exit(1)

    workflow_path = sys.argv[1]

    if not os.path.exists(workflow_path):
        print(f"Workflow not found: {workflow_path}")
        sys.exit(1)

    executor = WorkflowExecutor(workflow_path)
    success = await executor.execute()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
