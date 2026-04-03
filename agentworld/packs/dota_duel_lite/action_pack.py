from __future__ import annotations

from typing import Any, Dict

from .skill_runtime import build_skill_handlers


class DotaDuelActionPack:
    name = "dota_duel_lite_actions"
    version = "0.2"

    def action_specs(self) -> Dict[str, Dict[str, Any]]:
        return {
            "attack": {
                "cost": 1,
                "params": ["target_id"],
                "success_code": "ok:attack",
                "failure_codes": ["fail:out_of_range", "fail:dead_target"],
            },
            "cast_q": {"cost": 2, "params": ["target_id"], "success_code": "ok:cast", "failure_codes": ["fail:cooldown", "fail:no_mana"]},
            "cast_w": {"cost": 2, "params": ["target_id"], "success_code": "ok:cast", "failure_codes": ["fail:cooldown", "fail:no_mana"]},
            "cast_e": {"cost": 1, "params": ["target_id"], "success_code": "ok:cast", "failure_codes": ["fail:cooldown", "fail:no_mana"]},
            "cast_r": {"cost": 3, "params": ["target_id"], "success_code": "ok:cast", "failure_codes": ["fail:cooldown", "fail:no_mana"]},
        }

    def register_handlers(self, runtime: Any) -> None:
        runtime.register_action_handler("attack", self._attack(runtime))
        for action, handler in build_skill_handlers(runtime).items():
            runtime.register_action_handler(action, handler)

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
