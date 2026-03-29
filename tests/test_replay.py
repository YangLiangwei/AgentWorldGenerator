import tempfile
import unittest
from pathlib import Path

from agentworld.replay import build_replay_html, write_run_artifacts


class ReplayTests(unittest.TestCase):
    def test_write_artifacts_and_build_html(self):
        with tempfile.TemporaryDirectory() as td:
            paths = write_run_artifacts(
                td,
                events=[{"tick": 1, "actor_id": "a1", "action": "rest", "payload": {}, "result": "ok:rest"}],
                snapshots=[{"tick": 1, "agents": {}, "resources": {}}],
                render_contexts=[{"world_state_summary": {"tick": 1}}],
                prompts=[{"tick": 1, "prompt": "hello"}],
            )
            self.assertTrue(Path(paths["events"]).exists())
            out_html = Path(td) / "replay.html"
            build_replay_html(td, str(out_html))
            self.assertTrue(out_html.exists())


if __name__ == "__main__":
    unittest.main()
