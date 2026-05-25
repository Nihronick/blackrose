import { Button } from '@/components/ui/button'
import { useAppEnv } from '@/hooks/useAppEnv'
import { haptic } from '@/lib/haptic'
import { ChevronLeft } from '@/lib/icons'
import type { AppLanguage } from '@/store'
import type { FC } from 'react'
import type React from 'react'

interface HeaderProps {
  title: string
  onBack?: () => void
}

export const Header: FC<HeaderProps> = ({ title, onBack }) => {
  const { isTMA } = useAppEnv()
  const showBackButton = onBack && !isTMA

  return (
    <header className="sticky top-0 z-50 flex h-14 items-center gap-3 border-b border-border/5 bg-background/80 container-padding backdrop-blur-xl transition-all">
      {showBackButton && (
        <Button
          variant="ghost"
          size="icon"
          className="size-10 shrink-0 rounded-2xl transition-all active:scale-90 hover:bg-muted/50"
          onClick={() => {
            haptic.light()
            onBack()
          }}
          aria-label="Назад"
        >
          <ChevronLeft className="size-5" />
        </Button>
      )}
      <div className="min-w-0 flex-1">
        <h1 className="truncate text-base font-black tracking-tight text-foreground transition-all font-heading">
          {title}
        </h1>
      </div>
    </header>
  )
}
