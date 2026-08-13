from __future__ import annotations

import copy
import json
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
            {"id": tid, "title": tid.title(), "objective": f"research {tid}", "queries": [f"query {tid}"]}
            for tid in ids
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
            return self.results.pop(0)


class ReviewFindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.runs = self.root / "runs"
        self.worker = self.root / "worker.md"
        self.worker.write_text("Return findings JSON.", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def runner(self, executor, **kwargs):
        return research.ResearchRunner(
            session=kwargs.pop("session", "s1"),
            runs_dir=self.runs,
            backend="opencode",
            max_workers=kwargs.pop("max_workers", 2),
            timeout=1,
            executor=executor,
            worker_contract_path=self.worker,
            **kwargs,
        )

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

    def test_opencode_overlay_preserves_restrictive_read_and_other_existing_denies(self):
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
        self.assertEqual(cfg["permission"]["websearch"], "deny")
        self.assertEqual(cfg["agent"][research.OPENCODE_AGENT]["permission"]["read"], "deny")
        self.assertEqual(cfg["agent"][research.OPENCODE_AGENT]["permission"]["webfetch"], "deny")
        for key in research.OPENCODE_DENY:
            self.assertEqual(cfg["permission"][key], "deny")
            self.assertEqual(cfg["agent"][research.OPENCODE_AGENT]["permission"][key], "deny")

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


if __name__ == "__main__":
    unittest.main()
