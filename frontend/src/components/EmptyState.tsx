import { Button } from '@/components/ui/button'
import { motion } from 'framer-motion'
import type { FC, ReactNode } from 'react'

interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
}

export const EmptyState: FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  actionLabel,
  onAction,
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex flex-col items-center justify-center p-8 text-center my-12 max-w-md mx-auto rose-bento-card border-rose-500/20 rounded-3xl bg-card/60 shadow-2xl"
    >
      <div className="size-20 rounded-3xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mb-5 text-3xl shadow-inner animate-bounce">
        {icon || '🥀'}
      </div>
      <h3 className="text-xl font-black uppercase font-heading text-foreground mb-2">{title}</h3>
      <p className="text-xs font-medium text-muted-foreground leading-relaxed mb-6">
        {description}
      </p>

      {actionLabel && onAction && (
        <Button
          size="sm"
          className="rose-glow-btn h-11 px-6 text-xs uppercase font-heading cursor-pointer"
          onClick={onAction}
        >
          {actionLabel}
        </Button>
      )}
    </motion.div>
  )
}
