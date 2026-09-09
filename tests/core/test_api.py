"""Domain inspection orchestration."""

from __future__ import annotations

from unittest.mock import patch

import dns.resolver
import pytest

from lupaxa.zone_transfer.api import inspect_domain, inspect_many
from lupaxa.zone_transfer.exceptions import InvalidTargetError, NameserverLookupError
from lupaxa.zone_transfer.models import (
    Endpoint,
    NameServer,
    Progress,
    TransferAttempt,
    ZoneRecord,
)


def test_inspect_domain_empty_raises() -> None:
    with pytest.raises(InvalidTargetError, match="empty domain"):
        inspect_domain("  ")


def test_inspect_domain_empty_nameserver_list_raises() -> None:
    with pytest.raises(InvalidTargetError, match="empty nameserver list"):
        inspect_domain("example.com", nameservers=[])


def test_inspect_domain_whitespace_nameserver_list_raises() -> None:
    with pytest.raises(InvalidTargetError, match="empty nameserver list"):
        inspect_domain("example.com", nameservers=["  ", "\t"])


def test_inspect_domain_discovery_error() -> None:
    with patch(
        "lupaxa.zone_transfer.api.lookup_nameservers",
        side_effect=NameserverLookupError("Domain 'example.com' does not exist."),
    ):
        report = inspect_domain("example.com")
    assert report.domain == "example.com"
    assert "does not exist" in report.error
    assert report.attempts == []


def test_inspect_domain_uses_supplied_nameservers() -> None:
    endpoint = Endpoint(nameserver="203.0.113.10", address="203.0.113.10", family="IPv4")
    attempt = TransferAttempt(endpoint=endpoint, status="refused", reason="REFUSED", records=[])
    with (
        patch(
            "lupaxa.zone_transfer.api.expand_nameservers",
            return_value=[endpoint],
        ) as expand,
        patch("lupaxa.zone_transfer.api.transfer_zone", return_value=attempt) as xfr,
        patch("lupaxa.zone_transfer.api.lookup_nameservers") as lookup,
    ):
        report = inspect_domain("example.com", nameservers=["203.0.113.10"])
    lookup.assert_not_called()
    expand.assert_called_once_with(["203.0.113.10"], timeout=10.0)
    xfr.assert_called_once()
    assert report.attempts[0].status == "refused"


def test_inspect_domain_unresolved_host_is_error_row() -> None:
    endpoint = Endpoint(nameserver="empty.example.net", address="", family="")
    with (
        patch("lupaxa.zone_transfer.api.expand_nameservers", return_value=[endpoint]),
        patch("lupaxa.zone_transfer.api.transfer_zone") as xfr,
    ):
        report = inspect_domain("example.com", nameservers=["empty.example.net"])
    xfr.assert_not_called()
    assert report.attempts[0].status == "error"
    assert report.attempts[0].reason == "no A/AAAA records"


def test_inspect_domain_uses_resolve_error_for_empty_address() -> None:
    endpoint = Endpoint(
        nameserver="ns1.example.net",
        address="",
        family="",
        resolve_error="DNS query timeout occurred.",
    )
    with (
        patch("lupaxa.zone_transfer.api.expand_nameservers", return_value=[endpoint]),
        patch("lupaxa.zone_transfer.api.transfer_zone") as xfr,
    ):
        report = inspect_domain("example.com", nameservers=["ns1.example.net"])
    xfr.assert_not_called()
    assert "timeout" in report.attempts[0].reason.lower()
    assert report.attempts[0].reason != "no A/AAAA records"


def test_inspect_domain_query_timeout_is_not_no_records() -> None:
    with patch("lupaxa.zone_transfer.ns._query", side_effect=dns.resolver.Timeout()):
        report = inspect_domain("example.com", nameservers=["ns1.example.net"])
    assert report.attempts[0].status == "error"
    assert "timeout" in report.attempts[0].reason.lower()
    assert report.attempts[0].reason != "no A/AAAA records"


def test_inspect_domain_query_servfail_is_not_no_records() -> None:
    with patch(
        "lupaxa.zone_transfer.ns._query",
        side_effect=dns.resolver.NoNameservers(),
    ):
        report = inspect_domain("example.com", nameservers=["ns1.example.net"])
    assert report.attempts[0].status == "error"
    assert "fail" in report.attempts[0].reason.lower()
    assert report.attempts[0].reason != "no A/AAAA records"


def test_inspect_domain_query_no_answer_is_no_records() -> None:
    with patch("lupaxa.zone_transfer.ns._query", side_effect=dns.resolver.NoAnswer()):
        report = inspect_domain("example.com", nameservers=["ns1.example.net"])
    assert report.attempts[0].reason == "no A/AAAA records"


def test_inspect_domain_no_endpoints_sets_error() -> None:
    with (
        patch("lupaxa.zone_transfer.api.expand_nameservers", return_value=[]),
        patch("lupaxa.zone_transfer.api.transfer_zone") as xfr,
    ):
        report = inspect_domain("example.com", nameservers=["203.0.113.10"])
    xfr.assert_not_called()
    assert report.error == "no usable nameserver endpoints"
    assert report.attempts == []


def test_inspect_many_preserves_order() -> None:
    first = Endpoint(nameserver="203.0.113.10", address="203.0.113.10", family="IPv4")
    record = ZoneRecord(
        name="@",
        rtype="SOA",
        ttl=3600,
        rdata="ns1.example.net. hostmaster. 1 1 1 1 1",
    )
    allowed = TransferAttempt(endpoint=first, status="allowed", reason="", records=[record])
    with (
        patch(
            "lupaxa.zone_transfer.api.lookup_nameservers",
            return_value=[NameServer(name="ns1.example.net")],
        ),
        patch("lupaxa.zone_transfer.api.expand_nameservers", return_value=[first]),
        patch("lupaxa.zone_transfer.api.transfer_zone", return_value=allowed),
    ):
        reports = inspect_many(["b.example", "a.example"])
    assert [item.domain for item in reports] == ["b.example", "a.example"]


def test_inspect_many_empty_raises() -> None:
    with pytest.raises(InvalidTargetError, match="empty domain list"):
        inspect_many([])


def test_inspect_domain_emits_progress() -> None:
    endpoint = Endpoint(nameserver="203.0.113.10", address="203.0.113.10", family="IPv4")
    attempt = TransferAttempt(endpoint=endpoint, status="refused", reason="REFUSED", records=[])
    events: list[Progress] = []
    with (
        patch("lupaxa.zone_transfer.api.expand_nameservers", return_value=[endpoint]),
        patch("lupaxa.zone_transfer.api.transfer_zone", return_value=attempt),
        patch("lupaxa.zone_transfer.api.lookup_nameservers") as lookup,
    ):
        inspect_domain(
            "example.com",
            nameservers=["203.0.113.10"],
            on_progress=events.append,
        )
    lookup.assert_not_called()
    assert [event.phase for event in events] == ["resolve", "try"]
    assert events[0].domain == "example.com"
    assert "Resolving" in events[0].message
    assert events[1].current == 1
    assert events[1].total == 1
    assert "203.0.113.10" in events[1].message


def test_inspect_domain_emits_lookup_progress() -> None:
    endpoint = Endpoint(nameserver="ns1.example.net", address="203.0.113.10", family="IPv4")
    attempt = TransferAttempt(endpoint=endpoint, status="refused", reason="REFUSED", records=[])
    events: list[Progress] = []
    with (
        patch(
            "lupaxa.zone_transfer.api.lookup_nameservers",
            return_value=[NameServer(name="ns1.example.net")],
        ),
        patch("lupaxa.zone_transfer.api.expand_nameservers", return_value=[endpoint]),
        patch("lupaxa.zone_transfer.api.transfer_zone", return_value=attempt),
    ):
        inspect_domain("example.com", on_progress=events.append)
    assert events[0].phase == "lookup"
    assert "Looking up nameservers" in events[0].message
    assert [event.phase for event in events] == ["lookup", "resolve", "try"]


def test_inspect_many_forwards_progress() -> None:
    first = Endpoint(nameserver="203.0.113.10", address="203.0.113.10", family="IPv4")
    attempt = TransferAttempt(endpoint=first, status="refused", reason="REFUSED", records=[])
    events: list[Progress] = []
    with (
        patch("lupaxa.zone_transfer.api.expand_nameservers", return_value=[first]),
        patch("lupaxa.zone_transfer.api.transfer_zone", return_value=attempt),
    ):
        inspect_many(
            ["one.example", "two.example"],
            nameservers=["203.0.113.10"],
            on_progress=events.append,
        )
    domains = {event.domain for event in events}
    assert domains == {"one.example", "two.example"}
    assert any(event.phase == "try" for event in events)
