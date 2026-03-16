import unittest

from agentworld.validators import validate_world_report


class ValidatorTests(unittest.TestCase):
    def test_validation_report_ok(self):
        world = {
            "name": "w",
            "actions": {"rest": {"cost": 0, "params": []}},
            "initial_state": {
                "resources": {"start": {"food": 1}},
                "agents": {"a1": {"energy": 3, "location": "start"}},
            },
        }
        report = validate_world_report(world)
        self.assertTrue(report.ok)
        self.assertEqual(report.errors, 0)

    def test_validation_report_error(self):
        world = {
            "name": "w",
            "actions": {"rest": {"cost": 0, "params": []}},
            "initial_state": {
                "resources": {"start": {"food": -1}},
                "agents": {"a1": {"energy": -3, "location": "unknown"}},
            },
        }
        report = validate_world_report(world)
        self.assertFalse(report.ok)
        self.assertGreaterEqual(report.errors, 1)


if __name__ == "__main__":
    unittest.main()
