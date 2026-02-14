from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepResearchToolInput(BaseModel):
    topic: str = Field(..., description="The topic for which to conduct deep research.")
    current_year: int = Field(..., description="The current year to contextualize the research.")

class DeepResearchTool(BaseTool):
    name: str = "Deep Research Tool"
    description: str = (
        "A tool to perform deep research by gathering context, analyzing information, identifying gaps, and synthesizing findings into a structured Markdown research plan."
    )
    args_schema: Type[BaseModel] = DeepResearchToolInput

    def _run(self, topic: str, current_year: int) -> str:
        context = self._gather_context(topic, current_year)
        analysis = self._analyze_context(context)
        gaps = self._identify_gaps(analysis)
        findings = self._synthesize_findings(analysis, gaps)
        return self._generate_markdown(findings)

    def _gather_context(self, topic: str, current_year: int) -> dict:
        # Simulate gathering context and memories related to the topic
        return {"context": f"Contextual information for {topic} in {current_year}"}

    def _analyze_context(self, context: dict) -> dict:
        # Simulate analysis of the gathered context
        return {"analysis": f"Analysis of context: {context['context']}"}

    def _identify_gaps(self, analysis: dict) -> list:
        # Simulate identification of gaps or assumptions
        return ["Identified gap 1", "Identified gap 2"]

    def _synthesize_findings(self, analysis: dict, gaps: list) -> dict:
        # Simulate synthesis of findings
        return {
            "problem_analysis": analysis["analysis"],
            "gaps": gaps,
            "technical_approach": "Proposed technical approach",
            "design_decisions": "Design decisions made",
            "trade_offs": "Trade-offs considered",
            "risks": "Potential risks identified",
            "implementation_roadmap": "Detailed implementation roadmap"
        }

    def _generate_markdown(self, findings: dict) -> str:
        # Generate a Markdown document from the synthesized findings
        markdown = f"# Research Plan for {findings['problem_analysis']}\n\n"
        markdown += "## Problem Analysis\n"
        markdown += f"{findings['problem_analysis']}\n\n"
        markdown += "## Identified Gaps\n"
        markdown += "\n".join(f"- {gap}" for gap in findings['gaps']) + "\n\n"
        markdown += "## Technical Approach\n"
        markdown += f"{findings['technical_approach']}\n\n"
        markdown += "## Design Decisions\n"
        markdown += f"{findings['design_decisions']}\n\n"
        markdown += "## Trade-offs\n"
        markdown += f"{findings['trade_offs']}\n\n"
        markdown += "## Risks\n"
        markdown += f"{findings['risks']}\n\n"
        markdown += "## Implementation Roadmap\n"
        markdown += f"{findings['implementation_roadmap']}\n"
        return markdown
