import unittest

from agentworld.protocol import upgrade_render_context_payload, validate_render_context


class ProtocolTests(unittest.TestCase):
    def test_render_context_validate_and_upgrade(self):
        v01 = {
            "version": "render-context.v0.1",
            "world_state_summary": {"world": "w", "tick": 1, "visible_location": "x", "resource_nodes": 1},
            "camera_view": {"profile": "topdown", "focus_agent": "a1", "radius": 1, "location": "x"},
            "entities_visible": [{"id": "a1", "kind": "agent", "location": "x", "energy": 3, "inventory": {}}],
            "local_resources": {"food": 2},
            "recent_events": [],
            "style_profile": "sim-minimal-v1",
            "continuity_tokens": {"scene_token": "aa11bb22", "agent_anchor": "cc33dd44", "style_anchor": "ee55ff66"},
        }
        validate_render_context(v01)
        v02 = upgrade_render_context_payload(v01)
        self.assertEqual(v02["version"], "render-context.v0.2")


if __name__ == "__main__":
    unittest.main()
