import { useEffect, useState } from 'react'

/** Seconds left from a starting value, ticking down to zero. The caller remounts the
 * component (with a new key) to start a fresh countdown. */
export function useCountdown(seconds: number | null): number {
  const [left, setLeft] = useState(seconds ?? 0)

  useEffect(() => {
    if (!seconds) return
    const timer = window.setInterval(() => {
      setLeft((n) => {
        if (n <= 1) window.clearInterval(timer)
        return Math.max(0, n - 1)
      })
    }, 1000)
    return () => window.clearInterval(timer)
  }, [seconds])

  return left
}
