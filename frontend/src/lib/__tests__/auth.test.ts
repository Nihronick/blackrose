import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { getAuthHeaders, getMode, getStoredToken, setStoredToken, clearStoredToken, getStoredUser } from '../auth'
import * as O from 'fp-ts/Option'

/**
 * Тесты для auth.ts — модуль авторизации.
 *
 * Проверяет:
 * - getAuthHeaders: правильные заголовки для каждого режима
 * - getMode: определение режима (telegram/web/guest)
 * - localStorage: сохранение/чтение/удаление токена и user
 * - BUG-3: Content-Type в getAuthHeaders ломает FormData uploads
 */

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value }),
    removeItem: vi.fn((key: string) => { delete store[key] }),
    clear: vi.fn(() => { store = {} }),
    get length() { return Object.keys(store).length },
    key: vi.fn((i: number) => Object.keys(store)[i] ?? null),
  }
})()

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Mock Telegram WebApp
const originalTelegram = window.Telegram

describe('Auth module - localStorage operations', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
    // Remove Telegram WebApp mock
    Object.defineProperty(window, 'Telegram', { value: undefined, writable: true, configurable: true })
  })

  afterEach(() => {
    Object.defineProperty(window, 'Telegram', { value: originalTelegram, writable: true, configurable: true })
  })

  it('getStoredToken returns empty string when no token', () => {
    expect(getStoredToken()).toBe('')
  })

  it('setStoredToken saves token and user', () => {
    setStoredToken('test-jwt-token', {
      id: 123,
      first_name: 'Test',
      is_admin: false,
    })
    expect(getStoredToken()).toBe('test-jwt-token')
  })

  it('clearStoredToken removes token and user', () => {
    setStoredToken('token', { id: 1, first_name: 'User', is_admin: false })
    clearStoredToken()
    expect(getStoredToken()).toBe('')
  })

  it('getStoredUser returns None when no user', () => {
    const user = getStoredUser()
    expect(O.isNone(user)).toBe(true)
  })

  it('getStoredUser returns Some(user) after setStoredToken', () => {
    setStoredToken('token', { id: 42, first_name: 'Admin', is_admin: true })
    const user = getStoredUser()
    expect(O.isSome(user)).toBe(true)
    if (O.isSome(user)) {
      expect(user.value.id).toBe(42)
      expect(user.value.first_name).toBe('Admin')
      expect(user.value.is_admin).toBe(true)
    }
  })
})

describe('Auth module - getMode', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
  })

  it('returns "guest" when no telegram and no token', () => {
    Object.defineProperty(window, 'Telegram', { value: undefined, writable: true, configurable: true })
    expect(getMode()).toBe('guest')
  })

  it('returns "web" when JWT token exists', () => {
    Object.defineProperty(window, 'Telegram', { value: undefined, writable: true, configurable: true })
    setStoredToken('some-token', { id: 1, first_name: 'User', is_admin: false })
    expect(getMode()).toBe('web')
  })

  it('returns "telegram" when Telegram WebApp exists', () => {
    Object.defineProperty(window, 'Telegram', {
      value: { WebApp: { initData: 'user=%7B%22id%22%3A1%7D&hash=abc' } },
      writable: true,
      configurable: true,
    })
    expect(getMode()).toBe('telegram')
  })
})

describe('Auth module - getAuthHeaders', () => {
  beforeEach(() => {
    localStorageMock.clear()
    vi.clearAllMocks()
    Object.defineProperty(window, 'Telegram', { value: undefined, writable: true, configurable: true })
  })

  it('does not set Content-Type (BUG-3 fixed)', () => {
    const headers = getAuthHeaders()
    // BUG-3 FIXED: getAuthHeaders no longer sets Content-Type.
    // Content-Type is now only set in apiRaw() for non-FormData requests.
    expect(headers['Content-Type']).toBeUndefined()
  })

  it('includes Authorization header when JWT token exists', () => {
    setStoredToken('jwt-token-123', { id: 1, first_name: 'User', is_admin: false })
    const headers = getAuthHeaders()
    expect(headers['Authorization']).toBe('Bearer jwt-token-123')
  })

  it('includes X-Telegram-Init-Data when in Telegram', () => {
    Object.defineProperty(window, 'Telegram', {
      value: { WebApp: { initData: 'test-init-data-string' } },
      writable: true,
      configurable: true,
    })
    const headers = getAuthHeaders()
    expect(headers['X-Telegram-Init-Data']).toBe('test-init-data-string')
  })

  it('does not include Authorization when no token', () => {
    const headers = getAuthHeaders()
    expect(headers['Authorization']).toBeUndefined()
  })

  it('does not include X-Telegram-Init-Data when not in Telegram', () => {
    const headers = getAuthHeaders()
    expect(headers['X-Telegram-Init-Data']).toBeUndefined()
  })
})
