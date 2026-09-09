"""Progress events and terminal status spinner."""

from __future__ import annotations

import time

from lupaxa.zone_transfer.models import Progress
from lupaxa.zone_transfer.progress import StatusDisplay


class _FakeStream:
    def __init__(self, tty: bool) -> None:
        self._tty = tty
        self.writes: list[str] = []

    def isatty(self) -> bool:
        return self._tty

    def write(self, text: str) -> int:
        self.writes.append(text)
        return len(text)

    def flush(self) -> None:
        return None


def test_progress_message_fields() -> None:
    event = Progress(
        domain="example.com",
        phase="try",
        message="Trying ns1.example.net (203.0.113.10) [1/2]...",
        current=1,
        total=2,
    )
    assert event.phase == "try"
    assert event.current == 1
    assert event.total == 2


def test_status_display_spins_on_tty() -> None:
    stream = _FakeStream(tty=True)
    status = StatusDisplay(stream)
    status.show("Trying ns1.example.net (203.0.113.10) [1/1]...")
    deadline = time.monotonic() + 1.0
    joined = ""
    while time.monotonic() < deadline:
        joined = "".join(stream.writes)
        if "Trying ns1.example.net" in joined:
            break
        time.sleep(0.02)
    status.clear()
    assert "Trying ns1.example.net" in joined
    assert any(frame in joined for frame in "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏")
    assert any("\r" in chunk for chunk in stream.writes)


def test_status_display_is_silent_when_not_a_tty() -> None:
    stream = _FakeStream(tty=False)
    status = StatusDisplay(stream)
    status.show("Trying ns1.example.net (203.0.113.10) [1/1]...")
    time.sleep(0.15)
    status.clear()
    assert stream.writes == []
