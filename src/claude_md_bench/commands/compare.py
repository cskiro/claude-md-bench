"""
Compare command for claude-md-bench.

Compares two CLAUDE.md files and determines which is better.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console

from claude_md_bench.core.analyzer import ClaudeMDAnalyzer
from claude_md_bench.core.reporter import Reporter
from claude_md_bench.llm.ollama import OllamaClient, OllamaConnectionError

app = typer.Typer(
    name="compare",
    help="Compare two CLAUDE.md files",
    no_args_is_help=True,
)

console = Console()


@app.callback(invoke_without_command=True)
def compare(
    file_a: Annotated[
        Path,
        typer.Argument(
            help="First CLAUDE.md file to compare",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    file_b: Annotated[
        Path,
        typer.Argument(
            help="Second CLAUDE.md file to compare",
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
            "-h",
            help="Ollama API host",
        ),
    ] = "http://localhost:11434",
    output_dir: Annotated[
        Optional[Path],
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
    name_a: Annotated[
        Optional[str],
        typer.Option(
            "--name-a",
            help="Display name for first version",
        ),
    ] = None,
    name_b: Annotated[
        Optional[str],
        typer.Option(
            "--name-b",
            help="Display name for second version",
        ),
    ] = None,
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
    Compare two CLAUDE.md files and determine which is better.

    Analyzes both files on 5 dimensions (Clarity, Completeness, Actionability,
    Standards, Context) and provides detailed feedback with strengths and weaknesses.

    Example:
        claude-md-bench compare ~/.claude/CLAUDE.md ~/project/CLAUDE.md
    """
    # Use parent directory names if display names not provided
    project_name_a = name_a or file_a.parent.name
    project_name_b = name_b or file_b.parent.name

    # Initialize Ollama client
    with console.status("[cyan]Connecting to Ollama...[/cyan]"):
        ollama = OllamaClient(
            host=host,
            model=model,
            timeout=timeout,
        )

        if not ollama.check_health():
            console.print(f"[red]Error:[/red] Cannot connect to Ollama at {host}")
            console.print(f"Ensure Ollama is running: [cyan]ollama serve[/cyan]")

            # Check if model is available
            available_models = ollama.list_models()
            if available_models:
                console.print(f"\nAvailable models: {', '.join(available_models)}")
                if model not in available_models:
                    console.print(f"\nModel '{model}' not found. Pull it with:")
                    console.print(f"  [cyan]ollama pull {model}[/cyan]")

            raise typer.Exit(1)

    if not quiet:
        console.print(f"[green]✓[/green] Ollama ready (model: {model})")
        console.print()

    # Run comparison
    analyzer = ClaudeMDAnalyzer(ollama)

    try:
        with console.status("[cyan]Analyzing CLAUDE.md files...[/cyan]"):
            result = analyzer.compare(
                claude_md_a=file_a,
                claude_md_b=file_b,
                project_name_a=project_name_a,
                project_name_b=project_name_b,
            )
    except OllamaConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Analysis failed:[/red] {e}")
        raise typer.Exit(1)

    # Check for errors
    if result.version_a["analysis"].get("error"):
        console.print(f"[red]Error analyzing {file_a}:[/red] {result.version_a['analysis']['error']}")
        raise typer.Exit(1)

    if result.version_b["analysis"].get("error"):
        console.print(f"[red]Error analyzing {file_b}:[/red] {result.version_b['analysis']['error']}")
        raise typer.Exit(1)

    # Display results
    reporter = Reporter(output_dir=output_dir)

    if not quiet:
        reporter.print_comparison(result)

    # Save reports
    saved_paths: list[Path] = []

    if output_format in ("text", "both"):
        text_path = reporter.save_text_report(result)
        saved_paths.append(text_path)

    if output_format in ("html", "both"):
        html_path = reporter.save_html_report(result)
        if html_path:
            saved_paths.append(html_path)

    # Print saved report locations
    if saved_paths:
        console.print("\n[bold]Reports saved:[/bold]")
        for path in saved_paths:
            console.print(f"  [cyan]{path}[/cyan]")
            if path.suffix == ".html":
                console.print(f"  [dim]View in browser: file://{path}[/dim]")
