// Shapes for GET /results and GET /reports. Keep in step with
// backend/app/reports/published_results.py and app/reports/nightly_status.py.

export interface EvaluationRun {
  run_name: string
  model: string
  git_commit: string
  finished_at: string
  scenario_count: number
  passed: number
  task_success_rate: number
  escalation_accuracy: number
  missed_escalations: number
  false_escalations: number
  unauthorized_actions: number
  llm_calls: number
  by_category: Record<string, { passed: number; total: number }>
  report_path: string
}

export interface EntityScore {
  precision: number
  recall: number
  f1: number
}

export interface ExtractionRun {
  extractor: string
  split: string
  model: string | null
  transcripts: number
  exact_match_rate: number
  entities: Record<string, EntityScore>
  report_path: string
}

export interface ResultsResponse {
  evaluation: EvaluationRun[]
  extraction: ExtractionRun[]
}

export type ReportSource = 'project' | 'simulated'
export type ReportRow = Record<string, string | number | null>

export interface ReportsResponse {
  run_id: string
  run_finished_at: string
  report: {
    source: ReportSource
    note: string
    as_of: string
    generated_at: string
    row_counts: Record<string, number>
    reports: Record<string, ReportRow[]>
  }
}
