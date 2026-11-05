import pytest

from app.core.errors import LLMUnavailableError
from app.extraction.bench_setup import pacing_gap
from app.extraction.benchmark import BenchmarkInterruptedError, run_extractor
from app.extraction.dataset import Split, load_set
from app.extraction.llm_extractor import LLMExtractor
from app.extraction.models import Label
from app.extraction.regex_extractor import RegexExtractor
from app.extraction.report import BenchmarkReport, summarise
from app.extraction.report_md import render_markdown
from app.llm.fake import FakeLLM, text_reply
from tests.extraction.builders import chat

NO = '{"promise_made": false, "amount": null, "date": null}'
ROWS = [(chat("B: hi", tid=f"t{i}"), Label(id=f"t{i}", promise_made=False)) for i in range(3)]


def test_dataset_split_is_disjoint_and_fully_labelled():
    dev, test = load_set(Split.DEV), load_set(Split.TEST)
    assert len(dev) + len(test) >= 40
    assert not {t.id for t, _ in dev} & {t.id for t, _ in test}
    assert all(t.id == lb.id for t, lb in dev + test)


async def test_llm_calls_are_spaced_by_the_gap():
    waits: list[float] = []

    async def sleep(s: float) -> None:
        waits.append(s)

    llm = LLMExtractor(FakeLLM([text_reply(NO)] * 3))
    pairs = await run_extractor(llm, ROWS, gap_seconds=6.5, sleep=sleep)
    assert len(pairs) == 3 and waits == [6.5, 6.5]
    assert pacing_gap(10) == 6.5


async def test_an_outage_stops_the_run_instead_of_scoring_it():
    llm = LLMExtractor(FakeLLM([text_reply(NO), LLMUnavailableError()]))
    with pytest.raises(BenchmarkInterruptedError, match="t1"):
        await run_extractor(llm, ROWS)


async def test_report_markdown_lists_scores_and_misses(tmp_path):
    from datetime import UTC, datetime

    from app.extraction.report import BenchmarkMeta

    rows = [(chat("B: I'll pay $5 today.", tid="x"), Label(id="x", promise_made=False))]
    result = summarise("regex", await run_extractor(RegexExtractor(), rows))
    meta = BenchmarkMeta(
        run_name="r", split="dev", official=False, model="m", git_commit="abc",
        requests_per_minute=10, gap_seconds=6.5, transcript_ids=["x"],
        started_at=datetime.now(UTC),
    )  # fmt: skip
    md = render_markdown(BenchmarkReport(meta=meta, results=[result]))
    assert "| regex | promise_made | 0.0% | 0.0% | 0.0% | 0 / 1 / 0 |" in md
    assert "`x`" in md and "expected (False, None, None)" in md
