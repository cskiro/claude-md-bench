# Phase 1: Golden Test Files

## Overview

Create a curated set of CLAUDE.md files with known quality characteristics for benchmark validation.

## Deliverables

### Quality Level Files (12 files)

#### Excellent (90+)
| File | Description | Expected Score |
|------|-------------|----------------|
| `complete-project.md` | Full-featured with examples, commands, architecture | 92-98 |
| `well-structured.md` | Clear sections, good hierarchy, actionable | 90-95 |
| `comprehensive-api.md` | API project with endpoints, auth, errors | 90-95 |

#### Good (70-89)
| File | Description | Expected Score |
|------|-------------|----------------|
| `missing-context.md` | Good structure but lacks project background | 75-82 |
| `sparse-examples.md` | Complete but few examples | 78-85 |
| `verbose-but-good.md` | Quality content, could be more concise | 72-79 |

#### Mediocre (50-69)
| File | Description | Expected Score |
|------|-------------|----------------|
| `vague-instructions.md` | Ambiguous commands and descriptions | 55-65 |
| `inconsistent-style.md` | Mixed formats, unclear hierarchy | 50-62 |
| `outdated-patterns.md` | Old practices, missing modern tooling | 58-68 |

#### Poor (<50)
| File | Description | Expected Score |
|------|-------------|----------------|
| `minimal.md` | Just project name and one command | 20-35 |
| `disorganized.md` | Wall of text, no structure | 25-40 |
| `placeholder.md` | TODO comments, missing sections | 15-30 |

### Dimension-Specific Files (5 files)

| File | Strong Dimension | Weak Dimension |
|------|-----------------|----------------|
| `clear-but-incomplete.md` | Clarity (85+) | Completeness (<60) |
| `complete-but-vague.md` | Completeness (85+) | Clarity (<60) |
| `standard-but-generic.md` | Standards (85+) | Context (<60) |
| `actionable-but-bare.md` | Actionability (85+) | Context (<60) |
| `contextual-but-passive.md` | Context (85+) | Actionability (<60) |

### Domain Files (5 files)

| Domain | File | Key Patterns |
|--------|------|--------------|
| Python CLI | `python-cli.md` | pytest, pip, argparse, pyproject.toml |
| TypeScript Library | `typescript-lib.md` | npm, tsc, ESLint, tsconfig |
| React Application | `react-app.md` | Vite, Testing Library, components |
| Monorepo | `monorepo.md` | Workspaces, nx/turborepo, packages |
| API Service | `api-service.md` | REST/GraphQL, auth, rate limiting |

### Edge Case Files (4 files)

| File | Characteristic | Expected Behavior |
|------|----------------|-------------------|
| `empty.md` | 0 bytes | Error or score 0-5 |
| `single-line.md` | Just "# Project" | Score 5-15 |
| `very-long.md` | 100KB of content | Warn about verbosity |
| `code-only.md` | Just code blocks | Low clarity, recommend prose |

## Implementation Notes

### File Creation Guidelines

1. **Realistic**: Based on actual project patterns, not synthetic
2. **Varied**: Different project types, team sizes, languages
3. **Annotated**: Internal comments explaining design choices
4. **Versioned**: Track changes to golden files

### Score Validation Process

```python
def validate_golden_file(file_path: Path, expected_range: tuple[int, int]) -> bool:
    """
    Validate that a golden file scores within expected range.

    Run 3 times and check:
    - All runs within expected range
    - Variance < 5 points
    """
    scores = [analyze(file_path).overall for _ in range(3)]
    avg = sum(scores) / len(scores)
    variance = max(scores) - min(scores)

    return (
        expected_range[0] <= avg <= expected_range[1]
        and variance < 5
    )
```

### Maintenance

- Review quarterly for relevance
- Update when evaluation criteria change
- Archive deprecated patterns
- Add new patterns as discovered

## Acceptance Criteria

- [ ] All 26 golden files created
- [ ] Each file validated within expected score range
- [ ] Documentation includes rationale for each file
- [ ] Files organized in `benchmarks/` directory
- [ ] README with usage instructions

## Estimated Effort

- File creation: 4-6 hours
- Validation testing: 2-3 hours
- Documentation: 1-2 hours
- **Total: 7-11 hours**
