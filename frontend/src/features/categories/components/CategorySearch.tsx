import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { haptic } from '@/lib/haptic'
import { ChevronRight, Folder } from '@/lib/icons'
import { isLanguageKey } from '@/lib/language'
import { normalizeUrl } from '@/lib/utils'
import { useAppStore } from '@/store'
import { useSuspenseQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
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

export const CategorySearch: React.FC<CategorySearchProps> = ({
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
    <div className="grid grid-cols-1 gap-5 px-5 pb-32 pt-6">
      {filteredResults.length === 0 ? (
        <div className="py-20 text-center opacity-40">
          <Folder className="mx-auto mb-4 size-16 opacity-20" />
          <p className="text-lg font-bold">Ничего не найдено</p>
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
                      onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
                        e.currentTarget.style.display = 'none'
                      }}
                    />
                  ) : (
                    <motion.span layoutId={`guide-icon-${item.key}`} className="text-2xl">
                      📄
                    </motion.span>
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
