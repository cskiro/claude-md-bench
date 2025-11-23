"""Tests for the CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from claude_md_bench.cli import app


runner = CliRunner()


class TestVersionCommand:
    """Tests for the version command."""

    def test_version_shows_version_number(self) -> None:
        """Should display version information."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "claude-md-bench version" in result.stdout
        assert "0.1.0" in result.stdout


class TestCheckCommand:
    """Tests for the check command."""

    @patch("claude_md_bench.cli.OllamaClient")
    def test_check_success_with_models(self, mock_client_class: MagicMock) -> None:
        """Should show available models when Ollama is running."""
        mock_client = MagicMock()
        mock_client.list_models.return_value = ["llama3.2:latest", "qwen2.5:32b"]
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["check"])

        assert result.exit_code == 0
        assert "Ollama is running" in result.stdout
        assert "llama3.2:latest" in result.stdout

    @patch("claude_md_bench.cli.OllamaClient")
    def test_check_fails_when_ollama_not_running(
        self,
        mock_client_class: MagicMock,
    ) -> None:
        """Should show error when Ollama is not running."""
        mock_client = MagicMock()
        mock_client.list_models.return_value = []
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["check"])

        assert result.exit_code == 1
        assert "Cannot connect to Ollama" in result.stdout

    @patch("claude_md_bench.cli.OllamaClient")
    def test_check_specific_model_found(self, mock_client_class: MagicMock) -> None:
        """Should confirm when specific model is available."""
        mock_client = MagicMock()
        mock_client.list_models.return_value = ["llama3.2:latest"]
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["check", "--model", "llama3.2:latest"])

        assert result.exit_code == 0
        assert "is available" in result.stdout

    @patch("claude_md_bench.cli.OllamaClient")
    def test_check_specific_model_not_found(self, mock_client_class: MagicMock) -> None:
        """Should warn when specific model is not available."""
        mock_client = MagicMock()
        mock_client.list_models.return_value = ["llama3.2:latest"]
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["check", "--model", "nonexistent:model"])

        assert result.exit_code == 1
        assert "not found" in result.stdout


class TestModelsCommand:
    """Tests for the models command."""

    @patch("claude_md_bench.cli.OllamaClient")
    def test_models_lists_available(self, mock_client_class: MagicMock) -> None:
        """Should list all available models."""
        mock_client = MagicMock()
        mock_client.list_models.return_value = ["llama3.2:latest", "qwen2.5:32b"]
        mock_client_class.return_value = mock_client

        result = runner.invoke(app, ["models"])

        assert result.exit_code == 0
        assert "llama3.2:latest" in result.stdout
        assert "qwen2.5:32b" in result.stdout
        assert "Total: 2 models" in result.stdout


class TestCompareCommand:
    """Tests for the compare command."""

    def test_compare_missing_files_shows_error(self, tmp_path: Path) -> None:
        """Should show error for missing files."""
        result = runner.invoke(
            app,
            ["compare", str(tmp_path / "a.md"), str(tmp_path / "b.md")],
        )

        # Typer validates file existence before running command
        assert result.exit_code != 0

    @patch("claude_md_bench.commands.compare.OllamaClient")
    def test_compare_with_valid_files(
        self,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
        minimal_claude_md_file: Path,
    ) -> None:
        """Should run comparison with valid files."""
        mock_client = MagicMock()
        mock_client.check_health.return_value = True
        mock_client.generate.return_value = """CLARITY: 80
COMPLETENESS: 75
ACTIONABILITY: 82
STANDARDS: 85
CONTEXT: 70
OVERALL: 78

STRENGTHS:
- Good structure

WEAKNESSES:
- Could be better

RECOMMENDATIONS:
- Add more content

DETAILED_ANALYSIS:
Analysis complete.
"""
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "compare",
                str(sample_claude_md_file),
                str(minimal_claude_md_file),
                "--quiet",
            ],
        )

        assert result.exit_code == 0
        assert "Reports saved" in result.stdout

    @patch("claude_md_bench.commands.compare.OllamaClient")
    def test_compare_ollama_not_running(
        self,
        mock_client_class: MagicMock,
        sample_claude_md_file: Path,
        minimal_claude_md_file: Path,
    ) -> None:
        """Should show error when Ollama is not running."""
        mock_client = MagicMock()
        mock_client.check_health.return_value = False
        mock_client.list_models.return_value = []
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            app,
            ["compare", str(sample_claude_md_file), str(minimal_claude_md_file)],
        )

        assert result.exit_code == 1
        assert "Cannot connect to Ollama" in result.stdout


class TestMainCallback:
    """Tests for the main CLI callback."""

    def test_help_shows_usage(self) -> None:
        """Should show help text with --help."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "CLI tool for benchmarking" in result.stdout
        assert "compare" in result.stdout

    def test_no_args_shows_help(self) -> None:
        """Should show help when no arguments provided."""
        result = runner.invoke(app, [])

        assert result.exit_code == 0
        assert "Usage:" in result.stdout
