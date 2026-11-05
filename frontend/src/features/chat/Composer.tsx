import { useState, type FormEvent, type KeyboardEvent } from 'react'

const MAX_LENGTH = 2000 // matches ChatRequest.message max_length in backend/app/api/schemas.py

interface Props {
  disabled: boolean
  onSend: (text: string) => void
}

export function Composer({ disabled, onSend }: Props) {
  const [text, setText] = useState('')
  const empty = text.trim().length === 0

  function submit(event?: FormEvent) {
    event?.preventDefault()
    if (disabled || empty) return
    onSend(text)
    setText('')
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    // Enter sends; Shift+Enter keeps a new line.
    if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) submit(event)
  }

  return (
    <form className="composer" onSubmit={submit}>
      <label htmlFor="composer-input" className="visually-hidden">
        Message
      </label>
      <textarea
        id="composer-input"
        className="composer-input"
        rows={2}
        maxLength={MAX_LENGTH}
        placeholder="Write a message as the borrower"
        value={text}
        onChange={(event) => setText(event.target.value)}
        onKeyDown={onKeyDown}
        aria-describedby="composer-hint"
      />
      <div className="composer-row">
        <p id="composer-hint" className="small muted">
          Enter to send, Shift+Enter for a new line · {text.length}/{MAX_LENGTH}
        </p>
        <button type="submit" className="button" disabled={disabled || empty}>
          Send
        </button>
      </div>
    </form>
  )
}
