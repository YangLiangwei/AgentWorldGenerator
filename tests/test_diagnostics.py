import unittest

from agentworld.replay.diagnostics import summarize_events


class DiagnosticsTests(unittest.TestCase):
    def test_summarize_events(self):
        events = [
            {"tick": 1, "result": "ok:rest"},
            {"tick": 1, "result": "fail:no_resource"},
            {"tick": 2, "result": "ok:gather"},
        ]
        s = summarize_events(events)
        self.assertEqual(s["total_actions"], 3)
        self.assertEqual(s["failure_actions"], 1)
        self.assertIn("fail:no_resource", s["error_codes"])


if __name__ == "__main__":
    unittest.main()
