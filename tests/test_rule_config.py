import unittest

from agentworld.rules import validate_rule_pack_config
from agentworld.core.runtime import SimulationRuntime, ValidationError
from agentworld.schema import ActionSpec, AgentState, WorldSpec, WorldState


class RuleConfigTests(unittest.TestCase):
    def test_validate_rule_pack_config(self):
        issues = validate_rule_pack_config({"queue": {"queues": []}})
        self.assertTrue(any(i.level == "error" for i in issues))

    def test_runtime_rejects_invalid_rule_pack(self):
        spec = WorldSpec(
            name="w",
            max_ticks=10,
            actions={"rest": ActionSpec(name="rest", cost=0, params=[])},
            initial_state=WorldState(
                resources={"start": {"food": 1}},
                agents={"a1": AgentState(id="a1")},
            ),
            rules={"queue": {"queues": []}},
        )
        with self.assertRaises(ValidationError):
            SimulationRuntime(spec)


if __name__ == "__main__":
    unittest.main()
