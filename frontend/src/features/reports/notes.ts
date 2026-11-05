import type { ReportsResponse, ResultsResponse } from '../../api/types'

export const REPO_URL = 'https://github.com/anubhav-m/collection-agent/blob/main/'

export interface ReportNote {
  n: number
  key: string
  path: string
  what: string
}

/** Number every report file the page cites, in reading order, so each figure can point at one. */
export function buildNotes(
  results: ResultsResponse | null,
  project: ReportsResponse | null,
  simulated: ReportsResponse | null,
): ReportNote[] {
  const cited: Omit<ReportNote, 'n'>[] = []
  for (const run of results?.evaluation ?? []) {
    cited.push({
      key: `eval-${run.run_name}`,
      path: run.report_path,
      what: `Evaluation, ${run.run_name} run`,
    })
  }
  const extraction = results?.extraction[0]
  if (extraction) {
    cited.push({
      key: 'extraction',
      path: extraction.report_path,
      what: 'Extraction benchmark, held-out test split',
    })
  }
  for (const report of [project, simulated]) {
    if (!report) continue
    const source = report.report.source
    cited.push({
      key: `nightly-${source}`,
      path: `reports/nightly/${report.run_id}/${source}.json`,
      what: `Nightly ${source} report, run ${report.run_id}`,
    })
  }
  return cited.map((note, i) => ({ ...note, n: i + 1 }))
}

export function noteFor(notes: ReportNote[], key: string): ReportNote | undefined {
  return notes.find((note) => note.key === key)
}
