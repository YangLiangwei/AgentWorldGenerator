import unittest

from agentworld.replay.diagnostics import summarize_events


class DiagTests(unittest.TestCase):
    def test_summarize_events_fields(self):
        events = [
            {"tick": 1, "action": "gather", "result": "ok:gather"},
            {"tick": 1, "action": "move", "result": "fail:unknown_location"},
            {"tick": 2, "action": "move", "result": "fail:unknown_location"},
        ]
        s = summarize_events(events)
        self.assertEqual(s["total_actions"], 3)
        self.assertIn("top_failures", s)
        self.assertIn("action_stats", s)
        self.assertGreater(s["action_stats"]["move"]["failure_rate"], 0)


if __name__ == "__main__":
    unittest.main()
