import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { apiFetch } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { FileText, Loader2, Search, X } from '@/lib/icons'
import { useAppNavigation } from '@/lib/navigation'
import type { Guide } from '@/lib/types'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { type FC, useEffect, useRef, useState } from 'react'

const highlightMatch = (text: string, query: string) => {
  if (!query || !text) return text
  const parts = text.split(new RegExp(`(${query})`, 'gi'))
  return (
    <span>
      {parts.map((part, i) =>
        part.toLowerCase() === query.toLowerCase() ? (
          <span key={i} className="bg-primary/20 text-primary font-bold px-1 rounded-sm">
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
  const inputRef = useRef<HTMLInputElement>(null)

  // Debounce logic
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query)
    }, 400)
    return () => clearTimeout(timer)
  }, [query])

  // Focus on mount
  useEffect(() => {
    setTimeout(() => {
      inputRef.current?.focus()
    }, 100)
  }, [])

  const { data, isLoading, isFetching } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () =>
      apiFetch(`/search?q=${encodeURIComponent(debouncedQuery)}`) as Promise<{ results: Guide[] }>,
    enabled: debouncedQuery.trim().length >= 2,
  })

  const results = data?.results || []
  const hasSearched = debouncedQuery.trim().length >= 2
  const showEmpty = hasSearched && !isLoading && !isFetching && results.length === 0

  return (
    <div className="flex flex-col min-h-full bg-background animate-in fade-in slide-in-from-bottom-4 duration-300">
      {/* 1. Header with large search input */}
      <header className="sticky top-0 z-40 bg-background/80 backdrop-blur-xl border-b border-border/10">
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
                className="w-full h-14 pl-12 pr-12 rounded-3xl bg-muted/30 border border-border/10 focus:bg-muted/50 focus:outline-none focus:ring-2 focus:ring-primary/20 text-foreground font-medium text-base transition-all"
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

          <div className="flex items-center justify-between px-2">
            <span className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground/50 font-heading">
              Полнотекстовый поиск
            </span>
            {(isLoading || isFetching) && <Loader2 className="size-4 text-primary animate-spin" />}
          </div>
        </div>
      </header>

      {/* 2. Results Area */}
      <main className="flex-1 p-4 container-padding overflow-y-auto">
        {!hasSearched && (
          <div className="flex flex-col items-center justify-center h-full text-center mt-20 opacity-60">
            <div className="size-20 rounded-full bg-muted/50 flex items-center justify-center mb-4 border border-border/10 shadow-inner">
              <Search className="size-8 text-muted-foreground" />
            </div>
            <h2 className="text-xl font-black font-heading text-foreground">Поиск</h2>
            <p className="text-sm font-medium text-muted-foreground mt-2 max-w-xs">
              Введите хотя бы 2 символа, чтобы найти гайды, советы и калькуляторы.
            </p>
          </div>
        )}

        {showEmpty && (
          <div className="flex flex-col items-center justify-center h-full text-center mt-20">
            <div className="text-6xl mb-4 grayscale opacity-50 filter drop-shadow-sm">🥀</div>
            <h2 className="text-xl font-black font-heading text-foreground">Ничего не найдено</h2>
            <p className="text-sm font-medium text-muted-foreground mt-2">
              По запросу «<span className="text-foreground">{debouncedQuery}</span>» нет
              результатов.
            </p>
          </div>
        )}

        {hasSearched && results.length > 0 && (
          <div className="flex flex-col gap-4">
            <div className="text-xs font-black text-muted-foreground uppercase tracking-widest mb-1 px-1">
              Найдено совпадений: <span className="text-primary">{results.length}</span>
            </div>
            {results.map((guide, i) => (
              <motion.div
                key={guide.key}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => {
                  haptic.light()
                  push({ type: 'guide', id: guide.key })
                }}
                className="group cursor-pointer"
              >
                <Card className="card-elevated rounded-3xl border border-border/10 overflow-hidden hover:border-primary/20 transition-all duration-300 hover:shadow-glow">
                  <CardContent className="p-4 sm:p-5 flex gap-4">
                    <div className="size-12 shrink-0 rounded-[18px] bg-primary/10 flex items-center justify-center text-primary shadow-inner border border-primary/10 group-hover:bg-primary group-hover:text-white transition-colors duration-300">
                      <FileText className="size-6" />
                    </div>
                    <div className="flex-1 min-w-0 flex flex-col justify-center">
                      <h3 className="text-[15px] font-black text-foreground font-heading truncate group-hover:text-primary transition-colors">
                        {highlightMatch(guide.title, debouncedQuery)}
                      </h3>
                      <div className="mt-1.5 text-xs font-medium leading-relaxed text-muted-foreground/80 line-clamp-2">
                        {guide.preview ? (
                          highlightMatch(guide.preview, debouncedQuery)
                        ) : (
                          <span className="italic opacity-50">Контент гайда...</span>
                        )}
                      </div>
                      <div className="flex gap-2 mt-3">
                        <Badge
                          variant="secondary"
                          className="bg-muted/50 text-[10px] uppercase tracking-wider font-bold"
                        >
                          {guide.category_key || 'Гайд'}
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
