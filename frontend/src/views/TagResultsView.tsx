import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { apiSearch } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { ChevronRight, FileText, Folder, Hash, Search } from '@/lib/icons'
import { isLanguageKey } from '@/lib/language'
import { normalizeUrl } from '@/lib/utils'
import { useAppStore } from '@/store'
import { useSuspenseQuery } from '@tanstack/react-query'
import { type FC, type SyntheticEvent, useMemo } from 'react'

interface TagResultsItem {
  key: string
  title: string
  icon_url?: string
  category_key: string
}

interface TagResultsViewProps {
  tag: string
  onSelectGuide: (key: string) => void
}

/**
 * TagResultsView refactored with TSX, Suspense, and premium shadcn/ui design.
 */
export const TagResultsView: FC<TagResultsViewProps> = ({ tag, onSelectGuide }) => {
  const { data: searchData } = useSuspenseQuery({
    queryKey: ['tag-search', tag],
    queryFn: () => apiSearch(tag),
  })
  const language = useAppStore((state) => state.language)

  // Data extraction with safe array fallback
  const items = useMemo<TagResultsItem[]>(
    () =>
      (Array.isArray(searchData?.results) ? searchData.results : []).filter((item) =>
        isLanguageKey(item.key, language)
      ),
    [searchData, language]
  )

  return (
    <div className="view-scroll flex-1 overflow-y-auto container-padding py-4 sm:py-6">
      <div className="mb-6 flex items-center gap-3">
        <div className="flex size-10 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
          <Hash className="size-5" />
        </div>
        <div>
          <h2 className="text-xl font-black tracking-tight text-foreground leading-tight">
            #{tag}
          </h2>
          <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/60 mt-0.5">
            Результаты поиска
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 pb-32">
        {!items || items.length === 0 ? (
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
                    Гайдов с тегом #{tag} пока нет в нашей базе.
                  </p>
                </div>
              </div>
            </Card>
          </div>
        ) : (
          items.map((item: TagResultsItem) => (
            <Card
              key={item.key}
              className="group cursor-pointer overflow-hidden border-border/20 glass-card transition-all hover:brightness-105 active:scale-[0.98]"
              onClick={() => {
                haptic.light()
                onSelectGuide(item.key)
              }}
            >
              <CardContent className="flex items-center gap-5 p-5">
                <div className="flex size-14 shrink-0 items-center justify-center rounded-[20px] bg-primary/10 transition-all group-hover:bg-primary/20 shadow-inner">
                  {item.icon_url ? (
                    <img
                      src={normalizeUrl(item.icon_url)}
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
                    <span>{item.category_key}</span>
                  </div>
                  <h3 className="mt-1 line-clamp-2 text-[17px] font-black leading-tight text-foreground transition-all group-hover:text-primary">
                    {item.title}
                  </h3>
                </div>
                <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted/30 transition-all group-hover:bg-primary group-hover:text-white">
                  <ChevronRight className="size-4" />
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}
