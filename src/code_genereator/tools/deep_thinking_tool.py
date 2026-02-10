import os
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepThinkingToolInput(BaseModel):
    memory_data: str = Field(..., description="Data for deep analysis.")
    output_path: str = Field(..., description="Path to save the generated markdown plan.")

class DeepThinkingTool(BaseTool):
    name: str = "deep_thinking_tool"
    description: str = (
        "Analyzes memory data deeply and generates a markdown plan. "
        "Saves the plan to the specified output path."
    )
    args_schema: Type[BaseModel] = DeepThinkingToolInput

    def _run(self, memory_data: str, output_path: str) -> str:
        # Perform deep analysis on memory_data
        analysis_result = self._analyze_memory(memory_data)
        
        # Generate markdown content
        markdown_content = self._generate_markdown(analysis_result)
        
        # Write markdown to the specified output path
        self._write_to_file(output_path, markdown_content)
        
        return f"Markdown plan successfully written to: {output_path}"

    def _analyze_memory(self, memory_data: str) -> str:
        # Placeholder for deep analysis logic
        return f"Analysis of memory data: {memory_data}"

    def _generate_markdown(self, analysis_result: str) -> str:
        # Create markdown content from analysis result
        return f"# Deep Thinking Plan\n\n## Analysis Result\n\n{analysis_result}\n"

    def _write_to_file(self, output_path: str, content: str):
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Write content to file
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)
