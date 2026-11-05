import type { ApiErrorBody } from './types'

export type ApiErrorKind =
  'rate_limited' | 'daily_limit' | 'not_found' | 'invalid' | 'unavailable' | 'network'

const FRIENDLY: Record<ApiErrorKind, string> = {
  rate_limited: "You're sending messages quickly. Please wait a moment and try again.",
  daily_limit:
    'This demo has reached its daily limit on assistant replies. Please come back tomorrow.',
  not_found: "We couldn't find that. It may not exist yet.",
  invalid: "That request couldn't be sent. Please check it and try again.",
  unavailable: 'The service is having trouble right now. Please try again shortly.',
  network: "We couldn't reach the server. Check your connection and try again.",
}

/** A request failure safe to show to people: a kind, a friendly message, and a wait hint. */
export class ApiError extends Error {
  readonly kind: ApiErrorKind
  readonly retryAfterSeconds: number | null

  constructor(kind: ApiErrorKind, message: string, retryAfterSeconds: number | null = null) {
    super(message)
    this.kind = kind
    this.retryAfterSeconds = retryAfterSeconds
  }
}

/** Any thrown value as an ApiError, so callers only ever show friendly messages. */
export function toApiError(failure: unknown): ApiError {
  return failure instanceof ApiError ? failure : new ApiError('unavailable', FRIENDLY.unavailable)
}

function kindFor(status: number, code: string | undefined): ApiErrorKind {
  if (code === 'daily_limit_reached') return 'daily_limit'
  if (status === 429) return 'rate_limited'
  if (status === 404) return 'not_found'
  if (status === 422 || status === 400) return 'invalid'
  return 'unavailable'
}

async function errorFrom(response: Response): Promise<ApiError> {
  let body: ApiErrorBody | null = null
  try {
    body = (await response.json()) as ApiErrorBody
  } catch {
    body = null // a proxy or crash page with no JSON body still gets a friendly message
  }
  const kind = kindFor(response.status, body?.error?.code)
  // Only the backend's own limit messages are shown verbatim; they are written for people.
  const message = kind === 'daily_limit' && body ? body.error.message : FRIENDLY[kind]
  const retry = Number(response.headers.get('Retry-After'))
  return new ApiError(kind, message, Number.isFinite(retry) && retry > 0 ? retry : null)
}

export async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(path, {
      ...init,
      headers: { 'Content-Type': 'application/json', ...init?.headers },
    })
  } catch {
    throw new ApiError('network', FRIENDLY.network)
  }
  if (!response.ok) throw await errorFrom(response)
  return (await response.json()) as T
}
