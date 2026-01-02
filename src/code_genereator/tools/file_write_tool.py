"""
FileWriteTool for saving generated code files.

This tool allows agents (particularly the Judge) to write code files
to the filesystem, organizing them in the dist/ directory.
"""

import os
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class FileWriteToolInput(BaseModel):
    """Input schema for FileWriteTool."""
    
    file_path: str = Field(
        ...,
        description="The relative path where the file should be saved (e.g., 'dist/backend/main.py')"
    )
    content: str = Field(
        ...,
        description="The content to write to the file"
    )


class FileWriteTool(BaseTool):
    """
    Tool for writing files to the filesystem.
    
    Used by the Judge agent to save generated code files
    to the dist/ directory structure.
    """
    
    name: str = "file_write_tool"
    description: str = (
        "Writes content to a file at the specified path. "
        "Use this to save generated code files to the dist/ directory. "
        "The tool will create any necessary parent directories. "
        "Example: file_path='dist/backend/main.py', content='# Python code here'"
    )
    args_schema: Type[BaseModel] = FileWriteToolInput
    
    def _run(self, file_path: str, content: str) -> str:
        """
        Write content to the specified file path.
        
        Args:
            file_path: Relative path for the file (e.g., 'dist/backend/main.py')
            content: The content to write to the file
            
        Returns:
            Success message or error description
        """
        try:
            # Get the base directory (project root)
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            full_path = os.path.join(base_dir, file_path)
            
            # Create parent directories if they don't exist
            parent_dir = os.path.dirname(full_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            # Write the file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote file to: {file_path}"
            
        except PermissionError:
            return f"Error: Permission denied when writing to {file_path}"
        except Exception as e:
            return f"Error writing file {file_path}: {str(e)}"

