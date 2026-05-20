import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useHistory, type HistoryItem } from '../useHistory'
import { storage } from '../../lib/storage'

vi.mock('../../lib/storage')

describe('useHistory', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(storage.get as any).mockResolvedValue(null)
    ;(storage.set as any).mockResolvedValue(true)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('initializes with empty history', async () => {
    const { result } = renderHook(() => useHistory())

    expect(result.current.history).toEqual([])

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100))
    })

    expect(result.current.history).toEqual([])
  })

  it('loads history from storage on mount', async () => {
    const mockHistory: HistoryItem[] = [
      { key: 'guide1', title: 'Guide 1', icon: '📚' },
      { key: 'guide2', title: 'Guide 2' },
    ]

    ;(storage.get as any).mockResolvedValue(JSON.stringify(mockHistory))

    const { result } = renderHook(() => useHistory())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100))
    })

    expect(result.current.history).toEqual(mockHistory)
    expect(storage.get).toHaveBeenCalledWith('blackrose_history')
  })

  it('handles invalid JSON in storage gracefully', async () => {
    ;(storage.get as any).mockResolvedValue('invalid json')

    const { result } = renderHook(() => useHistory())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100))
    })

    expect(result.current.history).toEqual([])
  })

  it('adds item to history at the beginning', async () => {
    ;(storage.get as any).mockResolvedValue(null)

    const { result } = renderHook(() => useHistory())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 50))
    })

    const item: HistoryItem = { key: 'new-guide', title: 'New Guide', icon: '🔥' }

    await act(async () => {
      result.current.addToHistory(item)
    })

    expect(result.current.history[0]).toEqual(item)
    expect(result.current.history).toHaveLength(1)
  })

  it('moves existing item to the beginning', async () => {
    const mockHistory: HistoryItem[] = [
      { key: 'guide1', title: 'Guide 1' },
      { key: 'guide2', title: 'Guide 2' },
      { key: 'guide3', title: 'Guide 3' },
    ]

    ;(storage.get as any).mockResolvedValue(JSON.stringify(mockHistory))

    const { result } = renderHook(() => useHistory())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100))
    })

    const itemToMove: HistoryItem = { key: 'guide3', title: 'Guide 3' }

    await act(async () => {
      result.current.addToHistory(itemToMove)
    })

    expect(result.current.history[0].key).toBe('guide3')
    expect(result.current.history).toHaveLength(3)
    expect(result.current.history[1].key).toBe('guide1')
    expect(result.current.history[2].key).toBe('guide2')
  })

  it('respects MAX_HISTORY limit (20 items)', async () => {
    ;(storage.get as any).mockResolvedValue(null)

    const { result } = renderHook(() => useHistory())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 50))
    })

    // Add 25 items
    for (let i = 1; i <= 25; i++) {
      const item: HistoryItem = { key: `guide${i}`, title: `Guide ${i}` }
      await act(async () => {
        result.current.addToHistory(item)
      })
    }

    expect(result.current.history).toHaveLength(20)
    expect(result.current.history[0].key).toBe('guide25')
    expect(result.current.history[19].key).toBe('guide6')
  })

  it('ignores items with missing key', async () => {
    ;(storage.get as any).mockResolvedValue(null)

    const { result } = renderHook(() => useHistory())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 50))
    })

    const validItem: HistoryItem = { key: 'valid', title: 'Valid Guide' }
    const invalidItem: HistoryItem = { key: '', title: 'Invalid Guide' }

    await act(async () => {
      result.current.addToHistory(validItem)
      result.current.addToHistory(invalidItem)
    })

    expect(result.current.history).toHaveLength(1)
    expect(result.current.history[0].key).toBe('valid')
  })

  it('clears history', async () => {
    const mockHistory: HistoryItem[] = [
      { key: 'guide1', title: 'Guide 1' },
      { key: 'guide2', title: 'Guide 2' },
    ]

    ;(storage.get as any).mockResolvedValue(JSON.stringify(mockHistory))

    const { result } = renderHook(() => useHistory())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100))
    })

    expect(result.current.history).toHaveLength(2)

    await act(async () => {
      result.current.clearHistory()
    })

    expect(result.current.history).toHaveLength(0)
    expect(storage.set).toHaveBeenCalledWith('blackrose_history', '[]')
  })

  it('persists history to storage on add', async () => {
    ;(storage.get as any).mockResolvedValue(null)

    const { result } = renderHook(() => useHistory())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 50))
    })

    const item: HistoryItem = { key: 'test', title: 'Test Guide', icon: '📚' }

    await act(async () => {
      result.current.addToHistory(item)
    })

    expect(storage.set).toHaveBeenCalledWith(
      'blackrose_history',
      JSON.stringify([{ key: 'test', title: 'Test Guide', icon: '📚' }])
    )
  })
})
