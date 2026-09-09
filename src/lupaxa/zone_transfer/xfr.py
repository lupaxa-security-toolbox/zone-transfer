"""One AXFR attempt against one endpoint."""

from __future__ import annotations

import socket

import dns.exception
import dns.query
import dns.rdatatype
import dns.xfr
import dns.zone

from .models import Endpoint, TransferAttempt, ZoneRecord

DEFAULT_TIMEOUT = 10.0


def _from_xfr(domain: str, address: str, timeout: float) -> object:
    return dns.zone.from_xfr(dns.query.xfr(address, domain, timeout=timeout, lifetime=timeout))


def _records_from_zone(zone: object) -> list[ZoneRecord]:
    records: list[ZoneRecord] = []
    nodes = getattr(zone, "nodes", {})
    for name, node in nodes.items():
        owner = name.to_text() if hasattr(name, "to_text") else str(name)
        for rdataset in getattr(node, "rdatasets", []):
            rtype = dns.rdatatype.to_text(rdataset.rdtype)
            ttl = int(rdataset.ttl)
            for rdata in rdataset:
                records.append(
                    ZoneRecord(
                        name=owner,
                        rtype=rtype,
                        ttl=ttl,
                        rdata=rdata.to_text(),
                    )
                )
    return records


def _classify(exc: BaseException) -> tuple[str, str]:
    if isinstance(exc, (TimeoutError, socket.timeout, dns.exception.Timeout)):
        return ("error", "timeout")
    if isinstance(exc, (dns.exception.FormError, dns.xfr.TransferError)):
        return ("refused", str(exc) or "not permitted")
    return ("error", str(exc) or type(exc).__name__)


def transfer_zone(
    domain: str,
    endpoint: Endpoint,
    *,
    timeout: float = DEFAULT_TIMEOUT,
) -> TransferAttempt:
    """Run one TCP AXFR against ``endpoint.address``."""
    try:
        zone = _from_xfr(domain, endpoint.address, timeout)
    except Exception as exc:
        status, reason = _classify(exc)
        return TransferAttempt(endpoint=endpoint, status=status, reason=reason, records=[])
    return TransferAttempt(
        endpoint=endpoint,
        status="allowed",
        reason="",
        records=_records_from_zone(zone),
    )
