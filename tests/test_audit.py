"""Tests for the audit command and related functionality."""

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

    def test_audit_file_not_found_shows_error(self, tmp_path: Path) -> None:
        """Should show error for missing file."""
        result = runner.invoke(
            app,
            ["audit", str(tmp_path / "nonexistent.md")],
        )

        # Typer validates file existence before running command
        assert result.exit_code != 0

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
            score=75.0,
            file_size=1000,
            dimension_scores={
                "clarity": 80.0,
                "completeness": 70.0,
                "actionability": 75.0,
                "standards": 80.0,
                "context": 70.0,
            },
            strengths=["Well organized"],
            weaknesses=["Missing examples"],
            recommendations=["Add code examples"],
        )
        mock_analyzer_class.return_value = mock_analyzer

        result = runner.invoke(app, ["audit", str(sample_claude_md_file)])

        assert result.exit_code == 0
        assert "75.0" in result.stdout
        assert "Reports saved" in result.stdout

    @patch("claude_md_bench.commands.audit.OllamaClient")
    def test_audit_ollama_not_running(
        self,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should show error when Ollama is not running."""
        mock_client = MagicMock()
        mock_client.check_health.return_value = False
        mock_client.list_models.return_value = []
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["audit", str(sample_claude_md_file)])

        assert result.exit_code == 1
        assert "Cannot connect to Ollama" in result.stdout

    @patch("claude_md_bench.commands.audit.OllamaClient")
    def test_audit_ollama_connection_error(
        self,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should handle Ollama connection error gracefully."""
        from claude_md_bench.llm.ollama import OllamaConnectionError

        mock_client = MagicMock()
        mock_client.check_health.side_effect = OllamaConnectionError("Connection refused")
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["audit", str(sample_claude_md_file)])

        assert result.exit_code == 1
        assert "Connection error" in result.stdout

    @patch("claude_md_bench.commands.audit.OllamaClient")
    @patch("claude_md_bench.commands.audit.ClaudeMDAnalyzer")
    def test_audit_quiet_mode(
        self,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should suppress console output in quiet mode."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.analyze.return_value = AnalysisResult(
            score=75.0,
            file_size=1000,
        )
        mock_analyzer_class.return_value = mock_analyzer

        result = runner.invoke(
            app,
            ["audit", str(sample_claude_md_file), "--quiet"],
        )

        assert result.exit_code == 0
        # In quiet mode, should only show report locations
        assert "Reports saved" in result.stdout
        # Should not show the audit panel
        assert "Dimension Scores" not in result.stdout

    @patch("claude_md_bench.commands.audit.OllamaClient")
    @patch("claude_md_bench.commands.audit.ClaudeMDAnalyzer")
    def test_audit_text_format_only(
        self,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
        tmp_path: Path,
    ) -> None:
        """Should save only text report when format is text."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.analyze.return_value = AnalysisResult(
            score=75.0,
            file_size=1000,
        )
        mock_analyzer_class.return_value = mock_analyzer

        result = runner.invoke(
            app,
            [
                "audit",
                str(sample_claude_md_file),
                "--format",
                "text",
                "--output-dir",
                str(tmp_path),
                "--quiet",
            ],
        )

        assert result.exit_code == 0
        # Check that text report was saved
        text_files = list(tmp_path.glob("audit_*.txt"))
        assert len(text_files) == 1
        # Check that HTML report was not saved
        html_files = list(tmp_path.glob("audit_*.html"))
        assert len(html_files) == 0

    @patch("claude_md_bench.commands.audit.OllamaClient")
    @patch("claude_md_bench.commands.audit.ClaudeMDAnalyzer")
    def test_audit_html_format_only(
        self,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
        tmp_path: Path,
    ) -> None:
        """Should save only HTML report when format is html."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.analyze.return_value = AnalysisResult(
            score=75.0,
            file_size=1000,
        )
        mock_analyzer_class.return_value = mock_analyzer

        result = runner.invoke(
            app,
            [
                "audit",
                str(sample_claude_md_file),
                "--format",
                "html",
                "--output-dir",
                str(tmp_path),
                "--quiet",
            ],
        )

        assert result.exit_code == 0
        # Check that HTML report was saved
        html_files = list(tmp_path.glob("audit_*.html"))
        assert len(html_files) == 1
        # Check that text report was not saved
        text_files = list(tmp_path.glob("audit_*.txt"))
        assert len(text_files) == 0

    @patch("claude_md_bench.commands.audit.OllamaClient")
    @patch("claude_md_bench.commands.audit.ClaudeMDAnalyzer")
    def test_audit_analysis_error(
        self,
        mock_analyzer_class: MagicMock,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
    ) -> None:
        """Should show error when analysis fails."""
        # Setup mocks
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client_class.return_value = mock_client

        mock_analyzer = MagicMock()
        mock_analyzer.analyze.return_value = AnalysisResult(
            score=0.0,
            file_size=0,
            error="Analysis failed: invalid response",
        )
        mock_analyzer_class.return_value = mock_analyzer

        result = runner.invoke(app, ["audit", str(sample_claude_md_file)])

        assert result.exit_code == 1
        assert "Error analyzing" in result.stdout

    def test_audit_help_shows_usage(self) -> None:
        """Should show help text with --help."""
        result = runner.invoke(app, ["audit", "--help"])

        assert result.exit_code == 0
        assert "Audit a single CLAUDE.md file" in result.stdout
        assert "--model" in result.stdout
        assert "--format" in result.stdout


class TestReporterAuditMethods:
    """Tests for Reporter audit methods."""

    def test_print_audit_displays_results(
        self,
        mock_analysis_result: AnalysisResult,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Should print formatted audit results without error."""
        reporter = Reporter(output_dir=tmp_path)
        file_path = tmp_path / "test.md"
        file_path.write_text("# Test")

        # Should not raise any exceptions
        reporter.print_audit(mock_analysis_result, file_path)

    def test_save_audit_text_report_creates_file(
        self,
        mock_analysis_result: AnalysisResult,
        tmp_path: Path,
    ) -> None:
        """Should save text report to file."""
        reporter = Reporter(output_dir=tmp_path)
        file_path = tmp_path / "test.md"
        file_path.write_text("# Test")

        report_path = reporter.save_audit_text_report(mock_analysis_result, file_path)

        assert report_path.exists()
        assert report_path.suffix == ".txt"
        assert "audit_test_" in report_path.name

        # Check content
        content = report_path.read_text()
        assert "CLAUDE.md Audit Report" in content
        assert "75.0" in content
        assert "Well organized" in content
        assert "Missing examples" in content

    def test_save_audit_html_report_creates_file(
        self,
        mock_analysis_result: AnalysisResult,
        tmp_path: Path,
    ) -> None:
        """Should save HTML report to file."""
        reporter = Reporter(output_dir=tmp_path)
        file_path = tmp_path / "test.md"
        file_path.write_text("# Test Content")

        report_path = reporter.save_audit_html_report(mock_analysis_result, file_path)

        assert report_path is not None
        assert report_path.exists()
        assert report_path.suffix == ".html"
        assert "audit_test_" in report_path.name

        # Check content
        content = report_path.read_text()
        assert "CLAUDE.md Audit" in content
        assert "75.0" in content

    def test_save_audit_text_report_includes_all_sections(
        self,
        mock_analysis_result: AnalysisResult,
        tmp_path: Path,
    ) -> None:
        """Should include all analysis sections in text report."""
        reporter = Reporter(output_dir=tmp_path)
        file_path = tmp_path / "test.md"
        file_path.write_text("# Test")

        report_path = reporter.save_audit_text_report(mock_analysis_result, file_path)
        content = report_path.read_text()

        # Check all sections are present
        assert "Dimension Scores" in content
        assert "Strengths" in content
        assert "Weaknesses" in content
        assert "Recommendations" in content
        assert "Detailed Analysis" in content

        # Check dimension scores
        assert "Clarity" in content
        assert "Completeness" in content
        assert "Actionability" in content
        assert "Standards" in content
        assert "Context" in content

    def test_save_audit_text_report_with_empty_lists(
        self,
        tmp_path: Path,
    ) -> None:
        """Should handle empty strengths/weaknesses/recommendations."""
        reporter = Reporter(output_dir=tmp_path)
        file_path = tmp_path / "test.md"
        file_path.write_text("# Test")

        result = AnalysisResult(
            score=50.0,
            file_size=100,
            dimension_scores={},
            strengths=[],
            weaknesses=[],
            recommendations=[],
        )

        report_path = reporter.save_audit_text_report(result, file_path)

        assert report_path.exists()
        content = report_path.read_text()
        assert "50.0" in content

    def test_save_audit_html_report_with_file_content(
        self,
        mock_analysis_result: AnalysisResult,
        tmp_path: Path,
    ) -> None:
        """Should include file content in HTML report."""
        reporter = Reporter(output_dir=tmp_path)
        file_path = tmp_path / "test.md"
        test_content = "# Test CLAUDE.md\n\nThis is test content."
        file_path.write_text(test_content)

        report_path = reporter.save_audit_html_report(mock_analysis_result, file_path)

        assert report_path is not None
        html_content = report_path.read_text()
        assert "View CLAUDE.md Content" in html_content
        assert test_content in html_content

    def test_reporter_creates_output_directory(self, tmp_path: Path) -> None:
        """Should create output directory if it doesn't exist."""
        new_dir = tmp_path / "new_reports"
        assert not new_dir.exists()

        reporter = Reporter(output_dir=new_dir)

        assert new_dir.exists()
        assert reporter.output_dir == new_dir
