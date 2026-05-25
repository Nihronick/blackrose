import { ErrorBoundary } from '@/components/ErrorBoundary'
import { BrandIcon } from '@/components/ui/BrandIcon'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { CategoryList } from '@/features/categories'
import type { Category } from '@/features/categories'
import { apiRecentComments, apiRecentGuides, apiTopGuides } from '@/lib/api'
import { apiFetch } from '@/lib/api'
import { getStoredUser } from '@/lib/auth'
import { haptic } from '@/lib/haptic'
import {
  BookOpen,
  ChevronRight,
  Clock,
  Eye,
  FileText,
  LayoutGrid,
  MessageCircle,
  Sparkles,
  TrendingUp,
} from '@/lib/icons'
import { isLanguageKey } from '@/lib/language'
import { normalizeUrl } from '@/lib/utils'
import { useAppStore } from '@/store'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import * as O from 'fp-ts/Option'
import { pipe } from 'fp-ts/function'
import { motion } from 'framer-motion'
import { type FC, useRef } from 'react'

interface HomeDashboardProps {
  onSelectGuide: (key: string, title?: string, icon?: string) => void
  onSelectCategory: (category: Category) => void
}

export const HomeDashboard: FC<HomeDashboardProps> = ({ onSelectGuide, onSelectCategory }) => {
  const { language, cats } = useAppStore((state) => ({
    language: state.language,
    cats: state.cats,
  }))
  const userName = pipe(
    getStoredUser(),
    O.map((u) => u.first_name),
    O.getOrElse(() => 'Слеер')
  )

  // Queries
  const { data: topGuidesData, isLoading: topLoading } = useQuery({
    queryKey: ['top-guides', language],
    queryFn: apiTopGuides,
  })

  const { data: recentGuidesData, isLoading: recentLoading } = useQuery({
    queryKey: ['recent-guides', language],
    queryFn: apiRecentGuides,
  })

  const { data: recentCommentsData, isLoading: commentsLoading } = useQuery({
    queryKey: ['recent-comments'],
    queryFn: apiRecentComments,
  })

  const topGuides = (topGuidesData?.results || []).filter((g) => isLanguageKey(g.key, language))
  const recentGuides = (recentGuidesData?.results || []).filter((g) =>
    isLanguageKey(g.key, language)
  )
  const recentComments = recentCommentsData?.comments || []

  const queryClient = useQueryClient()
  const prefetchTimer = useRef<NodeJS.Timeout | null>(null)

  const prefetchGuide = (key: string) => {
    if (prefetchTimer.current) clearTimeout(prefetchTimer.current)
    prefetchTimer.current = setTimeout(() => {
      queryClient.prefetchQuery({
        queryKey: ['guide', key],
        queryFn: () => apiFetch(`/api/guide/${key}`),
        staleTime: 60_000,
      })
    }, 150)
  }

  return (
    <div className="flex flex-col gap-8 pb-4 stagger-in">
      {/* 1. Hero Welcome */}
      <section className="pt-2">
        <div className="relative overflow-hidden rounded-3xl sm:rounded-[40px] mesh-bg p-5 sm:p-8 border border-primary/15 shadow-2xl shadow-primary/10 transition-transform duration-500 hover:scale-[1.005] ambient-glow texture-noise">
          {/* Animated background pulse */}
          <div className="absolute -right-10 -top-10 size-48 rounded-full bg-primary/20 blur-[80px] animate-pulse" />
          <div className="absolute -left-10 -bottom-10 size-32 rounded-full bg-primary/10 blur-[60px]" />

          <div className="relative z-10 flex flex-col gap-4 py-2">
            <div className="flex items-center gap-2">
              <div className="size-2 rounded-full bg-primary animate-ping" />
              <span className="text-[10px] font-black uppercase tracking-[0.3em] text-primary">
                Live Updates
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black tracking-tight text-foreground font-heading flex flex-wrap gap-x-2 items-baseline">
              <span>Привет,</span>
              <span
                className="bg-gradient-to-r from-primary to-violet-400 bg-clip-text text-transparent pb-2"
                style={{
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}
              >
                {userName}!
              </span>
            </h1>
            <p className="text-sm sm:text-[15px] font-medium text-muted-foreground/80 leading-relaxed max-w-md sm:max-w-xl">
              {recentGuides.length > 0
                ? `У нас появилось ${recentGuides.length} новых гайдов. Пора стать сильнее!`
                : 'Сегодня отличный день, чтобы изучить что-то новое.'}
            </p>
          </div>
        </div>
      </section>

      {/* Main Grid: Col-8 (Left) & Col-4 (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column (8 grid-spans) */}
        <div className="lg:col-span-8 flex flex-col gap-8">
          {/* 2. Popular Guides (Horizontal) */}
          <section className="flex flex-col gap-4">
            <div className="section-label font-heading">
              <TrendingUp className="size-3.5 text-primary" />
              <span>Популярное</span>
            </div>

            <div className="flex gap-4 overflow-x-auto scrollbar-premium pb-4 no-scrollbar lg:scrollbar-premium">
              {topLoading
                ? [...Array(3)].map((_, i) => (
                    <Skeleton
                      key={i}
                      className="h-44 w-[200px] sm:w-[240px] min-w-[200px] sm:min-w-[240px] flex-shrink-0 rounded-[24px] bg-muted/40"
                    />
                  ))
                : topGuides.map((g) => (
                    <motion.div
                      key={g.key}
                      whileTap={{ scale: 0.96 }}
                      whileHover={{ y: -6 }}
                      className="w-[180px] sm:w-[220px] lg:w-[240px] min-w-[180px] sm:min-w-[220px] lg:min-w-[240px] flex-shrink-0 cursor-pointer group"
                      onMouseEnter={() => prefetchGuide(g.key)}
                      onTouchStart={() => prefetchGuide(g.key)}
                      onClick={() => {
                        haptic.light()
                        onSelectGuide(g.key, g.title, g.icon_url)
                      }}
                    >
                      <Card className="h-full border-border/10 glass-card rounded-[24px] overflow-hidden flex flex-col transition-all duration-300 hover:shadow-glow hover:border-primary/20">
                        <div className="relative h-24 sm:h-28 bg-gradient-to-br from-primary/10 via-muted/5 to-transparent flex items-center justify-center p-4">
                          <div className="size-16 rounded-2xl bg-background shadow-lg flex items-center justify-center p-2 group-hover:scale-105 transition-transform duration-300">
                            {g.icon_url ? (
                              <img
                                src={normalizeUrl(g.icon_url)}
                                alt=""
                                className="size-12 object-contain"
                              />
                            ) : (
                              <div className="flex size-12 items-center justify-center rounded-2xl bg-gradient-to-br from-primary/10 to-violet-500/5 border border-primary/20 shadow-inner">
                                <BookOpen className="size-6 text-primary animate-pulse" />
                              </div>
                            )}
                          </div>
                          <Badge className="absolute top-2 right-2 h-5 rounded-full bg-primary/20 text-[9px] font-black text-primary px-1.5 border-0">
                            {g.views >= 1000 ? `${(g.views / 1000).toFixed(1)}k` : g.views}
                          </Badge>
                        </div>
                        <CardContent className="p-4 flex-1 flex flex-col justify-center">
                          <h4 className="text-[13px] font-black tracking-normal leading-snug line-clamp-2 group-hover:text-primary transition-colors duration-300 font-heading">
                            {g.title}
                          </h4>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
            </div>
          </section>

          {/* 3. Newest Updates */}
          <section className="flex flex-col gap-4">
            <div className="section-label font-heading">
              <Clock className="size-3.5 text-emerald-400" />
              <span>Новинки</span>
            </div>

            <div className="flex flex-col gap-3">
              {recentLoading
                ? [...Array(2)].map((_, i) => (
                    <Skeleton key={i} className="h-20 w-full rounded-2xl bg-muted/40" />
                  ))
                : recentGuides.slice(0, 3).map((g) => (
                    <motion.div
                      key={g.key}
                      whileTap={{ scale: 0.98 }}
                      className="group cursor-pointer rounded-2xl border border-border/5 bg-muted/20 p-4 transition-all hover:bg-muted/30 hover:border-primary/10 hover:shadow-soft"
                      onMouseEnter={() => prefetchGuide(g.key)}
                      onTouchStart={() => prefetchGuide(g.key)}
                      onClick={() => {
                        haptic.light()
                        onSelectGuide(g.key, g.title, g.icon_url)
                      }}
                    >
                      <div className="flex items-center gap-4">
                        <div className="size-12 shrink-0 rounded-xl bg-background flex items-center justify-center p-2 shadow-sm">
                          {g.icon_url ? (
                            <img
                              src={normalizeUrl(g.icon_url)}
                              alt=""
                              className="size-8 object-contain"
                            />
                          ) : (
                            <div className="flex size-8 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border border-emerald-500/20 shadow-inner">
                              <FileText className="size-4 text-emerald-400" />
                            </div>
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="text-[14px] font-black tracking-normal leading-snug line-clamp-1 group-hover:text-primary transition-colors font-heading">
                            {g.title}
                          </h4>
                          <p className="mt-1 text-[10px] font-medium text-muted-foreground/60 uppercase tracking-wider">
                            {g.updated_at && !Number.isNaN(new Date(g.updated_at).getTime())
                              ? `Обновлено: ${new Date(g.updated_at).toLocaleDateString()}`
                              : 'Недавно'}
                          </p>
                        </div>
                        <ChevronRight className="size-4 text-muted-foreground/30 group-hover:text-primary transition-colors" />
                      </div>
                    </motion.div>
                  ))}
            </div>
          </section>
        </div>

        {/* Right Column (4 grid-spans) */}
        <div className="lg:col-span-4 flex flex-col gap-8">
          {/* 5. Support Project Premium Banner - Moved here to look like a sidebar panel on desktop */}
          <section className="flex flex-col">
            <Card className="card-elevated relative overflow-hidden rounded-3xl border border-primary/15 p-5 sm:p-6 hover:border-primary/25">
              <div className="absolute -right-8 -top-8 size-32 bg-primary/10 rounded-full blur-[40px] animate-pulse" />
              <div className="absolute -left-12 -bottom-12 size-36 bg-violet-500/5 rounded-full blur-[50px]" />

              <div className="relative z-10 flex flex-col gap-5">
                <div className="flex items-center gap-3.5">
                  <div className="size-11 rounded-[20px] bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-500 shadow-inner shrink-0 animate-bounce">
                    <BrandIcon name="patreon" size={20} />
                  </div>
                  <div>
                    <h4 className="text-xs font-black uppercase tracking-widest text-foreground font-heading">
                      Поддержать проект
                    </h4>
                    <p className="text-[9px] font-bold text-muted-foreground/60 uppercase tracking-wider mt-0.5">
                      Развитие BlackRose
                    </p>
                  </div>
                </div>

                <p className="text-xs font-medium text-muted-foreground/80 leading-relaxed">
                  BlackRose разрабатывается и поддерживается сообществом. Ваша поддержка помогает
                  нам оплачивать серверы и быстрее выпускать новые калькуляторы и гайды!
                </p>

                <div className="flex flex-col gap-2 mt-2">
                  <motion.button
                    whileTap={{ scale: 0.98 }}
                    whileHover={{ scale: 1.02 }}
                    className="w-full h-11 rounded-2xl bg-gradient-to-r from-primary to-violet-500 text-primary-foreground font-black text-xs uppercase tracking-wider transition-all duration-300 hover:shadow-glow active:scale-95 border border-primary/20 font-heading cursor-pointer flex items-center justify-center gap-2"
                    onClick={() => {
                      haptic.medium()
                      window.open('https://dalink.to/nihronick', '_blank')
                    }}
                  >
                    <span>Поддержать проект</span>
                  </motion.button>
                </div>
              </div>
            </Card>
          </section>

          {/* 4. Community Pulse (Latest Comments) */}
          <section className="flex flex-col gap-4">
            <div className="section-label font-heading">
              <MessageCircle className="size-3.5 text-amber-400" />
              <span>Пульс сообщества</span>
            </div>

            <div className="card-elevated rounded-3xl p-4 sm:p-6">
              {commentsLoading ? (
                <Skeleton className="h-32 w-full rounded-2xl bg-muted/40" />
              ) : recentComments.length === 0 ? (
                <p className="text-center py-4 text-xs font-medium text-muted-foreground/40 italic">
                  Здесь пока тихо...
                </p>
              ) : (
                <div className="flex flex-col gap-6">
                  {recentComments.map((c) => (
                    <div key={c.id} className="flex flex-col gap-2">
                      <div className="flex items-center gap-2">
                        <div className="size-5 rounded-full bg-primary/20 flex items-center justify-center text-[9px] font-black text-primary uppercase">
                          {(c.first_name || 'U').charAt(0)}
                        </div>
                        <span className="text-[11px] font-black text-foreground/80">
                          {c.first_name || 'Участник'}
                        </span>
                        <span className="text-[9px] font-medium text-muted-foreground/40">
                          • {c.guide_title}
                        </span>
                      </div>
                      <p className="text-xs font-medium text-muted-foreground leading-relaxed line-clamp-2">
                        "{c.text}"
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        </div>
      </div>

      {/* 6. Categories List at the bottom */}
      <section className="flex flex-col gap-4 mt-4">
        <div className="section-label font-heading">
          <LayoutGrid className="size-3.5 text-primary" />
          <span>Категории</span>
        </div>
        <CategoryList categories={cats || []} onSelectCategory={onSelectCategory} />
      </section>
    </div>
  )
}
