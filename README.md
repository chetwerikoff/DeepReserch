# DeepReserch runner

`research.py` is a small vendor-neutral execution layer for manager-owned deep research. Claude Code or Codex plans and synthesizes; OpenCode or Cursor CLI workers execute narrow source-backed research tasks; Python owns deterministic scheduling, validation, durable state, recovery, and mechanical source-group metrics.

## Requirements

- Python 3.11+ standard library only.
- At least one installed/authenticated worker CLI: OpenCode or Cursor CLI.
- No database, daemon, queue, workflow engine, YAML contract, Pydantic, or JSON-schema package.

## Run layout

```text
runs/<session>/
  plan.json
  state.json
  raw/
  results/
  synthesis.json
  metrics.json
  FINAL_REPORT.md
```

`runs/**` is ignored by Git.

## Manager workflow

Follow `prompts/manager.md`. A minimal plan is:

```json
{
  "topic": "Compare two approaches",
  "tasks": [
    {
      "id": "architecture",
      "title": "Architecture",
      "objective": "Find primary-source evidence about the architecture",
      "queries": ["official architecture docs", "repository design"]
    }
  ]
}
```

Run OpenCode workers with Cursor fallback:

```bash
python research.py run --session demo --backend opencode --fallback-backend cursor --max-workers 4
```

Or use Cursor as primary:

```bash
python research.py run --session demo --backend cursor
```

A task-local failure remains data and the command exits `0`; inspect the summary or:

```bash
python research.py status --session demo
```

Runner-fatal admission/state/backend-configuration errors exit non-zero.

## Research-safe worker modes

Research workers never write result files themselves. They return their answer on stdout; `research.py` captures the exact stdout/stderr bytes into a no-clobber raw-attempt envelope and writes validated normalized results.

### Cursor

Cursor is invoked non-interactively with Ask mode and runner-owned Exa MCP configuration:

```text
cursor-agent --print --mode=ask --output-format text --approve-mcps --workspace <runner-run-directory> <prompt>
```

At launch, the runner writes `<runner-run-directory>/.cursor/mcp.json` with only the remote
`exa` server (`https://mcp.exa.ai/mcp`) and points Cursor at that workspace. `--approve-mcps`
is required for non-interactive MCP use, but Cursor documents it as approving **all** configured
MCP servers; it has no per-server approval flag. Project-level config and `CURSOR_CONFIG_DIR`
were tested as narrower alternatives: project config still merges global servers, and the
environment variable is not a supported CLI configuration mechanism. Thus a clean host gets
only runner-configured Exa, while a host with extra global MCPs (such as this verification host)
will approve those too; the runner cannot scope that Cursor approval further.

The runner never adds `--force`/`--yolo` and never falls back to a write-capable Cursor mode.
Cursor CLI exposes its native `webSearchRequestQuery`/web fetch interaction but no mechanical
deny configuration for those built-in web tools. Ask mode leaves those requests approval-gated
(and the non-interactive runner rejects them), which is not equivalent to an explicit deny; this
remains a documented Cursor security gap. The executable can be overridden with `--cursor-command`.

### OpenCode

OpenCode is invoked with `opencode run` and a runner-owned inline agent. `OPENCODE_CONFIG_CONTENT` is merged at runtime so both the global permission layer and the selected `deep-research-worker` agent explicitly deny:

- `edit`
- `bash`
- `external_directory`
- `task`

The injected config defines only the remote Exa MCP server and allows its exact
`exa_web_search_exa`/`exa_web_fetch_exa` tools at both permission layers. OpenCode's built-in
`websearch` and `webfetch` tools remain allowed at both layers as a fallback when Exa is
unavailable, errors, or returns insufficient results. Exa preference is a prompt-level quality
policy, not a mechanical guarantee; the existing closed-world agent default and `read` rules
denying `*.env`/`*.env.*` remain in force.

The invocation selects that agent and does not attach to an arbitrary pre-existing `opencode serve` process. The executable can be overridden with `--opencode-command`.

These controls are mechanical. The worker prompt also says not to write, but prompt wording is not the security boundary.

## Durable attempts and recovery

Before every external worker subprocess starts, `state.json` atomically records the attempt ordinal, kind, backend, and `in_flight` phase. That write consumes the lifetime attempt.

If the runner dies after this durable start but before a complete raw outcome exists, restart marks the task `failed` with an interrupted/unknown reason and **does not replay the external call**. If a complete raw envelope exists, restart can safely continue the deterministic transition table without relaunching that attempt.

The automatic lifetime policy is closed:

1. primary research;
2. optional primary format repair after invalid JSON/required fields;
3. optional fallback research;
4. never a fourth invocation, never a repair of fallback output, and never a same-backend process retry.

A completed normalized result is fingerprint-bound to its immutable task definition. If a crash happens after the result file is durable but before `state.json` reaches `completed`, resume validates and reconciles the result without relaunching the worker.

## Source-group metrics

After the manager writes `synthesis.json`, run:

```bash
python research.py metrics --session demo
```

For GitHub URLs the group is `github.com/<owner>/<repo>`; other URLs group by normalized hostname. Duplicate findings from one group count once. `metrics.json` includes per-insight depth, average, median, minimum, weak insight IDs (`depth < 2`), and each insight's group list.

This is **not** publisher/editorial independence and is **not** a completeness or saturation score. The manager must make those judgments.

## Verification

Deterministic unit tests:

```bash
python -m unittest -v tests.test_research
```

### Live Cursor smoke (conditional but mandatory when installed/authenticated)

Use a disposable clean Git checkout. Record `git status --porcelain` before and after. Create a one-task plan whose answer can be found through web/read tools, then run:

```bash
python research.py run --session smoke-cursor --backend cursor --max-workers 1
```

PASS requires:

- accepted parseable `results/<task>.json`;
- raw attempt captured;
- actual invocation uses `--mode=ask`;
- `git status --porcelain` is identical before and after.

If Cursor is unavailable or unauthenticated on the verification host, record that explicit skip; do not claim live verification.

### Live OpenCode smoke (conditional but mandatory when installed/authenticated)

In a separate disposable clean checkout, run:

```bash
python research.py run --session smoke-opencode --backend opencode --max-workers 1
```

PASS requires:

- accepted parseable result;
- raw attempt captured;
- invocation selects `deep-research-worker` and injects runtime denies for `edit`, `bash`, `external_directory`, and `task`;
- repository status is unchanged.

If OpenCode is unavailable or unauthenticated on the verification host, record that explicit skip; do not claim live verification.
