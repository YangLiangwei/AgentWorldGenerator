import unittest

from agentworld.agents import AgentProfile, RuleAgent, build_profiles_from_world


class ProfileTests(unittest.TestCase):
    def test_build_profiles_from_world(self):
        world = {
            "initial_state": {
                "agents": {
                    "a1": {"traits": {"role": "doctor", "profile": {"persona": "careful"}}},
                    "a2": {"traits": {"role": "student"}},
                }
            }
        }
        profiles = build_profiles_from_world(world)
        self.assertEqual(profiles["a1"].role, "doctor")
        self.assertEqual(profiles["a1"].persona, "careful")
        self.assertEqual(profiles["a2"].role, "student")

    def test_rule_agent_respects_allowed_actions(self):
        profile = AgentProfile(
            id="a1",
            role="student",
            persona="curious",
            strategy="balanced",
            visual_anchor="student-casual",
            allowed_actions=["rest"],
        )
        agent = RuleAgent("a1", profile=profile)
        agent.observe(
            {
                "location": "start",
                "resources": {"start": {"food": 5}},
            }
        )
        d = agent.decide()
        self.assertEqual(d.action, "rest")


if __name__ == "__main__":
    unittest.main()
