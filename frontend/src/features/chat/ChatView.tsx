import { useState } from 'react'
import { InspectorPanel } from '../inspector/InspectorPanel'
import { BorrowerRail } from './BorrowerRail'
import { Conversation } from './Conversation'
import { SAMPLE_BORROWERS, type SampleBorrower } from './sampleBorrowers'
import { useChat } from './useChat'

export function ChatView() {
  const [borrower, setBorrower] = useState<SampleBorrower>(SAMPLE_BORROWERS[0])
  const chat = useChat(borrower.lenderId)
  const answered = chat.state.messages.filter((m) => m.role === 'assistant').length

  function choose(next: SampleBorrower) {
    if (next.id === borrower.id) return
    chat.reset()
    setBorrower(next)
  }

  return (
    <div className="chat-layout">
      <BorrowerRail selectedId={borrower.id} onSelect={choose} />
      <Conversation borrower={borrower} chat={chat} />
      <InspectorPanel
        conversationId={chat.state.conversationId}
        turnsAnswered={answered}
        notes={chat.state.notes}
      />
    </div>
  )
}
