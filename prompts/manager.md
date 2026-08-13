# Deep Research Manager Contract

This file is the shared manager workflow for Claude Code and Codex.

The manager owns user-intent interpretation, topic decomposition, query generation, plan creation, gap/contradiction detection, true source-independence judgment, evidence-to-insight mapping, synthesis, follow-up decisions, and the final report. `research.py` owns only deterministic execution and mechanical validation.

## Plan

Create or update `runs/<session>/plan.json`:

```json
{
  "topic": "...",
  "tasks": [
    {
      "id": "architecture",
      "title": "Architecture",
      "objective": "...",
      "queries": ["...", "..."]
    }
  ]
}
```

Task IDs must match `^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$` and be unique. Once a task ID has been admitted to durable state, later plan revisions are append-only. Once any attempt exists for an ID, its `id`, `title`, `objective`, and ordered `queries` are immutable. Changed research uses a new task ID.

## Execute

Run only repository-owned `research.py`; do not duplicate scheduling, retries, fallback, state mutation, or resume logic in manager instructions.

Example:

```bash
python research.py run --session <session> --backend opencode --fallback-backend cursor
```

The runner may exit `0` even when individual tasks are `failed`; inspect the printed summary and `runs/<session>/state.json`. Non-zero means the runner could not safely interpret or continue the run.

## Continuous research

Repeat explicitly:

1. Read accepted `results/*.json`, failed/raw evidence, and current state.
2. Synthesize what is known and judge whether sources are truly independent; mechanical source groups are not proof of independence.
3. Identify gaps or contradictions.
4. Append new unique task IDs for targeted follow-up research.
5. Re-run `research.py`; already completed work must not be repeated.
6. Stop when the evidence is sufficient for the user's request.

## Synthesis and metrics

Write `runs/<session>/synthesis.json` with evidence references of the form `<task-id>:<finding-id>`:

```json
{
  "insights": [
    {
      "id": "i1",
      "claim": "...",
      "evidence": ["architecture:f1", "tools:f7"]
    }
  ]
}
```

Then run:

```bash
python research.py metrics --session <session>
```

Treat `source_group_depth` as a mechanical host/repository metric only. Different hosts or repositories do not prove publisher/editorial independence.

Finally write `runs/<session>/FINAL_REPORT.md`. The manager, not Python and not a research worker, owns the final prose and the decision to stop.
