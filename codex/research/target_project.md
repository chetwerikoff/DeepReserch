# Target Project: ComposioHQ Agent Orchestrator

Repository:

- https://github.com/ComposioHQ/agent-orchestrator

## Research goal

Find the closest open-source and commercial analogs of ComposioHQ Agent Orchestrator.

The research must be anchored to the actual capabilities of ComposioHQ Agent Orchestrator, not just generic "multi-agent framework" keywords.

## Target project category

ComposioHQ Agent Orchestrator should be treated as a coding-agent orchestration platform.

The expected product space includes:

- fleets of AI coding agents
- parallel coding-agent execution
- one git worktree per agent/session
- one branch per task/session
- one PR per agent/session
- automatic CI failure handling
- automatic review-comment handling
- dashboard/supervision layer
- agent-agnostic execution: Claude Code, Codex, Aider, OpenCode, or similar
- runtime-agnostic execution: tmux, process, ConPTY, Docker, or similar
- tracker integration: GitHub, Linear, or similar
- local or self-hosted coding-agent orchestration
- autonomous task execution with human escalation only when needed

## Target anchoring step

Before ranking analogs, first inspect the target repository:

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

Build a short "Target Capability Baseline" section before competitor scoring.

The analog scoring must be anchored to this extracted baseline, not only to the prompt description.

## Expected baseline capabilities to verify

When inspecting ComposioHQ Agent Orchestrator, look for evidence of:

1. Fleet-style orchestration of multiple coding agents.
2. Parallel agent execution.
3. Isolated git worktree per agent/session.
4. Dedicated branch and PR per task/session.
5. Support for Claude Code, Codex, Aider, OpenCode, or similar agents.
6. Runtime abstraction: tmux, process, ConPTY, Docker, or similar.
7. Tracker abstraction: GitHub, Linear, or similar.
8. Dashboard or supervision UI.
9. CI failure detection and autonomous fixing.
10. Review-comment detection and autonomous fixing.
11. Merge conflict handling.
12. Session lifecycle management.
13. Agent activity/logging/event stream.
14. Human escalation only when judgment is needed.
15. Local-first or self-hosted workflow.
16. Production maturity: releases, docs, tests, active issues/PRs.

## What should count as strong overlap

A project has strong overlap with ComposioHQ Agent Orchestrator if it helps a user do this:

1. Connect a codebase or project.
2. Create multiple coding-agent tasks.
3. Spawn multiple isolated agents/sessions.
4. Give each agent an isolated workspace/worktree/branch.
5. Let agents implement changes.
6. Open or manage PRs.
7. Watch CI and review comments.
8. Ask agents to fix failures/comments.
9. Track all sessions from one dashboard or CLI.
10. Let humans intervene only when needed.

## Important warning

Do not treat generic agent frameworks as direct analogs unless they implement or demonstrate an actual coding-agent orchestration workflow similar to ComposioHQ Agent Orchestrator.

LangGraph, AutoGen, CrewAI, CAMEL, and similar projects may be useful substrates, but they are not direct analogs unless they include concrete coding-agent orchestration with worktrees, PRs, sessions, review loops, CI handling, or dashboard supervision.