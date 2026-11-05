import type { ReactNode } from 'react'

export type NoticeTone = 'info' | 'wait' | 'problem'

interface Props {
  tone: NoticeTone
  children: ReactNode
  action?: { label: string; onClick: () => void; disabled?: boolean }
}

/** A calm inline status line: loading, empty, waiting, or a friendly failure. */
export function Notice({ tone, children, action }: Props) {
  return (
    <div className={`notice notice-${tone}`} role={tone === 'problem' ? 'alert' : 'status'}>
      <p>{children}</p>
      {action && (
        <button
          type="button"
          className="button button-quiet"
          onClick={action.onClick}
          disabled={action.disabled}
        >
          {action.label}
        </button>
      )}
    </div>
  )
}
