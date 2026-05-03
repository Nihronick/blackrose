import { FC, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'

interface GuideContentProps {
  html: string
  onImageClick: (src: string) => void
  onCyberlinkClick: (data: { key: string; title: string; icon: string }) => void
}

export const GuideContent: FC<GuideContentProps> = ({ html, onImageClick, onCyberlinkClick }) => {
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = contentRef.current
    if (!el) return

    const handleImageClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (target.tagName === 'IMG' && target.classList.contains('guide-img')) {
        onImageClick((target as HTMLImageElement).src)
      }
    }

    const handleCyberlinkClick = (e: MouseEvent) => {
      const target = (e.target as HTMLElement).closest('.guide-cyberlink') as HTMLElement
      if (target) {
        e.preventDefault()
        const data = {
          key: target.dataset.guideKey || '',
          title: target.dataset.guideTitle || '',
          icon: target.dataset.guideIcon || '',
        }
        onCyberlinkClick(data)
      }
    }

    el.addEventListener('click', handleImageClick)
    el.addEventListener('click', handleCyberlinkClick)
    return () => {
      el.removeEventListener('click', handleImageClick)
      el.removeEventListener('click', handleCyberlinkClick)
    }
  }, [onImageClick, onCyberlinkClick])

  return (
    <motion.div
      ref={contentRef}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
      className="guide-content-wrapper prose prose-invert max-w-none"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
