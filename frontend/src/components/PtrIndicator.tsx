import { PTR_THRESHOLD } from '@/hooks/usePullToRefresh'
import { RefreshCw } from '@/lib/icons'
import { motion } from 'framer-motion'
import type { FC } from 'react'
import type React from 'react'

interface PtrIndicatorProps {
  pullY: number
  refreshing: boolean
}

/**
 * PtrIndicator refactored with framer-motion for premium HIG feel.
 * Displays a tactile, responsive spinner that reacts to pull distance.
 */
export const PtrIndicator: FC<PtrIndicatorProps> = ({ pullY, refreshing }) => {
  const rotation = (pullY / PTR_THRESHOLD) * 360
  const opacity = Math.min(pullY / 40, 1)
  const scale = refreshing ? 1 : Math.min(pullY / PTR_THRESHOLD, 1)

  return (
    <div className="absolute left-0 right-0 top-0 flex justify-center pointer-events-none z-50">
      <motion.div
        style={{ y: refreshing ? 20 : Math.max(pullY - 40, -40), opacity }}
        animate={refreshing ? { y: 20, opacity: 1, scale: 1.1 } : { scale }}
        className="flex size-10 items-center justify-center rounded-full bg-background/80 backdrop-blur-xl border border-white/10 shadow-xl"
      >
        <motion.div
          animate={refreshing ? { rotate: 360 } : { rotate: rotation }}
          transition={
            refreshing
              ? { repeat: Number.POSITIVE_INFINITY, duration: 1, ease: 'linear' }
              : { type: 'spring', damping: 20 }
          }
        >
          <RefreshCw className="size-5 text-primary" />
        </motion.div>
      </motion.div>
    </div>
  )
}
