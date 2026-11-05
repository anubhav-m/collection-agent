import type { ResultsResponse } from '../../api/types'
import { CategoryTable } from './CategoryTable'
import { EvaluationTable } from './EvaluationTable'
import { LoadState } from './LoadState'
import type { ReportNote } from './notes'
import type { Loaded } from './useLoad'

interface Props {
  load: Loaded<ResultsResponse>
  notes: ReportNote[]
}

export function EvaluationSection({ load, notes }: Props) {
  return (
    <section className="results-section" aria-labelledby="eval-title">
      <h2 id="eval-title" className="section-title">
        Agent evaluation
      </h2>
      <p className="muted section-lede">
        Scripted multi-turn conversations covering payment plans, verification, disputes, hardship,
        prompt injection and invented policy, run on the live model before and after one round of
        fixes.
      </p>
      <LoadState
        load={load}
        what="evaluation results"
        isEmpty={(d) => d.evaluation.length === 0}
        empty="No evaluation report has been saved yet."
      >
        {(data) => (
          <>
            <EvaluationTable runs={data.evaluation} notes={notes} />
            <CategoryTable runs={data.evaluation} />
          </>
        )}
      </LoadState>
    </section>
  )
}
