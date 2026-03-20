import unittest

from agentworld.rendering import (
    build_image_prompt,
    build_image_prompt_from_context,
    build_render_context,
    build_render_spec,
)


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

    def test_render_context_is_stable_for_same_input(self):
        obs = {
            "tick": 8,
            "location": "lab_alpha",
            "energy": 6,
            "inventory": {"sample": 2, "food": 1},
            "resources": {
                "lab_alpha": {"sample": 4, "food": 10},
                "hall": {"food": 9},
            },
        }
        c1 = build_render_context(obs, agent_id="agent_student_1", radius=2, world_name="university-world")
        c2 = build_render_context(obs, agent_id="agent_student_1", radius=2, world_name="university-world")
        self.assertEqual(c1, c2)
        self.assertEqual(c1["version"], "render-context.v0.1")

    def test_prompt_from_context(self):
        obs = {
            "tick": 5,
            "location": "triage",
            "energy": 8,
            "inventory": {"ticket": 1},
            "resources": {"triage": {"food": 3}},
        }
        ctx = build_render_context(obs, agent_id="agent_doctor_1", camera_profile="first_person", world_name="hospital-world")
        prompt = build_image_prompt_from_context(ctx)
        self.assertIn("hospital-world", prompt)
        self.assertIn("first_person", prompt)
        self.assertIn("agent_doctor_1", prompt)


if __name__ == "__main__":
    unittest.main()
