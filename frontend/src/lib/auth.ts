import * as O from 'fp-ts/Option'
import { pipe } from 'fp-ts/function'

const TOKEN_KEY = 'br_jwt'
const USER_KEY = 'br_user'

export interface User {
  id: string | number
  first_name: string
  is_admin: boolean
}

export type AuthMode = 'telegram' | 'web' | 'guest'

export function getTelegramInitData(): string {
  const initData = window.Telegram?.WebApp?.initData
  return typeof initData === 'string' ? initData : ''
}

export function hasTelegramWebApp(): boolean {
  return !!window.Telegram?.WebApp
}

export function getMode(): AuthMode {
  if (hasTelegramWebApp()) return 'telegram'
  if (getStoredToken()) return 'web'
  return 'guest'
}

export function isTelegram(): boolean {
  const initData = getTelegramInitData()
  return !!initData && initData.length > 0
}

export function getStoredToken(): string {
  try {
    return localStorage.getItem(TOKEN_KEY) || ''
  } catch {
    return ''
  }
}

export function setStoredToken(token: string, user: User): void {
  try {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  } catch {}
}

export function clearStoredToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  } catch {}
}

export function logout(): void {
  clearStoredToken()
  if (window.Telegram?.WebApp) {
    // В TMA выход = закрытие приложения
    window.Telegram.WebApp.close()
  } else {
    // В вебе просто рефреш для сброса стейта
    window.location.href = '/'
  }
}

export function getStoredUser(): O.Option<User> {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return pipe(O.fromNullable(raw), O.map(JSON.parse))
  } catch {
    return O.none
  }
}

export function getAuthHeaders() {
  const headers: Record<string, string> = {}
  const initData = getTelegramInitData()

  // Приоритет 1: Мы в Telegram Mini App
  if (initData) {
    headers['X-Telegram-Init-Data'] = initData
    return headers
  }

  // Приоритет 2: Мы в обычном браузере с JWT
  const token = getStoredToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  return headers
}
interface TelegramUser {
  id: number
  first_name: string
  last_name?: string
  username?: string
  photo_url?: string
  auth_date: number
  hash: string
}

export async function handleTelegramLogin(user: TelegramUser, base: string) {
  const resp = await fetch(`${base}/api/auth/web-login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}))
    throw new Error(err.detail || err.message || 'Ошибка авторизации')
  }
  const result = await resp.json()
  // Backend returns flat: { token, user_id, first_name, is_admin }
  setStoredToken(result.token, {
    id: result.user_id,
    first_name: result.first_name,
    is_admin: result.is_admin,
  })
  return result
}
