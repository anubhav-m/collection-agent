import { refusalLabel } from './labels'
import type { ToolEntry } from './turns'

function verdict(tool: ToolEntry): { text: string; tone: string } {
  if (tool.accepted === null) return { text: 'No result stored', tone: 'muted' }
  if (tool.accepted) return { text: 'Allowed', tone: 'state-ok' }
  return { text: `Refused: ${refusalLabel(tool.reason ?? 'unknown')}`, tone: 'state-handoff' }
}

function argsText(args: Record<string, unknown>): string {
  const entries = Object.entries(args)
  if (entries.length === 0) return 'no arguments'
  return entries.map(([key, value]) => `${key}: ${JSON.stringify(value)}`).join('\n')
}

interface Props {
  tool: ToolEntry
}

/** One requested tool call and what the server did with it. Refusals stay visible. */
export function ToolCallEntry({ tool }: Props) {
  const { text, tone } = verdict(tool)
  return (
    <li className="tool">
      <div className="tool-head">
        <code className="tool-name">{tool.name}</code>
        <span className={`tool-verdict ${tone}`}>{text}</span>
      </div>
      <pre className="tool-args data">{argsText(tool.args)}</pre>
      {tool.result && (
        <details className="tool-result">
          <summary className="small">Result sent to the model</summary>
          <pre className="data">{JSON.stringify(tool.result, null, 2)}</pre>
        </details>
      )}
    </li>
  )
}
