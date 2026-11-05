import type { ApiError } from '../../api/client'
import type { ChatResult } from '../../api/types'
import type { ChatMessage, ChatState } from './chatTypes'

let lastId = 0
const nextId = () => ++lastId

export function withUserMessage(state: ChatState, text: string): ChatState {
  const kept = state.messages.filter((m) => !m.failed)
  const turn = kept.filter((m) => m.role === 'user').length + 1
  const message: ChatMessage = { id: nextId(), role: 'user', text, turn, footnotes: [] }
  return { ...state, messages: [...kept, message], pending: true, error: null }
}

export function withReply(state: ChatState, result: ChatResult): ChatState {
  const turn = state.messages.filter((m) => m.role === 'user').length
  const start = state.notes.length + 1
  const notes = result.sources.map((source, i) => ({ n: start + i, turn, source }))
  const footnotes = notes.map((note) => note.n)
  const reply: ChatMessage = {
    id: nextId(),
    role: 'assistant',
    text: result.reply,
    turn,
    footnotes,
  }
  return {
    ...state,
    conversationId: result.conversation_id,
    messages: [...state.messages, reply],
    notes: [...state.notes, ...notes],
    last: result,
    pending: false,
  }
}

export function withFailure(state: ChatState, error: ApiError): ChatState {
  const messages = state.messages.map((m, i) =>
    i === state.messages.length - 1 && m.role === 'user' ? { ...m, failed: true } : m,
  )
  return { ...state, messages, pending: false, error, failures: state.failures + 1 }
}
