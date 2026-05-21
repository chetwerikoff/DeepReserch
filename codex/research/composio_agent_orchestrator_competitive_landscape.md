# Competitive Landscape: ComposioHQ Agent Orchestrator Analogs

Research date: 2026-05-20  
Target: [ComposioHQ/agent-orchestrator](https://github.com/ComposioHQ/agent-orchestrator)

## 1. Executive Summary

The closest analogs are projects that combine local coding-agent fleet control with git worktree isolation, branch/PR lifecycle, review or CI feedback loops, and a supervision surface. The strongest open/source-adjacent analogs found are [gabrielkoerich/orchestrator](https://github.com/gabrielkoerich/orchestrator), [dlorenc/multiclaude](https://github.com/dlorenc/multiclaude/), [agent-sh/agentsys](https://github.com/agent-sh/agentsys), [Agent-Field/SWE-AF](https://github.com/Agent-Field/SWE-AF), [daintreehq/daintree](https://github.com/daintreehq/daintree), [standardagents/dmux](https://github.com/justin-schroeder/dmux), [steveyegge/gastown](https://github.com/steveyegge/gastown/), and [yungookim/oh-my-pr](https://github.com/yungookim/oh-my-pr/tree/main).

The strongest commercial/product competitors are [Cursor Cloud Agents](https://cursor.com/docs/cloud-agent), [OpenAI Codex cloud](https://developers.openai.com/codex/cloud), [GitHub Copilot cloud agent](https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent), [Devin](https://docs.devin.ai/get-started/devin-intro), [Codegen](https://codegen.ai/), [Google Jules](https://jules.google/), and [Factory Droid](https://github.com/Factory-AI/droid-action). These are less local-first, but they solve the same user problem: delegate work, get branches/PRs, review output, and iterate through comments or failing checks.

The main category pattern is now clear: CLI agents are execution engines; worktrees are the isolation primitive; GitHub/Linear/issues are task substrates; dashboards/TUIs are supervision layers; CI/review comments are feedback channels; and durable artifacts are required for resumability and trust.

The opportunity for a smaller local-first `ai-orchestrator` is not to beat SaaS agents on model quality. It is to be the best lightweight control plane for Claude Code, Codex, Cursor Agent, OpenCode, Aider, and local models: simple task files, worktree safety, cost-aware routing, observable logs, PR/comment/CI loops, and overnight bounded autonomy.

## 2. Target Capability Baseline

Composio Agent Orchestrator is positioned as "the orchestration layer for parallel AI agents." Its README says it spawns parallel coding agents, each in its own git worktree, and that each agent gets its own branch and PR; CI failures and review comments are routed back to agents; humans are pulled in for judgment only. Source: [README](https://github.com/ComposioHQ/agent-orchestrator/blob/main/README.md).

Verified target capabilities:

| Capability | Evidence |
|---|---|
| Fleet/parallel coding-agent orchestration | README describes fleets, parallel workers, and "running 30" agents as the coordination problem. |
| Worktree/branch/PR per session | README and architecture docs describe one worktree, branch, and PR per issue/session. |
| Dashboard/supervision | `ao start` launches dashboard at `localhost:3000`; CLI status and attach commands are documented. |
| CI and review reaction loop | `reactions.ci-failed` and `reactions.changes-requested` configs route events to the agent with retry/escalation. |
| Plugin architecture | Runtime, agent, workspace, tracker, SCM, notifier, terminal slots; defaults include tmux, Claude Code, worktree, GitHub. |
| Agent/runtime/tracker abstraction | Agent alternatives include Codex, Aider, Cursor, OpenCode; runtime alternatives include process/ConPTY and Docker; tracker alternatives include Linear/GitLab. |
| Session lifecycle | Development docs show states from spawning to working, PR open, CI failed, review pending, approved, mergeable, merged, cleanup. |
| Persistent runtime data | Architecture docs store sessions/worktrees under `~/.agent-orchestrator/{hash}-{projectId}/`. |
| Activity/maturity | Exa/GitHub result showed MIT license, TypeScript, thousands of stars/forks, 33 releases, latest `@composio/ao@0.2.2` on 2026-03-29, last push 2026-05-08. Source: [repo](https://github.com/ComposioHQ/agent-orchestrator). |

Additional target docs inspected: [SETUP.md](https://github.com/ComposioHQ/agent-orchestrator/blob/main/SETUP.md), [DEVELOPMENT.md](https://github.com/ComposioHQ/agent-orchestrator/blob/main/docs/DEVELOPMENT.md), [ARCHITECTURE.md](https://github.com/ComposioHQ/agent-orchestrator/blob/main/ARCHITECTURE.md), and issue [#1345 pipeline execution model](https://github.com/ComposioHQ/agent-orchestrator/issues/1345).

## 3. Ranked Top 20 Analogs

| Rank | Project | Category | Score | URL | Why it matters |
|---:|---|---|---:|---|---|
| 1 | gabrielkoerich/orchestrator | Direct analog | 9.0 | https://github.com/gabrielkoerich/orchestrator | GitHub Issues to worktree/tmux agent to PR/review/merge, with Claude/Codex/OpenCode routing. |
| 2 | multiclaude | Direct analog | 8.8 | https://github.com/dlorenc/multiclaude/ | Claude Code fleet with tmux, git worktrees, worker/supervisor/merge-queue/PR-shepherd roles, CI-driven merge/fix behavior. |
| 3 | AgentSys | Direct analog | 8.6 | https://github.com/agent-sh/agentsys | Structured 12-phase task-to-merged-PR workflow with worktrees, CI monitor/fixer, review comments, and persistent state. |
| 4 | SWE-AF | Direct analog | 8.4 | https://github.com/Agent-Field/SWE-AF | Large-scale engineering factory: issue DAG, isolated worktrees, coder/QA/reviewer/merger/verifier loops, draft PR output. |
| 5 | Daintree / Canopy | Worktree/session manager | 8.0 | https://github.com/daintreehq/daintree | Local desktop macro-orchestration for many CLI agents across worktrees, terminals, GitHub PR/issue detection, review workflows. |
| 6 | dmux | Worktree/session manager | 7.8 | https://github.com/justin-schroeder/dmux | Tmux plus worktree multiplexer for many agents, branches, merge/PR actions, hooks, multi-project support. |
| 7 | Cursor Cloud Agents | Platform competitor | 7.8 | https://cursor.com/docs/cloud-agent | Parallel cloud agents, isolated VMs, branches, PRs, GitHub/Linear/Slack/API entrypoints, artifacts, CI autofix. |
| 8 | OpenAI Codex cloud/app | Platform competitor | 7.7 | https://developers.openai.com/codex/cloud | Background parallel cloud tasks, GitHub PRs, PR comments, code review, worktrees in app. |
| 9 | Gas Town | Direct analog | 7.6 | https://github.com/steveyegge/gastown/ | Multi-agent workspace manager with tmux, agent roles, persistent git-worktree hooks, merge queue and activity feed. |
| 10 | oh-my-pr | Coding-agent orchestrator | 7.5 | https://github.com/yungookim/oh-my-pr/tree/main | Local PR babysitter: watches reviews/CI, dispatches Codex/Claude in isolated worktrees, dashboard/API/MCP. |
| 11 | Agent Review CLI | Coding-agent orchestrator | 7.2 | https://github.com/Open-Document-Alliance/Agent-Review-CLI | Parallel review/fix/integrate/verify/publish pipeline with isolated worktrees and mixed Codex/Claude/OpenCode backends. |
| 12 | Hydra (PrimeLocus) | Direct analog | 7.1 | https://github.com/PrimeLocus/Hydra | Multi-agent daemon, queue, routing, worktree isolation, PR commands, headless workers, nightly loops. |
| 13 | OpenHands | Coding-agent platform/substrate | 7.0 | https://www.openhands.dev/ | Open-source cloud coding-agent platform with GitHub/GitLab/CI/CD/Slack integrations, parallel agents, PR/review automation. |
| 14 | Open SWE | Coding-agent orchestrator | 6.8 | https://github.com/langchain-ai/open-swe | LangGraph asynchronous coding agent, GitHub issue labels to tasks, planning, parallel tasks, PR creation. |
| 15 | GitHub Copilot cloud agent | Platform competitor | 6.8 | https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent | GitHub-native branch/PR agent in Actions environment; exactly one branch/PR per task, can respond to PR comments. |
| 16 | Claude Code Agent View | Worktree/session manager | 6.7 | https://code.claude.com/docs/en/agent-view | Native multi-session view, background sessions, local worktree isolation, ready/needs-input states. |
| 17 | Factory Droid | Platform competitor | 6.5 | https://github.com/Factory-AI/droid-action | GitHub Action/GitHub App agent for PR review, issue/PR commands, security scans, workflow repair suggestions. |
| 18 | OpenClaw code agent | Worktree/session manager | 6.5 | https://github.com/goldmar/openclaw-code-agent | Managed Claude/Codex background sessions with worktree isolation, merge/PR follow-through, session tools. |
| 19 | tmux-orchestrator | Worktree/session manager | 6.3 | https://github.com/twaldin/tmux-orchestrator | Bash/tmux Claude Code team manager with worktree spawning, GitHub issue context, messaging, status, auto-approval helpers. |
| 20 | Qodo Merge / Command | Adjacent inspiration | 5.8 | https://qodo.ai/products/qodo-merge | Strong PR review/comment/CI-feedback workflow, but less of a full coding-agent fleet/worktree orchestrator. |

## 4. Top 5 Direct Analogs

1. [gabrielkoerich/orchestrator](https://github.com/gabrielkoerich/orchestrator) - Closest small/local analog. It uses GitHub Issues as the task backend, routes tasks to Claude/Codex/OpenCode, creates isolated worktrees and branches, runs agents in tmux, commits/pushes/opens PRs, posts comments, supports retries, and has optional review agents. License/stars/activity: source evidence available from GitHub page; exact license not captured in Exa highlights.
2. [multiclaude](https://github.com/dlorenc/multiclaude/) - Very close Claude-specific analog. Its spec describes one tmux window and git worktree per agent, supervisor/worker/merge-queue/PR-shepherd roles, PR creation, CI-based merge and fixup workers, crash recovery, and human tmux intervention.
3. [agent-sh/agentsys](https://github.com/agent-sh/agentsys) - Most explicit end-to-end workflow analog. `/next-task` covers discovery, worktree setup, exploration, planning, implementation, review loop, validation, docs sync, PR creation, CI monitoring, comment handling, merge, cleanup, and resume state.
4. [Agent-Field/SWE-AF](https://github.com/Agent-Field/SWE-AF) - Strongest "engineering factory" analog. It creates an issue DAG, runs coding issues in parallel isolated worktrees, has QA/reviewer/synthesizer/advisor/replanner loops, merges branches, integration-tests, verifies acceptance, and opens draft PRs. Exa showed MIT license and hundreds of stars from docs.
5. [steveyegge/gastown](https://github.com/steveyegge/gastown/) - A broader workspace manager, but highly relevant. It coordinates Claude/Codex/Gemini/Copilot/Cursor/OpenCode via tmux, has roles such as Mayor/Polecat/Witness/Refinery, persistent git-worktree hooks, beads-based work tracking, activity feed, and merge queue. It is less AO-like on GitHub issue-to-PR automation than the top three.

## 5. Top 5 Commercial/Product Competitors

1. [Cursor Cloud Agents](https://cursor.com/docs/cloud-agent) - Isolated cloud VMs, parallel agents, multi-repo workspaces, branch/PR handoff, GitHub/Linear/Slack/API triggers, artifacts, remote desktop, and documented GitHub Actions autofix. Strong commercial analog, but cloud-first.
2. [OpenAI Codex cloud](https://developers.openai.com/codex/cloud) - Background parallel cloud tasks, GitHub connection, PR creation, issue/PR mention workflows, code review, and local/app worktree support. Strong platform competitor and execution backend.
3. [GitHub Copilot cloud agent](https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent) - GitHub-native agent: researches, plans, edits on a branch, optionally opens one PR per task, runs in Actions-powered ephemeral environments, can be invoked from issues/PR comments/integrations.
4. [Devin](https://docs.devin.ai/get-started/devin-intro) - Autonomous software engineer product for tickets, bugs, testing, PR review, codebase Q&A, Slack/Teams/Linear/Jira workflows, and PR comments. Strong user-problem overlap, closed architecture.
5. [Codegen](https://codegen.ai/) - Enterprise agent infrastructure for task-to-PR workflows with GitHub/Linear/Slack/MCP integrations, dashboards, repo rules, governance, cost/performance analytics, and enterprise deployment options.

Also relevant: [Google Jules](https://jules.google/) and [jules-action](https://github.com/google-labs-code/jules-action) for async cloud coding, GitHub issue labels, PRs, concurrent tasks, CI-failure/security/dependency workflows; [Factory Droid](https://github.com/Factory-AI/droid-action) for GitHub action-based PR/issue agent workflows; [Qodo](https://docs.qodo.ai/v1/tools/tools-list) for PR review, CI feedback, and suggestion implementation.

## 6. Top 5 Inspiration Projects

1. [dmux](https://github.com/justin-schroeder/dmux) - Best UI mental model for local terminal/worktree multiplexing: one pane per task, supported agents, merge/PR menu, lifecycle hooks.
2. [Daintree](https://github.com/daintreehq/daintree) - Strong local desktop supervision: panel grid, status inference, dev server management, context injection, MCP surface for agents to request orchestration actions.
3. [oh-my-pr](https://github.com/yungookim/oh-my-pr/tree/main) - Best narrow CI/review loop inspiration: durable SQLite queue, local REST/API/MCP, isolated PR worktrees, review thread resolution, bounded healing sessions.
4. [Cursor Worktrees](https://cursor.com/docs/configuration/worktrees) - Good UX primitives for per-task worktrees, `/best-of-n`, handoff/apply/delete commands, and model comparison.
5. [Qodo Merge](https://docs.qodo.ai/qodo-documentation/qodo-merge/features/chat-on-code-suggestions) - Good PR conversation UX: review suggestions become implementable discussions and the system decides whether the user wants apply/explain/help.

## 7. Feature Matrix

Legend: Yes = documented; Partial = documented but narrower than AO; Unknown = not found in inspected sources.

| Project | Category | Score | Multi-agent/fleet | Worktree/branch isolation | PR workflow | CI fixing | Review-comment fixing | Dashboard/supervision | Agent abstraction | Runtime abstraction | Tracker integration | CLI/local support | Notes |
|---|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| Composio AO | Target | 10 | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | GitHub/Linear/GitLab | Yes | Baseline. |
| gabrielkoerich/orchestrator | Direct | 9.0 | Yes | Yes | Yes | Partial | Partial | CLI dashboard | Claude/Codex/OpenCode | tmux | GitHub Issues | Yes | Very close local issue-to-PR loop. |
| multiclaude | Direct | 8.8 | Yes | Yes | Yes | Yes | Partial | tmux | Claude-focused | tmux | GitHub | Yes | Merge queue and PR shepherd. |
| AgentSys | Direct | 8.6 | Yes | Yes | Yes | Yes | Yes | Workflow/state files | Role/model agents | Claude plugin/skills | GitHub/GitLab/local | Yes | Strong gated SDLC pipeline. |
| SWE-AF | Direct | 8.4 | Yes | Yes | Draft PR | QA/test loops | Review loops | API/control plane | Role/model map | AgentField runtime | GitHub | Self-host/API | Very scalable, heavier. |
| Daintree | Worktree/session | 8.0 | Yes | Yes | PR detection | Unknown | Review workflows | Desktop | 15 CLI agents | PTY/process | GitHub | Yes | Local desktop fleet UX. |
| dmux | Worktree/session | 7.8 | Yes | Yes | Yes | Unknown | Unknown | Tmux TUI | Many CLI agents | tmux | GitHub | Yes | Excellent lightweight primitive. |
| Cursor Cloud Agents | Platform | 7.8 | Yes | Cloud branches/VMs | Yes | Yes | PR comment trigger | Web/dashboard | Cursor models | Cloud VM | GitHub/GitLab/Linear/Slack | No local-first | Strong SaaS competitor. |
| Codex cloud/app | Platform | 7.7 | Yes | Cloud/app worktrees | Yes | Prompted CI fix | Yes | Web/app | Codex | Cloud/local app | GitHub | CLI/app | Strong backend and product. |
| Gas Town | Direct | 7.6 | Yes | Yes | Merge queue | Partial | Unknown | TUI/feed | Many CLIs | tmux/hooks | beads/GitHub-ish | Yes | More workspace OS than AO clone. |
| oh-my-pr | Orchestrator | 7.5 | Multiple PRs | Yes | Existing PRs | Yes | Yes | React/TUI/API/MCP | Claude/Codex | Local process | GitHub | Yes | PR babysitter, not task spawner. |
| Agent Review CLI | Orchestrator | 7.2 | Yes | Yes | Yes | Verify loop | Review/fix pipeline | Ink TUI | Codex/Claude/OpenCode | subprocess | GitHub via gh | Yes | Review-focused, not general task tracker. |
| Hydra PrimeLocus | Direct | 7.1 | Yes | Yes | Commands | Self-healing | Unknown | Daemon/status | Claude/Gemini/Codex | workers/MCP | GitHub | Yes | Strong queue/routing. |
| OpenHands | Platform/substrate | 7.0 | Yes | Sandbox/cloud | Yes | CI/CD adaptable | Yes | Web/API/SDK | Model-agnostic | Sandbox/cloud | GitHub/GitLab/Slack | Self-host | Big platform, less worktree-centric. |
| Open SWE | Orchestrator | 6.8 | Yes | Cloud sandbox | Yes | Unknown | Human feedback | Web/cloud | LangGraph/model config | Cloud sandbox | GitHub labels/issues | Partial | Single-agent async tasks at scale. |
| Copilot cloud agent | Platform | 6.8 | Multiple tasks | Branch/env | One PR/task | Tests/linters | PR comment mention | GitHub UI | Copilot/custom | GitHub Actions env | GitHub | No | GitHub-native. |
| Claude Agent View | Worktree/session | 6.7 | Yes | Yes | Ready-for-review state | Unknown | User replies | TUI | Claude only | supervisor process | None/direct repo | Yes | Native Claude multi-session UX. |
| Factory Droid | Platform | 6.5 | Partial | Action workspace | Yes | Suggests/repairs | Yes | GitHub comments/logs | Droid | GitHub Actions | GitHub/Jira etc. | CLI/action | PR automation, not fleet control. |
| OpenClaw code agent | Worktree/session | 6.5 | Partial | Yes | Yes | Goal loops | Plan/review gates | Chat control plane | Claude/Codex | plugin/runtime | GitHub via gh | Yes | Good control-plane tools. |
| tmux-orchestrator | Worktree/session | 6.3 | Yes | Yes | GitHub issue/PR prompts | Unknown | Unknown | tmux scripts | Claude Code | tmux/bash | GitHub issue context | Yes | Simple bash/tmux approach. |
| Qodo Merge/Command | Adjacent | 5.8 | Specialized agents | No | PR tools | CI feedback | Suggestion chat | PR comments | Qodo agents | SaaS/action/CLI | GitHub/GitLab/Jira/Linear | Partial | Strong review layer, not AO clone. |

## 8. Worktree and Session Managers

These tools are primarily session/worktree control planes rather than complete task-to-merged-PR orchestrators:

- [Daintree](https://github.com/daintreehq/daintree): local desktop environment for Claude, Gemini, Codex, OpenCode, Cursor Agent, Aider, and others; worktree dashboard, terminal grid, context injection, GitHub PR/issue detection, MCP action surface.
- [dmux](https://github.com/justin-schroeder/dmux): tmux pane per task, worktree and branch per task, supported agents include Claude Code/Codex/OpenCode/Cursor/Copilot/Qwen/Gemini/Amp; merge and create-PR menu.
- [Claude Code Agent View](https://code.claude.com/docs/en/agent-view): native multi-background-session view with `.claude/worktrees/` isolation.
- [tmux-orchestrator](https://github.com/twaldin/tmux-orchestrator): bash/tmux scripts for Claude teams, `spawn_coder` with worktree and GitHub issue context.
- [agent-dashboard](https://github.com/bjornjee/agent-dashboard): real-time tmux dashboard for Claude/Codex agents, PR create/merge shortcuts, hooks and workflow skills.
- [agentdock](https://github.com/vishalnarkhede/agentdock): web dashboard for parallel Claude/Cursor agents across repos with tmux sessions, worktrees, Linear/Slack context, WebSocket terminal streaming.
- [OpenClaw code agent](https://github.com/goldmar/openclaw-code-agent): chat-launched Claude/Codex sessions with worktree isolation and merge/PR follow-through.

## 9. Agent Frameworks and Substrates

Generic agent frameworks should not be ranked above coding-agent orchestrators unless they ship a concrete coding workflow.

- [LangGraph](https://github.com/langchain-ai/langgraph) is important because Open SWE is built on it, but LangGraph itself is a substrate, not a direct AO analog.
- [CrewAI](https://github.com/crewAIInc/crewAI), [AutoGen](https://github.com/microsoft/autogen), [AG2](https://github.com/ag2ai/ag2), [CAMEL](https://github.com/camel-ai/camel), and Microsoft Agent Framework are useful for multi-agent abstractions but lack AO's concrete worktree/branch/PR/CI/review lifecycle in their core product.
- [OpenHands](https://www.openhands.dev/) is more than a substrate: it is an open coding-agent platform with GitHub/GitLab/CI/CD/Slack integrations and parallel agent claims. It is still less directly comparable to AO's local worktree/session manager design.
- [Open SWE](https://github.com/langchain-ai/open-swe) is a concrete asynchronous coding agent product: GitHub issue labels, planning, parallel tasks, and PR creation. It is a direct coding-agent orchestrator, not merely LangGraph.

## 10. Downranked or Excluded Candidates

- [Qodo Merge/Command](https://qodo.ai/products/qodo-merge): strong PR review and implementation assistance, but not a fleet/worktree/session orchestrator.
- [Factory Droid](https://github.com/Factory-AI/droid-action): strong GitHub PR/issue action surface; less evidence of local multi-agent fleet and worktree lifecycle.
- [OpenCode GitHub integration](https://opencode.ubitools.com/github/): useful issue/PR comment and Actions-based agent workflow; it is an agent integration rather than an AO-style orchestrator.
- [Codex Swarm](https://github.com/basilisk-labs/codex-swarm): useful task/agent prompt structure and branch_pr mode, but appears repo-local and lighter on autonomous fleet runtime.
- [Convex AI files](https://docs.convex.dev/ai): useful agent setup/skills guidance, not an orchestrator.
- Generic frameworks: CrewAI, AutoGen/AG2, CAMEL, LangGraph alone. They can build an orchestrator but do not themselves provide AO's worktree/PR/CI/review loop.
- Seed items with insufficient Exa evidence in this pass: `fynnfluegge/agtx`, `Enderfga/claw-orchestrator`, `conduit-cli/conduit`, `njbrake/agent-of-empires`, `kbwo/ccmanager`, `mco-org/mco`. These should remain unranked until primary sources confirm concrete coding-agent orchestration.

## 11. Category Map

- Fleet orchestrators: Composio AO, gabrielkoerich/orchestrator, multiclaude, AgentSys, SWE-AF, Gas Town, Hydra.
- Session/worktree managers: Daintree, dmux, Claude Agent View, tmux-orchestrator, agent-dashboard, agentdock, OpenClaw code agent.
- Coding-agent platforms: Cursor Cloud Agents, Codex cloud/app, GitHub Copilot cloud agent, Devin, Codegen, Jules, OpenHands.
- Coding-agent frameworks/substrates: LangGraph, OpenHands SDK, CrewAI, AutoGen/AG2, CAMEL, Microsoft Agent Framework.
- PR/review automation: oh-my-pr, Qodo Merge, Factory Droid, Codex code review, OpenCode GitHub integration.
- Generic multi-agent frameworks: useful for roles/routing/planning, but weak direct analogs unless paired with git/worktree/PR/CI machinery.

## 12. Implications for ai-orchestrator

A smaller/local-first alternative can win by being opinionated where large platforms are broad:

- Local-first orchestration: use local worktrees, local agent CLIs, local state, and no required SaaS control plane.
- Multi-model routing: route analysis to Claude, implementation to Codex/OpenCode, review to another agent, cheap classification to small/local models.
- Interoperability: first-class adapters for Codex, Claude Code, Cursor Agent, OpenCode, Aider, Gemini, Copilot CLI.
- Artifact-driven workflows: every run should produce task JSON, prompt, transcript, diff, test logs, PR URL, review findings, retry history, and final report.
- Git/worktree safety: dirty-tree checks, branch naming, protected main checkout, cleanup policies, conflict escalation.
- PR/review/CI loops: CI logs and review comments should be normalized as "findings" and routed back through bounded repair attempts.
- Cost-aware execution: model budgets per task, max retries, overnight queue caps, and "cheap reviewer before expensive fixer."
- Local inference helper layer: local models can classify, summarize logs, cluster review comments, or draft task plans even if final coding uses cloud CLIs.
- Human-readable task files: avoid opaque DB-only state; keep resumption and debugging possible with Markdown/JSON/YAML.

## 13. Recommended Roadmap for a Local-First Alternative

### Immediate

- Implement one task = one branch = one worktree = one run record.
- Add adapters for at least Codex and Claude Code with a common `run(prompt, cwd, mode)` interface.
- Store durable artifacts under `.ai-orchestrator/runs/{id}/`: prompt, transcript, diff, test output, status, cost estimate, PR URL.
- Add `status`, `attach`, `send`, `kill`, `cleanup`, and `open-pr` commands.
- Add safety checks: refuse dirty base checkout, never write in main checkout, preserve failed worktrees.

### Short-term

- Add a task queue with concurrency caps, retry caps, and resumable state.
- Add GitHub issue and PR integration through `gh`.
- Normalize CI failures and review comments into a `findings.json` schema.
- Add a bounded repair loop: fetch finding, send to same or alternate agent, run verification, push update, comment back.
- Add TUI/web dashboard for sessions, current status, last output, diff, PR link, CI state, and "needs human" queue.

### Medium-term

- Add agent/model routing rules by task type, risk, cost, file ownership, and prior success rate.
- Add multi-agent review: one implementer, one reviewer, one fixer; all artifacts preserved.
- Add Linear/Jira/GitLab providers behind a tracker abstraction.
- Add local-model helpers for summarization, routing, and log triage.
- Add overnight autonomous mode with strict budgets, protected paths, escalation policies, and final morning report.

## 14. Source Appendix

Target:

- https://github.com/ComposioHQ/agent-orchestrator
- https://github.com/ComposioHQ/agent-orchestrator/blob/main/README.md
- https://github.com/ComposioHQ/agent-orchestrator/blob/main/SETUP.md
- https://github.com/ComposioHQ/agent-orchestrator/blob/main/docs/DEVELOPMENT.md
- https://github.com/ComposioHQ/agent-orchestrator/blob/main/ARCHITECTURE.md
- https://github.com/ComposioHQ/agent-orchestrator/issues/1345

Open/source-adjacent:

- https://github.com/gabrielkoerich/orchestrator
- https://github.com/gabrielkoerich/orchestrator/blob/main/specs.md
- https://github.com/dlorenc/multiclaude/
- https://github.com/dlorenc/multiclaude/blob/main/SPEC.md
- https://github.com/agent-sh/agentsys
- https://github.com/agent-sh/agentsys/blob/main/docs/workflows/NEXT-TASK.md
- https://github.com/Agent-Field/SWE-AF
- https://github.com/Agent-Field/SWE-AF/blob/main/docs/ARCHITECTURE.md
- https://github.com/daintreehq/daintree
- https://github.com/canopyide/canopy
- https://github.com/justin-schroeder/dmux
- https://github.com/steveyegge/gastown/
- https://github.com/steveyegge/gastown/blob/main/docs/agent-provider-integration.md
- https://github.com/yungookim/oh-my-pr/tree/main
- https://github.com/Open-Document-Alliance/Agent-Review-CLI
- https://github.com/PrimeLocus/Hydra
- https://github.com/goldmar/openclaw-code-agent
- https://github.com/twaldin/tmux-orchestrator
- https://github.com/bjornjee/agent-dashboard
- https://github.com/vishalnarkhede/agentdock
- https://github.com/langchain-ai/open-swe
- https://www.openhands.dev/
- https://opencode.ubitools.com/github/

Commercial/platform:

- https://cursor.com/docs/cloud-agent
- https://cursor.com/docs/configuration/worktrees
- https://cursor.com/docs/cloud-agent/api/endpoints
- https://developers.openai.com/codex/cloud
- https://developers.openai.com/codex/integrations/github
- https://developers.openai.com/codex/app/worktrees
- https://developers.openai.com/codex/github-action
- https://docs.github.com/en/copilot/concepts/coding-agent/coding-agent
- https://docs.github.com/copilot/concepts/agents/about-third-party-agents
- https://docs.devin.ai/get-started/devin-intro
- https://devin.ai/lp/coding-agent
- https://codegen.ai/
- https://jules.google/
- https://github.com/google-labs-code/jules-action
- https://github.com/Factory-AI/droid-action
- https://docs.factory.ai/cli/features/install-github-app
- https://docs.factory.ai/onboarding/configuring-your-review-droid/droid-yaml-configuration
- https://qodo.ai/products/qodo-merge
- https://qodo.ai/products/qodo-command
- https://docs.qodo.ai/v1/tools/tools-list
- https://docs.qodo.ai/qodo-documentation/qodo-merge/features/chat-on-code-suggestions
