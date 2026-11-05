interface Props {
  target: string
  label: string
  children: string | number
}

/** A superscript reference that jumps to its source entry, which highlights via :target. */
export function FootnoteMark({ target, label, children }: Props) {
  return (
    <sup className="fn">
      <a href={`#${target}`} aria-label={label}>
        {children}
      </a>
    </sup>
  )
}
