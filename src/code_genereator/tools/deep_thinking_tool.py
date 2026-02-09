import os
import textwrap
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepThinkingToolInput(BaseModel):
    objective: str = Field(..., description="The main objective for deep thinking.")
    memories: List[str] = Field(default_factory=list, description="List of memories to consider.")
    constraints: Optional[str] = Field(None, description="Constraints to consider.")
    write_path: Optional[str] = Field(None, description="Path to write the generated Markdown plan.")


class DeepThinkingTool(BaseTool):
    name: str = "Deep Thinking Tool"
    description: str = "Tool to enable deep thinking in the code generation workflow, creating a comprehensive Markdown plan."
    args_schema: Type[BaseModel] = DeepThinkingToolInput

    def _run(self, objective: str, memories: List[str], constraints: Optional[str] = None, write_path: Optional[str] = None) -> str:
        # Normalize and deduplicate memories
        normalized_memories = list(set(memory.strip() for memory in memories if memory.strip()))

        # Synthesize key insights
        key_insights = self._synthesize_insights(normalized_memories)

        # Build Markdown plan
        markdown_plan = self._build_markdown_plan(objective, key_insights, constraints)

        # Write to file if write_path is provided
        if write_path:
            self._write_to_file(markdown_plan, write_path)
            return f"Markdown plan written to {write_path}\n\n{markdown_plan}"

        return markdown_plan

    def _synthesize_insights(self, memories: List[str]) -> List[str]:
        insights = []
        for memory in memories:
            insights.extend(textwrap.wrap(memory, width=80))
        return insights

    def _build_markdown_plan(self, objective: str, key_insights: List[str], constraints: Optional[str]) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        plan = f"# Deep Thinking Plan\n\n**Generated:** {now}\n\n## Objective\n\n{objective}\n\n"
        if constraints:
            plan += f"## Constraints\n\n{constraints}\n\n"
        plan += "## Memory Synthesis (Key Insights)\n\n"
        for insight in key_insights:
            plan += f"- {insight}\n"
        plan += "\n## Assumptions & Gaps\n\n## Risks\n\n## Decision Points\n\n## Strategy\n\n## Implementation Plan\n\n## Test Plan\n\n## Deliverables\n\n## Next Steps\n"
        return plan

    def _write_to_file(self, content: str, write_path: str):
        path = Path(write_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8') as file:
            file.write(content)
