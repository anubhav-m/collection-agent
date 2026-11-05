import { useCallback, useRef, useState } from 'react'
import { toApiError } from '../../api/client'
import { sendChat } from '../../api/endpoints'
import { withFailure, withReply, withUserMessage } from './chatState'
import { EMPTY_CHAT, type ChatState } from './chatTypes'

export function useChat(lenderId: string) {
  const [state, setState] = useState<ChatState>(EMPTY_CHAT)
  // Refs, not state, so a double click cannot send twice before the next render.
  const inFlight = useRef(false)
  const conversationId = useRef<string | null>(null)
  // Bumped on reset, so a reply that lands after the borrower changed is dropped.
  const generation = useRef(0)

  const send = useCallback(
    async (text: string) => {
      const message = text.trim()
      if (!message || inFlight.current) return
      inFlight.current = true
      const started = generation.current
      setState((s) => withUserMessage(s, message))
      try {
        const result = await sendChat({
          conversationId: conversationId.current,
          lenderId,
          message,
        })
        if (started !== generation.current) return
        conversationId.current = result.conversation_id
        setState((s) => withReply(s, result))
      } catch (error) {
        if (started !== generation.current) return
        setState((s) => withFailure(s, toApiError(error)))
      } finally {
        if (started === generation.current) inFlight.current = false
      }
    },
    [lenderId],
  )

  const failedText = state.messages.find((m) => m.failed)?.text
  const retry = useCallback(() => {
    if (failedText) void send(failedText)
  }, [failedText, send])

  const reset = useCallback(() => {
    generation.current += 1
    inFlight.current = false
    conversationId.current = null
    setState(EMPTY_CHAT)
  }, [])

  return { state, send, retry, reset }
}
