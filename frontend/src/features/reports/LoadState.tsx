import type { ReactNode } from 'react'
import { Notice } from '../../components/Notice'
import { SkeletonLines } from '../../components/SkeletonLines'
import type { Loaded } from './useLoad'

interface Props<T> {
  load: Loaded<T>
  what: string
  isEmpty: (data: T) => boolean
  empty: ReactNode
  children: (data: T) => ReactNode
}

/** Loading, failure, empty and ready states for one results section. */
export function LoadState<T>({ load, what, isEmpty, empty, children }: Props<T>) {
  if (load.loading && !load.data) return <SkeletonLines label={`Loading ${what}`} lines={4} />
  if (load.error && load.error.kind !== 'not_found') {
    return (
      <Notice tone="problem" action={{ label: 'Try again', onClick: load.retry }}>
        The {what} could not be loaded. {load.error.message}
      </Notice>
    )
  }
  if (!load.data || isEmpty(load.data)) return <Notice tone="info">{empty}</Notice>
  return <>{children(load.data)}</>
}
