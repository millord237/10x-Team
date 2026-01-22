#!/usr/bin/env node
/**
 * Tool Display Hook - Provides user-friendly names for tool calls
 * Developed by Team 10x.in
 *
 * This hook transforms generic tool names into meaningful descriptions
 * for better UX when Claude shows "Using <tool>..." messages.
 *
 * Instead of: "Using WebFetch..."
 * Shows: "Using Exa MCP for prospect search..."
 *
 * Hook Type: PreToolCall / PostToolCall
 */

const fs = require('fs');
const path = require('path');

// ============================================================================
// TOOL DISPLAY MAPPINGS
// ============================================================================

const TOOL_DISPLAY_NAMES = {
  // MCP Tools
  'WebFetch': {
    default: 'Web Content Fetcher',
    contexts: {
      'exa': 'Exa AI Search',
      'websets': 'Websets Deep Research',
      'linkedin': 'LinkedIn Data Fetcher',
      'google': 'Google Search'
    }
  },

  'WebSearch': {
    default: 'Web Search',
    contexts: {
      'exa': 'Exa AI Quick Search',
      'websets': 'Websets Comprehensive Search',
      'prospects': 'Prospect Discovery',
      'research': 'Research Search'
    }
  },

  // Browser Extension Actions
  'browser_navigate': {
    default: 'Browser Navigation',
    icon: '🌐'
  },
  'browser_click': {
    default: 'Browser Click Action',
    icon: '👆'
  },
  'browser_type': {
    default: 'Browser Text Input',
    icon: '⌨️'
  },
  'browser_scrape': {
    default: 'Web Page Scraper',
    icon: '📄'
  },
  'browser_screenshot': {
    default: 'Screenshot Capture',
    icon: '📸'
  },

  // Platform-Specific
  'linkedin_search': {
    default: 'LinkedIn Profile Search',
    skill: 'outreach',
    icon: '💼'
  },
  'linkedin_action': {
    default: 'LinkedIn Automation',
    skill: 'outreach',
    icon: '💼'
  },
  'twitter_action': {
    default: 'Twitter/X Automation',
    skill: 'outreach',
    icon: '🐦'
  },
  'instagram_action': {
    default: 'Instagram Automation',
    skill: 'outreach',
    icon: '📷'
  },
  'google_ads_fetch': {
    default: 'Google Ads Data Fetch',
    skill: 'analytics',
    icon: '📊'
  },
  'google_analytics_fetch': {
    default: 'Google Analytics Data Fetch',
    skill: 'analytics',
    icon: '📈'
  },

  // Workflow Tools
  'workflow_execute': {
    default: 'Workflow Execution',
    skill: 'workflow-engine',
    icon: '⚙️'
  },
  'workflow_create': {
    default: 'Workflow Creation',
    skill: 'workflow-engine',
    icon: '📝'
  },

  // Content Tools
  'generate_pdf': {
    default: 'PDF Report Generator',
    skill: 'workflow-engine',
    icon: '📄'
  },
  'generate_image': {
    default: 'Image Generator',
    skill: 'ai-multimodal',
    icon: '🖼️'
  },

  // Analysis Tools
  'seo_audit': {
    default: 'SEO Audit',
    skill: 'seo-optimization',
    icon: '🔍'
  },
  'analytics_report': {
    default: 'Analytics Report',
    skill: 'analytics',
    icon: '📊'
  }
};

// ============================================================================
// SKILL TO DISPLAY NAME MAPPINGS
// ============================================================================

const SKILL_DISPLAY_NAMES = {
  'outreach': 'Outreach & Discovery',
  'outreach/discovery-engine': 'Prospect Discovery Engine',
  'outreach/linkedin-adapter': 'LinkedIn Automation',
  'outreach/twitter-adapter': 'Twitter/X Automation',
  'outreach/instagram-adapter': 'Instagram Automation',
  'landing-page': 'Landing Page Builder',
  'content-marketing': 'Content Marketing',
  'copywriting': 'Conversion Copywriting',
  'email-marketing': 'Email Marketing',
  'seo-optimization': 'SEO Optimization',
  'campaign-management': 'Campaign Management',
  'analytics': 'Marketing Analytics',
  'ads-management': 'Ads Management',
  'workflow-engine': 'Workflow Engine',
  'ai-multimodal': 'AI Multimodal (Gemini)',
  'design': 'Design System',
  'frontend-design': 'Frontend Design'
};

// ============================================================================
// MCP TO DISPLAY NAME MAPPINGS
// ============================================================================

const MCP_DISPLAY_NAMES = {
  'exa': {
    name: 'Exa AI',
    description: 'Quick web search & LinkedIn lookups',
    icon: '🔍'
  },
  'websets': {
    name: 'Websets',
    description: 'Deep research & prospect lists',
    icon: '📋'
  },
  'context7': {
    name: 'Context7',
    description: 'Documentation search',
    icon: '📚'
  },
  'memory': {
    name: 'Memory',
    description: 'Knowledge graph storage',
    icon: '🧠'
  },
  'fetch': {
    name: 'Fetch',
    description: 'Web page content',
    icon: '🌐'
  },
  'sequential-thinking': {
    name: 'Sequential Thinking',
    description: 'Complex reasoning',
    icon: '🤔'
  },
  'browser-extension': {
    name: '10x Browser Extension',
    description: 'Browser automation & data fetching',
    icon: '🔌'
  }
};

// ============================================================================
// TOOL DISPLAY FORMATTER
// ============================================================================

class ToolDisplayFormatter {
  constructor(toolCall) {
    this.toolName = toolCall.name || toolCall.tool || '';
    this.toolParams = toolCall.params || toolCall.parameters || {};
    this.context = toolCall.context || {};
  }

  /**
   * Get user-friendly display name for the tool
   */
  getDisplayName() {
    const mapping = TOOL_DISPLAY_NAMES[this.toolName];

    if (!mapping) {
      // Return formatted version of tool name
      return this.formatToolName(this.toolName);
    }

    // Check for context-specific name
    if (mapping.contexts) {
      for (const [context, name] of Object.entries(mapping.contexts)) {
        if (this.matchesContext(context)) {
          return name;
        }
      }
    }

    return mapping.default;
  }

  /**
   * Get icon for the tool
   */
  getIcon() {
    const mapping = TOOL_DISPLAY_NAMES[this.toolName];
    return mapping?.icon || '🔧';
  }

  /**
   * Get associated skill name
   */
  getSkillName() {
    const mapping = TOOL_DISPLAY_NAMES[this.toolName];
    if (mapping?.skill) {
      return SKILL_DISPLAY_NAMES[mapping.skill] || mapping.skill;
    }
    return null;
  }

  /**
   * Get MCP display info
   */
  getMcpDisplayInfo(mcpName) {
    return MCP_DISPLAY_NAMES[mcpName] || {
      name: mcpName,
      description: 'MCP Server',
      icon: '🔌'
    };
  }

  /**
   * Check if tool matches a context
   */
  matchesContext(context) {
    const query = this.toolParams.query || this.toolParams.url || '';
    const queryLower = query.toLowerCase();

    switch (context) {
      case 'exa':
        return queryLower.includes('exa') || this.context.mcp === 'exa';
      case 'websets':
        return queryLower.includes('websets') || this.context.mcp === 'websets';
      case 'linkedin':
        return queryLower.includes('linkedin');
      case 'google':
        return queryLower.includes('google');
      case 'prospects':
        return queryLower.includes('prospect') || queryLower.includes('lead');
      case 'research':
        return queryLower.includes('research');
      default:
        return false;
    }
  }

  /**
   * Format tool name for display
   */
  formatToolName(name) {
    // Convert camelCase or snake_case to Title Case
    return name
      .replace(/([A-Z])/g, ' $1')
      .replace(/_/g, ' ')
      .replace(/^\s/, '')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ');
  }

  /**
   * Generate full display string
   */
  getFullDisplayString() {
    const icon = this.getIcon();
    const name = this.getDisplayName();
    const skill = this.getSkillName();

    let display = `${icon} ${name}`;

    if (skill) {
      display += ` (${skill})`;
    }

    return display;
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
      process.exit(0);
    }

    // Format display
    const formatter = new ToolDisplayFormatter(toolCall);

    const output = {
      displayName: formatter.getDisplayName(),
      fullDisplay: formatter.getFullDisplayString(),
      icon: formatter.getIcon(),
      skill: formatter.getSkillName()
    };

    // If MCP is specified, add MCP info
    if (toolCall.mcp) {
      output.mcp = formatter.getMcpDisplayInfo(toolCall.mcp);
    }

    console.log(JSON.stringify(output));
    process.exit(0);

  } catch (error) {
    console.error(`[tool-display] Error: ${error.message}`);
    process.exit(0);
  }
}

// Export for testing
module.exports = {
  ToolDisplayFormatter,
  TOOL_DISPLAY_NAMES,
  SKILL_DISPLAY_NAMES,
  MCP_DISPLAY_NAMES
};

// Run if called directly
if (require.main === module) {
  main();
}
