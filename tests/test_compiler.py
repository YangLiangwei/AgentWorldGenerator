import unittest

from agentworld.compiler import compile_scene, draft_scene_ir_from_text, intent_to_ir, text_to_intent


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

    def test_draft_scene_ir_from_text_service(self):
        ir = draft_scene_ir_from_text("service world with manager")
        spec = compile_scene(ir)
        self.assertGreaterEqual(len(spec.initial_state.agents), 2)

    def test_draft_scene_ir_from_text_university(self):
        ir = draft_scene_ir_from_text("a university world with labs and students")
        self.assertEqual(ir["world"]["name"], "university-world")
        first_traits = ir["entities"][0].get("traits", {})
        self.assertIn("profile", first_traits)
        spec = compile_scene(ir)
        self.assertGreaterEqual(len(spec.initial_state.agents), 4)

    def test_text_intent_pipeline(self):
        intent = text_to_intent("hospital simulation")
        self.assertEqual(intent["domain"], "hospital")
        ir = intent_to_ir(intent)
        self.assertEqual(ir["world"]["name"], "hospital-world")


if __name__ == "__main__":
    unittest.main()
