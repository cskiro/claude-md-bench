"""
CLAUDE.md Analyzer

Analyzes CLAUDE.md files for quality and completeness using LLM evaluation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from claude_md_bench.llm.ollama import OllamaClient

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Result of analyzing a single CLAUDE.md file."""

    score: float
    file_size: int
    dimension_scores: dict[str, float] = field(default_factory=dict)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    detailed_analysis: str = ""
    error: str | None = None


@dataclass
class ComparisonResult:
    """Result of comparing two CLAUDE.md files."""

    version_a: dict[str, Any]
    version_b: dict[str, Any]
    winner: str  # "A", "B", or "TIE"
    score_delta: float


class ClaudeMDAnalyzer:
    """Analyzes and compares CLAUDE.md files for effectiveness."""

    DIMENSIONS = ["clarity", "completeness", "actionability", "standards", "context"]

    def __init__(self, ollama_client: OllamaClient) -> None:
        """
        Initialize analyzer.

        Args:
            ollama_client: Ollama client for LLM analysis
        """
        self.ollama = ollama_client

    def analyze(
        self,
        claude_md_path: Path,
        project_name: str = "Unknown",
    ) -> AnalysisResult:
        """
        Analyze a single CLAUDE.md file for quality and completeness.

        Args:
            claude_md_path: Path to CLAUDE.md file
            project_name: Name of project for context

        Returns:
            Analysis result with scores and recommendations
        """
        logger.info(f"Analyzing {claude_md_path}")

        # Read file
        try:
            content = claude_md_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return AnalysisResult(
                score=0.0,
                file_size=0,
                error=f"File not found: {claude_md_path}",
            )
        except Exception as e:
            logger.error(f"Cannot read {claude_md_path}: {e}")
            return AnalysisResult(
                score=0.0,
                file_size=0,
                error=str(e),
            )

        # Build analysis prompt
        prompt = self._build_analysis_prompt(content, project_name)

        # Get LLM analysis
        try:
            response = self.ollama.generate(
                prompt=prompt,
                system=self._get_system_prompt(),
                temperature=0.3,
            )

            logger.debug(f"Raw LLM response (first 500 chars):\n{response[:500]}")

            # Parse response
            result = self._parse_analysis(response, len(content))

            logger.info(f"Analysis complete: score={result.score:.1f}/100")
            logger.debug(f"Dimension scores: {result.dimension_scores}")

            return result

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return AnalysisResult(
                score=0.0,
                file_size=len(content),
                error=str(e),
            )

    def compare(
        self,
        claude_md_a: Path,
        claude_md_b: Path,
        project_name_a: str = "Version A",
        project_name_b: str = "Version B",
    ) -> ComparisonResult:
        """
        Compare two CLAUDE.md files.

        Args:
            claude_md_a: Path to first CLAUDE.md
            claude_md_b: Path to second CLAUDE.md
            project_name_a: Name for first version
            project_name_b: Name for second version

        Returns:
            Comparison result with winner and detailed analysis
        """
        logger.info("\nComparing:")
        logger.info(f"  A: {claude_md_a}")
        logger.info(f"  B: {claude_md_b}")

        # Analyze both
        analysis_a = self.analyze(claude_md_a, project_name_a)
        analysis_b = self.analyze(claude_md_b, project_name_b)

        # Determine winner
        score_a = analysis_a.score
        score_b = analysis_b.score

        if score_a > score_b:
            winner = "A"
            delta = score_a - score_b
        elif score_b > score_a:
            winner = "B"
            delta = score_b - score_a
        else:
            winner = "TIE"
            delta = 0.0

        return ComparisonResult(
            version_a={
                "name": project_name_a,
                "path": str(claude_md_a),
                "analysis": self._result_to_dict(analysis_a),
            },
            version_b={
                "name": project_name_b,
                "path": str(claude_md_b),
                "analysis": self._result_to_dict(analysis_b),
            },
            winner=winner,
            score_delta=delta,
        )

    def _result_to_dict(self, result: AnalysisResult) -> dict[str, Any]:
        """Convert AnalysisResult to dictionary."""
        return {
            "score": result.score,
            "file_size": result.file_size,
            "dimension_scores": result.dimension_scores,
            "strengths": result.strengths,
            "weaknesses": result.weaknesses,
            "recommendations": result.recommendations,
            "detailed_analysis": result.detailed_analysis,
            "error": result.error,
        }

    def _get_system_prompt(self) -> str:
        """Get system prompt for analysis."""
        return """You are an expert at evaluating CLAUDE.md files for AI coding assistants.

A good CLAUDE.md file should:
1. **Be Clear & Specific**: Explicit commands, patterns, and examples
2. **Cover Key Areas**: Testing, quality checks, architecture, common pitfalls
3. **Be Actionable**: Concrete instructions, not vague guidelines
4. **Include Standards**: TDD workflow, type safety, code quality requirements
5. **Provide Context**: Project structure, common commands, troubleshooting

Evaluate files on these dimensions and provide constructive feedback."""

    def _build_analysis_prompt(self, content: str, project_name: str) -> str:
        """Build analysis prompt."""
        char_count = len(content)
        line_count = len(content.split("\n"))

        # Limit content to avoid context window issues
        max_content_chars = 4000
        truncated_content = content[:max_content_chars]
        if len(content) > max_content_chars:
            truncated_content += (
                f"\n\n[... truncated, {char_count - max_content_chars} more chars ...]"
            )

        return f"""# CLAUDE.md File Analysis

## Project Context
**Project**: {project_name}
**File Size**: {char_count} characters, {line_count} lines

## File Content
```markdown
{truncated_content}
```

## Your Task

Analyze this CLAUDE.md file and provide scores (0-100) for:

1. **Clarity** (0-100): Are instructions clear and specific?
2. **Completeness** (0-100): Covers all essential areas?
3. **Actionability** (0-100): Provides concrete, executable guidance?
4. **Standards** (0-100): Enforces quality standards (TDD, types, testing)?
5. **Context** (0-100): Adequate project context and structure?

Then provide:
- **Overall Score** (0-100): Weighted average
- **Strengths**: What this file does well (3-5 points)
- **Weaknesses**: What could be improved (3-5 points)
- **Recommendations**: Specific improvements (3-5 points)

Format your response as:

CLARITY: <score 0-100>
COMPLETENESS: <score 0-100>
ACTIONABILITY: <score 0-100>
STANDARDS: <score 0-100>
CONTEXT: <score 0-100>
OVERALL: <score 0-100>

STRENGTHS:
- <strength 1>
- <strength 2>
- <strength 3>

WEAKNESSES:
- <weakness 1>
- <weakness 2>
- <weakness 3>

RECOMMENDATIONS:
- <recommendation 1>
- <recommendation 2>
- <recommendation 3>

DETAILED_ANALYSIS:
<Your detailed analysis here>
"""

    def _parse_analysis(self, response: str, file_size: int) -> AnalysisResult:
        """Parse LLM analysis response."""
        scores: dict[str, float] = {}
        strengths: list[str] = []
        weaknesses: list[str] = []
        recommendations: list[str] = []
        detailed_analysis = ""

        # Extract scores - handle multiple formats
        for line in response.split("\n"):
            for metric in [
                "CLARITY",
                "COMPLETENESS",
                "ACTIONABILITY",
                "STANDARDS",
                "CONTEXT",
                "OVERALL",
            ]:
                line_upper = line.upper()
                if metric in line_upper:
                    try:
                        # Remove markdown formatting
                        clean_line = line.replace("**", "").replace("###", "").strip()

                        # Try format: "CLARITY: 90"
                        if ":" in clean_line:
                            score_part = clean_line.split(":")[-1].strip()
                            score_str = score_part.split()[0]  # Get first number
                            scores[metric.lower()] = float(score_str)
                        # Try format: "Clarity (90/100)"
                        elif "(" in clean_line and "/" in clean_line:
                            score_part = clean_line.split("(")[1].split("/")[0]
                            scores[metric.lower()] = float(score_part)
                    except (ValueError, IndexError):
                        pass

        # Extract bullet lists
        strengths = self._extract_bullets(response, "STRENGTHS")
        weaknesses = self._extract_bullets(response, "WEAKNESSES")
        recommendations = self._extract_bullets(response, "RECOMMENDATIONS")

        # Extract detailed analysis
        if "DETAILED_ANALYSIS:" in response:
            parts = response.split("DETAILED_ANALYSIS:")
            if len(parts) > 1:
                detailed_analysis = parts[1].strip()

        # Calculate overall score if not provided
        overall_score = scores.get("overall", 0.0)
        if overall_score == 0.0 and scores:
            # Calculate average of dimension scores
            dimension_sum = 0.0
            dimension_count = 0
            for key, value in scores.items():
                if key != "overall":
                    dimension_sum += value
                    dimension_count += 1
            if dimension_count > 0:
                overall_score = dimension_sum / dimension_count

        return AnalysisResult(
            score=overall_score,
            file_size=file_size,
            dimension_scores=scores,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations,
            detailed_analysis=detailed_analysis or response[:1000],
        )

    def _extract_bullets(self, text: str, section: str) -> list[str]:
        """Extract bullet list from section."""
        items: list[str] = []
        in_section = False

        for line in text.split("\n"):
            if f"{section}:" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith("-"):
                items.append(line.strip("- ").strip())
            elif in_section and line.strip() and not line.strip().startswith("-"):
                break

        return items[:5]  # Limit to 5
