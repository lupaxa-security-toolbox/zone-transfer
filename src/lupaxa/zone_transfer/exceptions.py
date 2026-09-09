"""Errors raised by the public Zone Transfer API."""

from __future__ import annotations


class ZoneTransferError(Exception):
    """Base error for Zone Transfer."""


class InvalidTargetError(ZoneTransferError):
    """The domain or nameserver list is empty or invalid."""


class NameserverLookupError(ZoneTransferError):
    """NS discovery failed for a domain."""
