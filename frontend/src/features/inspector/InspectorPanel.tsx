import { Notice } from '../../components/Notice'
import { SkeletonLines } from '../../components/SkeletonLines'
import type { SourceNote } from '../chat/chatTypes'
import { SourceList } from './SourceList'
import { StateLedger } from './StateLedger'
import { TurnList } from './TurnList'
import { toTurns } from './turns'
import { useConversationView } from './useConversationView'

interface Props {
  conversationId: string | null
  turnsAnswered: number
  notes: SourceNote[]
}

export function InspectorPanel({ conversationId, turnsAnswered, notes }: Props) {
  const { view, loading, error, retry } = useConversationView(conversationId, turnsAnswered)
  const turns = view ? toTurns(view.events) : []
  return (
    <aside className="inspector" aria-label="Inspector">
      <StateLedger view={view} />
      {error && (
        <Notice tone="problem" action={{ label: 'Try again', onClick: retry }}>
          The server record for this conversation could not be loaded. {error.message}
        </Notice>
      )}
      {loading && !view ? (
        <SkeletonLines label="Loading server decisions" />
      ) : (
        <TurnList turns={turns} />
      )}
      <SourceList notes={notes} />
    </aside>
  )
}
