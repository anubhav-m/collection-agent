import type { ReportsResponse } from '../../api/types'
import { int, pctUnits } from './format'

interface Props {
  data: ReportsResponse
}

export function SimulatedReport({ data }: Props) {
  const { report } = data
  const lenders = report.reports.kept_rate_lender ?? []
  const followups = report.reports.followups ?? []
  const overdue = followups.filter((row) => row.followup_status === 'overdue').length
  return (
    <div className="report report-simulated">
      <p className="simulated-flag small">
        Simulated data from a seeded generator. These numbers come from the generator's own settings
        and only show the SQL working at volume. They are not project results.
      </p>
      <table className="figures figures-compact">
        <caption className="table-caption">Promise kept rate by simulated lender</caption>
        <thead>
          <tr>
            <th scope="col">Simulated lender</th>
            <th scope="col" className="num">
              Promises due
            </th>
            <th scope="col" className="num">
              Kept
            </th>
            <th scope="col" className="num">
              Kept rate
            </th>
          </tr>
        </thead>
        <tbody>
          {lenders.map((row) => (
            <tr key={String(row.lender_id)}>
              <th scope="row">{String(row.lender_name)}</th>
              <td className="num">{int(Number(row.promises_due))}</td>
              <td className="num">{int(Number(row.promises_kept))}</td>
              <td className="num">{pctUnits(Number(row.kept_rate_pct))}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="small muted">
        Follow-ups: {int(followups.length)}, of which {int(overdue)} are overdue. As of{' '}
        {report.as_of}.
      </p>
    </div>
  )
}
