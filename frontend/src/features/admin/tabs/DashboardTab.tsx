import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { apiFetch, apiPost, apiImport } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { toast } from 'sonner'
import {
  ChevronRight,
  Download,
  Eye,
  FileText,
  LayoutGrid,
  MessageSquare,
  RefreshCw,
  TrendingUp,
  Upload,
} from '@/lib/icons'
import type { AdminStats, Guide } from '@/lib/types'
import { cn } from '@/lib/utils'
import { type FC, type ChangeEvent, useEffect, useState } from 'react'
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

interface AnalyticsData {
  day: string
  count: number
}

export const DashboardTab: FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [chartData, setChartData] = useState<AnalyticsData[]>([])
  const [guides, setGuides] = useState<Guide[]>([])
  const [loading, setLoading] = useState(true)
  const [clearing, setClearing] = useState(false)

  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const loadData = async () => {
    setLoading(true)
    setErrorMsg(null)
    try {
      const [s, c, g] = await Promise.all([
        apiFetch<AdminStats>('/api/admin/stats').catch(() => ({
          guides: 0,
          categories: 0,
          views: 0,
          comments: 0,
        })),
        apiFetch<AnalyticsData[]>('/api/admin/analytics/views?days=30').catch(() => []),
        apiFetch<Guide[]>('/api/admin/guides?limit=5').catch(() => []),
      ])
      setStats(s || { guides: 0, categories: 0, views: 0, comments: 0 })
      setChartData(c || [])
      setGuides(g || [])
    } catch (ex) {
      setErrorMsg('Не удалось загрузить часть системной статистики')
      setStats({ guides: 0, categories: 0, views: 0, comments: 0 })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleClearCache = async () => {
    setClearing(true)
    try {
      await apiPost('/api/admin/cache/clear', {})
      toast.success('Кэш Redis успешно очищен')
    } catch (e: unknown) {
      toast.error('Ошибка очистки кэша')
    } finally {
      setClearing(false)
    }
  }

  const handleExportBackup = async () => {
    try {
      const data = await apiFetch<unknown>('/api/admin/backup/export')
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `blackrose_backup_${new Date().toISOString().slice(0, 10)}.json`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e: any) {
      toast.error('Ошибка экспорта бэкапа: ' + (e.message || e))
    }
  }

  const handleImportBackup = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    try {
      const text = await file.text()
      const parsed = JSON.parse(text)
      const res = (await apiImport(parsed)) as { categories?: number; guides?: number }
      toast.success(`База успешно восстановлена! Категорий: ${res.categories || 0}, Гайдов: ${res.guides || 0}`)
      haptic.success()
      loadData()
    } catch (err: any) {
      toast.error('Ошибка реставрации бэкапа: ' + (err.message || err))
    } finally {
      e.target.value = ''
    }
  }

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center flex-col gap-4">
        <div className="adm2-spinner" />
        <span className="text-xs font-bold text-muted-foreground uppercase font-heading">Загрузка данных системы...</span>
      </div>
    )
  }

  const activeStats = stats || { guides: 0, categories: 0, views: 0, comments: 0 }

  const statCards = [
    {
      label: 'Гайдов',
      value: activeStats.guides,
      icon: FileText,
      color: 'text-rose-400',
      bg: 'bg-rose-500/10',
    },
    {
      label: 'Категорий',
      value: activeStats.categories,
      icon: LayoutGrid,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
    },
    {
      label: 'Просмотров',
      value: (activeStats.views ?? 0).toLocaleString(),
      icon: Eye,
      color: 'text-cyan-400',
      bg: 'bg-cyan-500/10',
    },
    {
      label: 'Комментариев',
      value: activeStats.comments ?? 0,
      icon: MessageSquare,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
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
              <XAxis dataKey="day" stroke="#888888" fontSize={10} tickLine={false} axisLine={false} />
              <YAxis stroke="#888888" fontSize={10} tickLine={false} axisLine={false} />
              <Tooltip contentStyle={{ background: '#0c101c', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px' }} />
              <Area type="monotone" dataKey="count" stroke="var(--color-primary)" fillOpacity={1} fill="url(#colorViews)" />
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

      <div className="space-y-4 pt-8 border-t border-border/10">
        <div className="flex items-center gap-2">
          <RefreshCw className="size-4 text-primary" />
          <h3 className="text-sm font-black uppercase tracking-widest text-foreground/40">
            Обслуживание системы & Бэкап
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                <div className="text-sm font-bold text-foreground font-heading">Полный Бэкап Базы (JSON)</div>
                <div className="text-[11px] font-medium text-muted-foreground/60 leading-relaxed">
                  Скачать резервный снимок всех гайдов, категорий, гильдий и настроек.
                </div>
              </div>
              <Button
                variant="default"
                className="rounded-2xl h-11 px-5 gap-2 bg-primary text-primary-foreground hover:bg-primary/90 transition-all cursor-pointer w-full shadow-lg shadow-primary/20"
                onClick={handleExportBackup}
              >
                <Download className="size-4" />
                <span>Скачать Бэкап</span>
              </Button>
            </div>
          </Card>

          <Card className="p-6 border border-emerald-500/20 glass-card rounded-3xl shadow-lg bg-gradient-to-br from-emerald-500/10 via-card to-transparent">
            <div className="flex flex-col justify-between h-full gap-4">
              <div className="space-y-1">
                <div className="text-sm font-bold text-foreground font-heading">Восстановить Бэкап (JSON)</div>
                <div className="text-[11px] font-medium text-muted-foreground/60 leading-relaxed">
                  Загрузить JSON файл резервной копии для развертывания контента.
                </div>
              </div>
              <label className="inline-flex items-center justify-center gap-2 rounded-2xl h-11 px-5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs uppercase tracking-wider transition-all cursor-pointer w-full shadow-lg shadow-emerald-950/30 border border-white/10">
                <Upload className="size-4" />
                <span>Восстановить из файла</span>
                <input
                  type="file"
                  accept=".json,application/json"
                  className="hidden"
                  onChange={handleImportBackup}
                />
              </label>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
