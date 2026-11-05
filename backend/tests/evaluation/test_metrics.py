from app.evaluation.metrics import compute_metrics, p95
from app.evaluation.report_md import render_markdown
from tests.evaluation.results_builder import result, run_file


def test_p95_nearest_rank():
    assert p95([]) == 0.0
    assert p95([5.0]) == 5.0
    assert p95([float(i) for i in range(1, 21)]) == 19.0
    assert p95([float(i) for i in range(1, 101)]) == 95.0


def test_metrics_count_success_escalation_usage_and_categories():
    results = [result("a", True), result("b", False, escalated=True)]
    m = compute_metrics(results)
    assert m["task_success_rate"] == 0.5 and m["passed"] == 1
    assert m["escalation_accuracy"] == 0.5 and m["false_escalations"] == 1
    assert m["missed_escalations"] == 0
    assert m["llm_usage"]["calls"] == 4 and m["llm_usage"]["total_tokens"] == 28
    assert m["llm_call_latency_ms"] == {"avg": 200.0, "p95": 300.0, "count": 4}
    assert m["by_category"] == {"normal_plan": {"passed": 1, "total": 2}}


def test_markdown_lists_every_scenario_with_reasons():
    md = render_markdown(run_file("baseline", [result("a", True), result("b", False, True)]))
    assert "| a | PASS | all checks passed |" in md
    assert "| b | FAIL | escalated: expected False, got True |" in md
    assert "Task success rate | 50.0% (1/2)" in md
