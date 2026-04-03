"""LLM backend abstraction and Claude CLI implementation."""

from __future__ import annotations

import json
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

from mcp2cli.constants import SESSIONS_DIR, SESSION_EXPIRY_HOURS


@dataclass
class LLMResult:
    """LLM invocation result."""

    session_id: str | None
    result: str
    is_error: bool


class LLMBackend(ABC):
    """Abstract LLM backend interface."""

    @property
    @abstractmethod
    def backend_type(self) -> str:
        ...

    @abstractmethod
    def invoke(
        self,
        prompt: str,
        *,
        command_name: str = "",
        server_name: str = "",
        show_progress: bool = False,
        progress_message: str = "",
    ) -> LLMResult:
        ...

    @abstractmethod
    def resume(
        self,
        session_id: str,
        prompt: str,
        *,
        show_progress: bool = False,
        progress_message: str = "",
    ) -> LLMResult:
        ...

    @abstractmethod
    def summarize_progress(self, partial_output: str, previous_summary: str = "") -> str:
        """Summarize current LLM progress into one line using the default model.

        Returns a one-line summary string, or empty string on failure.
        """
        ...


@dataclass
class SessionFile:
    """Persistent session file model."""

    session_id: str
    backend: str
    command: str
    server: str
    created_at: str
    last_used_at: str
    status: str  # "in_progress" | "completed"

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "backend": self.backend,
            "command": self.command,
            "server": self.server,
            "created_at": self.created_at,
            "last_used_at": self.last_used_at,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SessionFile:
        return cls(**data)


# ---------------------------------------------------------------------------
# Summarizer prompt
# ---------------------------------------------------------------------------

SUMMARIZE_PROMPT = """You are a progress status writer. Based on the AI assistant's output below, write ONE short English status line (max 40 chars) describing the LATEST specific finding or action.

Rules:
- Focus on the NEWEST concrete detail (a package name found, a URL visited, a specific piece of data discovered)
- NEVER use generic phrases like "Searching the web" or "Processing data"
- MUST be different from the previous status: "{previous_summary}"
- Use present participle form ("Found X on PyPI...", "Reading GitHub README...", "Identified 6 env vars...")

Current assistant output (latest portion):
{partial_output}

Output ONLY the status line, nothing else."""


class ClaudeCLIBackend(LLMBackend):
    """Claude CLI backend (MVP default)."""

    def __init__(self, command: str = "claude", model: str = "sonnet"):
        self.command = command
        self.model = model

    @property
    def backend_type(self) -> str:
        return "claude-cli"

    def invoke(
        self,
        prompt: str,
        *,
        command_name: str = "",
        server_name: str = "",
        show_progress: bool = False,
        progress_message: str = "",
    ) -> LLMResult:
        cmd = [
            self.command, "-p", prompt,
            "--output-format", "json",
            "--model", self.model,
            "--dangerously-skip-permissions",
        ]

        if show_progress:
            result = self._run_with_progress(cmd, progress_message or "Processing...")
        else:
            result = self._run(cmd)

        if result.session_id and command_name and server_name:
            self._save_session(result.session_id, command_name, server_name)

        return result

    def resume(
        self,
        session_id: str,
        prompt: str,
        *,
        show_progress: bool = False,
        progress_message: str = "",
    ) -> LLMResult:
        cmd = [
            self.command, "-p", prompt,
            "--output-format", "json",
            "--dangerously-skip-permissions",
            "--resume", session_id,
        ]

        if show_progress:
            return self._run_with_progress(cmd, progress_message or "Processing...")
        return self._run(cmd)

    def summarize_progress(self, partial_output: str, previous_summary: str = "") -> str:
        """Use the default model to summarize current progress into one line."""
        if not partial_output.strip():
            return ""
        # Truncate to last 800 chars to keep the call fast
        truncated = partial_output[-800:]
        prompt = SUMMARIZE_PROMPT.format(
            partial_output=truncated,
            previous_summary=previous_summary or "(none)",
        )
        cmd = [
            self.command, "-p", prompt,
            "--output-format", "json",
            "--model", self.model,
            "--dangerously-skip-permissions",
            "--max-turns", "1",
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            data = json.loads(proc.stdout)
            if data.get("is_error"):
                return ""
            return data.get("result", "").strip()[:60]
        except Exception:
            return ""

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def find_session(self, command_name: str, server_name: str) -> Optional[str]:
        """Find unexpired in-progress session for this backend."""
        path = self._session_path(command_name, server_name)
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text())
            sf = SessionFile.from_dict(data)

            created = datetime.fromisoformat(sf.created_at)
            if (datetime.now(timezone.utc) - created).total_seconds() > SESSION_EXPIRY_HOURS * 3600:
                path.unlink(missing_ok=True)
                return None

            if sf.status != "in_progress":
                return None

            if sf.backend != self.backend_type:
                return None

            return sf.session_id
        except (json.JSONDecodeError, KeyError, ValueError):
            path.unlink(missing_ok=True)
            return None

    def clear_session(self, command_name: str, server_name: str) -> None:
        self._session_path(command_name, server_name).unlink(missing_ok=True)

    # ------------------------------------------------------------------
    # Internal: run methods
    # ------------------------------------------------------------------

    def _run(self, cmd: list[str]) -> LLMResult:
        """Run claude CLI synchronously (non-streaming)."""
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        try:
            data = json.loads(proc.stdout)
            return LLMResult(
                session_id=data.get("session_id"),
                result=data.get("result", ""),
                is_error=data.get("is_error", False),
            )
        except json.JSONDecodeError:
            if proc.returncode != 0:
                return LLMResult(session_id=None, result=proc.stderr or proc.stdout, is_error=True)
            return LLMResult(session_id=None, result=proc.stdout, is_error=False)

    def _run_streaming(
        self,
        cmd: list[str],
        progress_cb: Callable[[str], None] | None = None,
    ) -> LLMResult:
        """Run claude CLI with stream-json, calling progress_cb with accumulated text."""
        stream_cmd = list(cmd)
        # Replace "json" with "stream-json" in the --output-format value
        try:
            idx = stream_cmd.index("json")
            stream_cmd[idx] = "stream-json"
        except ValueError:
            pass
        # stream-json requires --verbose when used with -p
        stream_cmd.append("--verbose")

        proc = subprocess.Popen(
            stream_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        accumulated = ""
        session_id: str | None = None
        result_text = ""
        is_error = False

        for line in proc.stdout:  # type: ignore[union-attr]
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            etype = event.get("type")

            # Capture session_id from any event that carries it
            if event.get("session_id"):
                session_id = event["session_id"]

            if etype == "assistant":
                content = event.get("message", {}).get("content", [])
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "text":
                        accumulated += block.get("text", "")
                        if progress_cb:
                            progress_cb(accumulated)
                    elif block.get("type") == "tool_use":
                        tool_info = f"[calling {block.get('name', 'tool')}] "
                        accumulated += tool_info
                        if progress_cb:
                            progress_cb(accumulated)

            elif etype == "result":
                result_text = event.get("result", "")
                is_error = event.get("is_error", False)
                if event.get("session_id"):
                    session_id = event["session_id"]

        proc.wait()

        if proc.returncode != 0 and not result_text:
            stderr_out = proc.stderr.read() if proc.stderr else ""
            return LLMResult(session_id=session_id, result=stderr_out, is_error=True)

        return LLMResult(session_id=session_id, result=result_text, is_error=is_error)

    def _run_with_progress(self, cmd: list[str], message: str) -> LLMResult:
        """Run LLM with streaming + spinner + periodic summarization."""
        from mcp2cli.ui.progress import LLMProgressDisplay

        progress = LLMProgressDisplay(
            backend=self,
            initial_message=message,
        )
        progress.start()
        try:
            return self._run_streaming(cmd, progress_cb=progress.update_partial)
        finally:
            progress.stop()

    # ------------------------------------------------------------------
    # Internal: session persistence
    # ------------------------------------------------------------------

    def _save_session(self, session_id: str, command_name: str, server_name: str) -> None:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()
        sf = SessionFile(
            session_id=session_id,
            backend=self.backend_type,
            command=command_name,
            server=server_name,
            created_at=now,
            last_used_at=now,
            status="in_progress",
        )
        self._session_path(command_name, server_name).write_text(
            json.dumps(sf.to_dict(), indent=2)
        )

    def _session_path(self, command_name: str, server_name: str) -> Path:
        safe_name = f"{command_name.replace(' ', '-')}-{server_name}"
        return SESSIONS_DIR / f"{safe_name}.session.json"


def get_backend() -> ClaudeCLIBackend:
    """Get the configured LLM backend (MVP: always ClaudeCLI)."""
    return ClaudeCLIBackend()
