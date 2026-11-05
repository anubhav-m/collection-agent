import type { ExtractionRun } from '../../api/types'
import { label, pct } from './format'

const extractorName = (run: ExtractionRun) =>
  run.extractor === 'llm' ? `LLM (${run.model})` : 'Regex rules'

interface Props {
  runs: ExtractionRun[]
}

export function ExtractionTable({ runs }: Props) {
  return (
    <table className="figures">
      <caption className="visually-hidden">Extraction precision, recall and F1</caption>
      <thead>
        <tr>
          <th scope="col">Extractor</th>
          <th scope="col">Entity</th>
          <th scope="col" className="num">
            Precision
          </th>
          <th scope="col" className="num">
            Recall
          </th>
          <th scope="col" className="num">
            F1
          </th>
        </tr>
      </thead>
      <tbody>
        {runs.flatMap((run) =>
          Object.entries(run.entities).map(([entity, score], i) => (
            <tr key={`${run.extractor}-${entity}`} className={i === 0 ? 'group-start' : undefined}>
              <th scope="row">
                {i === 0 && extractorName(run)}
                {i === 0 && <span className="th-sub">{run.transcripts} transcripts</span>}
              </th>
              <td>{label(entity)}</td>
              <td className="num">{pct(score.precision)}</td>
              <td className="num">{pct(score.recall)}</td>
              <td className="num">{pct(score.f1)}</td>
            </tr>
          )),
        )}
      </tbody>
    </table>
  )
}
