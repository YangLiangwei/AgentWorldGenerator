from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import json

from ..agents import RuleAgent, build_profiles_from_world
from ..compiler import compile_scene
from ..core import SimulationRuntime, ValidationError


@dataclass
class RunTask:
    task_id: str
    world_path: str
    ticks: int = 20
    retries: int = 1
    artifact_dir: str = ""


@dataclass
class OrchestratorConfig:
    max_concurrency: int = 1
    max_retries: int = 2
    max_ticks_per_task: int = 1000


@dataclass
class OrchestratorResult:
    task_id: str
    status: str
    attempts: int
    error: str = ""
    final_tick: int = 0
    events: int = 0


class Orchestrator:
    def __init__(self, config: Optional[OrchestratorConfig] = None) -> None:
        self.config = config or OrchestratorConfig()
        self._queue: List[RunTask] = []

    def submit(self, task: RunTask) -> None:
        self._queue.append(task)

    def _run_once(self, task: RunTask) -> OrchestratorResult:
        data = json.loads(Path(task.world_path).read_text())
        spec = compile_scene(data)
        runtime = SimulationRuntime(spec)
        profiles = build_profiles_from_world(data)
        agents = {aid: RuleAgent(aid, profile=profiles.get(aid)) for aid in runtime.state.agents.keys()}

        ticks = min(task.ticks, spec.max_ticks, self.config.max_ticks_per_task)
        for _ in range(ticks):
            decisions = {}
            for aid, agent in agents.items():
                agent.observe(runtime.observe(aid))
                d = agent.decide()
                decisions[aid] = {"action": d.action, "params": d.params}
            runtime.run_tick(decisions)

        if task.artifact_dir:
            out = Path(task.artifact_dir)
            out.mkdir(parents=True, exist_ok=True)
            (out / f"{task.task_id}.run.jsonl").write_text(runtime.log.to_jsonl())

        return OrchestratorResult(
            task_id=task.task_id,
            status="ok",
            attempts=1,
            final_tick=runtime.state.tick,
            events=len(runtime.log.all()),
        )

    def run_all(self) -> List[OrchestratorResult]:
        results: List[OrchestratorResult] = []
        while self._queue:
            task = self._queue.pop(0)
            max_attempts = min(task.retries + 1, self.config.max_retries + 1)
            attempt = 0
            last_error = ""
            while attempt < max_attempts:
                attempt += 1
                try:
                    r = self._run_once(task)
                    r.attempts = attempt
                    results.append(r)
                    break
                except (ValidationError, ValueError, KeyError) as e:
                    last_error = str(e)
                    if attempt >= max_attempts:
                        results.append(
                            OrchestratorResult(
                                task_id=task.task_id,
                                status="failed",
                                attempts=attempt,
                                error=last_error,
                            )
                        )
        return results
