import type { EvaluationRun } from '../../api/types'
import { label, runLabel } from './format'

interface Props {
  runs: EvaluationRun[]
}

export function CategoryTable({ runs }: Props) {
  const categories = Object.keys(runs.at(-1)?.by_category ?? {}).sort()
  if (categories.length === 0) return null
  return (
    <table className="figures figures-compact">
      <caption className="table-caption">Passed by scenario category</caption>
      <thead>
        <tr>
          <th scope="col">Category</th>
          {runs.map((run) => (
            <th key={run.run_name} scope="col" className="num">
              {runLabel(run)}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {categories.map((category) => (
          <tr key={category}>
            <th scope="row">{label(category)}</th>
            {runs.map((run) => {
              const cell = run.by_category[category]
              const short = cell && cell.passed < cell.total
              return (
                <td key={run.run_name} className={`num${short ? ' state-handoff' : ''}`}>
                  {cell ? `${cell.passed}/${cell.total}` : '—'}
                </td>
              )
            })}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
