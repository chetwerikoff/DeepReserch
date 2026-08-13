import json
import unittest

import research


class AuditProjectionTests(unittest.TestCase):
    def test_arbitrary_provider_and_agent_values_do_not_persist(self):
        cfg = {
            "provider": {
                "custom": {
                    "options": {
                        "subscriptionKey": "provider-secret-value",
                        "ordinarySetting": "also-must-not-persist",
                    }
                }
            },
            "permission": {
                "edit": "deny",
                "bash": "deny",
                "external_directory": "deny",
                "task": "deny",
            },
            "agent": {
                research.OPENCODE_AGENT: {
                    "mode": "primary",
                    "permission": {
                        "edit": "deny",
                        "bash": "deny",
                        "external_directory": "deny",
                        "task": "deny",
                    },
                    "options": {"customCredential": "agent-secret-value"},
                    "arbitraryField": "agent-arbitrary-value",
                }
            },
            "mcp": {
                research.EXA_MCP_NAME: {
                    "type": "remote",
                    "url": research.EXA_MCP_URL,
                    "enabled": True,
                    "oauth": False,
                    "codemode": False,
                }
            },
            "model": "provider/model",
            "unrelated": {"value": "unrelated-secret-value"},
        }

        persisted = research.scrub_opencode_config(json.dumps(cfg))

        for secret in (
            "provider-secret-value",
            "also-must-not-persist",
            "agent-secret-value",
            "agent-arbitrary-value",
            "unrelated-secret-value",
        ):
            self.assertNotIn(secret, persisted)

        audit = json.loads(persisted)
        self.assertEqual(
            audit["provider"]["custom"]["options"]["subscriptionKey"],
            "[REDACTED]",
        )
        self.assertNotIn("options", audit["agent"][research.OPENCODE_AGENT])
        self.assertNotIn("arbitraryField", audit["agent"][research.OPENCODE_AGENT])
        self.assertNotIn("unrelated", audit)
        self.assertEqual(
            audit["agent"][research.OPENCODE_AGENT]["permission"]["edit"],
            "deny",
        )
        self.assertEqual(
            audit["mcp"][research.EXA_MCP_NAME]["url"],
            research.EXA_MCP_URL,
        )


if __name__ == "__main__":
    unittest.main()
