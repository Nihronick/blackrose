import * as E from 'fp-ts/Either'
import * as TE from 'fp-ts/TaskEither'
import { pipe } from 'fp-ts/function'
import { clearStoredToken, getAuthHeaders } from './auth'
import type { ApiResponse, CommentsResponse, IconsGroupedResponse, SubscriptionsResponse, TagsResponse, TopGuidesResponse } from './types'

const BASE = import.meta.env.VITE_API_URL ?? ''

export interface ApiError extends Error {
  detail?: string
}

function throwHttpError(res: Response, data: ApiResponse<unknown>): never {
  if (res.status === 403) {
    const err: ApiError = new Error('ACCESS_DENIED')
    err.detail = typeof data === 'object' && data && 'detail' in data ? data.detail : undefined
    throw err
  }
  const detail =
    typeof data === 'object' && data && 'detail' in data && data.detail != null
      ? String(data.detail)
      : null
  throw new Error(detail ?? `Ошибка ${res.status}`)
}

/**
 * Generic API call helper
 */
async function apiRaw<T>(
  endpoint: string,
  method = 'GET',
  body?: unknown,
  isFormData = false
): Promise<T> {
  const headers = getAuthHeaders()
  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  const options: RequestInit = {
    method,
    headers,
  }

  if (body) {
    options.body = isFormData ? (body as BodyInit) : JSON.stringify(body)
  }

  const res = await fetch(`${BASE}${endpoint}`, options)
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throwHttpError(res, data)
  return data
}

// Basic methods
export const apiFetch = <T>(path: string) => apiRaw<T>(path, 'GET')
export const apiPost = <T>(path: string, body: unknown) => apiRaw<T>(path, 'POST', body)
export const apiPut = <T>(path: string, body: unknown) => apiRaw<T>(path, 'PUT', body)
export const apiDelete = <T>(path: string) => apiRaw<T>(path, 'DELETE')

// TE wrappers
const toTE = <T>(p: Promise<T>): TE.TaskEither<Error, T> =>
  TE.tryCatch(
    () => p,
    (err) => (err instanceof Error ? err : new Error(String(err)))
  )

export const apiFetchTE = <T>(path: string) => toTE<T>(apiFetch<T>(path))
export const apiPostTE = <T>(path: string, body: unknown) => toTE<T>(apiPost<T>(path, body))
export const apiPutTE = <T>(path: string, body: unknown) => toTE<T>(apiPut<T>(path, body))
export const apiDeleteTE = <T>(path: string) => toTE<T>(apiDelete<T>(path))

// Specialized methods
export async function apiSearch(query: string) {
  const q = encodeURIComponent(query.trim())
  return apiFetch<TopGuidesResponse>(`/api/search?q=${q}`)
}

export const apiTopGuides = () => apiFetch<TopGuidesResponse>('/api/top')
export const apiRecentGuides = () => apiFetch<TopGuidesResponse>('/api/recent/guides')
export const apiRecentComments = () => apiFetch<CommentsResponse>('/api/recent/comments')
export const apiGuidesByTag = (tag: string) =>
  apiFetch<TopGuidesResponse>(`/api/tag/${encodeURIComponent(tag)}`)
export const apiRecordView = (guideKey: string) =>
  apiPost<unknown>(`/api/guide/${guideKey}/view`, {})

export async function apiUpload(file: File, folder = 'guides') {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('folder', folder)
  return apiRaw<unknown>('/api/admin/upload', 'POST', fd, true)
}

export const apiImportMedia = (url: string, folder = 'imported') =>
  apiPost<unknown>('/api/admin/media/import', { url, folder })

export const apiSetGuideTags = (key: string, tags: string[]) =>
  apiPut<unknown>(`/api/admin/guide/${key}/tags`, { tags })

export const apiReorderGuides = (items: { key: string; sort_order: number }[]) =>
  apiPost<unknown>('/api/admin/reorder/guides', { items })

export const apiReorderCategories = (items: { key: string; sort_order: number }[]) =>
  apiPost<unknown>('/api/admin/reorder/categories', { items })

export const apiAddComment = (guideKey: string, text: string) =>
  apiPost<unknown>(`/api/guide/${guideKey}/comments`, { text })

export const apiDeleteComment = (guideKey: string, commentId: string | number) =>
  apiDelete<unknown>(`/api/guide/${guideKey}/comments/${commentId}`)

export const apiGetComments = (guideKey: string) =>
  apiFetch<CommentsResponse>(`/api/guide/${guideKey}/comments`)

export const apiIconsGrouped = () => apiFetch<IconsGroupedResponse>('/api/admin/icons/grouped')

export const apiExport = () => apiFetch<unknown>('/api/admin/export')
export const apiImport = (data: unknown) => apiPost<unknown>('/api/admin/import', data)
export const apiGetSubscriptions = () => apiFetch<SubscriptionsResponse>('/api/subscriptions')
export const apiSubscribe = (categoryKey: string) =>
  apiPost<unknown>(`/api/subscriptions/${categoryKey}`, {})
export const apiUnsubscribe = (categoryKey: string) =>
  apiDelete<unknown>(`/api/subscriptions/${categoryKey}`)
export const apiTags = () => apiFetch<TagsResponse>('/api/tags')
export const apiMediaList = () => apiFetch<{ groups: any[], total: number }>('/api/admin/media/list')

/**
 * Returns a proxied URL for Discord media to bypass CORS/expiration.
 * Uses the absolute BASE URL to ensure requests go to the backend.
 */
/**
 * Вспомогательная функция для проксирования ссылок (отключена).
 * Прямые ссылки на Discord CDN отлично работают в тегах <img> и <video> 
 * без CORS-ограничений. Использование прямого подключения решает проблему 
 * с поддержкой Range-запросов для видеоплееров.
 */
export function apiGetProxyUrl(url: string): string {
  return url || ''
}
