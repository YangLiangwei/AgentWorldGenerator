import unittest

from simworld.compiler import compile_scene, draft_scene_ir_from_text


class CompilerTests(unittest.TestCase):
    def test_compile_v02_world_dsl(self):
        scene = {
            "version": "0.2",
            "world": {"name": "x", "max_ticks": 10},
            "entities": [{"id": "a1", "type": "agent", "location": "start"}],
            "resource_nodes": [{"location": "start", "resources": {"food": 2}}],
        }
        spec = compile_scene(scene)
        self.assertEqual(spec.name, "x")
        self.assertIn("a1", spec.initial_state.agents)

    def test_draft_scene_ir_from_text(self):
        ir = draft_scene_ir_from_text("service world with manager")
        spec = compile_scene(ir)
        self.assertGreaterEqual(len(spec.initial_state.agents), 2)


if __name__ == "__main__":
    unittest.main()
