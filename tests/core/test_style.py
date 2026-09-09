"""Colour helpers for table output."""

from __future__ import annotations

import io

import pytest
from colored import Fore, Style

from lupaxa.zone_transfer.style import (
    color_name,
    color_status,
    color_title,
    color_value,
    use_color,
)


def test_color_name_is_cyan() -> None:
    assert color_name("Nameserver") == f"{Fore.cyan}Nameserver{Style.reset}"


def test_color_value_green_unless_empty() -> None:
    assert color_value("refused") == f"{Fore.green}refused{Style.reset}"
    assert color_value("") == ""


def test_color_status_for_allowed_refused_error() -> None:
    assert color_status("allowed") == f"{Fore.red}allowed{Style.reset}"
    assert color_status("refused") == f"{Fore.green}refused{Style.reset}"
    assert color_status("error") == f"{Fore.dark_gray}error{Style.reset}"


def test_color_title_is_cyan_label_and_bold_white_domain() -> None:
    title = color_title("example.com")
    assert title.startswith(f"{Fore.cyan}Results for:{Style.reset}")
    assert f"{Style.bold}{Fore.white}example.com{Style.reset}" in title


def test_use_color_respects_no_color(monkeypatch: pytest.MonkeyPatch) -> None:
    stream = io.StringIO()
    monkeypatch.setenv("NO_COLOR", "1")
    monkeypatch.delenv("FORCE_COLOR", raising=False)
    assert use_color(stream) is False
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setenv("FORCE_COLOR", "1")
    assert use_color(stream) is True
