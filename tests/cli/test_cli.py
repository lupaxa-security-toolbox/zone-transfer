"""CLI entrypoint."""

from __future__ import annotations

import json
from unittest.mock import patch

from lupaxa.zone_transfer.cli import main
from lupaxa.zone_transfer.models import (
    DomainReport,
    Endpoint,
    Progress,
    TransferAttempt,
    ZoneRecord,
)
from lupaxa.zone_transfer.version import get_version

ENDPOINT = Endpoint(nameserver="ns1.example.net", address="203.0.113.10", family="IPv4")


def _refused() -> DomainReport:
    return DomainReport(
        domain="example.com",
        error="",
        attempts=[
            TransferAttempt(endpoint=ENDPOINT, status="refused", reason="REFUSED", records=[]),
        ],
    )


def _allowed() -> DomainReport:
    record = ZoneRecord(
        name="@",
        rtype="SOA",
        ttl=3600,
        rdata="ns1.example.net. hostmaster. 1 1 1 1 1",
    )
    return DomainReport(
        domain="example.com",
        error="",
        attempts=[
            TransferAttempt(endpoint=ENDPOINT, status="allowed", reason="", records=[record]),
        ],
    )


def test_help_exits_zero() -> None:
    assert main(["--help"]) == 0


def test_version_flag(capsys) -> None:  # type: ignore[no-untyped-def]
    assert main(["--version"]) == 0
    assert get_version() in capsys.readouterr().out


def test_table_output(capsys) -> None:  # type: ignore[no-untyped-def]
    with patch("lupaxa.zone_transfer.cli.inspect_many", return_value=[_refused()]):
        code = main(["example.com"])
    assert code == 0
    out = capsys.readouterr().out
    assert "Results for: example.com" in out
    assert "refused" in out


def test_json_format(capsys) -> None:  # type: ignore[no-untyped-def]
    with patch("lupaxa.zone_transfer.cli.inspect_many", return_value=[_allowed()]):
        code = main(["example.com", "--format", "json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["domain"] == "example.com"
    assert payload[0]["attempts"][0]["status"] == "allowed"
    assert payload[0]["attempts"][0]["records"][0]["type"] == "SOA"


def test_fail_open_exits_two_when_allowed() -> None:
    with patch("lupaxa.zone_transfer.cli.inspect_many", return_value=[_allowed()]):
        assert main(["example.com", "--fail-open"]) == 2


def test_fail_open_stays_zero_when_refused() -> None:
    with patch("lupaxa.zone_transfer.cli.inspect_many", return_value=[_refused()]):
        assert main(["example.com", "--fail-open"]) == 0


def test_domain_error_exits_two() -> None:
    report = DomainReport(domain="missing.example", error="does not exist", attempts=[])
    with patch("lupaxa.zone_transfer.cli.inspect_many", return_value=[report]):
        assert main(["missing.example"]) == 2


def test_whitespace_nameserver_exits_two() -> None:
    assert main(["example.com", "--nameserver", " "]) == 2


def test_zero_attempts_never_exits_zero() -> None:
    report = DomainReport(domain="example.com", error="", attempts=[])
    with patch("lupaxa.zone_transfer.cli.inspect_many", return_value=[report]):
        assert main(["example.com"]) == 2


def test_timeout_must_be_positive() -> None:
    with patch("lupaxa.zone_transfer.cli.inspect_many") as mocked:
        assert main(["example.com", "--timeout", "0"]) == 2
        assert main(["example.com", "--timeout", "-1"]) == 2
    mocked.assert_not_called()


def test_timeout_nan_exits_two() -> None:
    with patch("lupaxa.zone_transfer.cli.inspect_many") as mocked:
        assert main(["example.com", "--timeout", "nan"]) == 2
    mocked.assert_not_called()


def test_timeout_inf_exits_two() -> None:
    with patch("lupaxa.zone_transfer.cli.inspect_many") as mocked:
        assert main(["example.com", "--timeout", "inf"]) == 2
    mocked.assert_not_called()


def test_no_color_flag_disables_table_colour(capsys, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("FORCE_COLOR", "1")
    monkeypatch.delenv("NO_COLOR", raising=False)
    with patch("lupaxa.zone_transfer.cli.inspect_many", return_value=[_refused()]):
        code = main(["example.com", "--no-color"])
    assert code == 0
    assert "\033[" not in capsys.readouterr().out


def test_multi_domain_passes_all_names() -> None:
    with patch(
        "lupaxa.zone_transfer.cli.inspect_many",
        return_value=[_refused(), _refused()],
    ) as mocked:
        assert main(["example.com", "example.org", "--nameserver", "203.0.113.10"]) == 0
    mocked.assert_called_once()
    args, kwargs = mocked.call_args
    assert args[0] == ["example.com", "example.org"]
    assert kwargs["nameservers"] == ["203.0.113.10"]
    assert callable(kwargs["on_progress"])


def test_cli_progress_writes_stderr_not_stdout(capsys) -> None:  # type: ignore[no-untyped-def]
    def fake_inspect(domains, **kwargs):  # type: ignore[no-untyped-def]
        del domains
        callback = kwargs.get("on_progress")
        assert callback is not None
        callback(
            Progress(
                domain="example.com",
                phase="try",
                message="Trying ns1.example.net (203.0.113.10) [1/1]...",
                current=1,
                total=1,
            )
        )
        return [_refused()]

    with (
        patch("lupaxa.zone_transfer.cli.inspect_many", side_effect=fake_inspect),
        patch("sys.stderr.isatty", return_value=True),
    ):
        assert main(["example.com", "--format", "json"]) == 0
    captured = capsys.readouterr()
    assert "Trying ns1.example.net" not in captured.out
    payload = json.loads(captured.out)
    assert payload[0]["domain"] == "example.com"
    assert "Trying ns1.example.net" in captured.err
