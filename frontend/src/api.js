const tg = window.Telegram?.WebApp

const BASE =
  import.meta.env.VITE_API_URL ||
  (['localhost', '127.0.0.1'].includes(window.location.hostname)
    ? ''
    : window.location.origin)

export function getInitData() {
  return tg?.initData || ''
}

export async function apiFetch(endpoint) {
  const headers = {}
  const initData = getInitData()
  if (initData) headers['X-Telegram-Init-Data'] = initData

  const res = await fetch(`${BASE}${endpoint}`, { headers })

  if (res.status === 403) {
    const data = await res.json().catch(() => ({}))
    const err = new Error('ACCESS_DENIED')
    err.detail = data.detail
    throw err
  }
  if (!res.ok) throw new Error(`Ошибка ${res.status}`)
  return res.json()
}
