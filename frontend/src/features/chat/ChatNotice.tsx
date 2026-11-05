import type { ApiError } from '../../api/client'
import { Notice } from '../../components/Notice'
import { useCountdown } from './useCountdown'

interface Props {
  error: ApiError | null
  onRetry: () => void
}

/** Friendly failure line for the last message, with a retry that waits out rate limits. */
export function ChatNotice({ error, onRetry }: Props) {
  const wait = useCountdown(error?.kind === 'rate_limited' ? error.retryAfterSeconds : null)
  if (!error) return null
  if (error.kind === 'daily_limit') {
    return <Notice tone="wait">{error.message}</Notice>
  }
  const waiting = wait > 0
  return (
    <Notice
      tone={error.kind === 'rate_limited' ? 'wait' : 'problem'}
      action={{
        label: waiting ? `Try again in ${wait}s` : 'Try again',
        onClick: onRetry,
        disabled: waiting,
      }}
    >
      Your last message was not sent. {error.message}
    </Notice>
  )
}
