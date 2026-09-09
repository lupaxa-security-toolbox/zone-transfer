# Reference

## Attempt status

| Status    | Meaning                                               |
| :-------- | :---------------------------------------------------- |
| `allowed` | AXFR succeeded; `records` holds the zone              |
| `refused` | Server answered not permitted (`REFUSED` / `FORMERR`) |
| `error`   | Timeout, connect failure, or no addresses             |

## Exit codes

| Code | When                                                               |
| :--- | :----------------------------------------------------------------- |
| `0`  | Every domain was tested; refused and per-endpoint errors are OK    |
| `2`  | Invalid input, `NS` discovery failure, or `--fail-open` + allowed  |

## JSON shape

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

`error` is a string, never `null`. `records` is always a list.

## Progress events

`inspect_domain` and `inspect_many` accept optional `on_progress`. Each
call receives a `Progress` object (`domain`, `phase`, `message`,
`current`, `total`). Phases are `lookup` (NS discovery), `resolve`
(A/AAAA expansion), and `try` (one AXFR). The CLI uses this hook for a
stderr spinner on a TTY.

## Library exceptions

| Exception               | When                                                                                            |
| :---------------------- | :---------------------------------------------------------------------------------------------- |
| `InvalidTargetError`    | Empty domain, empty nameserver list, or empty `inspect_many`                                    |
| `NameserverLookupError` | Raised by `lookup_nameservers`; `inspect_domain` catches it into `DomainReport.error`           |
| `ZoneTransferError`     | Base class                                                                                      |
