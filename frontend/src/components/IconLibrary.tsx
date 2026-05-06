import { SyntheticEvent, FC } from 'react';
import type React from 'react'
import { useEffect, useRef, useState } from 'react'
import { apiIconsGrouped } from '../lib/api'
import { haptic } from '../lib/haptic'
import { Check, ChevronDown, ChevronRight, Search, X } from '../lib/icons'
import { normalizeUrl } from '../lib/utils'

interface Icon {
  key: string
  url: string
}

interface IconGroup {
  id: string
  label: string
  icons: Icon[]
}

/**
 * IconLibrary — Directory of all icons grouped by category.
 * Clicking an icon copies {{key}} to clipboard.
 */
export const IconLibrary: FC = () => {
  const [groups, setGroups] = useState<IconGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState('')
  const [copied, setCopied] = useState<string | null>(null)
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({})
  const toastTimer = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    apiIconsGrouped()
      .then((response) => {
        const data = (
          Array.isArray(response)
            ? response
            : (response as unknown as { data: IconGroup[] }).data || []
        ) as IconGroup[]
        setGroups(data)
        const initial: Record<string, boolean> = {}
        data.slice(0, 2).forEach((g) => {
          initial[g.id] = true
        })
        setOpenGroups(initial)
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  const handleCopy = (key: string) => {
    const tag = `{{${key}}}`
    navigator.clipboard?.writeText(tag).catch(() => {
      const el = document.createElement('textarea')
      el.value = tag
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
    })
    haptic.success()
    setCopied(key)
    if (toastTimer.current) clearTimeout(toastTimer.current)
    toastTimer.current = setTimeout(() => setCopied(null), 1800)
  }

  const toggleGroup = (id: string) => {
    setOpenGroups((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const expandAll = () => {
    const all: Record<string, boolean> = {}
    groups.forEach((g) => {
      all[g.id] = true
    })
    setOpenGroups(all)
  }
  const collapseAll = () => setOpenGroups({})

  const q = filter.trim().toLowerCase()
  const filtered = q
    ? groups
        .map((g) => ({ ...g, icons: g.icons.filter((i) => i.key.toLowerCase().includes(q)) }))
        .filter((g) => g.icons.length > 0)
    : groups

  const totalVisible = filtered.reduce((s, g) => s + g.icons.length, 0)

  if (loading)
    return (
      <div className="flex items-center justify-center p-12">
        <div className="adm2-spinner" />
      </div>
    )
  if (error) return <div className="adm2-error mx-4 my-4">⚠️ {error}</div>

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Search Header */}
      <div className="sticky top-0 z-10 bg-background/80 backdrop-blur-md px-4 py-3 border-b border-border space-y-3">
        <div className="relative flex items-center bg-muted rounded-xl px-3 py-2">
          <Search className="size-4 text-muted-foreground mr-2" />
          <input
            className="flex-1 bg-transparent border-none outline-none text-sm placeholder:text-muted-foreground"
            placeholder="Поиск по ключу..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            autoComplete="off"
          />
          {filter && (
            <button
              className="text-muted-foreground hover:text-foreground p-1 transition-colors"
              onClick={() => setFilter('')}
            >
              <X className="size-4" />
            </button>
          )}
        </div>

        <div className="flex items-center justify-between text-xs font-medium text-muted-foreground px-1">
          <span>{totalVisible} иконок</span>
          {!q && (
            <div className="flex gap-4">
              <button className="text-primary hover:underline" onClick={expandAll}>
                развернуть все
              </button>
              <button className="text-primary hover:underline" onClick={collapseAll}>
                свернуть все
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="p-4 space-y-6">
        {/* Instruction Hint */}
        <div className="bg-secondary/50 rounded-xl p-4 border border-border text-xs leading-relaxed text-muted-foreground">
          👆 Нажми на иконку — скопируется <code>{'{{key}}'}</code> для вставки в текст гайда
        </div>

        {/* Groups List */}
        <div className="space-y-4">
          {filtered.map((group) => (
            <div
              key={group.id}
              className="border border-border rounded-2xl overflow-hidden bg-card shadow-sm"
            >
              <button
                className="w-full flex items-center gap-2 px-4 py-4 hover:bg-muted/50 transition-colors text-left"
                onClick={() => toggleGroup(group.id)}
              >
                <span className="font-bold text-sm tracking-tight">{group.label}</span>
                <span className="bg-muted text-[10px] font-bold px-2 py-0.5 rounded-full text-muted-foreground">
                  {group.icons.length}
                </span>
                <span className="ml-auto text-muted-foreground">
                  {q || openGroups[group.id] ? (
                    <ChevronDown className="size-4" />
                  ) : (
                    <ChevronRight className="size-4" />
                  )}
                </span>
              </button>

              {(q || openGroups[group.id]) && (
                <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-2 p-4 bg-background/50 border-t border-border">
                  {group.icons.map((icon) => (
                    <button
                      key={icon.key}
                      className={`
                        group relative flex flex-col items-center gap-2 p-2 rounded-xl border border-transparent transition-all
                        hover:border-primary/20 hover:bg-primary/5 active:scale-95
                        ${copied === icon.key ? 'border-green-500/50 bg-green-500/10' : ''}
                      `}
                      onClick={() => handleCopy(icon.key)}
                      title={`Скопировать {{${icon.key}}}`}
                    >
                      <img
                        src={normalizeUrl(icon.url)}
                        alt={icon.key}
                        width={32}
                        height={32}
                        className="object-contain"
                        loading="lazy"
                        onError={(e: SyntheticEvent<HTMLImageElement>) => {
                          e.currentTarget.style.opacity = '0.2'
                        }}
                      />
                      <span
                        className={`
                        text-[9px] text-center font-medium line-clamp-2 break-all px-1
                        ${copied === icon.key ? 'text-green-600 font-bold' : 'text-muted-foreground'}
                      `}
                      >
                        {copied === icon.key ? (
                          <span className="flex items-center gap-0.5">
                            <Check className="size-2.5" /> Copied
                          </span>
                        ) : (
                          icon.key
                        )}
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="py-20 text-center space-y-2">
            <div className="text-4xl">🔎</div>
            <div className="text-muted-foreground font-medium">Ничего не найдено</div>
            <div className="text-xs text-muted-foreground/60">Попробуйте изменить запрос</div>
          </div>
        )}
      </div>

      {/* Modern Toast Notification */}
      {copied && (
        <div className="fixed bottom-20 left-1/2 -translate-x-1/2 bg-foreground text-background px-4 py-2.5 rounded-2xl text-sm font-semibold shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-300 z-[100] flex items-center gap-2">
          <Check className="size-4 text-green-400" />
          <span>
            Ключ{' '}
            <code className="text-primary-foreground/80 font-geist-mono">{`{{${copied}}}`}</code>{' '}
            скопирован
          </span>
        </div>
      )}
    </div>
  )
}
