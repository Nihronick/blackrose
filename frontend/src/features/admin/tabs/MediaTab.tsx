import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { apiDelete, apiMediaList, apiUploadMediaFile } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import { Copy, Film, Image as ImageIcon, Search, Trash2, Upload, Plus, Check } from '@/lib/icons'
import type { MediaGroup, MediaItem, MediaListResponse } from '@/lib/types'
import { normalizeUrl } from '@/lib/utils'
import { type FC, type MouseEvent, type ChangeEvent, useEffect, useState } from 'react'
import { toast } from 'sonner'

export const MediaTab: FC = () => {
  const [data, setData] = useState<MediaListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [uploading, setUploading] = useState(false)

  const load = () => {
    setLoading(true)
    apiMediaList()
      .then(setData)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    load()
  }, [])

  const handleFileUpload = async (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files || files.length === 0) return

    setUploading(true)
    let uploadedCount = 0
    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        const res = await apiUploadMediaFile(file)
        if (res.ok) uploadedCount++
      }
      toast.success(`Успешно загружено файлов: ${uploadedCount}`)
      haptic.success()
      load()
    } catch (err: any) {
      toast.error('Ошибка загрузки: ' + (err.message || err))
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  if (loading)
    return (
      <div className="flex h-60 items-center justify-center">
        <div className="adm2-spinner" />
      </div>
    )

  const filteredGroups =
    data?.groups
      .map((group: MediaGroup) => ({
        ...group,
        items: group.items.filter((item: MediaItem) =>
          item.name.toLowerCase().includes(search.toLowerCase())
        ),
      }))
      .filter((group) => group.items.length > 0) || []

  const copyToClipboard = (url: string) => {
    navigator.clipboard.writeText(url)
    haptic.success()
    toast.success('Ссылка скопирована')
  }

  const handleDelete = async (e: MouseEvent, item: MediaItem) => {
    e.stopPropagation()
    if (!window.confirm('Удалить этот файл навсегда?')) return

    try {
      await apiDelete(`/api/admin/media?url=${encodeURIComponent(item.url)}`)
      haptic.success()
      toast.success('Файл удален')
      load()
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown error'
      toast.error(`Ошибка: ${message}`)
    }
  }

  return (
    <div className="w-full space-y-8 animate-in fade-in duration-500">
      {/* Upload Banner */}
      <Card className="p-6 border border-primary/20 bg-gradient-to-br from-card/90 via-card/50 to-card/90 backdrop-blur-xl rounded-3xl space-y-4 shadow-2xl">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-gradient-to-tr from-violet-600 to-indigo-600 rounded-2xl text-white shadow-lg shadow-violet-500/25 border border-white/10">
              <Upload className="size-6" />
            </div>
            <div>
              <h3 className="text-lg font-black uppercase font-heading text-foreground">
                Прямая Загрузка Медиафайлов (Upload Manager)
              </h3>
              <p className="text-xs text-muted-foreground font-medium mt-0.5">
                Загружайте фотографии и видео с вашего устройства прямо на сайт
              </p>
            </div>
          </div>

          <label className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl text-xs font-black uppercase tracking-wider bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white cursor-pointer shadow-xl shadow-violet-900/40 border border-white/10 active:scale-95 transition-all">
            <Plus className="size-4" />
            <span>{uploading ? 'Загрузка...' : 'Выбрать Файлы'}</span>
            <input
              type="file"
              multiple
              accept="image/*,video/*"
              className="hidden"
              disabled={uploading}
              onChange={handleFileUpload}
            />
          </label>
        </div>
      </Card>

      <div className="flex items-center justify-between">
        <h2 className="text-xl font-black tracking-tight uppercase text-foreground">
          Библиотека медиа ({data?.total})
        </h2>
        <div className="relative w-64">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <input
            className="w-full bg-background/80 border border-white/10 rounded-2xl h-10 pl-10 pr-4 text-xs font-medium focus:ring-2 ring-primary/40 outline-none text-foreground"
            placeholder="Поиск по названию..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="flex flex-col gap-10">
        {filteredGroups.map((group) => (
          <section key={group.id} className="space-y-4">
            <div className="flex items-center gap-2 px-2">
              <div className="h-4 w-1 bg-primary rounded-full" />
              <h3 className="text-sm font-black uppercase tracking-widest text-foreground/60">
                {group.label}
              </h3>
              <span className="text-[10px] font-bold text-muted-foreground/30 px-2 py-0.5 bg-muted/20 rounded-full">
                {group.items.length}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
              {group.items.map((item: MediaItem, i: number) => (
                <Card
                  key={i}
                  className="group relative aspect-square overflow-hidden border-none bg-muted/20 hover:ring-2 ring-primary/40 transition-all cursor-pointer"
                  onClick={() => copyToClipboard(item.url)}
                >
                  {item.type === 'image' ? (
                    <img
                      src={normalizeUrl(item.url)}
                      alt=""
                      className="size-full object-cover transition-transform duration-500 group-hover:scale-110"
                      loading="lazy"
                    />
                  ) : (
                    <div className="size-full flex flex-col items-center justify-center gap-2 bg-slate-900/40">
                      <Film className="size-8 text-white/40" />
                      <span className="text-[8px] font-black uppercase text-white/60 tracking-widest">
                        Video
                      </span>
                    </div>
                  )}

                  {/* Overlay */}
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center p-3 gap-2 backdrop-blur-[2px]">
                    <div className="flex gap-2">
                      <div
                        className="size-8 rounded-full bg-white/20 hover:bg-white/40 flex items-center justify-center transition-colors"
                        onClick={(e) => {
                          e.stopPropagation()
                          copyToClipboard(item.url)
                        }}
                      >
                        <Copy className="size-4 text-white" />
                      </div>
                      <div
                        className="size-8 rounded-full bg-destructive/60 hover:bg-destructive flex items-center justify-center transition-colors"
                        onClick={(e) => handleDelete(e, item)}
                      >
                        <Trash2 className="size-4 text-white" />
                      </div>
                    </div>
                    <span className="text-[9px] font-bold text-white text-center break-all line-clamp-2 leading-tight mt-1">
                      {item.name}
                    </span>
                  </div>

                  <div className="absolute top-2 left-2">
                    {item.type === 'image' ? (
                      <ImageIcon className="size-3 text-white/40" />
                    ) : (
                      <Film className="size-3 text-white/40" />
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </section>
        ))}
      </div>

      {filteredGroups.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground/30">
          <ImageIcon className="size-16 mb-4 opacity-10" />
          <p className="text-sm font-bold uppercase tracking-widest italic">Файлы не найдены</p>
        </div>
      )}
    </div>
  )
}
