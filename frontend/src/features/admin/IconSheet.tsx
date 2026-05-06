import { SyntheticEvent, FC } from 'react';
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { apiIconsGrouped } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { ChevronDown, ChevronRight, Hash, ImageIcon, Search, X } from '@/lib/icons'
import { cn } from '@/lib/utils'
import type React from 'react'
import { useEffect, useState } from 'react'
import { IC } from './adminIcons'

interface Icon {
  key: string
  url: string
}

interface IconGroup {
  id: string
  label: string
  icons: Icon[]
}

interface IconSheetProps {
  onInsert: (key: string) => void
  onClose: () => void
}

/**
 * IconSheet — Improved icon picker drawer for the rich editor.
 */
export const IconSheet: FC<IconSheetProps> = ({ onInsert, onClose }) => {
  const [groups, setGroups] = useState<IconGroup[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('')
  const [open, setOpen] = useState<Record<string, boolean>>({})

  useEffect(() => {
    apiIconsGrouped()
      .then((response: IconGroup[] | { data: IconGroup[] }) => {
        const data = Array.isArray(response) ? response : response.data
        setGroups(data)
        if (data[0]) setOpen({ [data[0].id]: true })
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const q = filter.trim().toLowerCase()
  const filtered = q
    ? groups
        .map((g) => ({ ...g, icons: g.icons.filter((i) => i.key.toLowerCase().includes(q)) }))
        .filter((g) => g.icons.length > 0)
    : groups

  return (
    <div
      className="fixed inset-0 z-[110] flex items-end justify-center bg-black/40 p-4 backdrop-blur-sm animate-in fade-in duration-200 sm:items-center"
      onClick={onClose}
    >
      <Card
        className="flex h-[80vh] w-full max-w-lg flex-col overflow-hidden bg-background shadow-2xl animate-in slide-in-from-bottom-8 duration-300 sm:h-[70vh] rounded-[28px] border-none"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-border/10 px-6 py-5">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-primary/10 rounded-xl text-primary">
              <ImageIcon className="size-4" />
            </div>
            <h3 className="text-lg font-bold tracking-tight">Вставить иконку</h3>
          </div>
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full hover:bg-muted"
            onClick={onClose}
          >
            <X className="size-5" />
          </Button>
        </div>

        <div className="px-6 py-4">
          <div className="relative group">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-primary" />
            <Input
              className="h-11 border-none bg-muted/50 pl-10 text-sm focus-visible:bg-background focus-visible:ring-2 focus-visible:ring-primary/20"
              placeholder="Поиск по названию..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              autoFocus
            />
            {filter && (
              <button
                className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground p-1"
                onClick={() => setFilter('')}
              >
                <X className="size-4" />
              </button>
            )}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-6 pb-6 no-scrollbar">
          {loading && (
            <div className="flex h-40 items-center justify-center">
              <div className="adm2-spinner" />
            </div>
          )}

          <div className="space-y-3">
            {filtered.map((group) => (
              <div
                key={group.id}
                className="border border-border/10 rounded-2xl overflow-hidden bg-background"
              >
                <button
                  className="flex w-full items-center gap-3 px-4 py-4 text-left transition-colors hover:bg-muted/30"
                  onClick={() => setOpen((prev) => ({ ...prev, [group.id]: !prev[group.id] }))}
                >
                  <span className="text-sm font-bold tracking-tight text-foreground/80">
                    {group.label}
                  </span>
                  <span className="flex items-center justify-center h-5 px-2 bg-muted rounded-full text-[10px] font-bold text-muted-foreground">
                    {group.icons.length}
                  </span>
                  <div className="ml-auto text-muted-foreground">
                    {q || open[group.id] ? (
                      <ChevronDown className="size-4" />
                    ) : (
                      <ChevronRight className="size-4" />
                    )}
                  </div>
                </button>

                {(q || open[group.id]) && (
                  <div className="grid grid-cols-4 gap-2 p-3 bg-muted/20 border-t border-border/5">
                    {group.icons.map((icon) => (
                      <button
                        key={icon.key}
                        className="group relative flex flex-col items-center gap-2 rounded-xl border border-transparent p-2 transition-all hover:bg-primary/5 hover:border-primary/20 active:scale-95"
                        title={`{{${icon.key}}}`}
                        onClick={() => {
                          onInsert(icon.key)
                          haptic.light?.()
                        }}
                      >
                        <img
                          src={icon.url}
                          alt={icon.key}
                          width={28}
                          height={28}
                          className="object-contain"
                          loading="lazy"
                          onError={(e: SyntheticEvent<HTMLImageElement>) => {
                            e.currentTarget.style.opacity = '0.2'
                          }}
                        />
                        <span className="text-[9px] font-medium text-muted-foreground line-clamp-1 group-hover:text-primary transition-colors">
                          {icon.key}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {!loading && filtered.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-center space-y-3 opacity-40">
              <Search className="size-10" />
              <div className="text-sm font-bold">Ничего не найдено</div>
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
