from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class ValidationIssue:
    level: str
    message: str


@dataclass
class ValidationReport:
    ok: bool
    errors: int
    warnings: int
    issues: List[ValidationIssue]


def validate_world_dict(data: Dict[str, Any]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []

    if "name" not in data:
        issues.append(ValidationIssue(level="error", message="missing world name"))
    if "actions" not in data or not data.get("actions"):
        issues.append(ValidationIssue(level="error", message="no actions configured"))
    if "initial_state" not in data:
        issues.append(ValidationIssue(level="error", message="missing initial_state"))
        return issues

    st = data["initial_state"]
    agents = st.get("agents", {})
    if not agents:
        issues.append(ValidationIssue(level="warning", message="world has zero agents"))

    resources = st.get("resources", {})
    if not resources:
        issues.append(ValidationIssue(level="warning", message="world has zero resource nodes"))

    for location, pool in resources.items():
        for resource, amount in pool.items():
            if amount < 0:
                issues.append(
                    ValidationIssue(level="error", message=f"negative resource {resource} at {location}")
                )

    for aid, agent in agents.items():
        if agent.get("energy", 0) < 0:
            issues.append(ValidationIssue(level="error", message=f"agent {aid} has negative energy"))
        loc = agent.get("location")
        if loc and loc not in resources:
            issues.append(
                ValidationIssue(level="warning", message=f"agent {aid} starts in unknown location '{loc}'")
            )

    return issues


def validate_world_report(data: Dict[str, Any]) -> ValidationReport:
    issues = validate_world_dict(data)
    errors = sum(1 for i in issues if i.level == "error")
    warnings = sum(1 for i in issues if i.level == "warning")
    return ValidationReport(ok=errors == 0, errors=errors, warnings=warnings, issues=issues)
