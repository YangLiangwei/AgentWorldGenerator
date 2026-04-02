import json
import tempfile
import unittest
from pathlib import Path

from agentworld.orchestrator import Orchestrator, RunTask


class OrchestratorTests(unittest.TestCase):
    def test_orchestrator_run_single_task(self):
        with tempfile.TemporaryDirectory() as td:
            world = {
                "name": "w",
                "max_ticks": 5,
                "actions": {
                    "gather": {"cost": 1, "params": ["resource"]},
                    "rest": {"cost": 0, "params": []},
                },
                "initial_state": {
                    "tick": 0,
                    "resources": {"start": {"food": 5}},
                    "agents": {"a1": {"energy": 5, "location": "start", "traits": {"role": "participant"}}},
                },
            }
            wp = Path(td) / "world.json"
            wp.write_text(json.dumps(world))

            orch = Orchestrator()
            orch.submit(RunTask(task_id="t1", world_path=str(wp), ticks=3))
            results = orch.run_all()
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].status, "ok")
            self.assertEqual(results[0].final_tick, 3)


if __name__ == "__main__":
    unittest.main()
