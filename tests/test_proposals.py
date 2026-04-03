import unittest

from agentworld.core import SimulationRuntime, validate_proposals
from agentworld.packs.dota_duel_lite import DotaDuelActionPack, propose_dota_actions
from agentworld.schema import WorldSpec


class ProposalTests(unittest.TestCase):
    def _world(self):
        return {
            "name": "duel",
            "max_ticks": 5,
            "actions": {
                "attack": {"cost": 1, "params": ["target_id"]},
                "cast_q": {"cost": 2, "params": ["target_id"]},
                "cast_w": {"cost": 2, "params": ["target_id"]},
                "cast_r": {"cost": 3, "params": ["target_id"]},
            },
            "initial_state": {
                "tick": 0,
                "resources": {"lane": {"food": 0}},
                "agents": {
                    "cm": {"energy": 20, "location": "lane", "traits": {"hero_id": "crystal_maiden", "hp": 560, "mana": 420, "atk": 46, "skill_q": "q_crystal_nova", "skill_w": "w_frostbite", "skill_e": "e_arcane_aura", "skill_r": "r_freezing_field"}},
                    "lina": {"energy": 20, "location": "lane", "traits": {"hero_id": "lina", "hp": 580, "mana": 450, "atk": 49, "skill_q": "q_dragon_slave", "skill_w": "w_light_strike_array", "skill_e": "e_fiery_soul", "skill_r": "r_laguna_blade"}},
                },
            },
        }

    def test_proposal_generation_and_validation(self):
        rt = SimulationRuntime(WorldSpec.from_dict(self._world()))
        DotaDuelActionPack().register_handlers(rt)
        props = propose_dota_actions(rt, "cm", "lina")
        valid = validate_proposals(rt, "cm", props)
        self.assertGreaterEqual(len(valid), 1)
        self.assertLessEqual(len(valid), 3)


if __name__ == "__main__":
    unittest.main()
