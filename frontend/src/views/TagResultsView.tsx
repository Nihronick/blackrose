import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { apiSearch } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { ChevronRight, Folder, Hash } from '@/lib/icons'
import { isLanguageKey } from '@/lib/language'
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
    <div className="view-scroll flex-1 overflow-y-auto px-5 py-6">
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
          <div className="flex h-[50vh] flex-col items-center justify-center text-center animate-in fade-in zoom-in duration-500">
            <div className="flex size-20 items-center justify-center rounded-full bg-muted mb-4">
              <Hash className="size-10 text-muted-foreground/20" />
            </div>
            <h3 className="text-lg font-bold text-foreground">Ничего не найдено</h3>
            <p className="max-w-[200px] text-xs font-medium text-muted-foreground/60 mt-1">
              Гайдов с тегом #{tag} пока нет в нашей базе.
            </p>
          </div>
        ) : (
          items.map((item: TagResultsItem) => (
            <Card
              key={item.key}
              className="group cursor-pointer border-border/50 bg-card transition-all hover:bg-accent active:scale-[0.98]"
              onClick={() => {
                haptic.light()
                onSelectGuide(item.key)
              }}
            >
              <CardContent className="flex items-center gap-4 p-4">
                <div className="flex size-14 shrink-0 items-center justify-center rounded-2xl bg-muted transition-colors group-hover:bg-background">
                  {item.icon_url ? (
                    <img
                      src={item.icon_url}
                      alt=""
                      className="size-10 object-contain"
                      onError={(e: SyntheticEvent<HTMLImageElement>) => {
                        e.currentTarget.style.display = 'none'
                      }}
                    />
                  ) : (
                    <span className="text-2xl">📄</span>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-muted-foreground/60 mb-1">
                    <Folder className="size-3" />
                    <span>{item.category_key}</span>
                  </div>
                  <h3 className="truncate text-base font-bold tracking-tight text-foreground leading-tight">
                    {item.title}
                  </h3>
                </div>
                <ChevronRight className="size-5 text-muted-foreground/30 transition-transform group-hover:translate-x-0.5" />
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  )
}

export default TagResultsView
