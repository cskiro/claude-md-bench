"""
CLI entry point for claude-md-bench.

Main Typer application that registers all commands.
"""

from __future__ import annotations

import logging
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from claude_md_bench import __version__
from claude_md_bench.commands.compare import compare
from claude_md_bench.llm.ollama import OllamaClient

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s - %(message)s",
)

app = typer.Typer(
    name="claude-md-bench",
    help="CLI tool for benchmarking and optimizing CLAUDE.md files",
    no_args_is_help=True,
    add_completion=True,
)

# Register compare command
app.command()(compare)

console = Console()


@app.command()
def version() -> None:
    """Show version information."""
    console.print(f"claude-md-bench version [cyan]{__version__}[/cyan]")


@app.command()
def check(
    host: Annotated[
        str,
        typer.Option(
            "--host",
            "-h",
            help="Ollama API host",
        ),
    ] = "http://localhost:11434",
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            "-m",
            help="Check if specific model is available",
        ),
    ] = None,
) -> None:
    """
    Check Ollama connectivity and available models.

    Verifies that Ollama is running and lists available models.

    Example:
        claude-md-bench check
        claude-md-bench check --model llama3.2:latest
    """
    console.print(f"Checking Ollama at [cyan]{host}[/cyan]...")
    console.print()

    # Create client (without specific model if not provided)
    ollama = OllamaClient(
        host=host,
        model=model or "llama3.2:latest",
    )

    # List available models
    models = ollama.list_models()

    if not models:
        console.print("[red]✗[/red] Cannot connect to Ollama")
        console.print()
        console.print("Make sure Ollama is running:")
        console.print("  [cyan]ollama serve[/cyan]")
        raise typer.Exit(1)

    console.print("[green]✓[/green] Ollama is running")
    console.print()

    # Display available models
    table = Table(title="Available Models", show_header=True, header_style="bold")
    table.add_column("Model", style="cyan")
    table.add_column("Status", justify="center")

    for m in sorted(models):
        if model and m == model:
            table.add_row(m, "[green]✓ Selected[/green]")
        else:
            table.add_row(m, "")

    console.print(table)

    # Check specific model if requested
    if model:
        if model in models:
            console.print(f"\n[green]✓[/green] Model '{model}' is available")
        else:
            console.print(f"\n[yellow]⚠[/yellow] Model '{model}' not found")
            console.print(f"Pull it with: [cyan]ollama pull {model}[/cyan]")
            raise typer.Exit(1)


@app.command()
def models(
    host: Annotated[
        str,
        typer.Option(
            "--host",
            "-h",
            help="Ollama API host",
        ),
    ] = "http://localhost:11434",
) -> None:
    """
    List available Ollama models.

    Quick shortcut to see what models are available for analysis.
    """
    ollama = OllamaClient(host=host)
    available = ollama.list_models()

    if not available:
        console.print("[red]✗[/red] Cannot connect to Ollama or no models available")
        raise typer.Exit(1)

    console.print("[bold]Available models:[/bold]")
    for m in sorted(available):
        console.print(f"  • {m}")

    console.print(f"\n[dim]Total: {len(available)} models[/dim]")


@app.callback()
def main(
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose logging",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            help="Enable debug logging",
        ),
    ] = False,
) -> None:
    """
    CLI tool for benchmarking and optimizing CLAUDE.md files.

    Use 'claude-md-bench compare' to compare two CLAUDE.md files and determine
    which one is more effective.

    For more information on a specific command, run:
        claude-md-bench <command> --help
    """
    # Configure logging based on verbosity
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif verbose:
        logging.getLogger().setLevel(logging.INFO)


if __name__ == "__main__":
    app()
