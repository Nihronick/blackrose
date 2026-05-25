import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { haptic } from '@/lib/haptic'
import { ChevronRight, Clock } from '@/lib/icons'
import { normalizeUrl } from '@/lib/utils'
import { motion } from 'framer-motion'
import type { FC, SyntheticEvent } from 'react'

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
      <div className="flex h-[80vh] flex-col items-center justify-center px-10 text-center animate-in fade-in zoom-in duration-500 relative">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-primary/10 rounded-full blur-[60px] pointer-events-none" />
        <div className="flex size-24 items-center justify-center rounded-[32px] bg-primary/10 text-primary text-4xl shadow-inner mb-6 ring-1 ring-primary/20 relative z-10">
          <Clock className="size-10" />
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
    <div className="view-scroll flex-1 overflow-y-auto container-padding py-4 sm:py-6 relative z-0">
      <div className="absolute top-0 left-0 w-full h-80 mesh-bg opacity-30 pointer-events-none -z-10" />

      <div className="section-label font-heading mb-4">
        <Clock className="size-3.5 text-primary" />
        <span>История просмотров</span>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:gap-4 pb-28 sm:pb-32 stagger-in">
        {history.map((item, idx) => (
          <Card
            key={`${item.key}-${idx}`}
            className="group cursor-pointer glass-card card-elevated rounded-3xl active:scale-[0.98] hover:border-primary/30"
            onClick={() => {
              haptic.light()
              onSelectGuide(item.key, item.title, item.icon)
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
                <h3 className="truncate text-base font-black tracking-normal text-foreground/90 font-heading">
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
