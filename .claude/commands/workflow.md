# /workflow

Autonomous workflow creation and execution command. Developed by Team 10x.in.

## Overview

The `/workflow` command enables Claude Code to:
1. Analyze your request and identify required skills
2. Create a workflow template automatically
3. Ask ALL clarification questions upfront (before execution)
4. Visualize the workflow in TLDraw canvas
5. Execute the workflow autonomously after your approval
6. Generate outputs in multiple formats (PDF, PPT, JSON, MD)

## Usage

```
/workflow <action> [options]
```

## Actions

### Create Workflow
```
/workflow create <description>
/workflow create "Complete marketing campaign for SaaS product"
```

Creates a new workflow from your natural language description.

### List Workflows
```
/workflow list
```

Lists all workflows and their statuses.

### View Workflow
```
/workflow view <workflow_id>
```

Shows workflow details and current status.

### Execute Workflow
```
/workflow execute <workflow_id>
```

Executes an approved workflow autonomously.

### Visualize in Canvas
```
/workflow canvas <workflow_id>
```

Opens the workflow in TLDraw canvas for visual editing.

### Export Outputs
```
/workflow export <workflow_id> <formats>
/workflow export wf_123456 pdf,ppt,json
```

Exports workflow results to specified formats.

## Workflow Lifecycle

```
1. CREATE    → You describe what you want
2. ANALYZE   → Claude identifies required skills
3. CLARIFY   → Claude asks ALL questions upfront
4. TEMPLATE  → Workflow JSON is generated
5. VISUALIZE → Opens in TLDraw canvas (port 3001)
6. APPROVE   → You confirm the workflow
7. EXECUTE   → Runs autonomously (no interruptions)
8. OUTPUT    → Generates PDF, PPT, and other formats
```

## Example Workflows

### Marketing Campaign
```
/workflow create "Create a complete marketing campaign including:
- Research on target audience
- Compelling copy for landing page
- Email sequence (5 emails)
- Social media posts
- Design assets"
```

### Multi-Platform Outreach
```
/workflow create "Set up outreach campaign:
- Find 100 SaaS founders in fintech
- LinkedIn connection + message sequence
- Twitter engagement
- Email follow-up sequence"
```

### Landing Page
```
/workflow create "Build a landing page for my AI writing tool:
- Conversion-focused copy
- Modern design
- Next.js implementation
- SEO optimization"
```

## Output Formats

| Format | Description |
|--------|-------------|
| JSON   | Raw workflow data and results |
| PDF    | Professional report with all content |
| PPT    | Slide presentation of workflow |
| MD     | Markdown documentation |

## Canvas Integration

When you create a workflow, it can be visualized in TLDraw:

1. Run `/workflow canvas <workflow_id>`
2. Canvas opens at http://localhost:3001
3. Review and optionally modify the workflow
4. Click "Export" to send back to Claude Code
5. Confirm to start autonomous execution

## Autonomous Execution

Once approved, the workflow runs without interruption:
- All skills chain together automatically
- Progress is logged in real-time
- Errors are handled gracefully
- Final outputs are generated automatically

## Related Commands

- `/outreach` - Multi-platform outreach automation
- `/landing-page` - Landing page creation
- `/campaign:email` - Email campaigns
- `/content` - Content creation

---

Developed by Team 10x.in
