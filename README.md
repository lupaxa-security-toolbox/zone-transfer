<p align="center">
  <a href="https://github.com/lupaxa-security-toolbox">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/organisations/security-toolbox/readme-logo.png" alt="Security Toolbox" />
  </a>
</p>

<h1 align="center">zone-transfer</h1>

Test whether a domain's nameservers allow DNS zone transfer (AXFR),
and show the zone contents when they do.

> [!WARNING]
> **Authorised use only.** This tool contacts nameservers and can expose
> a full zone. Use it only on systems you are allowed to test.

<p align="center">
  <a href="https://zone-transfer.thelupaxaproject.org/">Documentation</a>
  ·
  <a href="https://github.com/lupaxa-security-toolbox/zone-transfer">GitHub</a>
</p>

## Install

```bash
pip install lupaxa-zone-transfer
zone-transfer --help
```

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

The tool discovers `NS` records (or uses `--nameserver`), tries AXFR on
every IPv4 and IPv6 address, prints a status table, and dumps records
when a transfer is allowed. On a TTY it shows a spinner on stderr while
lookups and transfers run. `--fail-open` exits `2` if any server
allowed AXFR. `--format json` writes `{domain, error, attempts}`
objects. On a colour terminal, `allowed` is red and `refused` is green.

## Library

```python
from lupaxa.zone_transfer import inspect_domain

report = inspect_domain("example.com")
print(report.attempts[0].status)
```

Pass `on_progress` to receive lookup and transfer events. The library
does not print; the CLI uses that hook for the spinner.

## Development

```bash
make init
make python-install-dev
make python-check
make mkdocs-serve
```

<a href="https://github.com/the-lupaxa-project">
    <img src="https://raw.githubusercontent.com/the-lupaxa-project/brand-assets/master/logos/components/footer-for-child-orgs.svg" alt="The Lupaxa Project Footer" width="100%" />
</a>
