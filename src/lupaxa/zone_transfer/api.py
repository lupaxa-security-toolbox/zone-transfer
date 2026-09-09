"""Inspect one or more domains for open AXFR."""

from __future__ import annotations

from collections.abc import Callable

from .exceptions import InvalidTargetError, NameserverLookupError
from .models import DomainReport, Progress, TransferAttempt
from .ns import expand_nameservers, lookup_nameservers
from .xfr import DEFAULT_TIMEOUT, transfer_zone

OnProgress = Callable[[Progress], None]


def _emit(on_progress: OnProgress | None, event: Progress) -> None:
    if on_progress is not None:
        on_progress(event)


def inspect_domain(
    domain: str,
    *,
    nameservers: list[str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    on_progress: OnProgress | None = None,
) -> DomainReport:
    """Discover or use nameservers, expand addresses, and try AXFR on each."""
    name = domain.strip()
    if not name:
        raise InvalidTargetError("empty domain")

    if nameservers is None:
        _emit(
            on_progress,
            Progress(
                domain=name,
                phase="lookup",
                message=f"Looking up nameservers for {name}...",
            ),
        )
        try:
            values = [server.name for server in lookup_nameservers(name, timeout=timeout)]
        except NameserverLookupError as exc:
            return DomainReport(domain=name, error=str(exc), attempts=[])
    else:
        values = [item.strip() for item in nameservers if item.strip()]
        if not values:
            raise InvalidTargetError("empty nameserver list")

    _emit(
        on_progress,
        Progress(
            domain=name,
            phase="resolve",
            message=f"Resolving nameserver addresses for {name}...",
        ),
    )
    endpoints = expand_nameservers(values, timeout=timeout)
    if not endpoints:
        return DomainReport(
            domain=name,
            error="no usable nameserver endpoints",
            attempts=[],
        )

    total = len(endpoints)
    attempts: list[TransferAttempt] = []
    for index, endpoint in enumerate(endpoints, start=1):
        if not endpoint.address:
            attempts.append(
                TransferAttempt(
                    endpoint=endpoint,
                    status="error",
                    reason=endpoint.resolve_error or "no A/AAAA records",
                    records=[],
                )
            )
            continue
        _emit(
            on_progress,
            Progress(
                domain=name,
                phase="try",
                message=(f"Trying {endpoint.nameserver} ({endpoint.address}) [{index}/{total}]..."),
                current=index,
                total=total,
            ),
        )
        attempts.append(transfer_zone(name, endpoint, timeout=timeout))
    return DomainReport(domain=name, error="", attempts=attempts)


def inspect_many(
    domains: list[str],
    *,
    nameservers: list[str] | None = None,
    timeout: float = DEFAULT_TIMEOUT,
    on_progress: OnProgress | None = None,
) -> list[DomainReport]:
    """Inspect each domain independently; return results in input order."""
    if not domains:
        raise InvalidTargetError("empty domain list")
    return [
        inspect_domain(
            domain,
            nameservers=nameservers,
            timeout=timeout,
            on_progress=on_progress,
        )
        for domain in domains
    ]
