"""
Report Generator

Generates text and HTML reports for CLAUDE.md comparisons and audits.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from claude_md_bench.core.analyzer import AnalysisResult, ComparisonResult
from claude_md_bench.core.reporting_constants import (
    DIMENSIONS,
    generate_comparison_filename,
    generate_report_filename,
    get_delta_style,
    get_score_style,
)

logger = logging.getLogger(__name__)


class Reporter:
    """Generates comparison reports in various formats."""

    def __init__(self, output_dir: Path | None = None) -> None:
        """
        Initialize reporter.

        Args:
            output_dir: Directory for saving reports. Defaults to ~/.claude-md-bench/reports/
        """
        if output_dir is None:
            output_dir = Path.home() / ".claude-md-bench" / "reports"

        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.console = Console()

        # Setup Jinja2 for HTML templates
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env: Environment | None
        if template_dir.exists():
            self.jinja_env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(["html", "xml"]),
            )
        else:
            self.jinja_env = None
            logger.warning(f"Template directory not found: {template_dir}")

    def print_comparison(self, result: ComparisonResult) -> None:
        """
        Print comparison results to console with rich formatting.

        Args:
            result: Comparison result to display
        """
        # Header
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold cyan]CLAUDE.md Comparison Results[/bold cyan]",
                border_style="cyan",
            )
        )

        # Summary table
        table = Table(show_header=True, header_style="bold")
        table.add_column("Version", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Size", justify="right")
        table.add_column("Winner", justify="center")

        analysis_a = result.version_a["analysis"]
        analysis_b = result.version_b["analysis"]

        # Format scores with winner highlighting
        score_a = (
            f"[green]{analysis_a['score']:.1f}/100[/green]"
            if result.winner == "A"
            else f"{analysis_a['score']:.1f}/100"
        )
        score_b = (
            f"[green]{analysis_b['score']:.1f}/100[/green]"
            if result.winner == "B"
            else f"{analysis_b['score']:.1f}/100"
        )

        table.add_row(
            f"A: {result.version_a['name']}",
            score_a,
            f"{analysis_a['file_size']:,} chars",
            "🏆" if result.winner == "A" else "",
        )
        table.add_row(
            f"B: {result.version_b['name']}",
            score_b,
            f"{analysis_b['file_size']:,} chars",
            "🏆" if result.winner == "B" else "",
        )

        self.console.print(table)

        # Winner announcement
        if result.winner == "TIE":
            self.console.print("\n[yellow] Result: TIE[/yellow]")
        else:
            self.console.print(
                f"\n[green] Winner: Version {result.winner}[/green] "
                f"(+{result.score_delta:.1f} points)"
            )

        # Dimension scores
        self._print_dimension_scores(analysis_a, analysis_b)

        # Strengths and weaknesses
        self._print_analysis_details(result)

    def _print_dimension_scores(
        self,
        analysis_a: dict[str, Any],
        analysis_b: dict[str, Any],
    ) -> None:
        """Print dimension score comparison."""
        self.console.print("\n[bold]Dimension Scores[/bold]")

        table = Table(show_header=True, header_style="bold")
        table.add_column("Dimension", style="cyan")
        table.add_column("Version A", justify="right")
        table.add_column("Version B", justify="right")
        table.add_column("Delta", justify="right")

        scores_a = analysis_a.get("dimension_scores", {})
        scores_b = analysis_b.get("dimension_scores", {})

        for dim in DIMENSIONS:
            score_a = scores_a.get(dim, 0.0)
            score_b = scores_b.get(dim, 0.0)
            delta = score_a - score_b

            delta_str = f"+{delta:.0f}" if delta > 0 else f"{delta:.0f}"
            delta_color = get_delta_style(delta)

            table.add_row(
                dim.title(),
                f"{score_a:.0f}",
                f"{score_b:.0f}",
                f"[{delta_color}]{delta_str}[/]",
            )

        self.console.print(table)

    def _print_analysis_details(self, result: ComparisonResult) -> None:
        """Print strengths and weaknesses for both versions."""
        analysis_a = result.version_a["analysis"]
        analysis_b = result.version_b["analysis"]

        # Version A details
        self.console.print(f"\n[bold cyan]Version A: {result.version_a['name']}[/bold cyan]")

        self.console.print("[green]Strengths:[/green]")
        for s in analysis_a.get("strengths", []):
            self.console.print(f"  [green]✓[/green] {s}")

        self.console.print("[yellow]Weaknesses:[/yellow]")
        for w in analysis_a.get("weaknesses", []):
            self.console.print(f"  [yellow]✗[/yellow] {w}")

        # Version B details
        self.console.print(f"\n[bold cyan]Version B: {result.version_b['name']}[/bold cyan]")

        self.console.print("[green]Strengths:[/green]")
        for s in analysis_b.get("strengths", []):
            self.console.print(f"  [green]✓[/green] {s}")

        self.console.print("[yellow]Weaknesses:[/yellow]")
        for w in analysis_b.get("weaknesses", []):
            self.console.print(f"  [yellow]✗[/yellow] {w}")

    def save_text_report(self, result: ComparisonResult) -> Path:
        """
        Save comparison as text report.

        Args:
            result: Comparison result to save

        Returns:
            Path to saved report
        """
        filename = generate_comparison_filename(
            "comparison",
            result.version_a["name"],
            result.version_b["name"],
            "txt",
        )
        report_path = self.output_dir / filename

        analysis_a = result.version_a["analysis"]
        analysis_b = result.version_b["analysis"]

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("CLAUDE.md Comparison Report\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")

            f.write(f"Version A: {result.version_a['path']}\n")
            f.write(f"Score: {analysis_a['score']:.1f}/100\n")
            f.write(f"Size: {analysis_a['file_size']:,} chars\n\n")

            f.write(f"Version B: {result.version_b['path']}\n")
            f.write(f"Score: {analysis_b['score']:.1f}/100\n")
            f.write(f"Size: {analysis_b['file_size']:,} chars\n\n")

            f.write(f"Winner: Version {result.winner}\n")
            if result.winner != "TIE":
                f.write(f"Margin: {result.score_delta:.1f} points\n")
            f.write("\n")

            # Dimension scores
            f.write("-" * 70 + "\n")
            f.write("Dimension Scores\n")
            f.write("-" * 70 + "\n\n")

            scores_a = analysis_a.get("dimension_scores", {})
            scores_b = analysis_b.get("dimension_scores", {})

            for dim in DIMENSIONS:
                f.write(
                    f"{dim.title():<15} A: {scores_a.get(dim, 0):.0f}  B: {scores_b.get(dim, 0):.0f}\n"
                )

            f.write("\n")

            # Strengths and weaknesses
            f.write("-" * 70 + "\n")
            f.write("Analysis Details\n")
            f.write("-" * 70 + "\n\n")

            f.write("Version A Strengths:\n")
            for s in analysis_a.get("strengths", []):
                f.write(f"  + {s}\n")
            f.write("\n")

            f.write("Version A Weaknesses:\n")
            for w in analysis_a.get("weaknesses", []):
                f.write(f"  - {w}\n")
            f.write("\n")

            f.write("Version B Strengths:\n")
            for s in analysis_b.get("strengths", []):
                f.write(f"  + {s}\n")
            f.write("\n")

            f.write("Version B Weaknesses:\n")
            for w in analysis_b.get("weaknesses", []):
                f.write(f"  - {w}\n")

        logger.info(f"Text report saved to: {report_path}")
        return report_path

    def save_html_report(self, result: ComparisonResult) -> Path | None:
        """
        Save comparison as HTML report.

        Args:
            result: Comparison result to save

        Returns:
            Path to saved report, or None if templates not available
        """
        if self.jinja_env is None:
            logger.warning("Cannot generate HTML report: templates not available")
            return None

        try:
            template = self.jinja_env.get_template("comparison.html")
        except Exception as e:
            logger.error(f"Failed to load template: {e}")
            return None

        filename = generate_comparison_filename(
            "comparison",
            result.version_a["name"],
            result.version_b["name"],
            "html",
        )
        report_path = self.output_dir / filename

        analysis_a = result.version_a["analysis"]
        analysis_b = result.version_b["analysis"]

        # Build dimension comparison data
        dimensions_data: dict[str, dict[str, float]] = {}
        scores_a = analysis_a.get("dimension_scores", {})
        scores_b = analysis_b.get("dimension_scores", {})

        for dim in DIMENSIONS:
            dimensions_data[dim] = {
                "a": scores_a.get(dim, 0.0),
                "b": scores_b.get(dim, 0.0),
            }

        # Read file contents for drawer display
        try:
            content_a = Path(result.version_a["path"]).read_text(encoding="utf-8")
        except Exception:
            content_a = "Unable to read file content"

        try:
            content_b = Path(result.version_b["path"]).read_text(encoding="utf-8")
        except Exception:
            content_b = "Unable to read file content"

        # Render template
        html_content = template.render(
            version_a={
                "name": result.version_a["name"],
                "path": result.version_a["path"],
                "score": analysis_a["score"],
                "size": analysis_a["file_size"],
                "strengths": analysis_a.get("strengths", []),
                "weaknesses": analysis_a.get("weaknesses", []),
                "detailed_analysis": analysis_a.get("detailed_analysis", ""),
                "content": content_a,
            },
            version_b={
                "name": result.version_b["name"],
                "path": result.version_b["path"],
                "score": analysis_b["score"],
                "size": analysis_b["file_size"],
                "strengths": analysis_b.get("strengths", []),
                "weaknesses": analysis_b.get("weaknesses", []),
                "detailed_analysis": analysis_b.get("detailed_analysis", ""),
                "content": content_b,
            },
            winner=result.winner,
            score_delta=result.score_delta,
            dimensions=dimensions_data,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        report_path.write_text(html_content, encoding="utf-8")
        logger.info(f"HTML report saved to: {report_path}")
        return report_path

    def print_audit(self, result: AnalysisResult, file_path: Path) -> None:
        """
        Print audit results to console with rich formatting.

        Args:
            result: Analysis result to display
            file_path: Path to the audited file
        """
        logger.info(f"Printing audit results for: {file_path}")

        # Header
        self.console.print()
        self.console.print(
            Panel.fit(
                f"[bold cyan]CLAUDE.md Audit: {file_path.name}[/bold cyan]",
                border_style="cyan",
            )
        )

        # Overall score with color coding
        score_color = get_score_style(result.score)
        self.console.print(
            f"\n[bold]Overall Score:[/bold] [{score_color}]{result.score:.1f}/100[/{score_color}]"
        )
        self.console.print(f"[dim]File size: {result.file_size:,} characters[/dim]")

        # Dimension scores table
        self.console.print("\n[bold]Dimension Scores[/bold]")
        table = Table(show_header=True, header_style="bold")
        table.add_column("Dimension", style="cyan")
        table.add_column("Score", justify="right")

        for dim in DIMENSIONS:
            score = result.dimension_scores.get(dim, 0.0)
            score_style = get_score_style(score)
            table.add_row(dim.title(), f"[{score_style}]{score:.0f}[/{score_style}]")

        self.console.print(table)

        # Strengths
        if result.strengths:
            self.console.print("\n[green]Strengths:[/green]")
            for s in result.strengths:
                self.console.print(f"  [green]✓[/green] {s}")

        # Weaknesses
        if result.weaknesses:
            self.console.print("\n[yellow]Weaknesses:[/yellow]")
            for w in result.weaknesses:
                self.console.print(f"  [yellow]✗[/yellow] {w}")

        # Recommendations
        if result.recommendations:
            self.console.print("\n[cyan]Recommendations:[/cyan]")
            for r in result.recommendations:
                self.console.print(f"  [cyan]→[/cyan] {r}")

    def save_audit_text_report(self, result: AnalysisResult, file_path: Path) -> Path:
        """
        Save audit results as text report.

        Args:
            result: Analysis result to save
            file_path: Path to the audited file

        Returns:
            Path to saved report
        """
        filename = generate_report_filename("audit", file_path.stem, "txt")
        report_path = self.output_dir / filename

        with open(report_path, "w", encoding="utf-8") as f:
            f.write("CLAUDE.md Audit Report\n")
            f.write("=" * 70 + "\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"File: {file_path}\n")
            f.write(f"Size: {result.file_size:,} characters\n\n")

            f.write(f"Overall Score: {result.score:.1f}/100\n\n")

            # Dimension scores
            f.write("-" * 70 + "\n")
            f.write("Dimension Scores\n")
            f.write("-" * 70 + "\n\n")

            for dim in DIMENSIONS:
                score = result.dimension_scores.get(dim, 0.0)
                f.write(f"{dim.title():<15} {score:.0f}/100\n")

            f.write("\n")

            # Strengths
            f.write("-" * 70 + "\n")
            f.write("Strengths\n")
            f.write("-" * 70 + "\n\n")
            for s in result.strengths:
                f.write(f"  + {s}\n")
            f.write("\n")

            # Weaknesses
            f.write("-" * 70 + "\n")
            f.write("Weaknesses\n")
            f.write("-" * 70 + "\n\n")
            for w in result.weaknesses:
                f.write(f"  - {w}\n")
            f.write("\n")

            # Recommendations
            f.write("-" * 70 + "\n")
            f.write("Recommendations\n")
            f.write("-" * 70 + "\n\n")
            for r in result.recommendations:
                f.write(f"  * {r}\n")
            f.write("\n")

            # Detailed analysis
            if result.detailed_analysis:
                f.write("-" * 70 + "\n")
                f.write("Detailed Analysis\n")
                f.write("-" * 70 + "\n\n")
                f.write(result.detailed_analysis)
                f.write("\n")

        logger.info(f"Text report saved to: {report_path}")
        return report_path

    def save_audit_html_report(self, result: AnalysisResult, file_path: Path) -> Path | None:
        """
        Save audit results as HTML report.

        Args:
            result: Analysis result to save
            file_path: Path to the audited file

        Returns:
            Path to saved report, or None if templates not available
        """
        if self.jinja_env is None:
            logger.warning("Cannot generate HTML report: templates not available")
            return None

        try:
            template = self.jinja_env.get_template("audit.html")
        except Exception as e:
            logger.error(f"Failed to load audit template: {e}")
            return None

        filename = generate_report_filename("audit", file_path.stem, "html")
        report_path = self.output_dir / filename

        # Read file content for display
        try:
            file_content = file_path.read_text(encoding="utf-8")
        except Exception:
            file_content = "Unable to read file content"

        # Render template
        html_content = template.render(
            file_name=file_path.name,
            file_path=str(file_path),
            file_content=file_content,
            score=result.score,
            file_size=result.file_size,
            dimensions=DIMENSIONS,
            dimension_scores=result.dimension_scores,
            strengths=result.strengths,
            weaknesses=result.weaknesses,
            recommendations=result.recommendations,
            detailed_analysis=result.detailed_analysis,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        report_path.write_text(html_content, encoding="utf-8")
        logger.info(f"HTML report saved to: {report_path}")
        return report_path
