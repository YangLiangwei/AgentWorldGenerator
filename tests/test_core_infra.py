import unittest

from agentworld.core import StateStore, build_schedule
from agentworld.core.runtime import SimulationRuntime
from agentworld.schema import ActionSpec, AgentState, WorldSpec, WorldState


def _spec() -> WorldSpec:
    return WorldSpec(
        name="infra",
        max_ticks=10,
        actions={
            "rest": ActionSpec(name="rest", cost=0, params=[]),
        },
        initial_state=WorldState(
            resources={"start": {"food": 1}},
            agents={"a": AgentState(id="a", location="start")},
        ),
    )


class CoreInfraTests(unittest.TestCase):
    def test_scheduler_priority(self):
        sch = build_schedule({
            "b": {"action": "rest", "priority": 1},
            "a": {"action": "rest", "priority": 5},
        })
        self.assertEqual(sch[0].actor_id, "a")

    def test_state_store_and_diagnostics(self):
        rt = SimulationRuntime(_spec())
        rt.run_tick({"a": {"action": "rest", "params": {}}})
        self.assertEqual(len(rt.diagnostics.rows), 1)
        cp = rt.state_store.get_checkpoint("tick-1")
        self.assertEqual(cp["tick"], 1)

        diff = StateStore.diff(rt.state_store.get_checkpoint("tick-0"), cp)
        self.assertIn("unchanged", diff)


if __name__ == "__main__":
    unittest.main()
