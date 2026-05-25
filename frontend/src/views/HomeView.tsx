import { ErrorBoundary } from '@/components/ErrorBoundary'
import { HomeDashboard } from '@/components/HomeDashboard'
import { PtrIndicator } from '@/components/PtrIndicator'
import { TopGuidesSection } from '@/components/TopGuidesSection'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { type Category, CategorySearch, useCategories } from '@/features/categories'
import { usePullToRefresh } from '@/hooks/usePullToRefresh'
import { useSearchHistory } from '@/hooks/useSearchHistory'
import { haptic } from '@/lib/haptic'
import { Search, X } from '@/lib/icons'
import { useAppStore } from '@/store'
import { useQueryClient } from '@tanstack/react-query'
import { type FC, useEffect, useMemo, useRef, useState } from 'react'

interface HomeViewProps {
  onSelectCategory: (category: Category) => void
  onSelectGuide: (key: string, title?: string, icon?: string) => void
}

export const HomeView: FC<HomeViewProps> = ({ onSelectCategory, onSelectGuide }) => {
  const [search, setSearch] = useState('')
  const [debouncedQ, setDebouncedQ] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()
  const { searchHistory, addToSearchHistory, clearSearchHistory, removeFromSearchHistory } =
    useSearchHistory()
  const [isInputFocused, setIsInputFocused] = useState(false)

  const { pullY, refreshing } = usePullToRefresh(
    scrollRef,
    async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['top-guides'] }),
        queryClient.invalidateQueries({ queryKey: ['recent-guides'] }),
        queryClient.invalidateQueries({ queryKey: ['recent-comments'] }),
      ])
    },
    !search
  )

  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(search.trim()), 300)
    return () => clearTimeout(t)
  }, [search])

  const isSearch = debouncedQ.length >= 2
  const { data: categoriesData } = useCategories()
  const categories = useMemo(
    () => (Array.isArray(categoriesData) ? categoriesData : []),
    [categoriesData]
  )

  return (
    <div
      className="flex h-full flex-col bg-background animate-in fade-in duration-300"
      data-testid="home-view"
    >
      <header className="container-padding pt-4 sm:pt-6 pb-3 sm:pb-4">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 size-4 -translate-y-1/2 text-muted-foreground/50" />
          <Input
            className="h-11 sm:h-12 w-full rounded-2xl bg-muted/30 !pl-12 pr-12 border border-border/10 focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:border-primary/20 transition-all font-medium text-sm"
            placeholder="Поиск по базе знаний..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onFocus={() => setIsInputFocused(true)}
            onBlur={() => setTimeout(() => setIsInputFocused(false), 200)}
            autoComplete="off"
          />
          {search && (
            <Button
              variant="ghost"
              size="icon"
              className="absolute inset-y-0 right-1 my-auto size-10 rounded-full text-muted-foreground hover:bg-muted active:scale-90"
              onClick={() => {
                haptic.light()
                setSearch('')
              }}
            >
              <X className="size-4" />
            </Button>
          )}
        </div>
      </header>

      <div className="relative flex-1 overflow-hidden flex flex-col">
        <PtrIndicator pullY={pullY} refreshing={refreshing} />
        <div
          ref={scrollRef}
          className="view-scroll flex-1 overflow-y-auto container-padding py-3 sm:py-4 pb-28 sm:pb-32"
        >
          <ErrorBoundary>
            {isSearch ? (
              <CategorySearch
                query={debouncedQ}
                onSelectGuide={(key) => {
                  addToSearchHistory(debouncedQ)
                  onSelectGuide(key)
                }}
                onTagClick={(tag) => {}}
                categories={categories}
              />
            ) : isInputFocused && searchHistory.length > 0 ? (
              <div className="flex flex-col gap-4 animate-in fade-in slide-in-from-top-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 font-heading">
                    История поиска
                  </h4>
                  <button
                    onClick={clearSearchHistory}
                    className="text-[10px] font-bold text-primary/60 hover:text-primary font-heading"
                  >
                    Очистить
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {searchHistory.map((q) => (
                    <div
                      key={q}
                      className="flex items-center gap-1 rounded-full bg-muted/30 px-3 py-1.5 border border-border/10"
                    >
                      <button
                        onClick={() => {
                          haptic.light()
                          setSearch(q)
                        }}
                        className="text-xs font-medium text-foreground/80 hover:text-primary"
                      >
                        {q}
                      </button>
                      <button
                        onClick={() => removeFromSearchHistory(q)}
                        className="text-muted-foreground/40 hover:text-red-500 ml-1"
                      >
                        <X className="size-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-2">
                <TopGuidesSection onSelectGuide={onSelectGuide} />
                <HomeDashboard onSelectGuide={onSelectGuide} onSelectCategory={onSelectCategory} />
              </div>
            )}
          </ErrorBoundary>
        </div>
      </div>
    </div>
  )
}
