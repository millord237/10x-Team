# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Developed by Team 10x.in**

---

## CRITICAL: First-Time Setup Check

**DO NOT DELETE THIS FILE OR .setup-status.json**

Before proceeding with any task, CHECK if the environment is set up:

```
IF file ".setup-status.json" exists AND "installed" = true:
    → Environment is ready, proceed with tasks
ELSE:
    → Tell user to run setup first:
      Windows: .\install.ps1
      Linux/Mac: chmod +x setup.sh && ./setup.sh
```

The setup installs:
- Python 3.12+ with virtual environment
- Node.js 18+ with npm
- All Python dependencies (requirements.txt)
- All Node.js dependencies
- Marketing Dashboard
- TLDraw Canvas
- Output directories

---

ALWAYS activate `claude-code` skill before starting any implementation.

## Project: 10x Team

10x Team is a comprehensive toolkit for sales and marketing automation using Claude Code subagent orchestration. This toolkit enables autonomous marketing workflows for content creation, campaign management, SEO optimization, lead generation, multi-platform outreach, landing page generation, and browser automation.

**Repository:** https://github.com/anit-1to10x/10x-Team
**Target Users:** Indie hackers, small marketing teams, SMB marketing managers

---

## Architecture: Claude Code as the Brain

Claude Code is the central intelligence (orchestrator) that:
1. Analyzes user requests
2. Identifies required skills and agents
3. Asks ALL clarification questions BEFORE starting
4. Creates workflow templates
5. Visualizes workflows in TLDraw canvas
6. Executes workflows AUTONOMOUSLY after approval
7. Generates outputs in multiple formats (PDF, PPT, JSON)

### Orchestrator Agent
Location: `.claude/agents/orchestrator.md`

The Orchestrator coordinates all other agents and skills. It:
- Parses natural language requests
- Chains multiple skills together
- Manages workflow lifecycle
- Handles errors gracefully
- Produces final deliverables

---

## Autonomous Workflow System

### Workflow Lifecycle

```
USER REQUEST
    ↓
[1] ANALYZE - Parse request, identify skills
    ↓
[2] PLAN - Create workflow template (JSON)
    ↓
[3] CLARIFY - Ask ALL questions UPFRONT (not during execution)
    ↓
[4] VISUALIZE - Show in TLDraw canvas (port 3001)
    ↓
[5] APPROVE - User confirms workflow
    ↓
[6] EXECUTE - Run autonomously (NO interruptions)
    ↓
[7] OUTPUT - Generate PDF, PPT, JSON, MD
```

### Key Commands

| Command | Description |
|---------|-------------|
| `/workflow create <desc>` | Create workflow from description |
| `/workflow execute <id>` | Execute approved workflow |
| `/workflow canvas <id>` | Visualize in TLDraw |
| `/outreach` | Multi-platform outreach |
| `/landing-page` | Landing page creation |
| `/campaign:email` | Email campaigns |
| `/browser` | Browser automation |

---

## Project Structure

```
10x-Team/
├── .claude/                    ← KIT OUTPUT (core toolkit)
│   ├── agents/                 ← 40+ agents including orchestrator
│   ├── commands/               ← 150+ slash commands
│   ├── skills/                 ← 75+ integrated skills
│   │   ├── outreach/           ← Multi-platform outreach
│   │   ├── landing-page/       ← Landing page generator
│   │   ├── workflow-engine/    ← Autonomous workflow execution
│   │   └── [marketing skills]  ← Content, SEO, campaigns
│   ├── templates/              ← 108 message templates
│   ├── workflows/              ← Process definitions
│   └── hooks/                  ← Automation hooks
├── canvas/                     ← TLDraw workflow designer
├── browser-extension/          ← Chrome/Edge extension
├── output/                     ← Generated outputs
│   ├── workflows/              ← Workflow results
│   ├── reports/                ← Generated reports
│   ├── pdfs/                   ← PDF exports
│   └── presentations/          ← PPT exports
├── docs/                       ← Documentation
├── assets/                     ← Brand assets & examples
├── install.ps1                 ← Windows setup script
├── setup.sh                    ← Linux/Mac setup script
├── requirements.txt            ← Python dependencies
└── CLAUDE.md                   ← This file
```

---

## Apps & Ports

| App | Port | Description | Start Command |
|-----|------|-------------|---------------|
| Marketing Dashboard | 3000 | Vue 3 campaign management | `npm run dashboard` |
| TLDraw Canvas | 3001 | Visual workflow designer | `npm run canvas` |
| WebSocket Server | 3002 | Outreach automation | `npm run websocket` |
| API Server | 3003 | Backend services | - |

Start all: `npm run start:all` or `.\start-services.ps1`

---

## Key Principle: Dynamic Context

All commands/skills must read from USER's project, never hardcode values:

| Wrong | Right |
|-------|-------|
| `colors: #6366F1` hardcoded | Read from user's `docs/brand-guidelines.md` |
| `font: Inter` hardcoded | Extract via `inject-brand-context.cjs` |
| Specific company voice | Parse user's brand voice docs |

---

## MCP Server Usage Guidelines

**CRITICAL:** Select the appropriate MCP server based on task requirements.

### Exa MCP (`exa-mcp-server`)
**Use for:** Quick searches, fast responses, basic lookups

| Use Case | Example Query |
|----------|---------------|
| Quick company lookup | "What does Acme Corp do?" |
| Fast LinkedIn search | "Find 5 marketers at Google" |
| Simple web search | "Latest trends in SaaS marketing" |
| Basic research | "Who is the CEO of Stripe?" |

**Characteristics:**
- Fast response times (seconds)
- Good for exploratory searches
- Limited depth, broad coverage
- Best for initial discovery

### Websets MCP (`websets-mcp-server`)
**Use for:** Deep research, exhaustive prospect lists, B2B lead generation

| Use Case | Example Query |
|----------|---------------|
| Prospect list building | "Find 50 SaaS founders in fintech" |
| Deep LinkedIn research | "Marketing directors at Series B startups" |
| Enriched lead data | "CTOs at AI companies with 50-200 employees" |
| Competitor analysis | "All competitors of Notion with funding" |

**Characteristics:**
- Exhaustive, thorough results
- AI-powered enrichment
- Verified contact information
- Best for outreach campaigns

### Decision Matrix

```
IF query needs:
  - Quick answer, few results → Use EXA
  - Deep research, many results → Use WEBSETS
  - Basic company info → Use EXA
  - Prospect list for outreach → Use WEBSETS
  - Exploratory search → Use EXA
  - Campaign-ready leads → Use WEBSETS
```

### Auto-Selection Rules

The orchestrator MUST automatically select:

1. **Exa MCP** when user says:
   - "quick search", "find a few", "lookup", "what is"
   - Numbers < 10 prospects
   - General information queries

2. **Websets MCP** when user says:
   - "find prospects", "lead list", "outreach list"
   - Numbers >= 10 prospects
   - "detailed", "enriched", "verified"
   - B2B lead generation tasks

3. **Browser Extension** for authenticated data:
   - Google Ads performance (when logged in)
   - Google Analytics data (when logged in)
   - LinkedIn analytics and actions
   - Any web scraping or browser automation

---

## Browser Extension Capabilities

**The 10x.in Browser Extension handles automation WITHOUT requiring external MCPs.**

### Data Fetching (Authenticated)
| Platform | Capability | How |
|----------|------------|-----|
| Google Ads | Campaign performance, metrics | `FETCH_GOOGLE_ADS` message |
| Google Analytics | GA4 dashboard data | `FETCH_GOOGLE_ANALYTICS` message |
| LinkedIn | Profile analytics, search | `FETCH_LINKEDIN_ANALYTICS` message |

### Browser Automation
| Action | Command | Description |
|--------|---------|-------------|
| Navigate | `NAVIGATE` | Go to any URL |
| Click | `CLICK` | Click elements by selector |
| Type | `TYPE` | Type text with optional humanization |
| Scrape | `SCRAPE` | Extract data from page |
| Screenshot | `SCREENSHOT` | Capture visible tab |
| Full Page | `FULL_PAGE_SCREENSHOT` | Capture entire scrollable page |

### Logging & Audit

**All browser extension actions are logged for debugging and auditing.**

```javascript
// Get logs
chrome.runtime.sendMessage({ type: 'GET_LOGS', filters: { level: 'ACTION' } });

// Export logs as JSON
chrome.runtime.sendMessage({ type: 'EXPORT_LOGS', filters: { startDate: '2024-01-01' } });

// Clear old logs
chrome.runtime.sendMessage({ type: 'CLEAR_LOGS' });
```

Log categories: `MCP`, `SKILL`, `BROWSER`, `WEBSOCKET`, `COMMAND`, `INIT`, `DATA_FETCH`

### When to Use Browser Extension vs MCP

| Task | Use | Reason |
|------|-----|--------|
| Quick web search | Exa MCP | Fast API response |
| Prospect discovery | Websets MCP | Comprehensive lists |
| Google Ads data | Browser Extension | Requires login |
| GA4 analytics | Browser Extension | Requires login |
| LinkedIn scraping | Browser Extension | Requires login |
| General web scraping | Browser Extension | Direct page access |
| Screenshots | Browser Extension | Browser API |

---

## Skill Categories

### Marketing
- `content-marketing` - Content creation
- `copywriting` - Conversion copy
- `email-marketing` - Email sequences
- `seo-optimization` - SEO analysis
- `campaign-management` - Campaign planning

### Outreach
- `outreach/discovery-engine` - AI prospect discovery
- `outreach/linkedin-adapter` - LinkedIn automation
- `outreach/twitter-adapter` - Twitter automation
- `outreach/instagram-adapter` - Instagram automation
- `outreach/workflow-engine` - Multi-step sequences

### Landing Page
- `landing-page` - 6-agent workflow for landing pages

### Design
- `design` - Brand and visual design
- `ai-multimodal` - AI image/video generation

### Workflow
- `workflow-engine` - Autonomous workflow execution

---

## Workflows

- Primary workflow: `./.claude/workflows/primary-workflow.md`
- Development rules: `./.claude/workflows/development-rules.md`
- Orchestration protocols: `./.claude/workflows/orchestration-protocol.md`

**IMPORTANT:** Analyze the skills catalog and activate the skills that are needed for the task.
**IMPORTANT:** For multi-step tasks, use the workflow-engine for autonomous execution.
**IMPORTANT:** Always ask ALL clarification questions BEFORE starting execution.

---

## Output Formats

The system can generate outputs in:
- **JSON** - Raw data and results
- **PDF** - Professional reports (requires reportlab)
- **PPT** - Slide presentations (requires python-pptx)
- **Markdown** - Documentation

Outputs are saved to: `output/workflows/<workflow_id>/`

---

## Virtual Environment

All Python scripts MUST run in the virtual environment:

```bash
# Windows
.\.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

---

**IMPORTANT:** *MUST READ* and *MUST COMPLY* all *INSTRUCTIONS* in this file.

---

**Developed by Team 10x.in** | https://10x.in | https://github.com/anit-1to10x/10x-Team
