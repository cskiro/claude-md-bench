"""Shared constants and utilities for reporting.

This module provides a single source of truth for report-related constants
and utility functions used across the reporting system.
"""

from __future__ import annotations

from datetime import datetime
from typing import Final

# Score thresholds for color coding
SCORE_HIGH_THRESHOLD: Final[int] = 70
SCORE_MEDIUM_THRESHOLD: Final[int] = 50

# Dimension list - single source of truth for evaluation dimensions
DIMENSIONS: Final[tuple[str, ...]] = (
    "clarity",
    "completeness",
    "actionability",
    "standards",
    "context",
)


def get_score_style(score: float) -> str:
    """Return Rich style string based on score threshold.

    Args:
        score: The score value (0-100)

    Returns:
        Rich color string: "green", "yellow", or "red"
    """
    if score >= SCORE_HIGH_THRESHOLD:
        return "green"
    elif score >= SCORE_MEDIUM_THRESHOLD:
        return "yellow"
    return "red"


def get_score_css_class(score: float) -> str:
    """Return CSS class based on score threshold.

    Args:
        score: The score value (0-100)

    Returns:
        CSS class string: "score-high", "score-medium", or "score-low"
    """
    if score >= SCORE_HIGH_THRESHOLD:
        return "score-high"
    elif score >= SCORE_MEDIUM_THRESHOLD:
        return "score-medium"
    return "score-low"


def get_delta_style(delta: float) -> str:
    """Return Rich style string for score delta.

    Args:
        delta: The score difference (can be negative)

    Returns:
        Rich color string: "green" (positive), "red" (negative), or "white" (zero)
    """
    if delta > 0:
        return "green"
    elif delta < 0:
        return "red"
    return "white"


def generate_report_filename(prefix: str, name: str, extension: str) -> str:
    """Generate timestamped filename with sanitized name.

    Args:
        prefix: Report type prefix (e.g., "audit", "comparison")
        name: File or project name to include
        extension: File extension without dot (e.g., "txt", "html")

    Returns:
        Formatted filename like "audit_project-name_20241130_143022.txt"
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = name.replace("/", "_").replace("\\", "_")
    return f"{prefix}_{safe_name}_{timestamp}.{extension}"


def generate_comparison_filename(
    prefix: str,
    name_a: str,
    name_b: str,
    extension: str,
) -> str:
    """Generate timestamped filename for comparison reports.

    Args:
        prefix: Report type prefix (e.g., "comparison")
        name_a: First file/project name
        name_b: Second file/project name
        extension: File extension without dot

    Returns:
        Formatted filename like "comparison_file1_vs_file2_20241130_143022.txt"
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name_a = name_a.replace("/", "_").replace("\\", "_")
    safe_name_b = name_b.replace("/", "_").replace("\\", "_")
    return f"{prefix}_{safe_name_a}_vs_{safe_name_b}_{timestamp}.{extension}"
