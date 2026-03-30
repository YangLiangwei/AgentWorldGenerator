from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class RuleConfigIssue:
    level: str
    message: str


def validate_rule_pack_config(rules: Dict[str, Any]) -> List[RuleConfigIssue]:
    issues: List[RuleConfigIssue] = []
    if not isinstance(rules, dict):
        return [RuleConfigIssue(level="error", message="rules must be an object")]

    queue_cfg = rules.get("queue", {})
    if queue_cfg is not None:
        if not isinstance(queue_cfg, dict):
            issues.append(RuleConfigIssue(level="error", message="rules.queue must be an object"))
        else:
            queues = queue_cfg.get("queues", {})
            if not isinstance(queues, dict):
                issues.append(RuleConfigIssue(level="error", message="rules.queue.queues must be an object"))

    access_cfg = rules.get("access", {})
    if access_cfg is not None:
        if not isinstance(access_cfg, dict):
            issues.append(RuleConfigIssue(level="error", message="rules.access must be an object"))
        else:
            policies = access_cfg.get("policies", {})
            if not isinstance(policies, dict):
                issues.append(RuleConfigIssue(level="error", message="rules.access.policies must be an object"))

    transfer_cfg = rules.get("transfer", True)
    if not isinstance(transfer_cfg, (bool, dict)):
        issues.append(RuleConfigIssue(level="error", message="rules.transfer must be bool or object"))

    unknown = set(rules.keys()) - {"queue", "access", "transfer"}
    for key in sorted(unknown):
        issues.append(RuleConfigIssue(level="warning", message=f"unknown rule pack '{key}' ignored"))

    return issues
