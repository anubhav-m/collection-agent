import { FootnoteMark } from '../../components/FootnoteMark'
import { noteFor, type ReportNote } from './notes'

interface Props {
  notes: ReportNote[]
  cite: string
}

/** The footnote mark for one cited report file, or nothing if that file is missing. */
export function NoteMark({ notes, cite }: Props) {
  const note = noteFor(notes, cite)
  if (!note) return null
  return (
    <FootnoteMark target={`note-${note.n}`} label={`Source ${note.n}: ${note.path}`}>
      {note.n}
    </FootnoteMark>
  )
}
