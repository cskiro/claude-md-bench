# Phase 2: Drawer Component

**Issue**: [#2](https://github.com/cskiro/claude-md-bench/issues/2)

## Goal

Add a slide-out drawer that displays the actual CLAUDE.md content when clicking on Version A or Version B blocks.

## Approach

Custom implementation with Prism.js for syntax highlighting. No framework dependencies.

## Tasks

### Setup
- [ ] Add Prism.js CDN links to template (core + markdown + line-numbers)

### HTML Structure
- [ ] Add drawer panel with header, body, footer
- [ ] Add backdrop overlay element
- [ ] Add hidden content templates using `<script type="text/template">`
- [ ] Add trigger attributes to version blocks (`data-version`, `tabindex`, `role`)

### CSS
- [ ] Drawer positioning and transform animation
- [ ] Backdrop overlay styles
- [ ] Mobile responsive adjustments
- [ ] Match existing theme colors

### JavaScript
- [ ] Open/close state management
- [ ] Content loading from templates
- [ ] Focus trapping implementation
- [ ] Keyboard handling (Escape, Tab)
- [ ] Body scroll prevention
- [ ] Custom events for extensibility

### Reporter
- [ ] Pass `version_a.content` to template context
- [ ] Pass `version_b.content` to template context

## Implementation Details

### CDN Dependencies

```html
<!-- CSS -->
<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css" rel="stylesheet">
<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.css" rel="stylesheet">

<!-- JS (end of body) -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-markdown.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/line-numbers/prism-line-numbers.min.js"></script>
```

### HTML Structure

```html
<!-- Drawer Panel -->
<div id="drawer-panel"
     class="drawer"
     role="dialog"
     aria-modal="true"
     aria-labelledby="drawer-title"
     aria-hidden="true"
     tabindex="-1">

  <div class="drawer-header">
    <h2 id="drawer-title" class="drawer-title">Version A</h2>
    <button class="drawer-close" aria-label="Close panel">×</button>
  </div>

  <div class="drawer-body">
    <pre class="line-numbers"><code id="drawer-content" class="language-markdown"></code></pre>
  </div>

  <div class="drawer-footer">
    <span class="line-count">0 lines</span>
  </div>
</div>

<!-- Backdrop -->
<div id="drawer-backdrop" class="drawer-backdrop"></div>

<!-- Content Templates -->
<script type="text/template" id="version-a-content">{{ version_a.content | e }}</script>
<script type="text/template" id="version-b-content">{{ version_b.content | e }}</script>
```

### Version Block Triggers

```html
<div class="version-block"
     data-drawer-trigger
     data-version="A"
     tabindex="0"
     role="button"
     aria-label="View Version A content">
```

### JavaScript Architecture

See [ADR-001](../../adr/001-html-dashboard-drawer.md#javascript-structure) for the full SOLID-structured implementation.

Key components:
- State management (open/close, current version)
- Content loading with Prism highlighting
- Focus trapping with Tab key cycling
- Custom events (`drawer:open`, `drawer:close`)
- Public API (`window.DrawerPanel`)

## Acceptance Criteria

- [ ] Clicking version block opens drawer from right side
- [ ] Drawer shows full CLAUDE.md content with syntax highlighting
- [ ] Drawer can be closed by clicking outside or close button
- [ ] Content is scrollable within drawer
- [ ] Styled consistently with dark theme
- [ ] Keyboard accessible (Tab, Escape, Enter/Space)
- [ ] Screen reader announces dialog role

## Future Enhancement

Once complete, the next iteration will add diff-style highlighting:
- Green lines for strengths
- Red/yellow lines for weaknesses
- Line references from LLM analysis

The architecture supports this via:
- Custom events for hooking into open/close
- Line-numbers plugin for targeting specific lines
- Public API for extensions
