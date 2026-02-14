import os
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepResearchToolInput(BaseModel):
    topic: str = Field(..., description="The topic for deep research.")

class DeepResearchTool(BaseTool):
    name: str = "deep_research_tool"
    description: str = (
        "Performs deep research and outputs a structured Markdown report "
        "including problem analysis, technical approach, design decisions, "
        "trade-offs, risks, and an implementation roadmap."
    )
    args_schema: Type[BaseModel] = DeepResearchToolInput

    def _gather_context(self, topic: str) -> str:
        # Simulate gathering context related to the topic
        return f"Context for {topic}"

    def _analyze_data(self, context: str) -> str:
        # Simulate data analysis
        return f"Analysis of {context}"

    def _identify_gaps(self, analysis: str) -> str:
        # Simulate identifying gaps
        return f"Gaps in {analysis}"

    def _synthesize_findings(self, analysis: str, gaps: str) -> str:
        # Simulate synthesizing findings
        return f"Findings based on {analysis} with {gaps}"

    def _generate_markdown_report(self, findings: str) -> str:
        # Generate a Markdown report
        report_content = (
            "# Deep Research Report\n\n"
            "## Problem Analysis\n"
            f"{findings}\n\n"
            "## Technical Approach\n"
            "Details of the technical approach.\n\n"
            "## Design Decisions\n"
            "Design decisions made during the process.\n\n"
            "## Trade-offs\n"
            "Trade-offs considered.\n\n"
            "## Risks\n"
            "Potential risks identified.\n\n"
            "## Implementation Roadmap\n"
            "Step-by-step implementation plan.\n"
        )
        file_path = "dist/research_report.md"
        self._write_file(file_path, report_content)
        return f"Markdown report generated at {file_path}"

    def _write_file(self, file_path: str, content: str) -> None:
        # Use FileWriteTool to write the file
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        full_path = os.path.join(base_dir, file_path)
        parent_dir = os.path.dirname(full_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _run(self, topic: str) -> str:
        context = self._gather_context(topic)
        analysis = self._analyze_data(context)
        gaps = self._identify_gaps(analysis)
        findings = self._synthesize_findings(analysis, gaps)
        return self._generate_markdown_report(findings)
