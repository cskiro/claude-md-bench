# Phase 1: Core Command Infrastructure

**Issue**: [#4](https://github.com/cskiro/claude-md-bench/issues/4)

## Goal

Create the audit command file and register it in the CLI, following existing command patterns.

## Tasks

- [ ] Create `src/claude_md_bench/commands/audit.py` with command function
- [ ] Import and register in `src/claude_md_bench/cli.py`
- [ ] Implement core flow: OllamaClient -> ClaudeMDAnalyzer -> output

## Implementation Details

### Command Signature

```python
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
    model: Annotated[str, typer.Option("--model", "-m", help="Ollama model")] = "llama3.2:latest",
    host: Annotated[str, typer.Option("--host", help="Ollama API host")] = "http://localhost:11434",
    output_dir: Annotated[Optional[Path], typer.Option("--output-dir", "-o", help="Output directory")] = None,
    output_format: Annotated[str, typer.Option("--format", "-f", help="Output format")] = "both",
    timeout: Annotated[int, typer.Option("--timeout", "-t", help="Timeout in seconds")] = 120,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Suppress output")] = False,
) -> None:
```

### Data Flow

1. Initialize `OllamaClient(host, timeout)` and check health
2. Create `ClaudeMDAnalyzer(client, model)`
3. Call `analyzer.analyze(file, project_name=file.parent.name)`
4. Get `AnalysisResult` dataclass
5. Pass to Reporter for console/file output

### CLI Registration

```python
# In cli.py
from claude_md_bench.commands.audit import audit
app.command()(audit)
```

## Acceptance Criteria

- [ ] `claude-md-bench audit --help` shows correct options
- [ ] Command validates file exists and is readable
- [ ] Handles OllamaConnectionError gracefully
- [ ] Shows Rich console output with scores
- [ ] Project name derived from parent directory

## Notes

- Reuse `AnalysisResult` dataclass from analyzer.py
- Follow same error handling pattern as compare command
- Console output initially simple; enhanced in Phase 2
