import type { KeyboardEvent } from 'react'

export type View = 'chat' | 'results'

const TABS: { id: View; label: string }[] = [
  { id: 'chat', label: 'Chat' },
  { id: 'results', label: 'Results' },
]

interface Props {
  view: View
  onChange: (view: View) => void
}

export function AppHeader({ view, onChange }: Props) {
  function onKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key !== 'ArrowRight' && event.key !== 'ArrowLeft') return
    const next = view === 'chat' ? 'results' : 'chat'
    onChange(next)
    document.getElementById(`tab-${next}`)?.focus()
  }

  return (
    <header className="app-header">
      <div className="app-header-bar">
        <p className="app-name">
          Collections agent <span className="app-name-qualifier">simulation</span>
        </p>
        <div className="tabs" role="tablist" aria-label="Views" onKeyDown={onKeyDown}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              type="button"
              role="tab"
              className="tab"
              aria-selected={view === tab.id}
              aria-controls={`view-${tab.id}`}
              tabIndex={view === tab.id ? 0 : -1}
              onClick={() => onChange(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>
      <p className="sim-notice" role="note">
        Simulation. Every lender, borrower, account and payment here is fictional. This is a
        portfolio demo, not a production or legal compliance system.
      </p>
    </header>
  )
}
