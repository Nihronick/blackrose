import { Badge } from '@/components/ui/badge'
import { apiFetch } from '@/lib/api'
import { ChevronRight, Clock, FileJson, User } from '@/lib/icons'
import type { Guide, GuideHistory, HistoryResponse } from '@/lib/types'
import { cn } from '@/lib/utils'
import type React from 'react'
import { useCallback, useEffect, useMemo, useState } from 'react'

export const HistoryTab: React.FC = () => {
  const [guides, setGuides] = useState<Guide[]>([])
  const [selected, setSelected] = useState<Guide | null>(null)
  const [history, setHistory] = useState<GuideHistory[]>([])
  const [loadingH, setLoadingH] = useState(false)

  useEffect(() => {
    apiFetch<Guide[]>('/api/admin/guides')
      .then(setGuides)
      .catch(() => {})
  }, [])

  const loadHistory = useCallback(async (g: Guide) => {
    setSelected(g)
    setLoadingH(true)
    try {
      const data = await apiFetch<HistoryResponse>(`/api/admin/guide/${g.key}/history`)
      setHistory(data.history || [])
    } catch {
    } finally {
      setLoadingH(false)
    }
  }, [])

  const fmt = useCallback(
    (iso: string) =>
      iso
        ? new Date(iso).toLocaleString('ru', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit',
          })
        : '—',
    []
  )

  const actionLabel = useCallback(
    (a: string) =>
      ({ create: 'Создан', update: 'Изменён', delete: 'Удалён', import: 'Импорт' })[a] || a,
    []
  )

  const actionColor = useCallback(
    (a: string) =>
      ({
        create: 'text-green-500 bg-green-500/10',
        update: 'text-blue-500 bg-blue-500/10',
        delete: 'text-destructive bg-destructive/10',
        import: 'text-orange-500 bg-orange-500/10',
      })[a] || 'text-muted-foreground bg-muted',
    []
  )

  return (
    <div className="flex h-full animate-in fade-in duration-300">
      <div className="w-[45%] flex flex-col border-r border-border/10">
        <div className="px-4 py-4 border-b border-border/5">
          <h3 className="text-[10px] font-black uppercase tracking-widest text-foreground/30">
            История изменений
          </h3>
        </div>
        <div className="flex-1 overflow-y-auto px-2 py-3 space-y-1 no-scrollbar">
          {guides.map((g) => (
            <button
              key={g.key}
              onClick={() => loadHistory(g)}
              className={cn(
                'w-full text-left px-3 py-2.5 rounded-xl text-xs font-bold transition-all',
                selected?.key === g.key
                  ? 'bg-primary/10 text-primary shadow-sm'
                  : 'text-muted-foreground hover:bg-muted/50'
              )}
            >
              {g.title}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 flex flex-col bg-muted/20">
        <div className="flex-1 overflow-y-auto px-4 py-8 space-y-4 no-scrollbar">
          {!selected && (
            <div className="flex h-full flex-col items-center justify-center text-center opacity-30 space-y-3">
              <Clock className="size-10" />
              <div className="text-sm font-bold">Выберите гайд слева</div>
            </div>
          )}

          {selected && loadingH && (
            <div className="flex h-40 items-center justify-center">
              <div className="adm2-spinner" />
            </div>
          )}

          {selected && !loadingH && history.length === 0 && (
            <div className="flex h-40 flex-col items-center justify-center text-center opacity-30 space-y-2">
              <FileJson className="size-8" />
              <div className="text-xs font-bold">Пусто</div>
            </div>
          )}

          {selected &&
            !loadingH &&
            history.map((h) => (
              <div
                key={h.id}
                className="p-4 bg-background rounded-2xl border border-border/10 shadow-sm animate-in slide-in-from-bottom-2 duration-200"
              >
                <div className="flex items-center justify-between mb-3">
                  <Badge
                    className={cn(
                      'px-2 py-0.5 rounded-full text-[9px] border-none',
                      actionColor(h.action)
                    )}
                  >
                    {actionLabel(h.action)}
                  </Badge>
                  <div className="flex items-center gap-1.5 text-muted-foreground/60">
                    <Clock className="size-3" />
                    <span className="text-[10px] font-bold">{fmt(h.changed_at)}</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 mb-3">
                  <div className="flex size-7 items-center justify-center rounded-lg bg-muted">
                    <User className="size-3.5 text-muted-foreground/60" />
                  </div>
                  <div className="text-[10px] font-bold text-muted-foreground/80">
                    User ID: {h.changed_by || 'system'}
                  </div>
                </div>

                {h.snapshot ? (
                  <details className="group">
                    <summary className="flex items-center gap-1 text-[10px] font-black uppercase tracking-wider text-primary cursor-pointer hover:underline list-none">
                      <ChevronRight className="size-3 transition-transform group-open:rotate-90" />
                      Просмотреть снапшот
                    </summary>
                    <pre className="mt-2 p-3 bg-muted/50 rounded-xl text-[10px] font-mono leading-relaxed overflow-x-auto max-h-40 no-scrollbar">
                      {JSON.stringify(h.snapshot, null, 2)}
                    </pre>
                  </details>
                ) : null}
              </div>
            ))}
        </div>
      </div>
    </div>
  )
}
