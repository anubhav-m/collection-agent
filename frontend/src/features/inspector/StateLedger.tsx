import type { ConversationView } from '../../api/types'
import { reasonLabel } from './labels'

const MAX_ATTEMPTS = 3 // mirrors MAX_VERIFICATION_ATTEMPTS in backend/app/agent/state.py

interface Props {
  view: ConversationView | null
}

/** Server-held state. The browser only displays it; it can never set it. */
export function StateLedger({ view }: Props) {
  const escalated = view?.status === 'escalated'
  return (
    <section className="ledger" aria-labelledby="ledger-title">
      <h2 id="ledger-title" className="label">
        Server state
      </h2>
      <dl>
        <div>
          <dt>Identity</dt>
          <dd className={view?.verified ? 'state-ok' : undefined}>
            {view?.verified ? 'Verified' : 'Not verified'}
            {view && view.failed_verifications > 0 && (
              <span className="muted">
                {' '}
                · {view.failed_verifications} of {MAX_ATTEMPTS} attempts failed
              </span>
            )}
          </dd>
        </div>
        <div>
          <dt>Conversation</dt>
          <dd className={escalated ? 'state-handoff' : undefined}>
            {!view ? 'Not started' : escalated ? 'Handed to a person' : 'Active with the agent'}
          </dd>
        </div>
        <div>
          <dt>Reason</dt>
          <dd>{view?.escalation_reason ? reasonLabel(view.escalation_reason) : '—'}</dd>
        </div>
        <div>
          <dt>ID</dt>
          <dd className="data ledger-id">{view?.conversation_id ?? '—'}</dd>
        </div>
      </dl>
    </section>
  )
}
