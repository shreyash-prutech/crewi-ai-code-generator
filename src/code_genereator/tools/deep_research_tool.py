from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .file_write_tool import FileWriteTool, FileWriteToolInput


class DeepResearchToolInput(BaseModel):
    topic: str = Field(..., description="The topic to research.")
    context: str = Field(..., description="Relevant context or background information.")
    iterations: int = Field(3, description="Number of iterations for analysis and reasoning.")

class DeepResearchTool(BaseTool):
    name: str = "deep_research_tool"
    description: str = (
        "Performs deep research on a given topic, analyzes context, identifies gaps, and generates a Markdown research plan."
    )
    args_schema: Type[BaseModel] = DeepResearchToolInput

    def _run(self, topic: str, context: str, iterations: int) -> str:
        research_plan = f"# Research Plan for {topic}\n\n"
        research_plan += f"## Context\n\n{context}\n\n"
        research_plan += "## Analysis and Findings\n\n"
        
        for i in range(iterations):
            research_plan += f"### Iteration {i+1}\n\n"
            research_plan += f"- Analysis of {topic} in context of iteration {i+1}.\n"
            research_plan += f"- Identified gaps and assumptions in iteration {i+1}.\n"
            research_plan += f"- Synthesized findings for iteration {i+1}.\n\n"
        
        research_plan += "## Design Decisions\n\n"
        research_plan += "- Decision 1: Explanation and rationale.\n"
        research_plan += "- Decision 2: Explanation and rationale.\n\n"
        
        research_plan += "## Trade-offs and Risks\n\n"
        research_plan += "- Trade-off 1: Explanation and mitigation.\n"
        research_plan += "- Risk 1: Explanation and mitigation.\n\n"
        
        research_plan += "## Implementation Roadmap\n\n"
        research_plan += "1. Step 1: Detailed description.\n"
        research_plan += "2. Step 2: Detailed description.\n"
        research_plan += "3. Step 3: Detailed description.\n\n"
        
        file_write_tool = FileWriteTool()
        file_path = f"dist/research/{topic.replace(' ', '_').lower()}_research_plan.md"
        file_write_tool._run(file_path=file_path, content=research_plan)
        
        return f"Successfully wrote research plan to: {file_path}"
