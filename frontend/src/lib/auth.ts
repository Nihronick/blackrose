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
  return !!getTelegramInitData()
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

export function getStoredUser(): O.Option<User> {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return pipe(O.fromNullable(raw), O.map(JSON.parse))
  } catch {
    return O.none
  }
}

export function getAuthHeaders() {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  const initData = getTelegramInitData()
  if (initData) {
    headers['X-Telegram-Init-Data'] = initData
  }
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
  const resp = await fetch(`${base}/api/auth/telegram`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(user),
  })
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}))
    throw new Error(err.message || 'Ошибка авторизации')
  }
  const result = await resp.json()
  setStoredToken(result.token, result.user)
  return result
}
