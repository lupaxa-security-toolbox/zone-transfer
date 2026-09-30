<p align="center">
  <a href="https://github.com/lupaxa-security-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/security-toolbox/readme-logo.png" alt="Security Toolbox" />
  </a>
</p>

<h1 align="center">Zone Transfer</h1>

Test whether a domain's nameservers allow DNS zone transfer (AXFR),
and show the zone contents when they do.

> **Warning:** **Authorised use only.** This tool contacts nameservers and can expose
> a full zone. Use it only on systems you are allowed to test.

## Install

Requires Python 3.10+. Runtime dependencies (`dnspython`, `prettytable`,
and `colored`) install with the package.

```bash
pip install lupaxa-zone-transfer
zone-transfer --help
```

You can also run `python -m lupaxa.zone_transfer`.

## CLI

```bash
zone-transfer example.com
zone-transfer example.com example.org
zone-transfer example.com --nameserver ns1.example.net --nameserver 203.0.113.10
zone-transfer example.com --format json
zone-transfer example.com --fail-open
zone-transfer example.com --timeout 10 --no-color
python -m lupaxa.zone_transfer --version
```

Each domain is inspected independently. The tool discovers `NS` records
(or uses `--nameserver` for every domain and skips discovery), sorts
hosts by name with IPv4 before IPv6, and tries AXFR on every address.
On a TTY a spinner on stderr shows the current lookup or transfer.
`--fail-open` exits `2` if any server allowed AXFR.

| Flag                 | Default       | Description                                     |
| :------------------- | :------------ | :---------------------------------------------- |
| `--nameserver`, `-n` | discover `NS` | Nameserver host or IP (repeatable)              |
| `--format`, `-f`     | `table`       | Output format: `table` or `json`                |
| `--fail-open`        | off           | Exit `2` if any endpoint allowed AXFR           |
| `--timeout`          | `10`          | DNS and AXFR timeout in seconds (must be `> 0`) |
| `--no-color`         | off           | Disable colour in table output                  |
| `--version`          | —             | Print the package version and exit              |

Table output is titled with the domain. Rows are nameserver, address,
family, status, and reason. For each `allowed` attempt a second table
lists name, type, TTL, and rdata. On a colour terminal, `allowed` is
red, `refused` is green, and `error` is grey. Pass `--no-color` or set
`NO_COLOR` for plain text.

JSON is a list of `{domain, error, attempts}` objects. Each attempt has
`nameserver`, `address`, `family`, `status`, `reason`, and `records`.
Record objects use `type` (not `rtype`). `error` is a string, never
`null`. `records` is always a list.

```json
[
  {
    "domain": "example.com",
    "error": "",
    "attempts": [
      {
        "nameserver": "ns1.example.net",
        "address": "203.0.113.10",
        "family": "IPv4",
        "status": "allowed",
        "reason": "",
        "records": [
          {"name": "@", "type": "SOA", "ttl": 3600, "rdata": "ns1.example.net. hostmaster. 1 1 1 1 1"}
        ]
      }
    ]
  }
]
```

### Attempt Status

| Status    | Meaning                                               |
| :-------- | :---------------------------------------------------- |
| `allowed` | AXFR succeeded; `records` holds the zone              |
| `refused` | Server answered not permitted (`REFUSED` / `FORMERR`) |
| `error`   | Timeout, connect failure, or no addresses             |

### Exit Codes

| Code | When                                                              |
| :--- | :---------------------------------------------------------------- |
| `0`  | Every domain was tested; refused and per-endpoint errors are OK   |
| `2`  | Invalid input, `NS` discovery failure, or `--fail-open` + allowed |

A domain-level `NS` discovery failure sets `error` and exits `2`. A
refused transfer is a normal result and exits `0` unless `--fail-open`
saw an `allowed` attempt.

## Library

```python
from lupaxa.zone_transfer import inspect_domain, inspect_many

report = inspect_domain("example.com")
pinned = inspect_domain("example.com", nameservers=["203.0.113.10"])
reports = inspect_many(["example.com", "example.org"], timeout=10.0)

for attempt in report.attempts:
    print(attempt.endpoint.address, attempt.status)
    for record in attempt.records:
        print(record.name, record.rtype, record.rdata)
```

`inspect_domain` does not raise when AXFR is refused or one address
fails. Those become attempt rows. Empty domains, an empty nameserver
list, or an empty `inspect_many` list raise `InvalidTargetError`.
`NameserverLookupError` is raised by `lookup_nameservers`;
`inspect_domain` catches it into `DomainReport.error`.
`ZoneTransferError` is the base class.

Pass `on_progress` to receive `Progress` events (`domain`, `phase`,
`message`, `current`, `total`). Phases are `lookup` (NS discovery),
`resolve` (A/AAAA expansion), and `try` (one AXFR). The library does
not print; the CLI uses that hook for the spinner.

## Development

```bash
make init
make python-install-dev
make python-check
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
