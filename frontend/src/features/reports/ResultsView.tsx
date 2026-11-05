import { useCallback } from 'react'
import { getReports, getResults } from '../../api/endpoints'
import { EvaluationSection } from './EvaluationSection'
import { ExtractionSection } from './ExtractionSection'
import { NightlySection } from './NightlySection'
import { buildNotes } from './notes'
import { ReportNotes } from './ReportNotes'
import { useLoad } from './useLoad'

export function ResultsView() {
  const results = useLoad(getResults)
  const project = useLoad(useCallback(() => getReports('project'), []))
  const simulated = useLoad(useCallback(() => getReports('simulated'), []))
  const notes = buildNotes(results.data, project.data, simulated.data)

  return (
    <div className="results">
      <header className="results-head">
        <h1 className="results-title">Results</h1>
        <p className="muted">
          Every figure on this page is read from a report file saved in the repository. The numbered
          marks point to the file each figure came from.
        </p>
      </header>
      <EvaluationSection load={results} notes={notes} />
      <ExtractionSection load={results} notes={notes} />
      <NightlySection project={project} simulated={simulated} notes={notes} />
      <ReportNotes notes={notes} />
    </div>
  )
}
