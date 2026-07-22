import * as O from 'fp-ts/Option'
import { pipe } from 'fp-ts/function'

const TOKEN_KEY = 'br_jwt'
const REFRESH_TOKEN_KEY = 'br_refresh_jwt'
const USER_KEY = 'br_user'

export interface User {
  id: string | number
  first_name: string
  is_admin: boolean
}

export type AuthMode = 'telegram' | 'web' | 'guest'

export function getMode(): AuthMode {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp?.initData) {
    return 'telegram'
  }
  return getStoredToken() ? 'web' : 'guest'
}

export function getStoredToken(): string {
  try {
    return localStorage.getItem(TOKEN_KEY) || ''
  } catch {
    return ''
  }
}

export function getStoredRefreshToken(): string {
  try {
    return localStorage.getItem(REFRESH_TOKEN_KEY) || ''
  } catch {
    return ''
  }
}

export function setStoredToken(token: string, user: User, refreshToken?: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    if (refreshToken) {
      localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    }
  } catch {}
}

export function setStoredAccessToken(token: string): void {
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch {}
}

export function clearStoredToken(): void {
  try {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  } catch {}
}

export function logout(): void {
  clearStoredToken()
  if (typeof window !== 'undefined' && window.Telegram?.WebApp) {
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

export function getTelegramInitData(): string {
  if (typeof window !== 'undefined' && window.Telegram?.WebApp?.initData) {
    return window.Telegram.WebApp.initData
  }
  return ''
}

export function hasTelegramWebApp(): boolean {
  return typeof window !== 'undefined' && !!window.Telegram?.WebApp
}

export function isTelegram(): boolean {
  const initData = getTelegramInitData()
  return !!initData && initData.length > 0
}

export function getAuthHeaders() {
  const headers: Record<string, string> = {}

  // Priority 1: Bearer JWT for stored web/admin sessions
  const token = getStoredToken()
  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  // Priority 2: Supplementary Telegram Init-Data if launched inside TMA
  const initData = getTelegramInitData()
  if (initData) {
    headers['X-Telegram-Init-Data'] = initData
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
  // Backend returns flat: { token, refresh_token, user_id, first_name, is_admin }
  setStoredToken(
    result.token,
    {
      id: result.user_id,
      first_name: result.first_name,
      is_admin: result.is_admin,
    },
    result.refresh_token
  )
  return result
}
