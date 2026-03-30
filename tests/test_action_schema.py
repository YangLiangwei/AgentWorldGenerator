import unittest

from agentworld.protocol import validate_action_schema
from agentworld.schema import WorldSpec


class ActionSchemaTests(unittest.TestCase):
    def test_validate_action_schema(self):
        issues = validate_action_schema({"gather": {"params": "oops"}})
        self.assertTrue(any(i.level == "error" for i in issues))

    def test_worldspec_reads_action_codes(self):
        data = {
            "name": "w",
            "actions": {
                "rest": {
                    "cost": 0,
                    "params": [],
                    "success_code": "ok:rest",
                    "failure_codes": ["fail:validation"],
                }
            },
            "initial_state": {
                "tick": 0,
                "resources": {"start": {"food": 1}},
                "agents": {"a1": {"energy": 5, "location": "start"}},
            },
        }
        spec = WorldSpec.from_dict(data)
        self.assertEqual(spec.actions["rest"].success_code, "ok:rest")
        self.assertIn("fail:validation", spec.actions["rest"].failure_codes)


if __name__ == "__main__":
    unittest.main()
