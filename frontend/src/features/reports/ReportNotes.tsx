import { REPO_URL, type ReportNote } from './notes'

interface Props {
  notes: ReportNote[]
}

export function ReportNotes({ notes }: Props) {
  if (notes.length === 0) return null
  return (
    <section className="results-section report-notes" aria-labelledby="notes-title">
      <h2 id="notes-title" className="label">
        Sources
      </h2>
      <ol className="note-list">
        {notes.map((note) => (
          <li key={note.n} id={`note-${note.n}`}>
            <span className="source-n">{note.n}</span>
            <span>
              {note.what}:{' '}
              <a href={`${REPO_URL}${note.path}`} target="_blank" rel="noreferrer">
                <code>{note.path}</code>
              </a>
            </span>
          </li>
        ))}
      </ol>
    </section>
  )
}
