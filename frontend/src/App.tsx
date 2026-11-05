import { useState } from 'react'
import { AppHeader, type View } from './components/AppHeader'
import { ChatView } from './features/chat/ChatView'
import { ResultsView } from './features/reports/ResultsView'

export function App() {
  const [view, setView] = useState<View>('chat')
  return (
    <div className={`app app-view-${view}`}>
      <AppHeader view={view} onChange={setView} />
      <main className="app-main">
        {/* The chat stays mounted so a conversation survives a look at the results. */}
        <section
          id="view-chat"
          className="view"
          role="tabpanel"
          aria-labelledby="tab-chat"
          hidden={view !== 'chat'}
        >
          <ChatView />
        </section>
        <section
          id="view-results"
          className="view view-results"
          role="tabpanel"
          aria-labelledby="tab-results"
          hidden={view !== 'results'}
        >
          {view === 'results' && <ResultsView />}
        </section>
      </main>
    </div>
  )
}
