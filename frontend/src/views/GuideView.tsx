// @ts-nocheck
import { useSuspenseQuery } from '@tanstack/react-query'
import { AnimatePresence, motion } from 'framer-motion'
import { type FC, Suspense, lazy, useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'

import { useRecordView } from '@/hooks/queries'
import { usePullToRefresh } from '@/hooks/usePullToRefresh'
import { apiFetch } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { Eye } from '@/lib/icons'
import type { Guide as GuideType } from '@/lib/types'

import { FavoriteButton } from '@/components/FavoriteButton'
import { PtrIndicator } from '@/components/PtrIndicator'
import { TableOfContents } from '@/components/TableOfContents'
import { TagsList } from '@/components/TagBadge'
import { GuideContent } from '@/features/guide/components/GuideContent'
import { useGuideLogic } from '@/features/guide/hooks/useGuideLogic'
import { ShareButton } from './guide/components/ShareButton'

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
  onGuideLoaded?: (guide: GuideType) => void
  onTagClick: (tag: string) => void
}

export const GuideView: FC<GuideViewProps> = ({
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

  const { data: guide, refetch } = useSuspenseQuery({
    queryKey: ['guide', guideKey],
    queryFn: () => apiFetch<GuideType>(`/api/guide/${guideKey}`),
    staleTime: 120_000,
  })

  const { formattedText } = useGuideLogic(guide)
  const { mutate: recordView } = useRecordView()
  const { pullY, refreshing } = usePullToRefresh(scrollRef, async () => {
    await refetch()
  })

  useEffect(() => {
    if (guide) {
      onGuideLoaded?.(guide)
      recordView(guideKey)
      document.title = `${guide.title} | BlackRose`
    }
  }, [guide, guideKey, onGuideLoaded, recordView])

  return (
    <div className="flex h-full flex-col bg-background">
      <PtrIndicator pullY={pullY} refreshing={refreshing} />
      <div
        ref={scrollRef}
        className="view-scroll flex-1 overflow-y-auto overflow-x-hidden no-scrollbar relative"
      >
        {/* Ambient background glow for hero */}
        <div className="absolute top-0 left-0 w-full h-80 mesh-bg opacity-40 pointer-events-none -z-10" />

        <div className="container-padding pt-6 pb-32 max-w-4xl mx-auto">
          {/* Header */}
          <header className="mb-8 relative z-10">
            <div className="flex items-start justify-between gap-4">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-3"
              >
                <div className="flex items-center gap-2 mb-4">
                  <div className="size-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_rgba(123,140,248,0.8)]" />
                  <span className="text-[10px] font-black uppercase tracking-[0.3em] text-primary">
                    Slayerpedia Guide
                  </span>
                </div>
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black leading-tight tracking-tight text-foreground font-heading">
                  {guide.title}
                </h1>
              </motion.div>
              <div className="flex shrink-0 gap-2">
                <ShareButton title={guide.title} />
                <FavoriteButton
                  isFavorite={isFavorite}
                  onClick={() =>
                    onToggleFavorite({ key: guide.key, title: guide.title, icon: guide.icon || '' })
                  }
                />
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3 mt-6">
              {guide.views !== undefined && (
                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 rounded-full border border-primary/20 shadow-inner">
                  <Eye className="size-3.5 text-primary" />
                  <span className="text-[11px] font-bold text-primary">
                    {guide.views} просмотров
                  </span>
                </div>
              )}
              {guide.tags && <TagsList tags={guide.tags} onClick={onTagClick} />}
            </div>
          </header>

          {/* Main Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass-card rounded-[32px] p-5 sm:p-8 relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-64 h-64 bg-primary/5 rounded-full blur-[60px] pointer-events-none" />
            <TableOfContents text={guide.text || guide.content || ''} />
            <GuideContent
              html={formattedText}
              onImageClick={setLightbox}
              onCyberlinkClick={(data) => {
                haptic.light()
                setCyberlink(data)
              }}
            />
          </motion.div>

          {/* Comments Section */}
          <div className="mt-12">
            <Suspense
              fallback={<div className="h-40 rounded-3xl bg-muted/20 animate-pulse skeleton" />}
            >
              <CommentsSection guideKey={guideKey} />
            </Suspense>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {lightbox && (
          <Suspense fallback={null}>
            <Lightbox src={lightbox} onClose={() => setLightbox(null)} />
          </Suspense>
        )}
        {cyberlink && (
          <Suspense fallback={null}>
            <CyberlinkPopup
              {...cyberlink}
              guideKey={cyberlink.key}
              onOpen={(k, t, i) => {
                setCyberlink(null)
                onOpenGuide(k, t, i)
              }}
              onClose={() => setCyberlink(null)}
            />
          </Suspense>
        )}
      </AnimatePresence>
    </div>
  )
}
