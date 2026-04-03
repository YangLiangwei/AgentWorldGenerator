from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .heroes import HERO_SPECS


def _cooldown_ready(actor: Any, skill_id: str, tick: int) -> bool:
    cds = actor.traits.setdefault("skill_cooldowns", {})
    return int(cds.get(skill_id, -1)) <= tick


def _set_cooldown(actor: Any, skill_id: str, tick: int, cd: int) -> None:
    actor.traits.setdefault("skill_cooldowns", {})[skill_id] = tick + cd


def _append_effect(target: Any, effect: Dict[str, Any], tick: int) -> None:
    mods = target.traits.setdefault("modifiers", [])
    mods.append({"type": effect["type"], "until": tick + int(effect.get("duration", 0)), "value": effect.get("value")})


def cast_skill(runtime: Any, actor_id: str, skill_id: str, target_id: str) -> Tuple[str, Dict[str, Any]]:
    actor = runtime.state.agents[actor_id]
    target = runtime.state.agents.get(target_id)
    if target is None or int(target.traits.get("hp", 0)) <= 0:
        return "fail:dead_target", {}

    hero_id = actor.traits.get("hero_id")
    if hero_id not in HERO_SPECS:
        return "fail:unknown_hero", {}

    spec = HERO_SPECS[hero_id]["skills"].get(skill_id)
    if spec is None:
        return "fail:unknown_skill", {}

    now = runtime.state.tick
    if not _cooldown_ready(actor, skill_id, now):
        return "fail:cooldown", {}

    mana = int(actor.traits.get("mana", 0))
    mana_cost = int(spec.get("mana_cost", 0))
    if mana < mana_cost:
        return "fail:no_mana", {}

    actor.traits["mana"] = mana - mana_cost
    _set_cooldown(actor, skill_id, now, int(spec.get("cooldown", 0)))

    dmg = int(spec.get("damage", 0) * float(actor.traits.get("spell_power", 1.0)))
    target.traits["hp"] = max(0, int(target.traits.get("hp", 0)) - dmg)

    for eff in spec.get("effects", []):
        _append_effect(target, eff, now)

    return "ok:cast", {"skill": skill_id, "damage": dmg, "target": target_id, "target_hp": target.traits["hp"]}


def build_skill_handlers(runtime: Any) -> Dict[str, Any]:
    return {
        "cast_q": lambda actor, params: cast_skill(runtime, actor.id, actor.traits.get("skill_q", ""), str(params["target_id"])),
        "cast_w": lambda actor, params: cast_skill(runtime, actor.id, actor.traits.get("skill_w", ""), str(params["target_id"])),
        "cast_e": lambda actor, params: cast_skill(runtime, actor.id, actor.traits.get("skill_e", ""), str(params["target_id"])),
        "cast_r": lambda actor, params: cast_skill(runtime, actor.id, actor.traits.get("skill_r", ""), str(params["target_id"])),
    }
