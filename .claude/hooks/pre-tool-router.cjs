#!/usr/bin/env node
/**
 * Pre-Tool Router Hook - Intercepts tool calls for intelligent routing
 * Developed by Team 10x.in
 *
 * This hook runs BEFORE tool execution to:
 * 1. Route MCP calls to appropriate server (Exa vs Websets)
 * 2. Inject context into agent calls
 * 3. Activate skills based on tool parameters
 * 4. Set output format expectations
 *
 * Hook Type: PreToolCall
 */

const fs = require('fs');
const path = require('path');

// ============================================================================
// MCP ROUTING CONFIGURATION
// ============================================================================

const MCP_ROUTING = {
  // Tools that should use Websets MCP
  websets: {
    tools: ['prospect_search', 'lead_generation', 'b2b_research', 'contact_enrichment'],
    indicators: {
      keywords: ['prospect', 'lead', 'outreach', 'enriched', 'verified', 'comprehensive'],
      minResults: 10,
      intents: ['lead_generation', 'prospect_list', 'outreach_campaign']
    }
  },

  // Tools that should use Exa MCP
  exa: {
    tools: ['web_search', 'quick_lookup', 'company_info', 'person_search'],
    indicators: {
      keywords: ['quick', 'lookup', 'what is', 'who is', 'find a few'],
      maxResults: 9,
      intents: ['research', 'exploration', 'information']
    }
  },

  // Tools that should use specific MCPs
  toolToMcp: {
    'search': 'auto',           // Auto-detect based on query
    'find_prospects': 'websets',
    'find_leads': 'websets',
    'prospect_research': 'websets',
    'web_search': 'exa',
    'quick_search': 'exa',
    'company_lookup': 'exa',
    'linkedin_search': 'auto',   // Based on result count
    'twitter_search': 'exa',
    'google_search': 'exa'
  }
};

// ============================================================================
// AGENT CONTEXT INJECTION
// ============================================================================

const AGENT_CONTEXT = {
  // Context to inject based on agent type
  'discovery-agent': {
    mcpPreference: 'websets',
    skills: ['outreach', 'research'],
    outputFormats: ['json', 'pdf'],
    instructions: [
      'Use Websets MCP for exhaustive prospect discovery',
      'Enrich all contacts with available data',
      'Generate branded PDF report on completion'
    ]
  },

  'scout': {
    mcpPreference: 'exa',
    skills: ['research', 'docs-seeker'],
    outputFormats: ['json', 'markdown'],
    instructions: [
      'Use Exa MCP for quick codebase research',
      'Use Glob/Grep for file searches',
      'Provide concise summaries'
    ]
  },

  'analytics-analyst': {
    mcpPreference: null,  // Uses Google Analytics MCP
    skills: ['analytics'],
    outputFormats: ['pdf', 'json'],
    instructions: [
      'Use Google Analytics MCP for metrics',
      'Generate visual dashboards',
      'Create branded PDF reports'
    ]
  },

  'copywriter': {
    mcpPreference: 'exa',
    skills: ['copywriting', 'content-marketing'],
    outputFormats: ['markdown', 'json'],
    instructions: [
      'Use Exa MCP for competitor research',
      'Follow brand guidelines from assets/',
      'Apply conversion copywriting formulas'
    ]
  },

  'email-wizard': {
    mcpPreference: 'exa',
    skills: ['email-marketing', 'copywriting'],
    outputFormats: ['json', 'markdown'],
    instructions: [
      'Use Exa MCP for email template research',
      'Follow email marketing best practices',
      'Generate sequence templates'
    ]
  },

  'seo-specialist': {
    mcpPreference: 'exa',
    skills: ['seo-optimization', 'content-marketing'],
    outputFormats: ['pdf', 'json'],
    instructions: [
      'Use Exa MCP for keyword research',
      'Analyze competitor SEO strategies',
      'Generate SEO audit reports'
    ]
  },

  'campaign-manager': {
    mcpPreference: 'websets',
    skills: ['campaign-management', 'ads-management', 'analytics'],
    outputFormats: ['pdf', 'json'],
    instructions: [
      'Use Websets MCP for audience research',
      'Track campaign metrics',
      'Generate performance reports'
    ]
  }
};

// ============================================================================
// SKILL ACTIVATION RULES
// ============================================================================

const SKILL_ACTIVATION = {
  // Auto-activate skills based on tool usage
  'prospect_search': ['outreach', 'workflow-engine'],
  'lead_generation': ['outreach', 'email-marketing'],
  'landing_page_create': ['landing-page', 'design', 'copywriting'],
  'email_campaign': ['email-marketing', 'copywriting'],
  'seo_audit': ['seo-optimization', 'analytics'],
  'content_create': ['content-marketing', 'copywriting'],
  'ad_campaign': ['ads-management', 'campaign-management'],
  'analytics_report': ['analytics', 'workflow-engine']
};

// ============================================================================
// OUTPUT FORMAT RULES
// ============================================================================

const OUTPUT_RULES = {
  // Default output formats by task type
  taskToOutput: {
    'prospect_discovery': { formats: ['pdf', 'json', 'csv'], primary: 'pdf' },
    'analytics_report': { formats: ['pdf', 'json'], primary: 'pdf' },
    'seo_audit': { formats: ['pdf', 'markdown'], primary: 'pdf' },
    'content_creation': { formats: ['markdown', 'json'], primary: 'markdown' },
    'landing_page': { formats: ['html', 'css', 'js', 'pdf'], primary: 'html' },
    'email_campaign': { formats: ['json', 'markdown'], primary: 'json' },
    'workflow_execution': { formats: ['json', 'pdf', 'png'], primary: 'json' }
  },

  // Branding requirements
  branding: {
    pdfReports: true,
    brandName: '10x.in',
    logoPath: 'assets/brand/logo.png',
    colorPrimary: '#6366F1',
    colorSecondary: '#1a1a2e'
  }
};

// ============================================================================
// PRE-TOOL ROUTER CLASS
// ============================================================================

class PreToolRouter {
  constructor(toolCall) {
    this.toolName = toolCall.name || toolCall.tool || '';
    this.toolParams = toolCall.params || toolCall.parameters || {};
    this.context = toolCall.context || {};
    this.routing = {
      mcp: null,
      skills: [],
      outputFormat: null,
      instructions: [],
      injectedContext: {}
    };
  }

  /**
   * Process tool call and generate routing
   */
  process() {
    this.routeMcp();
    this.activateSkills();
    this.determineOutput();
    this.generateInstructions();
    return this.routing;
  }

  /**
   * Route to appropriate MCP server
   */
  routeMcp() {
    // Check direct tool-to-MCP mapping
    if (MCP_ROUTING.toolToMcp[this.toolName]) {
      const mapping = MCP_ROUTING.toolToMcp[this.toolName];

      if (mapping !== 'auto') {
        this.routing.mcp = mapping;
        return;
      }
    }

    // Auto-detect based on parameters
    const query = this.toolParams.query || this.toolParams.search || '';
    const resultCount = this.toolParams.limit || this.toolParams.count || 0;

    // Check for Websets indicators
    let websetsScore = 0;

    for (const keyword of MCP_ROUTING.websets.indicators.keywords) {
      if (query.toLowerCase().includes(keyword)) {
        websetsScore += 2;
      }
    }

    if (resultCount >= MCP_ROUTING.websets.indicators.minResults) {
      websetsScore += 5;
    }

    // Check for Exa indicators
    let exaScore = 0;

    for (const keyword of MCP_ROUTING.exa.indicators.keywords) {
      if (query.toLowerCase().includes(keyword)) {
        exaScore += 2;
      }
    }

    if (resultCount > 0 && resultCount <= MCP_ROUTING.exa.indicators.maxResults) {
      exaScore += 3;
    }

    // Determine MCP
    if (websetsScore > exaScore) {
      this.routing.mcp = 'websets';
    } else {
      this.routing.mcp = 'exa';
    }
  }

  /**
   * Activate relevant skills
   */
  activateSkills() {
    // Check tool-to-skill mapping
    if (SKILL_ACTIVATION[this.toolName]) {
      this.routing.skills = [...SKILL_ACTIVATION[this.toolName]];
    }

    // Add skills based on context
    if (this.context.workflow) {
      this.routing.skills.push('workflow-engine');
    }

    if (this.context.needsReport) {
      this.routing.skills.push('analytics');
    }

    // Deduplicate
    this.routing.skills = [...new Set(this.routing.skills)];
  }

  /**
   * Determine output format
   */
  determineOutput() {
    // Check for explicit format request
    if (this.toolParams.format || this.toolParams.outputFormat) {
      this.routing.outputFormat = this.toolParams.format || this.toolParams.outputFormat;
      return;
    }

    // Determine based on task type
    for (const [taskType, config] of Object.entries(OUTPUT_RULES.taskToOutput)) {
      if (this.toolName.includes(taskType) || (this.context.taskType === taskType)) {
        this.routing.outputFormat = config.primary;
        this.routing.availableFormats = config.formats;
        break;
      }
    }

    // Default to JSON
    if (!this.routing.outputFormat) {
      this.routing.outputFormat = 'json';
    }
  }

  /**
   * Generate routing instructions
   */
  generateInstructions() {
    // MCP instruction
    if (this.routing.mcp) {
      this.routing.instructions.push(
        `USE ${this.routing.mcp.toUpperCase()} MCP for this operation`
      );
    }

    // Skill instructions
    if (this.routing.skills.length > 0) {
      this.routing.instructions.push(
        `ACTIVATE skills: ${this.routing.skills.join(', ')}`
      );
    }

    // Output instructions
    if (this.routing.outputFormat === 'pdf') {
      this.routing.instructions.push(
        `GENERATE branded PDF with ${OUTPUT_RULES.branding.brandName} branding`
      );
    }

    // Add workflow instruction if multi-step
    if (this.context.multiStep) {
      this.routing.instructions.push(
        'CREATE workflow template before execution',
        'ASK all clarification questions upfront',
        'EXECUTE autonomously after approval'
      );
    }
  }

  /**
   * Inject context for agent
   */
  injectAgentContext(agentType) {
    if (AGENT_CONTEXT[agentType]) {
      const ctx = AGENT_CONTEXT[agentType];

      if (ctx.mcpPreference) {
        this.routing.mcp = ctx.mcpPreference;
      }

      this.routing.skills = [...new Set([...this.routing.skills, ...ctx.skills])];
      this.routing.instructions = [...this.routing.instructions, ...ctx.instructions];

      if (ctx.outputFormats.length > 0 && !this.routing.outputFormat) {
        this.routing.outputFormat = ctx.outputFormats[0];
      }

      this.routing.injectedContext = ctx;
    }

    return this.routing;
  }
}

// ============================================================================
// MAIN HOOK EXECUTION
// ============================================================================

function main() {
  try {
    // Read tool call from stdin
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

    if (!input) {
      process.exit(0);
    }

    // Parse tool call
    let toolCall;
    try {
      toolCall = JSON.parse(input);
    } catch {
      console.error('[pre-tool-router] Invalid JSON input');
      process.exit(0);
    }

    // Process routing
    const router = new PreToolRouter(toolCall);
    const routing = router.process();

    // Check if this is an agent call
    if (toolCall.agent || toolCall.agentType) {
      router.injectAgentContext(toolCall.agent || toolCall.agentType);
    }

    // Generate output
    const output = [];

    if (routing.mcp) {
      output.push(`<pre-tool-mcp>`);
      output.push(`Server: ${routing.mcp}`);
      output.push(`</pre-tool-mcp>`);
    }

    if (routing.skills.length > 0) {
      output.push(`<pre-tool-skills>`);
      output.push(`Activate: ${routing.skills.join(', ')}`);
      output.push(`</pre-tool-skills>`);
    }

    if (routing.outputFormat) {
      output.push(`<pre-tool-output>`);
      output.push(`Format: ${routing.outputFormat}`);
      if (routing.availableFormats) {
        output.push(`Available: ${routing.availableFormats.join(', ')}`);
      }
      output.push(`</pre-tool-output>`);
    }

    if (routing.instructions.length > 0) {
      output.push(`<pre-tool-instructions>`);
      for (const inst of routing.instructions) {
        output.push(`- ${inst}`);
      }
      output.push(`</pre-tool-instructions>`);
    }

    if (output.length > 0) {
      console.log(output.join('\n'));
    }

    process.exit(0);

  } catch (error) {
    console.error(`[pre-tool-router] Error: ${error.message}`);
    process.exit(0);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { PreToolRouter, MCP_ROUTING, AGENT_CONTEXT, SKILL_ACTIVATION };
