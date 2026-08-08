# Helix SDK (Python)

Python client for a running [Helix](https://github.com/letslego/helix) console — the stable `/helix/v1/*` HTTP API.

```bash
pip install letslego-helix
# or: pip install "git+https://github.com/letslego/helix-sdk-python.git"
```

## Quick start

```python
from helix_sdk import HelixClient

helix = HelixClient("http://127.0.0.1:8787")

turn = helix.chat("Plan a weekend trip to Paris", auto_approve=True)
print(turn.reply)

again = helix.chat("Make it cheaper", turn.session_id)
print(again.reply)

if again.parked:
    sessions = helix.sessions()
    # helix.resolve_approval(session_id, approval_id, True)
```

## API

| Method | HTTP |
| --- | --- |
| `agent()` | `GET /helix/v1/agent` |
| `stack()` | `GET /helix/v1/stack` |
| `sessions()` | `GET /helix/v1/sessions` |
| `workflows(session_id?)` | `GET /helix/v1/workflows` |
| `events(session_id?)` | `GET /helix/v1/events` |
| `run(...)` / `chat(...)` | `POST /helix/v1/sessions` |
| `resolve_approval(...)` | `POST /helix/v1/approvals` |
| `run_schedule(name)` | `POST /helix/v1/schedules/run` |

Zero runtime dependencies (stdlib `urllib` only).

## Ecosystem

- Framework: [helix](https://github.com/letslego/helix)
- TypeScript SDK: [helix-sdk](https://github.com/letslego/helix-sdk)
- Go SDK: [helix-sdk-go](https://github.com/letslego/helix-sdk-go)
- Overview: [helix-ecosystem](https://letslego.github.io/helix-ecosystem/)

## License

Apache-2.0 © LetsLego
