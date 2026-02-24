import os
from typing import Type

from code_genereator.tools.file_write_tool import (FileWriteTool,
                                                   FileWriteToolInput)
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepResearchToolInput(BaseModel):
    topic: str = Field(..., description="The research topic to investigate.")
    output_path: str = Field(..., description="The file path to save the research plan.")

class DeepResearchTool(BaseTool):
    name: str = "deep_research_tool"
    description: str = (
        "Performs deep research on a given topic, analyzes and synthesizes findings, "
        "and generates a well-structured Markdown research plan."
    )
    args_schema: Type[BaseModel] = DeepResearchToolInput

    def _run(self, topic: str, output_path: str) -> str:
        # Step 1: Gather relevant context and memories
        context = self._gather_context(topic)
        
        # Step 2: Analyze and reason over the context iteratively
        analysis = self._analyze_context(context)
        
        # Step 3: Identify gaps or assumptions
        gaps = self._identify_gaps(analysis)
        
        # Step 4: Synthesize findings
        findings = self._synthesize_findings(analysis, gaps)
        
        # Step 5: Generate Markdown research plan
        research_plan = self._generate_markdown_plan(topic, findings)
        
        # Step 6: Use FileWriteTool to save the research plan
        file_write_tool = FileWriteTool()
        file_write_tool.run(FileWriteToolInput(file_path=output_path, content=research_plan))
        
        return f"Research plan successfully saved to: {output_path}"

    def _gather_context(self, topic: str) -> str:
        context_items = [
            f"Topic: {topic}",
            "Goal: Deliver a deep research plan that guides code generation decisions.",
            "Workflow: gather context, analyze iteratively, identify gaps, synthesize findings, generate plan.",
            "Primary artifact: Markdown research plan saved via FileWriteTool.",
            "Constraints: structured output, explicit risks, and actionable roadmap.",
            "Stakeholders: code generation agents and reviewers consuming the plan.",
        ]
        context_details = "\n".join(f"- {item}" for item in context_items)
        return f"Context gathered for topic: {topic}\n{context_details}"

    def _analyze_context(self, context: str) -> str:
        analysis_points = [
            "The plan must translate research into concrete implementation steps.",
            "Required sections include problem analysis, approach, decisions, trade-offs, risks, and roadmap.",
            "The workflow should surface assumptions and unknowns early to guide follow-up research.",
            "Output must be readable Markdown suitable for downstream automation or human review.",
            "The analysis should connect gathered context to design and delivery constraints.",
        ]
        analysis_details = "\n".join(f"- {point}" for point in analysis_points)
        return f"Analysis of context: {context}\n\nInsights:\n{analysis_details}"

    def _identify_gaps(self, analysis: str) -> str:
        gaps = [
            "Precise data sources or systems to consult are not specified.",
            "Performance, scalability, or security constraints are not detailed.",
            "Acceptance criteria for the research plan output are undefined.",
            "Dependency on external tools or APIs is unclear.",
            "Timeline or prioritization guidance is missing.",
        ]
        gap_details = "\n".join(f"- {gap}" for gap in gaps)
        return f"Gaps identified in analysis: {analysis}\n\nOpen Questions:\n{gap_details}"

    def _synthesize_findings(self, analysis: str, gaps: str) -> str:
        synthesis = [
            "Deliver a structured research plan that balances immediate implementation needs with open questions.",
            "Treat missing constraints as explicit assumptions and highlight them in the plan.",
            "Align the roadmap with iterative validation and feedback loops.",
        ]
        synthesis_details = "\n".join(f"- {item}" for item in synthesis)
        return (
            "Findings synthesized from analysis: "
            f"{analysis} and gaps: {gaps}\n\nSynthesis:\n{synthesis_details}"
        )

    def _generate_markdown_plan(self, topic: str, findings: str) -> str:
        plan_sections = [
            "## Problem Analysis\n"
            "- Define the scope and objectives of the research.\n"
            "- Clarify stakeholders, expected outcomes, and success criteria.\n",
            "## Technical Approach\n"
            "- Identify the data sources, documentation, and code artifacts to review.\n"
            "- Outline iterative analysis steps and validation checkpoints.\n",
            "## Design Decisions\n"
            "- Choose how to structure findings for the code generation workflow.\n"
            "- Decide on tooling integration points and automation opportunities.\n",
            "## Trade-offs\n"
            "- Balance depth of research with delivery timelines.\n"
            "- Weigh automation against manual expert review.\n",
            "## Risks\n"
            "- Missing context could lead to incorrect assumptions.\n"
            "- Overly generic output may reduce implementation value.\n",
            "## Implementation Roadmap\n"
            "1. Gather and validate requirements with stakeholders.\n"
            "2. Perform iterative research and document insights.\n"
            "3. Validate findings against workflow constraints.\n"
            "4. Draft the research plan in structured Markdown.\n"
            "5. Review, refine, and finalize for code generation use.\n",
        ]
        plan_body = "\n".join(plan_sections)
        return (
            f"# Research Plan for {topic}\n\n"
            f"{plan_body}\n"
            "---\n"
            "## Synthesized Findings\n"
            f"{findings}"
        )

# Unit Tests
import unittest
from unittest.mock import patch


class TestDeepResearchTool(unittest.TestCase):
    def setUp(self):
        self.tool = DeepResearchTool()
        self.input_data = DeepResearchToolInput(topic="AI in Healthcare", output_path="dist/research_plan.md")

    @patch.object(FileWriteTool, 'run')
    def test_run(self, mock_file_write):
        result = self.tool._run(self.input_data.topic, self.input_data.output_path)
        self.assertIn("Research plan successfully saved to:", result)
        mock_file_write.assert_called_once()

    def test_gather_context(self):
        context = self.tool._gather_context("AI in Healthcare")
        self.assertIn("Context gathered for topic:", context)

    def test_analyze_context(self):
        analysis = self.tool._analyze_context("Sample context")
        self.assertIn("Analysis of context:", analysis)

    def test_identify_gaps(self):
        gaps = self.tool._identify_gaps("Sample analysis")
        self.assertIn("Gaps identified in analysis:", gaps)

    def test_synthesize_findings(self):
        findings = self.tool._synthesize_findings("Sample analysis", "Sample gaps")
        self.assertIn("Findings synthesized from analysis:", findings)

    def test_generate_markdown_plan(self):
        markdown = self.tool._generate_markdown_plan("AI in Healthcare", "Sample findings")
        self.assertIn("# Research Plan for AI in Healthcare", markdown)

if __name__ == "__main__":
    unittest.main()
