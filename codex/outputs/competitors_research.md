# Competitive Landscape Report: ai-orchestrator

Research date: 2026-05-20  
Method: target repository inspection plus Exa MCP search/fetch against official repositories, official docs, and product documentation. Seed candidates were treated as leads, not as truth.

## 1. Executive Summary

`ai-orchestrator` is a local, file-protocol coding-agent loop: a task in `.ai-loop/task.md` is implemented by Cursor Agent by default, reviewed by Codex, tested, iterated through fix prompts, safely staged, committed, and optionally pushed. Its strongest overlap is not generic "agent frameworks"; it is local coding-agent orchestration with Git, artifacts, retries, and separate implementer/reviewer roles.

The closest open-source competitors are:

1. Composio Agent Orchestrator: broadest direct overlap, with parallel coding agents, worktrees, CI/review feedback routing, PRs, plugin slots, and support for Claude Code, Codex, Aider, Cursor, and OpenCode.
2. SWE-AF: most advanced explicit role pipeline, with PM/architect/coder/QA/reviewer/merger/verifier roles, per-role model routing, worktrees, retries, replanning, PRs, and artifacts.
3. Gas Town: mature multi-agent workspace system with persistent work state, worktrees, dispatch, supervisors, merge queues, and multiple runtime support.
4. Orc and Open Orchestrator: small but highly relevant local-first orchestrators with worktrees, tmux, review loops, task decomposition, and safety gates.
5. MCO: not an implementation orchestrator, but a strong local multi-agent review/consensus engine across Claude, Codex, Gemini, OpenCode, and Qwen.

The strongest commercial/platform threats are Devin, Codegen, Factory Droid, Cursor Cloud Agents, Google Jules, GitHub Copilot cloud agent, and OpenAI Codex. They compete for the same user outcome: delegate coding tasks, get tested diffs/PRs, and review the result. They are less local-first, but have distribution, hosted environments, issue/Slack/GitHub integration, and enterprise controls.

The biggest differentiation opportunity for `ai-orchestrator` is to be the narrow, auditable, local-first PowerShell/Windows-friendly orchestrator for heterogeneous coding CLIs, with human-readable files as the state machine and independent review/fix/test gates.

## 2. Target Capability Baseline

Primary sources: target GitHub repository and raw `AGENTS.md` / `docs/architecture.md`.

Actual current capabilities:

- CLI-first PowerShell workflow installed into a target Git repo, centered on `.ai-loop/` files. Source: https://github.com/chetwerikoff/ai-orchestrator
- Task-first entrypoint `ai_loop_task_first.ps1`: clears stale runtime artifacts, runs an implementer, then invokes `ai_loop_auto.ps1` for tests plus Codex review/fix loop. Source: https://github.com/chetwerikoff/ai-orchestrator
- Production roles today: Cursor Agent as implementer, Codex CLI as technical reviewer, human as planner, and business review still manual/out-of-loop. Source: https://raw.githubusercontent.com/chetwerikoff/ai-orchestrator/master/docs/architecture.md
- Configurable implementer wrapper via `-CursorCommand`, including opt-in OpenCode + local Qwen wrapper; Cursor remains the default production implementer. Source: https://raw.githubusercontent.com/chetwerikoff/ai-orchestrator/master/docs/architecture.md
- Persistent artifacts include `.ai-loop/task.md`, `project_summary.md`, `implementer_summary.md`, `codex_review.md`, `final_status.md`, `test_output.txt`, `last_diff.patch`, `git_status.txt`, debug prompts/output, and persisted implementer runtime state. Source: https://github.com/chetwerikoff/ai-orchestrator
- Test/review/fix loop: pytest by default, Codex review gate, extraction of fix prompt, implementer rerun, final test gate, and bounded `MaxIterations` defaulting to 5. Source: https://raw.githubusercontent.com/chetwerikoff/ai-orchestrator/master/docs/architecture.md
- Git integration: diff/status capture, safe allowlisted staging, commit and optional push. It explicitly avoids staging everything and excludes runtime artifacts. Source: https://github.com/chetwerikoff/ai-orchestrator
- Safety controls: safe path allowlist, runtime artifact exclusion, task scope validation, dynamic declared-file preflight, no-change detection, max iterations, resume state, and dirty/scope-aware staging behavior. Source: https://raw.githubusercontent.com/chetwerikoff/ai-orchestrator/master/AGENTS.md
- Durable memory: `.ai-loop/project_summary.md` is updated by the implementer and read by Codex. Source: https://github.com/chetwerikoff/ai-orchestrator
- Aspirational target design: Claude planner, OpenCode + local Qwen coder, deterministic guards, Codex technical review, optional Claude business gate. Current state does not yet include automated Claude planner/business review. Source: https://raw.githubusercontent.com/chetwerikoff/ai-orchestrator/master/docs/architecture.md

Baseline implications for scoring:

- Direct overlap requires more than "multi-agent": it must coordinate coding CLIs, Git state, tests/review/fix loops, and durable task artifacts.
- Local-first CLI and file-state orchestration are core differentiators.
- Projects that only run one coding agent are product competitors, but not direct orchestrator competitors.
- Generic agent frameworks are substrates unless they ship a concrete coding-agent workflow.

## 3. Ranked Top 20 Candidates

| Rank | Candidate | Category | Score | URL | Why it matters |
|---:|---|---|---:|---|---|
| 1 | Composio Agent Orchestrator | Direct competitor | 9.5 | https://github.com/ComposioHQ/agent-orchestrator | Parallel coding agents in worktrees, CI/review reaction loops, PRs, dashboard, plugin slots, Claude/Codex/Aider/Cursor/OpenCode support. |
| 2 | SWE-AF | Direct competitor | 9.2 | https://github.com/Agent-Field/SWE-AF | Explicit autonomous engineering factory: planner, architect, coder, QA, reviewer, merger, verifier; role-model routing, retries, replanning, artifacts, worktrees, PRs. |
| 3 | Gas Town | Direct competitor | 8.8 | https://github.com/steveyegge/gastown | Mature multi-agent workspace manager with persistent work state, worktrees, dispatcher/supervisor concepts, merge queue, Claude/Codex/Gemini support. |
| 4 | Orc | Direct competitor | 8.5 | https://github.com/spencermarx/orc | Local tmux/git/markdown orchestrator with automatic decomposition, engineer/reviewer loop, isolated worktrees, goal branches, and human gates. |
| 5 | Open Orchestrator | Direct competitor | 8.3 | https://github.com/gitpcl/openorchestrator | Local worktree orchestration, switchboard UI, DAG planning, orchestrator agent, swarm mode, retry/timeouts, peer MCP, quality gates. |
| 6 | gabrielkoerich/orchestrator | Direct competitor | 8.1 | https://github.com/gabrielkoerich/orchestrator | GitHub Issues-to-worktree-to-agent-to-PR workflow with router, Claude/Codex/OpenCode executors, optional opposite-agent PR review. |
| 7 | agtx | Direct competitor | 8.0 | https://github.com/fynnfluegge/agtx | Kanban/task-board orchestrator with phase-based agent switching, worktrees, tmux sessions, Codex/Claude/Gemini/OpenCode/Cursor support, MCP board API. |
| 8 | MCO | Direct competitor | 7.8 | https://github.com/mco-org/mco | Strong local multi-provider review/run orchestrator with consensus, chain/debate/divide modes, artifacts, retries, custom agents, local Qwen/Ollama fit. |
| 9 | proboscis/orch | Direct competitor | 7.6 | https://github.com/proboscis/orch | Lightweight issue/run/event model; runs Claude/Codex/Gemini/OpenCode in background worktrees with status, attach, retries/events. |
| 10 | Agent Review CLI | Direct competitor | 7.4 | https://github.com/Open-Document-Alliance/Agent-Review-CLI | Review/fix/integrate/verify/publish pipeline across parallel worktree agents; Codex/Claude/OpenCode/mixed backends. |
| 11 | Open SWE | Coding-agent framework/product | 7.2 | https://github.com/langchain-ai/open-swe | Open-source async coding agent with sandboxed tasks, subagents, Slack/Linear/GitHub invocation, PR creation; less local CLI-first. |
| 12 | Daintree | Worktree/session manager | 7.1 | https://github.com/daintreehq/daintree | Desktop local control plane for many CLI agents, worktrees, context injection, review workflows, PR/issue detection, MCP server. |
| 13 | Claude Squad | Worktree/session manager | 6.8 | https://github.com/smtg-ai/claude-squad | Mature TUI for multiple Claude/Codex/OpenCode/Aider sessions in isolated git workspaces; less automated review/fix logic. |
| 14 | Conduit | Worktree/session manager | 6.7 | https://github.com/conduit-cli/conduit | Keyboard-first TUI/web UI for Codex/Claude/Gemini/OpenCode sessions, worktrees, queue editing, imports, token/cost views. |
| 15 | Codegen | Platform competitor | 6.6 | https://docs.codegen.com | Hosted code agents at scale with sandboxes, Slack/ticket/GitHub integrations, tests, reviews, branches, PRs, API/SDK. |
| 16 | Factory Droid | Platform competitor | 6.5 | https://docs.factory.ai | CLI/app/CI product with Droid Exec, Missions, local review, custom subagents, MCP, hooks, BYOK/local endpoints, GitHub action. |
| 17 | Cursor Cloud Agents | Platform competitor | 6.4 | https://cursor.com/docs/cloud-agent/api/endpoints | Programmatic cloud agents with repos, branches, PR creation, plan/agent mode, MCP servers, run streams, artifacts. |
| 18 | Devin | Platform competitor | 6.3 | https://docs.devin.ai | Autonomous software engineer for tickets, PR review, bugs, tests, terminal/web/IDE, parallel backlog work; hosted and closed. |
| 19 | Codex Orchestrator | Adjacent direct wrapper | 6.2 | https://github.com/kingbootoshi/codex-orchestrator | Claude Code plugin/CLI for spawning background Codex tmux jobs with status, redirect, captures, summaries; narrower than target. |
| 20 | GitHub Copilot cloud agent | Platform competitor | 6.0 | https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent | GitHub-native assigned coding tasks, PR creation, custom agents, MCP, hooks, skills; one repo/branch/PR limitations. |

## 4. Top 5 Direct Threats

### 1. Composio Agent Orchestrator

Threat level: very high. It directly targets "running 30 AI coding agents" with isolated git worktrees, branches, PRs, CI-failure routing, review-comment routing, dashboard supervision, and agent/runtime/tracker plugins. It already names Claude Code, Codex, Aider, Cursor, and OpenCode as supported/alternative agents. Source: https://github.com/ComposioHQ/agent-orchestrator

Why it threatens `ai-orchestrator`: it covers the same operational envelope but adds parallelism, web dashboard, GitHub/Linear integration, plugin architecture, CI reactions, PR lifecycle, and more mature ecosystem signals.

### 2. SWE-AF

Threat level: very high. SWE-AF is a concrete engineering factory, not a generic framework. It exposes PM, architect, tech lead, coder, QA, code reviewer, synthesizer, merger, integration tester, verifier, GitHub PR, issue advisor, and replanner roles; supports role-model maps; uses isolated worktrees; retries and replans; and writes artifacts. Source: https://github.com/Agent-Field/SWE-AF

Why it threatens `ai-orchestrator`: it already implements much of `ai-orchestrator`'s aspirational roadmap: planner, implementer, reviewer, QA, merger, verifier, role routing, retries, PR, and artifacts.

### 3. Gas Town

Threat level: high. Gas Town coordinates many AI coding agents across projects with persistent work tracking, worktrees, supervisors, merge queue, escalation, schedules, and Claude/Codex/GitHub Copilot/Gemini runtimes. Source: https://github.com/steveyegge/gastown

Why it threatens `ai-orchestrator`: it attacks the long-running semi-autonomous multi-agent workflow and persistence problem at a broader workspace layer.

### 4. Orc

Threat level: high despite low stars. Orc is very close conceptually: local tmux/git/plain-markdown orchestration, automatic decomposition, engineer/reviewer roles, isolated worktrees, review loops, max review rounds, human gates, and clean delivery branches. Source: https://github.com/spencermarx/orc

Why it threatens `ai-orchestrator`: it has a clear role hierarchy and review loop around local CLI agents while retaining the simplicity of files and shell.

### 5. Open Orchestrator

Threat level: high despite low stars. Open Orchestrator provides worktree/session management, task decomposition, batch/autopilot DAGs, orchestrator resume/stop/status, swarms with researcher/implementer/reviewer/tester roles, retries, timeouts, quality gates, MCP peer communication, memory, and local CLI support. Source: https://github.com/gitpcl/openorchestrator

Why it threatens `ai-orchestrator`: it has breadth across worktree operations and autonomous loops that `ai-orchestrator` currently handles in a narrower single-task pipeline.

## 5. Top 5 Inspiration Projects

1. MCO: borrow consensus review modes, chain/debate modes, per-provider perspectives, SARIF/Markdown/JSON outputs, per-provider timeouts, custom provider registry, and artifact directories. Source: https://github.com/mco-org/mco
2. Agent Review CLI: borrow the phase language `INIT -> PLAN -> DISCOVER -> FIX -> INTEGRATE -> VERIFY -> PUBLISH` and single-run report structure. Source: https://github.com/Open-Document-Alliance/Agent-Review-CLI
3. agtx: borrow a task board, MCP interface, per-phase plugin configs, idle/stuck diagnosis, and phase artifacts. Source: https://github.com/fynnfluegge/agtx
4. Conduit: borrow token/cost/context visibility, session import, queue editing, and raw event inspection for local CLIs. Source: https://github.com/conduit-cli/conduit
5. Cursor Cloud Agents / Jules: borrow artifact APIs, run status streaming, plan approval, activity logs, and explicit PR automation modes. Sources: https://cursor.com/docs/cloud-agent/api/endpoints and https://developers.google.com/jules/api

## 6. Feature Matrix

Legend: Yes = clearly supported; Partial = supported but narrower or implicit; No/Unknown = not confirmed from sources.

| Project | Category | Score | Multi-agent/session | Role/model routing | Task loop/retry | Git/worktree/PR | Test/review/fix | Artifacts/logs | CLI/local support | Local inference fit | Notes |
|---|---|---:|---|---|---|---|---|---|---|---|---|
| ai-orchestrator | Target | N/A | Partial | Partial | Yes | Yes | Yes | Yes | Yes | Yes | Cursor implementer + Codex reviewer today; OpenCode/Qwen opt-in. |
| Composio AO | Direct competitor | 9.5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Partial | Strongest broad overlap; dashboard plus plugins. |
| SWE-AF | Direct competitor | 9.2 | Yes | Yes | Yes | Yes | Yes | Yes | Partial | Yes | Most explicit role factory; API/control-plane style. |
| Gas Town | Direct competitor | 8.8 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Partial | Mature workspace/state/merge queue model. |
| Orc | Direct competitor | 8.5 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Partial | Very close local shell/tmux/markdown design. |
| Open Orchestrator | Direct competitor | 8.3 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Partial | Rich local worktree and swarm operations. |
| gabrielkoerich/orchestrator | Direct competitor | 8.1 | Yes | Yes | Partial | Yes | Yes | Partial | Yes | Partial | GitHub Issues as task backend; PR review agent. |
| agtx | Direct competitor | 8.0 | Yes | Yes | Partial | Yes | Partial | Yes | Yes | Partial | Board plus MCP phase orchestration. |
| MCO | Direct competitor | 7.8 | Yes | Yes | Yes | Partial | Yes | Yes | Yes | Yes | Review/run orchestration, not full implementation pipeline. |
| proboscis/orch | Direct competitor | 7.6 | Yes | Yes | Partial | Yes | Partial | Yes | Yes | Partial | Issue/run/event model with worktrees and attach. |
| Agent Review CLI | Direct competitor | 7.4 | Yes | Yes | Partial | Yes | Yes | Yes | Yes | Partial | Review/fix/integrate/verify/publish pipeline. |
| Open SWE | Platform/framework | 7.2 | Yes | Yes | Partial | Yes | Partial | Yes | Partial | Partial | Cloud sandbox async coding agent, PR creation. |
| Daintree | Worktree/session manager | 7.1 | Yes | Yes | Partial | Yes | Partial | Yes | Yes | Partial | Desktop control plane for local agent fleets. |
| Claude Squad | Worktree/session manager | 6.8 | Yes | Partial | Partial | Yes | Partial | Partial | Yes | Partial | Session manager more than autonomous loop. |
| Conduit | Worktree/session manager | 6.7 | Yes | Yes | Partial | Yes | Partial | Yes | Yes | Partial | TUI/web UI; cost/context/session persistence. |
| Codegen | Platform competitor | 6.6 | Yes | Unknown | Yes | Yes | Yes | Yes | No | No | Hosted enterprise agent platform. |
| Factory Droid | Platform competitor | 6.5 | Yes | Yes | Yes | Yes | Yes | Yes | Partial | Yes | CLI/app/cloud with hooks, skills, MCP, BYOK. |
| Cursor Cloud Agents | Platform competitor | 6.4 | Partial | Yes | Partial | Yes | Partial | Yes | No | No | Durable cloud agents and run/artifact API. |
| Devin | Platform competitor | 6.3 | Yes | Unknown | Yes | Yes | Yes | Yes | Partial | No | Hosted AI software engineer with terminal option. |
| Codex Orchestrator | Adjacent direct wrapper | 6.2 | Yes | Partial | Partial | Partial | Partial | Yes | Yes | No | Background Codex job spawning from Claude/CLI. |
| GitHub Copilot cloud agent | Platform competitor | 6.0 | Partial | Yes | Partial | Yes | Partial | Yes | No | No | GitHub-native, one repo/branch/PR per task. |
| Google Jules | Platform competitor | 6.0 | Yes | Partial | Partial | Yes | Partial | Yes | No | No | Sessions, plans, activities, artifacts, PR output. |
| OpenHands | Coding-agent product/framework | 5.8 | Partial | Yes | Partial | Partial | Partial | Yes | Yes | Partial | Strong coding agent/SDK; less orchestration-specific. |
| Codex CLI | Coding-agent product | 5.5 | No | Yes | Partial | Partial | Yes | Yes | Yes | No | Target uses it as reviewer; not an orchestrator by itself. |
| LangGraph | Substrate | 4.0 | Yes | Yes | Yes | No | No | Yes | Yes | Yes | Excellent durable agent runtime, but not a coding orchestrator product. |
| Deep Agents | Substrate | 4.5 | Yes | Yes | Yes | Partial | Partial | Yes | Yes | Yes | Agent harness with filesystem/subagents; Open SWE is the productized coding workflow. |
| CrewAI / AutoGen / CAMEL | Substrate | 3.5 | Yes | Yes | Yes | No | No | Partial | Yes | Yes | Generic multi-agent substrates. |

## 7. Commercial and Platform Competitors

### Devin

Category: Coding-agent product / platform competitor  
Score: 6.3  
Primary source: https://docs.devin.ai

Evidence: Devin is documented as an autonomous software engineer that can write, run, and test code; handle Linear/Jira tickets, features, bugs, tests, PR review, codebase Q&A, and documentation; expose shell, IDE, browser, API, web app, Slack/Teams workflows, and a terminal client.

Fit against `ai-orchestrator`: strong product-level threat for delegated coding tasks and PR workflows, but weaker fit for local file-state orchestration and explicit heterogeneous role routing.

### Codegen

Category: Coding-agent product / platform competitor  
Score: 6.6  
Sources: https://docs.codegen.com and https://github.com/codegen-sh/codegen

Evidence: Codegen runs frontier code agents at scale with sandboxes, telemetry, Slack/ticket/GitHub integrations, tests, PR reviews, branches/commits, and Python SDK/API.

Fit: strong enterprise hosted alternative; less direct if the user wants local PowerShell/file artifacts and control over CLI agents.

### Factory Droid

Category: Coding-agent product / platform competitor  
Score: 6.5  
Sources: https://docs.factory.ai and https://github.com/Factory-AI/droid-action

Evidence: Factory ships Droid CLI, Droid Exec for CI, Missions, local code review, custom Droids, hooks, MCP, skills, BYOK/local model endpoints, and GitHub Action workflows for fill/review/security scans.

Fit: strong platform alternative with local and hosted surfaces; direct overlap in review/test/automation but less file-protocol-specific.

### Cursor Cloud Agents

Category: Coding-agent product / platform competitor  
Score: 6.4  
Source: https://cursor.com/docs/cloud-agent/api/endpoints

Evidence: API creates durable cloud agents and per-prompt runs against repositories, branches, PRs, cloud/self-hosted environments, model selection, MCP servers, plan/agent modes, run streams, cancellation, and artifacts.

Fit: significant product threat, especially if `ai-orchestrator` users want programmatic background agents instead of local loops.

### Google Jules

Category: Coding-agent product / platform competitor  
Score: 6.0  
Sources: https://jules.google and https://developers.google.com/jules/api

Evidence: Jules creates sessions from GitHub sources, generates plans, exposes activities/progress/artifacts/change sets, can auto-create PRs, and has concurrency/task quotas by plan.

Fit: hosted async coding-agent alternative; less local-first.

### GitHub Copilot cloud agent

Category: Coding-agent product / platform competitor  
Score: 6.0  
Source: https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent

Evidence: GitHub documents assigned coding tasks, PR outcomes/metrics, custom instructions, memory, MCP, custom agents, hooks, skills, and limitations including one repository, one branch, and one PR per assigned task.

Fit: strong GitHub-native competitor, weaker for multi-agent local workflow and non-GitHub repos.

### OpenAI Codex

Category: Coding-agent product / platform competitor  
Score: 5.5  
Sources: https://github.com/openai/codex and https://developers.openai.com/codex

Evidence: Codex CLI is a local terminal coding agent for writing, understanding, reviewing, debugging/fixing, and automating dev tasks. The repository is active and Apache-2.0 licensed.

Fit: `ai-orchestrator` already uses Codex as a reviewer; Codex is not itself a multi-agent orchestrator, but is both dependency and product-level substitute for simpler tasks.

### Qodo

Category: Coding-agent product / platform competitor  
Score: 5.4  
Sources: https://qodo.ai/products/qodo-merge and https://qodo.ai/products/qodo-command

Evidence: Qodo Merge focuses on PR review, requirement validation, rules, issue context, and implementation-ready prompts. Qodo Command supports terminal agents, custom review agents, CI/webhook/MCP modes, and workflow automation.

Fit: stronger as review/quality inspiration than as a full implementer/reviewer orchestrator.

## 8. Agent Frameworks and Substrates

These projects should not be ranked above concrete coding orchestrators unless they ship a ready coding workflow.

### LangGraph

Category: Agent framework / substrate  
Score: 4.0  
Source: https://github.com/langchain-ai/langgraph

Useful for durable execution, persistence, human-in-the-loop, memory, streaming, and long-running stateful agent graphs. It is a substrate, not a direct local coding-agent orchestrator.

### Deep Agents

Category: Agent framework / substrate  
Score: 4.5  
Source: https://github.com/langchain-ai/deepagents

Useful because it provides planning, filesystem tools, shell execution, subagents, context management, and a CLI. Still a harness/substrate unless deployed as a coding workflow.

### Open SWE

Category: Coding-agent framework/product competitor  
Score: 7.2  
Source: https://github.com/langchain-ai/open-swe

Open SWE crosses from substrate to product: it has isolated cloud sandboxes, Slack/Linear/GitHub invocation, subagents, AGENTS.md context, PR creation, and prompt-driven validation. It is less local-first than `ai-orchestrator`, but directly relevant.

### OpenHands

Category: Coding-agent product / framework  
Score: 5.8  
Source: https://github.com/All-Hands-AI/OpenHands

OpenHands is a coding-agent product/SDK with CLI/cloud/app surfaces and agentic development capability. It is adjacent unless being used as the execution agent inside an orchestrator.

### CrewAI, AutoGen/AG2, CAMEL, Microsoft Agent Framework

Category: Agent framework / substrate  
Score: 3-4  
Representative sources: https://github.com/crewAIInc/crewAI, https://github.com/microsoft/autogen, https://github.com/ag2ai/ag2, https://github.com/camel-ai/camel

These are useful for role abstractions, agent societies, tool integration, memory, and workflow composition. They should not be treated as direct competitors to `ai-orchestrator` without a concrete coding-agent orchestration workflow involving Git, tests, PRs, and durable coding artifacts.

## 9. Downranked or Excluded Candidates

| Candidate | Primary URL | Classification | Score | Reason |
|---|---|---|---:|---|
| LangGraph | https://github.com/langchain-ai/langgraph | Substrate | 4.0 | Excellent durable runtime, but no built-in local coding-agent review/fix/Git loop. |
| Deep Agents | https://github.com/langchain-ai/deepagents | Substrate | 4.5 | Coding-capable harness with subagents/filesystem, but not primarily a Git/test/review orchestrator. |
| CrewAI | https://github.com/crewAIInc/crewAI | Substrate | 3.5 | Generic role-based agent framework; no direct evidence of target-like coding loop. |
| AutoGen / AG2 | https://github.com/microsoft/autogen and https://github.com/ag2ai/ag2 | Substrate | 3.5 | Generic multi-agent programming substrate. |
| CAMEL | https://github.com/camel-ai/camel | Substrate | 3.5 | Broad multi-agent research framework; useful inspiration, not direct coding CLI orchestration. |
| ChatDev | https://github.com/OpenBMB/ChatDev | Adjacent inspiration | 4.0 | Software-company role simulation, useful historically; less aligned with modern local CLI/Git/test agent loops. |
| Claude Squad | https://github.com/smtg-ai/claude-squad | Worktree/session manager | 6.8 | Strong session/worktree manager but not as automated around tests/review/fix artifacts. |
| Conduit | https://github.com/conduit-cli/conduit | Worktree/session manager | 6.7 | Strong local agent TUI; less autonomous review/fix loop evidence. |
| Daintree | https://github.com/daintreehq/daintree | Worktree/session manager | 7.1 | Strong supervision/control plane, but review/fix/test loops appear less prescriptive than `ai-orchestrator`. |
| Codex CLI | https://github.com/openai/codex | Product dependency | 5.5 | A coding agent used by target; not a multi-agent orchestrator alone. |
| Qodo Merge | https://qodo.ai/products/qodo-merge | Platform/review tool | 5.4 | Strong review and prompt generation; weaker implementation orchestration. |
| Jules | https://jules.google | Platform competitor | 6.0 | Hosted task-to-PR product; no local CLI/file-protocol control. |
| GitHub Copilot cloud agent | https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent | Platform competitor | 6.0 | GitHub-native but limited to GitHub, one repo/branch/PR per task. |
| `PrimeLocus/Hydra`, `Enderfga/claw-orchestrator`, `agent-sh/agentsys`, `kbwo/ccmanager`, `njbrake/agent-of-empires` | Seed URLs | Unknown/downranked | Unknown | Exa fetch/search did not provide enough primary evidence in this run to rank confidently. Keep on a follow-up verification list. |
| `gabrielkoerich/orch` seed | https://github.com/gabrielkoerich/orch | Ambiguous | Unknown | Search surfaced the more relevant `gabrielkoerich/orchestrator`; seed URL should be rechecked manually if needed. |

## 10. Gaps in ai-orchestrator

1. Limited parallelism: current target baseline is mostly one task/one implementer pass plus Codex review loop, not a fleet or worktree manager.
2. Planner is not automated yet: human writes `.ai-loop/task.md`; architecture notes say Claude planner is aspirational.
3. Business/product review is not automated yet: separate manual flow, not in orchestrator.
4. No native dashboard/TUI: competitors provide boards, switchboards, dashboards, status cards, raw events, token/cost views.
5. No issue tracker integration: competitors use GitHub Issues, Linear, Slack, Jira, PR comments, labels, or APIs as task sources.
6. Worktree isolation is weaker/absent in baseline: target operates in target project root with safe staging, while many competitors isolate branches/worktrees per task.
7. Limited model/role routing: target has implementer override and Codex reviewer, but not a general role-to-model/provider config.
8. No built-in multi-agent consensus review: MCO, SWE-AF, and Agent Review CLI show multi-reviewer/divide/debate patterns.
9. Limited observability: artifacts exist, but there is no unified run manifest, event stream, cost ledger, or status API.
10. Windows-first PowerShell is a strength but also a portability constraint; many competitors target macOS/Linux tmux first.

## 11. Differentiation Opportunities

1. Own local-first, file-first orchestration: make `.ai-loop/` a clean, documented protocol with stable schemas for task, declared files, review, test result, final status, run manifest, and next prompt.
2. Be the Windows/PowerShell-native orchestrator: most competitors assume tmux/macOS/Linux. A robust Windows implementation can be distinctive.
3. Add heterogeneous role routing: map planner/implementer/reviewer/fixer/business-review/local-helper to Codex, Claude, Cursor, OpenCode, Gemini, Qwen/Ollama, or custom commands.
4. Add worktree mode without abandoning root mode: optional per-task Git worktrees would close the biggest gap against AO, Gas Town, Orc, Daintree, agtx, and Open Orchestrator.
5. Make review/fix/test gates auditable: keep the current artifact trail and add machine-readable verdicts, severity tags, retry reasons, and failure fingerprints.
6. Add cost-aware model routing: use local Qwen/OpenCode for first-pass fixes, Codex/Claude for high-risk reviews, and cheaper models for summaries.
7. Add explicit business-logic review: separate technical review from product/domain review as a first-class gate.
8. Add overnight loop controls: time budget, iteration budget, idle detection, failure classification, stop/resume, and final escalation prompts.
9. Preserve human-readable task files: competitors often move to dashboards/databases; `ai-orchestrator` can make plain files the debugging and collaboration advantage.
10. Provide an integration surface: JSON run manifests and a tiny status CLI would let external tools build dashboards without replacing the file protocol.

## 12. Recommended Roadmap

### Immediate

- Add a machine-readable `.ai-loop/run.json` or `chain.json` summary containing task id, role commands/models, iteration count, tests, review verdicts, changed files, final status, and source commit.
- Create a concise `docs/file_protocol.md` documenting every durable and runtime artifact.
- Add role configuration in one file, e.g. `.ai-loop/roles.json`, instead of only CLI parameters.
- Make the Codex review output parser produce structured verdict JSON beside Markdown.
- Add a `--dry-run` / preflight command that validates task scope, required CLIs, Git state, safe paths, and test command before launching agents.

### Short-term

- Implement optional worktree mode: create isolated branch/worktree per task, run the same `.ai-loop` protocol there, then merge/PR or produce patch.
- Add a planner entrypoint that converts a user ask into `.ai-loop/task.md` with scope, acceptance criteria, denylist, and test command.
- Add business-review gate as a separate role from technical review.
- Add multi-review mode: Codex plus optional Claude/Gemini/MCO review, with consensus and a final synthesized fix prompt.
- Add event logging: append-only `.ai-loop/events.jsonl` for run start, agent command, test result, review verdict, retry, commit, final status.
- Add cost/token reporting hooks across implementer/reviewer/fixer roles where CLIs expose usage.

### Medium-term

- Add queue/batch execution with concurrency limits and optional worktree isolation.
- Add a lightweight local dashboard or TUI reading `.ai-loop/events.jsonl` and run manifests.
- Add GitHub/Linear issue ingestion and PR creation as optional adapters.
- Add local inference helper mode: Qwen/OpenCode/Ollama for scout, summarizer, cheap fixer, or first review, with escalation to frontier models.
- Add safety policies: branch protection checks, secret scans, denylist/allowlist policy packs, rollback/restore points, and human gate policies.
- Add plugin/adaptor contract for new coding CLIs, similar to AO/MCO/Conduit but with the `.ai-loop` file protocol as the stable center.

## 13. Source Appendix

Target:

- ai-orchestrator repository: https://github.com/chetwerikoff/ai-orchestrator
- Target `AGENTS.md`: https://raw.githubusercontent.com/chetwerikoff/ai-orchestrator/master/AGENTS.md
- Target architecture: https://raw.githubusercontent.com/chetwerikoff/ai-orchestrator/master/docs/architecture.md

Direct orchestrators and worktree/session managers:

- Composio Agent Orchestrator: https://github.com/ComposioHQ/agent-orchestrator
- SWE-AF: https://github.com/Agent-Field/SWE-AF
- Gas Town: https://github.com/steveyegge/gastown
- Orc: https://github.com/spencermarx/orc
- Open Orchestrator: https://github.com/gitpcl/openorchestrator
- gabrielkoerich/orchestrator: https://github.com/gabrielkoerich/orchestrator
- agtx: https://github.com/fynnfluegge/agtx
- MCO: https://github.com/mco-org/mco
- proboscis/orch: https://github.com/proboscis/orch
- Agent Review CLI: https://github.com/Open-Document-Alliance/Agent-Review-CLI
- Daintree: https://github.com/daintreehq/daintree
- Claude Squad: https://github.com/smtg-ai/claude-squad
- Conduit: https://github.com/conduit-cli/conduit
- Codex Orchestrator: https://github.com/kingbootoshi/codex-orchestrator
- multiclaude: https://github.com/dlorenc/multiclaude
- CCB: https://github.com/bfly123/claude_codex_bridge

Frameworks and coding-agent products:

- Open SWE: https://github.com/langchain-ai/open-swe
- Deep Agents: https://github.com/langchain-ai/deepagents
- LangGraph: https://github.com/langchain-ai/langgraph
- OpenHands: https://github.com/All-Hands-AI/OpenHands
- SWE-agent: https://github.com/SWE-agent/SWE-agent
- mini-swe-agent: https://github.com/SWE-agent/mini-swe-agent
- ChatDev: https://github.com/OpenBMB/ChatDev
- CrewAI: https://github.com/crewAIInc/crewAI
- AutoGen: https://github.com/microsoft/autogen
- AG2: https://github.com/ag2ai/ag2
- CAMEL: https://github.com/camel-ai/camel

Commercial/platform competitors:

- Codegen docs: https://docs.codegen.com
- Codegen SDK: https://github.com/codegen-sh/codegen
- Factory docs: https://docs.factory.ai
- Factory Droid GitHub Action: https://github.com/Factory-AI/droid-action
- Devin docs: https://docs.devin.ai
- Cursor Cloud Agents API: https://cursor.com/docs/cloud-agent/api/endpoints
- GitHub Copilot cloud agent: https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent
- Google Jules: https://jules.google
- Jules API: https://developers.google.com/jules/api
- OpenAI Codex repository: https://github.com/openai/codex
- OpenAI Codex docs: https://developers.openai.com/codex
- Qodo Merge: https://qodo.ai/products/qodo-merge
- Qodo Command: https://qodo.ai/products/qodo-command
