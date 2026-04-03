from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib import request


@dataclass
class LLMDecision:
    action: str
    params: Dict[str, Any]
    rationale: str = ""


class HttpLLMAgentAdapter:
    """Minimal HTTP adapter. Expects endpoint to return JSON:
    {"action": str, "params": {...}, "rationale": str}
    """

    def __init__(self, endpoint: str, timeout: float = 8.0, headers: Dict[str, str] | None = None) -> None:
        self.endpoint = endpoint
        self.timeout = timeout
        self.headers = headers or {}

    def decide(self, payload: Dict[str, Any], fallback_proposals: List[Dict[str, Any]]) -> LLMDecision:
        body = json.dumps({"state": payload, "proposals": fallback_proposals}, ensure_ascii=False).encode("utf-8")
        req_headers = {"Content-Type": "application/json", **self.headers}
        req = request.Request(self.endpoint, data=body, headers=req_headers, method="POST")
        with request.urlopen(req, timeout=self.timeout) as resp:
            out = json.loads(resp.read().decode("utf-8"))
        return LLMDecision(
            action=str(out.get("action", "")),
            params=dict(out.get("params", {})),
            rationale=str(out.get("rationale", "")),
        )
