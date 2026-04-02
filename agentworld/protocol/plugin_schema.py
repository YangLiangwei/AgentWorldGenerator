from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class PluginSchemaIssue:
    level: str
    message: str


def validate_pack_config(schema: Dict[str, Any], config: Dict[str, Any]) -> List[PluginSchemaIssue]:
    issues: List[PluginSchemaIssue] = []
    required = list(schema.get("required", []))
    props = dict(schema.get("properties", {}))

    for key in required:
        if key not in config:
            issues.append(PluginSchemaIssue(level="error", message=f"missing required field: {key}"))

    for key, rule in props.items():
        if key not in config:
            continue
        typ = rule.get("type")
        if typ == "object" and not isinstance(config[key], dict):
            issues.append(PluginSchemaIssue(level="error", message=f"{key} must be object"))
        if typ == "array" and not isinstance(config[key], list):
            issues.append(PluginSchemaIssue(level="error", message=f"{key} must be array"))
        if typ == "boolean" and not isinstance(config[key], bool):
            issues.append(PluginSchemaIssue(level="error", message=f"{key} must be boolean"))

    return issues
