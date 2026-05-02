import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { apiDelete, apiPut } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { BarChart3, Edit2, Layers, LogIn, Plus, Trash2 } from '@/lib/icons'
import type { Category } from '@/lib/types'
import { FC, useCallback, useState } from 'react'
import { IconPicker } from '../AdminGuideEditor'
import { IconPreview } from './components/IconPreview'

interface CategoriesTabProps {
  categories: Category[]
  onReload: () => void
}

export const CategoriesTab: FC<CategoriesTabProps> = ({ categories, onReload }) => {
  const [editing, setEditing] = useState<string | null>(null)
  const [form, setForm] = useState({ key: '', title: '', icon_url: '', sort_order: 0 })
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState<string | null>(null)
  const [err, setErr] = useState<string | null>(null)

  const handleSave = useCallback(async () => {
    if (!form.key.trim() || !form.title.trim()) {
      setErr('Key и Title обязательны')
      return
    }
    setSaving(true)
    setErr(null)
    try {
      await apiPut(`/api/admin/category/${form.key}`, {
        title: form.title,
        icon_url: form.icon_url || null,
        sort_order: Number(form.sort_order),
      })
      haptic.success?.()
      setEditing(null)
      onReload()
    } catch (e) {
      const err = e instanceof Error ? e : new Error(String(e))
      setErr(err.message)
    } finally {
      setSaving(false)
    }
  }, [form, onReload])

  const handleDelete = useCallback(
    async (cat: Category) => {
      if (!window.confirm(`Удалить категорию "${cat.title}" и все её гайды?`)) return
      setDeleting(cat.key)
      try {
        await apiDelete(`/api/admin/category/${cat.key}`)
        haptic.success?.()
        onReload()
      } catch (e) {
        const err = e instanceof Error ? e : new Error(String(e))
        alert(err.message)
      } finally {
        setDeleting(null)
      }
    },
    [onReload]
  )

  const handleEditClick = useCallback((cat: Category) => {
    setForm({
      key: cat.key,
      title: cat.title,
      icon_url: cat.icon_url || '',
      sort_order: cat.sort_order,
    })
    setEditing(cat.key)
  }, [])

  if (editing !== null) {
    return (
      <div className="flex flex-col h-full animate-in slide-in-from-right-10 duration-300">
        <div className="sticky top-0 z-20 flex items-center justify-between px-4 py-4 bg-background/80 backdrop-blur-lg border-b border-border/10">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full hover:bg-muted"
              onClick={() => setEditing(null)}
            >
              <LogIn className="size-5 rotate-180" />
            </Button>
            <div className="flex flex-col">
              <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">
                {editing === 'new' ? 'Новая категория' : 'Категория'}
              </span>
              <h2 className="text-base font-bold">{form.title || 'Без названия'}</h2>
            </div>
          </div>
          <Button
            className="h-11 rounded-2xl px-6 gap-2 font-black uppercase tracking-tighter"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? (
              <div className="adm2-spinner adm2-spinner-sm" />
            ) : (
              <BarChart3 className="size-4" />
            )}
            {saving ? 'Ждём...' : 'Сохранить'}
          </Button>
        </div>

        <div className="px-6 py-8 space-y-6">
          {err && (
            <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-2xl text-destructive text-sm font-bold">
              {err}
            </div>
          )}
          <div className="grid grid-cols-1 gap-6 max-w-lg">
            <div className="space-y-2">
              <label
                htmlFor="cat-key-input"
                className="text-[11px] font-black uppercase tracking-widest text-muted-foreground/50 ml-1"
              >
                Уникальный ключ
              </label>
              <Input
                id="cat-key-input"
                className="h-12 border-none bg-muted/50 font-mono text-sm"
                value={form.key}
                onChange={(e) => setForm((p) => ({ ...p, key: e.target.value }))}
                disabled={editing !== 'new'}
              />
            </div>
            <div className="space-y-2">
              <label
                htmlFor="cat-title-input"
                className="text-[11px] font-black uppercase tracking-widest text-muted-foreground/50 ml-1"
              >
                Название
              </label>
              <Input
                id="cat-title-input"
                className="h-12 border-none bg-muted/50 font-bold"
                value={form.title}
                onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))}
              />
            </div>
            <div className="space-y-2">
              <label
                htmlFor="cat-icon-url"
                className="text-[11px] font-black uppercase tracking-widest text-muted-foreground/50 ml-1"
              >
                Иконка
              </label>
              <IconPicker
                value={form.icon_url}
                onChange={(val) => setForm((p) => ({ ...p, icon_url: val }))}
              />
            </div>
            <div className="space-y-2">
              <label
                htmlFor="cat-order-input"
                className="text-[11px] font-black uppercase tracking-widest text-muted-foreground/50 ml-1"
              >
                Порядковый номер
              </label>
              <Input
                id="cat-order-input"
                className="h-12 border-none bg-muted/50 max-w-[100px]"
                type="number"
                value={form.sort_order}
                onChange={(e) => setForm((p) => ({ ...p, sort_order: Number(e.target.value) }))}
              />
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full animate-in fade-in duration-300">
      <div className="flex items-center justify-between px-4 py-6 border-b border-border/10">
        <div className="flex items-center gap-2">
          <Layers className="size-4 text-primary" />
          <h3 className="text-[10px] font-black uppercase tracking-widest text-foreground/40">
            {categories.length} категорий всего
          </h3>
        </div>
        <Button
          className="h-11 rounded-2xl px-6 gap-2 font-black uppercase tracking-tighter shadow-xl shadow-primary/20 transition-all active:scale-[0.98]"
          onClick={() => {
            setForm({ key: '', title: '', icon_url: '', sort_order: categories.length })
            setEditing('new')
          }}
        >
          <Plus className="size-5" />
          Новая
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2 no-scrollbar">
        {categories.map((cat) => (
          <div
            key={cat.key}
            className="group flex items-center gap-4 p-4 bg-muted/20 rounded-2xl border border-transparent hover:border-border/50 transition-all"
          >
            <IconPreview url={cat.icon_url} />
            <div className="flex-1 min-w-0">
              <div className="text-sm font-bold truncate">{cat.title}</div>
              <div className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/40 mt-1">
                {cat.key} · порядок: {cat.sort_order}
              </div>
            </div>
            <div className="flex flex-shrink-0 transition-all sm:opacity-0 sm:group-hover:opacity-100 sm:translate-x-4 sm:group-hover:translate-x-0">
              <Button
                variant="ghost"
                size="icon"
                className="size-9 rounded-xl hover:bg-muted"
                onClick={() => handleEditClick(cat)}
              >
                <Edit2 className="size-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="size-9 rounded-xl text-destructive hover:bg-destructive/10"
                disabled={deleting === cat.key}
                onClick={() => handleDelete(cat)}
              >
                {deleting === cat.key ? (
                  <div className="adm2-spinner adm2-spinner-sm" />
                ) : (
                  <Trash2 className="size-4" />
                )}
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
