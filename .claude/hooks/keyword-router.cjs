#!/usr/bin/env node
/**
 * Keyword Router Hook - Intelligent routing based on user intent
 * Developed by Team 10x.in
 *
 * This hook analyzes user messages and:
 * 1. Detects intent and keywords
 * 2. Selects appropriate MCP (Exa vs Websets)
 * 3. Activates relevant skills/agents
 * 4. Triggers appropriate workflows
 * 5. Recommends output formats (PDF, image, etc.)
 *
 * Hook Type: UserPromptSubmit (runs on every user message)
 */

const fs = require('fs');
const path = require('path');

// ============================================================================
// KEYWORD PATTERNS FOR ROUTING
// ============================================================================

const ROUTING_PATTERNS = {
  // MCP Selection Patterns
  mcp: {
    websets: {
      keywords: [
        'prospects', 'leads', 'lead list', 'lead generation',
        'outreach list', 'campaign list', 'b2b', 'prospect list',
        'detailed research', 'deep research', 'exhaustive',
        'enriched', 'verified contacts', 'comprehensive list',
        'find all', 'linkedin list', 'email list'
      ],
      patterns: [
        /find\s+(\d{2,})\s+/i,  // "find 50+" anything
        /(\d{2,})\s+(prospects|leads|contacts|marketers|founders)/i,
        /list\s+of\s+\d+/i,
        /prospect.*research/i,
        /lead.*generation/i
      ],
      minResultCount: 10
    },
    exa: {
      keywords: [
        'quick search', 'lookup', 'what is', 'who is',
        'find a few', 'quick info', 'brief', 'overview',
        'company info', 'basic research'
      ],
      patterns: [
        /find\s+(\d)\s+/i,  // "find 1-9" anything
        /what\s+(is|does|are)/i,
        /who\s+(is|are)/i,
        /quick\s+\w+/i
      ],
      maxResultCount: 9
    }
  },

  // Agent Selection Patterns
  agents: {
    'discovery-agent': {
      keywords: ['discover', 'research', 'find out', 'investigate', 'explore'],
      patterns: [/research\s+about/i, /find\s+out/i, /investigate/i]
    },
    'scout': {
      keywords: ['search code', 'find file', 'locate', 'where is', 'codebase'],
      patterns: [/where\s+is/i, /find\s+.*file/i, /search\s+.*code/i]
    },
    'copywriter': {
      keywords: ['write copy', 'headline', 'tagline', 'sales copy', 'ad copy', 'cta'],
      patterns: [/write\s+.*copy/i, /create\s+.*headline/i, /ad\s+copy/i]
    },
    'content-creator': {
      keywords: ['blog post', 'article', 'social post', 'content', 'write about'],
      patterns: [/write\s+.*blog/i, /create\s+.*content/i, /social\s+media\s+post/i]
    },
    'email-wizard': {
      keywords: ['email', 'newsletter', 'email sequence', 'drip', 'email campaign'],
      patterns: [/email\s+(sequence|campaign|series)/i, /newsletter/i]
    },
    'seo-specialist': {
      keywords: ['seo', 'keywords', 'ranking', 'search engine', 'organic traffic'],
      patterns: [/seo\s+(analysis|audit|optimize)/i, /keyword\s+research/i]
    },
    'analytics-analyst': {
      keywords: ['analytics', 'metrics', 'kpi', 'performance', 'dashboard', 'report'],
      patterns: [/analytics\s+report/i, /performance\s+metrics/i, /kpi\s+tracking/i]
    },
    'campaign-manager': {
      keywords: ['campaign', 'launch', 'ad campaign', 'marketing campaign'],
      patterns: [/launch\s+campaign/i, /create\s+campaign/i, /campaign\s+management/i]
    },
    'design-agent': {
      keywords: ['design', 'visual', 'mockup', 'ui', 'layout', 'brand'],
      patterns: [/design\s+.*page/i, /create\s+.*mockup/i, /visual\s+design/i]
    },
    'build-agent': {
      keywords: ['build', 'code', 'implement', 'develop', 'create page'],
      patterns: [/build\s+.*page/i, /implement\s+.*feature/i, /code\s+.*component/i]
    }
  },

  // Skill Activation Patterns
  skills: {
    'landing-page': {
      keywords: ['landing page', 'lander', 'conversion page', 'squeeze page'],
      patterns: [/create\s+.*landing/i, /build\s+.*landing/i]
    },
    'outreach': {
      keywords: ['outreach', 'cold email', 'linkedin outreach', 'twitter dm'],
      patterns: [/outreach\s+(campaign|sequence)/i, /(linkedin|twitter|email)\s+outreach/i]
    },
    'email-marketing': {
      keywords: ['email marketing', 'email automation', 'email flow'],
      patterns: [/email\s+(marketing|automation|flow)/i]
    },
    'content-marketing': {
      keywords: ['content strategy', 'content calendar', 'editorial', 'content plan'],
      patterns: [/content\s+(strategy|calendar|plan)/i]
    },
    'seo-optimization': {
      keywords: ['seo optimization', 'seo audit', 'keyword research', 'backlinks'],
      patterns: [/seo\s+(optimization|audit)/i, /backlink\s+(strategy|building)/i]
    },
    'campaign-management': {
      keywords: ['campaign management', 'ad management', 'campaign tracking'],
      patterns: [/campaign\s+(management|tracking|optimization)/i]
    },
    'analytics': {
      keywords: ['analytics', 'tracking', 'reporting', 'dashboard'],
      patterns: [/analytics\s+(setup|tracking|reporting)/i]
    },
    'ads-management': {
      keywords: ['google ads', 'facebook ads', 'meta ads', 'linkedin ads', 'tiktok ads'],
      patterns: [/(google|facebook|meta|linkedin|tiktok)\s+ads/i]
    },
    'affiliate-marketing': {
      keywords: ['affiliate', 'referral program', 'partner program'],
      patterns: [/affiliate\s+(program|marketing)/i, /referral\s+program/i]
    },
    'ai-multimodal': {
      keywords: ['analyze image', 'analyze video', 'transcribe', 'generate image'],
      patterns: [/analyze\s+(image|video|audio)/i, /generate\s+image/i]
    },
    'workflow-engine': {
      keywords: ['workflow', 'automate', 'multi-step', 'autonomous'],
      patterns: [/create\s+workflow/i, /automate\s+.*process/i]
    }
  },

  // Output Format Patterns
  outputs: {
    pdf: {
      keywords: ['pdf', 'report', 'document', 'printable'],
      patterns: [/generate\s+.*pdf/i, /create\s+.*report/i, /export\s+.*pdf/i]
    },
    image: {
      keywords: ['image', 'diagram', 'visualization', 'chart', 'infographic'],
      patterns: [/create\s+.*image/i, /generate\s+.*diagram/i, /visualize/i]
    },
    presentation: {
      keywords: ['presentation', 'slides', 'ppt', 'deck'],
      patterns: [/create\s+.*presentation/i, /generate\s+.*slides/i]
    },
    json: {
      keywords: ['json', 'data', 'export', 'raw data'],
      patterns: [/export\s+.*json/i, /raw\s+data/i]
    },
    markdown: {
      keywords: ['markdown', 'md', 'documentation', 'docs'],
      patterns: [/create\s+.*docs/i, /documentation/i]
    }
  },

  // Workflow Triggers
  workflows: {
    'prospect-discovery': {
      keywords: ['find prospects', 'discover leads', 'lead research'],
      patterns: [/find\s+.*prospects/i, /discover\s+.*leads/i]
    },
    'content-creation': {
      keywords: ['create content', 'content workflow', 'content pipeline'],
      patterns: [/content\s+(creation|workflow|pipeline)/i]
    },
    'campaign-launch': {
      keywords: ['launch campaign', 'campaign setup', 'go live'],
      patterns: [/launch\s+.*campaign/i, /campaign\s+setup/i]
    },
    'landing-page-creation': {
      keywords: ['create landing page', 'build landing page'],
      patterns: [/create\s+.*landing\s+page/i, /build\s+.*landing\s+page/i]
    },
    'outreach-sequence': {
      keywords: ['outreach sequence', 'outreach workflow', 'multi-channel outreach'],
      patterns: [/outreach\s+(sequence|workflow)/i, /multi-channel\s+outreach/i]
    },
    'seo-audit': {
      keywords: ['seo audit', 'site audit', 'technical seo'],
      patterns: [/seo\s+audit/i, /site\s+audit/i]
    },
    'analytics-report': {
      keywords: ['analytics report', 'performance report', 'monthly report'],
      patterns: [/analytics\s+report/i, /(weekly|monthly|quarterly)\s+report/i]
    }
  }
};

// ============================================================================
// ROUTING ENGINE
// ============================================================================

class KeywordRouter {
  constructor(userMessage) {
    this.message = userMessage.toLowerCase();
    this.originalMessage = userMessage;
    this.results = {
      mcp: null,
      agents: [],
      skills: [],
      outputs: [],
      workflows: [],
      confidence: {},
      context: {}
    };
  }

  /**
   * Analyze message and extract routing decisions
   */
  analyze() {
    this.detectMCP();
    this.detectAgents();
    this.detectSkills();
    this.detectOutputs();
    this.detectWorkflows();
    this.extractContext();
    return this.results;
  }

  /**
   * Detect appropriate MCP server
   */
  detectMCP() {
    // Check for Websets indicators
    const websetsConfig = ROUTING_PATTERNS.mcp.websets;
    let websetsScore = 0;

    for (const keyword of websetsConfig.keywords) {
      if (this.message.includes(keyword)) {
        websetsScore += 2;
      }
    }

    for (const pattern of websetsConfig.patterns) {
      if (pattern.test(this.message)) {
        websetsScore += 3;
        // Extract number if present
        const match = this.message.match(/(\d+)/);
        if (match && parseInt(match[1]) >= websetsConfig.minResultCount) {
          websetsScore += 5;
        }
      }
    }

    // Check for Exa indicators
    const exaConfig = ROUTING_PATTERNS.mcp.exa;
    let exaScore = 0;

    for (const keyword of exaConfig.keywords) {
      if (this.message.includes(keyword)) {
        exaScore += 2;
      }
    }

    for (const pattern of exaConfig.patterns) {
      if (pattern.test(this.message)) {
        exaScore += 3;
      }
    }

    // Determine MCP
    if (websetsScore > exaScore && websetsScore >= 2) {
      this.results.mcp = 'websets';
      this.results.confidence.mcp = Math.min(websetsScore / 10, 1);
    } else if (exaScore > websetsScore && exaScore >= 2) {
      this.results.mcp = 'exa';
      this.results.confidence.mcp = Math.min(exaScore / 10, 1);
    } else if (websetsScore > 0 || exaScore > 0) {
      // Default to Exa for ambiguous cases
      this.results.mcp = 'exa';
      this.results.confidence.mcp = 0.5;
    }
  }

  /**
   * Detect agents that should be activated
   */
  detectAgents() {
    for (const [agentName, config] of Object.entries(ROUTING_PATTERNS.agents)) {
      let score = 0;

      for (const keyword of config.keywords) {
        if (this.message.includes(keyword)) {
          score += 2;
        }
      }

      for (const pattern of config.patterns) {
        if (pattern.test(this.message)) {
          score += 3;
        }
      }

      if (score >= 2) {
        this.results.agents.push({
          name: agentName,
          score: score,
          confidence: Math.min(score / 8, 1)
        });
      }
    }

    // Sort by score
    this.results.agents.sort((a, b) => b.score - a.score);
  }

  /**
   * Detect skills that should be activated
   */
  detectSkills() {
    for (const [skillName, config] of Object.entries(ROUTING_PATTERNS.skills)) {
      let score = 0;

      for (const keyword of config.keywords) {
        if (this.message.includes(keyword)) {
          score += 2;
        }
      }

      for (const pattern of config.patterns) {
        if (pattern.test(this.message)) {
          score += 3;
        }
      }

      if (score >= 2) {
        this.results.skills.push({
          name: skillName,
          score: score,
          confidence: Math.min(score / 8, 1)
        });
      }
    }

    // Sort by score
    this.results.skills.sort((a, b) => b.score - a.score);
  }

  /**
   * Detect requested output formats
   */
  detectOutputs() {
    for (const [format, config] of Object.entries(ROUTING_PATTERNS.outputs)) {
      let score = 0;

      for (const keyword of config.keywords) {
        if (this.message.includes(keyword)) {
          score += 2;
        }
      }

      for (const pattern of config.patterns) {
        if (pattern.test(this.message)) {
          score += 3;
        }
      }

      if (score >= 2) {
        this.results.outputs.push({
          format: format,
          score: score
        });
      }
    }

    // Sort by score
    this.results.outputs.sort((a, b) => b.score - a.score);
  }

  /**
   * Detect workflows that should be triggered
   */
  detectWorkflows() {
    for (const [workflowName, config] of Object.entries(ROUTING_PATTERNS.workflows)) {
      let score = 0;

      for (const keyword of config.keywords) {
        if (this.message.includes(keyword)) {
          score += 2;
        }
      }

      for (const pattern of config.patterns) {
        if (pattern.test(this.message)) {
          score += 3;
        }
      }

      if (score >= 3) {
        this.results.workflows.push({
          name: workflowName,
          score: score,
          confidence: Math.min(score / 8, 1)
        });
      }
    }

    // Sort by score
    this.results.workflows.sort((a, b) => b.score - a.score);
  }

  /**
   * Extract additional context from message
   */
  extractContext() {
    // Extract numbers (potential result count)
    const numbers = this.message.match(/\b(\d+)\b/g);
    if (numbers) {
      this.results.context.numbers = numbers.map(n => parseInt(n));
      this.results.context.maxNumber = Math.max(...this.results.context.numbers);
    }

    // Extract platforms mentioned
    const platforms = [];
    const platformPatterns = [
      { name: 'linkedin', patterns: [/linkedin/i] },
      { name: 'twitter', patterns: [/twitter/i, /\bx\b/i] },
      { name: 'instagram', patterns: [/instagram/i, /\big\b/i] },
      { name: 'facebook', patterns: [/facebook/i, /\bfb\b/i] },
      { name: 'google', patterns: [/google/i] },
      { name: 'email', patterns: [/email/i, /gmail/i] }
    ];

    for (const platform of platformPatterns) {
      for (const pattern of platform.patterns) {
        if (pattern.test(this.message)) {
          platforms.push(platform.name);
          break;
        }
      }
    }
    this.results.context.platforms = [...new Set(platforms)];

    // Extract target audience hints
    const audiencePatterns = [
      { type: 'founders', patterns: [/founder/i, /ceo/i, /entrepreneur/i] },
      { type: 'marketers', patterns: [/marketer/i, /marketing/i, /cmo/i] },
      { type: 'developers', patterns: [/developer/i, /engineer/i, /cto/i] },
      { type: 'sales', patterns: [/sales/i, /sdr/i, /ae\b/i] },
      { type: 'executives', patterns: [/executive/i, /c-level/i, /vp\b/i] }
    ];

    const audiences = [];
    for (const audience of audiencePatterns) {
      for (const pattern of audience.patterns) {
        if (pattern.test(this.message)) {
          audiences.push(audience.type);
          break;
        }
      }
    }
    this.results.context.audiences = [...new Set(audiences)];

    // Detect urgency
    const urgencyPatterns = [/urgent/i, /asap/i, /quick/i, /fast/i, /immediately/i];
    this.results.context.urgent = urgencyPatterns.some(p => p.test(this.message));

    // Detect if this is a multi-step task
    const multiStepIndicators = [
      /and\s+then/i, /after\s+that/i, /followed\s+by/i,
      /step\s+\d/i, /first.*then/i, /multi-step/i
    ];
    this.results.context.multiStep = multiStepIndicators.some(p => p.test(this.message));
  }

  /**
   * Generate routing recommendation
   */
  generateRecommendation() {
    const rec = {
      primary: {},
      secondary: [],
      instructions: []
    };

    // Primary recommendation
    if (this.results.workflows.length > 0) {
      rec.primary.type = 'workflow';
      rec.primary.name = this.results.workflows[0].name;
      rec.primary.confidence = this.results.workflows[0].confidence;
    } else if (this.results.skills.length > 0) {
      rec.primary.type = 'skill';
      rec.primary.name = this.results.skills[0].name;
      rec.primary.confidence = this.results.skills[0].confidence;
    } else if (this.results.agents.length > 0) {
      rec.primary.type = 'agent';
      rec.primary.name = this.results.agents[0].name;
      rec.primary.confidence = this.results.agents[0].confidence;
    }

    // MCP recommendation
    if (this.results.mcp) {
      rec.mcp = {
        server: this.results.mcp,
        confidence: this.results.confidence.mcp,
        reason: this.results.mcp === 'websets'
          ? 'Deep research or large result count detected'
          : 'Quick search or small result count detected'
      };
    }

    // Output format recommendation
    if (this.results.outputs.length > 0) {
      rec.outputFormat = this.results.outputs[0].format;
    } else {
      // Default based on task type
      if (rec.primary.name && rec.primary.name.includes('analytics')) {
        rec.outputFormat = 'pdf';
      } else if (rec.primary.name && rec.primary.name.includes('prospect')) {
        rec.outputFormat = 'pdf';
      }
    }

    // Generate instructions
    if (this.results.mcp) {
      rec.instructions.push(
        `USE ${this.results.mcp.toUpperCase()} MCP for research queries`
      );
    }

    if (rec.primary.type === 'workflow') {
      rec.instructions.push(
        `TRIGGER workflow: ${rec.primary.name}`,
        'ASK all clarification questions upfront',
        'EXECUTE autonomously after approval'
      );
    }

    if (this.results.context.multiStep) {
      rec.instructions.push(
        'USE workflow-engine for multi-step execution',
        'CREATE workflow template before execution'
      );
    }

    if (rec.outputFormat === 'pdf') {
      rec.instructions.push(
        'GENERATE branded PDF report with 10x.in branding'
      );
    }

    return rec;
  }
}

// ============================================================================
// MAIN HOOK EXECUTION
// ============================================================================

function main() {
  try {
    // Read user message from stdin (Claude Code hook format)
    let input = '';

    // Check if we have stdin data
    if (process.stdin.isTTY === false) {
      const chunks = [];
      const fd = fs.openSync(0, 'r');
      const buf = Buffer.alloc(1024);
      let n;

      while ((n = fs.readSync(fd, buf)) > 0) {
        chunks.push(buf.slice(0, n));
      }

      input = Buffer.concat(chunks).toString('utf8');
    }

    // Parse input (expecting JSON with user_message)
    let userMessage = '';

    if (input) {
      try {
        const parsed = JSON.parse(input);
        userMessage = parsed.user_message || parsed.message || parsed.prompt || input;
      } catch {
        userMessage = input;
      }
    }

    // If no message, use command line args
    if (!userMessage && process.argv.length > 2) {
      userMessage = process.argv.slice(2).join(' ');
    }

    if (!userMessage) {
      // No input, exit silently
      process.exit(0);
    }

    // Run routing analysis
    const router = new KeywordRouter(userMessage);
    const analysis = router.analyze();
    const recommendation = router.generateRecommendation();

    // Generate output for Claude Code
    const output = [];

    // MCP Selection
    if (recommendation.mcp) {
      output.push(`<mcp-selection>`);
      output.push(`MCP: ${recommendation.mcp.server.toUpperCase()}`);
      output.push(`Confidence: ${(recommendation.mcp.confidence * 100).toFixed(0)}%`);
      output.push(`Reason: ${recommendation.mcp.reason}`);
      output.push(`</mcp-selection>`);
    }

    // Routing Decision
    if (recommendation.primary.type) {
      output.push(`<routing-decision>`);
      output.push(`Type: ${recommendation.primary.type}`);
      output.push(`Name: ${recommendation.primary.name}`);
      output.push(`Confidence: ${(recommendation.primary.confidence * 100).toFixed(0)}%`);
      output.push(`</routing-decision>`);
    }

    // Detected Skills
    if (analysis.skills.length > 0) {
      output.push(`<detected-skills>`);
      for (const skill of analysis.skills.slice(0, 3)) {
        output.push(`- ${skill.name} (${(skill.confidence * 100).toFixed(0)}%)`);
      }
      output.push(`</detected-skills>`);
    }

    // Detected Agents
    if (analysis.agents.length > 0) {
      output.push(`<detected-agents>`);
      for (const agent of analysis.agents.slice(0, 3)) {
        output.push(`- ${agent.name} (${(agent.confidence * 100).toFixed(0)}%)`);
      }
      output.push(`</detected-agents>`);
    }

    // Context
    if (Object.keys(analysis.context).length > 0) {
      output.push(`<user-context>`);
      if (analysis.context.platforms.length > 0) {
        output.push(`Platforms: ${analysis.context.platforms.join(', ')}`);
      }
      if (analysis.context.audiences.length > 0) {
        output.push(`Target Audience: ${analysis.context.audiences.join(', ')}`);
      }
      if (analysis.context.maxNumber) {
        output.push(`Expected Results: ${analysis.context.maxNumber}`);
      }
      if (analysis.context.urgent) {
        output.push(`Urgency: HIGH`);
      }
      if (analysis.context.multiStep) {
        output.push(`Task Type: Multi-step workflow`);
      }
      output.push(`</user-context>`);
    }

    // Instructions
    if (recommendation.instructions.length > 0) {
      output.push(`<routing-instructions>`);
      for (const instruction of recommendation.instructions) {
        output.push(`- ${instruction}`);
      }
      output.push(`</routing-instructions>`);
    }

    // Output format
    if (recommendation.outputFormat) {
      output.push(`<output-format>`);
      output.push(`Recommended: ${recommendation.outputFormat.toUpperCase()}`);
      output.push(`</output-format>`);
    }

    // Print output
    if (output.length > 0) {
      console.log(output.join('\n'));
    }

    process.exit(0);

  } catch (error) {
    // Log error but don't block (fail-open)
    console.error(`[keyword-router] Error: ${error.message}`);
    process.exit(0);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { KeywordRouter, ROUTING_PATTERNS };
