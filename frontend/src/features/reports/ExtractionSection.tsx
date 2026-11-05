import type { ResultsResponse } from '../../api/types'
import { ExtractionTable } from './ExtractionTable'
import { LoadState } from './LoadState'
import { NoteMark } from './NoteMark'
import type { ReportNote } from './notes'
import type { Loaded } from './useLoad'

interface Props {
  load: Loaded<ResultsResponse>
  notes: ReportNote[]
}

export function ExtractionSection({ load, notes }: Props) {
  return (
    <section className="results-section" aria-labelledby="extraction-title">
      <h2 id="extraction-title" className="section-title">
        Promise extraction
        <NoteMark notes={notes} cite="extraction" />
      </h2>
      <p className="muted section-lede">
        Finding a promised payment, its amount and its date in a finished chat. Scored on a held-out
        set of labelled fictional transcripts that was not used while building.
      </p>
      <LoadState
        load={load}
        what="extraction results"
        isEmpty={(d) => d.extraction.length === 0}
        empty="No extraction benchmark has been saved yet."
      >
        {(data) => <ExtractionTable runs={data.extraction} />}
      </LoadState>
    </section>
  )
}
