import { FC, Suspense, lazy, useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useSuspenseQuery } from '@tanstack/react-query'
import { toast } from 'sonner'

import { apiFetch } from '@/lib/api'
import type { Guide as GuideType } from '@/lib/types'
import { useRecordView } from '@/hooks/queries'
import { usePullToRefresh } from '@/hooks/usePullToRefresh'
import { haptic } from '@/lib/haptic'
import { Eye } from '@/lib/icons'

import { FavoriteButton } from '@/components/FavoriteButton'
import { PtrIndicator } from '@/components/PtrIndicator'
import { TagsList } from '@/components/TagBadge'
import { ShareButton } from './guide/components/ShareButton'
import { useGuideLogic } from '@/features/guide/hooks/useGuideLogic'
import { GuideContent } from '@/features/guide/components/GuideContent'

const CommentsSection = lazy(() => import('@/components/CommentsSection').then(m => ({ default: m.CommentsSection })))
const Lightbox = lazy(() => import('@/components/Lightbox').then(m => ({ default: m.Lightbox })))
const CyberlinkPopup = lazy(() => import('./guide/components/CyberlinkPopup').then(m => ({ default: m.CyberlinkPopup })))

interface GuideViewProps {
  guideKey: string
  isFavorite: boolean
  onToggleFavorite: (guide: { key: string; title: string; icon: string }) => void
  onOpenGuide: (key: string, title?: string, icon?: string) => void
  onGuideLoaded?: (guide: any) => void
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
  const [cyberlink, setCyberlink] = useState<{ key: string; title: string; icon: string } | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  const { data: guide, refetch } = useSuspenseQuery({
    queryKey: ['guide', guideKey],
    queryFn: () => apiFetch<GuideType>(`/api/guide/${guideKey}`),
    staleTime: 120_000,
  })

  const { formattedText } = useGuideLogic(guide)
  const { mutate: recordView } = useRecordView()
  const { pullY, refreshing } = usePullToRefresh(scrollRef, async () => { await refetch() })

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
      <div ref={scrollRef} className="view-scroll flex-1 overflow-y-auto overflow-x-hidden no-scrollbar">
        <div className="px-6 pt-10 pb-32">
          {/* Header */}
          <header className="mb-10 space-y-6">
            <div className="flex items-start justify-between gap-4">
              <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="space-y-3">
                <div className="flex items-center gap-2">
                  <div className="size-1.5 rounded-full bg-primary shadow-sm shadow-primary/40" />
                  <span className="text-[10px] font-black uppercase tracking-[0.2em] text-muted-foreground/60">Slayerpedia Guide</span>
                </div>
                <h1 className="text-3xl font-black leading-[1.1] tracking-tight">{guide.title}</h1>
              </motion.div>
              <div className="flex shrink-0 gap-2">
                <ShareButton title={guide.title} />
                <FavoriteButton isFavorite={isFavorite} onClick={() => onToggleFavorite({ key: guide.key, title: guide.title, icon: guide.icon || '' })} />
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {guide.views !== undefined && (
                <div className="flex items-center gap-1.5 px-3 py-1 bg-muted/40 rounded-full border border-border/5">
                  <Eye className="size-3 text-muted-foreground" />
                  <span className="text-[10px] font-bold text-muted-foreground">{guide.views}</span>
                </div>
              )}
              {guide.tags && <TagsList tags={guide.tags} onClick={onTagClick} />}
            </div>
          </header>

          {/* Main Content */}
          <GuideContent 
            html={formattedText} 
            onImageClick={setLightbox} 
            onCyberlinkClick={(data) => { haptic.light(); setCyberlink(data) }} 
          />

          {/* Comments Section */}
          <div className="mt-20">
             <Suspense fallback={<div className="h-40 rounded-3xl bg-muted/20 animate-pulse" />}>
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
              onOpen={(k, t, i) => { setCyberlink(null); onOpenGuide(k, t, i) }}
              onClose={() => setCyberlink(null)}
            />
          </Suspense>
        )}
      </AnimatePresence>
    </div>
  )
}

export default GuideView
