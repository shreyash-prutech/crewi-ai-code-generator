import datetime
import json
import pathlib
import re
from collections import Counter
from typing import Dict, List, Optional, Union

try:
    from crewai_tools import BaseTool
    from pydantic import BaseModel, Field
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

class DeepThinkingToolInput(BaseModel):
    objective: str = Field(..., description="The main objective for the deep-thinking process.")
    memories: Union[List[str], str, List[Dict[str, str]]] = Field(..., description="Memories to analyze.")
    constraints: Optional[List[str]] = Field(None, description="Constraints to consider.")
    output_dir: str = Field("plans", description="Directory to save the generated markdown plan.")
    return_content: bool = Field(False, description="Whether to return the content of the markdown plan.")

class DeepThinkingTool(BaseTool if CREWAI_AVAILABLE else object):
    name: str = "deep_thinking_tool"
    description: str = "Analyze provided memories and objective to produce a comprehensive markdown plan for planning and implementation."
    
    if CREWAI_AVAILABLE:
        args_schema: Type[BaseModel] = DeepThinkingToolInput

    def _run(self, objective: str, memories: Union[List[str], str, List[Dict[str, str]]], constraints: Optional[List[str]], output_dir: str, return_content: bool) -> Union[str, Dict[str, str]]:
        return self._execute(objective, memories, constraints, output_dir, return_content)

    def run(self, objective: str, memories: Union[List[str], str, List[Dict[str, str]]], constraints: Optional[List[str]], output_dir: str, return_content: bool) -> Union[str, Dict[str, str]]:
        return self._execute(objective, memories, constraints, output_dir, return_content)

    def _execute(self, objective: str, memories: Union[List[str], str, List[Dict[str, str]]], constraints: Optional[List[str]], output_dir: str, return_content: bool) -> Union[str, Dict[str, str]]:
        # Normalize inputs
        if isinstance(memories, str):
            memories = [memories]
        elif isinstance(memories, list) and all(isinstance(m, dict) for m in memories):
            memories = [m['content'] for m in memories if 'content' in m]

        # Extract keywords
        keywords = self._extract_keywords(memories)

        # Cluster memories
        clusters = self._cluster_memories(memories, keywords)

        # Generate markdown content
        markdown_content = self._generate_markdown(objective, constraints, clusters, memories)

        # Save markdown file
        output_path = self._save_markdown(markdown_content, objective, output_dir)

        if return_content:
            return json.dumps({"path": str(output_path), "content": markdown_content})
        return str(output_path)

    def _extract_keywords(self, memories: List[str]) -> List[str]:
        stopwords = set(["the", "and", "is", "in", "to", "of", "a", "with", "for", "on", "that", "this", "it", "as", "by", "an", "be", "are", "at", "from"])
        words = re.findall(r'\w+', ' '.join(memories).lower())
        filtered_words = [word for word in words if word not in stopwords]
        most_common = Counter(filtered_words).most_common(10)
        return [word for word, _ in most_common]

    def _cluster_memories(self, memories: List[str], keywords: List[str]) -> Dict[str, List[str]]:
        clusters = {keyword: [] for keyword in keywords}
        for memory in memories:
            for keyword in keywords:
                if keyword in memory.lower():
                    clusters[keyword].append(memory)
                    break
        return clusters

    def _generate_markdown(self, objective: str, constraints: Optional[List[str]], clusters: Dict[str, List[str]], memories: List[str]) -> str:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sanitized_objective = re.sub(r'\W+', '-', objective.lower()).strip('-')
        
        markdown = f"# Deep Thinking Plan for {objective}\n\n"
        markdown += f"**Generated on:** {timestamp}\n\n"
        markdown += f"## Objective\n\n{objective}\n\n"
        
        if constraints:
            markdown += "## Constraints\n\n"
            markdown += '\n'.join(f"- {constraint}" for constraint in constraints) + '\n\n'
        
        markdown += "## Memory Insights\n\n"
        for keyword, cluster in clusters.items():
            markdown += f"### {keyword.capitalize()}\n\n"
            markdown += '\n'.join(f"- {memory}" for memory in cluster) + '\n\n'
        
        markdown += "## Key Themes\n\n"
        markdown += '\n'.join(f"- {keyword.capitalize()}" for keyword in clusters.keys()) + '\n\n'
        
        markdown += "## Risks and Unknowns\n\n"
        markdown += "TBD\n\n"
        
        markdown += "## Assumptions\n\n"
        markdown += "TBD\n\n"
        
        markdown += "## Planning Approach\n\n"
        markdown += "TBD\n\n"
        
        markdown += "## Implementation Plan\n\n"
        markdown += "TBD\n\n"
        
        markdown += "## Deliverables\n\n"
        markdown += "TBD\n\n"
        
        markdown += "## Success Metrics\n\n"
        markdown += "TBD\n\n"
        
        markdown += "## Appendix\n\n"
        markdown += '\n'.join(f"- {memory}" for memory in memories) + '\n\n'
        
        return markdown

    def _save_markdown(self, content: str, objective: str, output_dir: str) -> pathlib.Path:
        sanitized_objective = re.sub(r'\W+', '-', objective.lower()).strip('-')
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{sanitized_objective}-{timestamp}.md"
        
        output_path = pathlib.Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        file_path = output_path / filename
        file_path.write_text(content, encoding='utf-8')
        
        return file_path

# Unit Tests
import unittest
from unittest.mock import patch


class TestDeepThinkingTool(unittest.TestCase):
    def setUp(self):
        self.tool = DeepThinkingTool()
        self.objective = "Improve team collaboration"
        self.memories = [
            "Team meetings are often unproductive.",
            "There is a lack of clear communication.",
            "Team members are not using the project management tool effectively."
        ]
        self.constraints = ["Must be implemented within 3 months", "Budget is limited to $10,000"]
        self.output_dir = "test_plans"
        self.return_content = True

    @patch('pathlib.Path.write_text')
    def test_run_with_valid_inputs(self, mock_write_text):
        result = self.tool.run(self.objective, self.memories, self.constraints, self.output_dir, self.return_content)
        result_dict = json.loads(result)
        self.assertIn("path", result_dict)
        self.assertIn("content", result_dict)
        self.assertTrue(result_dict["path"].startswith(self.output_dir))
        self.assertIn("# Deep Thinking Plan for Improve team collaboration", result_dict["content"])

    def test_run_with_empty_memories(self):
        result = self.tool.run(self.objective, [], self.constraints, self.output_dir, self.return_content)
        result_dict = json.loads(result)
        self.assertIn("path", result_dict)
        self.assertIn("content", result_dict)
        self.assertIn("## Memory Insights", result_dict["content"])

    def test_run_with_no_constraints(self):
        result = self.tool.run(self.objective, self.memories, None, self.output_dir, self.return_content)
        result_dict = json.loads(result)
        self.assertIn("path", result_dict)
        self.assertIn("content", result_dict)
        self.assertNotIn("## Constraints", result_dict["content"])

    def test_run_with_string_memory(self):
        result = self.tool.run(self.objective, "Team meetings are often unproductive.", self.constraints, self.output_dir, self.return_content)
        result_dict = json.loads(result)
        self.assertIn("path", result_dict)
        self.assertIn("content", result_dict)
        self.assertIn("## Memory Insights", result_dict["content"])

    def test_run_with_dict_memory(self):
        memories = [{"content": "Team meetings are often unproductive."}]
        result = self.tool.run(self.objective, memories, self.constraints, self.output_dir, self.return_content)
        result_dict = json.loads(result)
        self.assertIn("path", result_dict)
        self.assertIn("content", result_dict)
        self.assertIn("## Memory Insights", result_dict["content"])

if __name__ == "__main__":
    unittest.main()
