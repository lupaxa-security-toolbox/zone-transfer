<!-- markdownlint-disable -->
<p align="center">
  <a href="https://github.com/lupaxa-security-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/security-toolbox/readme-logo.png" alt="Project Logo" width="256"/><br/>
  </a>
</p>
<h3 align="center">
  The Lupaxa Security Toolbox<br />
  Part of The Lupaxa Project
</h3>

<br />

# lupaxa-zone-transfer

Test whether a domain's nameservers allow DNS zone transfer (AXFR),
and show the zone contents when they do.

> **Warning — authorised use only.** This tool contacts nameservers and
> can expose a full zone. Use it only on systems you are allowed to test.

## Features

- Discover authoritative `NS` records or use repeatable `--nameserver` values
- Sort nameservers by name; for each host, try IPv4 before IPv6
- Resolve every IPv4 and IPv6 address for nameserver hostnames
- Try AXFR against every discovered endpoint
- Report `allowed`, `refused`, and `error` outcomes
- Print transferred records with name, type, TTL, and rdata
- Human-readable table (colour on a TTY; `--no-color` or `NO_COLOR` to disable), or JSON
- Spinner on stderr while nameserver lookup and AXFR run (TTY only)
- Optional `--fail-open` exit status for CI-style security findings
- Library API (`inspect_domain` / `inspect_many`) and CLI (`zone-transfer`)
- Fully typed, linted, formatted, and tested

## Installation

### From PyPI

```bash
pip install lupaxa-zone-transfer
```

### From source (development mode)

```bash
pip install -e ".[dev]"
```

Requires Python 3.10+. Runtime dependencies: `dnspython`, `prettytable`,
and `colored`.

## Library quick start

```python
from lupaxa.zone_transfer import inspect_domain

report = inspect_domain("example.com")
print(report.attempts[0].status)
```

## CLI quick start

```bash
zone-transfer --help
zone-transfer example.com
zone-transfer example.com example.org
zone-transfer example.com --nameserver ns1.example.net --nameserver 203.0.113.10
zone-transfer example.com --format json
zone-transfer example.com --fail-open
zone-transfer example.com --timeout 10 --no-color
```

You can also run the CLI as a module:

```bash
python -m lupaxa.zone_transfer --help
python -m lupaxa.zone_transfer --version
```

## Documentation

Online documentation:

[Documentation](https://zone-transfer.thelupaxaproject.org/)

Source repository:

[GitHub](https://github.com/lupaxa-security-toolbox/zone-transfer)

### Serve docs locally

From a clone of the repository:

```bash
make mkdocs-serve
```

Then open the local URL printed by MkDocs in your browser.

## Development

Clone the repository and install with Make:

```bash
make init                # first-time makefile-skills checkout
make python-install-dev  # editable install with [dev]
make python-check        # lint, type-check, and test
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
