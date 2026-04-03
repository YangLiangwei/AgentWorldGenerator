import unittest

from agentworld.core import SimulationRuntime
from agentworld.packs.dota_duel_lite import DotaDuelActionPack, DotaDuelRulePack
from agentworld.schema import WorldSpec


class DotaDuelPackTests(unittest.TestCase):
    def _world(self):
        return {
            "name": "dota-duel-lite",
            "max_ticks": 20,
            "actions": {
                "attack": {"cost": 1, "params": ["target_id"]},
                "cast_q": {"cost": 2, "params": ["target_id"]},
            },
            "initial_state": {
                "tick": 0,
                "resources": {"lane": {"food": 0}},
                "agents": {
                    "hero_a": {
                        "energy": 20,
                        "location": "lane",
                        "traits": {"role": "hero", "hp": 100, "mana": 100, "atk": 12, "spell_q": 30},
                    },
                    "hero_b": {
                        "energy": 20,
                        "location": "lane",
                        "traits": {"role": "hero", "hp": 90, "mana": 100, "atk": 10, "spell_q": 20},
                    },
                },
            },
        }

    def test_pack_action_handlers(self):
        spec = WorldSpec.from_dict(self._world())
        rt = SimulationRuntime(spec)
        pack = DotaDuelActionPack()
        pack.register_handlers(rt)

        out = rt.step_action("hero_a", "attack", {"target_id": "hero_b"})
        self.assertEqual(out.result, "ok:attack")
        self.assertLess(rt.state.agents["hero_b"].traits["hp"], 90)

    def test_pack_rule_winner_event(self):
        spec = WorldSpec.from_dict(self._world())
        rt = SimulationRuntime(spec)
        pack = DotaDuelActionPack()
        pack.register_handlers(rt)
        winner_events = []
        rt.bus.subscribe("duel_end", lambda payload: winner_events.append(payload))

        rule = DotaDuelRulePack().build({"win_hp_threshold": 0})
        rt.register_rule(rule)

        # burst kill
        for _ in range(4):
            rt.step_action("hero_a", "cast_q", {"target_id": "hero_b"})
        self.assertTrue(len(winner_events) >= 1)


if __name__ == "__main__":
    unittest.main()
