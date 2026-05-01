import { haptic } from '@/lib/haptic'
import { ArrowLeft, Menu } from '@/lib/icons'
import { useAppEnv } from '@/hooks/useAppEnv'
import { cn } from '@/lib/utils'
import type React from 'react'
import { useCallback, useEffect, useRef, useState } from 'react'

const HOLD_MS = 600

interface FabButtonProps {
  visible: boolean
  label: string
  onBack: () => void
  onHoldComplete: () => void
}

/**
 * FabButton refactored with TSX and premium styling.
 * Implements a "Hold for Menu" interaction with visual feedback and haptics.
 * Design is optimized for thumb-reachability on mobile devices.
 */
export const FabButton: React.FC<FabButtonProps> = ({ visible, label, onBack, onHoldComplete }) => {
  const { isTMA } = useAppEnv()
  const [holding, setHolding] = useState(false)
  const [progress, setProgress] = useState(0)
  const timer = useRef<NodeJS.Timeout | null>(null)
  const animFrame = useRef<number | null>(null)
  const startTime = useRef<number | null>(null)
  const triggered = useRef(false)

  const stopAnimation = useCallback(() => {
    if (animFrame.current) cancelAnimationFrame(animFrame.current)
    startTime.current = null
    setProgress(0)
  }, [])

  const animate = useCallback((timestamp: number) => {
    if (!startTime.current) startTime.current = timestamp
    const elapsed = timestamp - startTime.current
    const p = Math.min(elapsed / HOLD_MS, 1)
    setProgress(p)

    if (p < 1) {
      animFrame.current = requestAnimationFrame(animate)
    }
  }, [])

  const onDown = (e: React.PointerEvent) => {
    // Only handle primary pointer (usually touch/left click)
    if (e.button !== 0 && e.pointerType === 'mouse') return

    triggered.current = false
    setHolding(true)
    haptic.light?.()

    startTime.current = null
    animFrame.current = requestAnimationFrame(animate)

    timer.current = setTimeout(() => {
      triggered.current = true
      setHolding(false)
      haptic.heavy?.()
      stopAnimation()
      onHoldComplete?.()
    }, HOLD_MS)
  }

  const cancel = useCallback(() => {
    if (timer.current) clearTimeout(timer.current)
    setHolding(false)
    stopAnimation()
  }, [stopAnimation])

  const onUp = (e: React.PointerEvent) => {
    if (holding || !triggered.current) {
      cancel()
      if (!triggered.current) {
        haptic.medium?.()
        // В телеге тап сразу открывает меню, так как "Назад" уже есть нативный
        if (isTMA) {
          onHoldComplete?.()
        } else {
          onBack?.()
        }
      }
    }
  }

  // Handle case where pointer leaves or cancels
  useEffect(() => {
    return () => cancel()
  }, [cancel])

  return (
    <div
      className={cn(
        'fixed bottom-8 left-1/2 z-50 -translate-x-1/2 transition-all duration-500 ease-[cubic-bezier(0.23,1,0.32,1)]',
        visible
          ? 'pointer-events-auto translate-y-0 opacity-100'
          : 'pointer-events-none translate-y-20 opacity-0'
      )}
    >
      <button
        className={cn(
          'relative flex h-14 items-center gap-2 overflow-hidden rounded-full bg-primary px-8 text-sm font-black text-primary-foreground shadow-2xl shadow-primary/40 transition-all select-none',
          holding ? 'scale-90 brightness-110' : 'scale-100 hover:scale-105 active:scale-95'
        )}
        onPointerDown={onDown}
        onPointerUp={onUp}
        onPointerLeave={cancel}
        onPointerCancel={cancel}
        onContextMenu={(e) => e.preventDefault()}
        style={{ touchAction: 'none' }}
        aria-label={isTMA ? 'Открыть меню навигации' : `Вернуться назад к ${label}`}
      >
        <div
          className="absolute inset-0 bg-white/20 transition-opacity"
          style={{
            width: `${progress * 100}%`,
            opacity: holding ? 1 : 0,
          }}
        />

        {isTMA ? (
          <Menu className={cn('size-4 transition-transform', holding && 'scale-110')} />
        ) : (
          <ArrowLeft className={cn('size-4 transition-transform', holding && '-translate-x-1')} />
        )}
        <span className="tracking-tight">{isTMA ? 'Меню' : label}</span>

        {/* Subtle hint that fades in on hover (wide screens) or long-press start */}
        <span
          className={cn(
            'absolute inset-0 flex items-center justify-center bg-primary text-[10px] font-black uppercase tracking-widest text-primary-foreground transition-all duration-300',
            holding ? 'translate-y-0 opacity-100' : 'translate-y-full opacity-0'
          )}
        >
          <Menu className="mr-2 size-3 animate-pulse" />
          Меню
        </span>
      </button>

      {/* Decorative pulse ring when holding */}
      {holding && (
        <div className="absolute inset-0 -z-10 animate-ping rounded-full bg-primary/20" />
      )}
    </div>
  )
}

export default FabButton
