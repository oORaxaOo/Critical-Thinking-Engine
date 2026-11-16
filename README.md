# Critical Thinking Engine

A lightweight, privacy-first decision-support layer for Hermes Agent. The CTE
helps Lilith form and explain reasoned positions instead of defaulting to
agreement.

## v0.1 scope

- Conservative, deterministic intent classification
- NORMAL / REVIEW / CRITICAL review policy
- Review of technical proposals, decisions, and technical factual claims
- Clear position guidance: SUPPORT, CHANGE, REJECT, or INSUFFICIENT_INFORMATION
- Evidence-focused guidance for technical factual claims
- Hermes `pre_llm_call` context injection
- Optional KIE publication of bounded review metadata
- No additional model calls, network access, transcript storage, or third-party
  runtime dependencies
- Fail-open behavior: a CTE or optional KIE publication error never blocks the
  Hermes turn

The classifier is deliberately heuristic. It is a routing aid, not a truth
detector, and ambiguous messages should not automatically receive critical
review. When KIE publication is enabled, the original user message and
generated review context remain outside the KIE event ledger.

## Status

The initial v0.1 implementation and follow-up classifier improvements are
merged into `main`.

The plugin has **not** been installed or enabled in a live Hermes profile.
Unit tests and CI do not replace validation through the exact Hermes
installation that will run Lilith.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Hermes validation

From the repository root, using the same Hermes v0.23.1 installation intended
for Lilith:

```bash
hermes plugins validate .
hermes plugins doctor . --ci
```

These checks validate admission rules and exercise the real plugin
discovery/registration runtime in an isolated temporary Hermes home. They do
not enable the plugin in the active profile or prove behavior in a running
WhatsApp gateway.

See [Architecture](docs/ARCHITECTURE.md), [Privacy](docs/PRIVACY.md), and
[Configuration](docs/CONFIGURATION.md).
