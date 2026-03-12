import { useState, useEffect, useRef } from 'react'
import { haptic } from '../haptic'

export const PTR_THRESHOLD = 70

export function usePullToRefresh(scrollRef, onRefresh, enabled = true) {
  const [pullY, setPullY]       = useState(0)
  const [refreshing, setRefreshing] = useState(false)
  const startY    = useRef(null)
  const pulling   = useRef(false)
  const triggered = useRef(false)

  useEffect(() => {
    if (!enabled) return
    const el = scrollRef.current
    if (!el) return

    const onTouchStart = (e) => {
      if (el.scrollTop === 0) {
        startY.current  = e.touches[0].clientY
        pulling.current = true
        triggered.current = false
      }
    }

    const onTouchMove = (e) => {
      if (!pulling.current || startY.current === null) return
      const dy = e.touches[0].clientY - startY.current
      if (dy > 0) {
        e.preventDefault()
        const y = Math.min(dy * 0.45, PTR_THRESHOLD + 20)
        setPullY(y)
        if (!triggered.current && y >= PTR_THRESHOLD * 0.75) {
          triggered.current = true
          haptic.select()
        }
      }
    }

    const onTouchEnd = () => {
      if (!pulling.current) return
      pulling.current   = false
      startY.current    = null
      setPullY((prev) => {
        if (prev >= PTR_THRESHOLD) {
          setRefreshing(true)
          haptic.medium()
          onRefresh().finally(() => { setRefreshing(false); setPullY(0) })
          return 0
        }
        return 0
      })
    }

    el.addEventListener('touchstart', onTouchStart, { passive: true })
    el.addEventListener('touchmove',  onTouchMove,  { passive: false })
    el.addEventListener('touchend',   onTouchEnd)
    return () => {
      el.removeEventListener('touchstart', onTouchStart)
      el.removeEventListener('touchmove',  onTouchMove)
      el.removeEventListener('touchend',   onTouchEnd)
    }
  }, [enabled, onRefresh, scrollRef])

  return { pullY, refreshing }
}
