# 10x Team

AI-powered marketing automation toolkit built on Claude Code subagent orchestration. Enables autonomous workflows for content creation, campaign management, SEO optimization, lead generation, multi-platform outreach, landing page generation, and browser automation.

**Status:** Phase 6 Complete (27 agents, 73+ commands, 28+ skills, 8 MCP integrations) | Production Ready
**Developed by:** Team 10x.in

## What is Claude Code?

Claude Code is Anthropic's official CLI that orchestrates AI agents for intelligent task automation. Learn more at [Claude Code](https://claude.com/product/claude-code).

## Quick Start

### Prerequisites
- Claude Code installed and configured
- Git and 4GB+ RAM
- macOS 10.15+, Ubuntu 20.04+, or Windows 10+ with WSL

### Installation

```bash
git clone https://github.com/anit-1to10x/10x-Team.git
cd 10x-Team
npm install
claude
```

### Usage Examples

```bash
# Content creation
/plan "Q1 content strategy"
/content/good "landing page copy"
/content/cro "optimize for conversions"

# Campaign management
/campaign:email "Black Friday sequence"
/brainstorm "seasonal campaign ideas"

# SEO & analysis
/seo:keywords "target keyword research"
/scout "analyze competitor pages"

# Outreach (NEW)
/outreach "start outreach workflow"
/outreach:discover "find SaaS founders"
/outreach:linkedin "send connection requests"

# Landing Pages (NEW)
/landing-page new
/lp resume "my-project"

# Browser Automation (NEW)
/browser:start
/browser:track
```

## Key Features

- **27 Specialized Agents** - TOFU, MOFU, BOFU funnel stages + core & support roles
- **73+ Commands** - Content, campaigns, SEO, social, email, analytics, design, fixes
- **28+ Skills** - AI/multimodal, design, strategy, marketing, integrations
- **8 MCP Integrations** - GA4, Google Ads, SendGrid, Discord, Slack, Resend, GSC, ReviewWeb
- **6 Workflow Systems** - Campaign, content, sales, SEO, analytics, orchestration
- **3 Automation Hooks** - Brand enforcement, campaign tracking, approvals
- **Marketing Dashboard** - Full-stack Vue 3 app (32 components, 5 stores, production-ready)
- **Outreach System** - Multi-platform outreach with 108 templates (NEW)
- **Landing Page Generator** - 6-agent workflow with 5 tech stacks (NEW)
- **Browser Extension** - Universal automation with activity tracking (NEW)

## Documentation

- **[Project Overview & PDR](./docs/project-overview-pdr.md)** - Requirements and roadmap
- **[Agent Catalog](./docs/agent-catalog.md)** - 27 agents by funnel stage
- **[Skill Catalog](./docs/skill-catalog.md)** - 28+ available skills
- **[Command Catalog](./docs/command-catalog.md)** - 73+ commands reference
- **[Code Standards](./docs/code-standards.md)** - Development guidelines
- **[System Architecture](./docs/system-architecture.md)** - Design and patterns
- **[Design Guidelines](./docs/design-guidelines.md)** - Brand and visual standards
- **[Project Roadmap](./docs/project-roadmap.md)** - Timeline and phases

## Marketing Agents (27 Total)

**TOFU:** Attraction Specialist, SEO Specialist, Lead Qualifier, Researcher
**MOFU:** Email Wizard, Sale Enabler, Funnel Architect, Content Creator, Continuity Specialist
**BOFU:** Upsell Maximizer
**Core:** Copywriter, Brainstormer, Content Reviewer, Campaign Debugger, Campaign Manager
**Community:** Social Media Manager, Community Manager
**Support:** Planner, Project Manager, Docs Manager, Git Manager, Journal Writer, Scout, Scout External, MCP Manager, UI/UX Designer

## Project Structure

```
10x-Team/
├── .claude/
│   ├── agents/          # 27 marketing agents
│   ├── commands/        # 73+ slash commands (118 files)
│   ├── skills/          # 28+ skills (2,664 files)
│   │   ├── outreach/    # Multi-platform outreach (NEW)
│   │   ├── landing-page/# Landing page generator (NEW)
│   │   └── browser-ext/ # Browser automation (NEW)
│   ├── workflows/       # 10 workflow definitions
│   ├── hooks/           # 7 automation hooks
│   └── templates/       # 108 message templates (NEW)
├── canvas/              # TLDraw workflow designer (NEW)
├── browser-extension/   # Chrome/Edge extension (NEW)
├── docs/                # Core documentation
└── assets/              # Brand assets & examples
```

## Apps & Ports

| App | Port | Description |
|-----|------|-------------|
| Marketing Dashboard | 3000 | Vue 3 campaign management |
| TLDraw Canvas | 3001 | Visual workflow designer |
| WebSocket Server | 3002 | Outreach automation |
| API Server | 3003 | Backend services |

## Marketing Dashboard

Full-stack web application for campaign management and AI automation:

- **Frontend:** Vue 3 + Vite (32 components, 5 Pinia stores)
- **Backend:** Hono + SQLite (5 API routes, 18+ endpoints)
- **Features:** Campaign Kanban, content library, asset gallery, AI enhancement, brand center
- **Security:** API key auth, path traversal protection, XSS prevention
- **Performance:** 62 KB gzipped (68% under 200 KB target)
- **Status:** Production ready (88% test coverage)

**Quick Start:**
```bash
cd .claude/skills/marketing-dashboard
./start.sh              # Dev: localhost:3000 (frontend) + localhost:3457 (API)
./build.sh && ./start-production.sh  # Production
```

## Environment Configuration

Set up MCP integrations for advanced features:

```bash
cp .claude/.env.example .claude/.env

# Required for integrations:
GEMINI_API_KEY=...
GA_ACCESS_TOKEN=...
GOOGLE_ADS_DEVELOPER_TOKEN=...
SENDGRID_API_KEY=...
DISCORD_BOT_TOKEN=...
SLACK_USER_TOKEN=...
```

See [MCP Setup Guide](./docs/mcp-setup-guide.md) for detailed instructions.

## Best Practices

- **Brand Consistency** - Use brand guidelines enforcement hooks
- **Content Quality** - All outputs go through content reviewer
- **Data-Driven** - Track metrics via GA4 integration
- **Documentation** - Keep playbooks and learnings current
- **Testing** - Use /plan variants for scenario testing

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Follow code standards in [CLAUDE.md](./CLAUDE.md)
4. Submit pull request

## Support

- **Documentation:** See `./docs` folder
- **Issues:** [GitHub Issues](https://github.com/anit-1to10x/10x-Team/issues)
- **Website:** [10x.in](https://10x.in)

## License

MIT License - Developed by Team 10x.in
