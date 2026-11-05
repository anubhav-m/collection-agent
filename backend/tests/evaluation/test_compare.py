from app.evaluation.compare import comparable, compare, render
from tests.evaluation.results_builder import result, run_file


def test_compare_lists_fixed_regressed_and_still_failing():
    before = run_file("baseline", [result("a", False), result("b", True), result("c", False)])
    after = run_file(
        "latest", [result("a", True), result("b", False), result("c", False)], commit="def"
    )
    assert comparable(before, after) is None
    diff = compare(before, after)
    assert (diff["fixed"], diff["regressed"], diff["still_failing"]) == (["a"], ["b"], ["c"])
    assert "| task_success_rate | 0.333 | 0.333 |" in render(diff)


def test_different_model_or_unfinished_run_is_not_comparable():
    before = run_file("baseline", [result("a", True)])
    assert comparable(before, run_file("latest", [result("a", True)], model="m-2"))
    unfinished = run_file("latest", [result("a", True)]).model_copy(update={"metrics": None})
    assert comparable(before, unfinished)
