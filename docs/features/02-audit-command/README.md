# Audit Command

Feature branch: `feature/audit-command`

## Overview

Add `claude-md-bench audit file.md` command to analyze a single CLAUDE.md file without requiring comparison or optimization loops. Provides quick quality assessment with scores and recommendations.

## Issue

- [#4](https://github.com/cskiro/claude-md-bench/issues/4) - Add audit command for single-file analysis

## Phases

| Phase | Description | Status |
|-------|-------------|--------|
| [Phase 1](./phase-1-core-infrastructure.md) | Core command infrastructure | Complete |
| [Phase 2](./phase-2-reporter-methods.md) | Reporter audit methods | Complete |
| [Phase 3](./phase-3-html-template.md) | HTML template | Complete |
| [Phase 4](./phase-4-tests.md) | Tests with 80% coverage | Complete |

## Files to Create

- `src/claude_md_bench/commands/audit.py`
- `src/claude_md_bench/templates/audit.html`
- `tests/test_audit.py`

## Files to Modify

- `src/claude_md_bench/cli.py`
- `src/claude_md_bench/core/reporter.py`

## CLI Specification

```bash
claude-md-bench audit my-claude.md [OPTIONS]

Options:
  --model, -m       Ollama model (default: llama3.2:latest)
  --host            Ollama API host (default: http://localhost:11434)
  --output-dir, -o  Output directory for reports
  --format, -f      Output format: text, html, both (default: both)
  --timeout, -t     Request timeout in seconds (default: 120)
  --quiet, -q       Suppress console output
```

## Testing Checklist

- [ ] Command executes successfully with valid file
- [ ] Error handling for missing file
- [ ] Error handling for Ollama connection failure
- [ ] Text report generation works
- [ ] HTML report generation works
- [ ] Both format option works
- [ ] Quiet mode suppresses console output
- [ ] Coverage >= 80% on new code
