#!/usr/bin/env python3
"""
10x Team Masterclass PDF Generator - Showcasing Toolkit Capabilities
Developed by 10x.in
"""

from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY


def create_styles():
    """Create simple blog-style PDF styles."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='BlogTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=20,
        alignment=TA_CENTER,
        textColor=colors.black
    ))

    styles.add(ParagraphStyle(
        name='BlogSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.gray
    ))

    styles.add(ParagraphStyle(
        name='Heading',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=25,
        spaceAfter=12,
        textColor=colors.black
    ))

    styles.add(ParagraphStyle(
        name='SubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=18,
        spaceAfter=8,
        textColor=colors.HexColor('#333333')
    ))

    styles.add(ParagraphStyle(
        name='Body',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        leading=16
    ))

    styles.add(ParagraphStyle(
        name='BulletItem',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=6,
        leading=14
    ))

    styles.add(ParagraphStyle(
        name='CodeBlock',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Courier',
        leftIndent=20,
        spaceAfter=8,
        spaceBefore=8,
        backColor=colors.HexColor('#f5f5f5'),
        leading=14
    ))

    styles.add(ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.gray
    ))

    return styles


def generate_pdf(output_path, title, subtitle, content, styles):
    """Generate a simple blog-style PDF."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    story = []

    # Title
    story.append(Paragraph(title, styles['BlogTitle']))
    story.append(Paragraph(subtitle, styles['BlogSubtitle']))
    story.append(Paragraph(f"10x Team Toolkit Guide | January 2026", styles['Footer']))
    story.append(Spacer(1, 30))

    # Content
    for section in content:
        if section['type'] == 'heading':
            story.append(Paragraph(section['text'], styles['Heading']))
        elif section['type'] == 'subheading':
            story.append(Paragraph(section['text'], styles['SubHeading']))
        elif section['type'] == 'paragraph':
            story.append(Paragraph(section['text'], styles['Body']))
        elif section['type'] == 'bullets':
            for bullet in section['items']:
                story.append(Paragraph(f"* {bullet}", styles['BulletItem']))
            story.append(Spacer(1, 8))
        elif section['type'] == 'code':
            story.append(Paragraph(section['text'], styles['CodeBlock']))

    # Footer
    story.append(Spacer(1, 40))
    story.append(Paragraph("-" * 30, styles['Footer']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Developed by 10x.in", styles['Footer']))
    story.append(Paragraph("https://10x.in", styles['Footer']))

    doc.build(story)


def main():
    output_dir = Path("C:/Downloads/MasterClass-January")
    output_dir.mkdir(parents=True, exist_ok=True)
    styles = create_styles()

    # PDF 1: High-Vibe Content with 10x Team
    generate_pdf(
        output_dir / "01-High-Vibe-Content-Creation.pdf",
        "High-Vibe Content Creation",
        "Using 10x Team to Plan and Create Content Consistently",
        [
            {'type': 'heading', 'text': 'The Challenge'},
            {'type': 'paragraph', 'text': 'Creating consistent, high-quality content is exhausting. You need ideas, frameworks, proper formatting, platform-specific variations, and a calendar to keep it all organized. Most teams struggle with either quantity or quality - rarely both.'},

            {'type': 'heading', 'text': 'How 10x Team Solves This'},
            {'type': 'paragraph', 'text': '10x Team provides specialized skills and commands that handle the heavy lifting of content creation while you maintain creative control.'},

            {'type': 'heading', 'text': 'Skills You Will Use'},

            {'type': 'subheading', 'text': 'content-marketing'},
            {'type': 'paragraph', 'text': 'Strategic content planning with editorial calendars, content pillars, and topic clustering. Automatically creates structured content plans aligned with your business goals.'},
            {'type': 'bullets', 'items': [
                'Content pillar mapping (3-5 core themes)',
                'Editorial calendar generation',
                'Content audit and gap analysis',
                'Repurposing workflows'
            ]},

            {'type': 'subheading', 'text': 'copywriting'},
            {'type': 'paragraph', 'text': 'Conversion-focused copy using proven formulas (AIDA, PAS, BAB). Includes headline templates, email patterns, and CTA optimization.'},
            {'type': 'bullets', 'items': [
                '50+ writing style templates in assets/writing-styles/',
                'Extract writing styles from any document (PDF, DOCX, video)',
                'Apply consistent voice across all content'
            ]},

            {'type': 'subheading', 'text': 'creativity'},
            {'type': 'paragraph', 'text': '55 creative style templates with copy-ready keywords, color palettes, and visual direction. From minimalist to maximalist, nostalgic to futuristic.'},

            {'type': 'heading', 'text': 'Commands to Run'},

            {'type': 'subheading', 'text': '/content:fast'},
            {'type': 'paragraph', 'text': 'Quick content generation when you need speed. Great for social posts, short-form content, and rapid ideation.'},
            {'type': 'code', 'text': '/content:fast "LinkedIn post about AI automation for marketers"'},

            {'type': 'subheading', 'text': '/content:good'},
            {'type': 'paragraph', 'text': 'Higher quality output with more research and refinement. Use for blog posts, newsletters, and long-form content.'},
            {'type': 'code', 'text': '/content:good "Blog post: 5 ways AI changes content marketing"'},

            {'type': 'subheading', 'text': '/content:enhance'},
            {'type': 'paragraph', 'text': 'Take existing copy and make it better. Fixes issues, improves flow, strengthens CTAs.'},
            {'type': 'code', 'text': '/content:enhance "Review and improve my landing page copy"'},

            {'type': 'heading', 'text': 'Workflow Example'},
            {'type': 'paragraph', 'text': 'Creating a week of LinkedIn content:'},
            {'type': 'bullets', 'items': [
                'Step 1: Activate content-marketing skill for content pillar planning',
                'Step 2: Use /content:good to create 5 pillar posts',
                'Step 3: Use /content:fast to create 10 quick engagement posts',
                'Step 4: Apply your brand voice from assets/writing-styles/',
                'Step 5: Export to your scheduling tool'
            ]},

            {'type': 'heading', 'text': 'What You Get'},
            {'type': 'bullets', 'items': [
                'Structured content calendar with themes and dates',
                'Platform-ready copy (LinkedIn, Twitter, email)',
                'Consistent brand voice across all content',
                'Headline variations for A/B testing',
                'Visual direction notes for designers'
            ]},

            {'type': 'heading', 'text': 'Try It Now'},
            {'type': 'code', 'text': '/content:good "Create a 2-week LinkedIn content calendar for a B2B SaaS company targeting startup founders"'},
        ],
        styles
    )
    print("[OK] 01-High-Vibe-Content-Creation.pdf")

    # PDF 2: Intent-Driven SEO with 10x Team
    generate_pdf(
        output_dir / "02-Intent-Driven-SEO.pdf",
        "Intent-Driven SEO",
        "Using 10x Team to Structure SEO with Intent",
        [
            {'type': 'heading', 'text': 'The Challenge'},
            {'type': 'paragraph', 'text': 'Traditional SEO tools show keywords and rankings. But they do not tell you WHY people search or whether your content matches their intent. Result: high traffic, low conversions.'},

            {'type': 'heading', 'text': 'How 10x Team Solves This'},
            {'type': 'paragraph', 'text': '10x Team connects directly to Google Search Console and keyword research APIs to analyze intent, not just keywords. It identifies mismatches and suggests fixes.'},

            {'type': 'heading', 'text': 'Skills You Will Use'},

            {'type': 'subheading', 'text': 'seo-optimization'},
            {'type': 'paragraph', 'text': 'Complete SEO toolkit with keyword research (ReviewWeb.site API), Google Search Console integration, technical SEO audits, and programmatic SEO templates.'},
            {'type': 'bullets', 'items': [
                'Keyword research with real data (volume, difficulty, CPC)',
                'Competitor domain analysis (traffic, top keywords, backlinks)',
                'Google Search Console queries, clicks, impressions, CTR, position',
                'JSON+LD schema generation',
                'Core Web Vitals measurement'
            ]},

            {'type': 'heading', 'text': 'Commands to Run'},

            {'type': 'subheading', 'text': '/seo'},
            {'type': 'paragraph', 'text': 'Main SEO command for audits, keyword research, and optimization recommendations.'},
            {'type': 'code', 'text': '/seo audit https://yoursite.com'},

            {'type': 'subheading', 'text': 'Google Search Console Scripts'},
            {'type': 'paragraph', 'text': 'Direct access to your Search Console data via command line:'},
            {'type': 'code', 'text': 'node .claude/skills/seo-optimization/scripts/gsc-query.cjs --sites'},
            {'type': 'code', 'text': 'node .claude/skills/seo-optimization/scripts/gsc-query.cjs --top-queries -s https://yoursite.com'},
            {'type': 'code', 'text': 'node .claude/skills/seo-optimization/scripts/gsc-query.cjs --low-ctr -s https://yoursite.com'},

            {'type': 'heading', 'text': 'Intent Analysis Workflow'},
            {'type': 'paragraph', 'text': 'Finding and fixing intent mismatches:'},
            {'type': 'bullets', 'items': [
                'Step 1: Pull top queries from Search Console',
                'Step 2: Claude classifies each query by intent (informational/commercial/transactional)',
                'Step 3: Compare intent to your current content type',
                'Step 4: Identify mismatches (e.g., blog ranking for transactional query)',
                'Step 5: Get specific rewrite recommendations'
            ]},

            {'type': 'heading', 'text': 'Setup (One-Time)'},
            {'type': 'paragraph', 'text': 'Connect Google Search Console:'},
            {'type': 'bullets', 'items': [
                '1. Enable Search Console API in Google Cloud Console',
                '2. Create OAuth credentials (Desktop app type)',
                '3. Save JSON to .claude/secrets/google_client_secret.json',
                '4. Run: node scripts/gsc-auth.cjs --auth',
                '5. Complete OAuth flow in browser'
            ]},

            {'type': 'heading', 'text': 'What You Get'},
            {'type': 'bullets', 'items': [
                'Intent classification for all your top keywords',
                'CTR vs position analysis (spots intent mismatch)',
                'Specific title tag and meta description rewrites',
                'Content structure recommendations by intent type',
                'Internal linking suggestions for intent flow'
            ]},

            {'type': 'heading', 'text': 'Programmatic SEO'},
            {'type': 'paragraph', 'text': 'For sites with hundreds of similar pages (product listings, locations, etc.), 10x Team generates pSEO templates that scale your SEO efforts.'},
            {'type': 'code', 'text': '/seo pseo-template "city landing pages for plumber services"'},

            {'type': 'heading', 'text': 'Try It Now'},
            {'type': 'code', 'text': '/seo "Analyze my top 20 pages and identify intent mismatches with fix recommendations"'},
        ],
        styles
    )
    print("[OK] 02-Intent-Driven-SEO.pdf")

    # PDF 3: Landing Pages with 10x Team
    generate_pdf(
        output_dir / "03-Landing-Pages-That-Convert.pdf",
        "Landing Pages That Convert",
        "Using 10x Team Multi-Agent System for Landing Pages",
        [
            {'type': 'heading', 'text': 'The Challenge'},
            {'type': 'paragraph', 'text': 'Building a high-converting landing page requires strategy, copywriting, design, development, and QA. Usually this means coordinating multiple people and days of back-and-forth.'},

            {'type': 'heading', 'text': 'How 10x Team Solves This'},
            {'type': 'paragraph', 'text': '10x Team uses a 6-agent system that works like a full agency team. Each agent specializes in one aspect, and a Project Manager agent coordinates everything.'},

            {'type': 'heading', 'text': 'The 6-Agent System'},

            {'type': 'subheading', 'text': '1. Discovery Agent'},
            {'type': 'paragraph', 'text': 'Gathers requirements through targeted questions. Understands your audience, pain points, and desired transformation.'},

            {'type': 'subheading', 'text': '2. Copywriting Agent'},
            {'type': 'paragraph', 'text': 'Creates headlines, body copy, and CTAs using conversion formulas. Generates A/B testing variations.'},

            {'type': 'subheading', 'text': '3. Design Agent'},
            {'type': 'paragraph', 'text': 'Plans visual strategy including layout, color psychology, and typography. Creates design direction document.'},

            {'type': 'subheading', 'text': '4. Build Agent'},
            {'type': 'paragraph', 'text': 'Generates production-ready HTML, CSS, and JavaScript. Mobile-responsive by default.'},

            {'type': 'subheading', 'text': '5. QA Agent'},
            {'type': 'paragraph', 'text': 'Prepares testing checklist for functionality, design, and conversion tracking.'},

            {'type': 'subheading', 'text': '6. Project Manager Agent'},
            {'type': 'paragraph', 'text': 'Coordinates all agents, reviews output against requirements, ensures quality before delivery.'},

            {'type': 'heading', 'text': 'Commands to Run'},

            {'type': 'subheading', 'text': '/landing-page or /lp'},
            {'type': 'paragraph', 'text': 'Launches the full 6-agent landing page creation process.'},
            {'type': 'code', 'text': '/landing-page'},
            {'type': 'paragraph', 'text': 'Or with a brief:'},
            {'type': 'code', 'text': '/lp "SaaS product landing page for AI writing assistant targeting content creators"'},

            {'type': 'heading', 'text': 'The Process'},
            {'type': 'bullets', 'items': [
                'Step 1: Answer discovery questions (5-10 minutes)',
                'Step 2: Agents work autonomously (you can watch or wait)',
                'Step 3: Project Manager reviews all output',
                'Step 4: You receive complete landing page package'
            ]},

            {'type': 'heading', 'text': 'What You Get'},
            {'type': 'bullets', 'items': [
                'Complete HTML/CSS/JS landing page',
                'Copy document with all text and A/B variations',
                'Design direction document',
                'Mobile-responsive implementation',
                'Conversion tracking setup guide',
                'QA checklist for launch'
            ]},

            {'type': 'heading', 'text': 'Worksheets Integration'},
            {'type': 'paragraph', 'text': 'For complex projects, you can provide a Landing Page Worksheet document. The agents will use your detailed requirements instead of asking questions.'},
            {'type': 'code', 'text': '/lp --worksheet docs/landing-page-worksheet.md'},

            {'type': 'heading', 'text': 'Output Location'},
            {'type': 'paragraph', 'text': 'All files are saved to:'},
            {'type': 'code', 'text': 'output/landing-pages/{project-name}/'},
            {'type': 'bullets', 'items': [
                'index.html - The landing page',
                'styles.css - Styling',
                'copy.md - All copy with variations',
                'design-direction.md - Visual strategy',
                'qa-checklist.md - Testing guide'
            ]},

            {'type': 'heading', 'text': 'Try It Now'},
            {'type': 'code', 'text': '/lp "Create a landing page for an email marketing course targeting small business owners who struggle with low open rates"'},
        ],
        styles
    )
    print("[OK] 03-Landing-Pages-That-Convert.pdf")

    # PDF 4: End-to-End Campaigns with 10x Team
    generate_pdf(
        output_dir / "04-End-to-End-Campaigns.pdf",
        "End-to-End Campaigns",
        "Using 10x Team Workflow Engine for Campaign Automation",
        [
            {'type': 'heading', 'text': 'The Challenge'},
            {'type': 'paragraph', 'text': 'Campaigns involve multiple assets: landing pages, emails, ads, social posts. Coordinating creation across these is where bottlenecks happen. Waiting on copy, chasing approvals, fixing handoffs.'},

            {'type': 'heading', 'text': 'How 10x Team Solves This'},
            {'type': 'paragraph', 'text': 'The Workflow Engine chains multiple skills together and executes them autonomously. You define the campaign, approve the plan, then let it run without interruption.'},

            {'type': 'heading', 'text': 'Skills You Will Use'},

            {'type': 'subheading', 'text': 'workflow-engine'},
            {'type': 'paragraph', 'text': 'The execution backbone that chains skills, manages data passing between steps, and generates outputs in multiple formats (PDF, PPT, JSON).'},

            {'type': 'subheading', 'text': 'campaign-management'},
            {'type': 'paragraph', 'text': 'Campaign planning frameworks including briefs, timelines, budgets, and optimization workflows.'},

            {'type': 'subheading', 'text': 'email-marketing'},
            {'type': 'paragraph', 'text': 'Email sequence templates, subject line generation, drip campaign architecture, and A/B test design.'},

            {'type': 'subheading', 'text': 'ads-management'},
            {'type': 'paragraph', 'text': 'Ad copywriting for Google, Meta, LinkedIn, TikTok. Audience targeting suggestions and budget optimization.'},

            {'type': 'heading', 'text': 'Commands to Run'},

            {'type': 'subheading', 'text': '/workflow create'},
            {'type': 'paragraph', 'text': 'Creates a workflow from your description and visualizes it in TLDraw canvas.'},
            {'type': 'code', 'text': '/workflow create "product launch campaign with landing page, 5-email sequence, and social content"'},

            {'type': 'subheading', 'text': '/workflow execute'},
            {'type': 'paragraph', 'text': 'Runs an approved workflow autonomously.'},
            {'type': 'code', 'text': '/workflow execute workflow-abc123'},

            {'type': 'subheading', 'text': '/campaign'},
            {'type': 'paragraph', 'text': 'Quick campaign brief and asset generation.'},
            {'type': 'code', 'text': '/campaign "Black Friday sale for SaaS product"'},

            {'type': 'heading', 'text': 'The Workflow Lifecycle'},
            {'type': 'bullets', 'items': [
                '1. ANALYZE - Parse your request, identify required skills',
                '2. PLAN - Create workflow template (JSON)',
                '3. CLARIFY - Ask ALL questions upfront (not during execution)',
                '4. VISUALIZE - Show in TLDraw canvas (port 3001)',
                '5. APPROVE - You confirm the workflow',
                '6. EXECUTE - Runs autonomously (no interruptions)',
                '7. OUTPUT - Generate PDF, PPT, JSON, MD files'
            ]},

            {'type': 'heading', 'text': 'Visual Workflow Canvas'},
            {'type': 'paragraph', 'text': 'Start the canvas to see your workflows visually:'},
            {'type': 'code', 'text': 'npm run canvas'},
            {'type': 'paragraph', 'text': 'Opens TLDraw at http://localhost:3001 showing workflow nodes and connections.'},

            {'type': 'heading', 'text': 'What You Get'},
            {'type': 'bullets', 'items': [
                'Campaign brief document',
                'Landing page (via landing-page skill)',
                '5-7 email sequence with subject line variations',
                '10+ social posts formatted per platform',
                'Ad copy variations for each platform',
                'Timeline and launch checklist',
                'PDF report with all assets'
            ]},

            {'type': 'heading', 'text': 'Output Location'},
            {'type': 'code', 'text': 'output/workflows/{workflow-id}/'},

            {'type': 'heading', 'text': 'Start All Services'},
            {'type': 'code', 'text': 'npm run start:all'},
            {'type': 'paragraph', 'text': 'Starts Dashboard (3000), Canvas (3001), and WebSocket (3002).'},

            {'type': 'heading', 'text': 'Try It Now'},
            {'type': 'code', 'text': '/workflow create "Q1 product launch for new AI feature - need landing page, email nurture sequence, LinkedIn content, and Google Ads copy"'},
        ],
        styles
    )
    print("[OK] 04-End-to-End-Campaigns.pdf")

    # PDF 5: Adaptive Messaging with 10x Team
    generate_pdf(
        output_dir / "05-Adaptive-Messaging.pdf",
        "Adaptive Messaging",
        "Using 10x Team Analytics to Respond to Audience Signals",
        [
            {'type': 'heading', 'text': 'The Challenge'},
            {'type': 'paragraph', 'text': 'Marketing data is everywhere - email opens, ad clicks, page views, conversions. But turning that data into message improvements requires analysis, hypothesis generation, and testing. Most teams look at dashboards but do not adapt.'},

            {'type': 'heading', 'text': 'How 10x Team Solves This'},
            {'type': 'paragraph', 'text': '10x Team connects to your analytics sources, interprets signals, and suggests specific message pivots based on what the data shows.'},

            {'type': 'heading', 'text': 'Skills You Will Use'},

            {'type': 'subheading', 'text': 'analytics'},
            {'type': 'paragraph', 'text': 'Marketing analytics with KPI tracking, attribution modeling, funnel analysis, and report generation.'},
            {'type': 'bullets', 'items': [
                'Campaign performance analysis',
                'ROI and ROAS calculation',
                'A/B test result interpretation',
                'Funnel drop-off identification'
            ]},

            {'type': 'subheading', 'text': 'social-media'},
            {'type': 'paragraph', 'text': 'Social media analytics, engagement tracking, and content performance analysis.'},

            {'type': 'subheading', 'text': 'Browser Extension'},
            {'type': 'paragraph', 'text': 'The 10x.in Browser Extension fetches authenticated data from Google Ads, Google Analytics, and LinkedIn that APIs cannot access.'},

            {'type': 'heading', 'text': 'Commands to Run'},

            {'type': 'subheading', 'text': '/analyze'},
            {'type': 'paragraph', 'text': 'Analyze campaign or content performance and get recommendations.'},
            {'type': 'code', 'text': '/analyze "Why did our email open rates drop 30% last month?"'},

            {'type': 'subheading', 'text': '/social'},
            {'type': 'paragraph', 'text': 'Social media content and analytics.'},
            {'type': 'code', 'text': '/social "Analyze our LinkedIn engagement and suggest content pivots"'},

            {'type': 'subheading', 'text': 'Marketing Dashboard'},
            {'type': 'code', 'text': 'npm run dashboard'},
            {'type': 'paragraph', 'text': 'Opens Vue 3 dashboard at http://localhost:3000 for visual campaign management.'},

            {'type': 'heading', 'text': 'Browser Extension for Authenticated Data'},
            {'type': 'paragraph', 'text': 'Some data requires login access. The Browser Extension handles:'},
            {'type': 'bullets', 'items': [
                'Google Ads - Campaign performance, cost data',
                'Google Analytics - GA4 dashboard data',
                'LinkedIn - Profile analytics, post performance',
                'Any authenticated web scraping'
            ]},
            {'type': 'code', 'text': '/browser fetch-google-ads'},
            {'type': 'code', 'text': '/browser fetch-linkedin-analytics'},

            {'type': 'heading', 'text': 'Signal Interpretation Workflow'},
            {'type': 'bullets', 'items': [
                'Step 1: Connect data sources (GSC, GA4, email platform)',
                'Step 2: Ask Claude to analyze performance trends',
                'Step 3: Get specific diagnosis (not just "CTR is down")',
                'Step 4: Receive message pivot recommendations',
                'Step 5: Generate A/B test variations based on analysis'
            ]},

            {'type': 'heading', 'text': 'What You Get'},
            {'type': 'bullets', 'items': [
                'Trend analysis with root cause identification',
                'Segment breakdown (which audiences changed)',
                'Specific message pivot recommendations',
                'New headline/subject line formulas based on winners',
                'A/B test plan with success metrics'
            ]},

            {'type': 'heading', 'text': 'MCP Server Integration'},
            {'type': 'paragraph', 'text': '10x Team supports Model Context Protocol servers for extended data access:'},
            {'type': 'bullets', 'items': [
                'Exa MCP - Quick web searches, company lookups',
                'Websets MCP - Deep prospect research, lead lists',
                'Custom MCPs - Connect any data source'
            ]},
            {'type': 'code', 'text': '/use-mcp "Search for recent news about our competitors"'},

            {'type': 'heading', 'text': 'Try It Now'},
            {'type': 'code', 'text': '/analyze "Our landing page conversion dropped from 5% to 2% this month. Analyze possible causes and suggest message changes."'},
        ],
        styles
    )
    print("[OK] 05-Adaptive-Messaging.pdf")

    print("-" * 50)
    print(f"Done! 5 PDFs created in {output_dir}")
    print("Developed by 10x.in")


if __name__ == "__main__":
    main()
