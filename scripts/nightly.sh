#!/usr/bin/env bash
# Nightly job: extract promises -> load SQLite -> write reports. Stops at the first failed
# step, logs each step with its timing, writes run.json, and exits non-zero on failure.
# Usage: scripts/nightly.sh [llm|regex] [YYYY-MM-DD]     (NIGHTLY_DIR, NIGHTLY_PYTHON optional)
set -uo pipefail  # no -e: each step's exit code is checked and recorded explicitly

extractor="${1:-llm}"
as_of="${2:-$(date +%Y-%m-%d)}"
case "$extractor" in llm | regex) ;; *) echo "extractor must be llm or regex" >&2; exit 2 ;; esac
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
backend="$here/../backend"
nightly_dir="${NIGHTLY_DIR:-$here/../reports/nightly}"
python="${NIGHTLY_PYTHON:-}"
if [[ -z "$python" ]]; then
  for candidate in "$backend/.venv/bin/python" "$backend/.venv/Scripts/python.exe"; do
    [[ -x "$candidate" ]] && python="$candidate" && break
  done
fi
run_id="${as_of}_$(date +%H%M%S)"
run_dir="$nightly_dir/$run_id"
mkdir -p "$run_dir"
log="$run_dir/nightly.log"
export PYTHONIOENCODING=utf-8

stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
now() { echo "${EPOCHREALTIME:-$(date +%s)}"; }
log_line() { echo "[$(stamp)] $*" | tee -a "$log"; }

steps_json=""
failed_step="null"
exit_code=0
run_step() {  # name, then the python arguments
  local name="$1"; shift
  log_line "START $name"
  local start; start="$(now)"
  (cd "$backend" && "$python" "$@") 2>&1 | while IFS= read -r line; do log_line "  $name | $line"; done
  local code="${PIPESTATUS[0]}"
  local seconds; seconds="$(awk -v a="$start" -v b="$(now)" 'BEGIN { printf "%.2f", b - a }')"
  local status=success; [[ "$code" -ne 0 ]] && status=failed
  log_line "END $name status=$status exit=$code seconds=$seconds"
  steps_json+="${steps_json:+, }{\"name\": \"$name\", \"status\": \"$status\", \"exit_code\": $code, \"seconds\": $seconds}"
  if [[ "$code" -ne 0 ]]; then failed_step="\"$name\""; exit_code="$code"; return 1; fi
}

started="$(stamp)"
log_line "nightly run $run_id (as of $as_of, extractor $extractor)"
if [[ -z "$python" ]]; then
  log_line "ERROR python not found in $backend/.venv"; failed_step='"setup"'; exit_code=1
else
  run_step extract -m app.extraction.run_stored --extractor "$extractor" --summary "$run_dir/extraction.json" &&
    run_step load -m app.reports.load_cli --as-of "$as_of" --extractor "$extractor" --out "$run_dir" &&
    run_step reports -m app.reports.report_cli --as-of "$as_of" --out "$run_dir"
fi
status=success; [[ "$exit_code" -ne 0 ]] && status=failed
cat >"$run_dir/run.json" <<JSON
{"run_id": "$run_id", "as_of": "$as_of", "status": "$status", "started_at": "$started",
 "finished_at": "$(stamp)", "failed_step": $failed_step, "exit_code": $exit_code,
 "steps": [$steps_json]}
JSON
cp "$run_dir/run.json" "$nightly_dir/last_run.json"
log_line "FINISHED status=$status exit=$exit_code output=$run_dir"
exit "$exit_code"
