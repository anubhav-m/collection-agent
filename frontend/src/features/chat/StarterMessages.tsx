interface Props {
  starters: string[]
  disabled: boolean
  onPick: (text: string) => void
}

export function StarterMessages({ starters, disabled, onPick }: Props) {
  return (
    <div className="starters" role="group" aria-label="Starter messages">
      {starters.map((text) => (
        <button
          key={text}
          type="button"
          className="starter"
          disabled={disabled}
          onClick={() => onPick(text)}
        >
          {text}
        </button>
      ))}
    </div>
  )
}
