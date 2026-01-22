#!/usr/bin/env python3
"""
Prospect Discovery Engine - Find prospects using Exa AI and generate branded reports
Developed by Team 10x.in

This script:
1. Uses Exa MCP for intelligent prospect discovery
2. Enriches profiles via browser extension (optional)
3. Generates branded PDF reports with 10x.in branding
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

# Try to import optional dependencies
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = ROOT_DIR / "output" / "discovery"
REPORTS_DIR = ROOT_DIR / "output" / "reports"


class ProspectDiscovery:
    """Prospect discovery using Exa AI with branded report generation."""

    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.reports_dir = REPORTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.prospects_file = self.output_dir / "prospects.json"
        self.sessions_file = self.output_dir / "sessions.json"

        # Load existing data
        self.prospects = self._load_json(self.prospects_file, [])
        self.sessions = self._load_json(self.sessions_file, [])

    def _load_json(self, path: Path, default: Any) -> Any:
        """Load JSON file or return default."""
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default

    def _save_json(self, path: Path, data: Any):
        """Save data to JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def create_session(self, query: str, source: str = "exa_search") -> Dict:
        """Create a new discovery session."""
        session = {
            "session_id": f"session_{uuid.uuid4().hex[:8]}",
            "query": query,
            "source": source,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "prospect_count": 0,
            "prospects": []
        }

        self.sessions.append(session)
        self._save_json(self.sessions_file, self.sessions)

        print(f"Created session: {session['session_id']}")
        return session

    def add_prospects_from_exa(self, session_id: str, exa_results: List[Dict]) -> List[Dict]:
        """
        Process Exa AI search results and add prospects.

        Expected exa_results format:
        [
            {
                "title": "John Smith - AI Founder | LinkedIn",
                "url": "https://linkedin.com/in/johnsmith",
                "snippet": "Founder at TechStartup. Previously at Google...",
                "author": "John Smith",
                "published_date": "2024-01-15"
            },
            ...
        ]
        """
        session = next((s for s in self.sessions if s["session_id"] == session_id), None)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        added_prospects = []

        for result in exa_results:
            # Parse LinkedIn URL to extract profile info
            url = result.get("url", "")
            title = result.get("title", "")
            snippet = result.get("snippet", "")

            # Extract name from title (usually "Name - Title | LinkedIn")
            name = title.split(" - ")[0].strip() if " - " in title else title.split(" | ")[0].strip()

            # Extract headline/title
            headline = ""
            if " - " in title:
                parts = title.split(" - ")
                if len(parts) > 1:
                    headline = parts[1].split(" | ")[0].strip()

            prospect = {
                "prospect_id": f"prospect_{uuid.uuid4().hex[:8]}",
                "name": name,
                "headline": headline,
                "linkedin_url": url if "linkedin.com" in url else None,
                "twitter_url": None,
                "email": None,
                "company": self._extract_company(headline, snippet),
                "location": self._extract_location(snippet),
                "snippet": snippet[:500] if snippet else None,
                "source": "exa_search",
                "session_id": session_id,
                "discovered_at": datetime.now().isoformat(),
                "status": "discovered",
                "tags": [],
                "notes": ""
            }

            # Deduplicate by LinkedIn URL
            if prospect["linkedin_url"]:
                existing = next((p for p in self.prospects if p.get("linkedin_url") == prospect["linkedin_url"]), None)
                if existing:
                    continue

            self.prospects.append(prospect)
            added_prospects.append(prospect)
            session["prospects"].append(prospect["prospect_id"])

        session["prospect_count"] = len(session["prospects"])

        self._save_json(self.prospects_file, self.prospects)
        self._save_json(self.sessions_file, self.sessions)

        print(f"Added {len(added_prospects)} prospects to session {session_id}")
        return added_prospects

    def _extract_company(self, headline: str, snippet: str) -> Optional[str]:
        """Extract company name from headline or snippet."""
        # Common patterns: "Title at Company", "Title @ Company"
        for text in [headline, snippet]:
            if not text:
                continue
            if " at " in text.lower():
                parts = text.lower().split(" at ")
                if len(parts) > 1:
                    return parts[1].split(".")[0].split(",")[0].strip().title()
            if " @ " in text:
                parts = text.split(" @ ")
                if len(parts) > 1:
                    return parts[1].split(".")[0].split(",")[0].strip()
        return None

    def _extract_location(self, snippet: str) -> Optional[str]:
        """Extract location from snippet."""
        if not snippet:
            return None
        # Look for common location patterns
        location_keywords = ["based in", "located in", "from", "area"]
        snippet_lower = snippet.lower()
        for keyword in location_keywords:
            if keyword in snippet_lower:
                idx = snippet_lower.find(keyword)
                location_part = snippet[idx + len(keyword):idx + len(keyword) + 50]
                # Extract until punctuation
                location = location_part.split(".")[0].split(",")[0].strip()
                if location:
                    return location.title()
        return None

    def get_prospects(self, session_id: str = None, status: str = None,
                      has_linkedin: bool = None, limit: int = None) -> List[Dict]:
        """Get prospects with optional filters."""
        results = self.prospects

        if session_id:
            results = [p for p in results if p.get("session_id") == session_id]
        if status:
            results = [p for p in results if p.get("status") == status]
        if has_linkedin:
            results = [p for p in results if p.get("linkedin_url")]
        if limit:
            results = results[:limit]

        return results

    def update_prospect_status(self, prospect_id: str, status: str, notes: str = None):
        """Update prospect status."""
        prospect = next((p for p in self.prospects if p["prospect_id"] == prospect_id), None)
        if prospect:
            prospect["status"] = status
            if notes:
                prospect["notes"] = notes
            prospect["updated_at"] = datetime.now().isoformat()
            self._save_json(self.prospects_file, self.prospects)

    def generate_branded_report(self, prospects: List[Dict], title: str = "Prospect Discovery Report") -> str:
        """Generate branded PDF report with 10x.in branding."""
        if not HAS_REPORTLAB:
            print("reportlab not installed. Generating Markdown report instead.")
            return self.generate_markdown_report(prospects, title)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.reports_dir / f"prospect_report_{timestamp}.pdf"

        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        styles = getSampleStyleSheet()

        # Custom branded styles
        title_style = ParagraphStyle(
            'BrandTitle',
            parent=styles['Heading1'],
            fontSize=28,
            spaceAfter=20,
            textColor=colors.HexColor('#1a1a2e'),
            alignment=TA_CENTER
        )

        brand_style = ParagraphStyle(
            'Brand',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#6366F1'),
            alignment=TA_CENTER,
            spaceAfter=30
        )

        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#16213e')
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            textColor=colors.HexColor('#333333'),
            leading=14
        )

        prospect_name_style = ParagraphStyle(
            'ProspectName',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=4,
            textColor=colors.HexColor('#1a1a2e'),
            fontName='Helvetica-Bold'
        )

        # Build PDF content
        story = []

        # Header with branding
        story.append(Paragraph("10x.in", brand_style))
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", body_style))
        story.append(Spacer(1, 20))

        # Summary stats
        story.append(Paragraph("Executive Summary", heading_style))

        stats_data = [
            ["Total Prospects", str(len(prospects))],
            ["With LinkedIn", str(sum(1 for p in prospects if p.get("linkedin_url")))],
            ["With Company", str(sum(1 for p in prospects if p.get("company")))],
            ["Discovery Date", datetime.now().strftime("%Y-%m-%d")]
        ]

        stats_table = Table(stats_data, colWidths=[200, 200])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0'))
        ]))

        story.append(stats_table)
        story.append(Spacer(1, 30))

        # Prospects list
        story.append(Paragraph("Discovered Prospects", heading_style))
        story.append(Spacer(1, 10))

        for i, prospect in enumerate(prospects, 1):
            # Prospect card
            story.append(Paragraph(f"{i}. {prospect.get('name', 'Unknown')}", prospect_name_style))

            if prospect.get('headline'):
                story.append(Paragraph(f"<b>Title:</b> {prospect['headline']}", body_style))

            if prospect.get('company'):
                story.append(Paragraph(f"<b>Company:</b> {prospect['company']}", body_style))

            if prospect.get('location'):
                story.append(Paragraph(f"<b>Location:</b> {prospect['location']}", body_style))

            if prospect.get('linkedin_url'):
                # Truncate long URLs
                url = prospect['linkedin_url']
                display_url = url if len(url) < 60 else url[:57] + "..."
                story.append(Paragraph(f"<b>LinkedIn:</b> {display_url}", body_style))

            if prospect.get('snippet'):
                snippet = prospect['snippet'][:200] + "..." if len(prospect['snippet']) > 200 else prospect['snippet']
                story.append(Paragraph(f"<b>About:</b> {snippet}", body_style))

            story.append(Spacer(1, 15))

            # Page break every 5 prospects
            if i % 5 == 0 and i < len(prospects):
                story.append(PageBreak())

        # Footer
        story.append(Spacer(1, 40))
        story.append(Paragraph("─" * 70, body_style))
        story.append(Spacer(1, 10))

        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )

        story.append(Paragraph("This report was generated by 10x Team - Marketing Automation Toolkit", footer_style))
        story.append(Paragraph("Developed by Team 10x.in | https://10x.in", footer_style))

        # Build PDF
        doc.build(story)
        print(f"Branded PDF report generated: {output_file}")
        return str(output_file)

    def generate_markdown_report(self, prospects: List[Dict], title: str = "Prospect Discovery Report") -> str:
        """Generate branded Markdown report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.reports_dir / f"prospect_report_{timestamp}.md"

        content = f"""# {title}

**Generated by 10x.in** | {datetime.now().strftime("%B %d, %Y at %H:%M")}

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Total Prospects | {len(prospects)} |
| With LinkedIn | {sum(1 for p in prospects if p.get("linkedin_url"))} |
| With Company | {sum(1 for p in prospects if p.get("company"))} |
| Discovery Date | {datetime.now().strftime("%Y-%m-%d")} |

---

## Discovered Prospects

"""

        for i, prospect in enumerate(prospects, 1):
            content += f"""### {i}. {prospect.get('name', 'Unknown')}

"""
            if prospect.get('headline'):
                content += f"**Title:** {prospect['headline']}\n"
            if prospect.get('company'):
                content += f"**Company:** {prospect['company']}\n"
            if prospect.get('location'):
                content += f"**Location:** {prospect['location']}\n"
            if prospect.get('linkedin_url'):
                content += f"**LinkedIn:** [{prospect['linkedin_url']}]({prospect['linkedin_url']})\n"
            if prospect.get('snippet'):
                snippet = prospect['snippet'][:200] + "..." if len(prospect['snippet']) > 200 else prospect['snippet']
                content += f"**About:** {snippet}\n"

            content += "\n---\n\n"

        content += """
---

*This report was generated by 10x Team - Marketing Automation Toolkit*

*Developed by Team 10x.in | https://10x.in*
"""

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Markdown report generated: {output_file}")
        return str(output_file)

    def export_prospects(self, prospects: List[Dict], format: str = "json") -> str:
        """Export prospects to JSON or CSV."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "csv":
            output_file = self.output_dir / f"prospects_export_{timestamp}.csv"
            import csv

            fieldnames = ["name", "headline", "company", "location", "linkedin_url", "twitter_url", "email", "status"]

            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(prospects)
        else:
            output_file = self.output_dir / f"prospects_export_{timestamp}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(prospects, f, indent=2, default=str)

        print(f"Exported to: {output_file}")
        return str(output_file)


def main():
    """CLI interface for prospect discovery."""
    if len(sys.argv) < 2:
        print("""
Prospect Discovery Engine - 10x.in
==================================

Usage: python prospect_discovery.py <command> [options]

Commands:
  session <query>           Create a new discovery session
  add <session_id> <json>   Add Exa results to session (JSON file path)
  list [--session <id>]     List prospects
  report [--session <id>]   Generate branded PDF report
  export [--format csv|json] Export prospects

Examples:
  python prospect_discovery.py session "LinkedIn marketers San Francisco"
  python prospect_discovery.py add session_abc123 exa_results.json
  python prospect_discovery.py report --session session_abc123
  python prospect_discovery.py export --format csv
        """)
        sys.exit(1)

    command = sys.argv[1]
    discovery = ProspectDiscovery()

    if command == "session":
        if len(sys.argv) < 3:
            print("Usage: prospect_discovery.py session <query>")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        session = discovery.create_session(query)
        print(json.dumps(session, indent=2))

    elif command == "add":
        if len(sys.argv) < 4:
            print("Usage: prospect_discovery.py add <session_id> <json_file>")
            sys.exit(1)
        session_id = sys.argv[2]
        json_file = sys.argv[3]

        with open(json_file, "r") as f:
            exa_results = json.load(f)

        prospects = discovery.add_prospects_from_exa(session_id, exa_results)
        print(f"Added {len(prospects)} prospects")

    elif command == "list":
        session_id = None
        if "--session" in sys.argv:
            idx = sys.argv.index("--session")
            session_id = sys.argv[idx + 1]

        prospects = discovery.get_prospects(session_id=session_id)
        print(f"Found {len(prospects)} prospects:")
        for p in prospects[:20]:  # Show first 20
            print(f"  - {p['name']} | {p.get('company', 'N/A')} | {p.get('linkedin_url', 'No LinkedIn')}")

    elif command == "report":
        session_id = None
        if "--session" in sys.argv:
            idx = sys.argv.index("--session")
            session_id = sys.argv[idx + 1]

        prospects = discovery.get_prospects(session_id=session_id)
        if not prospects:
            print("No prospects found")
            sys.exit(1)

        report_path = discovery.generate_branded_report(prospects)
        print(f"Report generated: {report_path}")

    elif command == "export":
        format = "json"
        if "--format" in sys.argv:
            idx = sys.argv.index("--format")
            format = sys.argv[idx + 1]

        prospects = discovery.get_prospects()
        export_path = discovery.export_prospects(prospects, format)
        print(f"Exported to: {export_path}")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
