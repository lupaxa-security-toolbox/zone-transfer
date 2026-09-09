"""AXFR classification and record extraction."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import dns.exception
import dns.rcode
import dns.xfr

from lupaxa.zone_transfer.models import Endpoint
from lupaxa.zone_transfer.xfr import transfer_zone

ENDPOINT = Endpoint(nameserver="ns1.example.net", address="203.0.113.10", family="IPv4")


def _zone_with_record() -> MagicMock:
    rdata = MagicMock()
    rdata.to_text.return_value = "203.0.113.50"
    rdataset = MagicMock()
    rdataset.rdtype = 1
    rdataset.ttl = 300
    rdataset.__iter__.return_value = iter([rdata])
    node = MagicMock()
    node.rdatasets = [rdataset]
    name = MagicMock()
    name.to_text.return_value = "www"
    zone = MagicMock()
    zone.nodes = {name: node}
    return zone


def test_transfer_allowed_includes_type_and_ttl() -> None:
    with (
        patch("lupaxa.zone_transfer.xfr._from_xfr", return_value=_zone_with_record()),
        patch("lupaxa.zone_transfer.xfr.dns.rdatatype.to_text", return_value="A"),
    ):
        attempt = transfer_zone("example.com", ENDPOINT, timeout=10.0)
    assert attempt.status == "allowed"
    assert attempt.reason == ""
    assert attempt.records[0].name == "www"
    assert attempt.records[0].rtype == "A"
    assert attempt.records[0].ttl == 300
    assert attempt.records[0].rdata == "203.0.113.50"


def test_transfer_form_error_is_refused() -> None:
    with patch(
        "lupaxa.zone_transfer.xfr._from_xfr",
        side_effect=dns.exception.FormError(),
    ):
        attempt = transfer_zone("example.com", ENDPOINT)
    assert attempt.status == "refused"
    assert attempt.records == []


def test_transfer_error_is_refused() -> None:
    with patch(
        "lupaxa.zone_transfer.xfr._from_xfr",
        side_effect=dns.xfr.TransferError(dns.rcode.REFUSED),
    ):
        attempt = transfer_zone("example.com", ENDPOINT)
    assert attempt.status == "refused"
    assert "REFUSED" in attempt.reason


def test_transfer_timeout_is_error() -> None:
    with patch(
        "lupaxa.zone_transfer.xfr._from_xfr",
        side_effect=TimeoutError("timed out"),
    ):
        attempt = transfer_zone("example.com", ENDPOINT)
    assert attempt.status == "error"
    assert attempt.reason == "timeout"
