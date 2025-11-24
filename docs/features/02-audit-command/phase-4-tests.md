# Phase 4: Tests

**Issue**: [#4](https://github.com/cskiro/claude-md-bench/issues/4)

## Goal

Achieve 80% test coverage on new audit command code following Testing Trophy approach.

## Tasks

- [ ] Create `tests/test_audit.py`
- [ ] Test CLI command invocation
- [ ] Test error handling scenarios
- [ ] Test all output formats
- [ ] Test reporter audit methods
- [ ] Verify coverage >= 80%

## Implementation Details

### Test File Structure

```python
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from claude_md_bench.cli import app
from claude_md_bench.core.analyzer import AnalysisResult
from claude_md_bench.core.reporter import Reporter

runner = CliRunner()


class TestAuditCommand:
    """Tests for the audit command."""

    @patch("claude_md_bench.commands.audit.OllamaClient")
    @patch("claude_md_bench.commands.audit.ClaudeMDAnalyzer")
    def test_audit_successful(
        self,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should complete audit and show results."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.analyze.return_value = AnalysisResult(
            score=7.5,
            file_size=1000,
            dimension_scores={"Clarity": 8.0, "Completeness": 7.0},
            strengths=["Well organized"],
            weaknesses=["Missing examples"],
            recommendations=["Add code examples"],
        )
        mock_analyzer_class.return_value = mock_analyzer

        result = runner.invoke(app, ["audit", str(sample_claude_md_file)])

        assert result.exit_code == 0
        assert "7.5" in result.stdout

    def test_audit_file_not_found(self) -> None:
        """Should show error for missing file."""
        result = runner.invoke(app, ["audit", "nonexistent.md"])

        assert result.exit_code != 0
        assert "not found" in result.stdout.lower() or "does not exist" in result.stdout.lower()

    @patch("claude_md_bench.commands.audit.OllamaClient")
    def test_audit_ollama_connection_error(
        self,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should handle Ollama connection failure."""
        from claude_md_bench.llm.ollama import OllamaConnectionError

        mock_client = MagicMock()
        mock_client.check_health.side_effect = OllamaConnectionError("Connection refused")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["audit", str(sample_claude_md_file)])

        assert result.exit_code != 0
        assert "ollama" in result.stdout.lower()

    @patch("claude_md_bench.commands.audit.OllamaClient")
    @patch("claude_md_bench.commands.audit.ClaudeMDAnalyzer")
    def test_audit_quiet_mode(
        self,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should suppress console output in quiet mode."""
        # Setup mocks (similar to successful test)
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.analyze.return_value = AnalysisResult(
            score=7.5, file_size=1000
        )
        mock_analyzer_class.return_value = mock_analyzer

        result = runner.invoke(app, ["audit", str(sample_claude_md_file), "--quiet"])

        assert result.exit_code == 0
        # Minimal or no output in quiet mode


class TestReporterAuditMethods:
    """Tests for Reporter audit methods."""

    def test_print_audit(self, mock_analysis_result: AnalysisResult) -> None:
        """Should print formatted audit results."""
        reporter = Reporter()
        # Test that print_audit doesn't raise
        reporter.print_audit(mock_analysis_result, Path("test.md"))

    def test_save_audit_text_report(
        self,
        mock_analysis_result: AnalysisResult,
        tmp_path: Path,
    ) -> None:
        """Should save text report to file."""
        reporter = Reporter(output_dir=tmp_path)
        report_path = reporter.save_audit_text_report(
            mock_analysis_result, Path("test.md")
        )

        assert report_path.exists()
        assert report_path.suffix == ".txt"
        content = report_path.read_text()
        assert "7.5" in content  # Score should be in report

    def test_save_audit_html_report(
        self,
        mock_analysis_result: AnalysisResult,
        tmp_path: Path,
    ) -> None:
        """Should save HTML report to file."""
        reporter = Reporter(output_dir=tmp_path)
        report_path = reporter.save_audit_html_report(
            mock_analysis_result, Path("test.md")
        )

        assert report_path is not None
        assert report_path.exists()
        assert report_path.suffix == ".html"
```

### Fixtures to Add (conftest.py)

```python
@pytest.fixture
def mock_analysis_result() -> AnalysisResult:
    """Create a mock AnalysisResult for testing."""
    return AnalysisResult(
        score=7.5,
        file_size=1000,
        dimension_scores={
            "Clarity": 8.0,
            "Completeness": 7.0,
            "Actionability": 7.5,
            "Standards": 8.0,
            "Context": 7.0,
        },
        strengths=["Well organized", "Clear commands"],
        weaknesses=["Missing examples", "No architecture diagram"],
        recommendations=["Add code examples", "Include system diagram"],
        detailed_analysis="This CLAUDE.md file provides good coverage...",
    )
```

## Acceptance Criteria

- [ ] All tests pass
- [ ] Coverage on `commands/audit.py` >= 80%
- [ ] Coverage on reporter audit methods >= 80%
- [ ] Tests follow existing patterns (class grouping, mock setup)
- [ ] No flaky tests

## Coverage Command

```bash
pytest tests/test_audit.py --cov=claude_md_bench.commands.audit --cov=claude_md_bench.core.reporter --cov-report=term-missing
```

## Notes

- Use existing fixtures from conftest.py where possible
- Mock LLM calls to avoid external dependency
- Test both success and error paths
