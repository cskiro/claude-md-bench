"""
Optimize command for claude-md-bench.

Iteratively improves a CLAUDE.md file using meta-prompting.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from claude_md_bench.core.optimizer import ClaudeMDOptimizer, OptimizationResult
from claude_md_bench.llm.ollama import OllamaClient, OllamaConnectionError

console = Console()


def optimize(
    file: Annotated[
        Path,
        typer.Argument(
            help="CLAUDE.md file to optimize",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            resolve_path=True,
        ),
    ],
    iterations: Annotated[
        int,
        typer.Option(
            "--iterations",
            "-i",
            help="Number of optimization iterations",
            min=1,
            max=10,
        ),
    ] = 3,
    model: Annotated[
        str,
        typer.Option(
            "--model",
            "-m",
            help="Ollama model to use for optimization",
        ),
    ] = "llama3.2:latest",
    host: Annotated[
        str,
        typer.Option(
            "--host",
            help="Ollama API host",
        ),
    ] = "http://localhost:11434",
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output path for optimized file (default: CLAUDE.optimized.md)",
            file_okay=True,
            dir_okay=False,
        ),
    ] = None,
    timeout: Annotated[
        int,
        typer.Option(
            "--timeout",
            "-t",
            help="Request timeout in seconds",
        ),
    ] = 180,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Suppress detailed output",
        ),
    ] = False,
) -> None:
    """
    Optimize a CLAUDE.md file using meta-prompting.

    Iteratively evaluates and improves the file, targeting weak areas
    identified in each evaluation round.

    Example:
        claude-md-bench optimize ~/.claude/CLAUDE.md
        claude-md-bench optimize CLAUDE.md --iterations 5 --model qwen2.5:32b
    """
    # Initialize Ollama client
    with console.status("[cyan]Connecting to Ollama...[/cyan]"):
        ollama = OllamaClient(
            host=host,
            model=model,
            timeout=timeout,
        )

        if not ollama.check_health():
            console.print(f"[red]Error:[/red] Cannot connect to Ollama at {host}")
            console.print("Ensure Ollama is running: [cyan]ollama serve[/cyan]")

            available_models = ollama.list_models()
            if available_models:
                console.print(f"\nAvailable models: {', '.join(available_models)}")
                if model not in available_models:
                    console.print(f"\nModel '{model}' not found. Pull it with:")
                    console.print(f"  [cyan]ollama pull {model}[/cyan]")

            raise typer.Exit(1)

    if not quiet:
        console.print(f"[green]![/green] Ollama ready (model: {model})")
        console.print()

    # Initialize optimizer
    optimizer = ClaudeMDOptimizer(ollama)

    # Run optimization
    try:
        if not quiet:
            console.print(Panel.fit(
                f"[bold cyan]Optimizing CLAUDE.md[/bold cyan]\n"
                f"File: {file}\n"
                f"Iterations: {iterations}",
                border_style="cyan",
            ))
            console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"[cyan]Running {iterations} optimization iterations...",
                total=None,
            )

            result = optimizer.optimize(
                claude_md_path=file,
                iterations=iterations,
                output_path=output,
            )

            progress.update(task, completed=True)

    except OllamaConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Optimization failed:[/red] {e}")
        raise typer.Exit(1)

    # Display results
    if not quiet:
        _print_optimization_result(result)


def _print_optimization_result(result: OptimizationResult) -> None:
    """Print optimization results to console."""
    console.print()

    # Summary panel
    improvement_color = "green" if result.total_improvement > 0 else "yellow" if result.total_improvement == 0 else "red"
    improvement_sign = "+" if result.total_improvement > 0 else ""

    console.print(Panel.fit(
        f"[bold]Optimization Complete[/bold]\n\n"
        f"Original Score: {result.original_score:.1f}/100\n"
        f"Final Score: [bold]{result.final_score:.1f}/100[/bold]\n"
        f"Improvement: [{improvement_color}]{improvement_sign}{result.total_improvement:.1f} points[/{improvement_color}]",
        border_style="green" if result.total_improvement > 0 else "yellow",
    ))

    # Iteration details table
    console.print("\n[bold]Iteration Progress[/bold]")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Iteration", justify="center", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Delta", justify="right")
    table.add_column("Status", justify="center")

    for iteration in result.iterations:
        delta_str = f"{iteration.delta:+.1f}"
        delta_color = "green" if iteration.delta > 0 else "red" if iteration.delta < 0 else "white"

        # Determine best iteration
        is_best = iteration.score == result.final_score
        status = "[green]Best[/green]" if is_best else ""

        table.add_row(
            str(iteration.iteration),
            f"{iteration.score:.1f}/100",
            f"[{delta_color}]{delta_str}[/{delta_color}]",
            status,
        )

    console.print(table)

    # Output location
    if result.output_path:
        console.print(f"\n[bold]Output saved to:[/bold]")
        console.print(f"  [cyan]{result.output_path}[/cyan]")

    # Size comparison
    original_size = len(result.original_content)
    final_size = len(result.final_content)
    size_delta = final_size - original_size
    size_pct = (size_delta / original_size * 100) if original_size > 0 else 0

    console.print(f"\n[dim]Size: {original_size:,} -> {final_size:,} chars ({size_pct:+.1f}%)[/dim]")
