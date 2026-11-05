import { useCallback, useEffect, useState } from 'react'
import { toApiError, type ApiError } from '../../api/client'
import { getConversation } from '../../api/endpoints'
import type { ConversationView } from '../../api/types'

interface Settled {
  key: string
  view: ConversationView | null
  error: ApiError | null
}

/** The server's stored record of the conversation, refetched after every finished turn. */
export function useConversationView(conversationId: string | null, turns: number) {
  const [attempt, setAttempt] = useState(0)
  const [settled, setSettled] = useState<Settled>({ key: '', view: null, error: null })
  const key = conversationId ? `${conversationId}:${turns}:${attempt}` : ''

  useEffect(() => {
    if (!conversationId) return
    let cancelled = false
    getConversation(conversationId).then(
      (view) => !cancelled && setSettled({ key, view, error: null }),
      (failure: unknown) =>
        !cancelled && setSettled((s) => ({ key, view: s.view, error: toApiError(failure) })),
    )
    return () => {
      cancelled = true
    }
  }, [conversationId, key])

  const retry = useCallback(() => setAttempt((n) => n + 1), [])
  // Keep showing the last record for this conversation while the next one loads.
  const sameConversation =
    conversationId !== null && settled.view?.conversation_id === conversationId
  const loading = conversationId !== null && settled.key !== key
  return {
    view: sameConversation ? settled.view : null,
    loading,
    error: !conversationId || loading ? null : settled.error,
    retry,
  }
}
