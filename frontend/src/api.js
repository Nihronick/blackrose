// Add these functions to your existing api.js

export function getInitData() {
  return window.Telegram?.WebApp?.initData ?? ''
}

const BASE = import.meta.env.VITE_API_URL ?? ''

function getHeaders() {
  const headers = { 'Content-Type': 'application/json' }
  const initData = getInitData()
  if (initData) headers['X-Telegram-Init-Data'] = initData
  return headers
}

export async function apiFetch(endpoint) {
  const res = await fetch(`${BASE}${endpoint}`, { headers: getHeaders() })
  if (res.status === 403) {
    const data = await res.json().catch(() => ({}))
    const err  = new Error('ACCESS_DENIED')
    err.detail = data.detail
    throw err
  }
  if (!res.ok) throw new Error(`Ошибка ${res.status}`)
  return res.json()
}

export async function apiPut(endpoint, body) {
  const res = await fetch(`${BASE}${endpoint}`, {
    method:  'PUT',
    headers: getHeaders(),
    body:    JSON.stringify(body),
  })
  if (res.status === 403) {
    const data = await res.json().catch(() => ({}))
    const err  = new Error('ACCESS_DENIED')
    err.detail = data.detail
    throw err
  }
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail ?? `Ошибка ${res.status}`)
  }
  return res.json()
}

export async function apiDelete(endpoint) {
  const res = await fetch(`${BASE}${endpoint}`, {
    method:  'DELETE',
    headers: getHeaders(),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail ?? `Ошибка ${res.status}`)
  }
  return res.json()
}

export async function apiSearch(query) {
  const q = encodeURIComponent(query.trim())
  return apiFetch(`/api/search?q=${q}`)
}

export async function apiIconsGrouped() {
  return apiFetch('/api/admin/icons/grouped')
}

export async function apiPost(endpoint, body) {
  const res = await fetch(`${BASE}${endpoint}`, {
    method:  'POST',
    headers: getHeaders(),
    body:    JSON.stringify(body),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error(data.detail ?? `Ошибка ${res.status}`)
  }
  return res.json()
}

export async function apiReorderGuides(order) {
  return apiPost('/api/admin/reorder/guides', { order })
}

export async function apiReorderCategories(order) {
  return apiPost('/api/admin/reorder/categories', { order })
}

export async function apiExport() {
  const res = await fetch(`${BASE}/api/admin/export`, { headers: getHeaders() })
  if (!res.ok) throw new Error(`Ошибка ${res.status}`)
  return res.json()
}

export async function apiImport(data) {
  return apiPost('/api/admin/import', data)
}

export async function apiGuideHistory(key) {
  return apiFetch(`/api/admin/guide/${key}/history`)
}

// ── Views ────────────────────────────────────────────────────
export async function apiRecordView(key) {
  const res = await fetch(`${BASE}/api/guide/${key}/view`, { method: 'POST', headers: getHeaders() })
  if (!res.ok) return
  return res.json()
}

export async function apiTopGuides() {
  return apiFetch('/api/top')
}

// ── Tags ─────────────────────────────────────────────────────
export async function apiTags() {
  return apiFetch('/api/tags')
}

export async function apiGuidesByTag(tag) {
  return apiFetch(`/api/tag/${encodeURIComponent(tag)}`)
}

export async function apiSetGuideTags(key, tags) {
  return apiPut(`/api/admin/guide/${key}/tags`, { tags })
}

// ── Comments ─────────────────────────────────────────────────
export async function apiGetComments(key) {
  return apiFetch(`/api/guide/${key}/comments`)
}

export async function apiAddComment(key, text) {
  return apiPost(`/api/guide/${key}/comments`, { text })
}

export async function apiDeleteComment(guideKey, commentId) {
  return apiDelete(`/api/guide/${guideKey}/comments/${commentId}`)
}

// ── Subscriptions ─────────────────────────────────────────────
export async function apiGetSubscriptions() {
  return apiFetch('/api/subscriptions')
}

export async function apiSubscribe(categoryKey) {
  const res = await fetch(`${BASE}/api/subscriptions/${categoryKey}`, { method: 'POST', headers: getHeaders() })
  if (!res.ok) throw new Error(`Ошибка ${res.status}`)
  return res.json()
}

export async function apiUnsubscribe(categoryKey) {
  return apiDelete(`/api/subscriptions/${categoryKey}`)
}
