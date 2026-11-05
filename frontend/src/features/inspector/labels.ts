// Plain-language names for server codes. Unknown codes fall back to the code itself.

const REASONS: Record<string, string> = {
  dispute: 'Dispute',
  hardship: 'Hardship',
  stop_contact: 'Stop contact',
  human_request: 'Asked for a person',
  verification_failed: 'Verification failed',
  other: 'Other',
}

const REFUSALS: Record<string, string> = {
  verification_required: 'Identity not verified yet',
  verification_failed: 'Details did not match',
  verification_locked: 'No verification attempts left',
  account_not_accessible: 'Account not linked to this borrower',
  plan_not_allowed: "Plan breaks the lender's rules",
  plan_already_exists: 'Plan already saved',
  invalid_arguments: 'Arguments failed validation',
  unknown_tool: 'Unknown tool',
  escalated: 'Conversation is with a person',
  tool_iteration_limit: 'Tool-call limit reached',
  policy_search_unavailable: 'Policy search unavailable',
}

const SOURCES: Record<string, string> = {
  rule: 'phrase rule in code',
  verification_limit: 'third failed verification',
  model: 'agent tool call',
}

export const reasonLabel = (code: string) => REASONS[code] ?? code
export const refusalLabel = (code: string) => REFUSALS[code] ?? code
export const escalationSourceLabel = (code: string) => SOURCES[code] ?? code
