# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Developed by Team 10x.in**

---

ALWAYS activate `claude-code` skill before starting any implementation.

## Project: 10x Team

10x Team is a comprehensive toolkit for sales and marketing automation using Claude Code subagent orchestration. This toolkit enables autonomous marketing workflows for content creation, campaign management, SEO optimization, lead generation, multi-platform outreach, landing page generation, and browser automation.

**Repository:** https://github.com/anit-1to10x/10x-Team
**Target Users:** Indie hackers, small marketing teams, SMB marketing managers

## What We're Building (CRITICAL)

**The deliverable is the `.claude/` folder itself** - a reusable kit users install in THEIR projects.

```
OUTPUT: ./10x-Team/.claude/
        ├── agents/      # Marketing subagents
        ├── commands/    # Slash commands
        ├── skills/      # Domain knowledge (including outreach, landing-page, browser-ext)
        ├── workflows/   # Process definitions
        ├── templates/   # Message templates (108 outreach templates)
        └── hooks/       # Automation hooks
```

**NOT building:** A specific marketing project with hardcoded brand values.

### Key Principle: Dynamic Context

All commands/skills must read from USER's project, never hardcode values:

| Wrong | Right |
|-------|-------|
| `colors: #6366F1` hardcoded | Read from user's `docs/brand-guidelines.md` |
| `font: Inter` hardcoded | Extract via `inject-brand-context.cjs` |
| Specific company voice | Parse user's brand voice docs |

### Brand Injection Pattern

```
User runs command → inject-brand-context.cjs → user's docs/ → dynamic prompt
```

**Script:** `.claude/skills/brand-guidelines/scripts/inject-brand-context.cjs`
- Reads: `docs/brand-guidelines.md` (user's file)
- Outputs: Brand context for prompt injection
- Fallback: Graceful message if no brand docs exist

### When Building Kit Components

1. **Commands**: Use `inject-brand-context.cjs` for brand-aware features
2. **Skills**: Reference patterns, not specific values.
   - When scripts got errors, analyze and fix them.
   - When SKILL.md or references got outdated, use `research` and `docs-seeker` skills to research and update them.
3. **Agents**: Activate skills that read user context
4. **Templates**: Use `{{placeholders}}` not hardcoded values

---

## Project Structure

```
10x-Team/
├── .claude/                    ← KIT OUTPUT (what we're building)
│   ├── agents/                 ← Marketing subagents
│   ├── commands/               ← Slash commands (e.g., /brand:update)
│   ├── skills/                 ← Domain knowledge & scripts
│   │   ├── outreach/           ← Multi-platform outreach (NEW)
│   │   ├── landing-page/       ← Landing page generator (NEW)
│   │   └── browser-ext/        ← Browser automation (NEW)
│   ├── templates/              ← 108 message templates (NEW)
│   ├── workflows/              ← Process definitions
│   └── hooks/                  ← Automation hooks
├── canvas/                     ← TLDraw workflow designer (NEW)
├── browser-extension/          ← Chrome/Edge extension (NEW)
├── docs/                       ← Example user docs (for testing)
├── assets/                     ← Example assets (for testing)
└── CLAUDE.md                   ← This file
```

**REMEMBER:**
- **All new skills, agents, commands → go to `.claude/`**
- **docs/, assets/ are example/test files** - they simulate a user's project
- **Scripts must be dynamic** - read from user's `docs/`, never hardcode values

---

## Apps & Ports

| App | Port | Description |
|-----|------|-------------|
| Marketing Dashboard | 3000 | Vue 3 campaign management |
| TLDraw Canvas | 3001 | Visual workflow designer |
| WebSocket Server | 3002 | Outreach automation |
| API Server | 3003 | Backend services |

---

## Role & Responsibilities

Your role is to analyze user marketing requirements, delegate tasks to appropriate marketing-focused sub-agents, and ensure cohesive delivery of marketing assets and campaigns that meet brand guidelines and conversion goals.

## Workflows

- Primary workflow: `./.claude/workflows/primary-workflow.md`
- Development rules: `./.claude/workflows/development-rules.md`
- Orchestration protocols: `./.claude/workflows/orchestration-protocol.md`
- Documentation management: `./.claude/workflows/documentation-management.md`
- And other workflows: `./.claude/workflows/*`

**IMPORTANT:** Analyze the skills catalog and activate the skills that are needed for the task during the process.
**IMPORTANT:** You must follow strictly the development rules in `./.claude/workflows/development-rules.md` file.
**IMPORTANT:** Before you plan or proceed any implementation, always read the `./README.md` file first to get context.
**IMPORTANT:** Sacrifice grammar for the sake of concision when writing reports.
**IMPORTANT:** In reports, list any unresolved questions at the end, if any.
**IMPORTANT**: Date format is configured in `.ck.json` and injected by session hooks via `$CK_PLAN_DATE_FORMAT` env var. Use this format for plan/report naming.

## Documentation Management

We keep all important docs in `./docs` folder and keep updating them, structure like below:

```
./docs
├── project-overview-pdr.md
├── marketing-overview.md
├── brand-guidelines.md
├── design-guidelines.md
├── agent-catalog.md
├── skill-catalog.md
├── command-catalog.md
├── codebase-summary.md
├── system-architecture.md
└── project-roadmap.md
```

**IMPORTANT:** *MUST READ* and *MUST COMPLY* all *INSTRUCTIONS* in project `./CLAUDE.md`, especially *WORKFLOWS* section is *CRITICALLY IMPORTANT*, this rule is *MANDATORY. NON-NEGOTIABLE. NO EXCEPTIONS. MUST REMEMBER AT ALL TIMES!!!*

---

**Developed by Team 10x.in** | https://10x.in | https://github.com/anit-1to10x/10x-Team
