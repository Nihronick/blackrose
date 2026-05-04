import { TagEditor } from '@/components/TagBadge'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { apiDelete, apiFetch, apiPut, apiSetGuideTags, apiUpload } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Clock,
  Eye,
  FileText,
  Film,
  History,
  ImageIcon,
  Info,
  LayoutGrid,
  MoreHorizontal,
  Palette,
  Plus,
  Save,
  Search,
  Settings,
  Trash2,
  Upload,
  X,
} from '@/lib/icons'
import type { Category, Guide } from '@/lib/types'
import { cn, normalizeUrl } from '@/lib/utils'
import { type ChangeEvent, type FC, type ReactNode, useEffect, useRef, useState } from 'react'
import { RichEditor } from './AdminRichEditor'
import { IC } from './adminIcons'

interface FieldProps {
  label: string
  hint?: string
  children: ReactNode
  icon?: ReactNode
}

const Field: FC<FieldProps> = ({ label, hint, children, icon }) => (
  <div className="space-y-2">
    <div className="flex items-center justify-between">
      <Label className="text-[13px] font-bold text-foreground/70 flex items-center gap-2">
        {icon && <span className="opacity-50">{icon}</span>}
        {label}
      </Label>
      {hint && (
        <span className="text-[10px] font-medium text-muted-foreground/60 uppercase tracking-wider">
          {hint}
        </span>
      )}
    </div>
    {children}
  </div>
)

const IconPreview: FC<{ url: string }> = ({ url }) => {
  if (!url)
    return (
      <div className="flex size-9 items-center justify-center rounded-xl bg-muted text-[10px] font-bold text-muted-foreground/40">
        ?
      </div>
    )
  return (
    <div className="flex size-9 items-center justify-center rounded-xl bg-muted/30 overflow-hidden ring-1 ring-border/5">
      <img
        src={normalizeUrl(url)}
        alt=""
        className="size-7 object-contain"
        onError={(e) => {
          ;(e.target as HTMLImageElement).style.display = 'none'
        }}
      />
    </div>
  )
}

interface FileUploaderProps {
  onUpload: (url: string) => void
  folder?: string
}

const FileUploader: FC<FileUploaderProps> = ({ onUpload, folder = 'guides' }) => {
  const [loading, setLoading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    try {
      const res = await apiUpload(file, folder)
      onUpload((res as { url: string }).url)
      haptic.success?.()
    } catch (ex) {
      const err = ex instanceof Error ? ex : new Error(String(ex))
      alert(err.message)
    } finally {
      setLoading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  return (
    <div className="shrink-0">
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        onChange={handleChange}
        accept="image/*,video/*"
      />
      <Button
        type="button"
        variant="secondary"
        size="icon"
        className="size-10 rounded-xl transition-all active:scale-90"
        disabled={loading}
        onClick={() => inputRef.current?.click()}
        title="Загрузить файл"
      >
        {loading ? <div className="adm2-spinner adm2-spinner-sm" /> : <Upload className="size-4" />}
      </Button>
    </div>
  )
}

interface IconPickerProps {
  value: string
  onChange: (val: string) => void
}

export const IconPicker: FC<IconPickerProps> = ({ value, onChange }) => {
  const [icons, setIcons] = useState<Array<{ key: string; url: string }>>([])
  const [open, setOpen] = useState(false)
  const [filter, setFilter] = useState('')

  useEffect(() => {
    if (open && !icons.length) {
      apiFetch<Array<{ key: string; url: string }>>('/api/admin/icons')
        .then(setIcons)
        .catch(() => {})
    }
  }, [open, icons.length])

  const filtered = filter
    ? icons.filter((i) => i.key.toLowerCase().includes(filter.toLowerCase()))
    : icons

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Input
          className="h-11 border-none bg-muted/50 text-sm font-medium focus-visible:bg-background focus-visible:ring-2 focus-visible:ring-primary/20"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="URL иконки или {{key}}"
        />
        <Button
          type="button"
          variant="secondary"
          className={cn(
            'size-11 rounded-xl p-0 shrink-0 transition-all',
            open && 'bg-primary text-primary-foreground'
          )}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? <X className="size-5" /> : <Palette className="size-5" />}
        </Button>
        {value && <IconPreview url={value} />}
      </div>

      {open && (
        <Card className="p-4 bg-muted/20 border-border/10 rounded-2xl animate-in fade-in slide-in-from-top-2 duration-200">
          <Input
            className="h-9 border-none bg-background/50 text-xs mb-3"
            placeholder="Поиск иконок..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
          <div className="grid grid-cols-6 sm:grid-cols-8 gap-2 overflow-y-auto max-h-[160px] no-scrollbar pr-1">
            {filtered.map((ic) => (
              <button
                key={ic.key}
                type="button"
                title={ic.key}
                className="flex size-10 items-center justify-center rounded-xl bg-background border border-transparent hover:border-primary/20 hover:bg-primary/5 transition-all"
                onClick={() => {
                  onChange(ic.url)
                  setOpen(false)
                  setFilter('')
                }}
              >
                <img src={normalizeUrl(ic.url)} alt={ic.key} className="size-6 object-contain" />
              </button>
            ))}
            {!filtered.length && (
              <span className="col-span-full py-4 text-center text-[11px] font-bold text-muted-foreground/30 uppercase">
                Пусто
              </span>
            )}
          </div>
        </Card>
      )}
    </div>
  )
}

interface UrlListEditorProps {
  label: string
  value: string[]
  onChange: (val: string[]) => void
  hint?: string
  icon?: React.ReactNode
}

const UrlListEditor: FC<UrlListEditorProps> = ({ label, value, onChange, hint, icon }) => {
  const safeValue = Array.isArray(value) ? value : []
  const add = () => onChange([...safeValue, ''])
  const upd = (i: number, v: string) => {
    const a = [...safeValue]
    a[i] = v
    onChange(a)
  }
  const del = (i: number) => onChange(safeValue.filter((_, j) => j !== i))

  return (
    <Field label={label} hint={hint} icon={icon}>
      <div className="space-y-2">
        {safeValue.map((url, i) => (
          <div key={i} className="flex gap-2 group animate-in slide-in-from-right-2 duration-150">
            <Input
              className="h-10 border-none bg-muted/50 text-xs focus-visible:bg-background"
              value={url}
              onChange={(e) => upd(i, e.target.value)}
              placeholder="https://..."
            />
            <FileUploader onUpload={(u) => upd(i, u)} />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="size-10 rounded-xl text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all active:scale-95"
              onClick={() => del(i)}
            >
              <Trash2 className="size-4" />
            </Button>
          </div>
        ))}
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="h-9 rounded-xl border-dashed border-border/50 text-[11px] font-black uppercase text-muted-foreground hover:text-primary hover:border-primary/40"
          onClick={add}
        >
          <Plus className="size-3.5 mr-1.5" />
          Добавить
        </Button>
      </div>
    </Field>
  )
}

interface GuideEditorProps {
  guide: Guide | null
  categories: Category[]
  onSave: () => void
  onCancel: () => void
}

export const GuideEditor: FC<GuideEditorProps> = ({ guide, categories, onSave, onCancel }) => {
  const isNew = !guide?.key
  const [form, setForm] = useState({
    key: guide?.key ?? '',
    category_key: guide?.category_key ?? categories[0]?.key ?? '',
    title: guide?.title ?? '',
    icon_url: guide?.icon_url ?? '',
    text: guide?.text ?? guide?.content ?? '',
    photo: Array.isArray(guide?.photo) ? guide.photo : [],
    video: Array.isArray(guide?.video) ? guide.video : [],
    document: Array.isArray(guide?.document) ? guide.document : [],
    sort_order: guide?.sort_order ?? 0,
  })
  const [tags, setTags] = useState<string[]>(
    Array.isArray(guide?.tags) ? (guide?.tags as string[]) : []
  )
  const [saving, setSaving] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  const setVal = (f: string) => (v: unknown) => setForm((p) => ({ ...p, [f]: v }))
  const setE = (f: string) => (e: ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((p) => ({ ...p, [f]: e.target.value }))

  const handleDelete = async () => {
    if (
      !window.confirm(
        'Вы уверены, что хотите удалить этот гайд? Все связанные медиа-файлы также будут удалены.'
      )
    )
      return
    setSaving(true)
    try {
      await apiDelete(`/api/admin/guide/${form.key}`)
      haptic.success?.()
      onSave() // Close and refresh
    } catch (e) {
      const err = e instanceof Error ? e : new Error(String(e))
      setErr(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleSave = async () => {
    if (!form.key.trim() || !form.title.trim() || !form.category_key) {
      setErr('Key, Title и категория обязательны')
      haptic.light?.()
      return
    }
    setSaving(true)
    setErr(null)
    try {
      await apiPut(`/api/admin/guide/${form.key}`, {
        category_key: form.category_key,
        title: form.title,
        icon_url: form.icon_url || null,
        text: form.text,
        photo: form.photo,
        video: form.video,
        document: form.document,
        sort_order: Number(form.sort_order),
      })
      await apiSetGuideTags(form.key, tags).catch(() => {})
      haptic.success?.()
      onSave()
    } catch (e) {
      const err = e instanceof Error ? e : new Error(String(e))
      setErr(err.message)
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="flex flex-col h-full bg-background animate-in fade-in duration-300">
      {/* Sticky Header */}
      <div className="sticky top-0 z-20 flex items-center justify-between px-4 py-4 bg-background/80 backdrop-blur-lg border-b border-border/10">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            className="rounded-full hover:bg-muted"
            onClick={onCancel}
          >
            <ArrowLeft className="size-5" />
          </Button>

          {!isNew && (
            <Button
              variant="ghost"
              size="icon"
              className="rounded-full hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-colors"
              onClick={handleDelete}
              disabled={saving}
              title="Удалить гайд"
            >
              <Trash2 className="size-4" />
            </Button>
          )}

          <div className="flex flex-col">
            <span className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60">
              {isNew ? 'Новый гайд' : 'Редактирование'}
            </span>
            <h2 className="text-base font-bold truncate max-w-[150px]">
              {form.title || 'Без названия'}
            </h2>
          </div>
        </div>

        <Button
          className="h-11 rounded-2xl px-6 gap-2 font-black uppercase tracking-tighter shadow-xl shadow-primary/20 transition-all active:scale-[0.98]"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? <div className="adm2-spinner adm2-spinner-sm" /> : <Save className="size-4" />}
          {saving ? 'Ждём...' : 'Готово'}
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-8 pb-32 no-scrollbar">
        {err && (
          <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-2xl text-destructive text-sm font-bold flex items-center gap-2 animate-in zoom-in-95">
            <Info className="size-4" />
            {err}
          </div>
        )}

        {/* Basic Info Section */}
        <section className="space-y-6">
          <div className="flex items-center gap-2 mb-2">
            <Settings className="size-4 text-primary" />
            <h3 className="text-xs font-black uppercase tracking-widest text-foreground/40">
              Основные настройки
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <Field label="Key" hint="уникальный, без пробелов">
              <Input
                className="h-12 border-none bg-muted/50 font-mono text-sm focus-visible:bg-background focus-visible:ring-primary/20"
                value={form.key}
                onChange={setE('key')}
                disabled={!isNew}
                placeholder="guide_key"
              />
            </Field>

            <Field label="Категория">
              <select
                className={cn(
                  'flex h-12 w-full items-center justify-between rounded-xl bg-muted/50 px-4 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary/20',
                  "appearance-none bg-[url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2024%2024%22%20fill%3D%22none%22%20stroke%3D%22currentColor%22%20stroke-width%3D%222%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%3E%3Cpolyline%20points%3D%226%209%2012%2015%2018%209%22%3E%3C/polyline%3E%3C/svg%3E')] bg-[length:16px] bg-[right_1rem_center] bg-no-repeat pr-10"
                )}
                value={form.category_key}
                onChange={setE('category_key')}
              >
                {categories.map((c) => (
                  <option key={c.key} value={c.key}>
                    {c.title}
                  </option>
                ))}
              </select>
            </Field>

            <Field label="Название">
              <Input
                className="h-12 border-none bg-muted/50 text-sm font-bold placeholder:font-medium focus-visible:bg-background focus-visible:ring-primary/20"
                value={form.title}
                onChange={setE('title')}
                placeholder="Название гайда"
              />
            </Field>

            <Field label="Сортировка" hint="чем выше, тем ниже в списке">
              <Input
                className="h-12 border-none bg-muted/50 text-sm focus-visible:bg-background focus-visible:ring-primary/20"
                type="number"
                value={form.sort_order}
                onChange={setE('sort_order')}
              />
            </Field>
          </div>

          <Field label="Иконка">
            <IconPicker value={form.icon_url} onChange={setVal('icon_url')} />
          </Field>
        </section>

        {/* Content Section */}
        <section className="space-y-6">
          <div className="flex items-center gap-2 mb-2">
            <FileText className="size-4 text-primary" />
            <h3 className="text-xs font-black uppercase tracking-widest text-foreground/40">
              Контент и медиа
            </h3>
          </div>

          <Field label="Текст гайда">
            <RichEditor
              value={form.text}
              onChange={setVal('text')}
              rows={18}
              placeholder="Напишите что-нибудь полезное..."
            />
          </Field>

          <Field label="Теги" hint="макс. 20 тегов">
            <TagEditor tags={tags} onChange={setTags} />
          </Field>
        </section>

        {/* Media Lists */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <UrlListEditor
            label="Фотографии"
            icon={<ImageIcon className="size-3.5" />}
            value={form.photo}
            onChange={setVal('photo')}
            hint="прямые ссылки"
          />
          <UrlListEditor
            label="Видео"
            icon={<Film className="size-3.5" />}
            value={form.video}
            onChange={setVal('video')}
            hint="YouTube или URL"
          />
          <UrlListEditor
            label="Документы"
            icon={<FileText className="size-3.5" />}
            value={form.document}
            onChange={setVal('document')}
            hint="PDF, DOCX и др."
          />
        </section>
      </div>

      {/* Floating Save Button Fallback for Mobile */}
      {!saving && (
        <div className="fixed bottom-6 right-6 z-30 sm:hidden">
          <Button
            className="size-14 rounded-full shadow-2xl shadow-primary/40 animate-in zoom-in-0 duration-300"
            onClick={handleSave}
          >
            <Save className="size-6" />
          </Button>
        </div>
      )}
    </div>
  )
}
