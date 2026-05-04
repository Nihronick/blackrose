import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { apiMediaList, apiUpload } from '@/lib/api'
import { haptic } from '@/lib/haptic'
import {
  Check,
  ChevronDown,
  ChevronRight,
  Film,
  ImageIcon,
  LayoutGrid,
  Search,
  Upload,
  X,
} from '@/lib/icons'
import { cn } from '@/lib/utils'
import type React from 'react'
import { useEffect, useRef, useState } from 'react'
import { toast } from 'sonner'

interface MediaItem {
  name: string
  url: string
  type: 'image' | 'video'
}

interface MediaGroup {
  id: string
  label: string
  items: MediaItem[]
}

interface MediaSheetProps {
  onInsert: (url: string, type: 'image' | 'video') => void
  onClose: () => void
}

export const MediaSheet: React.FC<MediaSheetProps> = ({ onInsert, onClose }) => {
  const [activeTab, setActiveTab] = useState<'upload' | 'gallery'>('upload')
  const [loading, setLoading] = useState(false)
  const [url, setUrl] = useState('')
  const [type, setType] = useState<'image' | 'video'>('image')
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Gallery states
  const [groups, setGroups] = useState<MediaGroup[]>([])
  const [galleryLoading, setGalleryLoading] = useState(false)
  const [filter, setFilter] = useState('')
  const [openGroups, setOpenGroups] = useState<Record<string, boolean>>({})

  useEffect(() => {
    if (activeTab === 'gallery') {
      setGalleryLoading(true)
      apiMediaList()
        .then((res) => {
          setGroups(res.groups)
          // Open first group by default
          if (res.groups[0]) setOpenGroups({ [res.groups[0].id]: true })
        })
        .finally(() => setGalleryLoading(false))
    }
  }, [activeTab])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setLoading(true)
    try {
      const res = (await apiUpload(file, 'guides')) as { url: string }
      setUrl(res.url)
      if (file.type.startsWith('video/')) setType('video')
      else setType('image')
      haptic.success?.()
      toast.success('Файл загружен')
    } catch (err) {
      toast.error('Ошибка загрузки: ' + (err instanceof Error ? err.message : String(err)))
    } finally {
      setLoading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handleInsert = (insertUrl?: string, insertType?: 'image' | 'video') => {
    const finalUrl = insertUrl || url
    const finalType = insertType || type
    if (!finalUrl) return
    onInsert(finalUrl, finalType)
    haptic.light?.()
  }

  const filteredGroups = filter.trim().toLowerCase()
    ? groups
        .map((g) => ({
          ...g,
          items: g.items.filter((i) => i.name.toLowerCase().includes(filter.toLowerCase())),
        }))
        .filter((g) => g.items.length > 0)
    : groups

  return (
    <div
      className="fixed inset-0 z-[110] flex items-end justify-center bg-black/40 p-4 backdrop-blur-sm animate-in fade-in duration-200 sm:items-center"
      onClick={onClose}
    >
      <Card
        className="flex h-[85vh] w-full max-w-2xl flex-col overflow-hidden bg-background shadow-2xl animate-in slide-in-from-bottom-8 duration-300 rounded-[28px] border-none p-0"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border/10 px-6 py-5">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-primary/10 rounded-xl text-primary">
              <ImageIcon className="size-4" />
            </div>
            <h3 className="text-lg font-bold tracking-tight">Вставить медиа</h3>
          </div>
          <Button variant="ghost" size="icon" className="rounded-full" onClick={onClose}>
            <X className="size-5" />
          </Button>
        </div>

        {/* Tabs Switcher */}
        <div className="px-6 py-4 flex gap-4 border-b border-border/5 bg-muted/5">
          <button
            className={cn(
              'px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all active:scale-95',
              activeTab === 'upload'
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                : 'text-muted-foreground hover:bg-muted'
            )}
            onClick={() => setActiveTab('upload')}
          >
            Загрузить
          </button>
          <button
            className={cn(
              'px-4 py-2 rounded-xl text-xs font-black uppercase tracking-widest transition-all active:scale-95',
              activeTab === 'gallery'
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                : 'text-muted-foreground hover:bg-muted'
            )}
            onClick={() => setActiveTab('gallery')}
          >
            Галерея
          </button>
        </div>

        <div className="flex-1 overflow-y-auto no-scrollbar">
          {activeTab === 'upload' ? (
            <div className="p-6 space-y-6">
              {/* Type Toggle */}
              <div className="flex p-1 bg-muted/50 rounded-xl w-fit">
                <button
                  className={cn(
                    'flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all',
                    type === 'image'
                      ? 'bg-background text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  )}
                  onClick={() => setType('image')}
                >
                  <ImageIcon className="size-3.5" />
                  Фото
                </button>
                <button
                  className={cn(
                    'flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all',
                    type === 'video'
                      ? 'bg-background text-foreground shadow-sm'
                      : 'text-muted-foreground hover:text-foreground'
                  )}
                  onClick={() => setType('video')}
                >
                  <Film className="size-3.5" />
                  Видео
                </button>
              </div>

              {/* Upload Area */}
              {!url && !loading && (
                <button
                  className="w-full flex flex-col items-center justify-center py-20 border-2 border-dashed border-border/50 rounded-[24px] bg-muted/10 hover:bg-muted/20 hover:border-primary/30 transition-all group"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <div className="p-4 bg-primary/10 rounded-2xl text-primary mb-4 group-hover:scale-110 transition-transform">
                    <Upload className="size-8" />
                  </div>
                  <span className="text-sm font-bold text-foreground/80">Нажмите для загрузки</span>
                  <span className="text-[11px] font-medium text-muted-foreground/40 mt-1 uppercase tracking-widest">
                    Изображения или видео
                  </span>
                </button>
              )}

              {loading && (
                <div className="w-full py-20 flex flex-col items-center justify-center gap-4">
                  <div className="adm2-spinner size-10" />
                  <span className="text-xs font-bold text-muted-foreground animate-pulse">
                    ЗАГРУЗКА...
                  </span>
                </div>
              )}

              {url && !loading && (
                <div className="space-y-4 animate-in fade-in zoom-in-95 duration-300">
                  <div className="relative aspect-video rounded-[24px] overflow-hidden bg-muted/30 border border-border/10 flex items-center justify-center">
                    {type === 'image' ? (
                      <img src={url} alt="Preview" className="max-h-full object-contain" />
                    ) : (
                      <Film className="size-16 text-muted-foreground/20" />
                    )}
                    <button
                      className="absolute top-4 right-4 size-10 rounded-full bg-black/50 text-white flex items-center justify-center hover:bg-black/70 backdrop-blur-md"
                      onClick={() => setUrl('')}
                    >
                      <X className="size-5" />
                    </button>
                  </div>
                  <Input
                    className="h-12 border-none bg-muted/50 text-sm font-medium"
                    value={url}
                    readOnly
                  />
                </div>
              )}

              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                onChange={handleUpload}
                accept={type === 'image' ? 'image/*' : 'video/*'}
              />

              <div className="flex items-center gap-3 pt-4">
                <Button
                  className="flex-1 h-14 rounded-2xl gap-2 font-black uppercase tracking-tighter"
                  disabled={!url || loading}
                  onClick={() => handleInsert()}
                >
                  <Check className="size-5" />
                  Вставить в текст
                </Button>
              </div>
            </div>
          ) : (
            <div className="p-6 pt-2">
              <div className="relative mb-6">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
                <Input
                  className="pl-10 h-12 border-none bg-muted/50 text-sm font-medium focus-visible:bg-background"
                  placeholder="Поиск по названию..."
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                />
              </div>

              {galleryLoading ? (
                <div className="py-20 flex justify-center">
                  <div className="adm2-spinner" />
                </div>
              ) : (
                <div className="space-y-4 pb-10">
                  {filteredGroups.map((group) => (
                    <div
                      key={group.id}
                      className="border border-border/10 rounded-2xl overflow-hidden bg-background"
                    >
                      <button
                        className="flex w-full items-center gap-3 px-5 py-4 text-left hover:bg-muted/30 transition-colors"
                        onClick={() => setOpenGroups((p) => ({ ...p, [group.id]: !p[group.id] }))}
                      >
                        <span className="text-sm font-bold tracking-tight">{group.label}</span>
                        <span className="bg-muted px-2 py-0.5 rounded-full text-[10px] font-bold text-muted-foreground">
                          {group.items.length}
                        </span>
                        <div className="ml-auto text-muted-foreground">
                          {openGroups[group.id] || filter ? (
                            <ChevronDown className="size-4" />
                          ) : (
                            <ChevronRight className="size-4" />
                          )}
                        </div>
                      </button>

                      {(openGroups[group.id] || filter) && (
                        <div className="grid grid-cols-3 sm:grid-cols-4 gap-3 p-4 bg-muted/20 border-t border-border/5">
                          {group.items.map((item, idx) => (
                            <button
                              key={idx}
                              className="group relative aspect-square rounded-xl overflow-hidden border border-border/10 bg-background hover:border-primary/40 hover:ring-2 hover:ring-primary/10 transition-all active:scale-95"
                              title={item.name}
                              onClick={() => handleInsert(item.url, item.type)}
                            >
                              {item.type === 'image' ? (
                                <img
                                  src={item.url}
                                  alt=""
                                  className="size-full object-cover"
                                  loading="lazy"
                                />
                              ) : (
                                <div className="size-full flex flex-col items-center justify-center bg-muted/50">
                                  <Film className="size-6 text-muted-foreground/40 mb-1" />
                                  <span className="text-[8px] font-bold uppercase text-muted-foreground/60">
                                    Video
                                  </span>
                                </div>
                              )}
                              <div className="absolute inset-x-0 bottom-0 bg-black/60 p-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                                <p className="text-[8px] text-white truncate font-bold leading-tight">
                                  {item.name}
                                </p>
                              </div>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}

                  {filteredGroups.length === 0 && (
                    <div className="py-20 text-center opacity-30 flex flex-col items-center gap-2">
                      <LayoutGrid className="size-10" />
                      <p className="text-sm font-bold uppercase tracking-widest">
                        Медиа не найдено
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </Card>
    </div>
  )
}
