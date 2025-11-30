"""Tests for the CLAUDE.md optimizer module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from claude_md_bench.core.analyzer import AnalysisResult
from claude_md_bench.core.optimizer import (
    ClaudeMDOptimizer,
    MetaPrompter,
    OptimizationIteration,
    OptimizationResult,
)


class TestOptimizationDataclasses:
    """Tests for optimization dataclasses."""

    def test_create_optimization_iteration(self) -> None:
        """Should create optimization iteration with all fields."""
        analysis = AnalysisResult(score=85.0, file_size=1500)
        iteration = OptimizationIteration(
            iteration=1,
            score=85.0,
            previous_score=80.0,
            delta=5.0,
            content="# CLAUDE.md\n\nImproved content",
            analysis=analysis,
        )

        assert iteration.iteration == 1
        assert iteration.score == 85.0
        assert iteration.previous_score == 80.0
        assert iteration.delta == 5.0
        assert iteration.content == "# CLAUDE.md\n\nImproved content"
        assert iteration.analysis == analysis

    def test_create_optimization_result(self) -> None:
        """Should create optimization result with default values."""
        result = OptimizationResult(
            original_score=70.0,
            final_score=85.0,
            total_improvement=15.0,
        )

        assert result.original_score == 70.0
        assert result.final_score == 85.0
        assert result.total_improvement == 15.0
        assert result.iterations == []
        assert result.original_content == ""
        assert result.final_content == ""
        assert result.output_path is None


class TestMetaPrompter:
    """Tests for MetaPrompter class."""

    @pytest.fixture
    def mock_improved_response(self) -> str:
        """Return a mock improved CLAUDE.md response."""
        return """<<<BEGIN_CLAUDE_MD>>>
# CLAUDE.md

## Project Overview
This is an improved CLAUDE.md with better guidance.

## Build Commands
```bash
npm run build
npm run test
npm run lint
```

## Code Standards
- Use TypeScript strict mode
- 80% test coverage required
- No console.log statements
- Run quality checks after every change

## Testing
- Follow TDD approach: RED-GREEN-REFACTOR
- Use Testing Trophy distribution
- Write tests before implementation
<<<END_CLAUDE_MD>>>"""

    def test_improve_returns_content(
        self,
        mock_ollama_client: MagicMock,
        mock_improved_response: str,
    ) -> None:
        """Should return improved CLAUDE.md content."""
        mock_ollama_client.generate.return_value = mock_improved_response
        prompter = MetaPrompter(mock_ollama_client)

        analysis = AnalysisResult(
            score=70.0,
            file_size=500,
            dimension_scores={"clarity": 65.0, "completeness": 70.0},
            strengths=["Clear commands"],
            weaknesses=["Missing TDD details"],
            recommendations=["Add TDD workflow"],
        )

        result = prompter.improve(
            current_content="# CLAUDE.md\n\nBasic content",
            analysis=analysis,
            iteration=1,
        )

        assert "# CLAUDE.md" in result
        assert "Project Overview" in result
        assert "<<<BEGIN_CLAUDE_MD>>>" not in result
        assert "<<<END_CLAUDE_MD>>>" not in result

    def test_improve_calls_ollama_generate(
        self,
        mock_ollama_client: MagicMock,
        mock_improved_response: str,
    ) -> None:
        """Should call ollama generate with correct parameters."""
        mock_ollama_client.generate.return_value = mock_improved_response
        prompter = MetaPrompter(mock_ollama_client)

        analysis = AnalysisResult(score=70.0, file_size=500)

        prompter.improve(
            current_content="# CLAUDE.md\n\nContent",
            analysis=analysis,
            iteration=1,
        )

        mock_ollama_client.generate.assert_called_once()
        call_kwargs = mock_ollama_client.generate.call_args[1]
        assert "prompt" in call_kwargs
        assert "system" in call_kwargs
        assert call_kwargs["temperature"] == 0.5

    def test_extract_clean_claude_md_with_markers(
        self,
        mock_ollama_client: MagicMock,
    ) -> None:
        """Should extract content between markers."""
        prompter = MetaPrompter(mock_ollama_client)

        raw_output = """Here's the improved version:

<<<BEGIN_CLAUDE_MD>>>
# CLAUDE.md

## Content
Improved content here.
<<<END_CLAUDE_MD>>>

Hope this helps!"""

        result = prompter._extract_clean_claude_md(raw_output)

        assert result.startswith("# CLAUDE.md")
        assert "Improved content here" in result
        assert "Hope this helps" not in result

    def test_extract_clean_claude_md_without_markers(
        self,
        mock_ollama_client: MagicMock,
    ) -> None:
        """Should extract content using pattern matching when markers missing."""
        prompter = MetaPrompter(mock_ollama_client)

        raw_output = """I've improved the file:

# CLAUDE.md

## Project Overview
Better documentation here.

## Commands
Run the tests."""

        result = prompter._extract_clean_claude_md(raw_output)

        assert result.startswith("# CLAUDE.md")
        assert "Better documentation" in result
        assert "I've improved" not in result

    def test_extract_removes_meta_text_patterns(
        self,
        mock_ollama_client: MagicMock,
    ) -> None:
        """Should remove common meta-text patterns from output."""
        prompter = MetaPrompter(mock_ollama_client)

        raw_output = """# CLAUDE.md Improvement Task

## Current CLAUDE.md

# CLAUDE.md

## Real Content
This is the actual content."""

        result = prompter._extract_clean_claude_md(raw_output)

        assert "Real Content" in result
        assert "Improvement Task" not in result


class TestClaudeMDOptimizer:
    """Tests for ClaudeMDOptimizer class."""

    @pytest.fixture
    def mock_analysis_responses(self) -> list[str]:
        """Return mock analysis responses for optimization iterations."""
        return [
            # Initial analysis (baseline)
            """CLARITY: 70
COMPLETENESS: 65
ACTIONABILITY: 75
STANDARDS: 70
CONTEXT: 60
OVERALL: 68

STRENGTHS:
- Basic structure present
- Clear commands

WEAKNESSES:
- Missing TDD workflow
- Incomplete standards

RECOMMENDATIONS:
- Add TDD details
- Expand standards section

DETAILED_ANALYSIS:
Baseline analysis.""",
            # After iteration 1
            """CLARITY: 78
COMPLETENESS: 75
ACTIONABILITY: 80
STANDARDS: 82
CONTEXT: 70
OVERALL: 77

STRENGTHS:
- Improved structure
- Better TDD guidance

WEAKNESSES:
- Could add more examples

RECOMMENDATIONS:
- Add code examples

DETAILED_ANALYSIS:
Improved after iteration 1.""",
            # After iteration 2
            """CLARITY: 82
COMPLETENESS: 80
ACTIONABILITY: 85
STANDARDS: 88
CONTEXT: 78
OVERALL: 82

STRENGTHS:
- Excellent TDD workflow
- Clear examples

WEAKNESSES:
- Minor gaps remain

RECOMMENDATIONS:
- Polish documentation

DETAILED_ANALYSIS:
Further improved.""",
        ]

    @pytest.fixture
    def mock_improved_contents(self) -> list[str]:
        """Return mock improved CLAUDE.md contents."""
        return [
            """<<<BEGIN_CLAUDE_MD>>>
# CLAUDE.md

## Project Overview
Improved in iteration 1.

## TDD Workflow
Follow RED-GREEN-REFACTOR.
<<<END_CLAUDE_MD>>>""",
            """<<<BEGIN_CLAUDE_MD>>>
# CLAUDE.md

## Project Overview
Improved in iteration 2.

## TDD Workflow
Follow RED-GREEN-REFACTOR with examples.

## Examples
```python
def test_example():
    assert True
```
<<<END_CLAUDE_MD>>>""",
        ]

    def test_optimize_returns_result(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
        mock_analysis_responses: list[str],
        mock_improved_contents: list[str],
    ) -> None:
        """Should return OptimizationResult after optimization."""
        # Interleave analysis and improvement responses
        responses = [
            mock_analysis_responses[0],  # Baseline analysis
            mock_improved_contents[0],  # First improvement
            mock_analysis_responses[1],  # Analysis of improvement 1
            mock_improved_contents[1],  # Second improvement
            mock_analysis_responses[2],  # Analysis of improvement 2
        ]
        mock_ollama_client.generate.side_effect = responses

        optimizer = ClaudeMDOptimizer(mock_ollama_client)
        result = optimizer.optimize(
            claude_md_path=sample_claude_md_file,
            iterations=2,
        )

        assert isinstance(result, OptimizationResult)
        assert result.original_score > 0
        assert result.final_score > 0
        assert len(result.iterations) == 2
        assert result.output_path is not None

    def test_optimize_tracks_improvement(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
        mock_analysis_responses: list[str],
        mock_improved_contents: list[str],
    ) -> None:
        """Should track improvement across iterations."""
        responses = [
            mock_analysis_responses[0],
            mock_improved_contents[0],
            mock_analysis_responses[1],
            mock_improved_contents[1],
            mock_analysis_responses[2],
        ]
        mock_ollama_client.generate.side_effect = responses

        optimizer = ClaudeMDOptimizer(mock_ollama_client)
        result = optimizer.optimize(
            claude_md_path=sample_claude_md_file,
            iterations=2,
        )

        # Should show improvement
        assert result.final_score > result.original_score
        assert result.total_improvement > 0

        # Iterations should show progression
        assert result.iterations[0].score > result.original_score
        assert result.iterations[1].score > result.iterations[0].score

    def test_optimize_saves_output_file(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
        mock_analysis_responses: list[str],
        mock_improved_contents: list[str],
    ) -> None:
        """Should save optimized file to output path."""
        responses = [
            mock_analysis_responses[0],
            mock_improved_contents[0],
            mock_analysis_responses[1],
        ]
        mock_ollama_client.generate.side_effect = responses

        optimizer = ClaudeMDOptimizer(mock_ollama_client)
        result = optimizer.optimize(
            claude_md_path=sample_claude_md_file,
            iterations=1,
        )

        assert result.output_path is not None
        assert result.output_path.exists()
        content = result.output_path.read_text()
        assert "# CLAUDE.md" in content

    def test_optimize_uses_custom_output_path(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
        tmp_path: Path,
        mock_analysis_responses: list[str],
        mock_improved_contents: list[str],
    ) -> None:
        """Should use custom output path when provided."""
        responses = [
            mock_analysis_responses[0],
            mock_improved_contents[0],
            mock_analysis_responses[1],
        ]
        mock_ollama_client.generate.side_effect = responses

        custom_output = tmp_path / "custom_output.md"
        optimizer = ClaudeMDOptimizer(mock_ollama_client)
        result = optimizer.optimize(
            claude_md_path=sample_claude_md_file,
            iterations=1,
            output_path=custom_output,
        )

        assert result.output_path == custom_output
        assert custom_output.exists()

    def test_optimize_selects_best_iteration(
        self,
        mock_ollama_client: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should select the best scoring iteration as final result."""
        # Create responses where iteration 1 is better than iteration 2
        responses = [
            # Baseline - 60
            """CLARITY: 60\nCOMPLETENESS: 60\nACTIONABILITY: 60\nSTANDARDS: 60\nCONTEXT: 60\nOVERALL: 60\n\nSTRENGTHS:\n- Basic\n\nWEAKNESSES:\n- Minimal\n\nRECOMMENDATIONS:\n- Improve\n\nDETAILED_ANALYSIS:\nBaseline.""",
            # Improvement 1
            """<<<BEGIN_CLAUDE_MD>>>\n# CLAUDE.md\n\nIteration 1 - Best\n<<<END_CLAUDE_MD>>>""",
            # After iteration 1 - 85 (best)
            """CLARITY: 85\nCOMPLETENESS: 85\nACTIONABILITY: 85\nSTANDARDS: 85\nCONTEXT: 85\nOVERALL: 85\n\nSTRENGTHS:\n- Great\n\nWEAKNESSES:\n- None\n\nRECOMMENDATIONS:\n- Keep\n\nDETAILED_ANALYSIS:\nExcellent.""",
            # Improvement 2
            """<<<BEGIN_CLAUDE_MD>>>\n# CLAUDE.md\n\nIteration 2 - Worse\n<<<END_CLAUDE_MD>>>""",
            # After iteration 2 - 75 (worse than 1)
            """CLARITY: 75\nCOMPLETENESS: 75\nACTIONABILITY: 75\nSTANDARDS: 75\nCONTEXT: 75\nOVERALL: 75\n\nSTRENGTHS:\n- Good\n\nWEAKNESSES:\n- Regressed\n\nRECOMMENDATIONS:\n- Fix\n\nDETAILED_ANALYSIS:\nRegressed.""",
        ]
        mock_ollama_client.generate.side_effect = responses

        optimizer = ClaudeMDOptimizer(mock_ollama_client)
        result = optimizer.optimize(
            claude_md_path=sample_claude_md_file,
            iterations=2,
        )

        # Should select iteration 1 (score 85) over iteration 2 (score 75)
        assert result.final_score == 85.0
        assert "Iteration 1 - Best" in result.final_content


class TestOptimizeCommand:
    """Tests for the optimize CLI command."""

    def test_optimize_command_exists(self) -> None:
        """Should have optimize command registered."""
        from claude_md_bench.cli import app

        commands = list(app.registered_commands)
        command_names = [cmd.name or cmd.callback.__name__ for cmd in commands]

        assert "optimize" in command_names

    def test_optimize_command_requires_file(self) -> None:
        """Should require file argument."""
        from typer.testing import CliRunner

        from claude_md_bench.cli import app

        runner = CliRunner()
        result = runner.invoke(app, ["optimize"])

        assert result.exit_code != 0
        assert "Missing argument" in result.stdout or "FILE" in result.stdout

    @patch("claude_md_bench.commands.optimize.OllamaClient")
    def test_optimize_command_workflow(
        self,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should complete optimization workflow and save output file."""
        from typer.testing import CliRunner

        from claude_md_bench.cli import app

        # Setup mock responses for: baseline analysis, improvement, improved analysis
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client.generate.side_effect = [
            # Baseline analysis
            """CLARITY: 70\nCOMPLETENESS: 65\nACTIONABILITY: 75\nSTANDARDS: 70\nCONTEXT: 60\nOVERALL: 68\n\nSTRENGTHS:\n- Basic structure\n\nWEAKNESSES:\n- Missing details\n\nRECOMMENDATIONS:\n- Add more\n\nDETAILED_ANALYSIS:\nBaseline.""",
            # Improved content
            """<<<BEGIN_CLAUDE_MD>>>\n# CLAUDE.md\n\n## Improved\nBetter content.\n<<<END_CLAUDE_MD>>>""",
            # Improved analysis
            """CLARITY: 80\nCOMPLETENESS: 78\nACTIONABILITY: 82\nSTANDARDS: 85\nCONTEXT: 75\nOVERALL: 80\n\nSTRENGTHS:\n- Better structure\n\nWEAKNESSES:\n- Minor gaps\n\nRECOMMENDATIONS:\n- Polish\n\nDETAILED_ANALYSIS:\nImproved.""",
        ]
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["optimize", str(sample_claude_md_file), "--iterations", "1", "--quiet"],
        )

        # Test workflow completed successfully
        assert result.exit_code == 0

        # Test output file was created
        output_file = sample_claude_md_file.parent / "CLAUDE.optimized.md"
        assert output_file.exists()

        # Test output contains improved content
        content = output_file.read_text()
        assert "# CLAUDE.md" in content

    @patch("claude_md_bench.commands.optimize.OllamaClient")
    def test_optimize_command_ollama_not_running(
        self,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should show error when Ollama is not running."""
        from typer.testing import CliRunner

        from claude_md_bench.cli import app

        mock_client = MagicMock()
        mock_client.check_health.return_value = False
        mock_client.list_models.return_value = []
        mock_client_class.return_value = mock_client

        runner = CliRunner()
        result = runner.invoke(
            app,
            ["optimize", str(sample_claude_md_file)],
        )

        assert result.exit_code == 1
        assert "Cannot connect to Ollama" in result.stdout
