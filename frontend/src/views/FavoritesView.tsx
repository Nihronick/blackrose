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
import { EmptyState } from '@/components/EmptyState'

export const FavoritesView: FC<FavoritesViewProps> = ({ favorites, onSelectGuide, onToggle }) => {
  if (favorites.length === 0) {
    return (
      <EmptyState
        icon="⭐"
        title="Избранное пусто"
        description="Нажмите на звездочку ⭐ на странице любого гайда, чтобы сохранить его здесь для быстрого доступа."
      />
    )
  }

  return (
    <div className="view-scroll flex-1 overflow-y-auto container-padding py-4 sm:py-6 relative z-0">
      <div className="absolute top-0 left-0 w-full h-80 mesh-bg opacity-30 pointer-events-none -z-10" />

      <div className="section-label font-heading mb-4">
        <Star className="size-3.5 text-primary" />
        <span>Избранные гайды</span>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:gap-4 pb-28 sm:pb-32 stagger-in">
        {favorites.map((item) => (
          <Card
            key={item.key}
            className="group cursor-pointer glass-card card-elevated rounded-3xl active:scale-[0.98] hover:border-primary/30"
            onClick={() => {
              haptic.light()
              onSelectGuide(item.key)
            }}
          >
            <CardContent className="flex items-center gap-3 sm:gap-4 p-3.5 sm:p-5">
              <div className="flex size-12 sm:size-14 shrink-0 items-center justify-center rounded-2xl bg-primary/10 shadow-inner transition-colors group-hover:bg-primary/20">
                {item.icon ? (
                  <motion.img
                    layoutId={`guide-icon-${item.key}`}
                    src={normalizeUrl(item.icon)}
                    alt=""
                    className="size-8 sm:size-10 object-contain"
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
                <h3 className="line-clamp-2 text-sm sm:text-base font-black tracking-normal text-foreground/90 font-heading leading-snug break-words">
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
