from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def load_jsonl(path: str) -> List[Dict]:
    p = Path(path)
    if not p.exists():
        return []
    rows: List[Dict] = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def summarize_events(events: List[Dict]) -> Dict:
    total = len(events)
    success = sum(1 for e in events if str(e.get("result", "")).startswith("ok:"))
    failures = [e for e in events if str(e.get("result", "")).startswith("fail:")]
    error_codes: Dict[str, int] = {}
    for e in failures:
        code = str(e.get("result", "fail:unknown"))
        error_codes[code] = error_codes.get(code, 0) + 1

    ticks = {int(e.get("tick", 0)) for e in events}
    dead_tick_ratio = 0.0
    if ticks:
        alive_ticks = {int(e.get("tick", 0)) for e in events if str(e.get("result", "")).startswith("ok:")}
        dead_tick_ratio = (len(ticks - alive_ticks) / len(ticks))

    return {
        "total_actions": total,
        "success_actions": success,
        "failure_actions": len(failures),
        "dead_tick_ratio": dead_tick_ratio,
        "error_codes": error_codes,
    }
