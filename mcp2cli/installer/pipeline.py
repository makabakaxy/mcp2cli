"""Step pipeline runner for install/convert flows."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import click


@dataclass
class Step:
    """A single step in the install/convert pipeline."""

    name: str
    run: Callable[[], bool]
    retry_cmd: str
    depends_on: list[str] = field(default_factory=list)
    skip_if: list[str] = field(default_factory=list)
    fatal: bool = True  # Non-fatal steps don't affect overall success


@dataclass
class PipelineResult:
    """Result of a pipeline run."""

    results: dict[str, bool]
    fatal_steps: set[str]

    @property
    def all_ok(self) -> bool:
        """True if all fatal steps succeeded."""
        return all(
            ok for name, ok in self.results.items() if name in self.fatal_steps
        )

    @property
    def failed_fatal(self) -> list[str]:
        """Names of fatal steps that failed."""
        return [
            name for name, ok in self.results.items()
            if not ok and name in self.fatal_steps
        ]


def run_pipeline(pipeline: list[Step]) -> PipelineResult:
    """Execute a pipeline of steps with dependency/skip logic.

    Returns a PipelineResult with per-step outcomes and overall status.
    """
    results: dict[str, bool] = {}
    fatal_steps = {step.name for step in pipeline if step.fatal}

    for step in pipeline:
        # Dependency check: skip if any dependency failed
        if any(not results.get(dep) for dep in step.depends_on):
            failed_deps = [d for d in step.depends_on if not results.get(d)]
            click.echo(f"  Skipping {step.name}: dependency failed ({', '.join(failed_deps)})")
            results[step.name] = False
            continue

        # Conditional skip: if any skip_if step succeeded, skip this one
        if any(results.get(s) for s in step.skip_if):
            click.echo(f"  Skipping {step.name}: preset used")
            results[step.name] = True  # Mark as success so dependents can proceed
            continue

        try:
            ok = step.run()
        except Exception as e:
            click.echo(f"  {step.name} error: {e}", err=True)
            ok = False

        results[step.name] = ok

        if not ok:
            click.echo(f"  ⚠ {step.name} failed. Retry later: {step.retry_cmd}")

    return PipelineResult(results=results, fatal_steps=fatal_steps)
