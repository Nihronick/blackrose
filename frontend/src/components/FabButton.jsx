import { useState, useRef } from 'react'
import { haptic } from '../haptic'

const HOLD_MS = 700

export function FabButton({ visible, label, onBack, onHoldComplete }) {
  const [holding, setHolding] = useState(false)
  const timer    = useRef(null)
  const midTimer = useRef(null)
  const triggered = useRef(false)

  const onDown = (e) => {
    e.preventDefault()
    triggered.current = false
    setHolding(true)

    // Промежуточная вибрация на середине — пользователь чувствует прогресс
    midTimer.current = setTimeout(() => haptic.medium(), HOLD_MS * 0.5)

    timer.current = setTimeout(() => {
      triggered.current = true
      setHolding(false)
      haptic.heavy()
      onHoldComplete?.()
    }, HOLD_MS)
  }

  const cancel = () => {
    clearTimeout(timer.current)
    clearTimeout(midTimer.current)
    setHolding(false)
  }

  const onUp = (e) => {
    e.preventDefault()
    cancel()
    if (!triggered.current) { haptic.light(); onBack?.() }
  }

  return (
    <div className={`fab-wrap${visible ? ' fab-visible' : ''}`}>
      <button
        className={`fab-btn${holding ? ' fab-holding' : ''}`}
        onPointerDown={onDown} onPointerUp={onUp}
        onPointerLeave={cancel} onPointerCancel={cancel}
        onContextMenu={e => e.preventDefault()}
      >
        {/* Прогресс-дуга вместо вращающегося кольца */}
        <svg className="fab-progress" viewBox="0 0 48 48">
          <circle cx="24" cy="24" r="20"
            fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth="3"/>
          <circle cx="24" cy="24" r="20"
            fill="none" stroke="rgba(255,255,255,0.9)" strokeWidth="3"
            strokeLinecap="round"
            strokeDasharray="125.6"
            strokeDashoffset="125.6"
            className="fab-arc"/>
        </svg>

        <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
          <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
        </svg>
        <span>{label}</span>
        <span className="fab-hint" aria-hidden="true">Удержите для меню</span>
      </button>
    </div>
  )
}
