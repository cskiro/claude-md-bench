# Phase 1: Detailed Analysis Section

**Issue**: [#1](https://github.com/cskiro/claude-md-bench/issues/1)

## Goal

Display the detailed analysis text that the LLM generates but is currently not shown in the HTML report.

## Approach

Use native `<details>` element for built-in collapsible behavior with accessibility support.

## Tasks

- [ ] Update `reporter.py` to pass `detailed_analysis` to template context
- [ ] Add `<details>` section to `comparison.html` below strengths/weaknesses
- [ ] Style with existing dark theme colors
- [ ] Test collapse/expand behavior

## Implementation Details

### Template Structure

```html
<details class="detailed-analysis">
  <summary>Detailed Analysis</summary>
  <div class="analysis-content">
    {{ analysis.detailed_analysis }}
  </div>
</details>
```

### CSS Styling

```css
.detailed-analysis {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(45, 37, 32, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(205, 127, 107, 0.2);
}

.detailed-analysis summary {
  cursor: pointer;
  color: #cd7f6b;
  font-weight: 500;
}

.detailed-analysis summary:hover {
  color: #e8a090;
}

.analysis-content {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(205, 127, 107, 0.2);
  white-space: pre-wrap;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  line-height: 1.6;
}
```

## Acceptance Criteria

- [x] Detailed analysis renders in HTML report
- [ ] Styled consistently with dark theme
- [ ] Doesn't clutter UI when analysis is short
- [ ] Defaults to collapsed state

## Notes

- The `detailed_analysis` field already exists in the data model
- Just needs to be passed through and rendered
