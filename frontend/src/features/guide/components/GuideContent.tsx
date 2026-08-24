import { haptic } from '@/lib/haptic'
import { motion } from 'framer-motion'
import { type FC, useEffect, useRef } from 'react'
import { toast } from 'sonner'

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

    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement

      // 1. Image Click (Lightbox)
      if (target.tagName === 'IMG' && !target.classList.contains('inline-icon')) {
        const src = (target as HTMLImageElement).src
        if (src) {
          onImageClick(src)
          return
        }
      }

      // 2. Cyberlink Click
      const cyberlink = target.closest('.guide-cyberlink') as HTMLElement
      if (cyberlink) {
        e.preventDefault()
        const data = {
          key: cyberlink.dataset.guideKey || '',
          title: cyberlink.dataset.guideTitle || '',
          icon: cyberlink.dataset.guideIcon || '',
        }
        onCyberlinkClick(data)
        return
      }

      // 3. Tab Button Click
      const tabBtn = target.closest('.guide-tab-btn') as HTMLElement
      if (tabBtn) {
        e.preventDefault()
        const tabTargetId = tabBtn.dataset.tabTarget
        const tabContainer = tabBtn.closest('.guide-tabs')
        if (tabTargetId && tabContainer) {
          haptic.selection()
          // Update active button state
          const buttons = tabContainer.querySelectorAll('.guide-tab-btn')
          buttons.forEach((b) => b.classList.remove('active'))
          tabBtn.classList.add('active')

          // Update active panel state
          const panels = tabContainer.querySelectorAll('.guide-tab-panel')
          panels.forEach((p) => {
            if ((p as HTMLElement).dataset.tabId === tabTargetId) {
              p.classList.remove('hidden')
            } else {
              p.classList.add('hidden')
            }
          })
        }
        return
      }

      // 4. Spoiler Click (Click-to-reveal)
      const spoiler = target.closest('.guide-spoiler') as HTMLElement
      if (spoiler) {
        haptic.light()
        spoiler.classList.toggle('revealed')
        return
      }

      // 5. Code / Promo Code Click-to-Copy
      const codeEl = target.closest('.guide-code') as HTMLElement
      if (codeEl) {
        const text = codeEl.textContent?.trim()
        if (text && text.length < 150) {
          haptic.medium()
          navigator.clipboard
            ?.writeText(text)
            .then(() => {
              toast.success(`«${text}» скопировано в буфер!`)
            })
            .catch(() => {})
          return
        }
      }
    }

    const handleImgError = (e: Event) => {
      const target = e.target as HTMLElement
      if (target && target.tagName === 'IMG') {
        target.style.display = 'none'
      }
    }

    el.addEventListener('click', handleClick)
    el.addEventListener('error', handleImgError, true)
    return () => {
      el.removeEventListener('click', handleClick)
      el.removeEventListener('error', handleImgError, true)
    }
  }, [onImageClick, onCyberlinkClick])

  return (
    <motion.div
      ref={contentRef}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.23, 1, 0.32, 1] }}
      className="guide-content-wrapper prose prose-invert max-w-none"
      // biome-ignore lint/security/noDangerouslySetInnerHtml: Markdown rendering
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
