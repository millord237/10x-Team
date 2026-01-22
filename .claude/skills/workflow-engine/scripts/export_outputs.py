#!/usr/bin/env python3
"""
Output Exporter - Generates PDF, PPT, and other output formats
Developed by Team 10x.in
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Try to import optional dependencies
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RgbColor
    HAS_PPTX = True
except ImportError:
    HAS_PPTX = False

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent


class OutputExporter:
    """Exports workflow results to various formats."""

    def __init__(self, workflow_path: str):
        self.workflow_path = Path(workflow_path)
        self.workflow_dir = self.workflow_path.parent
        self.workflow = None

    def load_workflow(self):
        """Load workflow from file."""
        with open(self.workflow_path, "r") as f:
            self.workflow = json.load(f)
        return self.workflow

    def export_json(self) -> str:
        """Export workflow as JSON."""
        output_file = self.workflow_dir / "final_output.json"

        # Compile all step outputs
        compiled = {
            "workflow_id": self.workflow["workflow_id"],
            "name": self.workflow["name"],
            "description": self.workflow["description"],
            "executed_at": self.workflow["execution"].get("completed_at"),
            "status": self.workflow["status"],
            "user_inputs": self.workflow["user_inputs"].get("answers", {}),
            "steps": [],
            "developed_by": "Team 10x.in"
        }

        for step in self.workflow["steps"]:
            step_data = {
                "step_id": step["step_id"],
                "name": step["name"],
                "skill": step["skill"],
                "status": step.get("status", "unknown"),
                "outputs": step.get("outputs", {})
            }
            compiled["steps"].append(step_data)

        with open(output_file, "w") as f:
            json.dump(compiled, f, indent=2)

        print(f"JSON exported: {output_file}")
        return str(output_file)

    def export_pdf(self) -> str:
        """Export workflow as PDF."""
        if not HAS_REPORTLAB:
            print("reportlab not installed. Install with: pip install reportlab")
            return None

        output_file = self.workflow_dir / "final_output.pdf"

        doc = SimpleDocTemplate(
            str(output_file),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#1a1a2e')
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor('#16213e')
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.HexColor('#333333')
        )

        # Build PDF content
        story = []

        # Title
        story.append(Paragraph(self.workflow["name"], title_style))
        story.append(Spacer(1, 12))

        # Metadata
        story.append(Paragraph("Workflow Details", heading_style))
        story.append(Paragraph(f"<b>Workflow ID:</b> {self.workflow['workflow_id']}", body_style))
        story.append(Paragraph(f"<b>Status:</b> {self.workflow['status']}", body_style))
        story.append(Paragraph(f"<b>Created:</b> {self.workflow['created_at']}", body_style))

        if self.workflow["execution"].get("completed_at"):
            story.append(Paragraph(f"<b>Completed:</b> {self.workflow['execution']['completed_at']}", body_style))

        story.append(Spacer(1, 20))

        # Description
        story.append(Paragraph("Description", heading_style))
        story.append(Paragraph(self.workflow["description"], body_style))
        story.append(Spacer(1, 20))

        # User Inputs
        if self.workflow["user_inputs"].get("answers"):
            story.append(Paragraph("User Inputs", heading_style))
            for key, value in self.workflow["user_inputs"]["answers"].items():
                story.append(Paragraph(f"<b>{key}:</b> {value}", body_style))
            story.append(Spacer(1, 20))

        # Steps
        story.append(Paragraph("Workflow Steps", heading_style))

        for step in self.workflow["steps"]:
            story.append(Paragraph(
                f"<b>Step {step['step_id']}:</b> {step['name']}",
                body_style
            ))
            story.append(Paragraph(f"Skill: {step['skill']}", body_style))
            story.append(Paragraph(f"Status: {step.get('status', 'pending')}", body_style))

            if step.get("outputs"):
                story.append(Paragraph(f"Output: {json.dumps(step['outputs'], indent=2)[:500]}...", body_style))

            story.append(Spacer(1, 12))

        story.append(Spacer(1, 30))

        # Footer
        story.append(Paragraph("─" * 50, body_style))
        story.append(Paragraph("Developed by Team 10x.in | https://10x.in", body_style))

        # Build PDF
        doc.build(story)
        print(f"PDF exported: {output_file}")
        return str(output_file)

    def export_ppt(self) -> str:
        """Export workflow as PowerPoint presentation."""
        if not HAS_PPTX:
            print("python-pptx not installed. Install with: pip install python-pptx")
            return None

        output_file = self.workflow_dir / "final_output.pptx"

        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        # Title slide
        title_slide_layout = prs.slide_layouts[6]  # Blank
        slide = prs.slides.add_slide(title_slide_layout)

        # Add title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(2.5), Inches(12), Inches(1.5))
        title_frame = title_box.text_frame
        title_para = title_frame.paragraphs[0]
        title_para.text = self.workflow["name"]
        title_para.font.size = Pt(44)
        title_para.font.bold = True

        # Add subtitle
        subtitle_box = slide.shapes.add_textbox(Inches(0.5), Inches(4), Inches(12), Inches(1))
        subtitle_frame = subtitle_box.text_frame
        subtitle_para = subtitle_frame.paragraphs[0]
        subtitle_para.text = self.workflow["description"]
        subtitle_para.font.size = Pt(24)

        # Add footer
        footer_box = slide.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(12), Inches(0.5))
        footer_frame = footer_box.text_frame
        footer_para = footer_frame.paragraphs[0]
        footer_para.text = "Developed by Team 10x.in"
        footer_para.font.size = Pt(14)

        # Steps slides
        for step in self.workflow["steps"]:
            slide = prs.slides.add_slide(title_slide_layout)

            # Step title
            title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
            title_frame = title_box.text_frame
            title_para = title_frame.paragraphs[0]
            title_para.text = f"Step {step['step_id']}: {step['name']}"
            title_para.font.size = Pt(32)
            title_para.font.bold = True

            # Step details
            content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(12), Inches(5))
            content_frame = content_box.text_frame

            # Skill
            p = content_frame.paragraphs[0]
            p.text = f"Skill: {step['skill']}"
            p.font.size = Pt(18)

            # Status
            p = content_frame.add_paragraph()
            p.text = f"Status: {step.get('status', 'pending')}"
            p.font.size = Pt(18)

            # Outputs
            if step.get("outputs"):
                p = content_frame.add_paragraph()
                p.text = ""
                p.font.size = Pt(12)

                p = content_frame.add_paragraph()
                p.text = "Outputs:"
                p.font.size = Pt(18)
                p.font.bold = True

                output_text = json.dumps(step["outputs"], indent=2)
                for line in output_text.split("\n")[:10]:  # Limit to 10 lines
                    p = content_frame.add_paragraph()
                    p.text = line
                    p.font.size = Pt(12)

        # Summary slide
        slide = prs.slides.add_slide(title_slide_layout)

        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
        title_frame = title_box.text_frame
        title_para = title_frame.paragraphs[0]
        title_para.text = "Summary"
        title_para.font.size = Pt(32)
        title_para.font.bold = True

        content_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(12), Inches(5))
        content_frame = content_box.text_frame

        p = content_frame.paragraphs[0]
        p.text = f"Workflow ID: {self.workflow['workflow_id']}"
        p.font.size = Pt(18)

        p = content_frame.add_paragraph()
        p.text = f"Total Steps: {len(self.workflow['steps'])}"
        p.font.size = Pt(18)

        p = content_frame.add_paragraph()
        p.text = f"Status: {self.workflow['status']}"
        p.font.size = Pt(18)

        if self.workflow["execution"].get("completed_at"):
            p = content_frame.add_paragraph()
            p.text = f"Completed: {self.workflow['execution']['completed_at']}"
            p.font.size = Pt(18)

        # Save
        prs.save(output_file)
        print(f"PPT exported: {output_file}")
        return str(output_file)

    def export_markdown(self) -> str:
        """Export workflow as Markdown."""
        output_file = self.workflow_dir / "final_output.md"

        content = f"""# {self.workflow['name']}

{self.workflow['description']}

---

## Workflow Details

- **Workflow ID:** {self.workflow['workflow_id']}
- **Status:** {self.workflow['status']}
- **Created:** {self.workflow['created_at']}
- **Completed:** {self.workflow['execution'].get('completed_at', 'N/A')}

---

## User Inputs

"""
        if self.workflow["user_inputs"].get("answers"):
            for key, value in self.workflow["user_inputs"]["answers"].items():
                content += f"- **{key}:** {value}\n"

        content += """
---

## Workflow Steps

"""
        for step in self.workflow["steps"]:
            content += f"""### Step {step['step_id']}: {step['name']}

- **Skill:** {step['skill']}
- **Action:** {step.get('action', 'execute')}
- **Status:** {step.get('status', 'pending')}

"""
            if step.get("outputs"):
                content += "**Outputs:**\n```json\n"
                content += json.dumps(step["outputs"], indent=2)
                content += "\n```\n\n"

        content += """---

*Developed by Team 10x.in | https://10x.in*
"""

        with open(output_file, "w") as f:
            f.write(content)

        print(f"Markdown exported: {output_file}")
        return str(output_file)

    def export_all(self, formats: list = None) -> dict:
        """Export to all requested formats."""
        if formats is None:
            formats = ["json", "md"]  # Default formats that don't require extra deps

        results = {}

        for fmt in formats:
            if fmt == "json":
                results["json"] = self.export_json()
            elif fmt == "pdf":
                results["pdf"] = self.export_pdf()
            elif fmt == "ppt" or fmt == "pptx":
                results["ppt"] = self.export_ppt()
            elif fmt == "md" or fmt == "markdown":
                results["md"] = self.export_markdown()

        return results


def main():
    if len(sys.argv) < 2:
        print("Usage: python export_outputs.py <workflow_path> [formats]")
        print("Formats: json, pdf, ppt, md (comma-separated)")
        print("Example: python export_outputs.py workflow.json json,pdf,ppt")
        sys.exit(1)

    workflow_path = sys.argv[1]
    formats = sys.argv[2].split(",") if len(sys.argv) > 2 else ["json", "md"]

    if not os.path.exists(workflow_path):
        print(f"Workflow not found: {workflow_path}")
        sys.exit(1)

    exporter = OutputExporter(workflow_path)
    exporter.load_workflow()
    results = exporter.export_all(formats)

    print("\n--- EXPORT RESULTS ---")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
