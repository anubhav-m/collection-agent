// Shapes returned by the FastAPI backend. Keep in step with backend/app/api/schemas.py,
// app/agent/results.py, app/api/results.py and app/api/reports.py.

export type ConversationStatus = 'active' | 'escalated'

export type EscalationReason =
  'dispute' | 'hardship' | 'stop_contact' | 'human_request' | 'verification_failed' | 'other'

export interface PolicySource {
  doc_id: string
  title: string
  section: string
  score: number
}

export interface ChatResult {
  conversation_id: string
  reply: string
  outcome: string
  status: ConversationStatus
  verified: boolean
  escalation_reason: EscalationReason | null
  sources: PolicySource[]
}

export type EventKind = 'user' | 'assistant' | 'tool_call' | 'tool_result' | 'escalation'

export interface ToolCallView {
  name: string
  args: Record<string, unknown>
}

export interface EventView {
  kind: EventKind
  text: string | null
  tool_calls: ToolCallView[]
  tool_name: string | null
  accepted: boolean | null
  reason: string | null
  result: Record<string, unknown> | null
  created_at: string
}

export interface ConversationView {
  conversation_id: string
  lender_id: string
  status: ConversationStatus
  verified: boolean
  failed_verifications: number
  escalation_reason: EscalationReason | null
  created_at: string
  events: EventView[]
}

export interface ApiErrorBody {
  error: { code: string; message: string; request_id: string }
}

// Result and report shapes live beside this file only to respect the line limit;
// import every API type from here.
export type * from './resultTypes'
