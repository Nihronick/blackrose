import { ErrorBoundary } from '@/components/ErrorBoundary'
import { BrandIcon } from '@/components/ui/BrandIcon'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { CategoryList } from '@/features/categories'
import type { Category } from '@/features/categories'
import { apiGuilds, apiRecentComments, apiRecentGuides, apiTopGuides, apiFetch } from '@/lib/api'
import { getStoredUser } from '@/lib/auth'
import { haptic } from '@/lib/haptic'
import {
  BookOpen,
  ChevronRight,
  Clock,
  Compass,
  FileText,
  LayoutGrid,
  MessageCircle,
  Shield,
  Star,
  TrendingUp,
  UserPlus,
} from '@/lib/icons'
import { isLanguageKey } from '@/lib/language'
import { useAppNavigation } from '@/lib/navigation'
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
  const { push } = useAppNavigation()
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

  const { data: guildsData, isLoading: guildsLoading } = useQuery({
    queryKey: ['guilds'],
    queryFn: apiGuilds,
  })

  const topGuides = (topGuidesData?.results || []).filter((g) => isLanguageKey(g.key, language))
  const recentGuides = (recentGuidesData?.results || []).filter((g) =>
    isLanguageKey(g.key, language)
  )
  const recentComments = recentCommentsData?.comments || []
  const guilds = guildsData?.guilds || []

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
    <div className="flex flex-col gap-8 pb-4 stagger-in px-4 sm:px-6 lg:px-8">
      {/* 1. Hero Welcome Banner */}
      <section className="pt-2">
        <div className="relative overflow-hidden rounded-3xl sm:rounded-[40px] mesh-bg p-5 sm:p-8 border border-primary/15 shadow-2xl shadow-primary/10 transition-transform duration-500 hover:scale-[1.005] ambient-glow texture-noise">
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

      {/* 2. Interactive Quick Action Buttons Hub */}
      <section className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
        <motion.div
          whileHover={{ y: -4, scale: 1.02 }}
          whileTap={{ scale: 0.96 }}
          onClick={() => {
            haptic.light()
            push({ type: 'guilds' })
          }}
          className="glass-card cursor-pointer p-4 rounded-3xl border border-primary/20 bg-gradient-to-br from-primary/15 via-card to-transparent flex flex-col justify-between h-28 relative overflow-hidden group shadow-lg shadow-primary/10 transition-all hover:border-primary/40"
        >
          <div className="flex justify-between items-start">
            <div className="size-10 rounded-2xl bg-primary/20 text-primary flex items-center justify-center font-bold">
              <Shield className="size-5" />
            </div>
            <Badge className="bg-primary/20 text-primary border-0 text-[9px] font-black uppercase">
              NEW
            </Badge>
          </div>
          <div>
            <h3 className="font-black text-sm text-foreground group-hover:text-primary transition-colors font-heading">
              Гильдии
            </h3>
            <p className="text-[10px] font-medium text-muted-foreground/80">Состав & Рейтинг</p>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ y: -4, scale: 1.02 }}
          whileTap={{ scale: 0.96 }}
          onClick={() => {
            haptic.light()
            push({ type: 'categories' })
          }}
          className="glass-card cursor-pointer p-4 rounded-3xl border border-border/10 bg-gradient-to-br from-violet-500/10 via-card to-transparent flex flex-col justify-between h-28 relative overflow-hidden group transition-all hover:border-violet-500/30"
        >
          <div className="size-10 rounded-2xl bg-violet-500/20 text-violet-400 flex items-center justify-center font-bold">
            <LayoutGrid className="size-5" />
          </div>
          <div>
            <h3 className="font-black text-sm text-foreground group-hover:text-violet-400 transition-colors font-heading">
              Категории
            </h3>
            <p className="text-[10px] font-medium text-muted-foreground/80">База всех знаний</p>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ y: -4, scale: 1.02 }}
          whileTap={{ scale: 0.96 }}
          onClick={() => {
            haptic.light()
            push({ type: 'roadmap' })
          }}
          className="glass-card cursor-pointer p-4 rounded-3xl border border-border/10 bg-gradient-to-br from-emerald-500/10 via-card to-transparent flex flex-col justify-between h-28 relative overflow-hidden group transition-all hover:border-emerald-500/30"
        >
          <div className="size-10 rounded-2xl bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
            <Compass className="size-5" />
          </div>
          <div>
            <h3 className="font-black text-sm text-foreground group-hover:text-emerald-400 transition-colors font-heading">
              Дорожная карта
            </h3>
            <p className="text-[10px] font-medium text-muted-foreground/80">Планы & Обновления</p>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ y: -4, scale: 1.02 }}
          whileTap={{ scale: 0.96 }}
          onClick={() => {
            haptic.light()
            push({ type: 'favorites' })
          }}
          className="glass-card cursor-pointer p-4 rounded-3xl border border-border/10 bg-gradient-to-br from-amber-500/10 via-card to-transparent flex flex-col justify-between h-28 relative overflow-hidden group transition-all hover:border-amber-500/30"
        >
          <div className="size-10 rounded-2xl bg-amber-500/20 text-amber-400 flex items-center justify-center font-bold">
            <Star className="size-5" />
          </div>
          <div>
            <h3 className="font-black text-sm text-foreground group-hover:text-amber-400 transition-colors font-heading">
              Избранное
            </h3>
            <p className="text-[10px] font-medium text-muted-foreground/80">Сохраненные гайды</p>
          </div>
        </motion.div>
      </section>

      {/* 3. Featured Guilds & Clans Section on Main Screen */}
      <section className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div className="section-label font-heading flex items-center gap-2">
            <Shield className="size-4 text-primary" />
            <span className="text-base font-black text-foreground">Гильдии & Клановый Состав</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="h-8 rounded-xl text-xs font-bold text-primary hover:bg-primary/10 transition-colors cursor-pointer"
            onClick={() => {
              haptic.light()
              push({ type: 'guilds' })
            }}
          >
            Все гильдии <ChevronRight className="size-3.5 ml-1" />
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {guildsLoading ? (
            [1, 2].map((i) => <Skeleton key={i} className="h-32 rounded-3xl bg-muted/40" />)
          ) : guilds.length === 0 ? (
            <div className="col-span-full p-6 text-center glass-card rounded-3xl border border-border/10">
              <Shield className="size-8 text-primary/40 mx-auto mb-2" />
              <p className="text-xs text-muted-foreground">Гильдии скоро будут добавлены</p>
            </div>
          ) : (
            guilds.slice(0, 3).map((g) => (
              <motion.div
                key={g.id}
                whileHover={{ y: -3 }}
                whileTap={{ scale: 0.97 }}
                onClick={() => {
                  haptic.light()
                  push({ type: 'guild', id: g.id })
                }}
                className="glass-card cursor-pointer p-5 rounded-3xl border border-primary/15 bg-gradient-to-br from-card via-primary/5 to-transparent hover:border-primary/30 transition-all flex flex-col justify-between gap-3 group relative overflow-hidden shadow-sm"
              >
                <div className="flex items-center gap-3.5">
                  <div className="size-12 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center shrink-0 shadow-inner">
                    {g.icon_url ? (
                      <img
                        src={g.icon_url}
                        alt={g.name}
                        className="size-full object-cover rounded-2xl"
                      />
                    ) : (
                      <Shield className="size-6 text-primary" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-black text-sm truncate group-hover:text-primary transition-colors font-heading">
                      {g.name}
                    </h4>
                    <p className="text-[11px] text-muted-foreground line-clamp-1 mt-0.5">
                      {g.description || 'Официальный клановый состав'}
                    </p>
                  </div>
                </div>

                <div>
                  <div className="flex justify-between text-[10px] font-black uppercase tracking-wider text-muted-foreground mb-1">
                    <span>Участники</span>
                    <span className="text-primary font-bold">
                      {g.member_count} / {g.max_members}
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-muted/60 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-primary to-violet-500 rounded-full transition-all duration-500"
                      style={{
                        width: `${Math.min(100, (g.member_count / g.max_members) * 100)}%`,
                      }}
                    />
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </section>

      {/* Main Grid: Col-8 (Left) & Col-4 (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column (8 grid-spans) */}
        <div className="lg:col-span-8 flex flex-col gap-8">
          {/* 4. Popular Guides (Horizontal) */}
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

          {/* 5. Newest Updates */}
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
          {/* 6. Support Project Banner */}
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

          {/* 7. Community Pulse */}
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

      {/* 8. Categories List at the bottom */}
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
