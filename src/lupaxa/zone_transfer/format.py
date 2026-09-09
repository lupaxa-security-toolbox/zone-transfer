"""Render domain reports as tables or JSON-ready dicts."""

from __future__ import annotations

from prettytable import PrettyTable

from .models import DomainReport, TransferAttempt
from .style import color_name, color_status, color_title, color_value


def _style_name(text: str, color: bool) -> str:
    return color_name(text) if color else text


def _style_value(text: str, color: bool) -> str:
    return color_value(text) if color else text


def _style_status(text: str, color: bool) -> str:
    return color_status(text) if color else text


def report_payload(report: DomainReport) -> dict[str, object]:
    """JSON object for one domain. RR type is the ``type`` key."""
    attempts: list[dict[str, object]] = []
    for attempt in report.attempts:
        attempts.append(
            {
                "nameserver": attempt.endpoint.nameserver,
                "address": attempt.endpoint.address,
                "family": attempt.endpoint.family,
                "status": attempt.status,
                "reason": attempt.reason,
                "records": [
                    {
                        "name": record.name,
                        "type": record.rtype,
                        "ttl": record.ttl,
                        "rdata": record.rdata,
                    }
                    for record in attempt.records
                ],
            }
        )
    return {"domain": report.domain, "error": report.error, "attempts": attempts}


def reports_payload(reports: list[DomainReport]) -> list[dict[str, object]]:
    """JSON list for one CLI run."""
    return [report_payload(report) for report in reports]


def _status_table(report: DomainReport, *, color: bool) -> PrettyTable:
    table = PrettyTable()
    table.field_names = [
        _style_name("Nameserver", color),
        _style_name("Address", color),
        _style_name("Family", color),
        _style_name("Status", color),
        _style_name("Reason", color),
    ]
    table.title = color_title(report.domain) if color else f"Results for: {report.domain}"
    if report.error:
        table.add_row(
            [
                _style_value(report.error, color),
                "",
                "",
                _style_status("error", color),
                "",
            ]
        )
        return table
    for attempt in report.attempts:
        table.add_row(
            [
                _style_name(attempt.endpoint.nameserver, color),
                _style_value(attempt.endpoint.address, color),
                _style_value(attempt.endpoint.family, color),
                _style_status(attempt.status, color),
                _style_value(attempt.reason, color),
            ]
        )
    return table


def _zone_table(attempt: TransferAttempt, *, color: bool) -> PrettyTable:
    table = PrettyTable()
    table.field_names = [
        _style_name("Name", color),
        _style_name("Type", color),
        _style_name("TTL", color),
        _style_name("Rdata", color),
    ]
    host = attempt.endpoint.nameserver
    address = attempt.endpoint.address
    table.title = (
        color_title(f"{host} ({address})") if color else f"Results for: {host} ({address})"
    )
    for record in attempt.records:
        table.add_row(
            [
                _style_name(record.name, color),
                _style_value(record.rtype, color),
                _style_value(str(record.ttl), color),
                _style_value(record.rdata, color),
            ]
        )
    return table


def format_report(report: DomainReport, *, color: bool = False) -> str:
    """Status table, then a record table for each allowed transfer."""
    chunks = [str(_status_table(report, color=color))]
    for attempt in report.attempts:
        if attempt.status == "allowed" and attempt.records:
            chunks.append(str(_zone_table(attempt, color=color)))
    return "\n".join(chunks)
