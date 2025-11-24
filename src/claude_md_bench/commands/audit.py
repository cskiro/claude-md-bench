"""
Audit command for claude-md-bench.

Analyzes a single CLAUDE.md file and provides quality assessment.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from claude_md_bench.core.analyzer import ClaudeMDAnalyzer
from claude_md_bench.core.reporter import Reporter
from claude_md_bench.llm.ollama import OllamaClient, OllamaConnectionError

console = Console()


def audit(
    file: Annotated[
        Path,
        typer.Argument(
            help="Path to the CLAUDE.md file to audit",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    model: Annotated[
        str,
        typer.Option(
            "--model",
            "-m",
            help="Ollama model to use for analysis",
        ),
    ] = "llama3.2:latest",
    host: Annotated[
        str,
        typer.Option(
            "--host",
            help="Ollama API host",
        ),
    ] = "http://localhost:11434",
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory for saving reports",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
    output_format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: text, html, or both",
        ),
    ] = "both",
    timeout: Annotated[
        int,
        typer.Option(
            "--timeout",
            "-t",
            help="Request timeout in seconds",
        ),
    ] = 120,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Suppress console output (only save reports)",
        ),
    ] = False,
) -> None:
    """
    Audit a single CLAUDE.md file for quality and completeness.

    Analyzes the file on 5 dimensions (Clarity, Completeness, Actionability,
    Standards, Context) and provides detailed feedback with recommendations.

    Example:
        claude-md-bench audit ~/.claude/CLAUDE.md
        claude-md-bench audit ./CLAUDE.md --format html --output-dir ./reports
    """
    # Use parent directory name as project name
    project_name = file.parent.name

    # Initialize Ollama client
    with console.status("[cyan]Connecting to Ollama...[/cyan]"):
        ollama = OllamaClient(
            host=host,
            model=model,
            timeout=timeout,
        )

        try:
            if not ollama.check_health():
                console.print(f"[red]Error:[/red] Cannot connect to Ollama at {host}")
                console.print("Ensure Ollama is running: [cyan]ollama serve[/cyan]")

                # Check if model is available
                available_models = ollama.list_models()
                if available_models:
                    console.print(f"\nAvailable models: {', '.join(available_models)}")
                    if model not in available_models:
                        console.print(f"\nModel '{model}' not found. Pull it with:")
                        console.print(f"  [cyan]ollama pull {model}[/cyan]")

                raise typer.Exit(1)
        except OllamaConnectionError as e:
            console.print(f"[red]Connection error:[/red] {e}")
            console.print("Ensure Ollama is running: [cyan]ollama serve[/cyan]")
            raise typer.Exit(1) from None

    if not quiet:
        console.print(f"[green]✓[/green] Ollama ready (model: {model})")
        console.print()

    # Run analysis
    analyzer = ClaudeMDAnalyzer(ollama)

    try:
        with console.status("[cyan]Analyzing CLAUDE.md file...[/cyan]"):
            result = analyzer.analyze(
                claude_md_path=file,
                project_name=project_name,
            )
    except OllamaConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        raise typer.Exit(1) from None
    except Exception as e:
        console.print(f"[red]Analysis failed:[/red] {e}")
        raise typer.Exit(1) from None

    # Check for errors
    if result.error:
        console.print(f"[red]Error analyzing {file}:[/red] {result.error}")
        raise typer.Exit(1)

    # Display results
    reporter = Reporter(output_dir=output_dir)

    if not quiet:
        reporter.print_audit(result, file)

    # Save reports
    saved_paths: list[Path] = []

    if output_format in ("text", "both"):
        text_path = reporter.save_audit_text_report(result, file)
        saved_paths.append(text_path)

    if output_format in ("html", "both"):
        html_path = reporter.save_audit_html_report(result, file)
        if html_path:
            saved_paths.append(html_path)

    # Print saved report locations
    if saved_paths:
        console.print("\n[bold]Reports saved:[/bold]")
        for path in saved_paths:
            console.print(f"  [cyan]{path}[/cyan]")
            if path.suffix == ".html":
                console.print(f"  [dim]View in browser: file://{path}[/dim]")
