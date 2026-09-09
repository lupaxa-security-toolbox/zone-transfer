# Getting started

## Requirements

- Python 3.10 or newer
- `dnspython`, `prettytable`, and `colored` (installed with the package)

## Install

```bash
pip install lupaxa-zone-transfer
zone-transfer --help
```

Library import:

```python
from lupaxa.zone_transfer import inspect_domain

report = inspect_domain("example.com")
print(report.attempts[0].status)
```

Module entry point:

```bash
python -m lupaxa.zone_transfer --version
```

### From source (development)

```bash
make init
make python-install-dev
zone-transfer --version
```

## First run

Pass one or more domain names. The tool discovers `NS` records, expands
every address, and prints a status table. When a transfer is allowed it
also prints the zone records. On a colour terminal the table is
coloured; pass `--no-color` or set `NO_COLOR` for plain text:

```bash
zone-transfer example.com
zone-transfer example.com --no-color
```

Pin nameservers (hostnames or IPs). The same list is used for every
domain on the run:

```bash
zone-transfer example.com --nameserver ns1.example.net --nameserver 203.0.113.10
```

JSON output:

```bash
zone-transfer example.com --format json
```

Treat an allowed transfer as a finding:

```bash
zone-transfer example.com --fail-open
```

## Makefile helpers

```bash
make init                 # clone makefile-skills into .makefiles/
make python-install-dev   # editable install with [dev]
make python-check         # lint + type + test
make mkdocs-serve         # local docs site
```
