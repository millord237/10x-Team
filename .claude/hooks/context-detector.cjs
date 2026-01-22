#!/usr/bin/env node
/**
 * Context Detector Hook - Extracts user intent and context for intelligent routing
 * Developed by Team 10x.in
 *
 * This hook analyzes user messages to:
 * 1. Detect user intent (research, create, analyze, etc.)
 * 2. Extract entities (companies, people, platforms)
 * 3. Determine task complexity and required workflow
 * 4. Recommend output formats based on context
 * 5. Trigger appropriate skills and agents
 *
 * Hook Type: UserPromptSubmit
 */

const fs = require('fs');
const path = require('path');

// ============================================================================
// INTENT CLASSIFICATION
// ============================================================================

const INTENTS = {
  // Research & Discovery
  research: {
    patterns: [
      /research\s+/i, /find\s+out/i, /discover\s+/i, /investigate\s+/i,
      /look\s+up/i, /search\s+for/i, /what\s+is/i, /who\s+is/i,
      /tell\s+me\s+about/i, /learn\s+about/i
    ],
    keywords: ['research', 'discover', 'find', 'search', 'lookup', 'investigate'],
    mcp: 'auto', // Depends on depth
    agents: ['discovery-agent', 'scout', 'researcher'],
    skills: ['research', 'docs-seeker'],
    outputs: ['json', 'markdown']
  },

  // Prospect Discovery
  prospect_discovery: {
    patterns: [
      /find\s+\d*\s*prospects/i, /find\s+\d*\s*leads/i,
      /discover\s+\d*\s*(prospects|leads)/i, /prospect\s+list/i,
      /lead\s+(list|generation)/i, /outreach\s+list/i,
      /find\s+\d+\s+(marketers|founders|ctos|ceos|developers)/i
    ],
    keywords: ['prospects', 'leads', 'lead generation', 'outreach list', 'prospect list'],
    mcp: 'websets',
    agents: ['discovery-agent'],
    skills: ['outreach', 'workflow-engine'],
    outputs: ['pdf', 'json', 'csv'],
    workflow: 'prospect-discovery'
  },

  // Content Creation
  create_content: {
    patterns: [
      /create\s+.*content/i, /write\s+.*blog/i, /write\s+.*article/i,
      /create\s+.*post/i, /generate\s+.*content/i, /draft\s+/i
    ],
    keywords: ['create', 'write', 'draft', 'generate', 'content', 'blog', 'article'],
    mcp: 'exa',
    agents: ['content-creator', 'copywriter'],
    skills: ['content-marketing', 'copywriting'],
    outputs: ['markdown', 'json'],
    workflow: 'content-creation'
  },

  // Copywriting
  copywriting: {
    patterns: [
      /write\s+.*copy/i, /create\s+.*headline/i, /ad\s+copy/i,
      /sales\s+copy/i, /cta/i, /tagline/i, /slogan/i
    ],
    keywords: ['copy', 'headline', 'tagline', 'cta', 'sales copy', 'ad copy'],
    mcp: 'exa',
    agents: ['copywriter'],
    skills: ['copywriting'],
    outputs: ['markdown', 'json']
  },

  // Email Marketing
  email_marketing: {
    patterns: [
      /email\s+(campaign|sequence|series)/i, /newsletter/i,
      /drip\s+(campaign|sequence)/i, /email\s+automation/i,
      /cold\s+email/i, /email\s+outreach/i
    ],
    keywords: ['email', 'newsletter', 'drip', 'email campaign', 'email sequence'],
    mcp: 'exa',
    agents: ['email-wizard', 'email-planner'],
    skills: ['email-marketing', 'copywriting'],
    outputs: ['json', 'markdown'],
    workflow: 'email-sequence'
  },

  // Landing Page
  landing_page: {
    patterns: [
      /landing\s+page/i, /create\s+.*page/i, /build\s+.*page/i,
      /conversion\s+page/i, /squeeze\s+page/i, /sales\s+page/i
    ],
    keywords: ['landing page', 'conversion page', 'sales page', 'squeeze page'],
    mcp: 'exa',
    agents: ['design-agent', 'build-agent', 'copywriting-agent'],
    skills: ['landing-page', 'design', 'copywriting'],
    outputs: ['html', 'css', 'js', 'pdf'],
    workflow: 'landing-page-creation'
  },

  // Campaign Management
  campaign: {
    patterns: [
      /campaign\s+(management|launch|create)/i, /launch\s+campaign/i,
      /ad\s+campaign/i, /marketing\s+campaign/i, /run\s+.*campaign/i
    ],
    keywords: ['campaign', 'launch', 'ad campaign', 'marketing campaign'],
    mcp: 'websets',
    agents: ['campaign-manager'],
    skills: ['campaign-management', 'ads-management'],
    outputs: ['pdf', 'json'],
    workflow: 'campaign-launch'
  },

  // Analytics & Reporting
  analytics: {
    patterns: [
      /analytics\s+(report|dashboard)/i, /performance\s+report/i,
      /kpi\s+tracking/i, /metrics\s+report/i, /analyze\s+performance/i,
      /(weekly|monthly|quarterly)\s+report/i
    ],
    keywords: ['analytics', 'report', 'dashboard', 'metrics', 'kpi', 'performance'],
    mcp: null, // Uses Google Analytics MCP
    agents: ['analytics-analyst'],
    skills: ['analytics'],
    outputs: ['pdf', 'json'],
    workflow: 'analytics-report'
  },

  // SEO
  seo: {
    patterns: [
      /seo\s+(audit|analysis|optimization)/i, /keyword\s+research/i,
      /backlink\s+(strategy|building|analysis)/i, /search\s+ranking/i,
      /organic\s+traffic/i
    ],
    keywords: ['seo', 'keyword', 'backlink', 'ranking', 'organic'],
    mcp: 'exa',
    agents: ['seo-specialist'],
    skills: ['seo-optimization'],
    outputs: ['pdf', 'markdown'],
    workflow: 'seo-audit'
  },

  // Design
  design: {
    patterns: [
      /design\s+/i, /create\s+.*mockup/i, /visual\s+design/i,
      /ui\s+design/i, /brand\s+design/i, /logo/i
    ],
    keywords: ['design', 'mockup', 'visual', 'ui', 'brand', 'logo'],
    mcp: 'exa',
    agents: ['design-agent', 'ui-ux-designer'],
    skills: ['design', 'ai-multimodal'],
    outputs: ['png', 'svg', 'pdf']
  },

  // Outreach
  outreach: {
    patterns: [
      /outreach\s+(campaign|sequence)/i, /linkedin\s+outreach/i,
      /twitter\s+dm/i, /cold\s+outreach/i, /multi-channel\s+outreach/i
    ],
    keywords: ['outreach', 'cold email', 'linkedin outreach', 'dm'],
    mcp: 'websets',
    agents: ['campaign-manager'],
    skills: ['outreach', 'email-marketing'],
    outputs: ['json', 'pdf'],
    workflow: 'outreach-sequence'
  },

  // Workflow Creation
  workflow: {
    patterns: [
      /create\s+workflow/i, /workflow\s+/i, /automate\s+/i,
      /multi-step/i, /autonomous/i
    ],
    keywords: ['workflow', 'automate', 'automation', 'multi-step'],
    mcp: 'auto',
    agents: ['orchestrator'],
    skills: ['workflow-engine'],
    outputs: ['json', 'png', 'pdf']
  },

  // Code/Development
  development: {
    patterns: [
      /build\s+/i, /implement\s+/i, /code\s+/i, /develop\s+/i,
      /create\s+.*component/i, /create\s+.*feature/i
    ],
    keywords: ['build', 'implement', 'code', 'develop', 'component', 'feature'],
    mcp: 'exa',
    agents: ['build-agent', 'fullstack-developer'],
    skills: ['frontend-development', 'backend-development'],
    outputs: ['code', 'markdown']
  }
};

// ============================================================================
// ENTITY EXTRACTION
// ============================================================================

const ENTITY_PATTERNS = {
  // Companies/Organizations
  companies: [
    /(?:at|from|for)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)/g,
    /([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+(?:company|inc|corp|ltd)/gi
  ],

  // People/Roles
  roles: [
    /(ceo|cto|cfo|cmo|founder|co-founder|director|manager|vp|head\s+of)/gi,
    /(marketer|developer|engineer|designer|analyst|specialist)/gi
  ],

  // Platforms
  platforms: {
    linkedin: [/linkedin/i],
    twitter: [/twitter/i, /\bx\.com\b/i, /\bx\s+/i],
    instagram: [/instagram/i, /\big\b/i],
    facebook: [/facebook/i, /\bfb\b/i],
    google: [/google/i],
    youtube: [/youtube/i],
    tiktok: [/tiktok/i]
  },

  // Numbers (for result counts, etc.)
  numbers: /\b(\d+)\b/g,

  // Industries
  industries: [
    /(saas|fintech|healthtech|edtech|ai|ml|blockchain|crypto)/gi,
    /(e-commerce|ecommerce|retail|healthcare|finance|education)/gi
  ],

  // Locations
  locations: [
    /(?:in|from|based\s+in)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)/g,
    /(san\s+francisco|new\s+york|london|berlin|singapore|bangalore)/gi
  ]
};

// ============================================================================
// CONTEXT DETECTOR CLASS
// ============================================================================

class ContextDetector {
  constructor(message) {
    this.message = message;
    this.messageLower = message.toLowerCase();
    this.context = {
      intents: [],
      primaryIntent: null,
      entities: {},
      mcp: null,
      agents: [],
      skills: [],
      outputs: [],
      workflow: null,
      complexity: 'simple',
      confidence: 0
    };
  }

  /**
   * Analyze message and extract context
   */
  analyze() {
    this.detectIntents();
    this.extractEntities();
    this.determineComplexity();
    this.generateRecommendations();
    return this.context;
  }

  /**
   * Detect user intents
   */
  detectIntents() {
    const intentScores = {};

    for (const [intentName, config] of Object.entries(INTENTS)) {
      let score = 0;

      // Check patterns
      for (const pattern of config.patterns) {
        if (pattern.test(this.message)) {
          score += 3;
        }
      }

      // Check keywords
      for (const keyword of config.keywords) {
        if (this.messageLower.includes(keyword)) {
          score += 2;
        }
      }

      if (score > 0) {
        intentScores[intentName] = score;
      }
    }

    // Sort intents by score
    const sortedIntents = Object.entries(intentScores)
      .sort((a, b) => b[1] - a[1])
      .map(([name, score]) => ({
        name,
        score,
        confidence: Math.min(score / 10, 1),
        config: INTENTS[name]
      }));

    this.context.intents = sortedIntents;

    if (sortedIntents.length > 0) {
      this.context.primaryIntent = sortedIntents[0];
      this.context.confidence = sortedIntents[0].confidence;
    }
  }

  /**
   * Extract entities from message
   */
  extractEntities() {
    // Extract numbers
    const numbers = [];
    let match;
    const numRegex = /\b(\d+)\b/g;
    while ((match = numRegex.exec(this.message)) !== null) {
      numbers.push(parseInt(match[1]));
    }
    if (numbers.length > 0) {
      this.context.entities.numbers = numbers;
      this.context.entities.maxNumber = Math.max(...numbers);
    }

    // Extract platforms
    const platforms = [];
    for (const [platform, patterns] of Object.entries(ENTITY_PATTERNS.platforms)) {
      for (const pattern of patterns) {
        if (pattern.test(this.message)) {
          platforms.push(platform);
          break;
        }
      }
    }
    if (platforms.length > 0) {
      this.context.entities.platforms = [...new Set(platforms)];
    }

    // Extract roles
    const roles = [];
    for (const pattern of ENTITY_PATTERNS.roles) {
      const roleMatches = this.message.match(pattern);
      if (roleMatches) {
        roles.push(...roleMatches.map(r => r.toLowerCase()));
      }
    }
    if (roles.length > 0) {
      this.context.entities.roles = [...new Set(roles)];
    }

    // Extract industries
    const industries = [];
    for (const pattern of ENTITY_PATTERNS.industries) {
      const indMatches = this.message.match(pattern);
      if (indMatches) {
        industries.push(...indMatches.map(i => i.toLowerCase()));
      }
    }
    if (industries.length > 0) {
      this.context.entities.industries = [...new Set(industries)];
    }
  }

  /**
   * Determine task complexity
   */
  determineComplexity() {
    let complexityScore = 0;

    // Multiple intents = more complex
    if (this.context.intents.length > 1) {
      complexityScore += this.context.intents.length;
    }

    // Large numbers = more complex
    if (this.context.entities.maxNumber && this.context.entities.maxNumber > 10) {
      complexityScore += 2;
    }

    // Multi-step indicators
    const multiStepPatterns = [
      /and\s+then/i, /after\s+that/i, /followed\s+by/i,
      /step\s+\d/i, /first.*then/i, /multi-step/i
    ];
    for (const pattern of multiStepPatterns) {
      if (pattern.test(this.message)) {
        complexityScore += 3;
        break;
      }
    }

    // Workflow keywords
    if (/workflow|automate|autonomous/i.test(this.message)) {
      complexityScore += 3;
    }

    // Multiple platforms
    if (this.context.entities.platforms && this.context.entities.platforms.length > 1) {
      complexityScore += 2;
    }

    // Determine complexity level
    if (complexityScore >= 6) {
      this.context.complexity = 'workflow';
    } else if (complexityScore >= 3) {
      this.context.complexity = 'multi-step';
    } else {
      this.context.complexity = 'simple';
    }
  }

  /**
   * Generate recommendations based on context
   */
  generateRecommendations() {
    if (!this.context.primaryIntent) {
      return;
    }

    const intent = this.context.primaryIntent.config;

    // MCP recommendation
    if (intent.mcp === 'auto') {
      // Auto-detect based on result count
      if (this.context.entities.maxNumber && this.context.entities.maxNumber >= 10) {
        this.context.mcp = 'websets';
      } else {
        this.context.mcp = 'exa';
      }
    } else {
      this.context.mcp = intent.mcp;
    }

    // Agents
    this.context.agents = [...intent.agents];

    // Skills
    this.context.skills = [...intent.skills];

    // Outputs
    this.context.outputs = [...intent.outputs];

    // Workflow
    if (intent.workflow && this.context.complexity !== 'simple') {
      this.context.workflow = intent.workflow;
    }

    // Add workflow-engine for complex tasks
    if (this.context.complexity === 'workflow' && !this.context.skills.includes('workflow-engine')) {
      this.context.skills.push('workflow-engine');
    }
  }

  /**
   * Generate human-readable summary
   */
  generateSummary() {
    const summary = [];

    if (this.context.primaryIntent) {
      summary.push(`Intent: ${this.context.primaryIntent.name} (${(this.context.confidence * 100).toFixed(0)}% confidence)`);
    }

    if (this.context.mcp) {
      summary.push(`MCP: ${this.context.mcp.toUpperCase()}`);
    }

    if (this.context.agents.length > 0) {
      summary.push(`Agents: ${this.context.agents.join(', ')}`);
    }

    if (this.context.skills.length > 0) {
      summary.push(`Skills: ${this.context.skills.join(', ')}`);
    }

    if (this.context.workflow) {
      summary.push(`Workflow: ${this.context.workflow}`);
    }

    summary.push(`Complexity: ${this.context.complexity}`);

    if (this.context.outputs.length > 0) {
      summary.push(`Outputs: ${this.context.outputs.join(', ')}`);
    }

    return summary;
  }
}

// ============================================================================
// MAIN HOOK EXECUTION
// ============================================================================

function main() {
  try {
    // Read user message from stdin
    let input = '';

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

    // Parse input
    let userMessage = '';

    if (input) {
      try {
        const parsed = JSON.parse(input);
        userMessage = parsed.user_message || parsed.message || parsed.prompt || input;
      } catch {
        userMessage = input;
      }
    }

    // Use command line args if no stdin
    if (!userMessage && process.argv.length > 2) {
      userMessage = process.argv.slice(2).join(' ');
    }

    if (!userMessage) {
      process.exit(0);
    }

    // Analyze context
    const detector = new ContextDetector(userMessage);
    const context = detector.analyze();
    const summary = detector.generateSummary();

    // Generate output
    const output = [];

    output.push(`<context-detection>`);

    // Intent
    if (context.primaryIntent) {
      output.push(`<detected-intent>`);
      output.push(`Intent: ${context.primaryIntent.name}`);
      output.push(`Confidence: ${(context.confidence * 100).toFixed(0)}%`);
      output.push(`</detected-intent>`);
    }

    // MCP Selection
    if (context.mcp) {
      output.push(`<mcp-recommendation>`);
      output.push(`Server: ${context.mcp.toUpperCase()}`);
      if (context.mcp === 'websets') {
        output.push(`Reason: Deep research or large result count (${context.entities.maxNumber || '>10'} results)`);
      } else if (context.mcp === 'exa') {
        output.push(`Reason: Quick search or small result count`);
      }
      output.push(`</mcp-recommendation>`);
    }

    // Agents
    if (context.agents.length > 0) {
      output.push(`<recommended-agents>`);
      for (const agent of context.agents) {
        output.push(`- ${agent}`);
      }
      output.push(`</recommended-agents>`);
    }

    // Skills
    if (context.skills.length > 0) {
      output.push(`<activate-skills>`);
      for (const skill of context.skills) {
        output.push(`- ${skill}`);
      }
      output.push(`</activate-skills>`);
    }

    // Entities
    if (Object.keys(context.entities).length > 0) {
      output.push(`<extracted-entities>`);
      if (context.entities.platforms) {
        output.push(`Platforms: ${context.entities.platforms.join(', ')}`);
      }
      if (context.entities.roles) {
        output.push(`Roles: ${context.entities.roles.join(', ')}`);
      }
      if (context.entities.industries) {
        output.push(`Industries: ${context.entities.industries.join(', ')}`);
      }
      if (context.entities.maxNumber) {
        output.push(`Expected Results: ${context.entities.maxNumber}`);
      }
      output.push(`</extracted-entities>`);
    }

    // Workflow
    if (context.workflow) {
      output.push(`<trigger-workflow>`);
      output.push(`Workflow: ${context.workflow}`);
      output.push(`Complexity: ${context.complexity}`);
      output.push(`</trigger-workflow>`);
    }

    // Output Formats
    if (context.outputs.length > 0) {
      output.push(`<output-formats>`);
      output.push(`Primary: ${context.outputs[0].toUpperCase()}`);
      output.push(`Available: ${context.outputs.join(', ')}`);
      output.push(`</output-formats>`);
    }

    output.push(`</context-detection>`);

    console.log(output.join('\n'));

    process.exit(0);

  } catch (error) {
    console.error(`[context-detector] Error: ${error.message}`);
    process.exit(0);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { ContextDetector, INTENTS, ENTITY_PATTERNS };
