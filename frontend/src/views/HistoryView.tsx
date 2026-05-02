import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { haptic } from '@/lib/haptic'
import { ChevronRight, Clock } from '@/lib/icons'
import { normalizeUrl } from '@/lib/utils'
import { motion } from 'framer-motion'
import { FC, SyntheticEvent } from 'react'

import type { HistoryItem } from '@/hooks/useHistory'

interface HistoryViewProps {
  history: HistoryItem[]
  onSelectGuide: (key: string, title?: string, icon?: string) => void
}

/**
 * HistoryView refactored with TSX, shadcn/ui and premium visuals.
 */
export const HistoryView: FC<HistoryViewProps> = ({ history, onSelectGuide }) => {
  if (!history || history.length === 0) {
    return (
      <div className="flex h-[80vh] flex-col items-center justify-center px-10 text-center animate-in fade-in zoom-in duration-500">
        <div className="flex size-24 items-center justify-center rounded-[32px] bg-muted text-4xl shadow-inner mb-6 ring-1 ring-border/50">
          🕒
        </div>
        <h3 className="text-xl font-black tracking-tight text-foreground mb-2">История пуста</h3>
        <p className="text-sm font-medium text-muted-foreground leading-relaxed">
          Здесь появятся гайды, которые вы недавно открывали. Исследуйте базу знаний, чтобы
          наполнить историю!
        </p>
      </div>
    )
  }

  return (
    <div className="view-scroll flex-1 overflow-y-auto px-5 py-6">
      <div className="grid grid-cols-1 gap-4 pb-32">
        {history.map((item, idx) => (
          <Card
            key={`${item.key}-${idx}`}
            className="group cursor-pointer border-border/50 bg-card transition-all hover:bg-accent active:scale-[0.98]"
            onClick={() => {
              haptic.light()
              onSelectGuide(item.key, item.title, item.icon)
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
                  {item.title || item.key}
                </h3>
                <div className="mt-1 flex items-center gap-2">
                  <Badge
                    variant="outline"
                    className="rounded-md px-1.5 py-0 text-[9px] font-bold uppercase tracking-wider text-muted-foreground/60 border-border/30"
                  >
                    {idx === 0 ? 'Только что' : `${idx + 1} назад`}
                  </Badge>
                </div>
              </div>
              <ChevronRight className="size-5 text-muted-foreground/30 transition-transform group-hover:translate-x-0.5" />
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default HistoryView
