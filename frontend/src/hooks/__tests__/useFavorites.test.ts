import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useFavorites, type FavoriteGuide } from '../useFavorites'
import { storage } from '../../lib/storage'

vi.mock('../../lib/storage')

describe('useFavorites', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(storage.get as any).mockResolvedValue(null)
    ;(storage.set as any).mockResolvedValue(true)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('initializes with empty favorites', async () => {
    const { result } = renderHook(() => useFavorites())

    expect(result.current.favorites).toEqual([])
    expect(result.current.loaded).toBe(false)

    // Wait for async storage.get to complete
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100))
    })

    expect(result.current.loaded).toBe(true)
  })

  it('loads favorites from storage on mount', async () => {
    const mockFavorites: FavoriteGuide[] = [
      { key: 'guide1', title: 'Guide 1', icon: '📚' },
      { key: 'guide2', title: 'Guide 2' },
    ]

    ;(storage.get as any).mockResolvedValue(JSON.stringify(mockFavorites))

    const { result } = renderHook(() => useFavorites())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100))
    })

    expect(result.current.favorites).toEqual(mockFavorites)
    expect(result.current.loaded).toBe(true)
    expect(storage.get).toHaveBeenCalledWith('blackrose_favorites')
  })

  it('handles invalid JSON in storage gracefully', async () => {
    ;(storage.get as any).mockResolvedValue('invalid json')

    const { result } = renderHook(() => useFavorites())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100))
    })

    expect(result.current.favorites).toEqual([])
    expect(result.current.loaded).toBe(true)
  })

  it('adds a favorite', async () => {
    ;(storage.get as any).mockResolvedValue(null)

    const { result } = renderHook(() => useFavorites())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 50))
    })

    const guide: FavoriteGuide = { key: 'new-guide', title: 'New Guide', icon: '🔥' }

    await act(async () => {
      await result.current.toggle(guide)
    })

    expect(result.current.favorites).toEqual([guide])
    expect(storage.set).toHaveBeenCalledWith('blackrose_favorites', JSON.stringify([guide]))
  })

  it('removes a favorite', async () => {
    const mockFavorites: FavoriteGuide[] = [
      { key: 'guide1', title: 'Guide 1' },
      { key: 'guide2', title: 'Guide 2' },
    ]

    ;(storage.get as any).mockResolvedValue(JSON.stringify(mockFavorites))

    const { result } = renderHook(() => useFavorites())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100))
    })

    expect(result.current.favorites).toHaveLength(2)

    const guideToRemove: FavoriteGuide = { key: 'guide1', title: 'Guide 1' }

    await act(async () => {
      await result.current.toggle(guideToRemove)
    })

    expect(result.current.favorites).toHaveLength(1)
    expect(result.current.favorites[0].key).toBe('guide2')
    expect(storage.set).toHaveBeenCalledWith(
      'blackrose_favorites',
      JSON.stringify([mockFavorites[1]])
    )
  })

  it('isFavorite returns correct value', async () => {
    const mockFavorites: FavoriteGuide[] = [{ key: 'guide1', title: 'Guide 1' }]

    ;(storage.get as any).mockResolvedValue(JSON.stringify(mockFavorites))

    const { result } = renderHook(() => useFavorites())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 100))
    })

    expect(result.current.isFavorite('guide1')).toBe(true)
    expect(result.current.isFavorite('guide2')).toBe(false)
  })

  it('toggles favorite multiple times correctly', async () => {
    ;(storage.get as any).mockResolvedValue(null)

    const { result } = renderHook(() => useFavorites())

    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 50))
    })

    const guide: FavoriteGuide = { key: 'test', title: 'Test Guide' }

    // Add
    await act(async () => {
      await result.current.toggle(guide)
    })
    expect(result.current.favorites).toHaveLength(1)

    // Remove
    await act(async () => {
      await result.current.toggle(guide)
    })
    expect(result.current.favorites).toHaveLength(0)

    // Add again
    await act(async () => {
      await result.current.toggle(guide)
    })
    expect(result.current.favorites).toHaveLength(1)
  })
})
