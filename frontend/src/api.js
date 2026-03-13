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
