import { describe, it, expect, vi, beforeEach } from 'vitest'

/**
 * Тесты для api.ts — API клиент.
 *
 * Проверяет:
 * - apiRaw: правильное построение запросов
 * - Error handling: парсинг ошибок от backend
 * - FormData uploads: BUG-3 — Content-Type не должен overrideить multipart
 * - apiSearch: URL encoding
 * - apiGetProxyUrl: возвращает url as-is
 */

// Mock fetch globally
const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

// Mock auth module
vi.mock('../auth', () => ({
  getAuthHeaders: () => ({}), // BUG-3 fixed: no Content-Type here
  clearStoredToken: vi.fn(),
  getTelegramInitData: () => '',
  getStoredToken: () => '',
  hasTelegramWebApp: () => false,
}))

import {
  apiFetch,
  apiPost,
  apiDelete,
  apiSearch,
  apiGetProxyUrl,
  apiUpload,
} from '../api'

describe('API module - basic operations', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('apiFetch sends GET request with correct path', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ categories: [] }),
    })

    await apiFetch('/api/categories')

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/categories'),
      expect.objectContaining({ method: 'GET' })
    )
  })

  it('apiPost sends POST with JSON body', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ ok: true }),
    })

    await apiPost('/api/guide/test/view', { some: 'data' })

    const [, options] = mockFetch.mock.calls[0]
    expect(options.method).toBe('POST')
    expect(JSON.parse(options.body as string)).toEqual({ some: 'data' })
  })

  it('apiDelete sends DELETE request', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ ok: true }),
    })

    await apiDelete('/api/admin/guide/test')

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/admin/guide/test'),
      expect.objectContaining({ method: 'DELETE' })
    )
  })
})

describe('API module - error handling', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('throws ACCESS_DENIED for 403', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 403,
      json: () => Promise.resolve({ detail: 'Forbidden' }),
    })

    await expect(apiFetch('/api/admin/guides')).rejects.toThrow('ACCESS_DENIED')
  })

  it('throws with detail message for other errors', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: 'Гайд не найден' }),
    })

    await expect(apiFetch('/api/guide/missing')).rejects.toThrow('Гайд не найден')
  })

  it('throws generic message when no detail', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: () => Promise.resolve({}),
    })

    await expect(apiFetch('/api/health')).rejects.toThrow('Ошибка 500')
  })

  it('handles JSON parse failure gracefully', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 502,
      json: () => Promise.reject(new Error('invalid json')),
    })

    await expect(apiFetch('/api/health')).rejects.toThrow('Ошибка 502')
  })
})

describe('API module - search', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('encodes search query properly', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ results: [] }),
    })

    await apiSearch('гайд по боссу')

    const url = mockFetch.mock.calls[0][0]
    expect(url).toContain('/api/search?q=')
    expect(url).toContain(encodeURIComponent('гайд по боссу'))
  })

  it('trims whitespace before encoding', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ results: [] }),
    })

    await apiSearch('  test  ')

    const url = mockFetch.mock.calls[0][0]
    expect(url).toContain('q=test')
  })
})

describe('API module - proxy URL', () => {
  it('returns url as-is', () => {
    const url = 'https://cdn.discordapp.com/attachments/123/456/image.png'
    expect(apiGetProxyUrl(url)).toBe(url)
  })

  it('returns empty string for empty input', () => {
    expect(apiGetProxyUrl('')).toBe('')
  })
})

describe('API module - FormData upload (BUG-3)', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  it('upload should not set Content-Type for FormData', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ url: 'https://uploaded.com/file.png' }),
    })

    const file = new File(['test'], 'test.png', { type: 'image/png' })
    await apiUpload(file, 'guides')

    const [, options] = mockFetch.mock.calls[0]
    const headers = options.headers as Record<string, string>

    // BUG-3 FIXED: getAuthHeaders() no longer sets Content-Type.
    // For FormData, apiRaw skips setting Content-Type, letting browser add boundary.
    expect(headers['Content-Type']).toBeUndefined()
  })
})
