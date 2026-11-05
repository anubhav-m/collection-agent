import { FootnoteMark } from '../../components/FootnoteMark'
import type { ChatMessage } from './chatTypes'
import { displayText } from './displayText'

interface Props {
  message: ChatMessage
}

/** One message as plain text; React escapes it, and no HTML from the model is rendered. */
export function MessageItem({ message }: Props) {
  const fromAgent = message.role === 'assistant'
  return (
    <li className={`message message-${message.role}${message.failed ? ' message-failed' : ''}`}>
      <p className="message-who small">{fromAgent ? 'Agent' : 'You'}</p>
      <p className="message-text">
        {fromAgent ? displayText(message.text) : message.text}
        {message.footnotes.map((n) => (
          <FootnoteMark key={n} target={`source-${n}`} label={`Policy source ${n}`}>
            {n}
          </FootnoteMark>
        ))}
      </p>
      {fromAgent && (
        <p className="message-meta small">
          <a href={`#turn-${message.turn}`}>Server decisions for turn {message.turn}</a>
        </p>
      )}
      {message.failed && <p className="message-meta small muted">Not sent</p>}
    </li>
  )
}
