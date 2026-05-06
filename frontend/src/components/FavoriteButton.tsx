import { Button } from '@/components/ui/button'
import { haptic } from '@/lib/haptic'
import { Star } from '@/lib/icons'
import { cn } from '@/lib/utils'
import type { FC, MouseEvent } from 'react'
import type React from 'react'

interface FavoriteButtonProps {
  isFav: boolean
  onToggle: () => void
  size?: number
  className?: string
}

/**
 * FavoriteButton refactored with TSX and premium shadcn/ui visuals.
 * Includes haptic feedback and scale animations on toggle.
 */
export const FavoriteButton: FC<FavoriteButtonProps> = ({
  isFav,
  onToggle,
  size = 40,
  className,
}) => {
  const handle = (e: MouseEvent) => {
    e.stopPropagation()
    haptic.success?.()
    onToggle()
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      className={cn(
        'rounded-full transition-all active:scale-90',
        isFav
          ? 'text-yellow-500 hover:text-yellow-600 bg-yellow-500/10 hover:bg-yellow-500/20'
          : 'text-muted-foreground/40 hover:text-muted-foreground/60',
        className
      )}
      style={{ width: size, height: size }}
      onClick={handle}
      title={isFav ? 'Убрать из избранного' : 'Добавить в избранное'}
    >
      <Star
        className={cn('transition-all', isFav ? 'fill-current' : 'fill-none')}
        style={{ width: size * 0.5, height: size * 0.5 }}
      />
    </Button>
  )
}

export default FavoriteButton
