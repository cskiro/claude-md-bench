# claude-md-bench

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CLI tool for benchmarking and optimizing CLAUDE.md files used by AI coding assistants.

## Overview

`claude-md-bench` analyzes and compares CLAUDE.md configuration files to help you create more effective instructions for AI coding assistants like Claude Code. It uses local LLM inference via Ollama to evaluate files on multiple dimensions:

- **Clarity**: Are instructions clear and specific?
- **Completeness**: Does it cover all essential areas?
- **Actionability**: Are there concrete, executable guidelines?
- **Standards**: Does it enforce quality standards (TDD, types, testing)?
- **Context**: Is there adequate project context and structure?

## Installation

### Prerequisites

1. **Python 3.11+**
2. **Ollama** - Local LLM inference
   ```bash
   # macOS
   brew install ollama

   # Start Ollama server
   ollama serve

   # Pull a model (llama3.2 is lightweight, qwen2.5:32b is better quality)
   ollama pull llama3.2:latest
   ```

### Install from source

```bash
git clone https://github.com/cskiro/claude-md-bench.git
cd claude-md-bench
pip install -e ".[dev]"
```

## Usage

### Check Ollama connectivity

```bash
# Verify Ollama is running and list available models
claude-md-bench check

# Check if specific model is available
claude-md-bench check --model qwen2.5:32b
```

### Compare two CLAUDE.md files

```bash
# Basic comparison
claude-md-bench compare ~/.claude/CLAUDE.md ~/project/CLAUDE.md

# With custom names and output directory
claude-md-bench compare file1.md file2.md \
  --name-a "Production" \
  --name-b "Development" \
  --output-dir ./reports

# Use a different model
claude-md-bench compare file1.md file2.md --model qwen2.5:32b

# Text-only output (no HTML)
claude-md-bench compare file1.md file2.md --format text
```

### Output

The tool generates:
- Console output with rich formatting
- Text report saved to `~/.claude-md-bench/reports/`
- HTML report with visual dimension comparison

## Example Output

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  CLAUDE.md Comparison Results          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌─────────────────────┬───────────┬────────────┬────────┐
│ Version             │ Score     │ Size       │ Winner │
├─────────────────────┼───────────┼────────────┼────────┤
│ A: Production       │ 85.0/100  │ 15,234     │        │
│ B: Development      │ 72.0/100  │ 8,567      │        │
└─────────────────────┴───────────┴────────────┴────────┘

🏆 Winner: Version A (+13.0 points)

Dimension Scores
┌─────────────────┬───────────┬───────────┬───────┐
│ Dimension       │ Version A │ Version B │ Delta │
├─────────────────┼───────────┼───────────┼───────┤
│ Clarity         │ 85        │ 70        │ +15   │
│ Completeness    │ 80        │ 65        │ +15   │
│ Actionability   │ 90        │ 75        │ +15   │
│ Standards       │ 85        │ 80        │ +5    │
│ Context         │ 85        │ 70        │ +15   │
└─────────────────┴───────────┴───────────┴───────┘
```

## Development

### Setup development environment

```bash
# Clone repository
git clone https://github.com/cskiro/claude-md-bench.git
cd claude-md-bench

# Install with dev dependencies
pip install -e ".[dev]"
```

### Run tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=claude_md_bench --cov-report=html

# Run specific test file
pytest tests/test_analyzer.py -v
```

### Code quality

```bash
# Lint with ruff
ruff check src tests

# Type check with mypy
mypy src

# Format code
ruff format src tests
```

## Architecture

```
src/claude_md_bench/
├── cli.py              # Main Typer application
├── commands/
│   └── compare.py      # Compare command
├── core/
│   ├── analyzer.py     # CLAUDE.md analysis logic
│   └── reporter.py     # Report generation
├── llm/
│   └── ollama.py       # Ollama client wrapper
└── templates/
    └── comparison.html # HTML report template
```

## Roadmap

### Phase 1 (Current): Compare ✅
- A/B comparison of CLAUDE.md files
- Multi-dimensional scoring
- HTML and text reports

### Phase 2: Benchmark
- Execute tasks against CLAUDE.md configurations
- TDD compliance evaluation
- Performance metrics

### Phase 3: Optimize
- Meta-prompting for CLAUDE.md improvement
- Iterative optimization loops
- Automated recommendations

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for the CLI
- Uses [Rich](https://rich.readthedocs.io/) for beautiful console output
- Powered by [Ollama](https://ollama.ai/) for local LLM inference
- Inspired by Arize AI's prompt optimization research
