import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  apiAddComment,
  apiDeleteComment,
  apiFetch,
  apiGetComments,
  apiGetSubscriptions,
  apiGuidesByTag,
  apiRecordView,
  apiSearch,
  apiSubscribe,
  apiTags,
  apiTopGuides,
  apiUnsubscribe,
} from '../lib/api'
import type { Category, Comment, Guide } from '../lib/types'

// ── Query Keys ────────────────────────────────────────────────
export const keys = {
  categories: () => ['categories'] as const,
  category: (key: string) => ['category', key] as const,
  guide: (key: string) => ['guide', key] as const,
  search: (q: string) => ['search', q] as const,
  top: () => ['top'] as const,
  comments: (key: string) => ['comments', key] as const,
  subscriptions: () => ['subscriptions'] as const,
  tag: (tag: string) => ['tag', tag] as const,
  tags: () => ['tags'] as const,
}

// ── Категории — доступны всем включая гостей ──────────────────
export function useCategories() {
  return useQuery({
    queryKey: keys.categories(),
    queryFn: () =>
      apiFetch<{ categories: Category[] }>('/api/categories').then((r) => r.categories),
    staleTime: 60_000,
  })
}

// ── Гайды в категории ─────────────────────────────────────────
export function useCategoryGuides(categoryKey: string) {
  return useQuery({
    queryKey: keys.category(categoryKey),
    queryFn: () =>
      apiFetch<{ items: Guide[] }>(`/api/category/${categoryKey}`).then((r) => r.items),
    staleTime: 60_000,
    enabled: !!categoryKey,
  })
}

// ── Гайд ─────────────────────────────────────────────────────
export function useGuide(guideKey: string) {
  return useQuery({
    queryKey: keys.guide(guideKey),
    queryFn: () => apiFetch(`/api/guide/${guideKey}`),
    staleTime: 120_000,
    enabled: !!guideKey,
  })
}

// ── Поиск ────────────────────────────────────────────────────
export function useSearch(q: string) {
  return useQuery({
    queryKey: keys.search(q),
    queryFn: () => apiSearch(q).then((r: { results: Guide[] }) => r.results),
    staleTime: 30_000,
    enabled: q.trim().length >= 2,
  })
}

// ── Топ гайдов — доступен всем ────────────────────────────────
export function useTopGuides() {
  return useQuery({
    queryKey: keys.top(),
    queryFn: () => apiTopGuides().then((r: { results: Guide[] }) => r.results),
    staleTime: 120_000,
  })
}

// ── Комментарии ───────────────────────────────────────────────
export function useComments(guideKey: string, enabled = false) {
  return useQuery({
    queryKey: keys.comments(guideKey),
    queryFn: () => apiGetComments(guideKey).then((r: { comments: Comment[] }) => r.comments),
    enabled: !!guideKey && enabled,
    staleTime: 30_000,
  })
}

export function useAddComment(guideKey: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (text: string) => apiAddComment(guideKey, text),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.comments(guideKey) }),
  })
}

export function useDeleteComment(guideKey: string) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (commentId: string | number) => apiDeleteComment(guideKey, commentId),
    onSuccess: () => qc.invalidateQueries({ queryKey: keys.comments(guideKey) }),
  })
}

// ── Подписки ─────────────────────────────────────────────────
export function useSubscriptions() {
  return useQuery({
    queryKey: keys.subscriptions(),
    queryFn: () =>
      apiGetSubscriptions().then((r: { subscriptions?: string[] }) => r.subscriptions ?? []),
    staleTime: 60_000,
  })
}

interface ToggleSubParams {
  categoryKey: string
  subscribed: boolean
}

interface MutationContext {
  prev?: string[]
}

export function useToggleSubscription() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ categoryKey, subscribed }: ToggleSubParams) =>
      subscribed ? apiUnsubscribe(categoryKey) : apiSubscribe(categoryKey),
    onMutate: async ({ categoryKey, subscribed }: ToggleSubParams) => {
      await qc.cancelQueries({ queryKey: keys.subscriptions() })
      const prev = qc.getQueryData<string[]>(keys.subscriptions())
      qc.setQueryData<string[]>(keys.subscriptions(), (old = []) =>
        subscribed ? old.filter((k) => k !== categoryKey) : [...old, categoryKey]
      )
      return { prev }
    },
    onError: (_err, _vars, ctx: MutationContext | undefined) => {
      if (ctx?.prev) {
        qc.setQueryData(keys.subscriptions(), ctx.prev)
      }
    },
    onSettled: () => qc.invalidateQueries({ queryKey: keys.subscriptions() }),
  })
}

// ── Теги ─────────────────────────────────────────────────────
export function useGuidesByTag(tag: string) {
  return useQuery({
    queryKey: keys.tag(tag),
    queryFn: () => apiGuidesByTag(tag).then((r: { results: Guide[] }) => r.results),
    staleTime: 60_000,
    enabled: !!tag,
  })
}

export function useTags() {
  return useQuery({
    queryKey: keys.tags(),
    queryFn: () => apiTags().then((r: { tags: string[] }) => r.tags),
    staleTime: 120_000,
  })
}

// ── Record view ───────────────────────────────────────────────
export function useRecordView() {
  return useMutation({
    mutationFn: (guideKey: string) => apiRecordView(guideKey),
  })
}
