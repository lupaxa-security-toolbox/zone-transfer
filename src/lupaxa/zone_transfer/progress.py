"""Terminal status line for long-running inspections."""

from __future__ import annotations

import threading
from typing import Protocol

_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


class StatusStream(Protocol):
    """Minimal stream used by ``StatusDisplay``."""

    def isatty(self) -> bool:
        raise NotImplementedError

    def write(self, text: str) -> int:
        raise NotImplementedError

    def flush(self) -> None:
        raise NotImplementedError


class StatusDisplay:
    """Write a spinning status line to a TTY; stay silent otherwise."""

    def __init__(self, stream: StatusStream) -> None:
        self._stream = stream
        self._tty = bool(getattr(stream, "isatty", lambda: False)())
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._message = ""
        self._frame = 0

    def show(self, message: str) -> None:
        """Start or update the spinner with ``message``."""
        if not self._tty:
            return
        with self._lock:
            self._message = message
        self._paint()
        if self._thread is None:
            self._stop.clear()
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()

    def clear(self) -> None:
        """Stop the spinner and erase the status line."""
        self._stop.set()
        thread = self._thread
        if thread is not None:
            thread.join(timeout=1.0)
            self._thread = None
        if self._tty:
            self._stream.write("\r\033[K")
            self._stream.flush()

    def _spin(self) -> None:
        while not self._stop.wait(0.08):
            self._paint()

    def _paint(self) -> None:
        with self._lock:
            frame = _FRAMES[self._frame % len(_FRAMES)]
            self._frame += 1
            line = f"{frame} {self._message}"
        self._stream.write(f"\r\033[K{line}")
        self._stream.flush()
