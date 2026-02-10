import re
from collections import Counter
from datetime import datetime
from typing import Dict, List, Optional, Type, Union

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DeepThinkToolInput(BaseModel):
    objective: str = Field(..., description="The main objective of the task.")
    memories: Union[List[str], str] = Field(..., description="Memories related to the task.")
    constraints: Optional[Union[List[str], str]] = Field(None, description="Constraints for the task.")
    deliverables: Optional[Union[List[str], str]] = Field(None, description="Expected deliverables.")
    filename: Optional[str] = Field(None, description="Filename to write the Markdown plan to.")

class DeepThinkTool(BaseTool):
    name: str = "DeepThinkTool"
    description: str = "A tool to enable deep thinking in the code generation workflow by analyzing memories and generating a detailed Markdown plan."
    args_schema: Type[BaseModel] = DeepThinkToolInput

    def _run(self, objective: str, memories: Union[List[str], str], constraints: Optional[Union[List[str], str]] = None, deliverables: Optional[Union[List[str], str]] = None, filename: Optional[str] = None) -> str:
        memories = self._normalize_to_list(memories)
        constraints = self._normalize_to_list(constraints)
        deliverables = self._normalize_to_list(deliverables)

        themes = self._extract_themes(memories)
        requirements = self._derive_requirements(objective, memories)
        risks, open_questions = self._detect_risks_and_questions(memories)

        markdown = self._generate_markdown_plan(objective, memories, constraints, deliverables, themes, requirements, risks, open_questions)

        if filename:
            with open(filename, 'w') as file:
                file.write(markdown)

        return markdown

    def _normalize_to_list(self, item: Union[List[str], str, None]) -> List[str]:
        if item is None:
            return []
        if isinstance(item, str):
            return [line.strip() for line in item.split('\n') if line.strip()]
        return item

    def _extract_themes(self, memories: List[str]) -> Dict[str, List[str]]:
        word_counter = Counter()
        for memory in memories:
            words = re.findall(r'\w+', memory.lower())
            word_counter.update(words)
        
        common_words = {word for word, count in word_counter.items() if count > 1}
        themes = {word: [] for word in common_words}

        for memory in memories:
            for word in common_words:
                if word in memory.lower():
                    themes[word].append(memory)
        
        return themes

    def _derive_requirements(self, objective: str, memories: List[str]) -> List[str]:
        requirements = []
        pattern = re.compile(r'\b(must|should|need to|require)\b', re.IGNORECASE)
        for text in [objective] + memories:
            matches = pattern.findall(text)
            if matches:
                requirements.append(text)
        return requirements

    def _detect_risks_and_questions(self, memories: List[str]) -> (List[str], List[str]):
        risks = []
        open_questions = []
        risk_keywords = ['risk', 'issue', 'problem', 'challenge']
        for memory in memories:
            if any(keyword in memory.lower() for keyword in risk_keywords):
                risks.append(memory)
            if '?' in memory:
                open_questions.append(memory)
        return risks, open_questions

    def _generate_markdown_plan(self, objective: str, memories: List[str], constraints: List[str], deliverables: List[str], themes: Dict[str, List[str]], requirements: List[str], risks: List[str], open_questions: List[str]) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        markdown = f"# Plan for {objective}\n\n"
        markdown += f"**Generated on:** {timestamp}\n\n"
        markdown += f"## Objective\n{objective}\n\n"
        markdown += "## Inputs Summary\n"
        markdown += f"**Memories:** {len(memories)} items\n"
        markdown += f"**Constraints:** {len(constraints)} items\n"
        markdown += f"**Deliverables:** {len(deliverables)} items\n\n"
        markdown += "## Memory Themes\n"
        for theme, items in themes.items():
            markdown += f"### {theme.capitalize()}\n"
            for item in items:
                markdown += f"- {item}\n"
            markdown += "\n"
        markdown += "## Assumptions & Requirements\n"
        for requirement in requirements:
            markdown += f"- {requirement}\n"
        markdown += "\n"
        markdown += "## Constraints\n"
        for constraint in constraints:
            markdown += f"- {constraint}\n"
        markdown += "\n"
        markdown += "## Deliverables\n"
        for deliverable in deliverables:
            markdown += f"- {deliverable}\n"
        markdown += "\n"
        markdown += "## Plan\n"
        markdown += "### High-level Steps\n"
        markdown += "- Step 1: Initial analysis\n"
        markdown += "- Step 2: Detailed planning\n"
        markdown += "- Step 3: Implementation\n"
        markdown += "- Step 4: Testing\n"
        markdown += "- Step 5: Review and iteration\n\n"
        markdown += "### Per-theme Sub-steps\n"
        for theme in themes:
            markdown += f"#### {theme.capitalize()}\n"
            markdown += f"- Analyze {theme} related memories\n"
            markdown += f"- Derive actions based on {theme}\n"
            markdown += "\n"
        markdown += "## Implementation Details\n"
        markdown += "- [ ] Review all memories\n"
        markdown += "- [ ] Validate requirements\n"
        markdown += "- [ ] Address constraints\n"
        markdown += "- [ ] Ensure deliverables are met\n\n"
        markdown += "## Risks & Mitigations\n"
        for risk in risks:
            markdown += f"- {risk}\n"
        markdown += "\n"
        markdown += "## Test Plan\n"
        markdown += "- Unit tests for each function\n"
        markdown += "- Integration tests for the workflow\n"
        markdown += "- User acceptance tests\n\n"
        markdown += "## Milestones\n"
        markdown += "- Milestone 1: Initial draft\n"
        markdown += "- Milestone 2: Review and feedback\n"
        markdown += "- Milestone 3: Final implementation\n\n"
        markdown += "## Open Questions\n"
        for question in open_questions:
            markdown += f"- {question}\n"
        markdown += "\n"
        markdown += "## Appendix: Raw Memories\n"
        for memory in memories:
            markdown += f"- {memory}\n"
        return markdown
