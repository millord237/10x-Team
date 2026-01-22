#!/usr/bin/env python3
"""
Workflow Creator - Creates workflow templates from user requests
Developed by Team 10x.in
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
import hashlib
import re

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "output" / "workflows"
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_workflow_id(name: str) -> str:
    """Generate unique workflow ID."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower())[:20]
    return f"wf_{timestamp}_{slug}"


def identify_skills(description: str) -> list:
    """Identify required skills from description."""
    skill_keywords = {
        # Marketing
        "content": "content-marketing",
        "blog": "content-marketing",
        "article": "content-marketing",
        "copy": "copywriting",
        "headline": "copywriting",
        "email": "email-marketing",
        "newsletter": "email-marketing",
        "seo": "seo-optimization",
        "keyword": "seo-optimization",
        "campaign": "campaign-management",
        "analytics": "analytics",

        # Outreach
        "outreach": "outreach/workflow-engine",
        "prospect": "outreach/discovery-engine",
        "linkedin": "outreach/linkedin-adapter",
        "twitter": "outreach/twitter-adapter",
        "instagram": "outreach/instagram-adapter",

        # Landing Page
        "landing": "landing-page",
        "page": "landing-page",
        "website": "landing-page",

        # Design
        "design": "design",
        "visual": "design",
        "brand": "brand-guidelines",
        "logo": "design",
        "image": "ai-multimodal",
        "video": "ai-multimodal",

        # Utility
        "research": "research",
        "brainstorm": "brainstorming",
        "plan": "planning"
    }

    description_lower = description.lower()
    skills = []

    for keyword, skill in skill_keywords.items():
        if keyword in description_lower and skill not in skills:
            skills.append(skill)

    return skills if skills else ["planning"]  # Default to planning


def generate_questions(skills: list, description: str) -> list:
    """Generate clarification questions based on skills."""
    questions = []
    question_id = 1

    # Common questions
    questions.append({
        "id": f"q{question_id}",
        "question": "What is your target audience or ideal customer?",
        "type": "text",
        "required": True
    })
    question_id += 1

    questions.append({
        "id": f"q{question_id}",
        "question": "What is the primary goal or conversion objective?",
        "type": "text",
        "required": True
    })
    question_id += 1

    # Skill-specific questions
    if "outreach" in str(skills):
        questions.append({
            "id": f"q{question_id}",
            "question": "What platforms should be used for outreach? (LinkedIn, Twitter, Instagram, Email)",
            "type": "text",
            "required": True
        })
        question_id += 1

    if "landing-page" in str(skills):
        questions.append({
            "id": f"q{question_id}",
            "question": "What tech stack do you prefer? (HTML, React, Next.js, Astro, Vue)",
            "type": "text",
            "required": False,
            "default": "HTML"
        })
        question_id += 1

    if "design" in str(skills) or "brand" in str(skills):
        questions.append({
            "id": f"q{question_id}",
            "question": "Do you have existing brand guidelines? If yes, where are they located?",
            "type": "text",
            "required": False
        })
        question_id += 1

    if "email-marketing" in str(skills):
        questions.append({
            "id": f"q{question_id}",
            "question": "How many emails should be in the sequence?",
            "type": "number",
            "required": False,
            "default": 5
        })
        question_id += 1

    return questions


def create_steps(skills: list, description: str) -> list:
    """Create workflow steps from identified skills."""
    steps = []
    step_id = 1

    # Always start with planning/research if complex
    if len(skills) > 2:
        steps.append({
            "step_id": step_id,
            "name": "Research & Planning",
            "skill": "planning",
            "action": "analyze_requirements",
            "inputs": {
                "description": description,
                "user_inputs": "{{user_inputs}}"
            },
            "outputs": {
                "plan": f"output/workflows/{{{{workflow_id}}}}/step{step_id}_plan.json"
            },
            "depends_on": [],
            "timeout": 300,
            "retry_count": 2
        })
        step_id += 1

    # Add steps for each skill
    for skill in skills:
        if skill == "planning":
            continue  # Already added above

        step = {
            "step_id": step_id,
            "name": skill.replace("-", " ").replace("/", " - ").title(),
            "skill": skill,
            "action": "execute",
            "inputs": {
                "context": f"{{{{steps.{step_id-1}.outputs}}}}" if step_id > 1 else "{{user_inputs}}",
                "user_inputs": "{{user_inputs}}"
            },
            "outputs": {
                "result": f"output/workflows/{{{{workflow_id}}}}/step{step_id}_output.json"
            },
            "depends_on": [step_id - 1] if step_id > 1 else [],
            "timeout": 600,
            "retry_count": 2
        }
        steps.append(step)
        step_id += 1

    # Always end with output generation
    steps.append({
        "step_id": step_id,
        "name": "Generate Outputs",
        "skill": "workflow-engine",
        "action": "generate_outputs",
        "inputs": {
            "all_steps": "{{steps}}",
            "formats": ["pdf", "json"]
        },
        "outputs": {
            "final": "output/workflows/{{workflow_id}}/final/"
        },
        "depends_on": list(range(1, step_id)),
        "timeout": 300,
        "retry_count": 1
    })

    return steps


def create_workflow(name: str, description: str) -> dict:
    """Create a complete workflow template."""
    workflow_id = generate_workflow_id(name)
    skills = identify_skills(description)
    questions = generate_questions(skills, description)
    steps = create_steps(skills, description)

    workflow = {
        "workflow_id": workflow_id,
        "name": name,
        "description": description,
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "created_by": "orchestrator",
        "status": "draft",

        "metadata": {
            "estimated_duration": f"{len(steps) * 5} minutes",
            "skill_count": len(skills),
            "step_count": len(steps),
            "autonomous": True,
            "developed_by": "Team 10x.in"
        },

        "skills_used": skills,

        "user_inputs": {
            "questions": questions,
            "answers": {},
            "gathered": False
        },

        "steps": steps,

        "outputs": {
            "directory": f"output/workflows/{workflow_id}",
            "formats": ["pdf", "json"],
            "files": []
        },

        "canvas": {
            "visualized": False,
            "exported_at": None,
            "canvas_url": "http://localhost:3001"
        },

        "execution": {
            "started_at": None,
            "completed_at": None,
            "current_step": None,
            "progress_percent": 0
        }
    }

    # Save workflow
    workflow_dir = OUTPUT_DIR / workflow_id
    workflow_dir.mkdir(parents=True, exist_ok=True)

    workflow_file = workflow_dir / "workflow.json"
    with open(workflow_file, "w") as f:
        json.dump(workflow, f, indent=2)

    print(f"Workflow created: {workflow_id}")
    print(f"Saved to: {workflow_file}")

    return workflow


def main():
    if len(sys.argv) < 3:
        print("Usage: python create_workflow.py <name> <description>")
        print("Example: python create_workflow.py 'Marketing Campaign' 'Create a complete marketing campaign for SaaS product'")
        sys.exit(1)

    name = sys.argv[1]
    description = " ".join(sys.argv[2:])

    workflow = create_workflow(name, description)

    # Output as JSON for Claude Code to parse
    print("\n--- WORKFLOW JSON ---")
    print(json.dumps(workflow, indent=2))


if __name__ == "__main__":
    main()
