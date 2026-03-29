import unittest

from agentworld.rendering import (
    build_image_prompt,
    build_image_prompt_from_context,
    build_render_context,
    build_render_spec,
    upgrade_render_context,
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
        c1 = build_render_context(
            obs,
            agent_id="agent_student_1",
            radius=2,
            world_name="university-world",
            recent_events=[{"tick": 8, "actor_id": "agent_student_1", "action": "gather", "result": "ok:gather"}],
        )
        c2 = build_render_context(
            obs,
            agent_id="agent_student_1",
            radius=2,
            world_name="university-world",
            recent_events=[{"tick": 8, "actor_id": "agent_student_1", "action": "gather", "result": "ok:gather"}],
        )
        self.assertEqual(c1, c2)
        self.assertEqual(c1["version"], "render-context.v0.2")
        self.assertIn("history_token", c1["continuity_tokens"])

    def test_prompt_from_context(self):
        obs = {
            "tick": 5,
            "location": "triage",
            "energy": 8,
            "inventory": {"ticket": 1},
            "resources": {"triage": {"food": 3}},
        }
        ctx = build_render_context(
            obs,
            agent_id="agent_doctor_1",
            camera_profile="first_person",
            world_name="hospital-world",
            agent_profile={"role": "doctor", "persona": "careful", "strategy": "service-first", "visual_anchor": "white-coat"},
        )
        self.assertEqual(ctx["agent_profile"]["role"], "doctor")
        prompt = build_image_prompt_from_context(ctx)
        self.assertIn("hospital-world", prompt)
        self.assertIn("first_person", prompt)
        self.assertIn("agent_doctor_1", prompt)
        self.assertIn("white-coat", prompt)

    def test_upgrade_v01_context(self):
        v01 = {
            "version": "render-context.v0.1",
            "world_state_summary": {"world": "w", "tick": 1, "visible_location": "x", "resource_nodes": 1},
            "camera_view": {"profile": "topdown", "focus_agent": "a1", "radius": 1, "location": "x"},
            "entities_visible": [{"id": "a1", "kind": "agent", "location": "x", "energy": 5, "inventory": {}}],
            "local_resources": {"food": 1},
            "recent_events": [{"tick": 1, "actor": "a1", "action": "rest", "result": "ok:rest"}],
            "style_profile": "sim-minimal-v1",
            "continuity_tokens": {"scene_token": "abc12345", "agent_anchor": "def67890", "style_anchor": "ghi00000"},
        }
        up = upgrade_render_context(v01)
        self.assertEqual(up["version"], "render-context.v0.2")
        self.assertIn("identity_token", up["continuity_tokens"])
        self.assertIn("history_token", up["continuity_tokens"])


if __name__ == "__main__":
    unittest.main()
