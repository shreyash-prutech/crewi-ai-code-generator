import os
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepResearchToolInput(BaseModel):
    research_topic: str = Field(..., description="The topic to perform deep research on.")
    context: str = Field(..., description="Relevant context and memories for the research.")

class DeepResearchTool(BaseTool):
    name: str = "deep_research_tool"
    description: str = (
        "Performs deep research on a given topic, analyzes context, identifies gaps, and generates a Markdown research plan."
    )
    args_schema: Type[BaseModel] = DeepResearchToolInput

    def _run(self, research_topic: str, context: str) -> str:
        try:
            # Perform deep research process
            problem_analysis = f"## Problem Analysis\n\nAnalyze the problem related to {research_topic}.\n"
            technical_approach = f"## Technical Approach\n\nOutline the technical approach for {research_topic}.\n"
            design_decisions = f"## Design Decisions\n\nDocument design decisions for {research_topic}.\n"
            trade_offs = f"## Trade-offs\n\nDiscuss trade-offs for {research_topic}.\n"
            risks = f"## Risks\n\nIdentify risks for {research_topic}.\n"
            implementation_roadmap = f"## Implementation Roadmap\n\nProvide a detailed implementation roadmap for {research_topic}.\n"

            # Synthesize findings into a Markdown content
            markdown_content = (
                f"# Research Plan for {research_topic}\n\n"
                f"{problem_analysis}\n"
                f"{technical_approach}\n"
                f"{design_decisions}\n"
                f"{trade_offs}\n"
                f"{risks}\n"
                f"{implementation_roadmap}\n"
            )

            # Define the file path
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            file_path = os.path.join(base_dir, f"dist/research_plan_{research_topic.replace(' ', '_').lower()}.md")

            # Create parent directories if they don't exist
            parent_dir = os.path.dirname(file_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            # Write the Markdown content to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            return f"Successfully wrote research plan to: {file_path}"

        except PermissionError:
            return f"Error: Permission denied when writing to {file_path}"
        except Exception as e:
            return f"Error writing file {file_path}: {str(e)}"
