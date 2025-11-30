# Development Standards Quick Reference

This document provides a quick reference for development standards.
For complete details, see the project [CLAUDE.md](../../CLAUDE.md).

## Code Style

- **Type hints**: Required on all functions (TypeScript-style)
- **No `any` types**: Use explicit types
- **No `var`**: Use `const`/`let` (or Python equivalents)
- **No loose equality**: Use `===`/`!==` (or Python `is`/`==`)
- **Logging**: Use `logging` module, no `print()` statements

## Testing (Testing Trophy)

| Type | Coverage | Focus |
|------|----------|-------|
| Integration | 70% | User workflows, API contracts |
| Unit | 20% | Business logic, edge cases |
| E2E | 10% | Critical paths |

**Minimum coverage**: 65% (POC), increase as codebase matures

**Test naming**: `test_should_[behavior]_when_[condition]`

**Query priority**: `getByRole()` > `getByLabelText()` > `getByText()` > `getByTestId()`

## Git Conventions

**Commits**: Conventional format

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code restructuring
- `test:` - Test additions/changes
- `chore:` - Maintenance

**Branches**: `feature/`, `bugfix/`, `chore/` + component name

**Commit frequency**: Often (small, incremental)

## Constants and Utilities

**Single source of truth**: Define constants once, import everywhere

- Dimensions: `core/reporting_constants.py`
- Score thresholds: `core/reporting_constants.py`

**Utility functions**: Extract when used 3+ times

## Architecture (Three-Layer)

```
CLI Layer (cli.py, commands/)
    ↓
Core Layer (core/) - Business logic
    ↓
LLM Layer (llm/) - External integrations
```

## References

- Full standards: [CLAUDE.md](../../CLAUDE.md)
- Testing details: CLAUDE.md § Testing Standards
- Git workflow: CLAUDE.md § Git Standards
