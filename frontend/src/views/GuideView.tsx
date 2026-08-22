import { useQuery } from '@tanstack/react-query'
import { AnimatePresence, motion } from 'framer-motion'
import { type FC, Suspense, lazy, useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'

import { useRecordView } from '@/hooks/queries'
import { usePullToRefresh } from '@/hooks/usePullToRefresh'
import { apiFetch, apiPost } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { Eye, Film, ImageIcon, Maximize } from '@/lib/icons'
import type { Guide as GuideType } from '@/lib/types'

import { Breadcrumbs } from '@/components/Breadcrumbs'
import { FavoriteButton } from '@/components/FavoriteButton'
import { PtrIndicator } from '@/components/PtrIndicator'
import { ScrollToTopFab } from '@/components/ScrollToTopFab'
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

  const {
    data: guide,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ['guide', guideKey],
    queryFn: () => apiFetch<GuideType>(`/api/guide/${guideKey}`),
    staleTime: 120_000,
  })

  const { data: reactionsData, refetch: refetchReactions } = useQuery({
    queryKey: ['guide-reactions', guideKey],
    queryFn: () =>
      apiFetch<{ counts: Record<string, number>; user_reactions: string[] }>(
        `/api/guide/${guideKey}/reactions`
      ),
    staleTime: 30_000,
  })

  const handleToggleReaction = async (reactionKey: string) => {
    haptic.selection()
    try {
      await apiPost<{ counts: Record<string, number>; user_reactions: string[] }>(
        `/api/guide/${guideKey}/react`,
        { reaction: reactionKey }
      )
      refetchReactions()
    } catch {
      toast.error('Не удалось сохранить реакцию')
    }
  }

  const { formattedText } = useGuideLogic(guide)
  const { mutate: recordView } = useRecordView()
  const { pullY, refreshing } = usePullToRefresh(scrollRef, async () => {
    await refetch()
  })


  const recordedKeyRef = useRef<string | null>(null)

  useEffect(() => {
    if (guide && recordedKeyRef.current !== guideKey) {
      recordedKeyRef.current = guideKey
      onGuideLoaded?.(guide)
      recordView(guideKey)
      document.title = `${guide.title} | BlackRose`
    }
  }, [guide, guideKey, onGuideLoaded, recordView])

  if (isLoading || !guide) {
    return (
      <div className="flex h-full flex-col overflow-hidden container-padding pt-6 pb-24 space-y-6 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="h-10 w-48 rounded-2xl bg-rose-500/10 border border-rose-500/20" />
          <div className="h-8 w-24 rounded-xl bg-amber-500/10 border border-amber-500/20" />
        </div>
        <div className="h-44 rounded-3xl rose-bento-card border-rose-500/20 bg-card/60" />
        <div className="h-64 rounded-3xl rose-bento-card border-rose-500/20 bg-card/40" />
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col bg-background rose-mesh-bg">
      <PtrIndicator pullY={pullY} refreshing={refreshing} />
      <div
        ref={scrollRef}
        className="view-scroll flex-1 overflow-y-auto overflow-x-hidden no-scrollbar relative"
      >
        <div className="container-padding pt-6 pb-32 max-w-4xl mx-auto">
          <Breadcrumbs
            items={[{ label: 'Категории', route: { type: 'categories' } }, { label: guide.title }]}
          />

          {/* Header */}
          <header className="mb-8 relative z-10 p-6 sm:p-8 rounded-3xl rose-bento-card border-rose-500/30 bg-gradient-to-br from-rose-950/40 via-card/70 to-card/90 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-3"
              >
                <div className="flex items-center gap-2 mb-4">
                  <div className="gold-accent-badge">
                    <Eye className="size-3.5 fill-amber-400" />
                    <span>Slayerpedia Guide</span>
                  </div>
                </div>
                <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black leading-tight tracking-tight text-foreground font-heading uppercase">
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
                <div className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-500/10 rounded-full border border-rose-500/30 shadow-inner">
                  <Eye className="size-3.5 text-rose-400" />
                  <span className="text-[11px] font-bold text-rose-400 font-mono tabular-nums">
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
            className="rose-bento-card rounded-3xl p-5 sm:p-8 relative overflow-hidden border-rose-500/20 shadow-2xl"
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

            {/* Interactive Emoji Reactions */}
            <div className="mt-8 pt-6 border-t border-rose-500/15 flex flex-wrap items-center justify-between gap-4">
              <span className="text-xs font-bold uppercase tracking-wider text-muted-foreground font-heading">
                Оцените гайд:
              </span>
              <div className="flex items-center gap-2 flex-wrap">
                {[
                  { emoji: '🔥', key: 'fire', label: 'Огонь' },
                  { emoji: '👍', key: 'like', label: 'Полезно' },
                  { emoji: '💡', key: 'idea', label: 'Познавательно' },
                  { emoji: '🐉', key: 'dragon', label: 'Слеер' },
                ].map((r) => {
                  const count = reactionsData?.counts?.[r.key] || 0
                  const isUserActive = reactionsData?.user_reactions?.includes(r.key)
                  return (
                    <button
                      key={r.key}
                      onClick={() => handleToggleReaction(r.key)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold transition-all active:scale-95 shadow-sm ${
                        isUserActive
                          ? 'bg-rose-500/25 border-rose-500 text-white shadow-rose-950/40'
                          : 'bg-card border-rose-500/20 hover:border-rose-500/50 hover:bg-rose-500/10 text-muted-foreground'
                      }`}
                    >
                      <span>{r.emoji}</span>
                      <span className="text-rose-300/90">{r.label}</span>
                      {count > 0 && (
                        <span className="ml-1 px-1.5 py-0.5 rounded-full bg-rose-500/20 text-[10px] text-rose-200">
                          {count}
                        </span>
                      )}
                    </button>
                  )
                })}
              </div>
            </div>

          </motion.div>

          {/* Media Gallery (Photos & Videos) */}
          {((guide.photo && guide.photo.length > 0) || (guide.video && guide.video.length > 0)) && (
            <div className="mt-8 space-y-6">
              {/* Photo Gallery */}
              {guide.photo && guide.photo.length > 0 && (
                <div className="rose-bento-card rounded-3xl p-5 sm:p-6 border-rose-500/20 shadow-xl">
                  <div className="flex items-center gap-2 mb-4">
                    <ImageIcon className="size-4 text-rose-400" />
                    <h3 className="text-sm font-black uppercase tracking-wider text-foreground font-heading">
                      Галерея скриншотов ({guide.photo.length})
                    </h3>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {guide.photo.map((imgUrl, idx) => (
                      <div
                        key={idx}
                        className="group relative overflow-hidden rounded-2xl border border-border/40 bg-card/50 aspect-video cursor-pointer hover:border-primary/50 transition-all shadow-md"
                        onClick={() => setLightbox(imgUrl)}
                      >
                        <img
                          src={imgUrl}
                          alt={`Скриншот ${idx + 1}`}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          loading="lazy"
                        />
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                          <Maximize className="size-6 text-white drop-shadow" />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Video Gallery */}
              {guide.video && guide.video.length > 0 && (
                <div className="rose-bento-card rounded-3xl p-5 sm:p-6 border-rose-500/20 shadow-xl">
                  <div className="flex items-center gap-2 mb-4">
                    <Film className="size-4 text-amber-400" />
                    <h3 className="text-sm font-black uppercase tracking-wider text-foreground font-heading">
                      Видеоинструкции ({guide.video.length})
                    </h3>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {guide.video.map((vUrl, idx) => {
                      const isYoutube = vUrl.includes('youtube.com') || vUrl.includes('youtu.be')
                      const embedUrl = isYoutube
                        ? vUrl
                            .replace('watch?v=', 'embed/')
                            .replace('youtu.be/', 'youtube.com/embed/')
                        : vUrl
                      return (
                        <div
                          key={idx}
                          className="rounded-2xl overflow-hidden border border-border/40 bg-black/80 aspect-video shadow-md"
                        >
                          {isYoutube ? (
                            <iframe
                              src={embedUrl}
                              title={`Видео ${idx + 1}`}
                              className="w-full h-full border-0"
                              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                              allowFullScreen
                            />
                          ) : (
                            <video src={vUrl} controls className="w-full h-full object-cover" />
                          )}
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          )}

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

      <ScrollToTopFab targetRef={scrollRef} />
    </div>
  )
}
