import { FavoriteButton } from '@/components/FavoriteButton'
import { Card, CardContent } from '@/components/ui/card'
import { haptic } from '@/lib/haptic'
import { ChevronRight, Star } from '@/lib/icons'
import { normalizeUrl } from '@/lib/utils'
import { motion } from 'framer-motion'
import type { FC, SyntheticEvent } from 'react'

import type { FavoriteGuide } from '@/hooks/useFavorites'

interface FavoritesViewProps {
  favorites: FavoriteGuide[]
  onSelectGuide: (key: string) => void
  onToggle: (item: FavoriteGuide) => void
}

/**
 * FavoritesView refactored with TSX, shadcn/ui and premium visuals.
 */
export const FavoritesView: FC<FavoritesViewProps> = ({ favorites, onSelectGuide, onToggle }) => {
  if (favorites.length === 0) {
    return (
      <div className="flex h-[80vh] flex-col items-center justify-center px-10 text-center animate-in fade-in zoom-in duration-500">
        <div className="flex size-24 items-center justify-center rounded-[32px] bg-muted text-4xl shadow-inner mb-6 ring-1 ring-border/50">
          ⭐
        </div>
        <h3 className="text-xl font-black tracking-tight text-foreground mb-2">Избранное пусто</h3>
        <p className="text-sm font-medium text-muted-foreground leading-relaxed">
          Нажмите на <span className="text-yellow-500 font-bold">⭐</span> в любом гайде, чтобы
          сохранить его здесь для быстрого доступа.
        </p>
      </div>
    )
  }

  return (
    <div className="view-scroll flex-1 overflow-y-auto px-5 py-6">
      <div className="grid grid-cols-1 gap-4 pb-32">
        {favorites.map((item) => (
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
              <div className="flex-1 min-w-0">
                <h3 className="truncate text-base font-bold tracking-tight text-foreground leading-tight">
                  {item.title}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <FavoriteButton isFav={true} onToggle={() => onToggle(item)} size={36} />
                <ChevronRight className="size-5 text-muted-foreground/30 transition-transform group-hover:translate-x-0.5" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default FavoritesView
