from __future__ import annotations

from typing import Any, Dict, Protocol


class RulePack(Protocol):
    name: str
    version: str

    def config_schema(self) -> Dict[str, Any]: ...

    def build(self, config: Dict[str, Any]) -> Any: ...


class ActionPack(Protocol):
    name: str
    version: str

    def action_specs(self) -> Dict[str, Dict[str, Any]]: ...

    def register_handlers(self, runtime: Any) -> None: ...


class RenderPack(Protocol):
    name: str
    version: str

    def config_schema(self) -> Dict[str, Any]: ...

    def render(self, render_context: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]: ...
