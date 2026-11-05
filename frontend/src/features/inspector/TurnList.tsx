import { escalationSourceLabel, reasonLabel } from './labels'
import { ToolCallEntry } from './ToolCallEntry'
import type { Turn } from './turns'

interface Props {
  turns: Turn[]
}

export function TurnList({ turns }: Props) {
  return (
    <section className="turns" aria-labelledby="turns-title">
      <h2 id="turns-title" className="label">
        Server decisions by turn
      </h2>
      {turns.length === 0 ? (
        <p className="muted small">
          Each message you send appears here with the tools the agent asked for and whether the
          server allowed them.
        </p>
      ) : (
        <ol className="turn-list">
          {turns.map((turn) => (
            <li key={turn.n} id={`turn-${turn.n}`} className="turn">
              <h3 className="turn-title">
                <span className="turn-number">Turn {turn.n}</span>
                <span className="turn-quote">{turn.userText}</span>
              </h3>
              {turn.tools.length === 0 && !turn.escalation && (
                <p className="muted small">Answered without tools.</p>
              )}
              {turn.tools.length > 0 && (
                <ol className="tool-list">
                  {turn.tools.map((tool) => (
                    <ToolCallEntry key={tool.key} tool={tool} />
                  ))}
                </ol>
              )}
              {turn.escalation && (
                <p className="escalation state-handoff small">
                  Handed to a person: {reasonLabel(turn.escalation.reason)}, by{' '}
                  {escalationSourceLabel(turn.escalation.source)}.
                </p>
              )}
            </li>
          ))}
        </ol>
      )}
    </section>
  )
}
