import { FavoriteButton } from '@/components/FavoriteButton'
import { PtrIndicator } from '@/components/PtrIndicator'
import { TagsList } from '@/components/TagBadge'
import { useRecordView } from '@/hooks/queries'
import { usePullToRefresh } from '@/hooks/usePullToRefresh'
import { apiFetch } from '@/lib/api'
import type { Guide as GuideType } from '@/lib/types'
import { haptic } from '@/lib/haptic'
import { Eye } from '@/lib/icons'
import { formatGuideText } from '@/lib/markdown'
import { normalizeUrl } from '@/lib/utils'
import { useSuspenseQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import type React from 'react'
import { Suspense, lazy, useEffect, useMemo, useRef, useState } from 'react'
import { toast } from 'sonner'

import { DocBlock } from './guide/components/DocBlock'
// Extracted components
import { ShareButton } from './guide/components/ShareButton'
import { VideoBlock } from './guide/components/VideoBlock'

interface Guide {
  key: string
  title: string
  icon: string
  text?: string
  text_content?: string
  guide_links?: Record<string, string>
  icons?: Record<string, string>
}

const CommentsSection = lazy(() =>
  import('@/components/CommentsSection').then((m) => ({ default: m.CommentsSection }))
)
const Lightbox = lazy(() => import('@/components/Lightbox').then((m) => ({ default: m.Lightbox })))
const CyberlinkPopup = lazy(() =>
  import('./guide/components/CyberlinkPopup').then((m) => ({ default: m.CyberlinkPopup }))
)

interface GuideViewProps {
  guideKey: string
  isFavorite: boolean
  onToggleFavorite: (guide: { key: string; title: string; icon: string }) => void
  onOpenGuide: (key: string, title?: string, icon?: string) => void
  onGuideLoaded?: (guide: Guide) => void
  onTagClick: (tag: string) => void
}

export const GuideView: React.FC<GuideViewProps> = ({
  guideKey,
  isFavorite,
  onToggleFavorite,
  onOpenGuide,
  onGuideLoaded,
  onTagClick,
}) => {
  const [lightbox, setLightbox] = useState<string | null>(null)
  const [cyberlink, setCyberlink] = useState<{ key: string; title: string; icon: string } | null>(
    null
  )
  const scrollRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  const { data: guide, refetch } = useSuspenseQuery({
    queryKey: ['guide', guideKey],
    queryFn: () => apiFetch<GuideType>(`/api/guide/${guideKey}`),
    staleTime: 120_000,
  })

  const { mutate: recordView } = useRecordView()

  const formattedText = useMemo(() => {
    const rawText = guide?.text || guide?.text_content || ''
    if (!rawText) return ''
    return formatGuideText(rawText, {
      guideLinks: (guide.guide_links as Record<string, { title?: string; icon?: string }>) ?? {},
      iconResolver: (nameValue: string) => {
        if (!guide.icons) return ''
        const name = nameValue?.trim()
        if (!name) return ''

        // 1. Direct match
        if (guide.icons[name]) return normalizeUrl(guide.icons[name])

        // 2. Build normalized map for fuzzy search (lowercase, no underscores)
        const normalize = (s: string) => s.toLowerCase().replace(/_/g, '').replace(/s$/, '')
        const searchName = normalize(name)

        // Try to find the first key that matches when normalized
        for (const key in guide.icons) {
          if (normalize(key) === searchName) {
            return normalizeUrl(guide.icons[key])
          }
        }

        return ''
      },
    })
  }, [guide])

  useEffect(() => {
    if (guide) onGuideLoaded?.(guide as Guide)
  }, [guide, onGuideLoaded])

  useEffect(() => {
    if (guideKey) recordView(guideKey)
  }, [guideKey, recordView])

  useEffect(() => {
    const el = contentRef.current
    if (!el) return
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement

      // 1. Icon names
      const icon = target.closest('[data-icon-name]') as HTMLElement | null
      if (icon) {
        e.preventDefault()
        haptic.select()
        const rawName = icon.dataset.iconName!
        const displayName = rawName
          .replace(/_/g, ' ')
          .replace(/([A-Z])/g, ' $1')
          .trim()
          .split(' ')
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
          .join(' ')

        toast(displayName, {
          icon: 'ℹ️',
          id: `icon-toast-${rawName}`,
          position: 'top-center',
        })
        return
      }

      // 2. Guide cyberlinks
      const link = target.closest('a[data-guide-key]') as HTMLElement | null
      if (!link) return
      e.preventDefault()
      haptic.light()
      setCyberlink({
        key: link.dataset.guideKey!,
        title: link.dataset.guideTitle || link.dataset.guideKey!,
        icon: link.dataset.guideIcon || '',
      })
    }
    el.addEventListener('click', handleClick)
    return () => el.removeEventListener('click', handleClick)
  }, [formattedText])

  // Hydrate premium video players
  useEffect(() => {
    const el = contentRef.current
    if (!el) return

    const placeholders = el.querySelectorAll('.premium-video-placeholder')
    const roots: any[] = []

    import('react-dom/client').then(({ createRoot }) => {
      placeholders.forEach((p) => {
        const placeholder = p as HTMLElement
        const url = placeholder.dataset.videoUrl
        if (url) {
          const root = createRoot(placeholder)
          root.render(<VideoBlock url={url} />)
          roots.push(root)
        }
      })
    })

    return () => {
      roots.forEach((root) => {
        setTimeout(() => root.unmount(), 0)
      })
    }
  }, [formattedText])

  const handleRefetch = async () => {
    await refetch()
  }

  const { pullY, refreshing } = usePullToRefresh(scrollRef, handleRefetch)

  const [progress, setProgress] = useState(0)
  useEffect(() => {
    const scrollEl = scrollRef.current
    if (!scrollEl) return
    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = scrollEl
      const scrollPercent = (scrollTop / (scrollHeight - clientHeight)) * 100
      setProgress(scrollPercent)
    }
    scrollEl.addEventListener('scroll', handleScroll)
    return () => scrollEl.removeEventListener('scroll', handleScroll)
  }, [])

  const toc = useMemo(() => {
    const items: Array<{ id: string; text: string; level: number }> = []
    const parser = new DOMParser()
    const doc = parser.parseFromString(formattedText, 'text/html')
    const headings = doc.querySelectorAll('h2, h3')
    headings.forEach((h, i) => {
      const id = h.id || `heading-${i}`
      items.push({
        id,
        text: h.textContent || '',
        level: parseInt(h.tagName.substring(1)),
      })
    })
    return items
  }, [formattedText])

  return (
    <>
      {/* Progress Bar */}
      <div className="fixed top-16 left-0 right-0 z-50 h-1 pointer-events-none">
        <motion.div
          className="h-full bg-primary shadow-[0_0_8px_rgba(var(--primary-rgb),0.5)]"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ ease: 'linear', duration: 0.1 }}
        />
      </div>

      <div className="view-scroll flex-1 overflow-y-auto relative" ref={scrollRef}>
        <PtrIndicator pullY={pullY} refreshing={refreshing} />

        <div className="mx-auto max-w-2xl px-5 pb-24 pt-8">
          {/* TOC Toggle (Desktop/Tablet) */}
          {toc.length > 1 && (
            <div className="sticky top-4 z-30 float-right ml-4 hidden md:block">
              <div className="glass-card rounded-[24px] p-4 border-border/10 shadow-xl max-w-[200px]">
                <h4 className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 mb-3">
                  Оглавление
                </h4>
                <div className="flex flex-col gap-2">
                  {toc.map((item) => (
                    <button
                      key={item.id}
                      className={`text-left text-[11px] font-bold transition-all hover:text-primary ${
                        item.level === 3 ? 'pl-3 border-l border-border/10' : ''
                      }`}
                      onClick={() => {
                        const el = document.getElementById(item.id)
                        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
                      }}
                    >
                      {item.text}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
          {/* Header */}
          <div className="flex flex-col gap-8 mb-10">
            <div className="flex flex-col gap-6">
              <div className="flex items-start justify-between gap-4">
                <div className="flex size-20 shrink-0 items-center justify-center rounded-[28px] glass-card p-1 shadow-2xl shadow-primary/10">
                  <div className="flex size-full items-center justify-center rounded-[24px] bg-primary/5 shadow-inner">
                    {guide.icon || guide.icon_url ? (
                      <motion.img
                        layoutId={`guide-icon-${guide.key}`}
                        src={normalizeUrl(guide.icon || guide.icon_url)}
                        alt=""
                        className="size-14 object-contain animate-float drop-shadow-md"
                        onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
                          e.currentTarget.style.display = 'none'
                        }}
                      />
                    ) : (
                      <motion.span layoutId={`guide-icon-${guide.key}`} className="text-3xl">
                        📄
                      </motion.span>
                    )}
                  </div>
                </div>

                <div className="flex shrink-0 items-center gap-2 pt-2">
                  <ShareButton guide={guide} />
                  <FavoriteButton
                    isFav={isFavorite}
                    onToggle={() => {
                      haptic.medium?.()
                      onToggleFavorite({ key: guide.key, title: guide.title, icon: guide.icon || guide.icon_url || '' })
                    }}
                    size={44}
                  />
                </div>
              </div>

              <div className="flex flex-col gap-4">
                <h2 className="text-3xl font-black tracking-tighter text-foreground leading-[1.1] selection:bg-primary/30">
                  {guide.title}
                </h2>
                <div className="flex flex-wrap items-center gap-4">
                  <ViewsCounter views={guide.views} />
                  {(guide.tags?.length ?? 0) > 0 && <TagsList tags={guide.tags || []} onTagClick={onTagClick} />}
                </div>
              </div>
            </div>
          </div>

          {/* Content */}
          <div
            ref={contentRef}
            className="guide-content prose prose-invert prose-p:leading-relaxed prose-headings:font-black prose-img:rounded-2xl max-w-none text-foreground/90"
            dangerouslySetInnerHTML={{ __html: formattedText }}
          />

          {/* Media */}
          <div className="mt-8 flex flex-col gap-4">
            {(guide.photo || [])
              .filter((s: string) => s && !s.startsWith('Ag'))
              .map((src: string, i: number) => (
                <img
                  key={i}
                  src={normalizeUrl(src)}
                  className="w-full cursor-zoom-in rounded-2xl border border-border/50 shadow-lg transition-transform active:scale-[0.98]"
                  loading="lazy"
                  alt=""
                  onError={(e: React.SyntheticEvent<HTMLImageElement>) => {
                    e.currentTarget.style.display = 'none'
                  }}
                  onClick={() => {
                    haptic.light()
                    setLightbox(normalizeUrl(src))
                  }}
                />
              ))}

            {(guide.video || []).map((url: string, i: number) => (
              <VideoBlock key={i} url={url} />
            ))}
            {(guide.document || []).map((url: string, i: number) =>
              url.includes('discord.com/channels/') ? null : <DocBlock key={i} url={url} />
            )}
          </div>

          <Suspense fallback={null}>
            <CommentsSection guideKey={guideKey} />
          </Suspense>
        </div>
      </div>

      {lightbox && (
        <Suspense fallback={null}>
          <Lightbox src={lightbox} onClose={() => setLightbox(null)} />
        </Suspense>
      )}

      {cyberlink && (
        <Suspense fallback={null}>
          <CyberlinkPopup
            guideKey={cyberlink.key}
            title={cyberlink.title}
            icon={cyberlink.icon}
            onOpen={onOpenGuide}
            onClose={() => setCyberlink(null)}
          />
        </Suspense>
      )}
    </>
  )
}

const ViewsCounter = ({ views }: { views?: number }) => {
  if (!views) return null
  return (
    <div className="flex items-center gap-1.5 rounded-full bg-muted/50 px-2.5 py-1 text-[11px] font-bold text-muted-foreground ring-1 ring-border/30">
      <Eye className="size-3.5" />
      <span>{views >= 1000 ? `${(views / 1000).toFixed(1)}k` : views}</span>
    </div>
  )
}

export default GuideView
