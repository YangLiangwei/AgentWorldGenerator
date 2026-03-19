import unittest

from agentworld.rendering import build_image_prompt, build_render_spec


class RenderingTests(unittest.TestCase):
    def test_render_spec_and_prompt(self):
        obs = {
            "tick": 3,
            "location": "hall",
            "energy": 7,
            "inventory": {"food": 1},
            "resources": {"hall": {"food": 9}},
        }
        spec = build_render_spec(obs, agent_id="a1", radius=2)
        self.assertEqual(spec["scene"]["location"], "hall")
        prompt = build_image_prompt(spec)
        self.assertIn("agent a1", prompt)
        self.assertIn("Tick 3", prompt)


if __name__ == "__main__":
    unittest.main()
