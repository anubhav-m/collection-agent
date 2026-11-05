import { useCallback, useEffect, useState } from 'react'
import { toApiError, type ApiError } from '../../api/client'

export interface Loaded<T> {
  data: T | null
  loading: boolean
  error: ApiError | null
  retry: () => void
}

interface Settled<T> {
  attempt: number
  data: T | null
  error: ApiError | null
}

/** Run one GET on mount, with loading, friendly-error and retry states. Loading is derived:
 * it is true until the current attempt has settled, so the effect never sets it directly. */
export function useLoad<T>(load: () => Promise<T>): Loaded<T> {
  const [attempt, setAttempt] = useState(0)
  const [settled, setSettled] = useState<Settled<T>>({ attempt: -1, data: null, error: null })

  useEffect(() => {
    let cancelled = false
    load().then(
      (data) => !cancelled && setSettled({ attempt, data, error: null }),
      (failure: unknown) =>
        !cancelled && setSettled((s) => ({ attempt, data: s.data, error: toApiError(failure) })),
    )
    return () => {
      cancelled = true
    }
  }, [load, attempt])

  const retry = useCallback(() => setAttempt((n) => n + 1), [])
  const loading = settled.attempt !== attempt
  return { data: settled.data, loading, error: loading ? null : settled.error, retry }
}
