# Benchmark Suite for CLAUDE.md Optimization

## Overview

A comprehensive benchmark suite for validating CLAUDE.md analysis and optimization quality. Enables scientific measurement of improvements and regression detection.

## Phases

| Phase | Description | Status |
|-------|-------------|--------|
| [Phase 1](./phase-1-golden-files.md) | Golden test files with known quality | Not Started |
| [Phase 2](./phase-2-benchmark-runner.md) | Automated benchmark runner | Not Started |
| [Phase 3](./phase-3-metrics-tracking.md) | Metrics collection and visualization | Not Started |
| [Phase 4](./phase-4-meta-learning.md) | Pattern analysis and model training | Not Started |

## Directory Structure

```
benchmarks/
├── golden/
│   ├── excellent/           # 90+ scores
│   │   ├── complete-project.md
│   │   └── well-structured.md
│   ├── good/                # 70-89 scores
│   │   ├── missing-context.md
│   │   └── sparse-examples.md
│   ├── mediocre/            # 50-69 scores
│   │   ├── vague-instructions.md
│   │   └── inconsistent-style.md
│   └── poor/                # <50 scores
│       ├── minimal.md
│       └── disorganized.md
├── domains/
│   ├── python-cli/
│   ├── typescript-lib/
│   ├── react-app/
│   ├── monorepo/
│   └── api-service/
├── dimensions/
│   ├── high-clarity-low-completeness.md
│   ├── high-actionability-low-standards.md
│   └── ...
├── edge-cases/
│   ├── empty.md
│   ├── single-line.md
│   ├── very-long.md
│   └── code-only.md
└── optimization-pairs/
    ├── case-001/
    │   ├── before.md
    │   └── after.md
    └── ...
```

## Test Categories

### 1. Quality Level Tests
Verify analyzer assigns appropriate scores to files of known quality.

**Acceptance Criteria:**
- Excellent files score 90+ on overall
- Good files score 70-89
- Mediocre files score 50-69
- Poor files score below 50
- Consistency: repeated runs within ±5 points

### 2. Dimension-Specific Tests
Verify analyzer correctly identifies strengths/weaknesses in specific dimensions.

**Acceptance Criteria:**
- Files designed to be weak in dimension X score lower on X
- Dimensional weaknesses appear in weaknesses list
- Recommendations address the weak dimension

### 3. Optimization Validation Tests
Verify optimizer improves files without degradation.

**Acceptance Criteria:**
- Score improvement ≥5 points for mediocre files
- Score improvement ≥10 points for poor files
- Good files not degraded (score stays within ±3 points)
- Excellent files not degraded

### 4. Edge Case Tests
Verify graceful handling of unusual inputs.

**Acceptance Criteria:**
- Empty file: returns error or minimal score with recommendation
- Single line: analyzes without crash
- Very long: handles within timeout, warns if too verbose
- Code-only: identifies lack of prose instructions

### 5. Domain-Specific Tests
Verify appropriate evaluation across project types.

**Acceptance Criteria:**
- Python projects: recognizes pytest, pip, venv patterns
- TypeScript: recognizes npm, tsc, ESLint patterns
- React: recognizes component patterns, testing-library
- Each domain has appropriate recommendations

## Benchmark Runner Design

```python
# benchmarks/runner.py
@dataclass
class BenchmarkResult:
    file_path: Path
    expected_range: tuple[int, int]
    actual_score: float
    passed: bool
    dimensions: dict[str, int]
    run_time_ms: int

def run_benchmark_suite() -> BenchmarkReport:
    """Run all benchmark tests and generate report."""
    ...

def run_single_benchmark(file_path: Path, expected: tuple[int, int]) -> BenchmarkResult:
    """Run benchmark on single file."""
    ...
```

## Metrics to Track

### Per-Run Metrics
- Overall score accuracy (within expected range)
- Dimension score consistency
- Analysis time (ms)
- Token usage

### Over-Time Metrics
- Score variance across runs (should be low)
- Optimization improvement rate
- Model performance comparison (llama3.2 vs qwen2.5)
- Cost per analysis

## Meta-Learning Goals

### Short-Term (v0.3)
1. Identify patterns in high-scoring CLAUDE.md files
2. Build heuristic scorer (no LLM calls)
3. Track which prompts produce best optimizations

### Medium-Term (v0.4)
1. Train lightweight classifier for quick pre-screening
2. A/B test optimization strategies
3. Build recommendation engine based on common weaknesses

### Long-Term (v0.5+)
1. Fine-tune small model on CLAUDE.md evaluation
2. Automated CLAUDE.md generation for new projects
3. Integration with CI/CD for quality gates

## Success Criteria for Benchmark Suite

1. **Coverage**: At least 30 golden files across all categories
2. **Reliability**: 95%+ tests pass on repeated runs
3. **Speed**: Full suite completes in <5 minutes
4. **Actionable**: Failed tests clearly indicate what broke
5. **Maintainable**: Easy to add new test cases

## Integration Points

- **CI/CD**: Run benchmarks on PR to prevent regressions
- **Dashboard**: Visualize benchmark trends over time
- **Alerts**: Notify on significant score degradation
- **Docs**: Generate benchmark report for releases
