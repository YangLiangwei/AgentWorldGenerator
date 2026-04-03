from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agentworld.compiler import compile_scene
from agentworld.core import SimulationRuntime, validate_proposals
from agentworld.packs.dota_duel_lite import DotaDuelActionPack, propose_dota_actions
from agentworld.rendering import build_image_prompt_from_context, build_render_context


STATE: Dict[str, Any] = {
    "runtime": None,
    "world": None,
}


def _json(handler: BaseHTTPRequestHandler, code: int, payload: Dict[str, Any]) -> None:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            return _json(self, 200, {"ok": True})
        if parsed.path == "/state":
            rt = STATE.get("runtime")
            if rt is None:
                return _json(self, 400, {"error": "world not initialized"})
            return _json(
                self,
                200,
                {
                    "tick": rt.state.tick,
                    "agents": {
                        aid: {
                            "location": a.location,
                            "energy": a.energy,
                            "traits": a.traits,
                            "inventory": a.inventory,
                        }
                        for aid, a in rt.state.agents.items()
                    },
                },
            )

        if parsed.path == "/render_text":
            rt = STATE.get("runtime")
            if rt is None:
                return _json(self, 400, {"error": "world not initialized"})
            q = parse_qs(parsed.query)
            agent = (q.get("agent") or [""])[0]
            if not agent:
                agent = sorted(rt.state.agents.keys())[0]
            if agent not in rt.state.agents:
                return _json(self, 400, {"error": "invalid agent"})
            obs = rt.observe(agent)
            ctx = build_render_context(obs, agent_id=agent, world_name="dota-duel-lite")
            prompt = build_image_prompt_from_context(ctx)
            return _json(self, 200, {"agent": agent, "render_context": ctx, "prompt": prompt})

        return _json(self, 404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b"{}"
        payload = json.loads(body.decode("utf-8"))

        if self.path == "/init":
            world_path = payload.get("world_path")
            if not world_path:
                return _json(self, 400, {"error": "world_path required"})
            data = json.loads(Path(world_path).read_text())
            spec = compile_scene(data)
            rt = SimulationRuntime(spec)
            DotaDuelActionPack().register_handlers(rt)
            STATE["runtime"] = rt
            STATE["world"] = world_path
            return _json(self, 200, {"ok": True, "world": world_path, "tick": 0})

        rt = STATE.get("runtime")
        if rt is None:
            return _json(self, 400, {"error": "world not initialized"})

        if self.path == "/propose":
            actor = payload.get("actor")
            target = payload.get("target")
            if actor not in rt.state.agents or target not in rt.state.agents:
                return _json(self, 400, {"error": "invalid actor/target"})
            props = propose_dota_actions(rt, actor, target)
            valid = validate_proposals(rt, actor, props)
            return _json(self, 200, {"proposals": [p.__dict__ for p in valid]})

        if self.path == "/act":
            actor = payload.get("actor")
            action = payload.get("action")
            params = payload.get("params", {})
            try:
                out = rt.step_action(actor, action, params)
            except Exception as e:
                return _json(self, 400, {"error": str(e)})
            return _json(self, 200, {"outcome": out.result, "delta": out.state_delta, "tick": rt.state.tick})

        return _json(self, 404, {"error": "not found"})


def run(port: int = 8787):
    srv = HTTPServer(("0.0.0.0", port), Handler)
    print(f"game server listening on :{port}")
    srv.serve_forever()


if __name__ == "__main__":
    run()
