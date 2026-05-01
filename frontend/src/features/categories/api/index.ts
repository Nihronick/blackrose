import { apiFetch } from '@/lib/api'
import * as TE from 'fp-ts/TaskEither'
import type { Category, SearchResult } from '../types'

export const categoriesApi = {
  list: (): TE.TaskEither<Error, Category[]> =>
    TE.tryCatch(
      async () => {
        const payload = await apiFetch<Category[] | { categories?: Category[] }>('/api/categories')
        if (Array.isArray(payload)) return payload as Category[]
        if (Array.isArray(payload?.categories)) return payload.categories as Category[]
        return []
      },
      (err) => (err instanceof Error ? err : new Error(String(err)))
    ),

  search: (query: string): TE.TaskEither<Error, SearchResult[]> =>
    TE.tryCatch(
      async () => {
        const payload = await apiFetch<SearchResult[] | { results?: SearchResult[] }>(`/api/search?q=${encodeURIComponent(query)}`)
        if (Array.isArray(payload)) return payload as SearchResult[]
        if (Array.isArray(payload?.results)) return payload.results as SearchResult[]
        return []
      },
      (err) => (err instanceof Error ? err : new Error(String(err)))
    ),
}
