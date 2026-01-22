# /outreach

Multi-platform outreach automation command. Developed by Team 10x.in.

## Usage

```
/outreach [action] [target]
```

## Actions

- `/outreach` - Start interactive outreach workflow
- `/outreach discover <query>` - Find prospects using AI (Exa)
- `/outreach linkedin <action>` - LinkedIn automation (connect, message, engage)
- `/outreach twitter <action>` - Twitter automation (follow, dm, engage)
- `/outreach instagram <action>` - Instagram automation (follow, dm, comment)
- `/outreach email <action>` - Email campaigns (compose, send, sequence)
- `/outreach workflow` - Open visual workflow designer (TLDraw canvas on port 3001)
- `/outreach templates` - Browse 108 pre-built message templates
- `/outreach status` - Check campaign status and rate limits

## Quick Examples

```bash
# Discover prospects
/outreach discover "SaaS founders in fintech"

# LinkedIn outreach
/outreach linkedin connect "https://linkedin.com/in/username"
/outreach linkedin message "Send intro message"

# Email campaign
/outreach email compose "Cold outreach to leads"
/outreach email sequence "7-day nurture sequence"

# Visual workflow
/outreach workflow create
```

## Ports

| Service | Port |
|---------|------|
| TLDraw Canvas | 3001 |
| WebSocket Server | 3002 |

## Skills Used

- `.claude/skills/outreach/*` - All outreach adapters
- `.claude/templates/*` - 108 message templates

---
Developed by Team 10x.in
