import pytest

from app.evaluation.output import paths_for, write_reports
from app.evaluation.progress import ResumeMismatchError, load_or_start, save_atomic
from tests.evaluation.results_builder import meta, result, run_file


def test_progress_round_trips_and_resumes(tmp_path):
    path = tmp_path / "baseline.progress.json"
    save_atomic(path, run_file("baseline", [result("a", True)]))
    resumed = load_or_start(path, meta())
    assert [r.id for r in resumed.results] == ["a"]


def test_missing_progress_starts_empty(tmp_path):
    assert load_or_start(tmp_path / "none.json", meta()).results == []


@pytest.mark.parametrize("change", [{"commit": "other"}, {"model": "m-2"}])
def test_resume_with_different_model_or_commit_is_refused(tmp_path, change):
    path = tmp_path / "baseline.progress.json"
    save_atomic(path, run_file("baseline", [result("a", True)]))
    with pytest.raises(ResumeMismatchError):
        load_or_start(path, meta(**change))


def test_final_reports_written_and_progress_removed(tmp_path):
    paths = paths_for(tmp_path, "baseline", official=True)
    run = run_file("baseline", [result("a", True)])
    save_atomic(paths.progress, run)
    write_reports(paths, run)
    assert paths.final_json.exists() and paths.final_md.exists()
    assert not paths.progress.exists()


def test_debug_runs_go_to_their_own_folder(tmp_path):
    paths = paths_for(tmp_path, "dbg", official=False)
    assert paths.final_json.parent.name == "debug" and paths.progress is None
