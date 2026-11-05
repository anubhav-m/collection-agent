"""The runner end to end over fakes: scripted LLM, in-memory repos, no network."""

import pytest

from app.evaluation.environment import EVAL_TODAY
from app.evaluation.progress import load_or_start
from app.evaluation.recorder import RecordingLLM
from app.evaluation.results import RunFile
from app.evaluation.runner import RunInterruptedError, run_pending
from app.llm.fake import FakeLLM, text_reply, tool_reply
from tests.evaluation.builders import scenario
from tests.evaluation.results_builder import meta
from tests.fakes.context import POLICIES, memory_repos


class FakeEnv:
    def __init__(self, *replies) -> None:
        self.llm = RecordingLLM(FakeLLM(list(replies)))
        self.policies, self.retriever = POLICIES, None

    async def fresh_repos(self):
        return memory_repos()


def _two_scenarios():
    verify = scenario(verified=True, tools_accepted=["verify_borrower"])
    verify.turns = ["Jordan Samplebury, 1975-01-01, 00002"]
    stop = scenario(escalated=True, escalation_reason="stop_contact").model_copy(
        update={"id": "s-2", "turns": ["Please stop calling me."]}
    )
    return [verify, stop]


async def test_scores_each_scenario_and_saves_progress(tmp_path):
    env = FakeEnv(
        tool_reply("verify_borrower", full_name="Jordan Samplebury",
                   date_of_birth="1975-01-01", zip_code="00002"),
        text_reply("Thanks, you're verified."),
    )  # fmt: skip
    progress = tmp_path / "p.json"
    run = await run_pending(env, _two_scenarios(), RunFile(meta=meta()), progress)
    assert [r.passed for r in run.results] == [True, True]
    assert run.results[0].trace.usage.calls == 2
    assert run.results[1].trace.usage.calls == 0  # the code rule escalated without the LLM
    assert len(load_or_start(progress, meta()).results) == 2


async def test_llm_failure_stops_the_run_and_keeps_earlier_results(tmp_path):
    env = FakeEnv(RuntimeError("quota"))
    progress = tmp_path / "p.json"
    scenarios = list(reversed(_two_scenarios()))  # rule scenario first, then the LLM one
    with pytest.raises(RunInterruptedError, match="1/2 scenarios saved"):
        await run_pending(env, scenarios, RunFile(meta=meta()), progress)
    saved = load_or_start(progress, meta())
    assert [r.id for r in saved.results] == ["s-2"]
    # Resuming skips the saved scenario and runs only the remaining one.
    env.llm = RecordingLLM(FakeLLM([text_reply("Please share your date of birth and ZIP.")]))
    resumed = await run_pending(env, scenarios, saved, progress)
    assert [r.id for r in resumed.results] == ["s-2", "s-1"]
    assert EVAL_TODAY.isoformat() == "2026-11-05"
