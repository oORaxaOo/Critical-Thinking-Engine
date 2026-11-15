# Critical Thinking Engine

A lightweight, privacy-first decision-support layer for Hermes Agent. The CTE helps Lilith form and explain reasoned positions instead of defaulting to agreement.

## v0.1 scope

- Conservative, deterministic intent classification
- NORMAL / REVIEW / CRITICAL review policy
- Clear position guidance: SUPPORT, CHANGE, REJECT, or INSUFFICIENT_INFORMATION
- Hermes `pre_llm_call` context injection
- No additional model calls, network access, transcript storage, or third-party runtime dependencies
- Fail-open behavior: a CTE error never blocks the Hermes turn

## Repository status

The first implementation is on the `feat/cte-v0.1-core` branch. It is not installed into a live Hermes environment and is not yet validated against the user's Hermes runtime. Review the architecture and privacy boundaries in `docs/` before installation.

## Tests

```bash
python -m unittest discover -s tests -v
```

See [Architecture](docs/ARCHITECTURE.md), [Privacy](docs/PRIVACY.md), and [Configuration](docs/CONFIGURATION.md).
