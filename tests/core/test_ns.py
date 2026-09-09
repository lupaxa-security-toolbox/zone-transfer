"""Nameserver lookup and address expansion."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import dns.resolver
import pytest

from lupaxa.zone_transfer.exceptions import InvalidTargetError, NameserverLookupError
from lupaxa.zone_transfer.ns import expand_nameservers, lookup_nameservers


def _ns_rdata(target: str) -> MagicMock:
    rdata = MagicMock()
    rdata.target.to_text.return_value = target
    return rdata


def _addr_rdata(address: str) -> MagicMock:
    rdata = MagicMock()
    rdata.address = address
    return rdata


def test_lookup_nameservers_empty_domain() -> None:
    with pytest.raises(InvalidTargetError, match="empty domain"):
        lookup_nameservers("   ")


def test_lookup_nameservers_returns_hosts_in_order() -> None:
    answers = [_ns_rdata("ns2.example.net."), _ns_rdata("ns1.example.net.")]
    with patch("lupaxa.zone_transfer.ns._query", return_value=answers) as mocked:
        servers = lookup_nameservers("example.com", timeout=10.0)
    mocked.assert_called_once_with("example.com", "NS", 10.0)
    assert [server.name for server in servers] == ["ns2.example.net", "ns1.example.net"]


def test_lookup_nameservers_nxdomain() -> None:
    with (
        patch(
            "lupaxa.zone_transfer.ns._query",
            side_effect=dns.resolver.NXDOMAIN(),
        ),
        pytest.raises(NameserverLookupError, match="does not exist"),
    ):
        lookup_nameservers("missing.example")


def test_expand_ip_literal_is_one_endpoint() -> None:
    endpoints = expand_nameservers(["203.0.113.10"])
    assert [(item.nameserver, item.address, item.family) for item in endpoints] == [
        ("203.0.113.10", "203.0.113.10", "IPv4"),
    ]


def test_expand_hostname_uses_every_a_and_aaaa() -> None:
    def fake_query(name: str, rdtype: str, timeout: float) -> list[MagicMock]:
        assert name == "ns1.example.net"
        assert timeout == 10.0
        if rdtype == "A":
            return [_addr_rdata("203.0.113.11"), _addr_rdata("203.0.113.10")]
        if rdtype == "AAAA":
            return [_addr_rdata("2001:db8::2"), _addr_rdata("2001:db8::1")]
        raise AssertionError(rdtype)

    with patch("lupaxa.zone_transfer.ns._query", side_effect=fake_query):
        endpoints = expand_nameservers(["ns1.example.net"], timeout=10.0)
    assert [(item.address, item.family) for item in endpoints] == [
        ("203.0.113.10", "IPv4"),
        ("203.0.113.11", "IPv4"),
        ("2001:db8::1", "IPv6"),
        ("2001:db8::2", "IPv6"),
    ]


def test_expand_hostname_without_addresses() -> None:
    with patch(
        "lupaxa.zone_transfer.ns._query",
        side_effect=dns.resolver.NoAnswer(),
    ):
        endpoints = expand_nameservers(["empty.example.net"])
    assert len(endpoints) == 1
    assert endpoints[0].address == ""
    assert endpoints[0].family == ""
    assert endpoints[0].resolve_error == ""


def test_expand_hostname_timeout_sets_resolve_error() -> None:
    with patch(
        "lupaxa.zone_transfer.ns._query",
        side_effect=dns.resolver.Timeout(),
    ):
        endpoints = expand_nameservers(["slow.example.net"])
    assert len(endpoints) == 1
    assert endpoints[0].address == ""
    assert "timeout" in endpoints[0].resolve_error.lower()


def test_expand_hostname_servfail_sets_resolve_error() -> None:
    with patch(
        "lupaxa.zone_transfer.ns._query",
        side_effect=dns.resolver.NoNameservers(),
    ):
        endpoints = expand_nameservers(["fail.example.net"])
    assert len(endpoints) == 1
    assert endpoints[0].address == ""
    assert "fail" in endpoints[0].resolve_error.lower()
