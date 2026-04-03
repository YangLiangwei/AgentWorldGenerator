from __future__ import annotations

from typing import Any, Dict


class DotaDuelRulePack:
    name = "dota_duel_lite_rules"
    version = "0.1"

    def config_schema(self) -> Dict[str, Any]:
        return {
            "required": ["win_hp_threshold"],
            "properties": {
                "win_hp_threshold": {"type": "integer"},
            },
        }

    def build(self, config: Dict[str, Any]) -> "DotaDuelRulePack":
        self.win_hp_threshold = int(config.get("win_hp_threshold", 0))
        return self

    def validate(self, runtime: Any, actor_id: str, action: str, params: Dict[str, Any]) -> None:
        return None

    def after_action(self, runtime: Any, actor_id: str, action: str, params: Dict[str, Any], result: str) -> None:
        alive = [aid for aid, a in runtime.state.agents.items() if int(a.traits.get("hp", 0)) > self.win_hp_threshold]
        if len(alive) == 1:
            runtime.bus.publish("duel_end", {"winner": alive[0], "tick": runtime.state.tick})
