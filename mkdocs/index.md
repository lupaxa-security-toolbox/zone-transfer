# Zone Transfer

`lupaxa-zone-transfer` tests whether a domain's nameservers allow DNS
zone transfer (AXFR). It discovers every `NS` (or uses the list you
pass), tries every IPv4 and IPv6 address, and prints the zone when a
server allows the transfer.

!!! warning "Authorised use only"
    AXFR contacts the target nameservers and can expose the full zone.
    Use it only on systems you are allowed to test.

Install the package for the library API and the `zone-transfer` console
command:

```bash
pip install lupaxa-zone-transfer
zone-transfer example.com
```

You can also run `python -m lupaxa.zone_transfer`.

## What it does

- Looks up `NS` records, or uses `--nameserver` (repeatable)
- Resolves every `A` and `AAAA` for each nameserver hostname
- Tries AXFR on each address
- Prints a status table (`allowed` / `refused` / `error`)
- Dumps name, type, TTL, and rdata for every allowed transfer
- Colours the table on a TTY (`--no-color` or `NO_COLOR` to disable)
- Prints JSON with `--format json`
- Exits `2` with `--fail-open` when any server allowed AXFR
- Exposes `inspect_domain` / `inspect_many` as library functions

## Next steps

- [Getting started](getting-started.md) — install and first run
- [Usage](usage.md) — CLI flags and the library API
- [Reference](reference.md) — JSON fields, statuses, and exit codes
- [Examples](examples.md) — table, JSON, and library recipes
