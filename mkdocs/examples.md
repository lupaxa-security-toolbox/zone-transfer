# Examples

## Table (default)

```bash
zone-transfer example.com
```

## Several domains

```bash
zone-transfer example.com example.org
```

## Pin nameservers

```bash
zone-transfer example.com --nameserver ns1.example.net --nameserver 2001:db8::1
```

## JSON

```bash
zone-transfer example.com --format json
```

## CI-style finding

```bash
zone-transfer example.com --fail-open
```

## Library

```python
from lupaxa.zone_transfer import inspect_domain

report = inspect_domain("example.com", timeout=10.0)
for attempt in report.attempts:
    print(attempt.endpoint.address, attempt.status)
    for record in attempt.records:
        print(record.name, record.rtype, record.rdata)
```
