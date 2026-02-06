import os
from datetime import datetime
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepThinkingToolInput(BaseModel):
    input_data: str = Field(..., description="The data to be analyzed for deep thinking.")
    output_path: str = Field(..., description="The relative path where the markdown plan should be saved.")

class DeepThinkingTool(BaseTool):
    name: str = "deep_thinking_tool"
    description: str = "Analyzes input data to simulate deep thinking and generates a markdown plan."

    args_schema: Type[BaseModel] = DeepThinkingToolInput

    def analyze_and_plan(self, input_data: str, output_path: str) -> str:
        try:
            # Simulate deep thinking by processing input data
            processed_content = self._process_input(input_data)

            # Generate markdown content
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            markdown_content = f"# Deep Thinking Plan\n\n**Generated:** {timestamp}\n\n## Analysis\n\n{processed_content}\n"

            # Get the base directory (project root)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            full_path = os.path.join(base_dir, output_path)

            # Create parent directories if they don't exist
            parent_dir = os.path.dirname(full_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            # Write the markdown file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            return f"Successfully wrote markdown plan to: {output_path}"

        except PermissionError:
            return f"Error: Permission denied when writing to {output_path}"
        except Exception as e:
            return f"Error writing markdown plan {output_path}: {str(e)}"

    def _process_input(self, input_data: str) -> str:
        # Placeholder for deep thinking logic, e.g., summarization
        return f"Processed content of input data: {input_data[:100]}..."

# Unit tests
import unittest
from unittest.mock import mock_open, patch


class TestDeepThinkingTool(unittest.TestCase):
    def setUp(self):
        self.tool = DeepThinkingTool()

    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    def test_analyze_and_plan_success(self, mock_makedirs, mock_open):
        input_data = "This is a test input for deep thinking."
        output_path = "dist/plans/deep_thinking_plan.md"
        result = self.tool.analyze_and_plan(input_data, output_path)
        self.assertIn("Successfully wrote markdown plan to", result)
        mock_open.assert_called_once_with(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), output_path), 'w', encoding='utf-8')

    @patch("builtins.open", side_effect=PermissionError)
    def test_analyze_and_plan_permission_error(self, mock_open):
        input_data = "This is a test input for deep thinking."
        output_path = "dist/plans/deep_thinking_plan.md"
        result = self.tool.analyze_and_plan(input_data, output_path)
        self.assertIn("Error: Permission denied", result)

    def test_process_input(self):
        input_data = "This is a test input for deep thinking."
        processed_content = self.tool._process_input(input_data)
        self.assertIn("Processed content of input data", processed_content)

if __name__ == "__main__":
    unittest.main()
