import type { ApiError } from '../../api/client'
import type { ChatResult, PolicySource } from '../../api/types'

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  text: string
  turn: number
  footnotes: number[] // policy-source numbers this reply drew on
  failed?: boolean
}

export interface SourceNote {
  n: number
  turn: number
  source: PolicySource
}

export interface ChatState {
  conversationId: string | null
  messages: ChatMessage[]
  notes: SourceNote[]
  last: ChatResult | null
  pending: boolean
  error: ApiError | null
  failures: number // counts failed sends, so each failure gets a fresh notice
}

export const EMPTY_CHAT: ChatState = {
  conversationId: null,
  messages: [],
  notes: [],
  last: null,
  pending: false,
  error: null,
  failures: 0,
}
