import { apiFetch } from '@/lib/api'
import * as TE from 'fp-ts/TaskEither'
import type { Category, SearchResult } from '../types'

export const categoriesApi = {
  list: (): TE.TaskEither<Error, Category[]> =>
    TE.tryCatch(
      async () => {
        const payload = await apiFetch<Category[] | { categories?: Category[] }>('/api/categories')
        const items = Array.isArray(payload)
          ? payload
          : Array.isArray(payload?.categories)
            ? payload.categories
            : []
        return items.map((c: Category) => ({
          ...c,
          icon: c.icon || c.icon_url,
          icon_url: c.icon_url || c.icon,
        })) as Category[]
      },
      (err) => (err instanceof Error ? err : new Error(String(err)))
    ),

  search: (query: string): TE.TaskEither<Error, SearchResult[]> =>
    TE.tryCatch(
      async () => {
        const payload = await apiFetch<SearchResult[] | { results?: SearchResult[] }>(
          `/api/search?q=${encodeURIComponent(query)}`
        )
        if (Array.isArray(payload)) return payload as SearchResult[]
        if (Array.isArray(payload?.results)) return payload.results as SearchResult[]
        return []
      },
      (err) => (err instanceof Error ? err : new Error(String(err)))
    ),
}
