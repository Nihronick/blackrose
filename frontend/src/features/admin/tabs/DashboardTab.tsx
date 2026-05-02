import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { apiFetch, apiPost } from '@/lib/api'
import { ChevronRight, Eye, FileText, LayoutGrid, MessageSquare, RefreshCw, TrendingUp } from '@/lib/icons'
import type { AdminStats, Guide } from '@/lib/types'
import { cn } from '@/lib/utils'
import { FC, useEffect, useState } from 'react'
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export const DashboardTab: FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [guides, setGuides] = useState<Guide[]>([])
  const [analytics, setAnalytics] = useState<any[]>([])
  const [clearing, setClearing] = useState(false)

  useEffect(() => {
    apiFetch<AdminStats>('/api/admin/stats')
      .then(setStats)
      .catch(() => {})
    apiFetch<{ results: Guide[] }>('/api/top')
      .then((res) => setGuides(res.results))
      .catch(() => {})
    apiFetch<{ chart: any[] }>('/api/admin/analytics?days=30')
      .then((res) => setAnalytics(res.chart))
      .catch(() => {})
  }, [])

  const handleClearCache = async () => {
    if (!window.confirm('Вы уверены, что хотите полностью очистить кэш? Это может временно замедлить работу приложения.')) return
    
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

  const chartData = (analytics || []).map(d => {
    const date = new Date(d.day)
    return {
      name: isNaN(date.getTime()) 
        ? '???' 
        : date.toLocaleDateString(undefined, { day: 'numeric', month: 'short' }),
      views: d.count
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
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => (
          <Card
            key={stat.label}
            className="p-5 border-none bg-card/40 backdrop-blur-sm shadow-sm ring-1 ring-border/5"
          >
            <div className={cn('inline-flex p-2.5 rounded-xl mb-3', stat.bg, stat.color)}>
              <stat.icon className="size-5" />
            </div>
            <div className="text-2xl font-black tracking-tighter mb-0.5">{stat.value}</div>
            <div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">
              {stat.label}
            </div>
          </Card>
        ))}
      </div>

      {/* Analytics Chart */}
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <TrendingUp className="size-4 text-primary" />
          <h3 className="text-sm font-black uppercase tracking-widest text-foreground/40">
            Тренд просмотров (30д)
          </h3>
        </div>
        <Card className="p-6 border-none bg-card/40 backdrop-blur-sm shadow-sm ring-1 ring-border/5 h-[300px] min-h-[300px] overflow-hidden">
          <ResponsiveContainer width="100%" height="100%" minHeight={200}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--color-primary)" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="var(--color-primary)" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis 
                dataKey="name" 
                axisLine={false} 
                tickLine={false} 
                tick={{fontSize: 10, fontWeight: 'bold', fill: 'var(--muted-foreground)'}}
                minTickGap={30}
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{fontSize: 10, fontWeight: 'bold', fill: 'var(--muted-foreground)'}}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'var(--card)', 
                  border: '1px solid var(--border)', 
                  borderRadius: '12px',
                  fontSize: '11px',
                  fontWeight: 'bold'
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

      {/* System Maintenance */}
      <div className="space-y-4 pt-8 border-t border-border/10">
        <div className="flex items-center gap-2">
          <RefreshCw className="size-4 text-primary" />
          <h3 className="text-sm font-black uppercase tracking-widest text-foreground/40">
            Обслуживание системы
          </h3>
        </div>
        <Card className="p-6 border-none bg-card/40 backdrop-blur-sm shadow-sm ring-1 ring-border/5">
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
            <div className="space-y-1">
              <div className="text-sm font-bold text-foreground">Очистка кэша Redis</div>
              <div className="text-[11px] font-medium text-muted-foreground/60 leading-relaxed max-w-md">
                Принудительно удаляет все сохраненные категории и данные гайдов из оперативной памяти. 
                Полезно, если данные в приложении не обновляются или отображаются некорректно.
              </div>
            </div>
            <Button 
              variant="outline" 
              className="rounded-xl h-12 px-6 gap-2 border-primary/20 hover:bg-primary/5 hover:text-primary transition-all active:scale-95 shrink-0"
              onClick={handleClearCache}
              disabled={clearing}
            >
              <RefreshCw className={cn("size-4", clearing && "animate-spin")} />
              <span>{clearing ? 'Очистка...' : 'Очистить кэш'}</span>
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}
