"""Run scenarios one by one, saving progress after each. Stops cleanly on LLM failure."""

import logging
from pathlib import Path

from app.evaluation.checks import score
from app.evaluation.environment import EVAL_TODAY, EvalEnvironment
from app.evaluation.progress import save_atomic
from app.evaluation.results import RunFile, ScenarioResult
from app.evaluation.scenario_run import run_scenario
from app.evaluation.scenarios import Scenario

logger = logging.getLogger(__name__)


class RunInterruptedError(Exception):
    """The LLM failed after its retries (often the daily quota). Progress is saved."""


async def run_pending(
    env: EvalEnvironment, scenarios: list[Scenario], run: RunFile, progress: Path | None
) -> RunFile:
    done = {r.id for r in run.results}
    for scenario in scenarios:
        if scenario.id in done:
            continue
        repos = await env.fresh_repos()
        trace = await run_scenario(
            scenario, repos, env.llm, env.policies, env.retriever, lambda: EVAL_TODAY
        )
        if env.llm.errors:
            # A scenario hit by an outage says nothing about the agent; rerun it later.
            raise RunInterruptedError(
                f"LLM failed during {scenario.id} ({', '.join(env.llm.errors)}). "
                f"{len(run.results)}/{len(scenarios)} scenarios saved."
            )
        result = ScenarioResult.build(scenario, trace, score(scenario, trace))
        run.results.append(result)
        if progress is not None:
            save_atomic(progress, run)
        status = "PASS" if result.passed else "FAIL"
        print(f"[{len(run.results)}/{len(scenarios)}] {status} {scenario.id}", flush=True)
        for failure in result.failures:
            print(f"      - {failure}", flush=True)
    return run
