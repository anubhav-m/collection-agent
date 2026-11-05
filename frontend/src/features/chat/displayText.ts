// Model replies sometimes carry Markdown emphasis. Messages are shown as plain text, so the
// markers are removed rather than rendered; nothing here ever produces HTML.
const EMPHASIS = /(\*\*|__)(.+?)\1/g
const CODE = /`([^`]+)`/g

export function displayText(text: string): string {
  return text.replace(EMPHASIS, '$2').replace(CODE, '$1')
}
