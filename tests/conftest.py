"""Pytest configuration and fixtures for claude-md-bench tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from claude_md_bench.core.analyzer import AnalysisResult
from claude_md_bench.llm.ollama import OllamaClient


@pytest.fixture
def sample_claude_md_content() -> str:
    """Return sample CLAUDE.md content for testing."""
    return """# CLAUDE.md

## Project Overview
This is a test project for validating CLAUDE.md analysis.

## Build Commands
```bash
npm run build
npm run test
```

## Code Standards
- Use TypeScript strict mode
- 80% test coverage required
- No console.log statements

## Testing
- Follow TDD approach
- Use Testing Trophy distribution
"""


@pytest.fixture
def sample_claude_md_file(tmp_path: Path, sample_claude_md_content: str) -> Path:
    """Create a sample CLAUDE.md file for testing."""
    file_path = tmp_path / "CLAUDE.md"
    file_path.write_text(sample_claude_md_content)
    return file_path


@pytest.fixture
def minimal_claude_md_file(tmp_path: Path) -> Path:
    """Create a minimal CLAUDE.md file for testing."""
    file_path = tmp_path / "CLAUDE_minimal.md"
    file_path.write_text("# CLAUDE.md\n\nBasic instructions.")
    return file_path


@pytest.fixture
def mock_ollama_response() -> str:
    """Return a mock LLM analysis response."""
    return """CLARITY: 85
COMPLETENESS: 70
ACTIONABILITY: 80
STANDARDS: 90
CONTEXT: 75
OVERALL: 80

STRENGTHS:
- Clear build commands
- Good testing standards
- TypeScript strict mode enforced

WEAKNESSES:
- Missing architecture documentation
- No troubleshooting section
- Limited context about project structure

RECOMMENDATIONS:
- Add architecture overview
- Include common pitfalls section
- Document debugging procedures

DETAILED_ANALYSIS:
This CLAUDE.md provides good foundational guidance for code quality and testing.
The build commands are clear and the standards section enforces important practices.
However, it lacks depth in architecture documentation and troubleshooting guidance.
"""


@pytest.fixture
def mock_ollama_client(mock_ollama_response: str) -> OllamaClient:
    """Create a mocked OllamaClient for testing without actual API calls."""
    client = MagicMock(spec=OllamaClient)
    client.generate.return_value = mock_ollama_response
    client.check_health.return_value = True
    client.list_models.return_value = ["llama3.2:latest", "qwen2.5:32b"]
    return client


@pytest.fixture
def mock_comparison_result() -> dict[str, Any]:
    """Return a mock comparison result for testing reporters."""
    return {
        "version_a": {
            "name": "Project A",
            "path": "/path/to/project-a/CLAUDE.md",
            "analysis": {
                "score": 85.0,
                "file_size": 1500,
                "dimension_scores": {
                    "clarity": 85.0,
                    "completeness": 80.0,
                    "actionability": 90.0,
                    "standards": 85.0,
                    "context": 75.0,
                },
                "strengths": ["Clear instructions", "Good standards"],
                "weaknesses": ["Missing architecture", "No examples"],
                "recommendations": ["Add examples", "Document architecture"],
                "detailed_analysis": "Version A analysis...",
                "error": None,
            },
        },
        "version_b": {
            "name": "Project B",
            "path": "/path/to/project-b/CLAUDE.md",
            "analysis": {
                "score": 72.0,
                "file_size": 800,
                "dimension_scores": {
                    "clarity": 70.0,
                    "completeness": 65.0,
                    "actionability": 75.0,
                    "standards": 80.0,
                    "context": 70.0,
                },
                "strengths": ["Concise", "Easy to read"],
                "weaknesses": ["Too brief", "Missing commands"],
                "recommendations": ["Expand content", "Add commands"],
                "detailed_analysis": "Version B analysis...",
                "error": None,
            },
        },
        "winner": "A",
        "score_delta": 13.0,
    }


@pytest.fixture
def mock_analysis_result() -> AnalysisResult:
    """Create a mock AnalysisResult for testing audit functionality."""
    return AnalysisResult(
        score=75.0,
        file_size=1000,
        dimension_scores={
            "clarity": 80.0,
            "completeness": 70.0,
            "actionability": 75.0,
            "standards": 80.0,
            "context": 70.0,
        },
        strengths=["Well organized", "Clear commands", "Good standards"],
        weaknesses=["Missing examples", "No architecture diagram", "Limited context"],
        recommendations=["Add code examples", "Include system diagram", "Expand troubleshooting"],
        detailed_analysis="This CLAUDE.md file provides good coverage of basic requirements...",
    )
