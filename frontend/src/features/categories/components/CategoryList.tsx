import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useSubscriptions } from '@/hooks/useSubscriptions'
import { haptic } from '@/lib/haptic'
import { Bell, ChevronRight } from '@/lib/icons'
import { apiFetch } from '@/lib/api'
import { normalizeUrl, pluralize } from '@/lib/utils'
import { useQueryClient } from '@tanstack/react-query'
import type React from 'react'
import type { Category } from '../types'

interface CategoryListProps {
  categories: Category[]
  onSelectCategory: (category: Category) => void
  isLoading?: boolean
}

export const CategoryList: React.FC<CategoryListProps> = ({ categories, onSelectCategory, isLoading }) => {
  const { isSubscribed, toggle } = useSubscriptions()
  const queryClient = useQueryClient()

  const prefetchTimer = React.useRef<NodeJS.Timeout | null>(null)

  const prefetchCategory = (key: string) => {
    if (prefetchTimer.current) clearTimeout(prefetchTimer.current)
    prefetchTimer.current = setTimeout(() => {
      queryClient.prefetchQuery({
        queryKey: ['category', key],
        queryFn: () => apiFetch<{ items: any }>(`/api/category/${key}`).then((r) => r.items),
        staleTime: 60_000,
      })
    }, 150) // Small delay to avoid prefetching on accidental hover/scroll
  }

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-5 px-5 pb-32 pt-6 sm:grid-cols-2 lg:grid-cols-3">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <div key={i} className="h-[104px] rounded-[32px] border border-border/10 skeleton" />
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-5 px-5 pb-32 pt-6 sm:grid-cols-2 lg:grid-cols-3">
      {categories.length === 0 ? (
        <div className="col-span-full py-20 text-center opacity-40">
          <div className="mx-auto mb-4 flex size-16 items-center justify-center rounded-3xl bg-muted/40">
            <ChevronRight className="size-8 rotate-90" />
          </div>
          <p className="text-lg font-bold">Ничего не найдено</p>
        </div>
      ) : (
        categories.map((item) => {
          const subscribed = isSubscribed(item.key)
          return (
            <Card
              key={item.key}
              className="group relative cursor-pointer overflow-hidden border-border/20 glass-card transition-all duration-500 hover:-translate-y-1.5 hover:shadow-glow hover:border-primary/30 active:scale-[0.97]"
              onMouseEnter={() => prefetchCategory(item.key)}
              onTouchStart={() => prefetchCategory(item.key)}
              onClick={() => {
                haptic.light()
                onSelectCategory(item)
              }}
            >
              <CardContent className="flex items-center gap-5 p-5">
                <div className="flex size-16 shrink-0 items-center justify-center rounded-[22px] bg-primary/10 transition-all group-hover:bg-primary/20 group-hover:rotate-3 shadow-inner">
                  {item.icon ? (
                    <img
                      src={normalizeUrl(item.icon)}
                      alt=""
                      className="size-11 object-contain drop-shadow-md"
                      onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
                        e.currentTarget.style.display = 'none'
                      }}
                    />
                  ) : (
                    <span className="text-3xl">📁</span>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="truncate text-lg font-black tracking-tight text-foreground/90">
                    {item.title}
                  </h3>
                  <div className="mt-1 flex items-center gap-2">
                    {item.count !== undefined && (
                      <Badge
                        variant="secondary"
                        className="rounded-xl border-none bg-primary/5 px-2 py-0.5 text-[11px] font-black text-primary/70"
                      >
                        {item.count} {pluralize(item.count, 'гайд', 'гайда', 'гайдов')}
                      </Badge>
                    )}
                    {subscribed && (
                      <Badge className="bg-emerald-500/10 text-emerald-400 border-0 text-[10px] font-black uppercase">
                        Active
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
