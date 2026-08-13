# Deep Research Manager Contract

This file is the shared manager workflow for Claude Code and Codex.

The manager owns user-intent interpretation, topic decomposition, query generation, plan creation, candidate discovery and screening, gap/contradiction detection, true source-independence judgment, evidence-to-insight mapping, synthesis, bounded follow-up decisions, and the final report. `research.py` owns only deterministic execution and mechanical validation; do not move research strategy into the runner.

## Choose the research path

Use the candidate-discovery workflow only when the candidate or solution universe is **open or unknown**: for example, when the user asks to discover analogs, alternatives, tools, approaches, candidate solutions, or recommendations from a broader option space.

A closed-set request such as “compare A and B and recommend one” stays a direct comparison/research task. Do not manufacture candidate classes or broad discovery unless the user explicitly asks to find alternatives, broaden the set, or discover the surrounding solution space.

Before the first `research.py run`, choose and record concrete practical bounds in the manager-owned `runs/<session>/plan.json`: total task budget, follow-up task budget, concurrency, per-task timeout, and, only where the selected backend can honor them, iteration/tool-call guidance. The first execution must use the recorded `max_workers` and `per_task_timeout_seconds` values via the runner's existing `--max-workers` and `--timeout` controls. If the selected backend cannot portably honor iteration/tool-call guidance, record `backend_guidance` as `null` rather than a placeholder. Do not start execution until these bounds are durable. Do not silently increase them later in the run. If a bound is exhausted, synthesize accepted evidence already collected and disclose the limitation instead of silently continuing.

## Plan

Create or update `runs/<session>/plan.json`:

```json
{
  "topic": "...",
  "research_bounds": {
    "task_budget": 12,
    "follow_up_task_budget": 4,
    "follow_up_discovery_rounds": 1,
    "max_workers": 4,
    "per_task_timeout_seconds": 300,
    "backend_guidance": null
  },
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

`research_bounds` is manager-owned metadata and must contain the actual selected values before the first execution, not labels such as `"request-specific"` or `"optional"`. `task_budget` caps all task IDs admitted during the run; `follow_up_task_budget` is the subset available for tasks appended after the first execution. For open-set work, `follow_up_discovery_rounds` must be at most `1`; for a closed-set comparison it is `0` unless the user explicitly broadens discovery. `backend_guidance` is either a concrete backend-supported limit/guidance object or `null` when the selected backend cannot honor such a limit. Treat these recorded bounds as immutable for the run; a materially changed scope should use a new session rather than silently rewriting the budget after spend.

Task IDs must match `^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$` and be unique. Once a task ID has been admitted to durable state, later plan revisions are append-only. Once any attempt exists for an ID, its `id`, `title`, `objective`, and ordered `queries` are immutable. Changed research uses a new task ID.

For direct closed-set work, create the narrow research tasks needed for the supplied options and continue to **Execute**.

For open-set work, the initial plan contains **discovery tasks only**. Discovery is high-recall enumeration, not final recommendation or full comparison.

### Scope for open-set discovery

Before creating discovery tasks:

1. Define **3–5 candidate classes**, adapted from: direct analogs, architectural analogs, standalone components, alternative approaches, and methodologies/research. Do not let “analogs” collapse into only similar finished products.
2. Derive request-specific screening criteria from material user constraints and hard inclusion/exclusion conditions.
3. For important or high-cost runs, define a small request-specific thematic control set, normally 1–3 known-relevant examples, to test recall. Controls never auto-shortlist a candidate and never expand the follow-up cap.

### Discovery routes

Use 3–4 stable coarse routes whose combined coverage includes all of the following:

- **problem / user language** — how the user describes the problem;
- **product / category language** — how solutions are normally named;
- **mechanism / capability language** — architectural or functional properties that could solve the problem;
- **neighboring ecosystem / snowballing** — related-work pages, lists, directories, inspirations, dependencies, comparison articles, README links, citations, and terminology discovered from candidates.

The adapted 3–4 routes must collectively cover **category/products, mechanisms, components/methods, and adjacent/long-tail candidates**. Components/methods may be covered through the product/category, mechanism/capability, or neighboring-ecosystem route; this does not require a fifth runner phase or worker type.

Problem/user language and product/category language may be combined when that is sufficient, but never omit mechanism/capability or adjacent/long-tail coverage. These are query routes, not runner phases or worker types.

Popularity metadata is never an admission gate. Stars, forks, topics, implementation language, release count, and similar metadata may inform later maturity analysis, but must not prevent a materially relevant candidate from reaching screening.

Discovery workers should return one candidate-backed finding per material candidate using the existing finding contract. Do not spend discovery budget on full architecture, maturity, license, or recommendation analysis.

## Execute

Run only repository-owned `research.py`; do not duplicate scheduling, retries, fallback, state mutation, or resume logic in manager instructions.

Example:

```bash
python research.py run --session <session> --backend opencode --fallback-backend cursor --max-workers 4 --timeout 300
```

Use the values recorded in `plan.json.research_bounds` rather than copying the example values blindly, and do not invoke the runner with `--max-workers` or `--timeout` values that disagree with the recorded bounds.

The runner may exit `0` even when individual tasks are `failed`; inspect the printed summary and `runs/<session>/state.json`. Non-zero means the runner could not safely interpret or continue the run.

## Screening gate for open-set discovery

After the initial discovery run, read accepted `results/*.json`, failed/raw evidence, and current state, then write `runs/<session>/candidates.json`. This is a manager-owned artifact; `research.py` does not validate or interpret it.

Minimum shape:

```json
{
  "candidate_classes": ["direct-analog", "architectural-analog", "component"],
  "screening_criteria": {
    "hard_constraints": ["Must have an inspectable implementation or primary technical documentation"],
    "include_when": ["Covers a material part of the requested problem"],
    "exclude_when": ["No usable primary source exists"]
  },
  "research_bounds": {
    "task_budget": 12,
    "follow_up_task_budget": 4,
    "follow_up_discovery_rounds": 1,
    "max_workers": 4,
    "per_task_timeout_seconds": 300,
    "backend_guidance": null
  },
  "control_checks": [
    {
      "name": "known-relevant-example",
      "canonical_url": "https://...",
      "present": true,
      "observed_routes": ["mechanism", "adjacent-long-tail"]
    }
  ],
  "candidates": [
    {
      "name": "example",
      "canonical_url": "https://...",
      "category": "architectural-analog",
      "discovered_by": "mechanism:durable-workflow",
      "evidence_refs": ["discovery_mechanism_terms:candidate_1"],
      "status": "shortlisted",
      "reason": "Supports persistent state and resumable workers"
    }
  ]
}
```

Mirror the pre-run `plan.json.research_bounds` values into `candidates.json`; do not choose a new budget after discovery has already spent work.

Persist every materially distinct discovered candidate, including those not selected for deep research. Allowed statuses are exactly `shortlisted`, `adjacent`, and `excluded`.

Every candidate must have at least one accepted `<task-id>:<finding-id>` discovery reference in `evidence_refs`. Multiple references are allowed when several routes found the same candidate. The existing `plan.json` supplies the objective and exact queries behind those task IDs, so do not create a second query log or provenance service.

Do not insert a candidate from manager memory or inference without accepted discovery evidence. If a manager-known candidate appears material but discovery did not return it, ground it through an allowed targeted discovery task first, subject to the same bounded policy.

Use the normalized canonical URL of the primary repository, official documentation, or primary paper as candidate identity. Strip obvious tracking parameters and trailing-slash variants; when the project is the candidate, resolve repository subpages to the repository root. Merge URL variants while preserving all evidence references and discovery routes. Keep forks as separate candidates only when they have a materially independent design; otherwise retain them as explicit excluded fork duplicates.

For each candidate, apply the persisted request-specific criteria plus this qualitative rubric, without numeric scoring:

- what part of the user's problem it covers;
- whether it is a product, architecture, component, alternative approach, or methodology/research;
- whether a primary source exists;
- whether the project/source is current or historical;
- whether it satisfies the recorded hard constraints;
- why it is shortlisted, adjacent, or excluded.

The screening gate is complete only when each material discovered candidate has accepted-finding provenance and an explicit disposition consistent with the recorded criteria. This keeps `not discovered` distinct from `discovered and excluded`.

## Deep research the shortlist

Only after the screening gate, append new unique task IDs to `plan.json` for shortlisted candidates or sensible shortlist groups. Deep-research tasks may investigate capabilities, architecture, limitations, maturity/activity, license, primary evidence, differences from the user's target, and transferable ideas.

Do not deeply research every discovery result merely because it was found. Run `research.py` and inspect accepted deep-research results before gap analysis or synthesis.

## Gap check and bounded follow-up

For open-set work, perform one post-shortlist gap check. Check whether:

- every defined candidate class is represented;
- discovery depended on only one query vocabulary;
- the sample is biased toward only popular or well-known projects;
- smaller, newer, documentation-first, or historical-but-relevant solutions are missing;
- discovery produced mechanism/category terms that were never searched;
- official related-work, alternatives, inspirations, dependencies, or ecosystem links expose missing candidates;
- distinctive mechanism phrases from shortlisted candidates have been searched;
- siblings, forks, and close naming variants were distinguished from independent implementations;
- any request-specific control failed to appear naturally.

This is a bounded recipe, not a recursive discovery engine.

If a material gap exists, append **at most one targeted follow-up discovery round** using new task IDs and run it. Then:

1. update `candidates.json` with every newly discovered material candidate and accepted-finding provenance;
2. screen new candidates using the same criteria, unless the user's scope itself changed and the criteria are explicitly updated;
3. append any newly justified deep-research tasks for newly shortlisted candidates;
4. if such deep-research tasks were appended, run `research.py` again and inspect their accepted results before synthesis.

Automatic discovery has exactly two valid terminal outcomes:

- **early saturation** — a reasonable reformulation/snowballing pass adds no new material candidate or solution class;
- **follow-up budget exhausted** — after the single permitted follow-up discovery round, stop automatic discovery even if novelty is still appearing. Do not claim saturation; record `saturation not demonstrated` and the remaining uncertainty.

Never start a second automatic discovery round merely to prove completeness.

For direct closed-set work, targeted follow-up research may still be appended for evidence gaps or contradictions, but it must remain within the request-specific task/time budget and must not turn into broad candidate discovery unless the user asked for it.

## Synthesis, evidence gate, and metrics

Treat accepted `results/*.json` plus `synthesis.json` evidence references as the compact evidence ledger; do not create a second evidence database.

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

Each synthesized claim must resolve through accepted evidence references to canonical source URLs. Before writing `FINAL_REPORT.md`, apply a pre-ship evidence gate:

- remove or explicitly mark as unverified any recommendation-bearing claim with no accepted evidence reference;
- reject malformed or unresolvable evidence references;
- verify that the cited source actually supports the claimed evidence; if a citation resolves but the source does not support the claim, reject the claim or remove/mark it unverified before `FINAL_REPORT.md`. Citation existence alone is not claim support.

Normalize canonical URLs before comparing candidates or sources. Cluster obvious mirrors, forks, syndicated copies, and derivative republications before counting or reporting semantic corroboration depth. The manager owns this semantic source-independence judgment.

Then run:

```bash
python research.py metrics --session <session>
```

Treat `source_group_depth` as a mechanical host/repository metric only. Different hosts or repositories do not prove publisher/editorial independence, and the metric is not a completeness or saturation score.

Finally write `runs/<session>/FINAL_REPORT.md`. For open-set discovery, include a brief coverage section with:

- candidate classes searched;
- shortlisted candidates;
- notable adjacent candidates;
- important exclusions and reasons;
- whether discovery ended by early saturation or follow-up-budget exhaustion;
- known discovery limitations, including `saturation not demonstrated` when applicable.

Recommendations and detailed comparisons must use accepted deep-research evidence, not discovery-only snippets. A candidate first found in follow-up discovery may appear in a recommendation or detailed comparison only after any required deep-research task for that candidate/group has executed and its accepted result has been inspected.

The manager, not Python and not a research worker, owns the final prose and the bounded decision to stop.
