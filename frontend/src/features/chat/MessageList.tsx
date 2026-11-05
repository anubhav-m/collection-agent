import { useEffect, useRef } from 'react'
import type { ChatMessage } from './chatTypes'
import { MessageItem } from './MessageItem'

interface Props {
  messages: ChatMessage[]
  pending: boolean
}

export function MessageList({ messages, pending }: Props) {
  const end = useRef<HTMLDivElement>(null)
  useEffect(() => {
    end.current?.scrollIntoView({ block: 'end' })
  }, [messages.length, pending])

  return (
    <div className="messages" role="log" aria-live="polite" aria-relevant="additions">
      {messages.length === 0 ? (
        <div className="messages-empty">
          <p>No messages yet.</p>
          <p className="small muted">
            Use a starter below or write your own. Share the name, date of birth and ZIP shown in
            the sample to get verified, then ask about the balance or a payment plan.
          </p>
        </div>
      ) : (
        <ol className="message-list">
          {messages.map((message) => (
            <MessageItem key={message.id} message={message} />
          ))}
          {pending && (
            <li
              className="message message-assistant message-pending"
              aria-label="Agent is replying"
            >
              <span className="typing" aria-hidden="true">
                <span />
                <span />
                <span />
              </span>
              <span className="small muted">The agent is checking with the server…</span>
            </li>
          )}
        </ol>
      )}
      <div ref={end} />
    </div>
  )
}
