# Configuration

## Install layout

Copy this repository's plugin directory contents into:

`~/.hermes/plugins/critical-thinking-engine/`

The directory must contain `plugin.yaml`, `__init__.py`, and the `critical_thinking/` package.

Enable the plugin through Hermes' normal plugin management workflow after reviewing the files. Restart the relevant Hermes process if required by the installed version.

## Current behavior

v0.1 has no user settings and registers only `pre_llm_call`. It does not register tools, commands, background jobs, or model providers.

## Verification

Run the standalone test suite:

`python -m unittest discover -s tests -v`

Then validate the plugin with the Hermes version actually installed:

`hermes plugins validate /path/to/critical-thinking-engine`

A successful unit test run does not replace live Hermes integration testing.
