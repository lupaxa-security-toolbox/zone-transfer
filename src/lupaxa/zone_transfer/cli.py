"""Command-line interface for Zone Transfer."""

from __future__ import annotations

import argparse
import json
import math
import sys

from .api import inspect_many
from .exceptions import InvalidTargetError
from .format import format_report, reports_payload
from .models import Progress
from .progress import StatusDisplay
from .style import use_color
from .version import get_version
from .xfr import DEFAULT_TIMEOUT


def _positive_timeout(value: str) -> float:
    timeout = float(value)
    if not math.isfinite(timeout) or timeout <= 0:
        raise argparse.ArgumentTypeError("timeout must be greater than 0")
    return timeout


def build_parser() -> argparse.ArgumentParser:
    """Build the ``zone-transfer`` argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Test whether a domain's nameservers allow DNS zone transfer (AXFR). "
            "Authorised use only."
        ),
    )
    parser.add_argument(
        "domains",
        nargs="+",
        help="Domain name(s) to test (for example example.com)",
    )
    parser.add_argument(
        "--nameserver",
        "-n",
        action="append",
        dest="nameservers",
        metavar="HOST-OR-IP",
        help="Nameserver to try (repeatable). If omitted, NS records are discovered",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=("table", "json"),
        default="table",
        help="Stdout format (default: table)",
    )
    parser.add_argument(
        "--fail-open",
        action="store_true",
        help="Exit 2 if any nameserver allowed AXFR",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_timeout,
        default=DEFAULT_TIMEOUT,
        metavar="SECONDS",
        help=f"DNS and AXFR timeout in seconds (default: {DEFAULT_TIMEOUT:g})",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colour in table output",
    )
    parser.add_argument("--version", action="version", version=get_version())
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code in (0, None):
            return 0
        if isinstance(code, int):
            return code
        return 2

    status = StatusDisplay(sys.stderr)

    def on_progress(event: Progress) -> None:
        status.show(event.message)

    try:
        try:
            reports = inspect_many(
                args.domains,
                nameservers=args.nameservers,
                timeout=args.timeout,
                on_progress=on_progress,
            )
        except InvalidTargetError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    finally:
        status.clear()

    if args.format == "json":
        print(json.dumps(reports_payload(reports), indent=2))
    else:
        color = not args.no_color and use_color(sys.stdout)
        for report in reports:
            print(format_report(report, color=color))

    if any(report.error or not report.attempts for report in reports):
        return 2
    if args.fail_open and any(
        attempt.status == "allowed" for report in reports for attempt in report.attempts
    ):
        return 2
    return 0
