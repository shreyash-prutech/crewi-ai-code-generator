from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepResearchToolInput(BaseModel):
    """Input schema for DeepResearchTool."""
    topic: str = Field(..., description="The main topic of research.")
    scope: str = Field(..., description="The scope of the research.")
    depth: int = Field(default=1, description="The depth of research analysis.")

class DeepResearchTool(BaseTool):
    name: str = "Deep Research Tool"
    description: str = "Performs deep research to generate a structured Markdown document outlining the research plan."
    args_schema: Type[BaseModel] = DeepResearchToolInput

    def _run(self, topic: str, scope: str, depth: int) -> str:
        context = self.gather_context(topic, scope)
        analysis = self.analyze_context(context, depth)
        gaps = self.identify_gaps(analysis)
        markdown_report = self.synthesize_findings(topic, analysis, gaps)
        return markdown_report

    def gather_context(self, topic, scope):
        return f"Gathering context for {topic} within the scope of {scope}."

    def analyze_context(self, context, depth):
        return f"Analyzing context at depth {depth}: {context}"

    def identify_gaps(self, analysis):
        return f"Identifying gaps in the analysis: {analysis}"

    def synthesize_findings(self, topic, analysis, gaps):
        return f"""# Research Plan for {topic}

## Analysis
{analysis}

## Identified Gaps
{gaps}

## Conclusion
Detailed implementation roadmap and risk analysis based on the above findings."""
