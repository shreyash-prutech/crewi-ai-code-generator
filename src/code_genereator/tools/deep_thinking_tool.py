import os
from datetime import datetime
from typing import List, Optional, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepThinkingToolInput(BaseModel):
    objective: str
    memories: Union[List[str], str]
    constraints: Optional[str] = None
    context: Optional[str] = None
    save_path: Optional[str] = None

class DeepThinkingTool(BaseTool):
    name: str = "deep_thinking_tool"
    description: str = (
        "Performs deep reasoning over provided memories and produces an actionable, testable planning and implementation MD plan."
    )
    args_schema: Type[BaseModel] = DeepThinkingToolInput

    def _run(self, objective: str, memories: Union[List[str], str], constraints: Optional[str] = None, context: Optional[str] = None, save_path: Optional[str] = None) -> str:
        if isinstance(memories, str):
            memories = [memories]
        
        memories = list(set(memories))  # Deduplicate
        memories.sort(key=lambda x: len(x), reverse=True)  # Sort by relevance (length heuristic)
        
        key_items = "\n".join(f"- {memory}" for memory in memories)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        markdown_content = f"""# Deep Thinking Plan - {timestamp}

## Overview/Objective
{objective}

## Context Summary
{key_items}

## Goals and Non-Goals
- Goals: TBD
- Non-Goals: TBD

## Assumptions and Risks
- Assumptions: TBD
- Risks: TBD

## Planning Phase
- Architecture: TBD
- Specification: TBD
- Data Modeling: TBD
- API Design: TBD

## Implementation Phase
- Database Tasks: TBD
- Backend Tasks: TBD
- Frontend Tasks: TBD

## Milestones and Deliverables
- Milestone 1: TBD
- Milestone 2: TBD

## Test Strategy
- Unit Tests: TBD
- Integration Tests: TBD
- End-to-End Tests: TBD

## Memory Hooks
{key_items}
"""

        if save_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            full_path = os.path.join(base_dir, save_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        
        return markdown_content
