import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactNode } from 'react'
import {
  useCategories,
  useCategoryGuides,
  useGuide,
  useSearch,
  useTopGuides,
  useComments,
  useAddComment,
  useDeleteComment,
  useSubscriptions,
  useToggleSubscription,
  useGuidesByTag,
  useTags,
  useRecordView,
  keys,
} from '../queries'
import * as api from '../../lib/api'

vi.mock('../../lib/api')

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('Query Keys', () => {
  it('creates correct category key', () => {
    expect(keys.categories()).toEqual(['categories'])
  })

  it('creates correct category guide key', () => {
    expect(keys.category('test')).toEqual(['category', 'test'])
  })

  it('creates correct guide key', () => {
    expect(keys.guide('test')).toEqual(['guide', 'test'])
  })

  it('creates correct search key', () => {
    expect(keys.search('query')).toEqual(['search', 'query'])
  })

  it('creates correct tag key', () => {
    expect(keys.tag('important')).toEqual(['tag', 'important'])
  })
})

describe('useCategories', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches categories', async () => {
    const mockCategories = [
      { key: 'cat1', title: 'Category 1' },
      { key: 'cat2', title: 'Category 2' },
    ]
    ;(api.apiFetch as any).mockResolvedValue({ categories: mockCategories })

    const { result } = renderHook(() => useCategories(), { wrapper: createWrapper() })

    expect(result.current.isLoading).toBe(true)

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockCategories)
  })

  it('handles errors gracefully', async () => {
    ;(api.apiFetch as any).mockRejectedValue(new Error('API Error'))

    const { result } = renderHook(() => useCategories(), { wrapper: createWrapper() })

    await waitFor(() => {
      expect(result.current.isError).toBe(true)
    })

    expect(result.current.error).toBeDefined()
  })
})

describe('useCategoryGuides', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches guides for a category', async () => {
    const mockGuides = [
      { key: 'guide1', title: 'Guide 1' },
      { key: 'guide2', title: 'Guide 2' },
    ]
    ;(api.apiFetch as any).mockResolvedValue({ items: mockGuides })

    const { result } = renderHook(() => useCategoryGuides('test-category'), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockGuides)
  })

  it('does not fetch if category key is empty', async () => {
    const { result } = renderHook(() => useCategoryGuides(''), {
      wrapper: createWrapper(),
    })

    expect(result.current.isLoading).toBe(false)
    expect(api.apiFetch).not.toHaveBeenCalled()
  })
})

describe('useGuide', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches a specific guide', async () => {
    const mockGuide = {
      key: 'guide1',
      title: 'Guide 1',
      content: 'Content here',
    }
    ;(api.apiFetch as any).mockResolvedValue(mockGuide)

    const { result } = renderHook(() => useGuide('guide1'), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockGuide)
  })

  it('does not fetch if guide key is empty', async () => {
    const { result } = renderHook(() => useGuide(''), {
      wrapper: createWrapper(),
    })

    expect(result.current.isLoading).toBe(false)
    expect(api.apiFetch).not.toHaveBeenCalled()
  })
})

describe('useSearch', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches search results', async () => {
    const mockResults = [
      { key: 'guide1', title: 'Found Guide' },
    ]
    ;(api.apiSearch as any).mockResolvedValue({ results: mockResults })

    const { result } = renderHook(() => useSearch('query'), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockResults)
  })

  it('does not search with query shorter than 2 chars', async () => {
    const { result } = renderHook(() => useSearch('a'), {
      wrapper: createWrapper(),
    })

    expect(result.current.isLoading).toBe(false)
    expect(api.apiSearch).not.toHaveBeenCalled()
  })

  it('does not search with empty query', async () => {
    const { result } = renderHook(() => useSearch(''), {
      wrapper: createWrapper(),
    })

    expect(result.current.isLoading).toBe(false)
    expect(api.apiSearch).not.toHaveBeenCalled()
  })
})

describe('useTopGuides', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches top guides', async () => {
    const mockTop = [
      { key: 'popular1', title: 'Popular Guide 1' },
      { key: 'popular2', title: 'Popular Guide 2' },
    ]
    ;(api.apiTopGuides as any).mockResolvedValue({ results: mockTop })

    const { result } = renderHook(() => useTopGuides(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockTop)
  })
})

describe('useComments', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('does not fetch comments by default', async () => {
    const { result } = renderHook(() => useComments('guide1'), {
      wrapper: createWrapper(),
    })

    expect(result.current.isLoading).toBe(false)
  })

  it('fetches comments when enabled', async () => {
    const mockComments = [
      { id: 1, text: 'Great guide!' },
      { id: 2, text: 'Very helpful' },
    ]
    ;(api.apiGetComments as any).mockResolvedValue({ comments: mockComments })

    const { result } = renderHook(() => useComments('guide1', true), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockComments)
  })
})

describe('useAddComment', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates mutation for adding comment', async () => {
    ;(api.apiAddComment as any).mockResolvedValue({ id: 1 })

    const { result } = renderHook(() => useAddComment('guide1'), {
      wrapper: createWrapper(),
    })

    expect(result.current.mutate).toBeDefined()
  })
})

describe('useDeleteComment', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates mutation for deleting comment', async () => {
    ;(api.apiDeleteComment as any).mockResolvedValue({})

    const { result } = renderHook(() => useDeleteComment('guide1'), {
      wrapper: createWrapper(),
    })

    expect(result.current.mutate).toBeDefined()
  })
})

describe('useSubscriptions', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches subscriptions', async () => {
    const mockSubs = ['cat1', 'cat2']
    ;(api.apiGetSubscriptions as any).mockResolvedValue({ subscriptions: mockSubs })

    const { result } = renderHook(() => useSubscriptions(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockSubs)
  })

  it('defaults to empty array if no subscriptions', async () => {
    ;(api.apiGetSubscriptions as any).mockResolvedValue({})

    const { result } = renderHook(() => useSubscriptions(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual([])
  })
})

describe('useToggleSubscription', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates mutation for toggling subscription', async () => {
    ;(api.apiSubscribe as any).mockResolvedValue({})

    const { result } = renderHook(() => useToggleSubscription(), {
      wrapper: createWrapper(),
    })

    expect(result.current.mutate).toBeDefined()
  })
})

describe('useGuidesByTag', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches guides for a tag', async () => {
    const mockGuides = [{ key: 'guide1', title: 'Guide 1' }]
    ;(api.apiGuidesByTag as any).mockResolvedValue({ results: mockGuides })

    const { result } = renderHook(() => useGuidesByTag('important'), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockGuides)
  })

  it('does not fetch if tag is empty', async () => {
    const { result } = renderHook(() => useGuidesByTag(''), {
      wrapper: createWrapper(),
    })

    expect(result.current.isLoading).toBe(false)
  })
})

describe('useTags', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches tags', async () => {
    const mockTags = ['important', 'beginner', 'advanced']
    ;(api.apiTags as any).mockResolvedValue({ tags: mockTags })

    const { result } = renderHook(() => useTags(), {
      wrapper: createWrapper(),
    })

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true)
    })

    expect(result.current.data).toEqual(mockTags)
  })
})

describe('useRecordView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates mutation for recording view', async () => {
    ;(api.apiRecordView as any).mockResolvedValue({})

    const { result } = renderHook(() => useRecordView(), {
      wrapper: createWrapper(),
    })

    expect(result.current.mutate).toBeDefined()
  })
})
