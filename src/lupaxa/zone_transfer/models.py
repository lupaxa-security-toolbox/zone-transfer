"""Report types for a zone-transfer inspection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NameServer:
    """One nameserver hostname or literal address."""

    name: str


@dataclass(frozen=True)
class Endpoint:
    """One resolved address for a nameserver."""

    nameserver: str
    address: str
    family: str
    resolve_error: str = ""


@dataclass(frozen=True)
class ZoneRecord:
    """One resource record from an allowed AXFR."""

    name: str
    rtype: str
    ttl: int
    rdata: str


@dataclass(frozen=True)
class TransferAttempt:
    """One AXFR try against one endpoint."""

    endpoint: Endpoint
    status: str
    reason: str
    records: list[ZoneRecord]


@dataclass(frozen=True)
class DomainReport:
    """Inspection result for one domain."""

    domain: str
    error: str
    attempts: list[TransferAttempt]


@dataclass(frozen=True)
class Progress:
    """One inspection-progress event for a caller-supplied callback."""

    domain: str
    phase: str
    message: str
    current: int = 0
    total: int = 0
