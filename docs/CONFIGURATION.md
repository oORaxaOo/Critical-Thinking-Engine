# Configuration

## Install layout

Copy this repository's plugin contents into:

`~/.hermes/plugins/critical-thinking-engine/`

The plugin root must contain `plugin.yaml`, `__init__.py`, and the `critical_thinking/` package. The repository's tests and documentation are not required by Hermes at runtime.

## Current behavior

v0.1 has no user settings and registers only `pre_llm_call`. It does not register tools, commands, background jobs, or model providers.

## Verification

Run the standalone test suite:

```bash
python -m unittest discover -s tests -v
```

Then run Hermes' plugin checks using the same installed Hermes version:

```bash
hermes plugins validate /path/to/critical-thinking-engine
hermes plugins doctor /path/to/critical-thinking-engine
```

`validate` checks the plugin package and declared registrations. `doctor` exercises plugin discovery, manifest loading, and `register(ctx)` in a temporary Hermes home. Neither command replaces a live integration test in the actual profile and gateway process.

Do not enable the plugin in the normal Hermes profile until the repository review and isolated doctor checks are satisfactory. A successful unit test run alone does not prove live compatibility.
