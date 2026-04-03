import unittest

from agentworld.core import SimulationRuntime
from agentworld.packs.dota_duel_lite import DotaDuelActionPack, HERO_SPECS
from agentworld.schema import WorldSpec


class DotaHeroesTests(unittest.TestCase):
    def _world(self):
        cm = HERO_SPECS["crystal_maiden"]
        lina = HERO_SPECS["lina"]
        return {
            "name": "cm-vs-lina",
            "max_ticks": 20,
            "actions": {
                "attack": {"cost": 1, "params": ["target_id"]},
                "cast_q": {"cost": 2, "params": ["target_id"]},
                "cast_w": {"cost": 2, "params": ["target_id"]},
                "cast_e": {"cost": 1, "params": ["target_id"]},
                "cast_r": {"cost": 3, "params": ["target_id"]},
            },
            "initial_state": {
                "tick": 0,
                "resources": {"lane": {"food": 0}},
                "agents": {
                    "cm": {
                        "energy": 30,
                        "location": "lane",
                        "traits": {
                            "hero_id": "crystal_maiden",
                            "hp": cm["hp"],
                            "mana": cm["mana"],
                            "atk": cm["atk"],
                            "spell_power": cm["spell_power"],
                            "skill_q": "q_crystal_nova",
                            "skill_w": "w_frostbite",
                            "skill_e": "e_arcane_aura",
                            "skill_r": "r_freezing_field",
                        },
                    },
                    "lina": {
                        "energy": 30,
                        "location": "lane",
                        "traits": {
                            "hero_id": "lina",
                            "hp": lina["hp"],
                            "mana": lina["mana"],
                            "atk": lina["atk"],
                            "spell_power": lina["spell_power"],
                            "skill_q": "q_dragon_slave",
                            "skill_w": "w_light_strike_array",
                            "skill_e": "e_fiery_soul",
                            "skill_r": "r_laguna_blade",
                        },
                    },
                },
            },
        }

    def test_cm_and_lina_skill_cast(self):
        rt = SimulationRuntime(WorldSpec.from_dict(self._world()))
        DotaDuelActionPack().register_handlers(rt)

        out1 = rt.step_action("cm", "cast_q", {"target_id": "lina"})
        self.assertEqual(out1.result, "ok:cast")
        self.assertLess(rt.state.agents["lina"].traits["hp"], HERO_SPECS["lina"]["hp"])

        out2 = rt.step_action("lina", "cast_r", {"target_id": "cm"})
        self.assertEqual(out2.result, "ok:cast")
        self.assertLess(rt.state.agents["cm"].traits["hp"], HERO_SPECS["crystal_maiden"]["hp"])

    def test_cooldown_works(self):
        rt = SimulationRuntime(WorldSpec.from_dict(self._world()))
        DotaDuelActionPack().register_handlers(rt)

        out1 = rt.step_action("lina", "cast_w", {"target_id": "cm"})
        out2 = rt.step_action("lina", "cast_w", {"target_id": "cm"})
        self.assertEqual(out1.result, "ok:cast")
        self.assertEqual(out2.result, "fail:cooldown")


if __name__ == "__main__":
    unittest.main()
