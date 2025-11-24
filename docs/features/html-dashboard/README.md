# HTML Dashboard Enhancements

Feature branch: `feature/html-report-enhancements`

## Overview

Enhance the HTML comparison report with detailed analysis display and interactive drawer component for viewing source CLAUDE.md content.

## Issues

- [#1](https://github.com/cskiro/claude-md-bench/issues/1) - Add detailed analysis section to HTML report
- [#2](https://github.com/cskiro/claude-md-bench/issues/2) - Add drawer component to view CLAUDE.md content

## Phases

| Phase | Description | Status |
|-------|-------------|--------|
| [Phase 1](./phase-1-detailed-analysis.md) | Detailed analysis section | Not Started |
| [Phase 2](./phase-2-drawer-component.md) | Drawer component | Not Started |

## Files Changed

- `src/claude_md_bench/core/reporter.py`
- `src/claude_md_bench/templates/comparison.html`

## Architecture

See [ADR-001](../../adr/001-html-dashboard-drawer.md) for technical decisions and rationale.

## Testing Checklist

- [ ] Detailed analysis renders and collapses correctly
- [ ] Drawer opens/closes on version block click
- [ ] Keyboard navigation works (Tab cycling, Escape to close)
- [ ] Screen reader announces dialog properly
- [ ] Mobile viewport displays correctly
- [ ] Syntax highlighting applies to markdown content
