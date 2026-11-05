import { ChatNotice } from './ChatNotice'
import { Composer } from './Composer'
import { MessageList } from './MessageList'
import type { SampleBorrower } from './sampleBorrowers'
import { StarterMessages } from './StarterMessages'
import type { useChat } from './useChat'

interface Props {
  borrower: SampleBorrower
  chat: ReturnType<typeof useChat>
}

export function Conversation({ borrower, chat }: Props) {
  const { state, send, retry, reset } = chat
  const escalated = state.last?.status === 'escalated'
  return (
    <section className="conversation" aria-labelledby="conversation-title">
      <header className="conversation-head">
        <div>
          <h1 id="conversation-title" className="conversation-title">
            {borrower.name}
          </h1>
          <p className="small muted">
            {borrower.lenderName} · {borrower.situation}
          </p>
        </div>
        <button
          type="button"
          className="button button-quiet"
          onClick={reset}
          disabled={state.messages.length === 0}
        >
          New conversation
        </button>
      </header>
      <MessageList messages={state.messages} pending={state.pending} />
      <div className="conversation-foot">
        {escalated && (
          <p className="handoff-banner" role="status">
            This conversation is now with a person. The agent will not discuss payments further.
          </p>
        )}
        {/* Keyed by the failure count so each new failure starts its own countdown. */}
        <ChatNotice key={state.failures} error={state.error} onRetry={retry} />
        <StarterMessages starters={borrower.starters} disabled={state.pending} onPick={send} />
        <Composer disabled={state.pending} onSend={send} />
      </div>
    </section>
  )
}
