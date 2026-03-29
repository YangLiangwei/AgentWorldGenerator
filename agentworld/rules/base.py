from __future__ import annotations

from typing import Any, Dict, Protocol


class RuleMiddleware(Protocol):
    name: str

    def validate(self, runtime: Any, actor_id: str, action: str, params: Dict[str, Any]) -> None: ...

    def after_action(self, runtime: Any, actor_id: str, action: str, params: Dict[str, Any], result: str) -> None: ...
