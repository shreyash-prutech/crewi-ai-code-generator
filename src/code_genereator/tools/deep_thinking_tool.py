import os
from typing import Any, Dict, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepThinkingToolInput(BaseModel):
    memory_data: Dict[str, Any] = Field(..., description="Data representing memories for analysis.")
    parameters: Dict[str, Any] = Field(..., description="Parameters to guide the deep thinking process.")

class DeepThinkingTool(BaseTool):
    name: str = "deep_thinking_tool"
    description: str = (
        "Performs deep analysis on provided memory data and generates a markdown plan for planning and implementation."
    )
    args_schema: Type[BaseModel] = DeepThinkingToolInput

    def _run(self, memory_data: Dict[str, Any], parameters: Dict[str, Any]) -> str:
        # Perform deep analysis on memory_data using parameters
        analysis_result = self._deep_analysis(memory_data, parameters)
        
        # Generate markdown content
        markdown_content = self._generate_markdown(analysis_result)
        
        # Define file path
        file_path = "dist/plans/deep_thinking_plan.md"
        
        # Write markdown to file
        self._write_markdown(file_path, markdown_content)
        
        return file_path

    def _deep_analysis(self, memory_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Implementing deep analysis logic
        # For demonstration: aggregate some counts/statistics
        summary = "Analyzed {} memory items with specific parameters.".format(len(memory_data))
        details = {key: len(value) if isinstance(value, list) else str(value) for key, value in memory_data.items()}
        # This aims to show count of items for each key in memory_data
        return {"summary": summary, "details": details}

    def _generate_markdown(self, analysis_result: Dict[str, Any]) -> str:
        # Convert analysis result into markdown format
        markdown = "# Deep Thinking Plan\n\n"
        markdown += f"## Summary\n{analysis_result['summary']}\n\n"
        markdown += "## Details\n"
        for key, value in analysis_result['details'].items():
            markdown += f"- **{key}**: {value}\n"
        return markdown

    def _write_markdown(self, file_path: str, content: str) -> None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        full_path = os.path.join(base_dir, file_path)
        parent_dir = os.path.dirname(full_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
