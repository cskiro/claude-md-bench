"""Tests for the CLAUDE.md analyzer module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from claude_md_bench.core.analyzer import AnalysisResult, ClaudeMDAnalyzer


class TestAnalysisResult:
    """Tests for AnalysisResult dataclass."""

    def test_create_analysis_result(self) -> None:
        """Should create analysis result with default values."""
        result = AnalysisResult(score=85.0, file_size=1500)

        assert result.score == 85.0
        assert result.file_size == 1500
        assert result.dimension_scores == {}
        assert result.strengths == []
        assert result.weaknesses == []
        assert result.recommendations == []
        assert result.detailed_analysis == ""
        assert result.error is None

    def test_create_analysis_result_with_error(self) -> None:
        """Should create analysis result with error."""
        result = AnalysisResult(
            score=0.0,
            file_size=0,
            error="File not found",
        )

        assert result.score == 0.0
        assert result.error == "File not found"


class TestClaudeMDAnalyzer:
    """Tests for ClaudeMDAnalyzer class."""

    def test_analyze_returns_result(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should return AnalysisResult when analyzing a file."""
        analyzer = ClaudeMDAnalyzer(mock_ollama_client)

        result = analyzer.analyze(sample_claude_md_file, "Test Project")

        assert isinstance(result, AnalysisResult)
        assert result.score > 0
        assert result.file_size > 0
        assert result.error is None

    def test_analyze_extracts_dimension_scores(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should extract dimension scores from LLM response."""
        analyzer = ClaudeMDAnalyzer(mock_ollama_client)

        result = analyzer.analyze(sample_claude_md_file, "Test Project")

        assert "clarity" in result.dimension_scores
        assert "completeness" in result.dimension_scores
        assert "actionability" in result.dimension_scores
        assert "standards" in result.dimension_scores
        assert "context" in result.dimension_scores

    def test_analyze_extracts_strengths_and_weaknesses(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should extract strengths and weaknesses from LLM response."""
        analyzer = ClaudeMDAnalyzer(mock_ollama_client)

        result = analyzer.analyze(sample_claude_md_file, "Test Project")

        assert len(result.strengths) > 0
        assert len(result.weaknesses) > 0
        assert len(result.recommendations) > 0

    def test_analyze_handles_missing_file(
        self,
        mock_ollama_client: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Should return error result when file doesn't exist."""
        analyzer = ClaudeMDAnalyzer(mock_ollama_client)
        missing_file = tmp_path / "nonexistent.md"

        result = analyzer.analyze(missing_file, "Test Project")

        assert result.score == 0.0
        assert result.error is not None
        assert "not found" in result.error.lower()

    def test_compare_returns_comparison_result(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
        minimal_claude_md_file: Path,
    ) -> None:
        """Should return ComparisonResult when comparing two files."""
        analyzer = ClaudeMDAnalyzer(mock_ollama_client)

        result = analyzer.compare(
            sample_claude_md_file,
            minimal_claude_md_file,
            "Project A",
            "Project B",
        )

        assert result.version_a["name"] == "Project A"
        assert result.version_b["name"] == "Project B"
        assert result.winner in ["A", "B", "TIE"]
        assert result.score_delta >= 0

    def test_compare_determines_winner_correctly(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
        minimal_claude_md_file: Path,
    ) -> None:
        """Should correctly determine winner based on scores."""
        # Mock different scores for A and B
        responses = [
            # First call (A) - higher score
            """CLARITY: 90
COMPLETENESS: 85
ACTIONABILITY: 88
STANDARDS: 92
CONTEXT: 80
OVERALL: 87

STRENGTHS:
- Excellent clarity
- Strong standards

WEAKNESSES:
- Minor gaps

RECOMMENDATIONS:
- Small improvements

DETAILED_ANALYSIS:
High quality file.
""",
            # Second call (B) - lower score
            """CLARITY: 60
COMPLETENESS: 55
ACTIONABILITY: 65
STANDARDS: 70
CONTEXT: 50
OVERALL: 60

STRENGTHS:
- Concise

WEAKNESSES:
- Too brief
- Missing content

RECOMMENDATIONS:
- Add more detail

DETAILED_ANALYSIS:
Needs more content.
""",
        ]
        mock_ollama_client.generate.side_effect = responses

        analyzer = ClaudeMDAnalyzer(mock_ollama_client)
        result = analyzer.compare(
            sample_claude_md_file,
            minimal_claude_md_file,
        )

        assert result.winner == "A"
        assert result.score_delta > 0


class TestParseAnalysis:
    """Tests for the _parse_analysis method."""

    def test_parse_handles_alternative_formats(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should parse scores in alternative formats."""
        # Mock response with markdown formatting
        mock_ollama_client.generate.return_value = """**CLARITY: 85**
**COMPLETENESS: 70**
**ACTIONABILITY: 80**
**STANDARDS: 90**
**CONTEXT: 75**
**OVERALL: 80**

STRENGTHS:
- Good structure

WEAKNESSES:
- Needs more detail

RECOMMENDATIONS:
- Expand sections

DETAILED_ANALYSIS:
Analysis text here.
"""

        analyzer = ClaudeMDAnalyzer(mock_ollama_client)
        result = analyzer.analyze(sample_claude_md_file, "Test")

        assert result.dimension_scores.get("clarity") == 85.0
        assert result.dimension_scores.get("completeness") == 70.0

    def test_parse_calculates_overall_when_missing(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should calculate overall score if not provided."""
        # Mock response without OVERALL
        mock_ollama_client.generate.return_value = """CLARITY: 80
COMPLETENESS: 80
ACTIONABILITY: 80
STANDARDS: 80
CONTEXT: 80

STRENGTHS:
- Consistent

WEAKNESSES:
- Average

RECOMMENDATIONS:
- Improve

DETAILED_ANALYSIS:
Average file.
"""

        analyzer = ClaudeMDAnalyzer(mock_ollama_client)
        result = analyzer.analyze(sample_claude_md_file, "Test")

        # Should calculate average of dimension scores
        assert result.score == 80.0

    def test_parse_limits_bullets_to_five(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should limit extracted bullets to 5 items."""
        mock_ollama_client.generate.return_value = """CLARITY: 80
COMPLETENESS: 80
ACTIONABILITY: 80
STANDARDS: 80
CONTEXT: 80
OVERALL: 80

STRENGTHS:
- One
- Two
- Three
- Four
- Five
- Six
- Seven

WEAKNESSES:
- A
- B
- C

RECOMMENDATIONS:
- X

DETAILED_ANALYSIS:
Test.
"""

        analyzer = ClaudeMDAnalyzer(mock_ollama_client)
        result = analyzer.analyze(sample_claude_md_file, "Test")

        assert len(result.strengths) <= 5
