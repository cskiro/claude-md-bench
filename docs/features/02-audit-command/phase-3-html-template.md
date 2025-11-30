# Phase 3: HTML Template

**Issue**: [#4](https://github.com/cskiro/claude-md-bench/issues/4)

## Goal

Create HTML template for audit reports matching existing dark theme and design patterns.

## Tasks

- [ ] Create `src/claude_md_bench/templates/audit.html`
- [ ] Include overall score with visual indicator
- [ ] Add dimension scores as horizontal bar chart
- [ ] Display strengths/weaknesses/recommendations
- [ ] Add collapsible detailed analysis section
- [ ] Ensure accessibility (ARIA, keyboard navigation)

## Implementation Details

### Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CLAUDE.md Audit - {{ file_name }}</title>
    <!-- Styles matching comparison.html theme -->
</head>
<body>
    <div class="container">
        <header>
            <h1>CLAUDE.md Audit Report</h1>
            <p class="file-path">{{ file_path }}</p>
            <p class="generated">Generated: {{ generated_at }}</p>
        </header>

        <section class="score-section">
            <div class="overall-score">
                <span class="score-value">{{ "%.1f"|format(score) }}</span>
                <span class="score-label">/10</span>
            </div>
            <div class="score-bar">
                <div class="score-fill" style="width: {{ score * 10 }}%"></div>
            </div>
        </section>

        <section class="dimensions">
            <h2>Dimension Scores</h2>
            {% for dim, value in dimension_scores.items() %}
            <div class="dimension-row">
                <span class="dim-name">{{ dim }}</span>
                <div class="dim-bar">
                    <div class="dim-fill" style="width: {{ value * 10 }}%"></div>
                </div>
                <span class="dim-value">{{ "%.1f"|format(value) }}</span>
            </div>
            {% endfor %}
        </section>

        <section class="analysis">
            <div class="strengths">
                <h3>Strengths</h3>
                <ul>
                {% for item in strengths %}
                    <li>{{ item }}</li>
                {% endfor %}
                </ul>
            </div>

            <div class="weaknesses">
                <h3>Weaknesses</h3>
                <ul>
                {% for item in weaknesses %}
                    <li>{{ item }}</li>
                {% endfor %}
                </ul>
            </div>

            <div class="recommendations">
                <h3>Recommendations</h3>
                <ul>
                {% for item in recommendations %}
                    <li>{{ item }}</li>
                {% endfor %}
                </ul>
            </div>
        </section>

        <details class="detailed-analysis">
            <summary>Detailed Analysis</summary>
            <div class="analysis-content">{{ detailed_analysis }}</div>
        </details>
    </div>
</body>
</html>
```

### CSS Styling

Match existing theme:
- Background: #DA7756 (coral)
- Container background: #2d2520 (dark brown)
- Accent colors: #cd7f6b, #e8a090
- Font: JetBrains Mono
- Border radius: 8px

### Accessibility

- Semantic HTML structure
- Proper heading hierarchy
- Color contrast ratios meeting WCAG 2.1 AA
- `<details>` for native collapse/expand with keyboard support

## Acceptance Criteria

- [ ] Template renders without errors
- [ ] Scores display with appropriate color coding
- [ ] Bar charts accurately represent scores
- [ ] Theme matches existing comparison.html
- [ ] Detailed analysis collapsible section works
- [ ] Mobile responsive layout
- [ ] Accessible with screen readers

## Notes

- Simpler than comparison.html (no A/B sections)
- Reuse CSS patterns from existing template
- File size ~300-400 lines (vs 748 for comparison)
