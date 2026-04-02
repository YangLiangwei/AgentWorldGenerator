from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class PluginMeta:
    kind: str
    name: str
    version: str


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: Dict[str, Dict[str, Any]] = {"rule": {}, "action": {}, "render": {}}

    def register(self, kind: str, plugin: Any) -> None:
        if kind not in self._plugins:
            raise ValueError(f"unknown plugin kind: {kind}")
        name = getattr(plugin, "name", None)
        version = getattr(plugin, "version", None)
        if not name or not version:
            raise ValueError("plugin must define name and version")
        self._plugins[kind][name] = plugin

    def get(self, kind: str, name: str) -> Any:
        return self._plugins[kind][name]

    def list_meta(self) -> Dict[str, list[PluginMeta]]:
        out: Dict[str, list[PluginMeta]] = {}
        for kind, entries in self._plugins.items():
            out[kind] = [PluginMeta(kind=kind, name=n, version=getattr(p, "version", "unknown")) for n, p in entries.items()]
        return out
