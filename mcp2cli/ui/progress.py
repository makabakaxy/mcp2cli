"""Spinner + LLM-summarized progress display during long LLM calls."""

from __future__ import annotations

import sys
import threading
from typing import TYPE_CHECKING

import click

if TYPE_CHECKING:
    from mcp2cli.generator.llm_backend import LLMBackend

SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
SUMMARIZE_INTERVAL = 10.0  # seconds


class LLMProgressDisplay:
    """Shows a spinner with periodically LLM-summarized progress.

    Two background threads:
    - spinner thread: refreshes the animation every 0.12s
    - summarizer thread: every SUMMARIZE_INTERVAL seconds, sends accumulated
      partial output to the default LLM for a one-line summary

    Thread safety: ``_lock`` protects ``_partial_output`` and ``_message``.
    Non-TTY fallback: prints each summary as a new line instead of overwriting.
    Error isolation: summarizer failures are silently ignored.
    """

    def __init__(
        self,
        backend: LLMBackend,
        initial_message: str,
        interval: float = SUMMARIZE_INTERVAL,
    ):
        self._backend = backend
        self._message = initial_message
        self._interval = interval
        self._partial_output = ""
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._spinner_thread: threading.Thread | None = None
        self._summarize_thread: threading.Thread | None = None
        self._is_tty = hasattr(sys.stderr, "isatty") and sys.stderr.isatty()
        self._last_line_len = 0

    def start(self) -> None:
        """Start the spinner and summarizer background threads."""
        self._stop_event.clear()
        if self._is_tty:
            self._spinner_thread = threading.Thread(
                target=self._spin_loop, daemon=True,
            )
            self._spinner_thread.start()
        self._summarize_thread = threading.Thread(
            target=self._summarize_loop, daemon=True,
        )
        self._summarize_thread.start()

    def stop(self) -> None:
        """Stop all background threads and clear the spinner line."""
        self._stop_event.set()
        if self._spinner_thread:
            self._spinner_thread.join(timeout=2)
        if self._summarize_thread:
            self._summarize_thread.join(timeout=2)
        # Clear the spinner line
        if self._is_tty and self._last_line_len > 0:
            sys.stderr.write("\r" + " " * self._last_line_len + "\r")
            sys.stderr.flush()

    def update_partial(self, text: str) -> None:
        """Called by the streaming reader to update the partial output buffer."""
        with self._lock:
            self._partial_output = text

    # ------------------------------------------------------------------
    # Internal loops
    # ------------------------------------------------------------------

    def _spin_loop(self) -> None:
        idx = 0
        while not self._stop_event.is_set():
            frame = SPINNER_FRAMES[idx % len(SPINNER_FRAMES)]
            with self._lock:
                msg = self._message
            line = f"  {frame} {msg}"
            padded = line.ljust(self._last_line_len)
            sys.stderr.write(f"\r{padded}")
            sys.stderr.flush()
            self._last_line_len = len(line)
            idx += 1
            self._stop_event.wait(0.12)

    def _summarize_loop(self) -> None:
        """Every N seconds, summarize partial output via lightweight LLM."""
        while not self._stop_event.is_set():
            self._stop_event.wait(self._interval)
            if self._stop_event.is_set():
                break

            with self._lock:
                partial = self._partial_output
                prev_msg = self._message

            if not partial:
                continue

            try:
                summary = self._backend.summarize_progress(partial, previous_summary=prev_msg)
                if summary:
                    with self._lock:
                        self._message = summary
                    if not self._is_tty:
                        click.echo(f"  ... {summary}")
            except Exception:
                pass  # Don't let summarizer errors affect main flow
