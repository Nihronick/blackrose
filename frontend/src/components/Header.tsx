import { Button } from '@/components/ui/button'
import { useAppEnv } from '@/hooks/useAppEnv'
import { haptic } from '@/lib/haptic'
import { ChevronLeft } from '@/lib/icons'
import type { AppLanguage } from '@/store'
import type React from 'react'

interface HeaderProps {
  title: string
  onBack?: () => void
}

export const Header: React.FC<HeaderProps> = ({ title, onBack }) => {
  const { isTMA } = useAppEnv()
  const showBackButton = onBack && !isTMA

  return (
    <header className="sticky top-0 z-50 flex h-14 items-center gap-3 border-b bg-background/80 px-4 backdrop-blur-xl transition-all">
      {showBackButton && (
        <Button
          variant="ghost"
          size="icon"
          className="size-9 h-auto shrink-0 transition-transform active:scale-90"
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
        <h1 className="truncate text-lg font-bold tracking-tight text-foreground transition-all">
          {title}
        </h1>
      </div>
    </header>
  )
}
