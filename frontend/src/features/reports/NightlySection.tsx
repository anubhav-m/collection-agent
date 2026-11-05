import type { ReportsResponse } from '../../api/types'
import { LoadState } from './LoadState'
import { NoteMark } from './NoteMark'
import type { ReportNote } from './notes'
import { ProjectReport } from './ProjectReport'
import { SimulatedReport } from './SimulatedReport'
import type { Loaded } from './useLoad'

interface Props {
  project: Loaded<ReportsResponse>
  simulated: Loaded<ReportsResponse>
  notes: ReportNote[]
}

const NO_RUN = 'No successful nightly run has produced this report yet.'

export function NightlySection({ project, simulated, notes }: Props) {
  return (
    <section className="results-section" aria-labelledby="nightly-title">
      <h2 id="nightly-title" className="section-title">
        Nightly reports
      </h2>
      <p className="muted section-lede">
        The nightly job extracts promises from stored chats, loads them into SQLite and runs the
        follow-up and escalation reports.
      </p>
      <h3 className="subsection-title">
        From this project's stored conversations
        <NoteMark notes={notes} cite="nightly-project" />
      </h3>
      <LoadState load={project} what="project report" isEmpty={() => false} empty={NO_RUN}>
        {(data) => <ProjectReport data={data} />}
      </LoadState>
      <h3 className="subsection-title">
        Simulated history, for scale testing only
        <NoteMark notes={notes} cite="nightly-simulated" />
      </h3>
      <LoadState load={simulated} what="simulated report" isEmpty={() => false} empty={NO_RUN}>
        {(data) => <SimulatedReport data={data} />}
      </LoadState>
    </section>
  )
}
