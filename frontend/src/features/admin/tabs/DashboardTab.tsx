import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { apiFetch, apiPost } from '@/lib/api'
import {
  ChevronRight,
  Download,
  Eye,
  FileText,
  LayoutGrid,
  MessageSquare,
  RefreshCw,
  TrendingUp,
} from '@/lib/icons'
import type { AdminStats, Guide } from '@/lib/types'
import { cn } from '@/lib/utils'
import { type FC, useEffect, useState } from 'react'
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

interface AnalyticsData {
  day: string
  count: number
}

export const DashboardTab: FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [guides, setGuides] = useState<Guide[]>([])
  const [analytics, setAnalytics] = useState<AnalyticsData[]>([])
  const [clearing, setClearing] = useState(false)

  useEffect(() => {
    apiFetch<AdminStats>('/api/admin/stats')
      .then(setStats)
      .catch(() => {})
    apiFetch<{ results: Guide[] }>('/api/top')
      .then((res) => setGuides(res.results))
      .catch(() => {})
    apiFetch<{ chart: AnalyticsData[] }>('/api/admin/analytics?days=30')
      .then((res) => setAnalytics(res.chart))
      .catch(() => {})
  }, [])

  const handleClearCache = async () => {
    if (
      !window.confirm(
        'Вы уверены, что хотите полностью очистить кэш? Это может временно замедлить работу приложения.'
      )
    )
      return

    setClearing(true)
    try {
      await apiPost('/api/admin/cache/clear', {})
      alert('Кэш успешно очищен')
    } catch (e) {
      alert('Ошибка при очистке кэша: ' + (e instanceof Error ? e.message : 'Unknown error'))
    } finally {
      setClearing(false)
    }
  }

  const handleExportBackup = async () => {
    try {
      const data = await apiFetch<unknown>('/api/admin/backup/export')
      const jsonStr = JSON.stringify(data, null, 2)
      const blob = new Blob([jsonStr], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `blackrose_backup_${Date.now()}.json`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      alert('Ошибка скачивания бэкапа: ' + e)
    }
  }

  const chartData = (analytics || []).map((d) => {
    const date = new Date(d.day)
    return {
      name: Number.isNaN(date.getTime())
        ? '???'
        : date.toLocaleDateString(undefined, { day: 'numeric', month: 'short' }),
      views: d.count,
    }
  })

  if (!stats) {
    return (
      <div className="flex h-60 items-center justify-center">
        <div className="adm2-spinner" />
      </div>
    )
  }

  const statCards = [
    {
      label: 'Гайдов',
      value: stats.guides,
      icon: FileText,
      color: 'text-blue-500',
      bg: 'bg-blue-500/10',
    },
    {
      label: 'Категорий',
      value: stats.categories,
      icon: LayoutGrid,
      color: 'text-green-500',
      bg: 'bg-green-500/10',
    },
    {
      label: 'Просмотров',
      value: (stats.views ?? 0).toLocaleString(),
      icon: Eye,
      color: 'text-orange-500',
      bg: 'bg-orange-500/10',
    },
    {
      label: 'Комментариев',
      value: stats.comments ?? 0,
      icon: MessageSquare,
      color: 'text-purple-500',
      bg: 'bg-purple-500/10',
    },
  ]

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {statCards.map((stat) => (
          <Card
            key={stat.label}
            className="p-6 border border-border/10 glass-card rounded-3xl shadow-lg hover:border-primary/30 hover:-translate-y-1 transition-all duration-300 group"
          >
            <div className={cn('inline-flex p-3 rounded-2xl mb-4 group-hover:scale-110 transition-transform', stat.bg, stat.color)}>
              <stat.icon className="size-6" />
            </div>
            <div className="text-3xl font-black tracking-tight mb-1 font-heading">{stat.value}</div>
            <div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/70">
              {stat.label}
            </div>
          </Card>
        ))}
      </div>

      {/* Analytics Chart */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="size-4 text-primary" />
          <h3 className="text-xs font-black uppercase tracking-widest text-muted-foreground">
            Тренд просмотров (30 дней)
          </h3>
        </div>
        <Card className="p-6 border border-border/10 glass-card rounded-3xl shadow-xl h-[360px] min-h-[360px] overflow-hidden">
          <ResponsiveContainer width="100%" height="100%" minHeight={200}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis
                dataKey="name"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 10, fontWeight: 'bold', fill: 'var(--muted-foreground)' }}
                minTickGap={30}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 10, fontWeight: 'bold', fill: 'var(--muted-foreground)' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--card)',
                  border: '1px solid var(--border)',
                  borderRadius: '12px',
                  fontSize: '11px',
                  fontWeight: 'bold',
                }}
              />
              <Area
                type="monotone"
                dataKey="views"
                stroke="var(--color-primary)"
                strokeWidth={3}
                fillOpacity={1}
                fill="url(#colorViews)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="size-4 text-primary" />
          <h3 className="text-sm font-black uppercase tracking-widest text-foreground/40">
            Популярный контент
          </h3>
        </div>

        <div className="grid grid-cols-1 gap-2">
          {guides.map((g, i) => (
            <div
              key={g.key}
              className="group relative flex items-center gap-4 p-3 bg-muted/20 hover:bg-muted/40 rounded-2xl transition-all border border-transparent hover:border-border/50"
            >
              <span className="flex size-7 items-center justify-center rounded-lg bg-background font-black text-[11px] text-muted-foreground group-hover:bg-primary group-hover:text-primary-foreground transition-colors shadow-sm ring-1 ring-border/5">
                {i + 1}
              </span>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-bold truncate pr-4">{g.title}</div>
                <div className="flex items-center gap-2 mt-0.5">
                  <Eye className="size-3 text-muted-foreground/40" />
                  <span className="text-[10px] font-bold text-muted-foreground/60">
                    {g.views} просмотров
                  </span>
                </div>
              </div>
              <ChevronRight className="size-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-all -translate-x-2 group-hover:translate-x-0" />
            </div>
          ))}
        </div>
      </div>

      {/* System Maintenance & Backup */}
      <div className="space-y-4 pt-8 border-t border-border/10">
        <div className="flex items-center gap-2">
          <RefreshCw className="size-4 text-primary" />
          <h3 className="text-sm font-black uppercase tracking-widest text-foreground/40">
            Обслуживание системы & Бэкап
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="p-6 border border-border/10 glass-card rounded-3xl shadow-lg">
            <div className="flex flex-col justify-between h-full gap-4">
              <div className="space-y-1">
                <div className="text-sm font-bold text-foreground font-heading">Очистка кэша Redis</div>
                <div className="text-[11px] font-medium text-muted-foreground/60 leading-relaxed">
                  Принудительно удаляет кэшированные данные из оперативной памяти сервера.
                </div>
              </div>
              <Button
                variant="outline"
                className="rounded-2xl h-11 px-5 gap-2 border-primary/20 hover:bg-primary/5 hover:text-primary transition-all cursor-pointer w-full"
                onClick={handleClearCache}
                disabled={clearing}
              >
                <RefreshCw className={cn('size-4', clearing && 'animate-spin')} />
                <span>{clearing ? 'Очистка...' : 'Очистить кэш'}</span>
              </Button>
            </div>
          </Card>

          <Card className="p-6 border border-primary/20 glass-card rounded-3xl shadow-lg bg-gradient-to-br from-primary/10 via-card to-transparent">
            <div className="flex flex-col justify-between h-full gap-4">
              <div className="space-y-1">
                <div className="text-sm font-bold text-foreground font-heading">Полный Бэкап Базы Данных</div>
                <div className="text-[11px] font-medium text-muted-foreground/60 leading-relaxed">
                  Скачать резервный дамповый снимок всех гайдов, категорий, гильдий и настроек в формате JSON.
                </div>
              </div>
              <Button
                variant="default"
                className="rounded-2xl h-11 px-5 gap-2 bg-primary text-primary-foreground hover:bg-primary/90 transition-all cursor-pointer w-full shadow-lg shadow-primary/20"
                onClick={handleExportBackup}
              >
                <Download className="size-4" />
                <span>Скачать Бэкап (JSON)</span>
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
