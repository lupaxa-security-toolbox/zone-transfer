"""lupaxa.zone_transfer — test whether nameservers allow AXFR."""

from __future__ import annotations

from .api import inspect_domain, inspect_many
from .exceptions import InvalidTargetError, NameserverLookupError, ZoneTransferError
from .models import DomainReport, Endpoint, NameServer, Progress, TransferAttempt, ZoneRecord
from .version import __version__, get_version
from .xfr import DEFAULT_TIMEOUT

__all__ = [
    "DEFAULT_TIMEOUT",
    "DomainReport",
    "Endpoint",
    "InvalidTargetError",
    "NameServer",
    "NameserverLookupError",
    "Progress",
    "TransferAttempt",
    "ZoneRecord",
    "ZoneTransferError",
    "__version__",
    "get_version",
    "inspect_domain",
    "inspect_many",
]
