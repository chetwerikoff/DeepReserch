# Claude Code Deep Research Adapter

For deep-research work, follow the shared manager contract in `prompts/manager.md`.

Use `research.py` for worker launch, bounded concurrency, retry/fallback, durable state, resume, raw capture, normalization, and metrics. Do not recreate those mechanisms in Claude instructions.
