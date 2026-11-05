import type { EvaluationRun } from '../../api/types'
import { int, pct, runLabel, shortDate } from './format'
import { NoteMark } from './NoteMark'
import type { ReportNote } from './notes'

const ROWS: { name: string; value: (run: EvaluationRun) => string }[] = [
  { name: 'Scenarios passed', value: (r) => `${r.passed} of ${r.scenario_count}` },
  { name: 'Task success rate', value: (r) => pct(r.task_success_rate) },
  { name: 'Escalation accuracy', value: (r) => pct(r.escalation_accuracy) },
  { name: 'Missed escalations', value: (r) => int(r.missed_escalations) },
  { name: 'False escalations', value: (r) => int(r.false_escalations) },
  { name: 'Unauthorized actions', value: (r) => int(r.unauthorized_actions) },
  { name: 'LLM calls in the run', value: (r) => int(r.llm_calls) },
]

interface Props {
  runs: EvaluationRun[]
  notes: ReportNote[]
}

export function EvaluationTable({ runs, notes }: Props) {
  return (
    <table className="figures">
      <caption className="visually-hidden">Evaluation runs compared</caption>
      <thead>
        <tr>
          <th scope="col">Measure</th>
          {runs.map((run) => (
            <th key={run.run_name} scope="col" className="num">
              {runLabel(run)}
              <NoteMark notes={notes} cite={`eval-${run.run_name}`} />
              <span className="th-sub">
                {shortDate(run.finished_at)} · {run.model}
              </span>
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {ROWS.map((row) => (
          <tr key={row.name}>
            <th scope="row">{row.name}</th>
            {runs.map((run) => (
              <td key={run.run_name} className="num">
                {row.value(run)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
