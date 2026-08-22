import * as E from 'fp-ts/Either'
import * as TE from 'fp-ts/TaskEither'
import { pipe } from 'fp-ts/function'
import {
  clearStoredToken,
  getAuthHeaders,
  getStoredRefreshToken,
  sanitizeHeaderValue,
  setStoredAccessToken,
  setStoredRefreshToken,
} from './auth'
import type {
  ApiResponse,
  CategoriesResponse,
  CommentsResponse,
  Guild,
  GuildJoinRequest,
  GuildMember,
  GuildRosterResponse,
  GuildStatusOption,
  IconsGroupedResponse,
  MediaListResponse,
  SubscriptionsResponse,
  TagsResponse,
  TopGuidesResponse,
} from './types'

const BASE = import.meta.env.VITE_API_URL ?? ''

export interface ApiError extends Error {
  detail?: string
}

function throwHttpError(res: Response, data: ApiResponse<unknown>): never {
  if (res.status === 403) {
    const err: ApiError = new Error('ACCESS_DENIED')
    err.detail =
      typeof data === 'object' && data && 'detail' in data
        ? Array.isArray(data.detail)
          ? data.detail.join(', ')
          : String(data.detail)
        : undefined
    throw err
  }

  let detail: string | null = null
  if (typeof data === 'object' && data && 'detail' in data && data.detail != null) {
    if (Array.isArray(data.detail)) {
      // Handle FastAPI validation error lists
      detail = data.detail
        .map((d) => (typeof d === 'object' ? d.msg || JSON.stringify(d) : String(d)))
        .join(', ')
    } else {
      detail = String(data.detail)
    }
  }

  throw new Error(detail ?? `Ошибка ${res.status}`)
}

function sanitizeHeaders(headers: Record<string, string>): Record<string, string> {
  const clean: Record<string, string> = {}
  for (const [key, value] of Object.entries(headers)) {
    if (value == null) continue
    clean[key] = sanitizeHeaderValue(String(value))
  }
  return clean
}

// ── Circuit Breaker State ─────────────────────────────────────────
class CircuitBreaker {
  private failures = 0
  private lastFailureTime = 0
  private readonly threshold: number
  private readonly resetTimeout: number
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED'

  constructor(threshold = 5, resetTimeout = 10000) {
    this.threshold = threshold
    this.resetTimeout = resetTimeout
  }

  canRequest(): boolean {
    if (this.state === 'CLOSED') return true
    if (this.state === 'OPEN') {
      const now = Date.now()
      if (now - this.lastFailureTime > this.resetTimeout) {
        this.state = 'HALF_OPEN'
        return true
      }
      return false
    }
    return true // HALF_OPEN
  }

  recordSuccess() {
    this.failures = 0
    this.state = 'CLOSED'
  }

  recordFailure() {
    this.failures++
    this.lastFailureTime = Date.now()
    if (this.failures >= this.threshold) {
      this.state = 'OPEN'
    }
  }

  getState() {
    return this.state
  }
}

export const apiCircuitBreaker = new CircuitBreaker(5, 10000)

/**
 * Calculates exponential backoff with full jitter to avoid thundering herds.
 */
function getExponentialBackoffDelay(attempt: number, baseDelay = 300, maxDelay = 3000): number {
  const exponential = Math.min(maxDelay, baseDelay * 2 ** attempt)
  const jitter = Math.random() * (exponential * 0.5)
  return exponential + jitter
}

/**
 * Generic API call helper with Circuit Breaker, Exponential Backoff, Idempotency and Timeouts.
 */
async function apiRaw<T>(
  endpoint: string,
  method = 'GET',
  body?: unknown,
  isFormData = false,
  hasRetried = false,
  attempt = 0
): Promise<T> {
  if (!apiCircuitBreaker.canRequest() && method === 'GET') {
    throw new Error('CIRCUIT_OPEN: Сервер временно недоступен. Используется локальный кэш.')
  }

  const headers = sanitizeHeaders(getAuthHeaders())
  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }

  // Idempotency key for mutations
  if (method !== 'GET' && !headers['X-Idempotency-Key']) {
    headers['X-Idempotency-Key'] = `req_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
  }

  // Request timeout protection (15 seconds)
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 15000)

  const options: RequestInit = {
    method,
    headers,
    signal: controller.signal,
  }

  if (body) {
    options.body = isFormData ? (body as BodyInit) : JSON.stringify(body)
  }

  // Warmup timer for HF Free Spaces cold starts (>2.5s)
  const warmupTimer = setTimeout(() => {
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('hf_space_warmup', { detail: { warming: true } }))
    }
  }, 2500)

  let res: Response
  try {
    res = await fetch(`${BASE}${endpoint}`, options)
    clearTimeout(timeoutId)
    apiCircuitBreaker.recordSuccess()
  } catch (err) {
    clearTimeout(timeoutId)
    apiCircuitBreaker.recordFailure()

    // Retry policy: Exponential backoff with jitter on network glitches or 5xx/429
    if (attempt < 2 && (method === 'GET' || method === 'HEAD')) {
      const delay = getExponentialBackoffDelay(attempt)
      await new Promise((resolve) => setTimeout(resolve, delay))
      return apiRaw<T>(endpoint, method, body, isFormData, true, attempt + 1)
    }
    throw err
  } finally {
    clearTimeout(warmupTimer)
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('hf_space_warmup', { detail: { warming: false } }))
    }
  }

  // Silent refresh flow on 401.
  if (res.status === 401 && !hasRetried && !endpoint.includes('/api/auth/refresh')) {
    const refreshToken = getStoredRefreshToken()
    if (refreshToken) {
      const refreshRes = await fetch(`${BASE}/api/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
      if (refreshRes.ok) {
        const refreshData = (await refreshRes.json()) as { token?: string; refresh_token?: string }
        if (refreshData?.token) {
          setStoredAccessToken(refreshData.token)
          if (refreshData.refresh_token) {
            setStoredRefreshToken(refreshData.refresh_token)
          }
          return apiRaw<T>(endpoint, method, body, isFormData, true, attempt)
        }
      } else {
        clearStoredToken()
      }
    }
  }

  // Auto-retry 502/503/504 Bad Gateway / Cold Starts with backoff (only once if not retried)
  if (res && (res.status === 502 || res.status === 503 || res.status === 504 || res.status === 429) && !hasRetried && attempt < 1 && method === 'GET') {
    apiCircuitBreaker.recordFailure()
    const delay = getExponentialBackoffDelay(attempt, 200, 2000)
    await new Promise((resolve) => setTimeout(resolve, delay))
    const retryRes = await apiRaw<T>(endpoint, method, body, isFormData, true, attempt + 1).catch(() => null)
    if (retryRes !== null) return retryRes
  }

  const data = res?.json ? await res.json().catch(() => ({})) : {}
  if (!res || !res.ok) {
    if (res?.status && res.status >= 500) {
      apiCircuitBreaker.recordFailure()
    }
    throwHttpError(res, data)
  }
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
  apiPost<unknown>('/api/admin/reorder/guides', { order: items })

export const apiReorderCategories = (items: { key: string; sort_order: number }[]) =>
  apiPost<unknown>('/api/admin/reorder/categories', { order: items })

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
export const apiMediaList = () => apiFetch<MediaListResponse>('/api/admin/media/list')

export const apiGetCategories = () => apiFetch<CategoriesResponse>('/api/categories')
export const apiEmergencyLogin = (emergencyKey: string) =>
  apiPost<{ token: string; ok: boolean }>('/api/auth/emergency-login', {
    emergency_key: emergencyKey,
  })

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

// --- Guild API ---
export const apiGuilds = () => apiFetch<{ guilds: Guild[] }>('/api/guilds')
export const apiGuildRoster = (id: number) =>
  apiFetch<GuildRosterResponse>(`/api/guilds/${id}/roster`)
export const apiGuildStatuses = (id: number) =>
  apiFetch<{ statuses: GuildStatusOption[] }>(`/api/guilds/${id}/statuses`)
export const apiMyGuildProfile = () =>
  apiFetch<{ profile: GuildMember | null }>('/api/guilds/my/profile')
export const apiUpdateMyGuildProfile = (data: { nickname: string; stage: number }) =>
  apiPut<unknown>('/api/guilds/my/profile', data)
export const apiJoinGuild = (data: { guild_id: number; nickname: string; message?: string }) =>
  apiPost<unknown>('/api/guilds/join', data)
export const apiGuildRequests = (guildId: number) =>
  apiFetch<{ requests: GuildJoinRequest[] }>(`/api/guilds/${guildId}/requests`)
export const apiApproveGuildRequest = (id: number) =>
  apiPost<unknown>(`/api/guilds/requests/${id}/approve`, {})
export const apiRejectGuildRequest = (id: number) =>
  apiPost<unknown>(`/api/guilds/requests/${id}/reject`, {})
export const apiUpdateGuildMember = (id: number, data: Record<string, unknown>) =>
  apiPut<unknown>(`/api/guilds/members/${id}`, data)
export const apiRemoveGuildMember = (id: number) => apiDelete<unknown>(`/api/guilds/members/${id}`)
export const apiAdminCreateGuild = (data: {
  name: string
  icon_url?: string
  description?: string
  max_members?: number
}) => apiPost<unknown>('/api/admin/guilds', data)
export const apiAdminUpdateGuild = (id: number, data: Record<string, unknown>) =>
  apiPut<unknown>(`/api/admin/guilds/${id}`, data)
export const apiAdminDeleteGuild = (id: number) => apiDelete<unknown>(`/api/admin/guilds/${id}`)
export const apiUpdateGuildSettings = (
  id: number,
  data: { name?: string; icon_url?: string; description?: string }
) => apiPut<{ ok: boolean }>(`/api/guilds/${id}/settings`, data)

// --- Discord Sync API ---
export const apiGetDiscordSyncStatus = () =>
  apiFetch<{
    running: boolean
    channels_count: number
    has_token: boolean
    has_saved_token?: boolean
    token_preview?: string | null
  }>('/api/admin/discord-sync/status')
export const apiStartDiscordSync = (user_token: string) =>
  apiPost<{ ok: boolean; message: string }>('/api/admin/discord-sync/start', { user_token })
export const apiStopDiscordSync = () =>
  apiPost<{ ok: boolean; message: string }>('/api/admin/discord-sync/stop', {})
export const apiGetDiscordSyncChannels = () =>
  apiFetch<{
    channels: Array<{
      channel_id: string
      channel_name?: string
      category_key: string
      auto_translate: boolean
      is_active: boolean
    }>
  }>('/api/admin/discord-sync/channels')
export const apiAddDiscordSyncChannel = (data: {
  channel_id: string
  category_key: string
  channel_name?: string
  auto_translate?: boolean
}) => apiPost<{ ok: boolean; channel: unknown }>('/api/admin/discord-sync/channels', data)
export const apiRemoveDiscordSyncChannel = (channel_id: string) =>
  apiDelete<{ ok: boolean }>(`/api/admin/discord-sync/channels/${channel_id}`)
export const apiGetSyncedDiscordGuides = () =>
  apiFetch<{
    synced_guides: Array<{
      id: number
      discord_message_id: string
      discord_channel_id: string
      guide_key: string
      author_tag: string
      created_at: string
      title: string
      category_key: string
      views: number
    }>
  }>('/api/admin/discord-sync/synced-guides')
export const apiDeleteSyncedDiscordGuide = (id: number, deleteGuide = false) =>
  apiDelete<{ ok: boolean; message: string }>(
    `/api/admin/discord-sync/synced-guides/${id}?delete_guide=${deleteGuide}`
  )
export const apiClearSyncedDiscordGuides = (deleteGuides = false) =>
  apiPost<{ ok: boolean; message: string }>(
    `/api/admin/discord-sync/synced-guides/clear?delete_guides=${deleteGuides}`,
    {}
  )
export const apiBackfillDiscordChannel = (channel_id: string) =>
  apiPost<{ ok: boolean; message: string }>(
    `/api/admin/discord-sync/channels/${channel_id}/backfill`,
    {}
  )
export const apiBackfillAllDiscordChannels = () =>
  apiPost<{ ok: boolean; message: string }>('/api/admin/discord-sync/backfill-all', {})
export const apiImportDiscordLink = (link: string) =>
  apiPost<{ ok: boolean; message: string }>('/api/admin/discord-sync/import-link', { link })

// --- User Management API ---
export interface AdminUserItem {
  user_id: number
  username?: string
  first_name?: string
  role: string
  is_active: boolean
  created_at?: string
}

export const apiGetAdminUsers = (query?: string) =>
  apiFetch<{ total: number; users: AdminUserItem[] }>(
    `/api/admin/users${query ? `?query=${encodeURIComponent(query)}` : ''}`
  )
export const apiUpdateUserRole = (userId: number, role: string) =>
  apiPut<{ ok: boolean }>(`/api/admin/users/${userId}/role`, { role })
export const apiToggleUserStatus = (userId: number, isActive: boolean) =>
  apiPut<{ ok: boolean }>(`/api/admin/users/${userId}/status`, { is_active: isActive })
export const apiUploadMediaFile = (file: File) => {
  const fd = new FormData()
  fd.append('file', file)
  return apiRaw<{ ok: boolean; url: string; filename: string }>(
    '/api/admin/media/upload',
    'POST',
    fd,
    true
  )
}
export const apiExportFullBackup = () => apiFetch<unknown>('/api/admin/backup/export')

// --- GDPR & 152-ФЗ Compliance API ---
export const apiExportUserData = () => apiFetch<Record<string, unknown>>('/api/user/me/export')
export const apiDeleteUserData = () => apiDelete<{ deleted: boolean; message: string }>('/api/user/me')
export const apiGetPrivacyPolicy = () => apiFetch<Record<string, unknown>>('/api/legal/privacy')

// --- SLO & Feature Flags API ---
export const apiGetSloMetrics = () => apiFetch<Record<string, unknown>>('/api/slo')
export const apiGetFeatureFlags = () => apiFetch<Record<string, boolean>>('/api/features')

