import unittest

from agentworld.core.diagnostics import DiagnosticsCollector
from agentworld.core.scheduler import build_schedule
from agentworld.core.state_store import StateStore


class CoreInfraTests(unittest.TestCase):
    def test_scheduler_priority(self):
        schedule = build_schedule(
            {
                "a": {"action": "rest", "priority": 1},
                "b": {"action": "rest", "priority": 3},
            }
        )
        self.assertEqual(schedule[0].actor_id, "b")

    def test_diagnostics_record(self):
        d = DiagnosticsCollector()
        row = d.record(1, ["ok:rest", "fail:no_resource"])
        self.assertEqual(row.success_actions, 1)
        self.assertEqual(row.failure_actions, 1)
        self.assertIn("fail:no_resource", row.error_codes)

    def test_state_store_diff(self):
        prev = {"tick": 1}
        curr = {"tick": 2}
        diff = StateStore.diff(prev, curr)
        self.assertFalse(diff["unchanged"])


if __name__ == "__main__":
    unittest.main()
