import datetime
import os

from pydantic import BaseModel, Field
from src.code_genereator.tools.file_write_tool import FileWriteTool


class DeepThinkingToolInput(BaseModel):
    memory_data: str = Field(..., description="Memory data for deep thinking.")

class DeepThinkingTool:
    name: str = "deep_thinking_tool"
    description: str = "Processes memories to generate a deep thinking markdown plan."
    args_schema: DeepThinkingToolInput = DeepThinkingToolInput

    def __init__(self, memory_data: str):
        self.memory_data = memory_data

    def generate_md_plan(self):
        insights = self.reflect_on_memories(self.memory_data)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"deep_thinking_plan_{timestamp}.md"
        content = f"# Deep Thinking Plan - {timestamp}\n\n## Insights\n{insights}"
        file_path = f"dist/plans/{filename}"
        file_write_tool = FileWriteTool()
        return file_write_tool._run(file_path=file_path, content=content)

    def reflect_on_memories(self, memory_data: str) -> str:
        # Simulated deep thinking logic to analyze memories and generate insights
        insights = f"Processed insights based on provided memories: {memory_data}"
        return insights
