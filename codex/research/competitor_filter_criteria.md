# Competitor Filtering Criteria for ComposioHQ Agent Orchestrator Analogs

## Purpose

This document defines how to filter, classify, and score projects when researching analogs of ComposioHQ Agent Orchestrator.

The goal is not to collect every AI agent framework.

The goal is to identify the closest direct analogs, worktree/session managers, commercial platform competitors, and useful inspiration projects for a coding-agent fleet orchestrator.

## Target project

Target:

- https://github.com/ComposioHQ/agent-orchestrator

ComposioHQ Agent Orchestrator should be treated as a coding-agent orchestration platform focused on managing multiple AI coding agents across isolated workspaces, branches, PRs, CI loops, and review loops.

## Definition of a close analog

A project is a close analog if it overlaps with at least 3 of these capabilities:

1. Runs multiple coding agents or coding-agent sessions.
2. Supports fleet-style orchestration of agents.
3. Creates or manages isolated workspaces, git worktrees, branches, or sessions.
4. Supports branch and PR lifecycle management.
5. Can route work to different agents, tools, CLIs, or models.
6. Can coordinate Claude Code, Codex, Aider, OpenCode, Cursor, OpenHands, SWE-agent, or similar coding agents.
7. Has task queue, loop, retry, or autonomous iteration support.
8. Integrates with GitHub, GitLab, Linear, issue trackers, PRs, reviews, or CI systems.
9. Can detect CI failures and ask agents to fix them.
10. Can detect review comments and ask agents to address them.
11. Provides dashboard, supervision UI, session view, logs, or event stream.
12. Supports local, self-hosted, or CLI-first operation.
13. Has runtime abstraction such as tmux, process, ConPTY, Docker, containers, or remote sandboxes.
14. Produces durable artifacts: logs, summaries, patches, task records, PR links, reports, session state.
15. Has safety controls: isolated workspaces, human gates, approval policies, retry caps, sandboxing, rollback, or dirty-tree checks.

## Special target-specific criteria

For this research, the strongest analogs to ComposioHQ Agent Orchestrator are projects that combine:

1. Multiple coding agents or sessions.
2. Isolated worktrees, branches, or workspaces.
3. PR lifecycle management.
4. CI failure handling.
5. Review-comment handling.
6. Dashboard or supervision layer.
7. Agent abstraction: Claude Code, Codex, Aider, OpenCode, Cursor, OpenHands, SWE-agent, or similar.
8. Runtime abstraction: tmux, process, ConPTY, Docker, containers, or similar.
9. GitHub, GitLab, Linear, or tracker integration.
10. Local, self-hosted, or CLI-first operation.

A project does not need to have all of these to be relevant, but projects with worktree/branch/PR/session orchestration should be ranked above generic multi-agent frameworks.

## Classification categories

Every candidate must be classified into exactly one primary category.

### 1. Direct analog

A project is a direct analog if it actually orchestrates multiple coding agents or coding-agent sessions and manages meaningful parts of the coding lifecycle.

Strong direct analog signals:

- manages multiple coding-agent sessions
- launches or coordinates Claude Code / Codex / Aider / OpenCode / Cursor / OpenHands / SWE-agent
- creates or manages git worktrees
- creates or manages branches
- creates or manages PRs
- tracks session/task lifecycle
- supports review/fix/test loops
- watches CI or test failures
- handles review comments
- stores artifacts, logs, summaries, or session state
- has CLI, dashboard, or supervision UI
- supports agent/runtime abstraction

### 2. Worktree/session manager

A project belongs here if it mainly coordinates multiple local coding-agent sessions, terminals, or Git worktrees.

It may be a direct analog if it also supports task execution, PR lifecycle, review loops, CI handling, or agent coordination.

Signals:

- creates or manages Git worktrees
- runs multiple agents in parallel
- manages terminal, tmux, shell, or process sessions
- coordinates local coding-agent instances
- helps the user supervise multiple concurrent coding tasks
- provides a UI or CLI for multiple agent sessions

### 3. Coding-agent orchestrator without full fleet/PR lifecycle

A project belongs here if it orchestrates coding agents or tasks but does not fully manage worktrees, branches, PRs, CI fixing, or review comments.

Signals:

- delegates coding tasks to agents
- supports planner / implementer / reviewer loops
- can run tests and feed failures back
- produces artifacts and summaries
- may lack PR lifecycle or dashboard supervision

### 4. Agent framework / substrate

A project belongs here if it is a general-purpose agent framework that could be used to build an orchestrator but is not itself a direct coding-agent fleet orchestrator.

Examples:

- LangGraph
- AutoGen
- CrewAI
- CAMEL
- generic multi-agent frameworks
- generic workflow frameworks
- generic agent runtime libraries

These projects should usually be classified as substrate or inspiration, not as direct analogs.

Do not classify a framework as a direct analog merely because it can theoretically build one.

### 5. Coding-agent product / platform competitor

A project belongs here if it competes at the product level, even if it is commercial, hosted, or closed-source.

Signals:

- cloud coding agents
- delegated coding tasks
- PR generation
- background agents
- GitHub integration
- issue-to-PR automation
- code review automation
- CI failure fixing
- review-comment fixing
- coding agent APIs
- dashboard or supervision interface

Examples may include Devin, Jules, Codegen, Factory, Cursor Cloud Agent, GitHub Copilot coding agent, OpenAI Codex, Qodo, or similar products.

### 6. Adjacent inspiration

A project belongs here if it is not a direct analog but has useful ideas for:

- memory
- task decomposition
- agent roles
- skill systems
- CLI design
- artifact storage
- review gates
- context preparation
- model routing
- local inference
- workflow UX
- session supervision
- worktree safety
- PR automation
- CI repair loops

### 7. Noise / not relevant

A project belongs here if it:

- is inactive or abandoned
- has no meaningful implementation
- is only a prompt collection
- has no coding-agent orchestration
- has no Git/test/review/PR loop
- is too generic
- is unrelated to autonomous development workflows
- is only a library without a concrete coding-agent workflow
- is a marketing page without usable technical detail

## Direct analog scoring

Use a 0-10 score.

### Score 9-10: Very close direct analog

The project directly overlaps with ComposioHQ Agent Orchestrator.

It likely includes most of:

- fleet-style coding-agent orchestration
- multiple agents or sessions
- isolated worktrees, branches, or workspaces
- PR workflow
- CI failure handling
- review-comment handling
- dashboard or supervision layer
- agent abstraction
- runtime abstraction
- tracker integration
- persistent artifacts/logs
- active implementation

### Score 7-8: Strong analog

The project has strong overlap but may miss one or two important capabilities.

Examples:

- strong worktree/session orchestration but weaker CI/review automation
- strong coding-agent workflow but limited dashboard
- strong cloud agent platform but weaker local/self-hosted control
- strong PR automation but limited multi-agent fleet management

### Score 5-6: Adjacent competitor

The project is relevant but not a direct substitute.

Examples:

- a coding agent without fleet orchestration
- a worktree/session manager without PR/CI lifecycle
- a framework with examples of coding-agent workflows
- a PR automation product
- a useful agent runtime that needs custom orchestration

### Score 3-4: Weakly related inspiration

The project has useful ideas but is not a direct analog.

Examples:

- generic agent framework
- memory layer
- task planning tool
- workflow library
- prompt/skill library
- isolated idea useful for orchestration

### Score 1-2: Mostly irrelevant

The project has minimal overlap.

### Score 0: Not relevant

The project should not be included except in an excluded/noise appendix.

## Required evidence per candidate

For every candidate, collect:

- name
- URL
- category
- direct analog score
- reason for score
- license if available
- GitHub stars/forks if available
- last meaningful commit or release if available
- evidence of activity
- architecture summary
- agent/session model
- fleet/multi-agent support
- role/model/tool routing support
- task queue / loop / retry support
- worktree / workspace isolation
- branch / PR lifecycle support
- CI failure handling
- review-comment handling
- merge-conflict handling
- dashboard / supervision UI
- tracker integration: GitHub, GitLab, Linear, issue trackers
- runtime abstraction: tmux, process, ConPTY, Docker, containers, remote sandboxes
- agent abstraction: Claude Code, Codex, Aider, OpenCode, Cursor, OpenHands, SWE-agent, etc.
- artifact/logging/event support
- local/self-hosted support
- local inference compatibility
- commercial/SaaS dependency if any
- fit as an analog of ComposioHQ Agent Orchestrator
- source URLs for important claims

## Ranking rules

Rank direct analogs first.

Do not rank generic frameworks above real coding-agent orchestrators unless the framework includes a concrete coding-agent orchestration product.

Commercial platforms can rank high if they solve the same user problem, even if their architecture is closed.

Open-source projects should be evaluated by both capability and maturity.

Small GitHub projects can rank high if they are very close to the target workflow.

Projects with real worktree/branch/PR/session orchestration should usually rank above generic "multi-agent" frameworks.

Projects with CI fixing and review-comment fixing should rank above tools that only spawn agents.

Projects with dashboard/supervision should rank above headless scripts if all other factors are equal.

## Important anti-bias rules

Do not overvalue GitHub stars.

Do not overvalue famous frameworks.

Do not assume that "multi-agent" means "coding-agent fleet orchestrator".

Do not assume that "agentic coding" means worktree/PR lifecycle management.

Do not assume that a project is active only because it has recent README edits.

Do not assume that a SaaS product supports local workflows unless documentation confirms it.

Do not treat "can be built with this framework" as the same as "the project already does it".

Do not classify a generic framework as a direct analog unless there is evidence of concrete coding-agent orchestration.

If evidence is missing, mark it as unknown instead of guessing.

## Final classification output

The final report must separate:

1. Top direct analogs.
2. Worktree/session managers.
3. Coding-agent orchestrators without full fleet/PR lifecycle.
4. Agent frameworks and substrates.
5. Commercial/platform competitors.
6. Adjacent inspiration projects.
7. Excluded or downranked projects.