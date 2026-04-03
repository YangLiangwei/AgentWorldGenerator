from __future__ import annotations

from typing import List

from ...core.proposals import ActionProposal


def propose_dota_actions(runtime, actor_id: str, target_id: str) -> List[ActionProposal]:
    actor = runtime.state.agents[actor_id]
    target = runtime.state.agents[target_id]
    hp_gap = int(actor.traits.get("hp", 0)) - int(target.traits.get("hp", 0))

    proposals: List[ActionProposal] = []
    proposals.append(
        ActionProposal(
            action="attack",
            params={"target_id": target_id},
            rationale="稳定输出压制对手",
            expected="造成普攻伤害并压低对手血线",
        )
    )

    if int(actor.traits.get("mana", 0)) >= 20:
        proposals.append(
            ActionProposal(
                action="cast_q",
                params={"target_id": target_id},
                rationale="使用Q技能打爆发并附带效果",
                expected="造成技能伤害并可能附加控制/减速",
            )
        )

    if hp_gap < 0:
        proposals.append(
            ActionProposal(
                action="cast_w",
                params={"target_id": target_id},
                rationale="尝试控制对手，争取反打窗口",
                expected="造成中等伤害并附加控制",
            )
        )
    else:
        proposals.append(
            ActionProposal(
                action="cast_r",
                params={"target_id": target_id},
                rationale="优势时尝试大招压制",
                expected="造成高额伤害",
            )
        )

    return proposals[:3]
