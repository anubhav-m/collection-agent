import type { ReportsResponse } from '../../api/types'
import { label, pctUnits, shortDate } from './format'

interface Props {
  data: ReportsResponse
}

export function ProjectReport({ data }: Props) {
  const { report } = data
  const counts = report.row_counts
  const reasons = report.reports.escalation_reasons ?? []
  return (
    <div className="report">
      <p className="small muted">
        As of {report.as_of}, run finished {shortDate(data.run_finished_at)}. The project has only a
        few stored demo conversations, so most of these reports are short or empty.
      </p>
      <dl className="report-counts">
        <div>
          <dt>Follow-ups due</dt>
          <dd className="num">{counts.followups ?? 0}</dd>
        </div>
        <div>
          <dt>Lenders with a kept rate</dt>
          <dd className="num">{counts.kept_rate_lender ?? 0}</dd>
        </div>
        <div>
          <dt>Escalation reason rows</dt>
          <dd className="num">{counts.escalation_reasons ?? 0}</dd>
        </div>
      </dl>
      {reasons.length > 0 && (
        <table className="figures figures-compact">
          <caption className="table-caption">Escalation reasons by lender</caption>
          <thead>
            <tr>
              <th scope="col">Lender</th>
              <th scope="col">Reason</th>
              <th scope="col" className="num">
                Escalations
              </th>
              <th scope="col" className="num">
                Share
              </th>
            </tr>
          </thead>
          <tbody>
            {reasons.map((row) => (
              <tr key={`${row.lender_id}-${row.reason}`}>
                <th scope="row">{String(row.lender_name)}</th>
                <td>{label(String(row.reason))}</td>
                <td className="num">{Number(row.escalations)}</td>
                <td className="num">{pctUnits(Number(row.share_pct))}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
