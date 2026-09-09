"""Table and JSON rendering."""

from __future__ import annotations

from typing import Any, cast

from lupaxa.zone_transfer.format import format_report, report_payload
from lupaxa.zone_transfer.models import DomainReport, Endpoint, TransferAttempt, ZoneRecord

ENDPOINT = Endpoint(nameserver="ns1.example.net", address="203.0.113.10", family="IPv4")


def test_report_payload_uses_type_key() -> None:
    record = ZoneRecord(
        name="@",
        rtype="SOA",
        ttl=3600,
        rdata="ns1.example.net. hostmaster. 1 1 1 1 1",
    )
    report = DomainReport(
        domain="example.com",
        error="",
        attempts=[
            TransferAttempt(endpoint=ENDPOINT, status="allowed", reason="", records=[record]),
        ],
    )
    payload = report_payload(report)
    assert payload["domain"] == "example.com"
    assert payload["error"] == ""
    attempts = cast(list[dict[str, Any]], payload["attempts"])
    attempt = attempts[0]
    records = cast(list[dict[str, Any]], attempt["records"])
    assert attempt["nameserver"] == "ns1.example.net"
    assert records[0]["type"] == "SOA"
    assert "rtype" not in records[0]


def test_format_report_includes_status_and_dump() -> None:
    record = ZoneRecord(name="www", rtype="A", ttl=300, rdata="203.0.113.50")
    report = DomainReport(
        domain="example.com",
        error="",
        attempts=[
            TransferAttempt(endpoint=ENDPOINT, status="allowed", reason="", records=[record]),
        ],
    )
    text = format_report(report, color=False)
    cells = {part.strip() for line in text.splitlines() for part in line.split("|") if part.strip()}
    assert "Results for: example.com" in text
    assert ENDPOINT.nameserver in cells
    assert "allowed" in text
    assert "www" in text
    assert "A" in text
    assert "203.0.113.50" in text


def test_format_report_color_includes_ansi_for_allowed() -> None:
    record = ZoneRecord(name="www", rtype="A", ttl=300, rdata="203.0.113.50")
    report = DomainReport(
        domain="example.com",
        error="",
        attempts=[
            TransferAttempt(endpoint=ENDPOINT, status="allowed", reason="", records=[record]),
        ],
    )
    text = format_report(report, color=True)
    assert "allowed" in text
    assert "\033[" in text
