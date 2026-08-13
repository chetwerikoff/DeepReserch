from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import research


class OpenCodeExportRegressionTests(unittest.TestCase):
    def test_verification_reads_export_larger_than_64k(self):
        session_id = "large-export-session"
        export_data = json.dumps(
            {
                "padding": "x" * (64 * 1024),
                "info": {"id": session_id, "agent": research.OPENCODE_AGENT},
            }
        ).encode()
        self.assertGreater(len(export_data), 64 * 1024)
        stdout = (
            json.dumps(
                {
                    "type": "text",
                    "sessionID": session_id,
                    "part": {"type": "text", "text": '{"findings":[]}'},
                }
            )
            + "\n"
        ).encode()
        inv = research.Invocation("opencode", ("opencode", "run"), {}, "hello")

        def fake_run(argv, **kwargs):
            export_stdout = kwargs["stdout"]
            if export_stdout is research.subprocess.PIPE:
                return research.subprocess.CompletedProcess(argv, 0, export_data[:65536], b"")
            export_stdout.write(export_data)
            export_stdout.flush()
            return research.subprocess.CompletedProcess(argv, 0, None, b"")

        with patch.object(research.subprocess, "run", side_effect=fake_run):
            answer, actual_session_id, agent, error = research.verify_opencode_output(inv, stdout, 1)

        self.assertIsNone(error)
        self.assertEqual(actual_session_id, session_id)
        self.assertEqual(agent, research.OPENCODE_AGENT)
        self.assertEqual(answer, b'{"findings":[]}')


if __name__ == "__main__":
    unittest.main()
