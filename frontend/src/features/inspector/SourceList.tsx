import type { SourceNote } from '../chat/chatTypes'

interface Props {
  notes: SourceNote[]
}

/** Policy passages retrieved for replies, numbered to match the marks in the chat. */
export function SourceList({ notes }: Props) {
  return (
    <section className="sources" aria-labelledby="sources-title">
      <h2 id="sources-title" className="label">
        Policy sources
      </h2>
      {notes.length === 0 ? (
        <p className="muted small">
          When a reply relies on the lender's policy documents, the passages it used are listed here
          with their match score.
        </p>
      ) : (
        <ol className="source-list">
          {notes.map(({ n, turn, source }) => (
            <li key={n} id={`source-${n}`} className="source">
              <span className="source-n">{n}</span>
              <div>
                <p className="source-title">
                  {source.title} <span className="muted">· {source.section}</span>
                </p>
                <p className="small muted">
                  <code>{source.doc_id}</code> · turn {turn} · score {source.score.toFixed(2)}
                </p>
              </div>
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
