from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import research


class OpenCodeClosedWorldTests(unittest.TestCase):
    def test_selected_agent_is_closed_world_and_keeps_secret_denies(self):
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

        expected_keys = {"*", "read", *research.OPENCODE_ALLOW, *research.OPENCODE_DENY}
        self.assertEqual(set(perms), expected_keys)
        self.assertEqual(perms["*"], "deny")
        self.assertNotIn("custom_mutate", perms)
        self.assertNotIn("mymcp_*", perms)
        self.assertNotIn("custom_global_*", perms)
        for key in research.OPENCODE_DENY:
            self.assertEqual(perms[key], "deny")

        self.assertEqual(perms["webfetch"], "deny")
        self.assertIsInstance(perms["read"], dict)
        self.assertEqual(perms["read"]["*"], "allow")
        self.assertEqual(perms["read"]["*.env"], "deny")
        self.assertEqual(perms["read"]["*.env.*"], "deny")
        self.assertEqual(perms["read"]["*.env.example"], "allow")
        self.assertEqual(perms["read"]["*.secret"], "deny")
        self.assertEqual(perms["read"]["private/**"], "deny")

    def test_existing_scalar_deny_stays_fail_closed(self):
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
                for key in research.OPENCODE_DENY:
                    self.assertEqual(perms[key], "deny")


if __name__ == "__main__":
    unittest.main()
