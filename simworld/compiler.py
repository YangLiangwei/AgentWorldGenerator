from __future__ import annotations

from typing import Any, Dict

from .spec import WorldSpec


def compile_scene(scene: Dict[str, Any]) -> WorldSpec:
    """Compile a structured scene dict into WorldSpec.

    TODO:
      - add schema validation and defaults merge
      - add NL->SceneIR->WorldSpec pipeline
      - add static checks (resource conservation/action reachability)
    """
    return WorldSpec.from_dict(scene)
