import unittest

from agentworld.core.runtime import SimulationRuntime, ValidationError
from agentworld.schema import ActionSpec, AgentState, WorldSpec, WorldState


def _make_spec() -> WorldSpec:
    return WorldSpec(
        name="rules-world",
        max_ticks=10,
        actions={
            "rest": ActionSpec(name="rest", cost=0, params=[]),
            "move": ActionSpec(name="move", cost=0, params=["location"]),
            "transfer": ActionSpec(name="transfer", cost=0, params=["target_id", "resource", "amount"]),
            "enqueue": ActionSpec(name="enqueue", cost=0, params=["queue_id"]),
            "service": ActionSpec(name="service", cost=0, params=["queue_id"]),
        },
        initial_state=WorldState(
            tick=0,
            resources={"a": {"food": 1}, "b": {"food": 1}},
            agents={
                "x": AgentState(id="x", location="a", inventory={"food": 2}, traits={"role": "doctor"}),
                "y": AgentState(id="y", location="a", inventory={}, traits={"role": "student"}),
            },
        ),
        rules={
            "access": {"policies": {"move@b": ["doctor"]}},
            "queue": {"queues": {"q1": []}},
            "transfer": True,
        },
    )


class RuleMiddlewareTests(unittest.TestCase):
    def test_transfer_rule(self):
        rt = SimulationRuntime(_make_spec())
        rt.step_action("x", "transfer", {"target_id": "y", "resource": "food", "amount": 1})
        self.assertEqual(rt.state.agents["x"].inventory["food"], 1)
        self.assertEqual(rt.state.agents["y"].inventory["food"], 1)

    def test_access_rule(self):
        rt = SimulationRuntime(_make_spec())
        with self.assertRaises(ValidationError):
            rt.step_action("y", "move", {"location": "b"})

    def test_queue_rule(self):
        rt = SimulationRuntime(_make_spec())
        with self.assertRaises(ValidationError):
            rt.step_action("x", "service", {"queue_id": "q1"})

        rt.step_action("x", "enqueue", {"queue_id": "q1"})
        out = rt.step_action("x", "service", {"queue_id": "q1"})
        self.assertEqual(out.result, "ok:service")


if __name__ == "__main__":
    unittest.main()
