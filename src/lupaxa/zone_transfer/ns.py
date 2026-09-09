"""Discover NS hosts and expand them to every A/AAAA address."""

from __future__ import annotations

import ipaddress
from collections.abc import Iterable

import dns.resolver
from dns.exception import DNSException

from .exceptions import InvalidTargetError, NameserverLookupError
from .models import Endpoint, NameServer


def _query(name: str, rdtype: str, timeout: float) -> Iterable[object]:
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout
    resolver.timeout = timeout
    return resolver.resolve(name, rdtype)


def _host_text(rdata: object) -> str:
    target = getattr(rdata, "target", "")
    to_text = getattr(target, "to_text", None)
    text = str(to_text()) if callable(to_text) else str(target)
    return text.rstrip(".")


def _name_sort_key(name: str) -> str:
    return name.casefold()


def _endpoint_sort_key(endpoint: Endpoint) -> tuple[str, int, str]:
    family_rank = {"IPv4": 0, "IPv6": 1}.get(endpoint.family, 2)
    return (_name_sort_key(endpoint.nameserver), family_rank, endpoint.address)


def lookup_nameservers(domain: str, *, timeout: float = 10.0) -> list[NameServer]:
    """Query ``NS`` records for ``domain`` and return them in name order."""
    name = domain.strip()
    if not name:
        raise InvalidTargetError("empty domain")
    try:
        answers = _query(name, "NS", timeout)
    except dns.resolver.NXDOMAIN as exc:
        raise NameserverLookupError(f"Domain '{name}' does not exist.") from exc
    except dns.resolver.Timeout as exc:
        raise NameserverLookupError("DNS query timeout occurred.") from exc
    except dns.resolver.NoNameservers as exc:
        raise NameserverLookupError("No name servers were found.") from exc
    except dns.resolver.NoAnswer as exc:
        raise NameserverLookupError(f"Domain '{name}' has no NS records.") from exc
    except DNSException as exc:
        raise NameserverLookupError(str(exc) or "NS lookup failed.") from exc

    servers = [NameServer(name=_host_text(rdata)) for rdata in answers]
    if not servers:
        raise NameserverLookupError(f"Domain '{name}' has no NS records.")
    return sorted(servers, key=lambda server: _name_sort_key(server.name))


def _as_ip(value: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    try:
        return ipaddress.ip_address(value)
    except ValueError:
        return None


def _addresses_for(name: str, rdtype: str, timeout: float) -> tuple[list[str], str]:
    try:
        answers = _query(name, rdtype, timeout)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return [], ""
    except dns.resolver.Timeout:
        return [], "DNS query timeout occurred."
    except DNSException as exc:
        return [], str(exc) or "DNS lookup failed."
    found = [str(getattr(rdata, "address", "")).strip() for rdata in answers]
    return sorted(address for address in found if address), ""


def expand_nameservers(values: list[str], *, timeout: float = 10.0) -> list[Endpoint]:
    """Turn hostnames and IP literals into endpoints (name order, IPv4 then IPv6)."""
    endpoints: list[Endpoint] = []
    for raw in values:
        value = raw.strip()
        if not value:
            continue
        parsed = _as_ip(value)
        if parsed is not None:
            family = "IPv4" if parsed.version == 4 else "IPv6"
            endpoints.append(Endpoint(nameserver=value, address=value, family=family))
            continue
        ipv4, error_v4 = _addresses_for(value, "A", timeout)
        ipv6, error_v6 = _addresses_for(value, "AAAA", timeout)
        if not ipv4 and not ipv6:
            endpoints.append(
                Endpoint(
                    nameserver=value,
                    address="",
                    family="",
                    resolve_error=error_v4 or error_v6,
                )
            )
            continue
        for address in ipv4:
            endpoints.append(Endpoint(nameserver=value, address=address, family="IPv4"))
        for address in ipv6:
            endpoints.append(Endpoint(nameserver=value, address=address, family="IPv6"))
    return sorted(endpoints, key=_endpoint_sort_key)
