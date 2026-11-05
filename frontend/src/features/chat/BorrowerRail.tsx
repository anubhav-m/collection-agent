import { SAMPLE_BORROWERS, type SampleBorrower } from './sampleBorrowers'

interface Props {
  selectedId: string
  onSelect: (borrower: SampleBorrower) => void
}

export function BorrowerRail({ selectedId, onSelect }: Props) {
  return (
    <nav className="rail" aria-labelledby="rail-title">
      <h2 id="rail-title" className="label">
        Sample borrowers
      </h2>
      <p className="small muted rail-help">
        Pick one, then send a starter message. Switching starts a new conversation.
      </p>
      <ul className="borrower-list">
        {SAMPLE_BORROWERS.map((b) => (
          <li key={b.id}>
            <button
              type="button"
              className="borrower"
              aria-pressed={b.id === selectedId}
              onClick={() => onSelect(b)}
            >
              <span className="borrower-name">{b.name}</span>
              <span className="small muted">{b.lenderName}</span>
              <span className="small borrower-identity data">
                DOB {b.dateOfBirth} · ZIP {b.zip}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  )
}
