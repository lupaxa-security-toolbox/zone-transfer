# Usage

Input is one or more domain names. Each name is inspected independently.
When `--nameserver` is set, that list is used for every domain and `NS`
discovery is skipped. Discovered nameservers are listed in name order.
When a nameserver has both IPv4 and IPv6 addresses, IPv4 is tried first.

## CLI flags

| Flag                 | Default       | Description                                     |
| :------------------- | :------------ | :---------------------------------------------- |
| `--nameserver`, `-n` | discover `NS` | Nameserver host or IP (repeatable)              |
| `--format`, `-f`     | `table`       | Output format: `table` or `json`                |
| `--fail-open`        | off           | Exit `2` if any endpoint allowed AXFR           |
| `--timeout`          | `10`          | DNS and AXFR timeout in seconds (must be `> 0`) |
| `--no-color`         | off           | Disable colour in table output                  |
| `--version`          | —             | Print the package version and exit              |

```bash
zone-transfer example.com
zone-transfer example.com example.org
zone-transfer example.com --nameserver ns1.example.net --nameserver 203.0.113.10
zone-transfer example.com --format json
zone-transfer example.com --fail-open
zone-transfer example.com --timeout 10 --no-color
```

Table output is a PrettyTable titled with the domain. Rows are
nameserver, address, family, status, and reason. For each `allowed`
attempt a second table lists name, type, TTL, and rdata. On a colour
terminal the title is cyan `Results for:` plus a bold white domain,
names are cyan, values are green, `allowed` is red, `refused` is green,
and `error` is grey. Pass `--no-color` or set `NO_COLOR` to disable.
While the inspection is running, a spinner on stderr shows the current
lookup or AXFR attempt. It is TTY-only and never written to stdout, so
JSON stays clean.

JSON is a list of objects with `domain`, `error`, and `attempts`. Each
attempt has `nameserver`, `address`, `family`, `status`, `reason`, and
`records`. Record objects use `type` (not `rtype`).

A domain-level `NS` discovery failure sets `error` and exits `2`. A
refused transfer is a normal result and exits `0` unless `--fail-open`
saw an `allowed` attempt.

## Library

```python
from lupaxa.zone_transfer import inspect_domain, inspect_many

report = inspect_domain("example.com")
pinned = inspect_domain("example.com", nameservers=["203.0.113.10"])
reports = inspect_many(["example.com", "example.org"], timeout=10.0)
```

`inspect_domain` does not raise when AXFR is refused or one address
fails. Those become attempt rows. Empty domains, an empty nameserver
list, or an empty `inspect_many` list raise `InvalidTargetError`.
Pass `on_progress` to receive `Progress` events (`lookup`, `resolve`,
`try`); the library stays silent unless that callback is set.
