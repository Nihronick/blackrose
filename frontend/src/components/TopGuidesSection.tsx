import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { apiTopGuides } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { ChevronRight, Eye, TrendingUp } from '@/lib/icons'
import { isLanguageKey } from '@/lib/language'
import { normalizeUrl } from '@/lib/utils'
import { useAppStore } from '@/store'
import { useSuspenseQuery } from '@tanstack/react-query'
import type { FC, SyntheticEvent } from 'react'
import type React from 'react'
import { Suspense, useState } from 'react'

interface TopGuide {
  key: string
  title: string
  icon_url: string
  views: number
}

interface TopGuidesSectionProps {
  onSelectGuide: (key: string, title?: string, icon?: string) => void
}

/**
 * TopGuidesSection refactored with TSX, Suspense, and premium visuals.
 */
export const TopGuidesSection: FC<TopGuidesSectionProps> = ({ onSelectGuide }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="px-5 my-6 transition-all">
      {!isOpen ? (
        <button
          className="flex items-center gap-3 rounded-[20px] bg-primary/10 px-6 py-3.5 text-xs font-black uppercase tracking-[0.15em] text-primary transition-all active:scale-95 shadow-sm shadow-primary/5 hover:bg-primary/15"
          onClick={() => {
            haptic.medium?.()
            setIsOpen(true)
          }}
        >
          <TrendingUp className="size-4 animate-pulse" />
          <span>Популярное</span>
        </button>
      ) : (
        <div className="flex flex-col gap-5 animate-in fade-in slide-in-from-top-4 duration-500 ease-out">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TrendingUp className="size-4 text-primary" />
              <h3 className="text-[11px] font-black uppercase tracking-[0.2em] text-foreground/70">
                Популярные сейчас
              </h3>
            </div>
            <Button
              variant="ghost"
              className="h-8 rounded-xl px-3 text-[10px] font-bold uppercase tracking-widest text-primary hover:bg-primary/10 transition-colors"
              onClick={() => {
                haptic.light?.()
                setIsOpen(false)
              }}
            >
              Скрыть
            </Button>
          </div>

          <Suspense fallback={<StatsSkeleton />}>
            <GuidesList onSelectGuide={onSelectGuide} />
          </Suspense>
        </div>
      )}
    </div>
  )
}

const GuidesList = ({ onSelectGuide }: TopGuidesSectionProps) => {
  const { data } = useSuspenseQuery({
    queryKey: ['top-guides'],
    queryFn: apiTopGuides,
  }) as { data: { results: TopGuide[] } }
  const language = useAppStore((state) => state.language)

  const guides: TopGuide[] = (data?.results || []).filter((guide: TopGuide) =>
    isLanguageKey(guide.key, language)
  )

  if (guides.length === 0)
    return (
      <div className="py-8 text-center text-xs font-medium text-muted-foreground">Нет данных</div>
    )

  return (
    <div className="flex flex-col gap-3 pb-2">
      {guides.slice(0, 5).map((g, idx) => (
        <Card
          key={g.key}
          className="group cursor-pointer border-border/10 glass-card transition-all hover:translate-x-1 active:scale-[0.98]"
          onClick={() => {
            haptic.light?.()
            onSelectGuide(g.key, g.title, g.icon_url)
          }}
        >
          <CardContent className="flex items-center gap-5 p-4">
            <span className="flex size-6 shrink-0 items-center justify-center text-xs font-black italic text-primary/50">
              #{idx + 1}
            </span>
            <div className="size-14 shrink-0 rounded-[18px] glass-card p-1.5 shadow-inner">
              <div className="flex size-full items-center justify-center rounded-[14px] bg-background shadow-xs">
                {g.icon_url ? (
                  <img
                    src={normalizeUrl(g.icon_url)}
                    alt=""
                    className="size-9 object-contain drop-shadow-sm"
                    onError={(e: SyntheticEvent<HTMLImageElement>) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  />
                ) : (
                  <div className="flex size-full items-center justify-center text-lg">📖</div>
                )}
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="text-[15px] font-black tracking-tight text-foreground transition-all group-hover:text-primary leading-tight line-clamp-2">
                {g.title}
              </h4>
              <div className="mt-2 flex items-center gap-2 text-[10px] font-black text-primary/80 uppercase tracking-wider">
                <div className="flex items-center gap-1.5 rounded-lg bg-primary/10 px-2 py-0.5">
                  <Eye className="size-3" />
                  <span>{g.views >= 1000 ? `${(g.views / 1000).toFixed(1)}k` : g.views}</span>
                </div>
                <div className="h-1 w-1 rounded-full bg-primary/20" />
                <span>Most Viewed</span>
              </div>
            </div>
            <div className="flex size-8 items-center justify-center rounded-full bg-muted/30 transition-all group-hover:bg-primary group-hover:text-white">
              <ChevronRight className="size-4" />
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

const StatsSkeleton = () => (
  <div className="flex flex-col gap-2">
    {[...Array(3)].map((_, i) => (
      <Skeleton key={i} className="h-16 w-full rounded-2xl bg-muted/50" />
    ))}
  </div>
)
