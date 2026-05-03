import { ErrorBoundary } from '@/components/ErrorBoundary'
import { PtrIndicator } from '@/components/PtrIndicator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { HomeDashboard } from '@/components/HomeDashboard'
import { CategoryList, CategorySearch, useCategories } from '@/features/categories'
import type { Category } from '@/features/categories'
import { usePullToRefresh } from '@/hooks/usePullToRefresh'
import { haptic } from '@/lib/haptic'
import { LayoutGrid, Search, X } from '@/lib/icons'
import { isLanguageKey } from '@/lib/language'
import { useAppStore } from '@/store'
import { useQueryClient } from '@tanstack/react-query'
import { FC, useEffect, useMemo, useRef, useState } from 'react'
import { useSearchHistory } from '@/hooks/useSearchHistory'

interface CategoriesViewProps {
  onSelectCategory: (category: Category) => void
  onSelectGuide: (key: string) => void
  onCategoriesLoaded: (categories: Category[]) => void
  onTagClick: (tag: string) => void
}

/**
 * CategoriesView refactored with HIG patterns and premium PTR.
 */
export const CategoriesView: FC<CategoriesViewProps> = ({
  onSelectCategory,
  onSelectGuide,
  onCategoriesLoaded,
  onTagClick,
}) => {
  const [search, setSearch] = useState('')
  const [debouncedQ, setDebouncedQ] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()
  const language = useAppStore((state) => state.language)
  const { searchHistory, addToSearchHistory, clearSearchHistory, removeFromSearchHistory } = useSearchHistory()
  const [isInputFocused, setIsInputFocused] = useState(false)

  // Pull-to-refresh logic at the top level
  const { pullY, refreshing } = usePullToRefresh(
    scrollRef,
    async () => {
      await queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
    !search
  )

  useEffect(() => {
    const t = setTimeout(() => setDebouncedQ(search.trim()), 300)
    return () => clearTimeout(t)
  }, [search])

  const isSearch = debouncedQ.length >= 2
  const { data: categoriesData } = useCategories()
  const categories = useMemo<Category[]>(
    () =>
      (Array.isArray(categoriesData) ? categoriesData : []).filter((cat) =>
        isLanguageKey(cat.key, language)
      ),
    [categoriesData, language]
  )

  useEffect(() => {
    onCategoriesLoaded?.(categories)
  }, [onCategoriesLoaded, categories])

  return (
    <div className="flex h-full flex-col bg-background" data-testid="categories-view">
      <header className="px-5 pt-8 pb-4">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 size-4 -translate-y-1/2 text-muted-foreground/50" />
          <Input
            className="h-12 w-full rounded-2xl bg-muted/50 pl-11 pr-12 border-none ring-1 ring-border/5 focus-visible:ring-primary/20 transition-all font-medium"
            placeholder="Поиск по базе знаний..."
            data-testid="search-input"
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
        <div ref={scrollRef} className="view-scroll flex-1 overflow-y-auto px-5 py-4 pb-32">
          <ErrorBoundary>
            {isSearch ? (
              <CategorySearch
                query={debouncedQ}
                onSelectGuide={(key) => {
                  addToSearchHistory(debouncedQ)
                  onSelectGuide(key)
                }}
                onTagClick={onTagClick}
                categories={categories}
              />
            ) : isInputFocused && searchHistory.length > 0 ? (
              <div className="flex flex-col gap-4 animate-in fade-in slide-in-from-top-2">
                <div className="flex items-center justify-between">
                  <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">
                    История поиска
                  </h4>
                  <button onClick={clearSearchHistory} className="text-[10px] font-bold text-primary/60 hover:text-primary">
                    Очистить
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {searchHistory.map((q) => (
                    <div key={q} className="flex items-center gap-1 rounded-full bg-muted/30 px-3 py-1.5 border border-border/10">
                      <button
                        onClick={() => {
                          haptic.light()
                          setSearch(q)
                        }}
                        className="text-xs font-medium text-foreground/80 hover:text-primary"
                      >
                        {q}
                      </button>
                      <button onClick={() => removeFromSearchHistory(q)} className="text-muted-foreground/40 hover:text-red-500 ml-1">
                        <X className="size-3" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-6">
                <HomeDashboard onSelectGuide={onSelectGuide} onSelectCategory={onSelectCategory} />

                <div className="flex flex-col gap-4 mt-4">
                  <div className="flex items-center gap-2">
                    <LayoutGrid className="size-4 text-muted-foreground" />
                    <h3 className="text-xs font-black uppercase tracking-[0.15em] text-foreground/70">
                      Категории
                    </h3>
                  </div>
                  <CategoryList 
                    categories={categories} 
                    onSelectCategory={onSelectCategory} 
                    isLoading={!categoriesData && !categories.length}
                  />
                </div>
              </div>
            )}
          </ErrorBoundary>

          {/* Credits & Support */}
          <div className="mt-12 mb-8 flex flex-col items-center text-center gap-6 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            <div className="h-px w-12 bg-border/40" />

            <div className="flex flex-col gap-2">
              <p className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground/40">
                Информация взята из
              </p>
              <a
                href="https://discord.gg/slayerlegend"
                target="_blank"
                rel="noreferrer"
                className="text-sm font-black text-foreground hover:text-primary transition-colors flex items-center justify-center gap-2"
              >
                Slayer Legend Official Discord
              </a>
              <p className="text-[10px] text-muted-foreground/50 max-w-[240px] leading-relaxed">
                Благодарим Leoht и все сообщество Discord за создание и поддержку этих гайдов.
              </p>
            </div>

            <Button
              variant="outline"
              size="sm"
              className="h-10 rounded-xl bg-primary/5 border-primary/20 text-primary font-bold px-6 hover:bg-primary/10 hover:border-primary/40 transition-all active:scale-95"
              onClick={() => {
                haptic.medium()
                window.open('https://dalink.to/nihronick', '_blank')
              }}
            >
              Поддержать проект
            </Button>

            <p className="text-[10px] font-medium text-muted-foreground/30">
              BlackRose v3.3 • 2026
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CategoriesView
