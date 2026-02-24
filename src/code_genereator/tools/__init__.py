"""Tools for the Agentic Software Factory."""

from code_genereator.tools.custom_tool import MyCustomTool
from code_genereator.tools.deep_research_tool import DeepResearchTool
from code_genereator.tools.file_write_tool import FileWriteTool

AVAILABLE_TOOLS = [
    MyCustomTool,
    FileWriteTool,
    DeepResearchTool,
]

__all__ = ["MyCustomTool", "FileWriteTool"]

