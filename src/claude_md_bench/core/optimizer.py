"""
CLAUDE.md Optimizer

Uses meta-prompting to iteratively improve CLAUDE.md files based on evaluation feedback.
Inspired by Arize prompt learning research.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from claude_md_bench.core.analyzer import AnalysisResult, ClaudeMDAnalyzer
from claude_md_bench.llm.ollama import OllamaClient

logger = logging.getLogger(__name__)


@dataclass
class OptimizationIteration:
    """Result of a single optimization iteration."""

    iteration: int
    score: float
    previous_score: float
    delta: float
    content: str
    analysis: AnalysisResult


@dataclass
class OptimizationResult:
    """Result of the full optimization process."""

    original_score: float
    final_score: float
    total_improvement: float
    iterations: list[OptimizationIteration] = field(default_factory=list)
    original_content: str = ""
    final_content: str = ""
    output_path: Path | None = None


class MetaPrompter:
    """Generates improved CLAUDE.md using meta-prompting."""

    def __init__(self, ollama_client: OllamaClient) -> None:
        """
        Initialize meta-prompter.

        Args:
            ollama_client: Ollama client for LLM inference
        """
        self.ollama = ollama_client

    def improve(
        self,
        current_content: str,
        analysis: AnalysisResult,
        iteration: int = 1,
    ) -> str:
        """
        Generate improved CLAUDE.md based on evaluation feedback.

        Args:
            current_content: Current CLAUDE.md content
            analysis: Analysis result with scores and feedback
            iteration: Current iteration number

        Returns:
            Improved CLAUDE.md content
        """
        logger.info(f"Generating improved CLAUDE.md (iteration {iteration})")

        prompt = self._build_meta_prompt(current_content, analysis, iteration)

        try:
            raw_output = self.ollama.generate(
                prompt=prompt,
                system=self._get_system_prompt(),
                temperature=0.5,
            )

            improved_md = self._extract_clean_claude_md(raw_output)
            logger.info(f"Generated improved CLAUDE.md ({len(improved_md)} chars)")
            return improved_md

        except Exception as e:
            logger.error(f"Meta-prompting failed: {e}")
            raise

    def _get_system_prompt(self) -> str:
        """Get system prompt for meta-prompting."""
        return """You are an expert at optimizing CLAUDE.md files for AI coding assistants.

CRITICAL OUTPUT RULES:
- Output ONLY the complete, improved CLAUDE.md file content
- Start your response with the marker: <<<BEGIN_CLAUDE_MD>>>
- Then immediately output the CLAUDE.md content starting with "# CLAUDE.md"
- End your response with the marker: <<<END_CLAUDE_MD>>>
- Do NOT include any explanations, commentary, or meta-text outside the markers
- Do NOT say "Here's the improved version" or similar phrases
- Output the raw markdown file ready to save between the markers

Your task: Improve the CLAUDE.md file by:
1. Preserving all working guidance (keep what's good)
2. Strengthening areas that scored poorly in the evaluation
3. Adding concrete examples where needed
4. Maintaining the original structure and organization
5. Keeping it actionable and specific

EXAMPLE OUTPUT FORMAT:
<<<BEGIN_CLAUDE_MD>>>
# CLAUDE.md

## Project Overview
[Your improved content here]
<<<END_CLAUDE_MD>>>"""

    def _build_meta_prompt(
        self,
        content: str,
        analysis: AnalysisResult,
        iteration: int,
    ) -> str:
        """Build meta-prompt for improvement."""
        # Format dimension scores
        dim_scores_text = "\n".join(
            f"  - {dim}: {score:.0f}/100"
            for dim, score in analysis.dimension_scores.items()
            if dim != "overall"
        )

        # Format weaknesses
        weaknesses_text = "\n".join(f"  - {w}" for w in analysis.weaknesses)

        # Format recommendations
        recommendations_text = "\n".join(f"  - {r}" for r in analysis.recommendations)

        # Truncate if too long
        max_chars = 15000
        truncated = content[:max_chars]
        truncated_notice = ""
        if len(content) > max_chars:
            truncated_notice = f"\n\n[Note: Full file is {len(content)} chars. Showing first {max_chars} for context.]\n"

        return f"""# CLAUDE.md Improvement Task (Iteration {iteration})

## Current CLAUDE.md
```markdown
{truncated}
```{truncated_notice}

## Current Performance
**Overall Score**: {analysis.score:.1f}/100

**Dimension Scores**:
{dim_scores_text if dim_scores_text else "  No dimension scores available"}

## Issues Identified

**Weaknesses**:
{weaknesses_text if weaknesses_text else "  No specific weaknesses identified"}

**Recommendations**:
{recommendations_text if recommendations_text else "  No specific recommendations"}

## Your Task

Improve this CLAUDE.md file to address the weaknesses and recommendations above.

**Focus Areas** (prioritize low-scoring dimensions):
1. If Clarity is low: Make instructions more explicit and specific
2. If Completeness is low: Add missing essential sections
3. If Actionability is low: Add concrete examples and commands
4. If Standards is low: Strengthen TDD, type safety, quality check requirements
5. If Context is low: Add more project structure and architecture info

**CRITICAL: Preservation Requirements**:
- **PRESERVE ALL WORKING CONTENT**: Do NOT remove sections that aren't mentioned in weaknesses
- **MAINTAIN OR INCREASE LENGTH**: Don't over-simplify
- **KEEP ALL SECTIONS**: Preserve existing structure
- **ADD, DON'T REPLACE**: Strengthen weak areas by adding, not removing
- **TARGET ADDITIONS**: Only modify sections related to identified weaknesses

**Output Format**:
Provide ONLY the improved CLAUDE.md content between the markers.
Do not include explanations or commentary.
"""

    def _extract_clean_claude_md(self, raw_output: str) -> str:
        """
        Extract clean CLAUDE.md content from LLM output.

        Args:
            raw_output: Raw LLM response

        Returns:
            Clean CLAUDE.md content
        """
        # Strategy 1: Extract between markers
        begin_marker = "<<<BEGIN_CLAUDE_MD>>>"
        end_marker = "<<<END_CLAUDE_MD>>>"

        if begin_marker in raw_output and end_marker in raw_output:
            start_idx = raw_output.index(begin_marker) + len(begin_marker)
            end_idx = raw_output.index(end_marker)
            content = raw_output[start_idx:end_idx].strip()
            logger.debug("Extracted CLAUDE.md using markers")
            return content

        # Strategy 2: Find markdown header patterns
        patterns = [
            "# CLAUDE.md\n",
            "# Project Overview\n",
            "# Overview\n",
            "# Development",
        ]

        for pattern in patterns:
            if pattern in raw_output:
                idx = raw_output.index(pattern)
                content = raw_output[idx:].strip()
                logger.warning(f"Extracted CLAUDE.md using pattern: {pattern.strip()}")
                return content

        # Strategy 3: Remove meta-text patterns
        lines = raw_output.split("\n")
        skip_patterns = [
            "# CLAUDE.md Improvement Task",
            "## Current CLAUDE.md",
            "## Current Performance",
            "## Issues Identified",
            "## Your Task",
            "I can help",
            "Here is a revised version",
            "Here's the improved version",
            "Based on the provided",
            "**Improvement Plan**",
        ]

        start_line_idx = 0
        for i, line in enumerate(lines):
            line_stripped = line.strip()

            if not line_stripped:
                continue

            if any(skip.lower() in line.lower() for skip in skip_patterns):
                continue

            if line_stripped.startswith("#") and not any(
                skip.lower() in line.lower() for skip in skip_patterns
            ):
                start_line_idx = i
                break

        if start_line_idx > 0:
            content = "\n".join(lines[start_line_idx:]).strip()
            logger.warning(f"Extracted CLAUDE.md by skipping {start_line_idx} meta-text lines")
            return content

        # Strategy 4: Return as-is
        logger.error("Could not extract clean CLAUDE.md - returning raw output")
        return raw_output.strip()


class ClaudeMDOptimizer:
    """Orchestrates the CLAUDE.md optimization loop."""

    def __init__(self, ollama_client: OllamaClient) -> None:
        """
        Initialize optimizer.

        Args:
            ollama_client: Ollama client for evaluation and generation
        """
        self.ollama = ollama_client
        self.analyzer = ClaudeMDAnalyzer(ollama_client)
        self.meta_prompter = MetaPrompter(ollama_client)

    def optimize(
        self,
        claude_md_path: Path,
        iterations: int = 3,
        output_path: Path | None = None,
    ) -> OptimizationResult:
        """
        Run optimization loop to improve CLAUDE.md.

        Args:
            claude_md_path: Path to CLAUDE.md file
            iterations: Number of optimization iterations
            output_path: Path to save optimized file (default: alongside original)

        Returns:
            OptimizationResult with all iterations and final content
        """
        logger.info(f"Starting optimization of {claude_md_path} ({iterations} iterations)")

        # Read original content
        original_content = claude_md_path.read_text(encoding="utf-8")
        project_name = claude_md_path.parent.name

        # Initial evaluation
        logger.info("Evaluating baseline CLAUDE.md...")
        baseline_analysis = self.analyzer.analyze(claude_md_path, project_name)
        original_score = baseline_analysis.score

        logger.info(f"Baseline score: {original_score:.1f}/100")

        # Track iterations
        result = OptimizationResult(
            original_score=original_score,
            final_score=original_score,
            total_improvement=0.0,
            original_content=original_content,
            final_content=original_content,
        )

        current_content = original_content
        current_score = original_score
        current_analysis = baseline_analysis

        # Optimization loop
        for i in range(1, iterations + 1):
            logger.info(f"\n--- Iteration {i}/{iterations} ---")

            # Generate improved version
            improved_content = self.meta_prompter.improve(
                current_content=current_content,
                analysis=current_analysis,
                iteration=i,
            )

            # Save to temp file for analysis
            temp_path = claude_md_path.parent / f".claude_md_temp_iter_{i}.md"
            temp_path.write_text(improved_content, encoding="utf-8")

            # Evaluate improved version
            improved_analysis = self.analyzer.analyze(temp_path, f"{project_name} (iter {i})")
            improved_score = improved_analysis.score

            # Calculate delta
            delta = improved_score - current_score

            logger.info(f"Iteration {i}: {current_score:.1f} -> {improved_score:.1f} ({delta:+.1f})")

            # Record iteration
            iteration_result = OptimizationIteration(
                iteration=i,
                score=improved_score,
                previous_score=current_score,
                delta=delta,
                content=improved_content,
                analysis=improved_analysis,
            )
            result.iterations.append(iteration_result)

            # Update for next iteration (always use latest, even if score dropped)
            # This allows recovery from local minima
            current_content = improved_content
            current_score = improved_score
            current_analysis = improved_analysis

            # Clean up temp file
            temp_path.unlink(missing_ok=True)

        # Determine best version (highest score across all iterations)
        best_iteration = max(result.iterations, key=lambda x: x.score)
        result.final_score = best_iteration.score
        result.final_content = best_iteration.content
        result.total_improvement = result.final_score - result.original_score

        # Save optimized file
        if output_path is None:
            output_path = claude_md_path.parent / "CLAUDE.optimized.md"

        output_path.write_text(result.final_content, encoding="utf-8")
        result.output_path = output_path

        logger.info(f"\nOptimization complete!")
        logger.info(f"Original: {result.original_score:.1f}/100")
        logger.info(f"Final: {result.final_score:.1f}/100")
        logger.info(f"Improvement: {result.total_improvement:+.1f} points")
        logger.info(f"Saved to: {output_path}")

        return result
