from __future__ import annotations

from typing import Any, Dict

from ...protocol.errors import OK_NOOP


class DotaDuelActionPack:
    name = "dota_duel_lite_actions"
    version = "0.1"

    def action_specs(self) -> Dict[str, Dict[str, Any]]:
        return {
            "attack": {
                "cost": 1,
                "params": ["target_id"],
                "success_code": "ok:attack",
                "failure_codes": ["fail:out_of_range", "fail:dead_target"],
            },
            "cast_q": {
                "cost": 2,
                "params": ["target_id"],
                "success_code": "ok:cast_q",
                "failure_codes": ["fail:cooldown", "fail:no_mana"],
            },
        }

    def register_handlers(self, runtime: Any) -> None:
        runtime.register_action_handler("attack", self._attack(runtime))
        runtime.register_action_handler("cast_q", self._cast_q(runtime))

    def _attack(self, runtime: Any):
        def _handler(actor, params):
            target_id = str(params["target_id"])
            target = runtime.state.agents.get(target_id)
            if target is None:
                return "fail:dead_target", {}
            if target.traits.get("hp", 0) <= 0:
                return "fail:dead_target", {}
            dmg = int(actor.traits.get("atk", 10))
            target.traits["hp"] = max(0, int(target.traits.get("hp", 100)) - dmg)
            return "ok:attack", {"damage": dmg, "target": target_id, "target_hp": target.traits["hp"]}

        return _handler

    def _cast_q(self, runtime: Any):
        def _handler(actor, params):
            mana = int(actor.traits.get("mana", 0))
            if mana < 20:
                return "fail:no_mana", {}
            target_id = str(params["target_id"])
            target = runtime.state.agents.get(target_id)
            if target is None or target.traits.get("hp", 0) <= 0:
                return "fail:dead_target", {}
            actor.traits["mana"] = mana - 20
            dmg = int(actor.traits.get("spell_q", 25))
            target.traits["hp"] = max(0, int(target.traits.get("hp", 100)) - dmg)
            return "ok:cast_q", {"damage": dmg, "target": target_id, "target_hp": target.traits["hp"]}

        return _handler
