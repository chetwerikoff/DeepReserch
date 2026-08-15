# GitHub Open-Set Research Overlay

Use this profile only when the candidate universe is open/unknown and the requested candidates are GitHub-hosted projects or repositories. It is a narrow overlay on `prompts/manager.md`, not a second workflow.

`prompts/manager.md` remains authoritative for path selection, candidate classes, request-specific screening criteria, task modes, `research_bounds`, `candidates.json`, accepted-finding provenance, shortlist-only deep research, the single bounded post-shortlist gap check, evidence gating, synthesis, and stop/saturation semantics. This profile adds only GitHub-specific query tactics, repository relationship interpretation, and technique/current-signal reporting guidance.

## Search path and evidence admission

Keep the existing worker execution contract unchanged: manager-authored discovery tasks run through the configured **Exa-first web search/read path with built-in web fallback**. GitHub REST/MCP may be used by the acting manager or verification environment only when it is already available and useful; it is optional and must not become a prerequisite, runner/tool-provisioning change, or alternate admission path.

A repository enters `candidates.json` only from accepted discovery evidence using the existing `<task-id>:<finding-id>` reference. Manager memory, an unrecorded API lookup, or an API-only observation that never reaches an accepted worker finding is not admission provenance.

Semantic fit comes before popularity/activity metadata. A materially relevant repository may reach screening with zero/few stars, sparse/no topics, a new/unfamiliar name, no obvious category term in its name/README, or little historical popularity metadata. Stars, forks, contributor counts, release counts, lifetime commits, and similar metadata are never admission gates.

## GitHub-specific discovery tactics

Adapt the generic discovery routes into GitHub-focused queries. These are query families, not extra runner phases or worker types.

### 1. Problem / user vocabulary

Search the problem as users and maintainers are likely to describe it, including symptom phrases, workflow pain points, desired outcomes, and domain language. Combine those phrases with repository-oriented context only where useful. Useful evidence surfaces include repository pages, README/docs pages, and issues/discussions that show the project materially addresses the problem.

Do not require the repository name or README title to contain the obvious category keyword when the evidence shows semantic relevance.

### 2. Product / category vocabulary

Search common project, library, framework, tool, protocol, plugin, server, client, runtime, or ecosystem category names plus aliases and neighboring terminology. Use repository pages and primary docs to establish what the project actually is rather than treating search-result labels or popularity as the candidate definition.

### 3. Mechanism / capability vocabulary

Search architecture, protocol, runtime, storage, orchestration, integration, data-flow, execution-model, or other mechanism/capability phrases that could solve the user's problem under a different product/category name. Distinctive technical phrases from accepted evidence are especially useful for finding projects that category-name searches miss.

A project discovered through a mechanism phrase is screened on semantic fit under the generic manager criteria, not on whether it uses the expected category label or has strong popularity metadata.

### 4. Adjacent / long-tail / relationship snowballing

From accepted discovery or shortlist evidence, inspect cheap relationship surfaces that may expose long-tail candidates: dependencies, inspirations, alternatives/related-work sections, linked projects, topics, distinctive phrases, issue/discussion references, forks/upstreams, and mirrors.

Use these relationships to reformulate the existing neighboring-ecosystem route and, when the generic gap check allows it, the existing single targeted follow-up discovery round. Do not add recursive traversal, a fork crawler, a graph store, or a second automatic discovery system.

## Forks, mirrors, and repository independence

Reuse the canonical-URL and semantic-independence rules from `prompts/manager.md`.

For GitHub specifically:

- when an unchanged or trivially changed fork/mirror is materially discovered, retain a distinct ledger entry only as needed to preserve discovery provenance, set `status: excluded`, and state the upstream/duplicate relationship in the reason;
- treat a fork as an independent candidate only when accepted evidence shows a materially independent design or product direction;
- do not count derivative forks/mirrors as independent corroboration, independent representative projects, or separate technique/trend/current-signal cluster evidence;
- when canonicalizing duplicates, preserve every accepted discovery reference and route that found the project;
- use cheap available repository/README/docs/relationship evidence for the judgment; do not spend budget on recursive relationship enumeration.

## Shortlist-only activity and momentum enrichment

Deep inspection remains shortlist-only. After screening, deep-research tasks for shortlisted repositories may collect inexpensive source-backed context such as:

- repository age or first-public-history context when available;
- recency of meaningful activity;
- recent release cadence;
- recent commit, contributor, issue, or PR activity when available inside the recorded run budget;
- upstream/fork/project relationships relevant to maturity or independence;
- recurring mechanisms or terminology across **independent** shortlisted projects.

Do not append deep-research tasks merely to obtain activity metadata for adjacent or excluded candidates. Those candidates may retain only metadata already encountered during discovery unless they later pass the normal shortlist gate.

## Technique, current activity/momentum, and trend

For GitHub current-signal analysis, record an observation timestamp or explicit date cutoff in `FINAL_REPORT.md`.

Use the terms conservatively:

- **technique / mechanism** — a technical pattern supported by relevant repository evidence; this makes no temporal claim;
- **current activity / momentum** — recent evidence such as releases, commits, contributors, issues, or PRs, interpreted with repository age/category context where that changes the meaning;
- **trend** — a stronger temporal claim that requires an explicit temporal basis: evidence of change/cadence over a stated window and/or a recently recurring mechanism/format across multiple independent projects.

If the evidence shows only present state, report activity, maturity, or momentum—not growth or trend strength. Raw stars, forks, lifetime commits, release totals, or any other single point-in-time/lifetime count never establish a trend. Do not create a composite score or numerical popularity/trend ranking. Prefer qualitative like-with-like comparisons when age/category materially changes interpretation.

## Final technique/current-signal map

For an open-set GitHub run, add a compact evidence-backed map to `FINAL_REPORT.md` using this conceptual shape:

```text
technique / current signal -> representative independent projects -> observed evidence -> maturity / caveat
```

Keep technique claims visibly separate from temporal claims. Every substantive project, mechanism, activity, momentum, or trend statement in the map must resolve through accepted deep-research evidence under the normal synthesis/evidence gate. Excluded derivative forks/mirrors cannot supply an additional independent project count.

## GitHub inputs to the existing gap check

Do not create another gap-check system. Feed GitHub-specific discoveries into the single manager-owned post-shortlist gap check already defined in `prompts/manager.md`, especially:

- newly learned mechanism/capability phrases;
- dependencies, inspirations, related-work, and linked-project references;
- upstream/fork/mirror relationships;
- distinctive terminology from shortlisted projects;
- evidence that discovery is biased toward established/popular repositories.

If the one allowed follow-up discovery round still returns material novelty, stop automatic discovery and report `saturation not demonstrated` exactly as the generic workflow requires.

## Verification controls for this profile

When verifying this profile, define the controls **before inspecting the run outcome**, record why each is a valid control, and exercise them through the ordinary runner/evidence path rather than direct-name admission shortcuts:

1. a semantically relevant metadata-poor/long-tail repository;
2. a relevant repository discoverable only through mechanism/capability vocabulary;
3. an upstream repository plus an unchanged/trivial fork or mirror;
4. a new low-star relevant repository with recent meaningful activity.

The expected behavior is: the metadata-poor and low-star controls are not rejected for weak popularity metadata; the mechanism-only control can enter screening through accepted discovery evidence; the derivative fork is retained as an excluded duplicate when materially discovered and does not count as independent corroboration or technique/current-signal/trend evidence; and recent activity may support current momentum when deeply evidenced after shortlisting, but weak star count by itself never becomes a growth/trend claim.
