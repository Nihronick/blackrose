import { Button } from '@/components/ui/button'
import { haptic } from '@/lib/haptic'
import { ChevronUp } from '@/lib/icons'
import { AnimatePresence, motion } from 'framer-motion'
import { type FC, useEffect, useState } from 'react'

export const ScrollToTopFab: FC<{ targetRef?: React.RefObject<HTMLElement | null> }> = ({
  targetRef,
}) => {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = targetRef?.current || window
    const handleScroll = () => {
      const scrollY = targetRef?.current ? targetRef.current.scrollTop : window.scrollY
      setVisible(scrollY > 300)
    }

    el.addEventListener('scroll', handleScroll)
    return () => el.removeEventListener('scroll', handleScroll)
  }, [targetRef])

  const scrollToTop = () => {
    haptic.light()
    if (targetRef?.current) {
      targetRef.current.scrollTo({ top: 0, behavior: 'smooth' })
    } else {
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }
  }

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.8, y: 20 }}
          className="fixed bottom-24 right-6 z-40"
        >
          <Button
            size="icon"
            className="size-12 rounded-full rose-glow-btn shadow-2xl border border-white/20 cursor-pointer"
            onClick={scrollToTop}
            title="Наверх"
            aria-label="Наверх"
          >
            <ChevronUp className="size-6 text-white" />
          </Button>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
