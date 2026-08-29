import { motion } from 'framer-motion'
import { type FC, type RefObject, useEffect, useState } from 'react'

interface ReadingProgressBarProps {
  targetRef?: RefObject<HTMLElement | null>
}

export const ReadingProgressBar: FC<ReadingProgressBarProps> = ({ targetRef }) => {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const el = targetRef?.current || window
    const handleScroll = () => {
      if (targetRef?.current) {
        const { scrollTop, scrollHeight, clientHeight } = targetRef.current
        const maxScroll = scrollHeight - clientHeight
        const currentProgress = maxScroll > 0 ? (scrollTop / maxScroll) * 100 : 0
        setProgress(Math.min(100, Math.max(0, currentProgress)))
      } else {
        const scrollTop = window.scrollY
        const docHeight = document.documentElement.scrollHeight - window.innerHeight
        const currentProgress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0
        setProgress(Math.min(100, Math.max(0, currentProgress)))
      }
    }

    el.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll()
    return () => el.removeEventListener('scroll', handleScroll)
  }, [targetRef])

  if (progress <= 0) return null

  return (
    <div className="fixed top-0 left-0 right-0 z-50 h-[3px] bg-rose-500/10 backdrop-blur-xs pointer-events-none">
      <motion.div
        className="h-full bg-gradient-to-r from-rose-500 via-amber-400 to-rose-400 shadow-[0_0_8px_rgba(244,63,94,0.6)]"
        style={{ width: `${progress}%` }}
        initial={{ width: 0 }}
        animate={{ width: `${progress}%` }}
        transition={{ ease: 'easeOut', duration: 0.1 }}
      />
    </div>
  )
}
