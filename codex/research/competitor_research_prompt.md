# Competitive Research Pipeline for ComposioHQ Agent Orchestrator Analogs

Act as a deep competitive research pipeline manager.

Use Exa MCP for web search and crawling if available.

Do not rely on memory for factual claims.

Every important claim must include a source URL.

---

# Input files

Read these files before starting:

1. `research/target_project.md`
2. `research/competitor_filter_criteria.md`
3. `research/seed_candidates.md`

Use them as follows:

- `target_project.md` defines ComposioHQ Agent Orchestrator and the target capability baseline to extract.
- `competitor_filter_criteria.md` defines how to classify and score analogs.
- `seed_candidates.md` provides starting references only. It is not ground truth.

---

# Goal

Find the closest analogs, competitors, and adjacent inspiration projects for:

- https://github.com/ComposioHQ/agent-orchestrator

The final output should help decide:

1. Which projects are closest to ComposioHQ Agent Orchestrator?
2. Which projects are direct analogs?
3. Which projects are worktree/session managers but not full orchestrators?
4. Which projects are commercial platform competitors?
5. Which generic frameworks should be treated only as substrates?
6. Which projects are useful inspiration but not direct competitors?
7. What architectural patterns define this product category?
8. What gaps or opportunities exist for a smaller/local-first ai-orchestrator project?

---

# Required workflow

## Step 1: Target capability baseline

First inspect the target repository:

- https://github.com/ComposioHQ/agent-orchestrator

Look for:

- README
- CLAUDE.md if present
- docs
- packages
- CLI entrypoints
- dashboard/web app
- agent plugins
- runtime plugins
- worktree/session management
- GitHub/Linear integrations
- CI/review handling
- release notes
- issues/discussions that clarify actual usage

Produce a section called "Target Capability Baseline".

This section must summarize the actual capabilities of ComposioHQ Agent Orchestrator.

Do not score analogs before this baseline is built.

## Step 2: Research slices

Spawn or simulate separate research agents for these slices:

1. Direct coding-agent orchestrators.
2. Worktree/session managers.
3. Fleet-style coding-agent managers.
4. Claude Code / Codex / Cursor / OpenCode wrappers.
5. OpenHands / SWE-agent / Open SWE style systems.
6. Commercial or semi-commercial coding-agent platforms.
7. GitHub maturity and activity.
8. Missing analogs beyond the seed list.

Each slice should search independently and return structured findings.

## Step 3: Use the seed candidate list

Read:

- `research/seed_candidates.md`

Use this seed list as a starting pool only.

For every seed candidate:

1. Search/fetch primary sources.
2. Verify what the project actually does.
3. Classify it using `research/competitor_filter_criteria.md`.
4. Score it against the ComposioHQ Agent Orchestrator Target Capability Baseline.
5. Deduplicate it against related docs/repos.
6. Downrank it if it is generic, inactive, unrelated, or lacks real coding-agent orchestration.

Also search beyond the seed list for missing analogs.

The final report must not be limited to the seed list.

## Step 4: Candidate data schema

For each candidate, collect:

- name
- primary URL
- category
- direct analog score from 0 to 10
- reason for score
- license if available
- GitHub stars/forks if available
- last meaningful commit or release if available
- evidence of activity
- core architecture
- agent/session model
- fleet/multi-agent support
- worktree/branch/PR model
- role/model routing support
- task queue / loop / retry support
- CI failure handling
- review-comment handling
- merge-conflict handling
- dashboard/supervision UI
- GitHub/Linear/tracker integration
- runtime abstraction: tmux/process/ConPTY/Docker/etc.
- agent abstraction: Claude Code/Codex/Aider/OpenCode/etc.
- artifact/logging/event support
- local/self-hosted support
- local inference compatibility
- commercial/SaaS dependency if any
- why it matters as an analog of ComposioHQ Agent Orchestrator
- source URLs for important claims

## Step 5: Classification rules

Every candidate must be classified into exactly one primary category:

1. Direct analog.
2. Worktree/session manager.
3. Coding-agent orchestrator without full fleet/PR lifecycle.
4. Agent framework / substrate.
5. Coding-agent product / platform competitor.
6. Adjacent inspiration.
7. Noise / not relevant.

Do not classify generic frameworks as direct analogs unless they include a concrete coding-agent orchestration workflow.

Do not rank a famous framework above a small but highly relevant coding-agent orchestrator.

## Step 6: Scoring rules

Use a 0-10 direct analog score.

Score 9-10:

- very close analog
- fleet-style coding-agent orchestration
- multiple agents or sessions
- isolated worktrees/branches
- PR workflow
- CI failure handling
- review-comment handling
- dashboard or supervision layer
- agent/runtime abstraction
- active project with meaningful implementation

Score 7-8:

- strong analog
- significant overlap
- may miss one or two important capabilities such as dashboard, CI fixing, or tracker abstraction

Score 5-6:

- adjacent competitor
- relevant but not a direct substitute

Score 3-4:

- weakly related inspiration
- useful ideas but not a direct analog

Score 1-2:

- mostly irrelevant

Score 0:

- not relevant

---

# Required final report structure

Write the final report in Markdown.

The report must include these sections:

## 1. Executive Summary

Briefly summarize:

- the closest analogs to ComposioHQ Agent Orchestrator
- the strongest commercial competitors
- the most useful inspiration projects
- the biggest architectural patterns in this category
- the biggest opportunities for a smaller/local-first ai-orchestrator project

## 2. Target Capability Baseline

Summarize what ComposioHQ Agent Orchestrator actually does based on inspected sources.

## 3. Ranked Top 20 Analogs

A ranked list with:

- rank
- name
- category
- score
- URL
- why it matters

## 4. Top 5 Direct Analogs

Explain why each one is a close analog.

## 5. Top 5 Commercial/Product Competitors

Explain which closed or semi-closed platforms solve the same user problem.

## 6. Top 5 Inspiration Projects

Explain what architectural ideas can be borrowed.

## 7. Feature Matrix

Use a Markdown table.

Columns:

- Project
- Category
- Score
- Multi-agent/fleet
- Worktree/branch isolation
- PR workflow
- CI fixing
- Review-comment fixing
- Dashboard/supervision
- Agent abstraction
- Runtime abstraction
- Tracker integration
- CLI/local support
- Notes

## 8. Worktree and Session Managers

Separate tools that mainly coordinate worktrees/sessions from full coding-agent orchestrators.

## 9. Agent Frameworks and Substrates

Explain which frameworks are useful but not direct analogs.

## 10. Downranked or Excluded Candidates

List candidates that were checked but excluded/downranked.

For each, explain why.

## 11. Category Map

Create a map of the product category:

- fleet orchestrators
- session/worktree managers
- coding-agent platforms
- coding-agent frameworks
- PR/review automation tools
- generic multi-agent frameworks

## 12. Implications for ai-orchestrator

Explain what a smaller/local-first ai-orchestrator can learn from ComposioHQ Agent Orchestrator and its analogs.

Focus on:

- local-first orchestration
- multi-model routing
- Codex / Claude / Cursor / OpenCode interoperability
- artifact-driven workflows
- Git/worktree safety
- PR/review/CI loops
- cost-aware model routing
- local inference as helper layer
- overnight autonomous loops
- human-readable task files
- simpler setup than large fleet orchestrators

## 13. Recommended Roadmap for a Local-First Alternative

Split into:

### Immediate

What to improve in days.

### Short-term

What to improve in 1-3 weeks.

### Medium-term

What to improve in 1-2 months.

## 14. Source Appendix

List important sources used.

---

# Quality bar

The report should be useful to a founder or senior software architect.

Avoid vague statements.

Avoid hype.

Prefer concrete implementation details.

If a source is weak, say so.

If a project looks inactive, say so.

If a project is only a generic framework, do not pretend it is a direct analog.

If evidence is missing, mark the field as unknown instead of guessing.