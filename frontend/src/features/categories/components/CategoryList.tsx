// @ts-nocheck
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useSubscriptions } from '@/hooks/useSubscriptions'
import { apiFetch } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { Bell, ChevronRight, Database, Folder, RefreshCw, ShieldAlert } from '@/lib/icons'
import { normalizeUrl, pluralize } from '@/lib/utils'
import { useQueryClient } from '@tanstack/react-query'
import { type FC, type SyntheticEvent, useRef } from 'react'
import type { Category, Guide } from '../types'

interface CategoryListProps {
  categories: Category[]
  onSelectCategory: (category: Category) => void
  isLoading?: boolean
}

export const CategoryList: FC<CategoryListProps> = ({
  categories,
  onSelectCategory,
  isLoading,
}) => {
  const { isSubscribed, toggle } = useSubscriptions()
  const queryClient = useQueryClient()

  const prefetchTimer = useRef<NodeJS.Timeout | null>(null)

  const prefetchCategory = (key: string) => {
    if (prefetchTimer.current) clearTimeout(prefetchTimer.current)
    prefetchTimer.current = setTimeout(() => {
      queryClient.prefetchQuery({
        queryKey: ['category', key],
        queryFn: () => apiFetch<{ items: Guide[] }>(`/api/category/${key}`).then((r) => r.items),
        staleTime: 60_000,
      })
    }, 150)
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-3 sm:gap-4 pt-4 sm:pt-6 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div
            key={i}
            className="h-[88px] sm:h-[104px] rounded-3xl border border-border/10 skeleton"
          />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:gap-4 pt-4 sm:pt-6 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4 stagger-in">
      {categories.length === 0 ? (
        <div className="col-span-full py-10 w-full">
          <Card className="glass-card relative overflow-hidden rounded-[32px] border border-border/10 bg-gradient-to-br from-primary/5 via-card/50 to-transparent p-8 text-center shadow-glow transition-all duration-300">
            {/* Pulsing decoration lights */}
            <div className="absolute -right-8 -top-8 size-32 bg-primary/10 rounded-full blur-[45px] animate-pulse" />
            <div className="absolute -left-12 -bottom-12 size-36 bg-violet-500/5 rounded-full blur-[50px]" />

            <div className="relative z-10 flex flex-col items-center gap-4">
              <div className="flex size-16 items-center justify-center rounded-[24px] bg-primary/10 border border-primary/20 shadow-inner text-primary">
                <Database className="size-8 text-primary animate-pulse" />
              </div>
              <div>
                <h4 className="text-base font-black tracking-normal text-foreground font-heading">
                  Разделы не найдены
                </h4>
                <p className="text-xs font-medium text-muted-foreground/80 max-w-md mx-auto mt-2 leading-relaxed">
                  Похоже, база данных пуста или находится в процессе загрузки. Пожалуйста, обновите
                  страницу или попробуйте позже.
                </p>
              </div>

              <Button
                variant="outline"
                size="sm"
                className="mt-2 h-10 rounded-2xl bg-primary/10 border-primary/20 text-primary font-bold px-6 hover:bg-primary/15 hover:border-primary/40 transition-all active:scale-95 shadow-soft font-heading flex items-center gap-2 cursor-pointer"
                onClick={() => {
                  haptic.medium()
                  window.location.reload()
                }}
              >
                <RefreshCw className="size-4 animate-spin-slow" />
                <span>Обновить</span>
              </Button>
            </div>
          </Card>
        </div>
      ) : (
        categories.map((item) => {
          const subscribed = isSubscribed(item.key)
          return (
            <Card
              key={item.key}
              className="group relative cursor-pointer overflow-hidden rounded-3xl rose-bento-card border-rose-500/20 active:scale-[0.98] animate-in fade-in slide-in-from-bottom-2"
              onMouseEnter={() => prefetchCategory(item.key)}
              onTouchStart={() => prefetchCategory(item.key)}
              onClick={() => {
                haptic.light()
                onSelectCategory(item)
              }}
            >
              <CardContent className="flex items-center gap-3 sm:gap-4 p-3.5 sm:p-5">
                <div className="flex size-12 sm:size-14 shrink-0 items-center justify-center rounded-2xl sm:rounded-[22px] bg-rose-500/10 border border-rose-500/20 transition-all group-hover:bg-rose-500/20 group-hover:rotate-3 shadow-inner">
                  {item.icon ? (
                    <img
                      src={normalizeUrl(item.icon)}
                      alt=""
                      loading="lazy"
                      decoding="async"
                      className="size-8 sm:size-10 object-contain drop-shadow-md"
                      onError={(e: SyntheticEvent<HTMLImageElement>) => {
                        e.currentTarget.style.display = 'none'
                      }}
                    />
                  ) : (
                    <Folder className="size-6 text-rose-400" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="truncate text-base sm:text-lg font-black font-heading tracking-normal text-foreground uppercase group-hover:text-rose-400 transition-colors">
                    {item.title}
                  </h3>
                  <div className="mt-1 flex items-center gap-2">
                    {item.count !== undefined && (
                      <Badge
                        variant="secondary"
                        className="rounded-xl border-none bg-rose-500/10 px-2 py-0.5 text-[11px] font-black text-rose-400 font-mono tabular-nums"
                      >
                        {item.count} {pluralize(item.count, 'гайд', 'гайда', 'гайдов')}
                      </Badge>
                    )}
                    {subscribed && (
                      <Badge className="bg-amber-500/15 text-amber-400 border border-amber-500/30 text-[10px] font-black uppercase">
                        Подписан
                      </Badge>
                    )}
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  className={`size-10 rounded-2xl transition-all active:scale-90 ${subscribed ? 'bg-primary/20 text-primary' : 'bg-muted/40 text-muted-foreground/40 hover:bg-muted'}`}
                  onClick={(e) => {
                    e.stopPropagation()
                    haptic.medium()
                    toggle(item.key)
                  }}
                >
                  <Bell className={`size-4 ${subscribed ? 'fill-current' : ''}`} />
                </Button>
              </CardContent>
            </Card>
          )
        })
      )}
    </div>
  )
}
