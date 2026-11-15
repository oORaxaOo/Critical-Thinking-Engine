# Privacy and Safety

CTE v0.1 is local, stateless, and fail-open.

- It does not persist user messages or assistant responses.
- It does not log message contents.
- It does not make network requests.
- It does not invoke an additional LLM.
- It does not execute tools or modify files, settings, or project state.
- If the hook encounters an error, it returns no context and Hermes proceeds normally.

The plugin receives the current message through Hermes' documented hook interface. It intentionally does not inspect or retain conversation history.
