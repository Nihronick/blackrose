import { ErrorBoundary } from '@/components/ErrorBoundary'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { apiRecentComments, apiRecentGuides, apiTopGuides } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import {
  ChevronRight,
  Clock,
  Eye,
  MessageCircle,
  Sparkles,
  TrendingUp,
} from '@/lib/icons'
import { isLanguageKey } from '@/lib/language'
import { normalizeUrl } from '@/lib/utils'
import { useAppStore } from '@/store'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import type React from 'react'

interface HomeDashboardProps {
  onSelectGuide: (key: string, title?: string, icon?: string) => void
}

export const HomeDashboard: React.FC<HomeDashboardProps> = ({ onSelectGuide }) => {
  const language = useAppStore((state) => state.language)
  const userName = window.Telegram?.WebApp?.initDataUnsafe?.user?.first_name || 'Слеер'

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

  const topGuides = (topGuidesData?.results || []).filter((g) =>
    isLanguageKey(g.key, language)
  )
  const recentGuides = (recentGuidesData?.results || []).filter((g) =>
    isLanguageKey(g.key, language)
  )
  const recentComments = recentCommentsData?.comments || []

  return (
    <div className="flex flex-col gap-8 pb-4 animate-in fade-in duration-700">
      {/* 1. Hero Welcome */}
      <section className="px-5 pt-2">
        <div className="relative overflow-hidden rounded-[32px] bg-gradient-to-br from-primary/20 via-primary/5 to-transparent p-6 border border-primary/10 shadow-xl shadow-primary/5">
          <div className="relative z-10">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="size-4 text-primary animate-pulse" />
              <span className="text-[10px] font-black uppercase tracking-[0.2em] text-primary/70">
                Добро пожаловать
              </span>
            </div>
            <h1 className="text-3xl font-black tracking-tighter text-foreground mb-1">
              Привет, {userName}!
            </h1>
            <p className="text-sm font-medium text-muted-foreground/80 leading-relaxed max-w-[240px]">
              Сегодня отличный день, чтобы стать сильнее. С чего начнем?
            </p>
          </div>
          {/* Decorative element */}
          <div className="absolute -right-8 -top-8 size-40 rounded-full bg-primary/10 blur-3xl" />
        </div>
      </section>

      {/* 2. Popular Guides (Horizontal) */}
      <section className="flex flex-col gap-4">
        <div className="px-5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <TrendingUp className="size-4 text-primary" />
            <h3 className="text-xs font-black uppercase tracking-[0.15em] text-foreground/70">
              Популярное
            </h3>
          </div>
        </div>

        <div className="flex gap-4 overflow-x-auto px-5 no-scrollbar pb-2">
          {topLoading
            ? [...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-44 w-36 shrink-0 rounded-[24px] bg-muted/40" />
              ))
            : topGuides.map((g) => (
                <motion.div
                  key={g.key}
                  whileTap={{ scale: 0.96 }}
                  className="w-36 shrink-0 cursor-pointer"
                  onClick={() => {
                    haptic.light()
                    onSelectGuide(g.key, g.title, g.icon_url)
                  }}
                >
                  <Card className="h-full border-border/10 glass-card rounded-[24px] overflow-hidden flex flex-col">
                    <div className="relative aspect-square p-4 bg-muted/20 flex items-center justify-center">
                      <div className="size-16 rounded-2xl bg-background shadow-lg flex items-center justify-center p-2">
                        {g.icon_url ? (
                          <img
                            src={normalizeUrl(g.icon_url)}
                            alt=""
                            className="size-12 object-contain"
                          />
                        ) : (
                          <span className="text-2xl">📖</span>
                        )}
                      </div>
                      <Badge className="absolute top-2 right-2 h-5 rounded-full bg-primary/20 text-[9px] font-black text-primary px-1.5 border-0">
                        {g.views >= 1000 ? `${(g.views / 1000).toFixed(1)}k` : g.views}
                      </Badge>
                    </div>
                    <CardContent className="p-3 flex-1">
                      <h4 className="text-[13px] font-black tracking-tight leading-tight line-clamp-2">
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
        <div className="px-5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="size-4 text-emerald-400" />
            <h3 className="text-xs font-black uppercase tracking-[0.15em] text-foreground/70">
              Новинки
            </h3>
          </div>
        </div>

        <div className="flex flex-col gap-3 px-5">
          {recentLoading
            ? [...Array(2)].map((_, i) => (
                <Skeleton key={i} className="h-20 w-full rounded-2xl bg-muted/40" />
              ))
            : recentGuides.slice(0, 3).map((g) => (
                <motion.div
                  key={g.key}
                  whileTap={{ scale: 0.98 }}
                  className="group cursor-pointer rounded-2xl border border-border/5 bg-muted/20 p-4 transition-all hover:bg-muted/30"
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
                        <span className="text-xl">📄</span>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h4 className="text-[14px] font-black tracking-tight leading-tight line-clamp-1 group-hover:text-primary transition-colors">
                        {g.title}
                      </h4>
                      <p className="mt-1 text-[10px] font-medium text-muted-foreground/60 uppercase tracking-wider">
                        Обновлено: {new Date(g.updated_at || '').toLocaleDateString()}
                      </p>
                    </div>
                    <ChevronRight className="size-4 text-muted-foreground/30 group-hover:text-primary transition-colors" />
                  </div>
                </motion.div>
              ))}
        </div>
      </section>

      {/* 4. Community Pulse (Latest Comments) */}
      <section className="flex flex-col gap-4">
        <div className="px-5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageCircle className="size-4 text-amber-400" />
            <h3 className="text-xs font-black uppercase tracking-[0.15em] text-foreground/70">
              Пульс сообщества
            </h3>
          </div>
        </div>

        <div className="px-5">
          <div className="rounded-[28px] border border-border/10 bg-muted/10 p-5">
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
        </div>
      </section>
    </div>
  )
}
