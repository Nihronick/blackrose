import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { haptic } from '@/lib/haptic'
import { ChevronRight, FileText, Folder, Search } from '@/lib/icons'
import { isLanguageKey } from '@/lib/language'
import { normalizeUrl } from '@/lib/utils'
import { useAppStore } from '@/store'
import { useSuspenseQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import type { FC, SyntheticEvent } from 'react'
import type React from 'react'
import { useMemo } from 'react'
import { categoriesApi } from '../api'
import type { Category } from '../types'

interface Guide {
  key: string
  title: string
  icon?: string
  category_key: string
}

interface CategorySearchProps {
  query: string
  onSelectGuide: (key: string) => void
  onTagClick: (tag: string) => void
  categories: Category[]
}

export const CategorySearch: FC<CategorySearchProps> = ({
  query,
  onSelectGuide,
  onTagClick,
  categories,
}) => {
  const { data: searchResults } = useSuspenseQuery({
    queryKey: ['categories', 'search', query],
    queryFn: async () => {
      const result = await categoriesApi.search(query)()
      if (result._tag === 'Left') throw result.left
      return result.right
    },
  })
  const language = useAppStore((state) => state.language)

  const filteredResults = useMemo(
    () => searchResults.filter((item) => isLanguageKey(item.key, language)),
    [searchResults, language]
  )

  const getCatTitle = (key: string) => categories?.find((c) => c.key === key)?.title ?? key

  return (
    <div className="grid grid-cols-1 gap-5 pt-6">
      {filteredResults.length === 0 ? (
        <div className="col-span-full py-10 w-full animate-in fade-in duration-300">
          <Card className="glass-card relative overflow-hidden rounded-[32px] border border-border/10 bg-gradient-to-br from-primary/5 via-card/50 to-transparent p-8 text-center shadow-glow">
            {/* Pulsing decoration lights */}
            <div className="absolute -right-8 -top-8 size-32 bg-primary/10 rounded-full blur-[45px] animate-pulse" />
            <div className="absolute -left-12 -bottom-12 size-36 bg-violet-500/5 rounded-full blur-[50px]" />

            <div className="relative z-10 flex flex-col items-center gap-4">
              <div className="flex size-16 items-center justify-center rounded-[24px] bg-primary/10 border border-primary/20 shadow-inner text-primary">
                <Search className="size-8 text-primary animate-pulse" />
              </div>
              <div>
                <h4 className="text-base font-black tracking-normal text-foreground font-heading">
                  Ничего не найдено
                </h4>
                <p className="text-xs font-medium text-muted-foreground/80 max-w-sm mx-auto mt-2 leading-relaxed">
                  Мы обыскали всю базу знаний, но не смогли найти совпадений для вашего запроса.
                  Попробуйте ввести другие ключевые слова.
                </p>
              </div>
            </div>
          </Card>
        </div>
      ) : (
        filteredResults.map((item) => (
          <Card
            key={item.key}
            className="group cursor-pointer overflow-hidden border-border/20 glass-card transition-all hover:brightness-105 active:scale-[0.98]"
            onClick={() => {
              haptic.light()
              onSelectGuide(item.key)
            }}
          >
            <CardContent className="flex flex-col p-5">
              <div className="flex items-start gap-5">
                <div className="flex size-14 shrink-0 items-center justify-center rounded-[20px] bg-primary/10 transition-all group-hover:bg-primary/20 shadow-inner">
                  {item.icon ? (
                    <motion.img
                      layoutId={`guide-icon-${item.key}`}
                      src={normalizeUrl(item.icon)}
                      alt=""
                      className="size-10 object-contain drop-shadow-sm"
                      onError={(e: SyntheticEvent<HTMLImageElement>) => {
                        e.currentTarget.style.display = 'none'
                      }}
                    />
                  ) : (
                    <FileText className="size-6 text-primary" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest text-primary">
                    <Folder className="size-3" />
                    <span className="truncate">{getCatTitle(item.category_key)}</span>
                  </div>
                  <h3 className="mt-1 line-clamp-2 text-[17px] font-black leading-tight text-foreground transition-all group-hover:text-primary">
                    {item.title}
                  </h3>
                </div>
                <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted/30 transition-all group-hover:bg-primary group-hover:text-white">
                  <ChevronRight className="size-4" />
                </div>
              </div>

              {item.tags && item.tags.length > 0 && (
                <div className="mt-5 flex flex-wrap gap-2" onClick={(e) => e.stopPropagation()}>
                  {item.tags.slice(0, 5).map((t: string) => (
                    <Badge
                      key={t}
                      variant="outline"
                      className="cursor-pointer border-none bg-primary/5 px-2.5 py-1 text-[11px] font-bold text-primary transition-all hover:bg-primary hover:text-white"
                      onClick={() => {
                        haptic.light()
                        onTagClick(t)
                      }}
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
  )
}
