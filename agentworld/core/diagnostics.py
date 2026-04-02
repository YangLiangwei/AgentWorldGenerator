from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List


@dataclass
class TickDiagnostic:
    tick: int
    total_actions: int
    success_actions: int
    failure_actions: int
    dead_tick: bool
    error_codes: Dict[str, int]


class DiagnosticsCollector:
    def __init__(self) -> None:
        self.rows: List[TickDiagnostic] = []

    def record(self, tick: int, results: List[str]) -> TickDiagnostic:
        success = sum(1 for r in results if r.startswith("ok:"))
        failure = sum(1 for r in results if r.startswith("fail:"))
        errors: Dict[str, int] = {}
        for r in results:
            if r.startswith("fail:"):
                errors[r] = errors.get(r, 0) + 1
        row = TickDiagnostic(
            tick=tick,
            total_actions=len(results),
            success_actions=success,
            failure_actions=failure,
            dead_tick=(success == 0),
            error_codes=errors,
        )
        self.rows.append(row)
        return row

    def as_json_rows(self) -> List[Dict]:
        return [asdict(r) for r in self.rows]
