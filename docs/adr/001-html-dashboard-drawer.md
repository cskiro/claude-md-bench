# Architecture Decisions

## ADR-001: Custom Drawer vs Library

**Decision**: Build custom drawer implementation

**Context**: Need a slide-out panel to display CLAUDE.md content

**Options Considered**:
1. Micromodal.js (1.9kb) - Accessible, but modal-focused
2. HystModal (3kb) - WAI-ARIA support
3. Custom implementation (~2kb)

**Rationale**:
- Drawer pattern is simple enough that library adds unnecessary overhead
- Need full control for future diff highlighting feature
- Specialized content rendering (markdown with syntax highlighting)
- Estimated custom code is similar size to smallest library

---

## ADR-002: Syntax Highlighting Library

**Decision**: Prism.js via CDN

**Context**: Need to highlight markdown content in drawer

**Options Considered**:
1. Prism.js - 2kb core + ~500b per language
2. highlight.js - 1.6MB for 34 languages
3. No highlighting - just monospace

**Rationale**:
- Only need markdown highlighting (one language)
- Prism is modular and lightweight
- Line-numbers plugin available for future diff feature
- CDN avoids build complexity
- Tomorrow theme matches dark aesthetic

**Bundle Impact**: ~3.5kb gzipped

---

## ADR-003: Content Storage Strategy

**Decision**: Embed in HTML using `<script type="text/template">`

**Context**: Need to display file content when drawer opens

**Options Considered**:
1. Data attributes on trigger elements
2. Inline `<script type="text/template">`
3. Fetch from server/file

**Rationale**:
- No fetch latency
- Works offline
- Cleaner than data attributes (no escaping issues)
- Content already available during Jinja2 rendering

---

## ADR-004: Animation Approach

**Decision**: CSS transforms with `will-change` hint

**Context**: Need smooth slide-in animation for drawer

**Options Considered**:
1. `transform: translateX()` - GPU accelerated
2. `left/right` positioning - Triggers layout

**Rationale**:
- Transform-based animations don't trigger layout recalculation
- Significantly smoother on mobile devices
- Industry standard (GitHub, GitLab use this approach)

---

## ADR-005: Accessibility Implementation

**Decision**: Full ARIA support with focus trapping

**Requirements**:
- `role="dialog"` and `aria-modal="true"`
- `aria-labelledby` pointing to title
- Focus moves to drawer on open
- Tab cycles within drawer only
- Escape closes drawer
- Focus returns to trigger on close

**Rationale**:
- WCAG 2.1 AA compliance
- Screen reader users need proper announcements
- Keyboard-only users need full functionality

---

## JavaScript Structure

Following SOLID principles for maintainability and extensibility.

### Module Organization

```javascript
// Single Responsibility - each concern is separate
const DrawerController = { open, close, toggle };
const FocusManager = { trap, release, returnFocus };
const ContentLoader = { loadContent, clearContent };
const KeyboardHandler = { handleEscape, handleTab };
```

### State Management

```javascript
let state = {
  isOpen: false,
  previouslyFocused: null,
  currentVersion: null
};
```

### Event-Based Extensibility

Custom events allow future features without modifying core:

```javascript
// Core drawer dispatches events
drawer.dispatchEvent(new CustomEvent('drawer:open', { detail: { version } }));

// Future diff extension listens
window.DrawerPanel.on('open', (e) => {
  if (e.detail.showDiff) {
    applyDiffHighlighting();
  }
});
```

### Public API

Expose minimal API for extensions:

```javascript
window.DrawerPanel = {
  open(version) { ... },
  close() { ... },
  on(event, callback) { ... }
};
```

---

## CSS Architecture

### Theme Variables (matches existing)

```css
:root {
  --bg-primary: #1a1816;
  --bg-secondary: #2d2520;
  --text-primary: #e8e6e3;
  --text-secondary: #b0ada8;
  --accent-coral: #cd7f6b;
  --accent-teal: #6eb5a8;
}
```

### Animation Performance

```css
.drawer {
  transform: translateX(100%);
  transition: transform 0.3s ease-out;
  will-change: transform;
  contain: layout style paint;
}
```

### Mobile Responsiveness

```css
@media (max-width: 768px) {
  .drawer {
    width: 100vw;
  }
}
```

---

## Future Diff Highlighting

The architecture is designed to support this without modifying the core drawer:

### CSS Classes

```css
.line-added {
  background: rgba(110, 181, 168, 0.2);
  border-left: 3px solid var(--accent-teal);
}

.line-removed {
  background: rgba(205, 127, 107, 0.2);
  border-left: 3px solid var(--accent-coral);
}
```

### Extension Pattern

```javascript
// diff-extension.js
window.DrawerPanel.on('open', (e) => {
  const lines = document.querySelectorAll('.line-numbers-rows > span');
  diffData.forEach((change, index) => {
    lines[index].classList.add(`line-${change.type}`);
  });
});
```

This keeps the core drawer simple while allowing rich extensions.
