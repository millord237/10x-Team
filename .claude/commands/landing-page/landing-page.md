---
description: Create a high-converting landing page using 10x Team's multi-agent methodology
argument-hint: "[new|resume|list] [project-name]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - TodoWrite
  - Task
  - WebFetch
---

# /landing-page Command

Create professional landing pages using a coordinated team of specialist agents.

## Usage

```
/landing-page new              - Start a new landing page project
/landing-page resume <name>    - Continue an existing project
/landing-page list             - Show all projects
/lp                           - Shortcut for /landing-page new
```

## Contract

**Input**: User provides project requirements through guided questions
**Output**: Complete landing page with HTML/CSS/JS, testing kit, and launch materials

## Execution Steps

### Step 1: Parse Arguments

```
IF argument is "list":
  - Read projects/ folder
  - Display all project folders with status
  - EXIT

IF argument is "resume <name>":
  - Check if projects/<name> exists
  - Read projects/<name>/status.json
  - Resume from last phase
  - CONTINUE to Step 3

IF argument is "new" OR no argument:
  - CONTINUE to Step 2
```

### Step 2: Collect User Requirements

Load the skill file and follow its user input collection process:

```
READ: .claude/skills/landing-page/SKILL.md
FOLLOW: "PHASE 1: USER INPUT COLLECTION" section
```

Ask the user these questions in order:

1. **Project Name**: What should we call this project?
2. **Business Description**: In one sentence, what does your business/product do?
3. **Conversion Goal**: What action do you want visitors to take?
4. **Target Audience**: Who is your ideal customer?
5. **Top 3 Objections**: Why might someone NOT take action?
6. **Brand Personality**: 3-5 adjectives describing your brand feel
7. **Differentiator**: What makes you different from competitors?
8. **Social Proof**: What proof do you have that your product works?
9. **Available Assets**: What assets do you have (screenshots, videos, logos)?
10. **Technical Preferences**: Any specific tech requirements?

**Optional**: Ask if user has a worksheets document to import.

### Step 3: Save User Preferences

```bash
mkdir -p user-preferences
```

Save to `user-preferences/{project-name}.json`:
```json
{
  "projectName": "",
  "businessDescription": "",
  "primaryConversion": "",
  "targetAudience": {},
  "topObjections": [],
  "brandPersonality": [],
  "differentiator": "",
  "socialProof": {},
  "availableAssets": [],
  "technicalPreferences": {},
  "collectedAt": "ISO-DATE",
  "status": "input_complete"
}
```

### Step 4: Create Project Structure

```bash
mkdir -p "projects/{project-name}/requirements"
mkdir -p "projects/{project-name}/copy"
mkdir -p "projects/{project-name}/design"
mkdir -p "projects/{project-name}/build/css"
mkdir -p "projects/{project-name}/build/js"
mkdir -p "projects/{project-name}/testing"
mkdir -p "projects/{project-name}/launch"
```

### Step 5: Execute Agent Pipeline

Use TodoWrite to create master todo list, then execute each phase:

**Phase 1 - Discovery**:
```
READ: .claude/skills/landing-page/agents/discovery-agent.md
EXECUTE: Follow agent instructions
OUTPUT: projects/{name}/requirements/brief.json
```

**Phase 2 - Copywriting**:
```
READ: .claude/skills/landing-page/agents/copywriting-agent.md
EXECUTE: Follow agent instructions
OUTPUT: projects/{name}/copy/headlines.md
OUTPUT: projects/{name}/copy/page-copy.md
```

**Phase 3 - Visual Design**:
```
READ: .claude/skills/landing-page/agents/design-agent.md
EXECUTE: Follow agent instructions
OUTPUT: projects/{name}/design/strategy.md
OUTPUT: projects/{name}/design/colors.json
OUTPUT: projects/{name}/design/typography.json
```

**Phase 4 - Build**:
```
READ: .claude/skills/landing-page/agents/build-agent.md
EXECUTE: Follow agent instructions
OUTPUT: projects/{name}/build/index.html
OUTPUT: projects/{name}/build/css/styles.css
OUTPUT: projects/{name}/build/js/main.js
```

**Phase 5 - QA & Testing**:
```
READ: .claude/skills/landing-page/agents/qa-agent.md
EXECUTE: Follow agent instructions
OUTPUT: projects/{name}/testing/test-kit.md
```

**Phase 6 - Launch**:
```
READ: .claude/skills/landing-page/agents/launch-agent.md
EXECUTE: Follow agent instructions
OUTPUT: projects/{name}/launch/checklist.md
OUTPUT: projects/{name}/launch/maintenance.md
UPDATE: projects/{name}/build/index.html (add SEO)
```

### Step 6: Present Results

Display summary to user:
```
Your landing page is ready!

PROJECT: {projectName}
LOCATION: ./projects/{projectName}/

CREATED:
- Landing Page: build/index.html
- Styles: build/css/styles.css
- Scripts: build/js/main.js
- Testing Kit: testing/test-kit.md
- Launch Checklist: launch/checklist.md

NEXT STEPS:
1. Open build/index.html in a browser to preview
2. Run user tests using testing/test-kit.md
3. Follow launch/checklist.md for deployment
```

## Quality Gates

After each phase, verify:
- [ ] Output files exist
- [ ] Content matches user requirements
- [ ] No placeholder text remaining

If issues found, re-run that phase with corrections.

## Error Handling

```
IF any step fails:
  - Log error to projects/{name}/status.json
  - Notify user of specific issue
  - Offer to retry or skip
```
