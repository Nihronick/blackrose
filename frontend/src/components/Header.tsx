import { Button } from '@/components/ui/button'
import { useAppEnv } from '@/hooks/useAppEnv'
import { haptic } from '@/lib/haptic'
import { ChevronLeft, Home } from '@/lib/icons'
import { useAppNavigation } from '@/lib/navigation'
import type { FC } from 'react'

interface HeaderProps {
  title: string
  onBack?: () => void
}

export const Header: FC<HeaderProps> = ({ title, onBack }) => {
  const { isTMA } = useAppEnv()
  const { push } = useAppNavigation()
  const showBackButton = !!onBack && !isTMA

  return (
    <header className="sticky top-0 z-50 flex items-center justify-between gap-3 border-b border-border/10 bg-background/85 container-padding backdrop-blur-xl transition-all safe-header pb-2">
      <div className="flex items-center gap-2 min-w-0 flex-1">
        {showBackButton && (
          <Button
            variant="ghost"
            size="sm"
            className="h-9 px-2.5 shrink-0 rounded-2xl transition-all active:scale-95 hover:bg-muted/60 text-muted-foreground hover:text-foreground font-bold text-xs flex items-center gap-1"
            onClick={() => {
              haptic.light()
              onBack()
            }}
            aria-label="Назад"
          >
            <ChevronLeft className="size-4" />
            <span className="hidden sm:inline font-heading">Назад</span>
          </Button>
        )}
        <h1 className="truncate text-sm sm:text-base font-black tracking-tight text-foreground font-heading">
          {title}
        </h1>
      </div>

      <div className="flex items-center gap-1 shrink-0">
        <Button
          variant="ghost"
          size="icon"
          className="size-9 rounded-2xl hover:bg-muted/60 text-muted-foreground hover:text-primary transition-colors"
          onClick={() => {
            haptic.light()
            push({ type: 'home' })
          }}
          title="На главную"
          aria-label="На главную"
        >
          <Home className="size-4" />
        </Button>
      </div>
    </header>
  )
}
