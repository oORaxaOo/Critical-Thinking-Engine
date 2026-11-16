# Configuration and Validation

## Install layout

For a future installation, the plugin root must contain `plugin.yaml`,
`__init__.py`, and the `critical_thinking/` package. The repository's tests
and documentation are not required by Hermes at runtime.

Do not copy or enable the plugin in the normal Hermes profile yet. Complete
the isolated checks below first.

## Current behavior

The CTE registers only `pre_llm_call`. It does not register tools, commands,
background jobs, or model providers.

## Optional KIE publication

When KIE is installed in the same Python environment as Hermes and the
`kie_database` setting is an absolute path, the CTE publishes one
`critical_thinking.review_result` event when it injects review context.

Only the classified intent, review level, fixed reason code, bounded signal
labels, and two boolean flags are transferred. The original user message,
conversation history, and generated prompt context are never sent to KIE.

Publication is fail-open: missing KIE, an invalid path, or a database error
does not block the CTE review hook. Without the setting, the plugin retains
its previous behavior.

Example plugin settings:

```yaml
plugins:
  entries:
    critical-thinking-engine:
      settings:
        kie_database: /absolute/path/to/kie-integration.sqlite3
```

The file remains owned by KIE. The CTE does not open or modify any engine
database. Protect the KIE file using host filesystem permissions.

## Validation against Hermes v0.23.1

Run these commands from the repository root, using the same Hermes
installation that will run Lilith:

```bash
hermes plugins validate .
hermes plugins doctor . --ci
```

- `validate` checks plugin admission requirements, manifest parsing,
  loadability, declared capabilities, and related catalog/security checks.
- `doctor` stages a copy in a temporary Hermes home, blocks outbound socket
  connections during the check, and loads the plugin through Hermes' real
  discovery and registration runtime.
- Neither command enables the plugin in the active profile.
- Neither command proves behavior inside the running WhatsApp gateway. A
  separate controlled integration test is still required.

Run the repository unit tests separately:

```bash
python -m unittest discover -s tests -v
```

Record the exact Hermes version and complete command output before deciding
whether the plugin is ready for installation.
