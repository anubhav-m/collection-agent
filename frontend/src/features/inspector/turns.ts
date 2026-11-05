import type { EventView } from '../../api/types'

export interface ToolEntry {
  key: string
  name: string
  args: Record<string, unknown>
  accepted: boolean | null // null while no result was stored for the call
  reason: string | null
  result: Record<string, unknown> | null
}

export interface Turn {
  n: number
  userText: string
  tools: ToolEntry[]
  escalation: { reason: string; source: string } | null
}

/** Group the stored event log into numbered turns, pairing each tool call with its result. */
export function toTurns(events: EventView[]): Turn[] {
  const turns: Turn[] = []
  let pending: ToolEntry[] = [] // calls requested in this turn that have no result yet
  for (const event of events) {
    if (event.kind === 'user') {
      turns.push({ n: turns.length + 1, userText: event.text ?? '', tools: [], escalation: null })
      pending = []
      continue
    }
    const turn = turns.at(-1)
    if (!turn) continue
    if (event.kind === 'tool_call') {
      for (const call of event.tool_calls) {
        const entry: ToolEntry = {
          key: `${turn.n}-${turn.tools.length}`,
          name: call.name,
          args: call.args,
          accepted: null,
          reason: null,
          result: null,
        }
        turn.tools.push(entry)
        pending.push(entry)
      }
    } else if (event.kind === 'tool_result') {
      const index = pending.findIndex((t) => t.name === event.tool_name)
      if (index === -1) continue
      const [entry] = pending.splice(index, 1)
      entry.accepted = event.accepted
      entry.reason = event.reason
      entry.result = event.result
    } else if (event.kind === 'escalation') {
      turn.escalation = {
        reason: event.reason ?? 'other',
        source: (event.text ?? '').replace('source=', ''),
      }
    }
  }
  return turns
}
