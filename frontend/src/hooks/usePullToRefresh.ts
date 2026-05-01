import Honeybadger from '@honeybadger-io/js'
import { type MutableRefObject, useEffect, useRef, useState } from 'react'
import { haptic } from '../lib/haptic'

export const PTR_THRESHOLD = 80

/**
 * usePullToRefresh refactored with TypeScript and HIG patterns.
 * Provides smooth, bounce-resistant scrolling and haptic-triggered refresh.
 */
export function usePullToRefresh(
  scrollRef: MutableRefObject<HTMLElement | null>,
  onRefresh: () => Promise<void>,
  enabled = true
) {
  const [pullY, setPullY] = useState(0)
  const [refreshing, setRefreshing] = useState(false)
  const startY = useRef<number | null>(null)
  const pulling = useRef(false)
  const hapticTriggered = useRef(false)

  useEffect(() => {
    if (!enabled) return
    const el = scrollRef.current
    if (!el) return

    const onTouchStart = (e: TouchEvent) => {
      // Only start pulling if at the top of the viewport
      if (el.scrollTop <= 1) {
        startY.current = e.touches[0].clientY
        pulling.current = true
        hapticTriggered.current = false
      }
    }

    const onTouchMove = (e: TouchEvent) => {
      if (!pulling.current || startY.current === null) return

      const dy = e.touches[0].clientY - startY.current

      if (dy > 0) {
        // Prevent scroll if pulling down
        if (el.scrollTop <= 1) {
          e.preventDefault()
          // Logarithmic resistance for natural feel
          const y = Math.min(dy * 0.4, PTR_THRESHOLD + 40)
          setPullY(y)

          if (!hapticTriggered.current && y >= PTR_THRESHOLD) {
            hapticTriggered.current = true
            haptic.select()
          }
        }
      } else {
        // If they pull up, cancel the PTR logic
        pulling.current = false
      }
    }

    const onTouchEnd = () => {
      if (!pulling.current) return

      const finalY = pullY
      pulling.current = false
      startY.current = null

      if (finalY >= PTR_THRESHOLD) {
        setRefreshing(true)
        haptic.success()

        onRefresh()
          .catch((err) => {
            if (import.meta.env.VITE_HONEYBADGER_API_KEY) {
              Honeybadger.notify(err, { context: { source: 'usePullToRefresh' } })
            }
          })
          .finally(() => {
            setRefreshing(false)
            setPullY(0)
          })
      } else {
        setPullY(0)
      }
    }

    el.addEventListener('touchstart', onTouchStart, { passive: true })
    el.addEventListener('touchmove', onTouchMove, { passive: false })
    el.addEventListener('touchend', onTouchEnd)

    return () => {
      el.removeEventListener('touchstart', onTouchStart)
      el.removeEventListener('touchmove', onTouchMove)
      el.removeEventListener('touchend', onTouchEnd)
    }
  }, [enabled, onRefresh, scrollRef, pullY])

  return { pullY, refreshing }
}
