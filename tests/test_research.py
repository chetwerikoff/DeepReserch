from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import research


VALID_FINDINGS = b'{"findings":[{"id":"f1","claim":"claim","source_url":"https://example.com/a","source_tier":"S"}]}'


def plan(*ids: str) -> dict:
    return {
        "topic": "topic",
        "tasks": [
            {
                "id": task_id,
                "title": task_id.title(),
                "objective": f"research {task_id}",
                "queries": [f"query {task_id}"],
            }
            for task_id in ids
        ],
    }


class SequenceExecutor:
    def __init__(self, results):
        self.results = list(results)
        self.invocations = []
        self.lock = threading.Lock()

    def __call__(self, invocation, timeout):
        with self.lock:
            self.invocations.append(invocation)
            if not self.results:
                raise AssertionError("unexpected extra invocation")
            item = self.results.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.runs = self.root / "runs"
        self.worker = ROOT / "prompts" / "worker.md"

    def tearDown(self):
        self.tmp.cleanup()

    def runner(self, executor, **kwargs):
        return research.ResearchRunner(
            session=kwargs.pop("session", "s1"),
            runs_dir=self.runs,
            backend=kwargs.pop("backend", "opencode"),
            fallback_backend=kwargs.pop("fallback_backend", None),
            max_workers=kwargs.pop("max_workers", 2),
            timeout=1,
            executor=executor,
            worker_contract_path=self.worker,
            **kwargs,
        )

    def test_candidate_discovery_contract_reuses_opportunistic_enrichment(self):
        worker_contract = self.worker.read_text(encoding="utf-8")
        manager_contract = (ROOT / "prompts" / "manager.md").read_text(encoding="utf-8")

        self.assertIn("execute all manager-authored supplied queries before any derived query", worker_contract)
        self.assertIn("zero or one opportunistic enrichment", worker_contract)
        self.assertIn("one promising candidate or material lead", worker_contract)
        self.assertIn("at most **two tightly related derived search queries**", worker_contract)
        self.assertIn("cannot trigger another enrichment round", worker_contract)
        self.assertIn("Do not repeat research already adequately covered", manager_contract)
        self.assertIn("it substitutes for later deep research", manager_contract)

    def fake_opencode(self):
        path = self.root / "fake-opencode.py"
        path.write_text(
            "#!/usr/bin/env python3\n"
            "import json, os, sys\n"
            "if sys.argv[1:3] == ['debug', 'config']:\n"
            "    if os.environ.get('FAKE_CONFIG_MODE') == 'permissive':\n"
            "        print(json.dumps({'permission': {'edit': 'allow', 'bash': 'allow', 'external_directory': 'allow', 'task': 'allow'}, 'agent': {'deep-research-worker': {'mode': 'primary', 'permission': {'edit': 'allow', 'bash': 'allow', 'external_directory': 'allow', 'task': 'allow'}}}, 'mcp': {'exa': {'type': 'remote', 'url': 'https://mcp.exa.ai/mcp', 'enabled': True}}}))\n"
            "    else:\n"
            "        print(os.environ['OPENCODE_CONFIG_CONTENT'])\n"
            "elif sys.argv[1] == 'export':\n"
            "    print(json.dumps({'info': {'id': sys.argv[2], 'agent': os.environ.get('FAKE_AGENT', 'deep-research-worker')}}))\n"
            "else:\n"
            "    marker = os.environ.get('FAKE_RUN_MARKER')\n"
            "    if marker:\n"
            "        open(marker, 'w', encoding='utf-8').write('run\\n')\n"
            "    sid = 'fake-session'\n"
            "    print(json.dumps({'type': 'step_start', 'sessionID': sid, 'part': {'type': 'step-start'}}))\n"
            "    print(json.dumps({'type': 'text', 'sessionID': sid, 'part': {'type': 'text', 'text': '{\"findings\":[]}'} }))\n"
            "    print(json.dumps({'type': 'step_finish', 'sessionID': sid, 'part': {'type': 'step-finish'}}))\n",
            encoding="utf-8",
        )
        path.chmod(0o755)
        return path

    def test_cursor_invocation_is_ask_mode_and_never_force(self):
        inv = research.build_invocation(
            "cursor",
            "hello",
            model="m1",
            cursor_command="cursor-agent",
            base_env={},
            cursor_workspace=self.root / "cursor-workspace",
        )
        self.assertEqual(inv.argv[:5], ("cursor-agent", "--print", "--mode=ask", "--output-format", "text"))
        self.assertIn("--model", inv.argv)
        self.assertNotIn("--force", inv.argv)
        self.assertIn("--approve-mcps", inv.argv)
        workspace = Path(inv.argv[inv.argv.index("--workspace") + 1])
        self.assertEqual(workspace, (self.root / "cursor-workspace").resolve())
        cursor_mcp = json.loads((workspace / ".cursor" / "mcp.json").read_text())
        self.assertEqual(
            cursor_mcp,
            {"mcpServers": {research.EXA_MCP_NAME: {"url": research.EXA_MCP_URL}}},
        )

    def test_opencode_invocation_enforces_global_and_agent_denials(self):
        existing = {
            "permission": {"websearch": "allow", "edit": "allow"},
            "agent": {research.OPENCODE_AGENT: {"permission": {"bash": "allow"}}},
            "model": "provider/model",
        }
        inv = research.build_invocation(
            "opencode",
            "hello",
            opencode_command="opencode",
            base_env={"OPENCODE_CONFIG_CONTENT": json.dumps(existing)},
        )
        self.assertEqual(inv.argv[:5], ("opencode", "run", "--agent", research.OPENCODE_AGENT, "--format"))
        self.assertNotIn("--attach", inv.argv)
        cfg = json.loads(inv.env["OPENCODE_CONFIG_CONTENT"])
        for key in ("edit", "bash", "external_directory", "task"):
            self.assertEqual(cfg["permission"][key], "deny")
            self.assertEqual(cfg["agent"][research.OPENCODE_AGENT]["permission"][key], "deny")
        for key in ("websearch", "webfetch"):
            self.assertEqual(cfg["permission"][key], "allow")
            self.assertEqual(cfg["agent"][research.OPENCODE_AGENT]["permission"][key], "allow")
        self.assertEqual(
            cfg["mcp"],
            {
                research.EXA_MCP_NAME: {
                    "type": "remote",
                    "url": research.EXA_MCP_URL,
                    "enabled": True,
                    "oauth": False,
                    "codemode": False,
                }
            },
        )
        for key in research.EXA_MCP_TOOLS:
            self.assertEqual(cfg["permission"][key], "allow")
            self.assertEqual(cfg["agent"][research.OPENCODE_AGENT]["permission"][key], "allow")
        self.assertEqual(cfg["model"], "provider/model")

    def test_raw_cursor_attempt_records_argv_and_mcp_content(self):
        ex = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        summary = self.runner(ex, backend="cursor").execute(research.validate_plan(plan("a")))
        self.assertEqual(summary["counts"]["completed"], 1)
        raw = json.loads((self.runs / "s1" / "raw" / "a-attempt-01.txt").read_text())
        self.assertEqual(raw["schema"], "deep-research-raw-attempt/v2")
        self.assertEqual(raw["argv"], list(ex.invocations[0].argv))
        self.assertEqual(raw["argv"][2], "--mode=ask")
        self.assertNotIn("--force", raw["argv"])
        self.assertIsNone(raw["opencode_config_content"])
        self.assertEqual(
            raw["cursor_mcp_json"],
            {"mcpServers": {research.EXA_MCP_NAME: {"url": research.EXA_MCP_URL}}},
        )

    def test_raw_opencode_config_redacts_credentials_and_keeps_audit_structure(self):
        secret_api_key = "host-api-key-should-not-persist"
        secret_token = "host-token-should-not-persist"
        secret_header = "Bearer host-header-should-not-persist"
        existing = {
            "provider": {
                "host": {
                    "options": {
                        "apiKey": secret_api_key,
                        "access_token": secret_token,
                        "headers": {"Authorization": secret_header},
                    }
                }
            },
            "permission": {"edit": "allow"},
            "agent": {research.OPENCODE_AGENT: {"permission": {"bash": "allow"}}},
            "model": "host/model",
        }
        ex = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        runner = self.runner(ex)
        runner = research.ResearchRunner(
            session="s1",
            runs_dir=self.runs,
            backend="opencode",
            max_workers=2,
            timeout=1,
            executor=ex,
            worker_contract_path=self.worker,
        )
        with patch.dict(os.environ, {"OPENCODE_CONFIG_CONTENT": json.dumps(existing)}, clear=False):
            runner.execute(research.validate_plan(plan("a")))
        raw_path = self.runs / "s1" / "raw" / "a-attempt-01.txt"
        raw_text = raw_path.read_text()
        self.assertNotIn(secret_api_key, raw_text)
        self.assertNotIn(secret_token, raw_text)
        self.assertNotIn(secret_header, raw_text)
        persisted = json.loads(json.loads(raw_text)["opencode_config_content"])
        options = persisted["provider"]["host"]["options"]
        self.assertEqual(options["apiKey"], "[REDACTED]")
        self.assertEqual(options["access_token"], "[REDACTED]")
        self.assertEqual(options["headers"], "[REDACTED]")
        self.assertEqual(persisted["model"], "host/model")
        self.assertIn("permission", persisted)
        self.assertIn("agent", persisted)
        self.assertEqual(persisted["agent"][research.OPENCODE_AGENT]["permission"]["edit"], "deny")
        self.assertEqual(
            persisted["mcp"][research.EXA_MCP_NAME]["url"],
            research.EXA_MCP_URL,
        )

    def test_opencode_subprocess_verification_accepts_selected_agent(self):
        command = self.fake_opencode()
        inv = research.build_invocation(
            "opencode", "hello", opencode_command=str(command), base_env={"FAKE_AGENT": research.OPENCODE_AGENT}
        )
        result = research.subprocess_executor(inv, 1)
        self.assertEqual(result.exit_code, 0)
        self.assertIsNone(result.verification_error)
        self.assertEqual(result.opencode_session_id, "fake-session")
        self.assertEqual(result.opencode_agent, research.OPENCODE_AGENT)
        self.assertEqual(result.stdout, b'{"findings":[]}')
        self.assertNotEqual(result.raw_stdout, result.stdout)

    def test_opencode_same_name_permissive_agent_is_rejected_before_run(self):
        command = self.fake_opencode()
        marker = self.root / "opencode-run-marker"
        inv = research.build_invocation(
            "opencode",
            "hello",
            opencode_command=str(command),
            base_env={"FAKE_CONFIG_MODE": "permissive", "FAKE_RUN_MARKER": str(marker)},
        )
        result = research.subprocess_executor(inv, 1)
        self.assertEqual(result.verification_error, "opencode_safe_mode_preflight_failed:global_permission:edit")
        self.assertFalse(marker.exists())
        self.assertEqual(result.raw_stdout, b"")

    def test_opencode_fallback_agent_fails_task_without_extra_attempt(self):
        command = self.fake_opencode()
        runner = self.runner(research.subprocess_executor, opencode_command=str(command))
        with patch.dict(os.environ, {"FAKE_AGENT": "default"}, clear=False):
            summary = runner.execute(research.validate_plan(plan("a")))
        self.assertEqual(summary["tasks"]["a"]["status"], "failed")
        self.assertEqual(summary["tasks"]["a"]["attempts"], 1)
        state = json.loads((self.runs / "s1" / "state.json").read_text())
        self.assertIn("opencode_agent_verification_failed:unexpected_agent:default", state["tasks"]["a"]["error"])
        raw = json.loads((self.runs / "s1" / "raw" / "a-attempt-01.txt").read_text())
        self.assertEqual(raw["opencode_agent"], "default")
        self.assertIn("opencode_agent_verification_failed", raw["verification_error"])
        self.assertFalse((self.runs / "s1" / "results" / "a.json").exists())

    def test_opencode_selected_agent_run_is_accepted(self):
        command = self.fake_opencode()
        runner = self.runner(research.subprocess_executor, opencode_command=str(command))
        with patch.dict(os.environ, {"FAKE_AGENT": research.OPENCODE_AGENT}, clear=False):
            summary = runner.execute(research.validate_plan(plan("a")))
        self.assertEqual(summary["tasks"]["a"]["status"], "completed")
        self.assertEqual(summary["tasks"]["a"]["attempts"], 1)

    def test_invalid_inline_opencode_config_fails_closed(self):
        with self.assertRaises(research.RunnerFatal):
            research.build_invocation("opencode", "x", base_env={"OPENCODE_CONFIG_CONTENT": "{"})

    def test_plan_rejects_bad_and_duplicate_ids(self):
        bad = plan("ok")
        bad["tasks"][0]["id"] = "../escape"
        with self.assertRaises(research.RunnerFatal):
            research.validate_plan(bad)
        dup = plan("same", "same")
        with self.assertRaises(research.RunnerFatal):
            research.validate_plan(dup)

    def test_plan_research_bounds_are_optional_object_allowlisted(self):
        bounds = {
            "task_budget": 12,
            "follow_up_task_budget": 4,
            "follow_up_discovery_rounds": 1,
            "max_workers": 4,
            "per_task_timeout_seconds": 300,
            "backend_guidance": None,
            "nested": {"manager_owned": [1, True, None]},
        }
        raw = plan("a")
        raw["research_bounds"] = bounds
        raw["unknown_root"] = {"must": "drop"}
        validated = research.validate_plan(raw)
        self.assertEqual(validated["research_bounds"], bounds)
        self.assertIsNot(validated["research_bounds"], bounds)
        self.assertNotIn("unknown_root", validated)

        legacy = research.validate_plan(plan("legacy"))
        self.assertNotIn("research_bounds", legacy)

        invalid = plan("a")
        invalid["research_bounds"] = []
        with self.assertRaises(research.RunnerFatal):
            research.validate_plan(invalid)

    def test_research_bounds_survive_admission_resume_and_append(self):
        bounds = {
            "task_budget": 12,
            "follow_up_task_budget": 4,
            "follow_up_discovery_rounds": 1,
            "max_workers": 4,
            "per_task_timeout_seconds": 300,
            "backend_guidance": None,
        }
        initial = plan("a")
        initial["research_bounds"] = copy.deepcopy(bounds)
        first = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        self.runner(first).execute(research.validate_plan(initial))

        plan_path = self.runs / "s1" / "plan.json"
        state_path = self.runs / "s1" / "state.json"
        self.assertEqual(json.loads(plan_path.read_text())["research_bounds"], bounds)
        initial_sha = json.loads(state_path.read_text())["tasks"]["a"]["task_definition_sha256"]

        resumed = SequenceExecutor([])
        self.runner(resumed).execute(research.validate_plan(initial))
        self.assertEqual(resumed.invocations, [])
        self.assertEqual(json.loads(plan_path.read_text())["research_bounds"], bounds)

        revised_bounds = copy.deepcopy(bounds)
        revised_bounds["follow_up_task_budget"] = 5
        bounds_only_revision = plan("a")
        bounds_only_revision["research_bounds"] = revised_bounds
        bounds_only_resume = SequenceExecutor([])
        self.runner(bounds_only_resume).execute(research.validate_plan(bounds_only_revision))
        self.assertEqual(bounds_only_resume.invocations, [])
        self.assertEqual(json.loads(plan_path.read_text())["research_bounds"], revised_bounds)
        self.assertEqual(
            json.loads(state_path.read_text())["tasks"]["a"]["task_definition_sha256"],
            initial_sha,
        )

        appended = plan("a", "b")
        appended["research_bounds"] = copy.deepcopy(revised_bounds)
        second = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        summary = self.runner(second).execute(research.validate_plan(appended))
        self.assertEqual(summary["counts"]["completed"], 2)
        self.assertEqual(len(second.invocations), 1)
        self.assertIn("research b", second.invocations[0].prompt)
        self.assertEqual(json.loads(plan_path.read_text())["research_bounds"], revised_bounds)
        self.assertEqual(
            json.loads(state_path.read_text())["tasks"]["a"]["task_definition_sha256"],
            initial_sha,
        )

    def test_legacy_plan_without_research_bounds_still_runs(self):
        ex = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        summary = self.runner(ex, session="legacy").execute(research.validate_plan(plan("a")))
        self.assertEqual(summary["counts"]["completed"], 1)
        durable = json.loads((self.runs / "legacy" / "plan.json").read_text())
        self.assertNotIn("research_bounds", durable)

    def test_contained_path_rejects_escape(self):
        base = self.root / "safe"
        base.mkdir()
        with self.assertRaises(research.RunnerFatal):
            research.safe_path(base, "..", "outside")

    def test_primary_success_writes_raw_result_and_state(self):
        ex = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        summary = self.runner(ex).execute(research.validate_plan(plan("a")))
        self.assertEqual(summary["counts"]["completed"], 1)
        raw = self.runs / "s1" / "raw" / "a-attempt-01.txt"
        result = self.runs / "s1" / "results" / "a.json"
        self.assertTrue(raw.exists())
        self.assertTrue(result.exists())
        raw_value = json.loads(raw.read_text())
        self.assertEqual(raw_value["schema"], "deep-research-raw-attempt/v2")
        self.assertEqual(raw_value["argv"], list(ex.invocations[0].argv))
        self.assertIsInstance(raw_value["opencode_config_content"], str)
        self.assertIsNone(raw_value["cursor_mcp_json"])
        self.assertEqual(research.base64.b64decode(raw_value["stdout_b64"]), VALID_FINDINGS)
        result_value = json.loads(result.read_text())
        self.assertEqual(result_value["accepted_attempt_ordinal"], 1)
        self.assertEqual(result_value["task_id"], "a")

    def test_invalid_primary_then_invalid_repair_then_fallback_success_exactly_three(self):
        ex = SequenceExecutor(
            [
                research.InvocationResult(b"not-json", b"", 0),
                research.InvocationResult(b'{"findings":"bad"}', b"", 0),
                research.InvocationResult(VALID_FINDINGS, b"", 0),
            ]
        )
        summary = self.runner(ex, fallback_backend="cursor").execute(research.validate_plan(plan("a")))
        self.assertEqual(summary["tasks"]["a"]["status"], "completed")
        self.assertEqual(len(ex.invocations), 3)
        state = json.loads((self.runs / "s1" / "state.json").read_text())
        kinds = [a["kind"] for a in state["tasks"]["a"]["attempts"]]
        self.assertEqual(kinds, ["primary-research", "primary-format-repair", "fallback-research"])
        self.assertEqual(state["tasks"]["a"]["accepted_attempt_ordinal"], 3)
        self.assertIn("not-json", ex.invocations[1].prompt)
        self.assertIn("worker stdout has no JSON object", ex.invocations[1].prompt)
        self.assertNotIn("research a", ex.invocations[1].prompt)

    def test_primary_timeout_goes_directly_to_fallback(self):
        ex = SequenceExecutor(
            [
                research.InvocationResult(b"", b"", None, True),
                research.InvocationResult(VALID_FINDINGS, b"", 0),
            ]
        )
        summary = self.runner(ex, fallback_backend="cursor").execute(research.validate_plan(plan("a")))
        self.assertEqual(summary["tasks"]["a"]["status"], "completed")
        self.assertEqual(len(ex.invocations), 2)
        state = json.loads((self.runs / "s1" / "state.json").read_text())
        self.assertEqual([a["kind"] for a in state["tasks"]["a"]["attempts"]], ["primary-research", "fallback-research"])

    def test_fallback_invalid_stops_without_fourth_invocation(self):
        ex = SequenceExecutor(
            [
                research.InvocationResult(b"bad", b"", 0),
                research.InvocationResult(b"still bad", b"", 0),
                research.InvocationResult(b"fallback bad", b"", 0),
            ]
        )
        summary = self.runner(ex, fallback_backend="cursor").execute(research.validate_plan(plan("a")))
        self.assertEqual(summary["tasks"]["a"]["status"], "failed")
        self.assertEqual(len(ex.invocations), 3)

    def test_task_local_failure_does_not_stop_sibling(self):
        barrier = threading.Barrier(2)
        calls = []

        def executor(inv, timeout):
            calls.append(inv)
            barrier.wait(timeout=2)
            if "research bad" in inv.prompt:
                return research.InvocationResult(b"", b"boom", 1)
            return research.InvocationResult(VALID_FINDINGS, b"", 0)

        summary = self.runner(executor, max_workers=2).execute(research.validate_plan(plan("bad", "good")))
        self.assertEqual(summary["tasks"]["bad"]["status"], "failed")
        self.assertEqual(summary["tasks"]["good"]["status"], "completed")

    def test_concurrent_completions_preserve_both_state_updates(self):
        barrier = threading.Barrier(2)

        def executor(inv, timeout):
            barrier.wait(timeout=2)
            return research.InvocationResult(VALID_FINDINGS, b"", 0)

        summary = self.runner(executor, max_workers=2).execute(research.validate_plan(plan("a", "b")))
        self.assertEqual(summary["counts"]["completed"], 2)
        state = json.loads((self.runs / "s1" / "state.json").read_text())
        self.assertEqual(state["tasks"]["a"]["status"], "completed")
        self.assertEqual(state["tasks"]["b"]["status"], "completed")

    def test_unknown_inflight_after_crash_is_consumed_and_not_replayed(self):
        class SimulatedCrash(BaseException):
            pass

        crashing = SequenceExecutor([SimulatedCrash("power loss")])
        with self.assertRaises(research.RunnerFatal):
            self.runner(crashing).execute(research.validate_plan(plan("a")))
        state = json.loads((self.runs / "s1" / "state.json").read_text())
        self.assertEqual(state["tasks"]["a"]["status"], "in_flight")
        self.assertEqual(len(state["tasks"]["a"]["attempts"]), 1)
        self.assertFalse((self.runs / "s1" / "raw" / "a-attempt-01.txt").exists())

        resumed = SequenceExecutor([])
        summary = self.runner(resumed).execute(research.validate_plan(plan("a")))
        self.assertEqual(summary["tasks"]["a"]["status"], "failed")
        self.assertEqual(len(resumed.invocations), 0)
        state2 = json.loads((self.runs / "s1" / "state.json").read_text())
        self.assertEqual(len(state2["tasks"]["a"]["attempts"]), 1)
        self.assertIn("interrupted_unknown", state2["tasks"]["a"]["error"])

    def test_resume_from_complete_raw_continues_without_relaunch(self):
        p = research.validate_plan(plan("a"))
        runner = self.runner(SequenceExecutor([]))
        runner.admit(p)
        attempt = runner.start("a", "primary-research", "opencode", None)
        invocation = research.build_invocation("opencode", "hello", base_env={})
        research.exclusive_write(
            runner.raw_path("a", attempt["ordinal"]),
            research.json_bytes(research.raw_value(attempt, invocation, research.InvocationResult(VALID_FINDINGS, b"", 0))),
        )

        resumed = SequenceExecutor([])
        summary = self.runner(resumed).execute(p)
        self.assertEqual(summary["tasks"]["a"]["status"], "completed")
        self.assertEqual(len(resumed.invocations), 0)

    def test_result_to_state_crash_reconciles_without_relaunch(self):
        p = research.validate_plan(plan("a"))
        runner = self.runner(SequenceExecutor([]))
        runner.admit(p)
        attempt = runner.start("a", "primary-research", "opencode", None)
        invocation = research.build_invocation("opencode", "hello", base_env={})
        research.exclusive_write(
            runner.raw_path("a", attempt["ordinal"]),
            research.json_bytes(research.raw_value(attempt, invocation, research.InvocationResult(VALID_FINDINGS, b"", 0))),
        )
        state = runner.state["tasks"]["a"]
        result = {
            "task_id": "a",
            "task_definition_sha256": state["task_definition_sha256"],
            "accepted_attempt_ordinal": 1,
            "findings": research.validate_findings(json.loads(VALID_FINDINGS)),
        }
        research.atomic_json(runner.result_path("a"), result)
        resumed = SequenceExecutor([])
        summary = self.runner(resumed).execute(p)
        self.assertEqual(summary["tasks"]["a"]["status"], "completed")
        self.assertEqual(len(resumed.invocations), 0)

    def test_completed_task_is_skipped_on_resume(self):
        first = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        self.runner(first).execute(research.validate_plan(plan("a")))
        second = SequenceExecutor([])
        summary = self.runner(second).execute(research.validate_plan(plan("a")))
        self.assertEqual(summary["tasks"]["a"]["status"], "completed")
        self.assertEqual(second.invocations, [])

    def test_task_definition_drift_after_attempt_is_runner_fatal(self):
        first = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        self.runner(first).execute(research.validate_plan(plan("a")))
        changed = plan("a")
        changed["tasks"][0]["objective"] = "changed semantics"
        with self.assertRaises(research.RunnerFatal):
            self.runner(SequenceExecutor([])).execute(research.validate_plan(changed))

    def test_task_definition_drift_after_admission_before_launch_is_fatal(self):
        original = research.validate_plan(plan("a"))
        self.runner(SequenceExecutor([])).admit(original)
        changed = plan("a")
        changed["tasks"][0]["queries"] = ["changed query"]
        with self.assertRaises(research.RunnerFatal):
            self.runner(SequenceExecutor([])).execute(research.validate_plan(changed))

    def test_plan_revision_may_append_new_id_only(self):
        first = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        self.runner(first).execute(research.validate_plan(plan("a")))
        second = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        summary = self.runner(second).execute(research.validate_plan(plan("a", "b")))
        self.assertEqual(summary["counts"]["completed"], 2)
        self.assertEqual(len(second.invocations), 1)
        self.assertIn("research b", second.invocations[0].prompt)

        with self.assertRaises(research.RunnerFatal):
            self.runner(SequenceExecutor([])).execute(research.validate_plan(plan("b")))

    def test_source_group_github_repo_and_hostname(self):
        self.assertEqual(research.source_group("https://github.com/Owner/Repo/issues/1"), "github.com/owner/repo")
        self.assertEqual(research.source_group("https://docs.example.com/a"), "docs.example.com")

    def test_metrics_dedupe_groups_and_weak_ids(self):
        p = research.validate_plan(plan("a", "b"))
        ex = SequenceExecutor([
            research.InvocationResult(b'{"findings":[{"id":"f1","claim":"c1","source_url":"https://github.com/O/R/a"},{"id":"f2","claim":"c2","source_url":"https://github.com/O/R/b"}]}', b"", 0),
            research.InvocationResult(b'{"findings":[{"id":"f1","claim":"c3","source_url":"https://example.org/x"}]}', b"", 0),
        ])
        self.runner(ex).execute(p)
        synthesis = {
            "insights": [
                {"id": "i1", "claim": "x", "evidence": ["a:f1", "a:f2", "b:f1"]},
                {"id": "i2", "claim": "y", "evidence": ["a:f1"]},
            ]
        }
        research.atomic_json(self.runs / "s1" / "synthesis.json", synthesis)
        metrics = research.compute_metrics(self.runs / "s1")
        self.assertEqual(metrics["insights"][0]["source_group_depth"], 2)
        self.assertEqual(metrics["minimum_depth"], 1)
        self.assertEqual(metrics["weak_insight_ids"], ["i2"])
        self.assertIn("do not prove", metrics["disclaimer"])
        serialized = json.dumps(metrics)
        self.assertNotIn("saturation", serialized.lower())
        self.assertNotIn("completeness", serialized.lower())

    def test_metrics_reject_missing_or_malformed_refs(self):
        ex = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        self.runner(ex).execute(research.validate_plan(plan("a")))
        for evidence in (["a:missing"], ["bad:ref:shape"]):
            research.atomic_json(
                self.runs / "s1" / "synthesis.json",
                {"insights": [{"id": "i1", "claim": "x", "evidence": evidence}]},
            )
            with self.assertRaises(research.RunnerFatal):
                research.compute_metrics(self.runs / "s1")

    def test_worker_output_rejects_duplicate_findings_and_bad_url(self):
        with self.assertRaises(research.ValidationError):
            research.validate_findings(
                {
                    "findings": [
                        {"id": "f1", "claim": "x", "source_url": "not-url"},
                        {"id": "f1", "claim": "y", "source_url": "https://example.com"},
                    ]
                }
            )

    def test_extract_json_tolerates_fence_and_chatter(self):
        payload = research.extract_object("hello\n```json\n{\"findings\": []}\n```\nbye")
        self.assertEqual(payload, {"findings": []})

    def test_cli_task_failure_exits_zero_but_missing_backend_is_fatal(self):
        plan_path = self.root / "plan.json"
        plan_path.write_text(json.dumps(plan("a")), encoding="utf-8")
        fake = self.root / "cursor-fail"
        fake.write_text("#!/bin/sh\necho boom >&2\nexit 1\n", encoding="utf-8")
        fake.chmod(0o755)
        rc = research.main([
            "run", "--session", "cli1", "--runs-dir", str(self.runs),
            "--plan", str(plan_path), "--backend", "cursor",
            "--cursor-command", str(fake), "--max-workers", "1",
        ])
        self.assertEqual(rc, 0)
        state = json.loads((self.runs / "cli1" / "state.json").read_text())
        self.assertEqual(state["tasks"]["a"]["status"], "failed")

        rc2 = research.main([
            "run", "--session", "cli2", "--runs-dir", str(self.runs),
            "--plan", str(plan_path), "--backend", "cursor",
            "--cursor-command", str(self.root / "missing-cursor"),
        ])
        self.assertEqual(rc2, 2)

    def test_preexisting_raw_symlink_escape_is_rejected(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink unavailable")
        run_root = self.runs / "s1"
        run_root.mkdir(parents=True)
        outside = self.root / "outside"
        outside.mkdir()
        try:
            os.symlink(outside, run_root / "raw", target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable")
        with self.assertRaises(research.RunnerFatal):
            self.runner(SequenceExecutor([]))

    def test_partial_raw_is_task_local_interrupted_unknown_and_sibling_continues(self):
        p = research.validate_plan(plan("bad", "good"))
        seeded = self.runner(SequenceExecutor([]))
        seeded.admit(p)
        attempt = seeded.start("bad", "primary-research", "opencode", None)
        seeded.raw_path("bad", attempt["ordinal"]).write_text("{", encoding="utf-8")

        resumed = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
        summary = self.runner(resumed, max_workers=1).execute(p)

        self.assertEqual(summary["tasks"]["bad"]["status"], "failed")
        self.assertIn("interrupted_unknown", summary["tasks"]["bad"]["error"])
        self.assertEqual(summary["tasks"]["good"]["status"], "completed")
        self.assertEqual(len(resumed.invocations), 1)
        state = json.loads((self.runs / "s1" / "state.json").read_text())
        self.assertEqual(len(state["tasks"]["bad"]["attempts"]), 1)

    def test_failed_state_write_does_not_leak_candidate_into_memory_or_later_state(self):
        p = research.validate_plan(plan("a"))
        runner = self.runner(SequenceExecutor([]))
        runner.admit(p)
        before = copy.deepcopy(runner.state)
        real_atomic_json = research.atomic_json

        def fail_state_write(path, value):
            if path == runner.state_path:
                raise OSError("injected state write failure")
            return real_atomic_json(path, value)

        with patch.object(research, "atomic_json", side_effect=fail_state_write):
            with self.assertRaises(OSError):
                runner.start("a", "primary-research", "opencode", None)

        self.assertEqual(runner.state, before)
        disk = json.loads(runner.state_path.read_text())
        self.assertEqual(disk["tasks"]["a"]["status"], "pending")
        self.assertEqual(disk["tasks"]["a"]["attempts"], [])

        runner.fail("a", "later mutation")
        disk2 = json.loads(runner.state_path.read_text())
        self.assertEqual(disk2["tasks"]["a"]["status"], "failed")
        self.assertEqual(disk2["tasks"]["a"]["attempts"], [])

    def test_opencode_overlay_preserves_restrictive_read_and_restores_web_allow(self):
        existing = {
            "permission": {"read": "deny", "websearch": "deny", "edit": "allow"},
            "agent": {
                research.OPENCODE_AGENT: {
                    "permission": {"read": "deny", "webfetch": "deny", "bash": "allow"}
                }
            },
        }
        cfg = json.loads(research.opencode_config(json.dumps(existing)))

        self.assertEqual(cfg["permission"]["read"], "deny")
        self.assertEqual(cfg["permission"]["websearch"], "allow")
        self.assertEqual(cfg["permission"]["webfetch"], "allow")
        self.assertEqual(cfg["agent"][research.OPENCODE_AGENT]["permission"]["read"], "deny")
        self.assertEqual(cfg["agent"][research.OPENCODE_AGENT]["permission"]["webfetch"], "allow")
        for key in research.OPENCODE_DENY:
            self.assertEqual(cfg["permission"][key], "deny")
            self.assertEqual(cfg["agent"][research.OPENCODE_AGENT]["permission"][key], "deny")
        for key in research.OPENCODE_WEB_ALLOW:
            self.assertEqual(cfg["permission"][key], "allow")
            self.assertEqual(cfg["agent"][research.OPENCODE_AGENT]["permission"][key], "allow")

    def test_selected_opencode_agent_is_closed_world_and_keeps_secret_denies(self):
        existing = {
            "permission": {
                "custom_global_*": "allow",
                "read": {"*.secret": "deny", "*.env": "allow"},
                "websearch": "allow",
            },
            "agent": {
                research.OPENCODE_AGENT: {
                    "permission": {
                        "custom_mutate": "allow",
                        "mymcp_*": "allow",
                        "bash": "allow",
                        "read": {"private/**": "deny", "*.env.*": "allow"},
                        "webfetch": "deny",
                    }
                }
            },
        }

        cfg = json.loads(research.opencode_config(json.dumps(existing)))
        perms = cfg["agent"][research.OPENCODE_AGENT]["permission"]
        expected_keys = {
            "*",
            "read",
            *research.OPENCODE_ALLOW,
            *research.OPENCODE_WEB_ALLOW,
            *research.EXA_MCP_TOOLS,
            *research.OPENCODE_DENY,
        }
        self.assertEqual(set(perms), expected_keys)
        self.assertEqual(perms["*"], "deny")
        self.assertNotIn("custom_mutate", perms)
        self.assertNotIn("mymcp_*", perms)
        self.assertNotIn("custom_global_*", perms)
        for key in research.OPENCODE_DENY:
            self.assertEqual(perms[key], "deny")
        self.assertEqual(perms["webfetch"], "allow")
        self.assertEqual(perms["websearch"], "allow")
        for key in research.EXA_MCP_TOOLS:
            self.assertEqual(perms[key], "allow")
        self.assertIsInstance(perms["read"], dict)
        self.assertEqual(perms["read"]["*"], "allow")
        self.assertEqual(perms["read"]["*.env"], "deny")
        self.assertEqual(perms["read"]["*.env.*"], "deny")
        self.assertEqual(perms["read"]["*.env.example"], "allow")
        self.assertEqual(perms["read"]["*.secret"], "deny")
        self.assertEqual(perms["read"]["private/**"], "deny")

    def test_opencode_existing_scalar_deny_stays_fail_closed(self):
        for existing in (
            {"permission": "deny"},
            {"agent": {research.OPENCODE_AGENT: {"permission": "deny"}}},
        ):
            with self.subTest(existing=existing):
                cfg = json.loads(research.opencode_config(json.dumps(existing)))
                perms = cfg["agent"][research.OPENCODE_AGENT]["permission"]
                self.assertEqual(perms["*"], "deny")
                for key in ("read", *research.OPENCODE_ALLOW):
                    self.assertEqual(perms[key], "deny")
                for key in research.EXA_MCP_TOOLS:
                    self.assertEqual(perms[key], "deny")
                for key in research.OPENCODE_WEB_ALLOW:
                    self.assertEqual(perms[key], "allow")
                for key in research.OPENCODE_DENY:
                    self.assertEqual(perms[key], "deny")

    def test_completed_state_requires_valid_bound_result_on_resume(self):
        for variant in ("missing", "corrupt", "fingerprint", "accepted_ordinal"):
            with self.subTest(variant=variant):
                session = f"s-{variant}"
                first = SequenceExecutor([research.InvocationResult(VALID_FINDINGS, b"", 0)])
                p = research.validate_plan(plan("a"))
                self.runner(first, session=session).execute(p)
                result_path = self.runs / session / "results" / "a.json"
                state_path = self.runs / session / "state.json"

                if variant == "missing":
                    result_path.unlink()
                elif variant == "corrupt":
                    result_path.write_text("{", encoding="utf-8")
                elif variant == "fingerprint":
                    result = json.loads(result_path.read_text())
                    result["task_definition_sha256"] = "0" * 64
                    research.atomic_json(result_path, result)
                else:
                    state = json.loads(state_path.read_text())
                    state["tasks"]["a"]["accepted_attempt_ordinal"] = 2
                    research.atomic_json(state_path, state)

                resumed = SequenceExecutor([])
                with self.assertRaises(research.RunnerFatal):
                    self.runner(resumed, session=session).execute(p)
                self.assertEqual(resumed.invocations, [])

    def test_atomic_write_replaces_with_complete_json(self):
        path = self.root / "state.json"
        research.atomic_json(path, {"a": 1})
        research.atomic_json(path, {"b": 2})
        self.assertEqual(json.loads(path.read_text()), {"b": 2})


if __name__ == "__main__":
    unittest.main()
