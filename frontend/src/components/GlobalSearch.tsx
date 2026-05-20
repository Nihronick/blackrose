import { apiFetch } from '@/lib/api'
import type { Guide } from '@/lib/types'
import { ChevronRight, FileText, Loader2, Search } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

import { useAppStore } from '@/store'

export const GlobalSearch = () => {
  const { searchOpen: open, setSearchOpen: setOpen } = useAppStore()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<Guide[]>([])
  const [loading, setLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen(!useAppStore.getState().searchOpen)
      }
      if (e.key === 'Escape' && open) {
        setOpen(false)
      }
    }
    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [open])

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100)
    } else {
      setQuery('')
      setResults([])
    }
  }, [open])

  useEffect(() => {
    if (query.trim().length < 2) {
      setResults([])
      return
    }

    const timer = setTimeout(async () => {
      setLoading(true)
      try {
        const data = (await apiFetch(`/search?q=${encodeURIComponent(query)}`)) as {
          results: Guide[]
        }
        setResults(data.results || [])
      } catch (err) {
        console.error('Search failed', err)
      } finally {
        setLoading(false)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [query])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[20vh] sm:pt-[10vh] px-4 backdrop-blur-sm">
      <div className="fixed inset-0 bg-background/50" onClick={() => setOpen(false)} />
      <div className="relative w-full max-w-lg bg-card rounded-2xl shadow-2xl border ring-1 ring-border/5 overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-center px-4 border-b h-14">
          <Search className="size-5 text-muted-foreground shrink-0 mr-2" />
          <input
            ref={inputRef}
            className="flex-1 bg-transparent border-none outline-none text-base placeholder:text-foreground h-full"
            placeholder="Поиск гайдов..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          {loading && <Loader2 className="size-4 animate-spin text-muted-foreground" />}
          <div className="text-[10px] bg-muted px-1.5 py-0.5 rounded font-mono text-muted-foreground ml-2 hidden sm:block">
            ESC
          </div>
        </div>

        <div className="max-h-[60vh] overflow-y-auto overflow-x-hidden p-2">
          {query.length < 2 && results.length === 0 && (
            <div className="p-6 text-center text-sm text-muted-foreground">
              Введите хотя бы 2 символа для поиска
            </div>
          )}

          {query.length >= 2 && results.length === 0 && !loading && (
            <div className="p-6 text-center text-sm text-muted-foreground">Ничего не найдено</div>
          )}

          {results.map((g) => (
            <button
              key={g.key}
              onClick={() => {
                setOpen(false)
                window.location.hash = `#/guide/${g.key}`
              }}
              className="w-full text-left flex items-center gap-3 p-3 rounded-xl hover:bg-muted/50 transition-colors group"
            >
              <div className="size-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center shrink-0">
                <FileText className="size-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-sm text-foreground truncate">{g.title}</div>
                <div className="text-xs text-muted-foreground truncate opacity-70">
                  {g.preview?.substring(0, 60)}...
                </div>
              </div>
              <ChevronRight className="size-4 text-muted-foreground opacity-50 group-hover:opacity-100 transition-opacity" />
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
