interface Props {
  lines?: number
  label: string
}

/** Placeholder rows shown while content loads, in place of a spinner. */
export function SkeletonLines({ lines = 3, label }: Props) {
  return (
    <div className="skeleton" role="status" aria-label={label}>
      {Array.from({ length: lines }, (_, i) => (
        <span key={i} className="skeleton-line" />
      ))}
    </div>
  )
}
