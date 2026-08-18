import { EmptyState } from '@/components/EmptyState'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { apiFetch } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { FileText, Loader2, Search, X, Sparkles } from '@/lib/icons'
import { useAppNavigation } from '@/lib/navigation'
import { indexGuides, searchGuidesClient, type SearchDoc } from '@/lib/searchIndex'
import type { Guide } from '@/lib/types'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { type FC, useDeferredValue, useEffect, useMemo, useRef, useState, useTransition } from 'react'

const highlightMatch = (text: string, query: string) => {
  if (!query || !text) return text
  const terms = query.trim().split(/\s+/).filter(Boolean)
  if (terms.length === 0) return text
  const regex = new RegExp(`(${terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'gi')
  const parts = text.split(regex)
  return (
    <span>
      {parts.map((part, i) =>
        terms.some((t) => t.toLowerCase() === part.toLowerCase()) ? (
          <span key={i} className="bg-primary/25 text-primary font-bold px-1 py-0.5 rounded-md">
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </span>
  )
}

export const SearchView: FC = () => {
  const { push, pop } = useAppNavigation()
  const [query, setQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const deferredQuery = useDeferredValue(debouncedQuery)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [, startTransition] = useTransition()
  const inputRef = useRef<HTMLInputElement>(null)

  // Debounce logic
  useEffect(() => {
    const timer = setTimeout(() => {
      startTransition(() => {
        setDebouncedQuery(query)
      })
    }, 150)
    return () => clearTimeout(timer)
  }, [query])

  // Focus on mount
  useEffect(() => {
    setTimeout(() => {
      inputRef.current?.focus()
    }, 100)
  }, [])

  // Pre-fetch all categories/guides to populate instant client-side search index
  const { data: categoriesData } = useQuery({
    queryKey: ['categories-all-search'],
    queryFn: async () => {
      const res = await apiFetch<{ categories: Array<{ key: string; title: string }> }>('/categories')
      return res.categories || []
    },
    staleTime: 1000 * 60 * 10,
  })

  // Backend full-text search query
  const { data: serverData, isLoading, isFetching } = useQuery({
    queryKey: ['search', deferredQuery],
    queryFn: async () => {
      const res = await apiFetch<{ results: Guide[] }>(`/search?q=${encodeURIComponent(deferredQuery)}`)
      if (res.results) {
        indexGuides(res.results)
      }
      return res.results || []
    },
    enabled: deferredQuery.trim().length >= 2,
    staleTime: 1000 * 60 * 5,
  })

  // Client-side MiniSearch instant matching
  const clientResults = useMemo(() => {
    return searchGuidesClient(query, 50)
  }, [query])

  // Merge and deduplicate client & server results
  const allResults = useMemo(() => {
    const map = new Map<string, Guide | SearchDoc>()
    for (const item of clientResults) {
      map.set(item.key, item)
    }
    for (const item of serverData || []) {
      map.set(item.key, item)
    }
    let list = Array.from(map.values())
    if (selectedCategory) {
      list = list.filter((g) => g.category_key === selectedCategory)
    }
    return list
  }, [clientResults, serverData, selectedCategory])

  // Categories present in results for quick filtering
  const availableCategories = useMemo(() => {
    const set = new Set<string>()
    for (const g of allResults) {
      if (g.category_key) set.add(g.category_key)
    }
    return Array.from(set)
  }, [allResults])

  const hasSearched = query.trim().length >= 2
  const showEmpty = hasSearched && !isLoading && !isFetching && allResults.length === 0

  return (
    <div className="flex flex-col min-h-full bg-background animate-in fade-in slide-in-from-bottom-4 duration-300">
      {/* 1. Header with large search input */}
      <header className="sticky top-0 z-40 bg-background/85 backdrop-blur-xl border-b border-border/10">
        <div className="flex flex-col gap-3 p-4 container-padding">
          <div className="flex items-center gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 size-5 text-muted-foreground" />
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Искать в базе знаний..."
                className="w-full h-14 pl-12 pr-12 rounded-3xl bg-muted/30 border border-border/10 focus:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-primary/25 text-foreground font-medium text-base transition-all"
              />
              {query && (
                <button
                  type="button"
                  onClick={() => {
                    setQuery('')
                    inputRef.current?.focus()
                  }}
                  className="absolute right-4 top-1/2 -translate-y-1/2 size-6 rounded-full bg-muted-foreground/10 text-muted-foreground flex items-center justify-center hover:bg-muted-foreground/20 transition-colors"
                >
                  <X className="size-4" />
                </button>
              )}
            </div>
            <button
              type="button"
              onClick={() => pop()}
              className="px-2 text-sm font-bold text-muted-foreground hover:text-foreground transition-colors font-heading"
            >
              Отмена
            </button>
          </div>

          {/* Category Filter Chips */}
          {hasSearched && availableCategories.length > 1 && (
            <div className="flex items-center gap-2 overflow-x-auto no-scrollbar py-1">
              <button
                type="button"
                onClick={() => setSelectedCategory(null)}
                className={`px-3 py-1 text-xs rounded-full font-bold transition-colors shrink-0 ${
                  selectedCategory === null
                    ? 'bg-primary text-white'
                    : 'bg-muted/40 text-muted-foreground hover:bg-muted'
                }`}
              >
                Все ({allResults.length})
              </button>
              {availableCategories.map((catKey) => {
                const catTitle = categoriesData?.find((c) => c.key === catKey)?.title || catKey
                return (
                  <button
                    key={catKey}
                    type="button"
                    onClick={() => setSelectedCategory(selectedCategory === catKey ? null : catKey)}
                    className={`px-3 py-1 text-xs rounded-full font-bold transition-colors shrink-0 ${
                      selectedCategory === catKey
                        ? 'bg-primary text-white'
                        : 'bg-muted/40 text-muted-foreground hover:bg-muted'
                    }`}
                  >
                    {catTitle}
                  </button>
                )
              })}
            </div>
          )}

          <div className="flex items-center justify-between px-2">
            <div className="flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-widest text-muted-foreground/60 font-heading">
              <Sparkles className="size-3 text-primary" />
              <span>Мгновенный поиск MiniSearch</span>
            </div>
            {(isLoading || isFetching) && <Loader2 className="size-4 text-primary animate-spin" />}
          </div>
        </div>
      </header>

      {/* 2. Results Area */}
      <main className="flex-1 p-4 container-padding overflow-y-auto">
        {!hasSearched && (
          <EmptyState
            icon={<Search className="size-8 text-rose-400" />}
            title="Поиск по базе знаний"
            description="Введите хотя бы 2 символа, чтобы мгновенно найти нужные гайды, советы и тактики Slayer Legend."
          />
        )}

        {showEmpty && (
          <EmptyState
            icon="🥀"
            title="Ничего не найдено"
            description={`По запросу «${query}» материалов не найдено. Попробуйте ввести другие ключевые слова.`}
            actionLabel="Сбросить поиск"
            onAction={() => {
              setQuery('')
              setSelectedCategory(null)
            }}
          />
        )}

        {hasSearched && allResults.length > 0 && (
          <div className="flex flex-col gap-3">
            <div className="text-xs font-black text-muted-foreground uppercase tracking-widest mb-1 px-1">
              Найдено совпадений: <span className="text-primary">{allResults.length}</span>
            </div>
            {allResults.map((guide, i) => (
              <motion.div
                key={guide.key}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: Math.min(i * 0.03, 0.3) }}
                onClick={() => {
                  haptic.light()
                  push({ type: 'guide', id: guide.key })
                }}
                className="group cursor-pointer"
              >
                <Card className="card-elevated rounded-3xl border border-border/10 overflow-hidden hover:border-primary/25 transition-all duration-300 hover:shadow-glow">
                  <CardContent className="p-4 sm:p-5 flex gap-4">
                    <div className="size-12 shrink-0 rounded-[18px] bg-primary/10 flex items-center justify-center text-primary shadow-inner border border-primary/10 group-hover:bg-primary group-hover:text-white transition-colors duration-300">
                      <FileText className="size-6" />
                    </div>
                    <div className="flex-1 min-w-0 flex flex-col justify-center">
                      <h3 className="text-[15px] font-black text-foreground font-heading truncate group-hover:text-primary transition-colors">
                        {highlightMatch(guide.title, query)}
                      </h3>
                      <div className="mt-1.5 text-xs font-medium leading-relaxed text-muted-foreground/80 line-clamp-2">
                        {guide.preview ? (
                          highlightMatch(guide.preview, query)
                        ) : (
                          <span className="italic opacity-50">Контент гайда...</span>
                        )}
                      </div>
                      <div className="flex gap-2 mt-3">
                        <Badge
                          variant="secondary"
                          className="bg-muted/50 text-[10px] uppercase tracking-wider font-bold"
                        >
                          {categoriesData?.find((c) => c.key === guide.category_key)?.title || guide.category_key || 'Гайд'}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
