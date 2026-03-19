import json
import unittest
from pathlib import Path

from agentworld.compiler import compile_scene
from agentworld.core.runtime import SimulationRuntime, ValidationError
from agentworld.schema import ActionSpec


def _load_spec():
    p = Path(__file__).resolve().parents[1] / "examples" / "world_minimal.json"
    return compile_scene(json.loads(p.read_text()))


class RuntimeTests(unittest.TestCase):
    def test_deterministic_transition(self):
        spec1 = _load_spec()
        spec2 = _load_spec()
        r1 = SimulationRuntime(spec1)
        r2 = SimulationRuntime(spec2)

        decisions = {
            "a1": {"action": "gather", "params": {"resource": "food"}},
            "a2": {"action": "rest", "params": {}},
        }

        r1.run_tick(decisions)
        r2.run_tick(decisions)

        self.assertEqual(r1.state.tick, 1)
        self.assertEqual(r2.state.tick, 1)
        self.assertEqual(r1.state.resources, r2.state.resources)
        self.assertEqual(r1.state.agents["a1"].inventory, r2.state.agents["a1"].inventory)

    def test_action_validation(self):
        spec = _load_spec()
        runtime = SimulationRuntime(spec)

        with self.assertRaises(ValidationError):
            runtime.step_action("a1", "unknown", {})

        with self.assertRaises(ValidationError):
            runtime.step_action("a1", "gather", {})

    def test_object_and_outcome_atoms(self):
        spec = _load_spec()
        runtime = SimulationRuntime(spec)

        obj = runtime.get_object("a1")
        self.assertEqual(obj["kind"], "agent")

        outcome = runtime.step_action("a1", "gather", {"resource": "food"})
        self.assertIn("ok:", outcome.result)
        self.assertIn("energy", outcome.state_delta)

    def test_custom_action_handler(self):
        spec = _load_spec()
        spec.actions["ping"] = ActionSpec(name="ping", cost=0, params=[])
        runtime = SimulationRuntime(spec)

        def _ping(agent, params):
            agent.traits["pinged"] = True
            return "ok:ping", {"traits": {"pinged": True}}

        runtime.register_action_handler("ping", _ping)
        out = runtime.step_action("a1", "ping", {})
        self.assertEqual(out.result, "ok:ping")
        self.assertTrue(runtime.state.agents["a1"].traits["pinged"])

    def test_role_constraint(self):
        spec = _load_spec()
        spec.actions["treat"] = ActionSpec(name="treat", cost=0, params=[])
        spec.constraints = [{"kind": "requires_role", "action": "treat", "roles": ["doctor"]}]
        spec.initial_state.agents["a1"].traits["role"] = "student"
        runtime = SimulationRuntime(spec)

        with self.assertRaises(ValidationError):
            runtime.step_action("a1", "treat", {})


if __name__ == "__main__":
    unittest.main()
