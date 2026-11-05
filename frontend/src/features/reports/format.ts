const percent = new Intl.NumberFormat('en-US', { style: 'percent', maximumFractionDigits: 1 })
const count = new Intl.NumberFormat('en-US')

/** A 0–1 rate as a percentage, for example 0.974 → "97.4%". */
export const pct = (rate: number) => percent.format(rate)

/** A value already in percent units, for example 69.1 → "69.1%". */
export const pctUnits = (value: number) => `${value.toFixed(1)}%`

export const int = (value: number) => count.format(value)

export const shortDate = (iso: string) => iso.slice(0, 10)

export const label = (code: string) =>
  code.replaceAll('_', ' ').replace(/^./, (first) => first.toUpperCase())

/** The evaluation runs are named baseline and latest; show what they mean. */
export const runLabel = (run: { run_name: string }) =>
  run.run_name === 'latest' ? 'After fixes' : 'Baseline'
