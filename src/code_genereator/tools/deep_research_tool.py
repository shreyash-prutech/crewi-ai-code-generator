import os
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .file_write_tool import FileWriteTool


class DeepResearchToolInput(BaseModel):
    """Input schema for DeepResearchTool."""
    requirement: str = Field(..., description="The software requirement to analyze.")
    context: str = Field(..., description="Additional context for the research.")

class DeepResearchTool(BaseTool):
    name: str = "deep_research_tool"
    description: str = (
        "Performs deep research on the given requirement and context, "
        "analyzes and synthesizes findings into a Markdown research plan."
    )
    args_schema: Type[BaseModel] = DeepResearchToolInput

    def _run(self, requirement: str, context: str) -> str:
        # Perform research process
        research_plan = (
            f"# Research Plan\n\n"
            f"## Requirement\n{requirement}\n\n"
            f"## Context\n{context}\n\n"
            f"## Analysis\n"
            f"### Problem Analysis\n"
            f"Analyze the problem based on the requirement and context.\n\n"
            f"### Technical Approach\n"
            f"Outline the technical approach to address the requirement.\n\n"
            f"### Design Decisions\n"
            f"Detail the design decisions made during the analysis.\n\n"
            f"### Trade-offs\n"
            f"Discuss the trade-offs considered during the design.\n\n"
            f"### Risks\n"
            f"Identify potential risks and mitigation strategies.\n\n"
            f"### Implementation Roadmap\n"
            f"Provide a detailed implementation roadmap with milestones."
        )
        
        # Save the research plan using FileWriteTool
        file_write_tool = FileWriteTool()
        file_write_tool.run(file_path="dist/research_plan.md", content=research_plan)
        
        return "Research plan generated and saved to dist/research_plan.md"
