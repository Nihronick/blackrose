import { ReorderList } from '@/components/ReorderList'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiDelete, apiFetch, apiReorderGuides } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { Edit2, LayoutGrid, Plus, Search, Trash2 } from '@/lib/icons'
import type { Category, Guide } from '@/lib/types'
import { cn } from '@/lib/utils'
import type React from 'react'
import { useCallback, useEffect, useState } from 'react'
import { GuideEditor } from '../AdminGuideEditor'
import { IconPreview } from './components/IconPreview'

interface GuidesTabProps {
  categories: Category[]
  importedGuide?: any
  onImportProcessed?: () => void
}

export const GuidesTab: React.FC<GuidesTabProps> = ({ categories, importedGuide, onImportProcessed }) => {
  const [guides, setGuides] = useState<Guide[]>([])
  const [catFilter, setCatFilter] = useState('')
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState<Guide | 'new' | null>(null)
  const [loading, setLoading] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const path = catFilter ? `/api/admin/guides?category_key=${catFilter}` : '/api/admin/guides'
      const data = await apiFetch<Guide[]>(path)
      setGuides(data)
    } catch {
    } finally {
      setLoading(false)
    }
  }, [catFilter])

  useEffect(() => {
    load()
  }, [load])

  useEffect(() => {
    if (importedGuide) {
      setEditing(importedGuide)
      onImportProcessed?.()
    }
  }, [importedGuide, onImportProcessed])

  const handleDelete = useCallback(
    async (g: Guide) => {
      if (!window.confirm(`Удалить гайд "${g.title}"?`)) return
      setDeleting(g.key)
      try {
        await apiDelete(`/api/admin/guide/${g.key}`)
        haptic.success?.()
        load()
      } catch (e) {
        const err = e instanceof Error ? e : new Error(String(e))
        alert(err.message)
      } finally {
        setDeleting(null)
      }
    },
    [load]
  )

  const handleEdit = useCallback(async (g: Guide) => {
    try {
      const full = await apiFetch<Guide>(`/api/admin/guide/${g.key}`)
      setEditing(full)
    } catch (e) {
      const err = e instanceof Error ? e : new Error(String(e))
      alert(`Ошибка загрузки: ${err.message}`)
    }
  }, [])

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value)
  }, [])

  const handleCategoryFilterChange = useCallback((key: string) => {
    setCatFilter(key)
  }, [])

  const handleReorder = useCallback(async (newOrder: Guide[]) => {
    await apiReorderGuides(newOrder.map((g, i) => ({ key: g.key, sort_order: i * 10 }))).catch(
      () => {}
    )
  }, [])

  const visible = guides.filter(
    (g) =>
      !search ||
      g.title.toLowerCase().includes(search.toLowerCase()) ||
      g.key.toLowerCase().includes(search.toLowerCase())
  )

  if (editing !== null) {
    return (
      <GuideEditor
        guide={editing === 'new' ? null : editing}
        categories={categories}
        onSave={() => {
          setEditing(null)
          load()
        }}
        onCancel={() => setEditing(null)}
      />
    )
  }

  return (
    <div className="flex flex-col h-full animate-in fade-in duration-300">
      <div className="sticky top-0 z-10 bg-background/80 backdrop-blur-lg px-4 pt-1 pb-4 border-b border-border/10 space-y-4">
        <div className="flex items-center gap-2">
          <div className="relative flex-1 group">
            <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground group-focus-within:text-primary transition-colors" />
            <Input
              className="h-11 border-none bg-muted/50 pl-10 text-sm font-medium focus-visible:bg-background focus-visible:ring-2 focus-visible:ring-primary/20"
              placeholder="Поиск по гайдам..."
              value={search}
              onChange={handleSearchChange}
            />
          </div>
          <Button
            className="size-11 rounded-xl shadow-lg shadow-primary/20 shrink-0"
            onClick={() => setEditing('new')}
          >
            <Plus className="size-6" />
          </Button>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
            <button
              onClick={() => handleCategoryFilterChange('')}
              className={cn(
                'px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-wider transition-all whitespace-nowrap',
                catFilter === ''
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              )}
            >
              Все
            </button>
            {categories.map((c) => (
              <button
                key={c.key}
                onClick={() => handleCategoryFilterChange(c.key)}
                className={cn(
                  'px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-wider transition-all whitespace-nowrap',
                  catFilter === c.key
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted text-muted-foreground hover:bg-muted/80'
                )}
              >
                {c.title}
              </button>
            ))}
          </div>
          <div className="text-[10px] font-black text-muted-foreground/30 uppercase ml-4 whitespace-nowrap">
            {visible.length} шт
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 pb-20 no-scrollbar">
        {loading && (
          <div className="flex h-40 items-center justify-center">
            <div className="adm2-spinner" />
          </div>
        )}

        <div className="space-y-2">
          <ReorderList
            items={visible}
            onReorder={handleReorder}
            renderItem={(g) => (
              <div className="group flex items-center gap-4 p-3 bg-muted/20 rounded-2xl border border-transparent hover:border-border/50 transition-all hover:bg-card hover:shadow-sm">
                <IconPreview url={g.icon_url} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-bold truncate">{g.title}</div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/40">
                      {g.key}
                    </span>
                    <span className="text-[9px] text-muted-foreground/20">|</span>
                    <span className="text-[10px] font-bold text-primary/60">
                      {categories.find((c) => c.key === g.category_key)?.title ?? g.category_key}
                    </span>
                  </div>
                </div>
                <div className="flex flex-shrink-0 transition-all sm:opacity-0 sm:group-hover:opacity-100 sm:translate-x-4 sm:group-hover:translate-x-0">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-8 rounded-lg hover:bg-muted"
                    onClick={() => handleEdit(g)}
                  >
                    <Edit2 className="size-3.5" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="size-8 rounded-lg text-destructive hover:bg-destructive/10"
                    disabled={deleting === g.key}
                    onClick={() => handleDelete(g)}
                  >
                    {deleting === g.key ? (
                      <div className="adm2-spinner adm2-spinner-sm" />
                    ) : (
                      <Trash2 className="size-3.5" />
                    )}
                  </Button>
                </div>
              </div>
            )}
          />
        </div>

        {!loading && visible.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 text-center opacity-30 space-y-3">
            <LayoutGrid className="size-10" />
            <div className="text-sm font-bold">{search ? 'Ничего не найдено' : 'Пусто'}</div>
          </div>
        )}
      </div>
    </div>
  )
}
