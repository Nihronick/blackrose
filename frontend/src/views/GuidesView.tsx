import { PtrIndicator } from '@/components/PtrIndicator'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { usePullToRefresh } from '@/hooks/usePullToRefresh'
import { apiFetch } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { BookOpen, ChevronRight, Eye } from '@/lib/icons'
import type { CategoryGuidesResponse } from '@/lib/types'
import { normalizeUrl } from '@/lib/utils'
import { useSuspenseQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { type FC, type SyntheticEvent, useMemo, useRef } from 'react'

interface GuideItem {
  key: string
  title: string
  icon: string
  preview?: string
  views: number
  tags: string[]
}

interface Category {
  key: string
  title: string
  icon?: string
}

interface GuidesViewProps {
  category: Category
  onSelectGuide: (key: string, title?: string, icon?: string) => void
}

/**
 * GuidesView refactored with TSX, Suspense, and premium shadcn/ui design.
 */
export const GuidesView: FC<GuidesViewProps> = ({ category, onSelectGuide }) => {
  const scrollRef = useRef<HTMLDivElement>(null)
  const categoryKey = category?.key

  const { data: categoryData, refetch } = useSuspenseQuery({
    queryKey: ['category-guides', categoryKey],
    queryFn: () => apiFetch<CategoryGuidesResponse>(`/api/category/${categoryKey}`),
    staleTime: 60_000,
  })

  const items = useMemo(
    () => (Array.isArray(categoryData?.items) ? categoryData.items : []),
    [categoryData]
  )

  const handleRefresh = async () => {
    await refetch()
  }

  const { pullY, refreshing } = usePullToRefresh(scrollRef, handleRefresh)

  return (
    <div className="view-scroll flex-1 overflow-y-auto relative z-0" ref={scrollRef}>
      <div className="absolute top-0 left-0 w-full h-80 mesh-bg opacity-30 pointer-events-none -z-10" />
      <PtrIndicator pullY={pullY} refreshing={refreshing} />

      <div className="grid grid-cols-1 gap-3 sm:gap-4 container-padding py-4 sm:py-6 pb-28 sm:pb-32 stagger-in relative z-10">
        {items.length === 0 ? (
          <div className="flex h-[60vh] flex-col items-center justify-center text-center animate-in fade-in zoom-in duration-500 relative">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-primary/10 rounded-full blur-[60px] pointer-events-none" />
            <div className="flex size-20 items-center justify-center rounded-[28px] bg-primary/10 mb-4 ring-1 ring-primary/20 shadow-inner relative z-10">
              <BookOpen className="size-10 text-primary" />
            </div>
            <h3 className="text-lg font-bold text-foreground">В этой категории пусто</h3>
            <p className="max-w-[200px] text-xs font-medium text-muted-foreground/60 mt-1">
              Гайды скоро появятся, заходите позже!
            </p>
          </div>
        ) : (
          items.map((item) => (
            <Card
              key={item.key}
              className="group cursor-pointer glass-card card-elevated rounded-3xl active:scale-[0.98] hover:border-primary/30"
              onClick={() => {
                haptic.light()
                onSelectGuide(item.key, item.title, item.icon)
              }}
            >
              <CardContent className="flex flex-col gap-3 p-4">
                <div className="flex items-start gap-4">
                  <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-primary/10 shadow-inner transition-colors group-hover:bg-primary/20">
                    {item.icon ? (
                      <motion.img
                        layoutId={`guide-icon-${item.key}`}
                        src={normalizeUrl(item.icon)}
                        alt=""
                        className="size-10 object-contain"
                        onError={(e: SyntheticEvent<HTMLImageElement>) => {
                          e.currentTarget.style.display = 'none'
                        }}
                      />
                    ) : (
                      <motion.span layoutId={`guide-icon-${item.key}`} className="text-2xl">
                        📖
                      </motion.span>
                    )}
                  </div>
                  <div className="flex flex-1 flex-col min-w-0">
                    <h3 className="truncate text-base font-black tracking-normal text-foreground/90 font-heading leading-tight">
                      {item.title}
                    </h3>
                    {item.text && (
                      <p className="mt-1 line-clamp-2 text-[13px] font-medium leading-relaxed text-muted-foreground">
                        {item.text}
                      </p>
                    )}

                    <div className="mt-2 flex items-center gap-3">
                      {item.views > 0 && (
                        <div className="flex items-center gap-1 text-[11px] font-bold text-primary/70">
                          <Eye className="size-3" />
                          <span>
                            {item.views >= 1000 ? `${(item.views / 1000).toFixed(1)}k` : item.views}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  <ChevronRight className="size-5 text-muted-foreground/30 transition-transform group-hover:translate-x-0.5" />
                </div>

                {(item.tags?.length ?? 0) > 0 && (
                  <div className="flex flex-wrap gap-1.5" onClick={(e) => e.stopPropagation()}>
                    {(item.tags || []).slice(0, 3).map((t) => (
                      <Badge
                        key={t}
                        variant="secondary"
                        className="rounded-md border-border/30 bg-muted/40 px-1.5 py-0 text-[9px] font-bold uppercase tracking-wider text-muted-foreground/80"
                      >
                        #{t}
                      </Badge>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
