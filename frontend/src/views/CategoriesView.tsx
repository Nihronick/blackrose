import { ErrorBoundary } from '@/components/ErrorBoundary'
import { PtrIndicator } from '@/components/PtrIndicator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { CategoryList, useCategories } from '@/features/categories'
import type { Category } from '@/features/categories'
import { usePullToRefresh } from '@/hooks/usePullToRefresh'
import { haptic } from '@/lib/haptic'
import { LayoutGrid, Search, X } from '@/lib/icons'
import { useAppStore } from '@/store'
import { useQueryClient } from '@tanstack/react-query'
import { type FC, useEffect, useMemo, useRef, useState } from 'react'

interface CategoriesViewProps {
  onSelectCategory: (category: Category) => void
  onCategoriesLoaded?: (categories: Category[]) => void
}

/**
 * Clean and premium CategoriesView mapping to a dedicated bottom navigation tab.
 */
export const CategoriesView: FC<CategoriesViewProps> = ({
  onSelectCategory,
  onCategoriesLoaded,
}) => {
  const [search, setSearch] = useState('')
  const scrollRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()
  const language = useAppStore((state) => state.language)

  const { pullY, refreshing } = usePullToRefresh(
    scrollRef,
    async () => {
      await queryClient.invalidateQueries({ queryKey: ['categories'] })
    },
    !search
  )

  const { data: categoriesData } = useCategories()
  const categories = useMemo<Category[]>(
    () => (Array.isArray(categoriesData) ? categoriesData : []),
    [categoriesData]
  )

  useEffect(() => {
    onCategoriesLoaded?.(categories)
  }, [onCategoriesLoaded, categories])

  const filteredCategories = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return categories
    return categories.filter((c) => c.title.toLowerCase().includes(q))
  }, [categories, search])

  return (
    <div
      className="flex h-full flex-col bg-background animate-in fade-in duration-300 rose-mesh-bg min-h-screen"
      data-testid="categories-view"
    >
      <div className="absolute top-0 left-0 w-full h-80 mesh-bg opacity-30 pointer-events-none -z-10" />
      <header className="container-padding pt-4 sm:pt-6 pb-3 sm:pb-4 relative z-10">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 size-4 -translate-y-1/2 text-muted-foreground/50" />
          <Input
            className="h-11 sm:h-12 w-full rounded-2xl bg-muted/30 pl-11 pr-12 border border-border/10 focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:border-primary/20 transition-all font-medium text-sm"
            placeholder="Поиск категорий..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
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
            <div className="flex flex-col gap-4">
              <div className="section-label font-heading">
                <LayoutGrid className="size-3.5 text-primary" />
                <span>Категории ({filteredCategories.length})</span>
              </div>
              <CategoryList
                categories={filteredCategories}
                onSelectCategory={onSelectCategory}
                isLoading={!categoriesData && !categories.length}
              />
            </div>
          </ErrorBoundary>

          {/* Credits & Support */}
          <div className="mt-12 mb-8 flex flex-col items-center text-center gap-6 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            <div className="h-px w-12 bg-border/40" />

            <div className="flex flex-col gap-2">
              <p className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground/40 font-heading">
                Информация взята из
              </p>
              <a
                href="https://discord.gg/slayerlegend"
                target="_blank"
                rel="noreferrer"
                className="text-sm font-black text-foreground hover:text-primary transition-colors flex items-center justify-center gap-2 font-heading"
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
              className="h-11 rounded-2xl bg-primary/10 border-primary/20 text-primary font-bold px-8 hover:bg-primary/15 hover:border-primary/40 transition-all active:scale-95 shadow-soft font-heading"
              onClick={() => {
                haptic.medium()
                window.open('https://dalink.to/nihronick', '_blank')
              }}
            >
              Поддержать проект
            </Button>

            <p className="text-[10px] font-medium text-muted-foreground/30 font-heading">
              BlackRose v3.3 • 2026
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
