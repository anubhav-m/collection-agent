import { request } from './client'
import type {
  ChatResult,
  ConversationView,
  ReportSource,
  ReportsResponse,
  ResultsResponse,
} from './types'

export interface ChatInput {
  conversationId: string | null
  lenderId: string
  message: string
}

export function sendChat({ conversationId, lenderId, message }: ChatInput): Promise<ChatResult> {
  // A new conversation needs the lender; an existing one is identified by its ID alone.
  const body = conversationId
    ? { conversation_id: conversationId, message }
    : { lender_id: lenderId, message }
  return request<ChatResult>('/chat', { method: 'POST', body: JSON.stringify(body) })
}

export function getConversation(conversationId: string): Promise<ConversationView> {
  return request<ConversationView>(`/conversations/${encodeURIComponent(conversationId)}`)
}

export function getResults(): Promise<ResultsResponse> {
  return request<ResultsResponse>('/results')
}

export function getReports(source: ReportSource): Promise<ReportsResponse> {
  return request<ReportsResponse>(`/reports?source=${source}`)
}
