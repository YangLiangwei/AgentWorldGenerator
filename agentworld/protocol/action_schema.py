from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ActionSchemaIssue:
    level: str
    message: str


def validate_action_schema(actions: Dict[str, Any]) -> List[ActionSchemaIssue]:
    issues: List[ActionSchemaIssue] = []
    if not isinstance(actions, dict) or not actions:
        return [ActionSchemaIssue(level="error", message="actions must be a non-empty object")]

    for name, spec in actions.items():
        if not isinstance(spec, dict):
            issues.append(ActionSchemaIssue(level="error", message=f"action {name} must be an object"))
            continue
        if "params" in spec and not isinstance(spec.get("params"), list):
            issues.append(ActionSchemaIssue(level="error", message=f"action {name}.params must be a list"))
        if "cost" in spec and int(spec.get("cost", 0)) < 0:
            issues.append(ActionSchemaIssue(level="error", message=f"action {name}.cost must be >= 0"))
    return issues
