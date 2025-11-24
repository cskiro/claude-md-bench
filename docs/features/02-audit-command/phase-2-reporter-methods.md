# Phase 2: Reporter Audit Methods

**Issue**: [#4](https://github.com/cskiro/claude-md-bench/issues/4)

## Goal

Add methods to Reporter class for displaying and saving audit results for a single file.

## Tasks

- [ ] Add `print_audit(result: AnalysisResult, file_path: Path)` method
- [ ] Add `save_audit_text_report(result: AnalysisResult, file_path: Path) -> Path` method
- [ ] Add `save_audit_html_report(result: AnalysisResult, file_path: Path) -> Path | None` method
- [ ] Update audit command to use new Reporter methods

## Implementation Details

### print_audit() Method

Display audit results to console using Rich:

```python
def print_audit(self, result: AnalysisResult, file_path: Path) -> None:
    """Print audit results to console."""
    # Header with file info
    self.console.print(Panel(f"[bold]Audit: {file_path.name}[/bold]"))

    # Overall score
    score_color = "green" if result.score >= 7 else "yellow" if result.score >= 5 else "red"
    self.console.print(f"Overall Score: [{score_color}]{result.score:.1f}/10[/{score_color}]")

    # Dimension scores table
    table = Table(title="Dimension Scores")
    table.add_column("Dimension")
    table.add_column("Score", justify="right")
    for dim, score in result.dimension_scores.items():
        table.add_row(dim, f"{score:.1f}")
    self.console.print(table)

    # Strengths/Weaknesses/Recommendations as lists
```

### save_audit_text_report() Method

```python
def save_audit_text_report(self, result: AnalysisResult, file_path: Path) -> Path:
    """Save audit results as text report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_name = f"audit_{file_path.stem}_{timestamp}.txt"
    report_path = self.output_dir / report_name

    # Write formatted text similar to console output
    return report_path
```

### save_audit_html_report() Method

```python
def save_audit_html_report(self, result: AnalysisResult, file_path: Path) -> Path | None:
    """Save audit results as HTML report."""
    template = self._get_template("audit.html")
    if not template:
        return None

    context = {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "score": result.score,
        "dimension_scores": result.dimension_scores,
        "strengths": result.strengths,
        "weaknesses": result.weaknesses,
        "recommendations": result.recommendations,
        "detailed_analysis": result.detailed_analysis,
        "file_size": result.file_size,
        "generated_at": datetime.now().isoformat(),
    }

    # Render and save
    return report_path
```

## Acceptance Criteria

- [ ] Console output is formatted and colored appropriately
- [ ] Text report includes all analysis data
- [ ] HTML report renders correctly (depends on Phase 3 template)
- [ ] Report paths follow naming convention: `audit_{filename}_{timestamp}.{ext}`
- [ ] Methods handle missing template gracefully

## Notes

- Keep method signatures consistent with existing comparison methods
- Reuse `_get_template()` helper from existing Reporter code
