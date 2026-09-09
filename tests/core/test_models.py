"""Dataclass defaults for zone-transfer reports."""

from __future__ import annotations

from lupaxa.zone_transfer.models import (
    DomainReport,
    Endpoint,
    NameServer,
    TransferAttempt,
    ZoneRecord,
)


def test_nameserver_and_endpoint() -> None:
    server = NameServer(name="ns1.example.net")
    endpoint = Endpoint(nameserver=server.name, address="203.0.113.10", family="IPv4")
    assert server.name == "ns1.example.net"
    assert endpoint.family == "IPv4"


def test_zone_record_fields() -> None:
    record = ZoneRecord(name="@", rtype="A", ttl=300, rdata="203.0.113.10")
    assert record.rtype == "A"
    assert record.ttl == 300


def test_domain_report_defaults() -> None:
    attempt = TransferAttempt(
        endpoint=Endpoint(nameserver="ns1.example.net", address="", family=""),
        status="error",
        reason="no A/AAAA records",
        records=[],
    )
    report = DomainReport(domain="example.com", error="", attempts=[attempt])
    assert report.attempts[0].records == []
    assert report.error == ""
